import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.ai.providers import DraftGeneration
from app.database.models import (
    Category,
    Company,
    GeneratedMessage,
    MessageDraftStatus,
    OpportunityScore,
    PipelineStatus,
    User,
)
from app.services.external_search import RequestLimiter
from app.services.message_drafts import DraftReviewInput, MessageDraftService, MessageDraftValidationError


class ProviderFake:
    model = "gpt-5.6-luna"

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
        self.score = None
        self.saved = None
        self.today = []
        self.has_diagnostic = False

    def get_company(self, _company_id: uuid.UUID) -> Company:
        return self.company

    def get_category(self, _category_id: uuid.UUID) -> Category:
        return self.category

    def latest_website_audit(self, _company_id: uuid.UUID):
        return None

    def latest_score(self, _company_id: uuid.UUID):
        return self.score

    def get_draft(self, _draft_id: uuid.UUID) -> GeneratedMessage | None:
        return self.saved

    def list_for_company(self, _company_id: uuid.UUID) -> list[GeneratedMessage]:
        return [self.saved] if self.saved else []

    def list_openai_created_since(self, _started_at):
        return self.today

    def acquire_generation_locks(self, _usage_day, _diagnostic_company_id) -> None:
        pass

    def has_diagnostic_for_company(self, _company_id: uuid.UUID) -> bool:
        return self.has_diagnostic

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
    assert draft.generated_content["evidence_refs"] == ["company_profile"]


@pytest.mark.parametrize("draft_type", ["COMMERCIAL_DIAGNOSTIC", "PROPOSAL_DRAFT"])
def test_generation_supports_sprint_12_draft_types(draft_type: str) -> None:
    repository = RepositoryFake()
    draft = service(repository).generate(repository.company.id, User(id=uuid.uuid4()), draft_type)
    assert draft.draft_type == draft_type
    assert draft.input_snapshot["draft_type"] == draft_type
    assert draft.prompt_version.endswith("-v1")


def test_generation_rejects_unknown_draft_type() -> None:
    repository = RepositoryFake()
    with pytest.raises(MessageDraftValidationError, match="Tipo de rascunho inválido"):
        service(repository).generate(repository.company.id, User(id=uuid.uuid4()), "WEBSITE_DEMO")


def test_daily_limit_blocks_generation() -> None:
    repository = RepositoryFake()
    repository.today = [SimpleNamespace(usage={}, model="gpt-5.6-luna")] * 20
    with pytest.raises(MessageDraftValidationError, match="20/20"):
        service(repository).generate(repository.company.id, User(id=uuid.uuid4()))


def test_cost_uses_cached_input_rate_when_available() -> None:
    repository = RepositoryFake()
    current = service(repository)
    usage = {"input_tokens": 1000, "cached_input_tokens": 400, "output_tokens": 100}
    assert current._estimate_cost(usage) == pytest.approx(Decimal("0.000248"))


def test_cost_conservatively_prices_all_input_when_cache_detail_is_absent() -> None:
    repository = RepositoryFake()
    current = service(repository)
    assert current._estimate_cost({"input_tokens": 1000, "output_tokens": 100}) == pytest.approx(Decimal("0.00032"))


def test_only_one_diagnostic_per_company() -> None:
    repository = RepositoryFake()
    repository.has_diagnostic = True
    with pytest.raises(MessageDraftValidationError, match="somente um por empresa"):
        service(repository).generate(repository.company.id, User(id=uuid.uuid4()), "COMMERCIAL_DIAGNOSTIC")


def test_diagnostic_uses_only_explainable_score_evidence() -> None:
    repository = RepositoryFake()
    repository.score = OpportunityScore(
        id=uuid.uuid4(),
        company_id=repository.company.id,
        total=72,
        formula_version="v1-human-40-30-30",
        components={
            "fit": {"value": 80, "weight": 0.4, "missing": False},
            "reputation": {"value": 70, "weight": 0.3, "missing": False},
            "digital_gap": {"value": 65, "weight": 0.3, "missing": False},
            "private_note": "não enviar",
        },
        explanation="Texto livre não deve sair.",
        calculated_by_user_id=uuid.uuid4(),
    )
    draft = service(repository).generate(repository.company.id, User(id=uuid.uuid4()), "COMMERCIAL_DIAGNOSTIC")
    assert draft.input_snapshot["opportunity_score"] == {
        "total": 72,
        "formula_version": "v1-human-40-30-30",
        "components": {"fit": 80, "reputation": 70, "digital_gap": 65},
    }
    assert "Texto livre" not in str(draft.input_snapshot)
    assert draft.generated_content["evidence_refs"] == [
        "company_profile",
        f"opportunity_score:{repository.score.id}",
    ]


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
