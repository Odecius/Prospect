import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.database.models import CompanySourceRef
from app.external.providers import BusinessSearchProvider
from app.repositories.external_sources import ExternalSourceRepository


class ExternalSearchValidationError(Exception):
    pass


class ExternalImportConflictError(ExternalSearchValidationError):
    def __init__(self, company_id: uuid.UUID) -> None:
        self.company_id = company_id
        super().__init__("Place ID já vinculado a outra empresa.")


@dataclass(frozen=True)
class ExternalSearchInput:
    term: str
    city: str
    state_code: str
    cursor: str | None = None
    south: float | None = None
    west: float | None = None
    north: float | None = None
    east: float | None = None


@dataclass(frozen=True)
class ExternalSearchResult:
    items: list[dict]
    next_cursor: str | None
    provider_attribution: str = "Google Maps"
    temporary: bool = True


class RequestLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def consume(self, actor_id: str) -> None:
        now = time.monotonic()
        with self._lock:
            events = self._events[actor_id]
            while events and events[0] <= now - self.window_seconds:
                events.popleft()
            if len(events) >= self.limit:
                raise ExternalSearchValidationError("Limite de pesquisas por minuto atingido.")
            events.append(now)


class ExternalSearchService:
    def __init__(
        self,
        provider: BusinessSearchProvider,
        repository: ExternalSourceRepository,
        secret_key: str,
        page_size: int,
        max_pages: int,
        limiter: RequestLimiter,
    ) -> None:
        self.provider = provider
        self.repository = repository
        self.serializer = URLSafeTimedSerializer(secret_key, salt="external-search-cursor-v1")
        self.page_size = page_size
        self.max_pages = max_pages
        self.limiter = limiter

    def search(self, data: ExternalSearchInput, actor_id: uuid.UUID) -> ExternalSearchResult:
        self.limiter.consume(str(actor_id))
        term = " ".join(data.term.strip().split())
        city = " ".join(data.city.strip().split())
        state = data.state_code.strip().upper()
        if not term or not city or len(state) != 2:
            raise ExternalSearchValidationError("Termo, cidade e UF são obrigatórios.")
        page, page_token = 1, None
        if data.cursor:
            try:
                cursor = self.serializer.loads(data.cursor, max_age=600)
            except (BadSignature, SignatureExpired) as error:
                raise ExternalSearchValidationError("Cursor inválido ou expirado.") from error
            expected = {
                "term": term,
                "city": city,
                "state": state,
                "south": data.south,
                "west": data.west,
                "north": data.north,
                "east": data.east,
            }
            if any(cursor.get(key) != value for key, value in expected.items()):
                raise ExternalSearchValidationError("Cursor não corresponde à pesquisa.")
            page, page_token = int(cursor["page"]), cursor["page_token"]
        if page > self.max_pages:
            raise ExternalSearchValidationError("Limite de páginas por pesquisa atingido.")
        restriction = self._restriction(data)
        result = self.provider.search(f"{term} em {city}, {state}, Brasil", self.page_size, page_token, restriction)
        next_cursor = None
        if result.next_page_token and page < self.max_pages:
            next_cursor = self.serializer.dumps(
                {
                    "term": term,
                    "city": city,
                    "state": state,
                    "south": data.south,
                    "west": data.west,
                    "north": data.north,
                    "east": data.east,
                    "page": page + 1,
                    "page_token": result.next_page_token,
                }
            )
        return ExternalSearchResult(items=[asdict(place) for place in result.places], next_cursor=next_cursor)

    def link_place(self, company_id: uuid.UUID, place_id: str) -> CompanySourceRef:
        company = self.repository.get_company(company_id)
        source = self.repository.google_source()
        if company is None or company.archived_at or company.merged_into_company_id:
            raise ExternalSearchValidationError("Empresa ativa não encontrada.")
        if source is None:
            raise ExternalSearchValidationError("Fonte Google Places não configurada.")
        clean_id = place_id.strip()
        if not clean_id or len(clean_id) > 300:
            raise ExternalSearchValidationError("Place ID inválido.")
        existing = self.repository.find_external_id(source.id, clean_id)
        if existing:
            raise ExternalImportConflictError(existing.company_id)
        reference = CompanySourceRef(
            company_id=company_id,
            data_source_id=source.id,
            external_id=clean_id,
            observed_at=datetime.now(UTC),
            last_verified_at=datetime.now(UTC),
        )
        self.repository.add(reference)
        self.repository.commit()
        return reference

    @staticmethod
    def _restriction(data: ExternalSearchInput) -> dict | None:
        values = [data.south, data.west, data.north, data.east]
        if all(value is None for value in values):
            return None
        if any(value is None for value in values):
            raise ExternalSearchValidationError("Região geográfica exige quatro coordenadas.")
        if not (-90 <= data.south < data.north <= 90 and -180 <= data.west < data.east <= 180):
            raise ExternalSearchValidationError("Região geográfica inválida.")
        return {
            "rectangle": {
                "low": {"latitude": data.south, "longitude": data.west},
                "high": {"latitude": data.north, "longitude": data.east},
            }
        }
