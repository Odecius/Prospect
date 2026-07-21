import uuid

from fastapi.testclient import TestClient

from app.api.authentication import require_csrf_token, require_current_user
from app.api.external_search import get_external_search_service
from app.database.models import CompanySourceRef, User, UserStatus
from app.main import create_app
from app.services.external_search import ExternalSearchResult


class ExternalServiceFake:
    def search(self, _data: object, _actor_id: uuid.UUID) -> ExternalSearchResult:
        return ExternalSearchResult(
            items=[
                {
                    "external_id": "place-1",
                    "name": "Empresa Fictícia",
                    "formatted_address": None,
                    "city": None,
                    "state_code": None,
                    "latitude": None,
                    "longitude": None,
                    "primary_type": None,
                    "types": [],
                    "business_status": None,
                    "rating": None,
                    "user_rating_count": None,
                    "website_uri": None,
                    "google_maps_uri": None,
                    "attributions": [],
                }
            ],
            next_cursor=None,
        )

    def link_place(self, company_id: uuid.UUID, place_id: str) -> CompanySourceRef:
        return CompanySourceRef(
            id=uuid.uuid4(),
            company_id=company_id,
            data_source_id=uuid.uuid4(),
            external_id=place_id,
        )


def client() -> TestClient:
    user = User(id=uuid.uuid4(), status=UserStatus.ACTIVE)
    application = create_app()
    application.dependency_overrides[require_current_user] = lambda: user
    application.dependency_overrides[require_csrf_token] = lambda: None
    application.dependency_overrides[get_external_search_service] = ExternalServiceFake
    return TestClient(application)


def test_search_response_is_marked_temporary_and_attributed() -> None:
    with client() as test_client:
        response = test_client.post(
            "/api/external/google-places/search", json={"term": "loja", "city": "São Paulo", "state_code": "SP"}
        )
    assert response.status_code == 200
    assert response.json()["temporary"] is True
    assert response.json()["retention_seconds"] == 0
    assert response.json()["provider_attribution"] == "Google Maps"


def test_link_endpoint_persists_place_id_after_explicit_action() -> None:
    company_id = uuid.uuid4()
    with client() as test_client:
        response = test_client.post(
            "/api/external/google-places/link", json={"company_id": str(company_id), "place_id": "place-1"}
        )
    assert response.status_code == 201
    assert response.json()["company_id"] == str(company_id)
    assert response.json()["place_id"] == "place-1"
