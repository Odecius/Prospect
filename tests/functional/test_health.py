from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.database.session import get_database_session
from app.main import create_app


def test_health_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_includes_health_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/health" in response.json()["paths"]
    assert "/ready" in response.json()["paths"]


class ReadySession:
    def execute(self, _statement: object) -> None:
        return None


class UnavailableSession:
    def execute(self, _statement: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("database unavailable"))


def test_readiness_checks_database_without_exposing_details() -> None:
    application = create_app()
    application.dependency_overrides[get_database_session] = lambda: ReadySession()

    with TestClient(application) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_generic_unavailable_response() -> None:
    application = create_app()
    application.dependency_overrides[get_database_session] = lambda: UnavailableSession()

    with TestClient(application) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Aplicação temporariamente indisponível"}


def test_security_headers_are_present_without_hsts_outside_production() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["content-security-policy"].startswith("default-src 'self'")
    assert "strict-transport-security" not in response.headers
