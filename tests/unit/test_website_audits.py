import socket
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.database.models import Company, Contact, ContactType, User, WebsiteAudit, WebsiteAuditStatus
from app.services.external_search import RequestLimiter
from app.services.website_audits import (
    FetchResult,
    WebsiteAuditFetchError,
    WebsiteAuditService,
    WebsiteAuditValidationError,
    assert_public_destination,
    normalize_audit_url,
)


class FetcherFake:
    def __init__(self, error: str | None = None) -> None:
        self.error = error

    def fetch(self, url: str) -> FetchResult:
        if self.error:
            raise WebsiteAuditFetchError(self.error)
        return FetchResult(url, 200, 42, {"reachable": True, "uses_https": True})


class RepositoryFake:
    def __init__(self) -> None:
        self.company = Company(id=uuid.uuid4(), archived_at=None, merged_into_company_id=None)
        self.contact = Contact(
            id=uuid.uuid4(),
            company_id=self.company.id,
            contact_type=ContactType.WEBSITE,
            value="https://example.com",
            invalidated_at=None,
        )
        self.latest = None
        self.saved = None

    def get_company(self, _company_id: uuid.UUID) -> Company:
        return self.company

    def get_contact(self, _contact_id: uuid.UUID) -> Contact:
        return self.contact

    def latest_for_contact(self, _contact_id: uuid.UUID) -> WebsiteAudit | None:
        return self.latest

    def list_for_company(self, _company_id: uuid.UUID) -> list[WebsiteAudit]:
        return []

    def add(self, audit: WebsiteAudit) -> None:
        self.saved = audit

    def commit(self) -> None:
        pass

    def now(self) -> datetime:
        return datetime.now(UTC)


def make_service(repository: RepositoryFake, fetcher: FetcherFake | None = None) -> WebsiteAuditService:
    return WebsiteAuditService(repository, fetcher or FetcherFake(), RequestLimiter(5), 60, True)


def test_url_policy_blocks_credentials_ports_and_private_destinations() -> None:
    assert normalize_audit_url("example.com") == "https://example.com/"
    with pytest.raises(WebsiteAuditValidationError, match="credenciais"):
        normalize_audit_url("https://user:secret@example.com")
    with pytest.raises(WebsiteAuditValidationError, match="portas"):
        normalize_audit_url("https://example.com:8443")

    def private_resolver(*_args: object, **_kwargs: object) -> list[tuple]:
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 0))]

    with pytest.raises(WebsiteAuditValidationError, match="privado"):
        assert_public_destination("https://example.com/", private_resolver)


def test_service_persists_only_findings_and_actor() -> None:
    repository = RepositoryFake()
    actor = User(id=uuid.uuid4())
    audit = make_service(repository).audit(repository.company.id, repository.contact.id, actor)
    assert audit.status is WebsiteAuditStatus.COMPLETED
    assert audit.findings == {"reachable": True, "uses_https": True}
    assert audit.performed_by_user_id == actor.id
    assert not hasattr(audit, "raw_html")


def test_controlled_failure_is_persisted_without_remote_content() -> None:
    repository = RepositoryFake()
    audit = make_service(repository, FetcherFake("TIMEOUT")).audit(
        repository.company.id, repository.contact.id, User(id=uuid.uuid4())
    )
    assert audit.status is WebsiteAuditStatus.FAILED
    assert audit.error_code == "TIMEOUT"
    assert audit.findings == {}


def test_cooldown_and_registered_website_are_required() -> None:
    repository = RepositoryFake()
    repository.latest = WebsiteAudit(created_at=datetime.now(UTC) - timedelta(seconds=10))
    with pytest.raises(WebsiteAuditValidationError, match="intervalo"):
        make_service(repository).audit(repository.company.id, repository.contact.id, User(id=uuid.uuid4()))
    repository.latest = None
    repository.contact.contact_type = ContactType.EMAIL
    with pytest.raises(WebsiteAuditValidationError, match="website ativo"):
        make_service(repository).audit(repository.company.id, repository.contact.id, User(id=uuid.uuid4()))


def test_production_safety_switch_can_disable_execution() -> None:
    repository = RepositoryFake()
    service = WebsiteAuditService(repository, FetcherFake(), RequestLimiter(5), 60, False)
    with pytest.raises(WebsiteAuditValidationError, match="não está habilitada"):
        service.audit(repository.company.id, repository.contact.id, User(id=uuid.uuid4()))
