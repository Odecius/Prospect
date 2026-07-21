import uuid

from fastapi.testclient import TestClient

from app.api.authentication import require_csrf_token, require_current_user
from app.api.contacts import get_contact_service
from app.database.models import (
    CompanyMergeAudit,
    Contact,
    ContactType,
    DuplicateCandidate,
    DuplicateLevel,
    DuplicateStatus,
    User,
    UserStatus,
)
from app.main import create_app


class FakeContactService:
    def __init__(self, user: User) -> None:
        self.user = user
        self.company_a = uuid.uuid4()
        self.company_b = uuid.uuid4()
        self.contact = Contact(
            id=uuid.uuid4(),
            company_id=self.company_a,
            contact_type=ContactType.EMAIL,
            value="contato@example.test",
            value_normalized="contato@example.test",
            is_primary=True,
            created_by_user_id=user.id,
        )
        self.candidate = DuplicateCandidate(
            id=uuid.uuid4(),
            company_a_id=self.company_a,
            company_b_id=self.company_b,
            level=DuplicateLevel.PROBABLE,
            status=DuplicateStatus.OPEN,
            signals={"contact_type": "EMAIL"},
        )

    def list_contacts(self, company_id: uuid.UUID) -> list[Contact]:
        return [self.contact] if company_id == self.company_a else []

    def create_contact(self, company_id: uuid.UUID, **_values: object) -> Contact:
        self.contact.company_id = company_id
        return self.contact

    def invalidate(self, contact_id: uuid.UUID) -> Contact | None:
        return self.contact if contact_id == self.contact.id else None

    def list_candidates(self) -> list[DuplicateCandidate]:
        return [self.candidate]

    def review_candidate(
        self, candidate_id: uuid.UUID, decision: DuplicateStatus, reason: str, _actor: User
    ) -> DuplicateCandidate | None:
        if candidate_id != self.candidate.id:
            return None
        self.candidate.status = decision
        self.candidate.decision_reason = reason
        return self.candidate

    def merge(self, _candidate_id: uuid.UUID, survivor_id: uuid.UUID, reason: str, actor: User) -> CompanyMergeAudit:
        return CompanyMergeAudit(
            id=uuid.uuid4(),
            survivor_company_id=survivor_id,
            merged_company_id=self.company_b,
            performed_by_user_id=actor.id,
            reason=reason,
            details={},
        )


def client_and_service() -> tuple[TestClient, FakeContactService]:
    user = User(
        id=uuid.uuid4(),
        email_normalized="admin@example.test",
        display_name="Admin",
        password_hash="unused",
        status=UserStatus.ACTIVE,
    )
    service = FakeContactService(user)
    application = create_app()
    application.dependency_overrides[require_current_user] = lambda: user
    application.dependency_overrides[require_csrf_token] = lambda: None
    application.dependency_overrides[get_contact_service] = lambda: service
    return TestClient(application), service


def test_contact_endpoints_serialize_corporate_contact() -> None:
    client, service = client_and_service()
    with client:
        created = client.post(
            f"/api/companies/{service.company_a}/contacts",
            json={"contact_type": "EMAIL", "value": "contato@example.test", "is_primary": True},
        )
        listed = client.get(f"/api/companies/{service.company_a}/contacts")

    assert created.status_code == 201
    assert created.json()["contact_type"] == "EMAIL"
    assert listed.json()[0]["value"] == "contato@example.test"


def test_duplicate_review_and_merge_require_explicit_calls() -> None:
    client, service = client_and_service()
    with client:
        candidates = client.get("/api/duplicate-candidates")
        reviewed = client.post(
            f"/api/duplicate-candidates/{service.candidate.id}/review",
            json={"status": "CONFIRMED_DUPLICATE", "reason": "Mesmo contato corporativo."},
        )
        merged = client.post(
            f"/api/duplicate-candidates/{service.candidate.id}/merge",
            json={"survivor_company_id": str(service.company_a), "reason": "Revisão humana concluída."},
        )

    assert candidates.json()[0]["status"] == "OPEN"
    assert reviewed.json()["status"] == "CONFIRMED_DUPLICATE"
    assert merged.status_code == 201
    assert merged.json()["status"] == "merged"
