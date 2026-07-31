import uuid
from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.authentication import require_csrf_token, require_current_user
from app.api.message_drafts import get_message_draft_service
from app.database.models import GeneratedMessage, MessageDraftStatus, User, UserStatus
from app.main import create_app
from app.services.message_drafts import AIUsageToday


class DraftServiceFake:
    def __init__(self) -> None:
        self.draft = GeneratedMessage(
            id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            status=MessageDraftStatus.DRAFT,
            draft_type="COMMERCIAL_INTRODUCTION",
            provider="fake",
            model="fake-model",
            prompt_version="test-v1",
            generated_content={"subject": "Assunto", "body": "Corpo", "safety_notes": []},
            reviewed_content=None,
            input_snapshot={"company_name": "Empresa Fictícia"},
            usage={},
            requested_by_user_id=uuid.uuid4(),
            created_at=datetime.now(UTC),
        )

    def list_drafts(self, company_id: uuid.UUID) -> list[GeneratedMessage]:
        self.draft.company_id = company_id
        return [self.draft]

    def usage_today(self) -> AIUsageToday:
        return AIUsageToday(3, 20, Decimal("0.001234"), "gpt-5.6-luna")

    def generate(
        self, company_id: uuid.UUID, actor: User, draft_type: str = "COMMERCIAL_INTRODUCTION"
    ) -> GeneratedMessage:
        self.draft.company_id = company_id
        self.draft.requested_by_user_id = actor.id
        self.draft.draft_type = draft_type
        return self.draft

    def review(self, _draft_id: uuid.UUID, data: object, actor: User) -> GeneratedMessage:
        self.draft.status = data.decision
        self.draft.review_reason = data.reason
        self.draft.reviewed_by_user_id = actor.id
        self.draft.reviewed_at = datetime.now(UTC)
        return self.draft


def client() -> TestClient:
    user = User(id=uuid.uuid4(), status=UserStatus.ACTIVE)
    application = create_app()
    application.dependency_overrides[require_current_user] = lambda: user
    application.dependency_overrides[require_csrf_token] = lambda: None
    application.dependency_overrides[get_message_draft_service] = DraftServiceFake
    return TestClient(application)


def test_generate_list_and_review_drafts() -> None:
    company_id = uuid.uuid4()
    with client() as test_client:
        created = test_client.post(f"/api/companies/{company_id}/message-drafts")
        listed = test_client.get(f"/api/companies/{company_id}/message-drafts")
        reviewed = test_client.post(
            f"/api/message-drafts/{created.json()['id']}/review",
            json={"decision": "REJECTED", "reason": "Tom inadequado."},
        )
    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["generated_content"]["body"] == "Corpo"
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "REJECTED"


def test_generate_commercial_diagnostic() -> None:
    company_id = uuid.uuid4()
    with client() as test_client:
        response = test_client.post(
            f"/api/companies/{company_id}/message-drafts",
            json={"draft_type": "COMMERCIAL_DIAGNOSTIC"},
        )
    assert response.status_code == 201
    assert response.json()["draft_type"] == "COMMERCIAL_DIAGNOSTIC"


def test_ai_usage_today() -> None:
    with client() as test_client:
        response = test_client.get("/api/ai-usage/today")
    assert response.status_code == 200
    assert response.json() == {
        "calls": 3,
        "limit": 20,
        "estimated_cost_usd": 0.001234,
        "model": "gpt-5.6-luna",
    }
