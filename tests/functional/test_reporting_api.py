import uuid

from fastapi.testclient import TestClient

from app.api.authentication import require_csrf_token, require_current_user
from app.api.reporting import get_reporting_service
from app.database.models import User, UserStatus
from app.main import create_app


class ReportingServiceFake:
    def dashboard(self) -> dict:
        return {
            "total_active": 4,
            "do_not_contact": 1,
            "without_website": 2,
            "with_score": 3,
            "with_completed_audit": 1,
            "with_approved_content": 1,
            "by_pipeline": {"NEW": 3, "DO_NOT_CONTACT": 1},
        }

    def export_csv(self, _filters: object, _actor: User) -> str:
        return "\ufeffempresa,categoria\nEmpresa Fictícia,Serviços\n"


def client() -> TestClient:
    application = create_app()
    application.dependency_overrides[require_current_user] = lambda: User(id=uuid.uuid4(), status=UserStatus.ACTIVE)
    application.dependency_overrides[require_csrf_token] = lambda: None
    application.dependency_overrides[get_reporting_service] = ReportingServiceFake
    return TestClient(application)


def test_dashboard_and_manual_csv_export() -> None:
    with client() as test_client:
        dashboard = test_client.get("/api/reporting/dashboard")
        exported = test_client.post("/api/reporting/companies.csv", json={"state_code": "SP"})
    assert dashboard.status_code == 200
    assert dashboard.json()["by_pipeline"]["DO_NOT_CONTACT"] == 1
    assert exported.status_code == 200
    assert exported.headers["content-disposition"] == 'attachment; filename="abc-prospect-segmento.csv"'
    assert "Empresa Fictícia" in exported.text


def test_reporting_requires_authentication() -> None:
    with TestClient(create_app()) as test_client:
        dashboard = test_client.get("/api/reporting/dashboard")
        exported = test_client.post("/api/reporting/companies.csv", json={})
    assert dashboard.status_code == 401
    assert exported.status_code == 401
