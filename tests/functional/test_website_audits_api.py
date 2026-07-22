import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.authentication import require_csrf_token, require_current_user
from app.api.website_audits import get_website_audit_service
from app.database.models import User, UserStatus, WebsiteAudit, WebsiteAuditStatus
from app.main import create_app


class WebsiteAuditServiceFake:
    def __init__(self) -> None:
        self.audit_item = WebsiteAudit(
            id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            contact_id=uuid.uuid4(),
            requested_url="https://example.com/",
            final_url="https://example.com/",
            status=WebsiteAuditStatus.COMPLETED,
            http_status=200,
            duration_ms=35,
            findings={"reachable": True, "viewport_present": True},
            error_code=None,
            performed_by_user_id=uuid.uuid4(),
            created_at=datetime.now(UTC),
        )

    def list_audits(self, _company_id: uuid.UUID) -> list[WebsiteAudit]:
        return [self.audit_item]

    def audit(self, company_id: uuid.UUID, contact_id: uuid.UUID, actor: User) -> WebsiteAudit:
        self.audit_item.company_id = company_id
        self.audit_item.contact_id = contact_id
        self.audit_item.performed_by_user_id = actor.id
        return self.audit_item


def client() -> TestClient:
    user = User(id=uuid.uuid4(), status=UserStatus.ACTIVE)
    application = create_app()
    application.dependency_overrides[require_current_user] = lambda: user
    application.dependency_overrides[require_csrf_token] = lambda: None
    application.dependency_overrides[get_website_audit_service] = WebsiteAuditServiceFake
    return TestClient(application)


def test_create_and_list_website_audits() -> None:
    company_id, contact_id = uuid.uuid4(), uuid.uuid4()
    with client() as test_client:
        created = test_client.post(f"/api/companies/{company_id}/website-audits", json={"contact_id": str(contact_id)})
        listed = test_client.get(f"/api/companies/{company_id}/website-audits")
    assert created.status_code == 201
    assert created.json()["contact_id"] == str(contact_id)
    assert created.json()["findings"]["reachable"] is True
    assert listed.status_code == 200
    assert len(listed.json()) == 1
