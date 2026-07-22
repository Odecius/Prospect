import uuid

import pytest

from app.ai.providers import DraftGeneration
from app.database.models import (
    Category,
    Company,
    GeneratedMessage,
    MessageDraftStatus,
    PipelineStatus,
    User,
)
from app.services.external_search import RequestLimiter
from app.services.message_drafts import DraftReviewInput, MessageDraftService, MessageDraftValidationError


class ProviderFake:
    def generate(self, context: dict) -> DraftGeneration:
        self.context = context
        return DraftGeneration("Assunto", "Corpo revisável", ["Confirmar informações"], "fake", "fake-model", {})


class RepositoryFake:
    def __init__(self) -> None:
        self.company = Company(
            id=uuid.uuid4(),
            legal_or_trade_name="Empresa Fictícia",
            category_id=uuid.uuid4(),
            city="Recife",
            state_code="PE",
            pipeline_status=PipelineStatus.NEW,
            archived_at=None,
            merged_into_company_id=None,
        )
        self.category = Category(id=self.company.category_id, name="Serviços profissionais")
        self.saved = None

    def get_company(self, _company_id: uuid.UUID) -> Company:
        return self.company

    def get_category(self, _category_id: uuid.UUID) -> Category:
        return self.category

    def latest_website_audit(self, _company_id: uuid.UUID):
        return None

    def get_draft(self, _draft_id: uuid.UUID) -> GeneratedMessage | None:
        return self.saved

    def list_for_company(self, _company_id: uuid.UUID) -> list[GeneratedMessage]:
        return [self.saved] if self.saved else []

    def add(self, draft: GeneratedMessage) -> None:
        self.saved = draft

    def commit(self) -> None:
        pass


def service(repository: RepositoryFake, enabled: bool = True) -> MessageDraftService:
    return MessageDraftService(repository, ProviderFake(), RequestLimiter(3), enabled)


def test_generation_sends_only_minimal_business_context() -> None:
    repository = RepositoryFake()
    draft = service(repository).generate(repository.company.id, User(id=uuid.uuid4()))
    assert draft.status is MessageDraftStatus.DRAFT
    assert set(draft.input_snapshot) == {
        "draft_type",
        "language",
        "company_name",
        "category",
        "city",
        "state_code",
    }
    assert draft.reviewed_content is None


def test_do_not_contact_blocks_generation_and_review() -> None:
    repository = RepositoryFake()
    repository.company.pipeline_status = PipelineStatus.DO_NOT_CONTACT
    with pytest.raises(MessageDraftValidationError, match="DO_NOT_CONTACT"):
        service(repository).generate(repository.company.id, User(id=uuid.uuid4()))
    repository.company.pipeline_status = PipelineStatus.NEW
    draft = service(repository).generate(repository.company.id, User(id=uuid.uuid4()))
    repository.company.pipeline_status = PipelineStatus.DO_NOT_CONTACT
    with pytest.raises(MessageDraftValidationError, match="DO_NOT_CONTACT"):
        service(repository).review(
            draft.id,
            DraftReviewInput(MessageDraftStatus.APPROVED, "Revisei o conteúdo."),
            User(id=uuid.uuid4()),
        )


def test_human_can_edit_and_approve_once_without_send_state() -> None:
    repository = RepositoryFake()
    current = service(repository)
    draft = current.generate(repository.company.id, User(id=uuid.uuid4()))
    reviewed = current.review(
        draft.id,
        DraftReviewInput(MessageDraftStatus.APPROVED, "Texto conferido.", "Assunto editado", "Corpo editado"),
        User(id=uuid.uuid4()),
    )
    assert reviewed.status is MessageDraftStatus.APPROVED
    assert reviewed.reviewed_content == {"subject": "Assunto editado", "body": "Corpo editado"}
    assert "SENT" not in {item.value for item in MessageDraftStatus}
    with pytest.raises(MessageDraftValidationError, match="imutável"):
        current.review(
            draft.id,
            DraftReviewInput(MessageDraftStatus.REJECTED, "Nova decisão."),
            User(id=uuid.uuid4()),
        )
