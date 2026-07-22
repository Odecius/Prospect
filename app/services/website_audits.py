import ipaddress
import re
import socket
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from app.database.models import ContactType, User, WebsiteAudit, WebsiteAuditStatus
from app.repositories.website_audits import WebsiteAuditRepository
from app.services.external_search import ExternalSearchValidationError, RequestLimiter


class WebsiteAuditValidationError(Exception):
    pass


class WebsiteAuditFetchError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class FetchResult:
    final_url: str
    http_status: int
    duration_ms: int
    findings: dict


class _HomepageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_title = False
        self.has_description = False
        self.has_viewport = False
        self.has_canonical = False
        self.has_form = False
        self.lang_present = False
        self._inside_title = False
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): (value or "") for key, value in attrs}
        tag = tag.casefold()
        if tag == "html" and values.get("lang", "").strip():
            self.lang_present = True
        elif tag == "title":
            self._inside_title = True
        elif tag == "meta":
            name = values.get("name", "").casefold()
            self.has_description |= name == "description" and bool(values.get("content", "").strip())
            self.has_viewport |= name == "viewport" and bool(values.get("content", "").strip())
        elif tag == "link":
            self.has_canonical |= "canonical" in values.get("rel", "").casefold() and bool(
                values.get("href", "").strip()
            )
        elif tag == "form":
            self.has_form = True

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title and data.strip():
            self.has_title = True
        if len(" ".join(self._text)) < 100_000:
            self._text.append(data)

    def findings(self) -> dict:
        text = " ".join(self._text).casefold()
        return {
            "title_present": self.has_title,
            "meta_description_present": self.has_description,
            "viewport_present": self.has_viewport,
            "language_present": self.lang_present,
            "canonical_present": self.has_canonical,
            "contact_form_signal": self.has_form,
            "email_signal": bool(re.search(r"\b[^\s@]+@[^\s@]+\.[a-z]{2,}\b", text)),
            "phone_signal": bool(re.search(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?\d{4,5}[-\s]?\d{4}", text)),
            "whatsapp_signal": "whatsapp" in text or "wa.me/" in text,
        }


def normalize_audit_url(value: str) -> str:
    parsed = urlsplit(value.strip() if "://" in value else f"https://{value.strip()}")
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        raise WebsiteAuditValidationError("Website deve usar HTTP ou HTTPS.")
    if parsed.username or parsed.password or parsed.fragment:
        raise WebsiteAuditValidationError("Website não pode conter credenciais ou fragmento.")
    try:
        port = parsed.port
    except ValueError as error:
        raise WebsiteAuditValidationError("Porta inválida.") from error
    if port and port not in {80, 443}:
        raise WebsiteAuditValidationError("Somente as portas 80 e 443 são permitidas.")
    host = parsed.hostname.casefold().rstrip(".")
    netloc = host if not port else f"{host}:{port}"
    return urlunsplit((parsed.scheme.casefold(), netloc, parsed.path or "/", parsed.query, ""))


def assert_public_destination(url: str, resolver=socket.getaddrinfo) -> None:
    host = urlsplit(url).hostname
    if not host or host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise WebsiteAuditValidationError("Destino local ou reservado bloqueado.")
    try:
        addresses = {item[4][0] for item in resolver(host, None, type=socket.SOCK_STREAM)}
    except socket.gaierror as error:
        raise WebsiteAuditFetchError("DNS_FAILURE") from error
    if not addresses:
        raise WebsiteAuditFetchError("DNS_FAILURE")
    for value in addresses:
        address = ipaddress.ip_address(value.split("%")[0])
        if not address.is_global:
            raise WebsiteAuditValidationError("Destino local, privado ou reservado bloqueado.")


class WebsiteAuditFetcher:
    def __init__(self, timeout: float, max_bytes: int, max_redirects: int) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects

    def fetch(self, raw_url: str) -> FetchResult:
        current = normalize_audit_url(raw_url)
        started = time.monotonic()
        initial_scheme = urlsplit(current).scheme
        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=False,
                trust_env=False,
                headers={"User-Agent": "ABC-Prospect-Website-Audit/1.0 (+internal-review)"},
            ) as client:
                for redirect_count in range(self.max_redirects + 1):
                    assert_public_destination(current)
                    with client.stream("GET", current) as response:
                        if response.status_code in {301, 302, 303, 307, 308}:
                            location = response.headers.get("location")
                            if not location or redirect_count >= self.max_redirects:
                                raise WebsiteAuditFetchError("REDIRECT_LIMIT")
                            current = normalize_audit_url(urljoin(current, location))
                            continue
                        content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
                        body = bytearray()
                        for chunk in response.iter_bytes():
                            body.extend(chunk)
                            if len(body) > self.max_bytes:
                                raise WebsiteAuditFetchError("RESPONSE_TOO_LARGE")
                        duration_ms = round((time.monotonic() - started) * 1000)
                        is_html = content_type in {"text/html", "application/xhtml+xml"}
                        findings = {
                            "reachable": 200 <= response.status_code < 400,
                            "uses_https": urlsplit(current).scheme == "https",
                            "redirected_to_https": initial_scheme == "http" and urlsplit(current).scheme == "https",
                            "content_type_html": is_html,
                            "response_bytes": len(body),
                        }
                        if is_html:
                            parser = _HomepageParser()
                            parser.feed(body.decode(response.encoding or "utf-8", errors="replace"))
                            findings.update(parser.findings())
                        return FetchResult(current, response.status_code, duration_ms, findings)
        except WebsiteAuditFetchError:
            raise
        except httpx.TimeoutException as error:
            raise WebsiteAuditFetchError("TIMEOUT") from error
        except (httpx.NetworkError, httpx.ProtocolError) as error:
            raise WebsiteAuditFetchError("NETWORK_ERROR") from error
        raise WebsiteAuditFetchError("REDIRECT_LIMIT")


class WebsiteAuditService:
    def __init__(
        self,
        repository: WebsiteAuditRepository,
        fetcher: WebsiteAuditFetcher,
        limiter: RequestLimiter,
        cooldown_seconds: int,
        enabled: bool,
    ) -> None:
        self.repository = repository
        self.fetcher = fetcher
        self.limiter = limiter
        self.cooldown_seconds = cooldown_seconds
        self.enabled = enabled

    def list_audits(self, company_id: uuid.UUID) -> list[WebsiteAudit]:
        return self.repository.list_for_company(company_id)

    def audit(self, company_id: uuid.UUID, contact_id: uuid.UUID, actor: User) -> WebsiteAudit:
        if not self.enabled:
            raise WebsiteAuditValidationError("Auditoria de websites não está habilitada neste ambiente.")
        try:
            self.limiter.consume(str(actor.id))
        except ExternalSearchValidationError as error:
            raise WebsiteAuditValidationError("Limite de auditorias por minuto atingido.") from error
        company = self.repository.get_company(company_id)
        contact = self.repository.get_contact(contact_id)
        if company is None or company.archived_at or company.merged_into_company_id:
            raise WebsiteAuditValidationError("Empresa ativa não encontrada.")
        if (
            contact is None
            or contact.company_id != company_id
            or contact.contact_type is not ContactType.WEBSITE
            or contact.invalidated_at is not None
        ):
            raise WebsiteAuditValidationError("Selecione um website ativo cadastrado para esta empresa.")
        latest = self.repository.latest_for_contact(contact_id)
        now = self.repository.now()
        if latest and latest.created_at:
            created_at = latest.created_at if latest.created_at.tzinfo else latest.created_at.replace(tzinfo=UTC)
            if (now - created_at).total_seconds() < self.cooldown_seconds:
                raise WebsiteAuditValidationError("Aguarde o intervalo mínimo antes de auditar este website novamente.")
        requested_url = normalize_audit_url(contact.value)
        try:
            result = self.fetcher.fetch(requested_url)
            audit = WebsiteAudit(
                company_id=company_id,
                contact_id=contact_id,
                requested_url=requested_url,
                final_url=result.final_url,
                status=WebsiteAuditStatus.COMPLETED,
                http_status=result.http_status,
                duration_ms=result.duration_ms,
                findings=result.findings,
                performed_by_user_id=actor.id,
                created_at=datetime.now(UTC),
            )
        except WebsiteAuditFetchError as error:
            audit = WebsiteAudit(
                company_id=company_id,
                contact_id=contact_id,
                requested_url=requested_url,
                status=WebsiteAuditStatus.FAILED,
                findings={},
                error_code=error.code,
                performed_by_user_id=actor.id,
                created_at=datetime.now(UTC),
            )
        self.repository.add(audit)
        self.repository.commit()
        return audit
