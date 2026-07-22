import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.authentication import require_csrf_token, require_current_user
from app.api.message_drafts import get_message_draft_service
from app.database.models import GeneratedMessage, MessageDraftStatus, User, UserStatus
from app.main import create_app


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

    def generate(self, company_id: uuid.UUID, actor: User) -> GeneratedMessage:
        self.draft.company_id = company_id
        self.draft.requested_by_user_id = actor.id
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
