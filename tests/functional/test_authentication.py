import uuid

from fastapi.testclient import TestClient

from app.api.authentication import get_authentication_service
from app.database.models import User, UserStatus
from app.main import create_app


class FakeAuthenticationService:
    def __init__(self) -> None:
        self.user = User(
            id=uuid.uuid4(),
            email_normalized="admin@example.test",
            display_name="Test Admin",
            password_hash="not-exposed",
            status=UserStatus.ACTIVE,
        )

    def authenticate(self, email: str, password: str) -> User | None:
        if email == "admin@example.test" and password == "correct-test-password":
            return self.user
        return None

    def get_active_user(self, user_id: str) -> User | None:
        return self.user if user_id == str(self.user.id) else None


def client_with_fake_authentication() -> TestClient:
    application = create_app()
    service = FakeAuthenticationService()
    application.dependency_overrides[get_authentication_service] = lambda: service
    return TestClient(application)


def test_anonymous_session_and_invalid_credentials_are_generic() -> None:
    with client_with_fake_authentication() as client:
        session_response = client.get("/auth/session")
        login_response = client.post("/auth/login", json={"email": "admin@example.test", "password": "wrong-password"})

    assert session_response.json() == {"authenticated": False}
    assert login_response.status_code == 401
    assert login_response.json() == {"detail": "Credenciais inválidas."}


def test_login_session_csrf_and_logout_lifecycle() -> None:
    with client_with_fake_authentication() as client:
        login_response = client.post(
            "/auth/login", json={"email": "admin@example.test", "password": "correct-test-password"}
        )
        csrf_token = login_response.json()["csrf_token"]
        session_response = client.get("/auth/session")
        rejected_logout = client.post("/auth/logout", headers={"X-CSRF-Token": "wrong"})
        logout_response = client.post("/auth/logout", headers={"X-CSRF-Token": csrf_token})
        anonymous_response = client.get("/auth/session")

    assert login_response.status_code == 200
    assert "abc_prospect_session=" in login_response.headers["set-cookie"]
    assert "httponly" in login_response.headers["set-cookie"].lower()
    assert "samesite=lax" in login_response.headers["set-cookie"].lower()
    assert session_response.json()["authenticated"] is True
    assert rejected_logout.status_code == 403
    assert logout_response.status_code == 204
    assert anonymous_response.json() == {"authenticated": False}


def test_logout_requires_authentication() -> None:
    with client_with_fake_authentication() as client:
        response = client.post("/auth/logout", headers={"X-CSRF-Token": "anything"})

    assert response.status_code == 401
