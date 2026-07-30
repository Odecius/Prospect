import uuid

import pytest

from app.database.models import Company, CompanySourceRef, DataSource
from app.external.providers import ExternalPlace, ExternalSearchPage
from app.services.external_search import (
    ExternalImportConflictError,
    ExternalSearchInput,
    ExternalSearchService,
    ExternalSearchValidationError,
    RequestLimiter,
)


class ProviderFake:
    def __init__(self, next_token: str | None = None) -> None:
        self.next_token = next_token

    def search(
        self, query: str, page_size: int, page_token: str | None = None, location_restriction: dict | None = None
    ) -> ExternalSearchPage:
        self.call = (query, page_size, page_token, location_restriction)
        return ExternalSearchPage(
            places=[
                ExternalPlace(
                    "place-1", "Empresa", None, None, None, None, None, None, [], None, None, None, None, None, []
                )
            ],
            next_page_token=self.next_token,
        )


class RepositoryFake:
    def __init__(self) -> None:
        self.company = Company(id=uuid.uuid4(), archived_at=None, merged_into_company_id=None)
        self.source = DataSource(id=uuid.uuid4(), name="Google Places API (New)")
        self.existing = None
        self.saved = None

    def get_company(self, _company_id: uuid.UUID) -> Company:
        return self.company

    def google_source(self) -> DataSource:
        return self.source

    def find_external_id(self, _source_id: uuid.UUID, _external_id: str) -> CompanySourceRef | None:
        return self.existing

    def add(self, value: CompanySourceRef) -> None:
        self.saved = value

    def commit(self) -> None:
        pass


def service(
    provider: ProviderFake | None = None, repository: RepositoryFake | None = None, limit: int = 5
) -> ExternalSearchService:
    return ExternalSearchService(
        provider or ProviderFake(), repository or RepositoryFake(), "x" * 32, 10, 2, RequestLimiter(limit)
    )


def test_search_builds_controlled_query_and_opaque_pagination() -> None:
    provider = ProviderFake("google-token")
    first = service(provider).search(ExternalSearchInput(" lojas ", " São Paulo ", "sp"), uuid.uuid4())
    assert provider.call[:3] == ("lojas em São Paulo, SP, Brasil", 10, None)
    assert first.next_cursor and "google-token" not in first.next_cursor
    assert first.temporary is True


def test_request_limit_is_enforced_without_provider_call() -> None:
    current = service(limit=1)
    actor = uuid.uuid4()
    current.search(ExternalSearchInput("lojas", "São Paulo", "SP"), actor)
    with pytest.raises(ExternalSearchValidationError, match="Limite"):
        current.search(ExternalSearchInput("lojas", "São Paulo", "SP"), actor)


def test_geographic_rectangle_is_validated_and_mapped() -> None:
    provider = ProviderFake()
    service(provider).search(
        ExternalSearchInput("lojas", "São Paulo", "SP", south=-24, west=-47, north=-23, east=-46), uuid.uuid4()
    )
    assert provider.call[3]["rectangle"]["low"] == {"latitude": -24, "longitude": -47}
    with pytest.raises(ExternalSearchValidationError, match="quatro coordenadas"):
        service().search(ExternalSearchInput("lojas", "São Paulo", "SP", south=-24), uuid.uuid4())


def test_link_persists_only_place_id_and_detects_existing_import() -> None:
    repository = RepositoryFake()
    reference = service(repository=repository).link_place(repository.company.id, "place-1")
    assert reference.external_id == "place-1"
    assert reference.source_url is None
    assert reference.raw_name is None
    repository.existing = CompanySourceRef(
        company_id=uuid.uuid4(), data_source_id=repository.source.id, external_id="place-1"
    )
    with pytest.raises(ExternalImportConflictError):
        service(repository=repository).link_place(repository.company.id, "place-1")
