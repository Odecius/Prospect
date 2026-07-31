import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.ai.providers import MessageDraftProvider
from app.database.models import GeneratedMessage, MessageDraftStatus, PipelineStatus, User, WebsiteAuditStatus
from app.repositories.message_drafts import MessageDraftRepository
from app.services.external_search import ExternalSearchValidationError, RequestLimiter

DRAFT_TYPES = {
    "COMMERCIAL_INTRODUCTION": "commercial-introduction-v1",
    "COMMERCIAL_DIAGNOSTIC": "commercial-diagnostic-v1",
    "PROPOSAL_DRAFT": "proposal-draft-v1",
}
AI_DAILY_CALL_LIMIT = 20
AI_USAGE_TIMEZONE = ZoneInfo("Europe/London")
OPENAI_PRICING_SOURCE = "https://developers.openai.com/api/docs/pricing"
OPENAI_PRICING_VERIFIED_ON = "2026-07-31"


class MessageDraftValidationError(Exception):
    pass


class AIDailyLimitExceededError(MessageDraftValidationError):
    pass


class DiagnosticLimitExceededError(MessageDraftValidationError):
    pass


@dataclass(frozen=True)
class AIUsageToday:
    calls: int
    limit: int
    estimated_cost_usd: Decimal
    model: str


@dataclass(frozen=True)
class DraftReviewInput:
    decision: MessageDraftStatus
    reason: str
    subject: str | None = None
    body: str | None = None


class MessageDraftService:
    def __init__(
        self,
        repository: MessageDraftRepository,
        provider: MessageDraftProvider,
        limiter: RequestLimiter,
        enabled: bool,
        input_price_per_million_usd: Decimal = Decimal("0.20"),
        cached_input_price_per_million_usd: Decimal = Decimal("0.02"),
        output_price_per_million_usd: Decimal = Decimal("1.20"),
    ) -> None:
        self.repository = repository
        self.provider = provider
        self.limiter = limiter
        self.enabled = enabled
        self.input_price_per_million_usd = input_price_per_million_usd
        self.cached_input_price_per_million_usd = cached_input_price_per_million_usd
        self.output_price_per_million_usd = output_price_per_million_usd

    def list_drafts(self, company_id: uuid.UUID) -> list[GeneratedMessage]:
        return self.repository.list_for_company(company_id)

    def usage_today(self) -> AIUsageToday:
        drafts = self.repository.list_openai_created_since(self._start_of_today_utc())
        cost = sum((self._stored_or_estimated_cost(item) for item in drafts), Decimal("0"))
        return AIUsageToday(len(drafts), AI_DAILY_CALL_LIMIT, cost, self.provider.model)

    def generate(
        self, company_id: uuid.UUID, actor: User, draft_type: str = "COMMERCIAL_INTRODUCTION"
    ) -> GeneratedMessage:
        if not self.enabled:
            raise MessageDraftValidationError("Geração de rascunhos por IA não está configurada.")
        if draft_type not in DRAFT_TYPES:
            raise MessageDraftValidationError("Tipo de rascunho inválido.")
        usage = self.usage_today()
        if usage.calls >= usage.limit:
            raise AIDailyLimitExceededError(
                "Limite diário de IA atingido (20/20). Novas gerações estarão disponíveis amanhã."
            )
        if draft_type == "COMMERCIAL_DIAGNOSTIC" and self.repository.has_diagnostic_for_company(company_id):
            raise DiagnosticLimitExceededError(
                "Esta empresa já possui um diagnóstico. Durante os testes, é permitido somente um por empresa."
            )
        try:
            self.limiter.consume(str(actor.id))
        except ExternalSearchValidationError as error:
            raise MessageDraftValidationError("Limite de gerações por minuto atingido.") from error
        company = self._active_contactable_company(company_id)
        category = self.repository.get_category(company.category_id)
        context = {
            "draft_type": draft_type,
            "language": "pt-BR",
            "company_name": company.legal_or_trade_name,
            "category": category.name if category else "Não informada",
            "city": company.city,
            "state_code": company.state_code,
        }
        evidence_refs = ["company_profile"]
        audit = self.repository.latest_website_audit(company_id)
        if audit and audit.status is WebsiteAuditStatus.COMPLETED:
            allowed = {
                "reachable",
                "uses_https",
                "redirected_to_https",
                "title_present",
                "meta_description_present",
                "viewport_present",
                "contact_form_signal",
            }
            context["website_signals"] = {key: bool(value) for key, value in audit.findings.items() if key in allowed}
            evidence_refs.append(f"website_audit:{audit.id}")
        score = self.repository.latest_score(company_id)
        if score:
            context["opportunity_score"] = {
                "total": score.total,
                "formula_version": score.formula_version,
                "components": {
                    key: component.get("value")
                    for key, component in score.components.items()
                    if key in {"fit", "reputation", "digital_gap"}
                    and isinstance(component, dict)
                    and (component.get("value") is None or isinstance(component.get("value"), int | float))
                },
            }
            evidence_refs.append(f"opportunity_score:{score.id}")
        generated = self.provider.generate(context)
        recorded_usage = dict(generated.usage)
        recorded_usage["estimated_cost_usd"] = float(self._estimate_cost(recorded_usage))
        recorded_usage["cost_estimate"] = {
            "input_usd_per_million": str(self.input_price_per_million_usd),
            "cached_input_usd_per_million": str(self.cached_input_price_per_million_usd),
            "output_usd_per_million": str(self.output_price_per_million_usd),
            "source": OPENAI_PRICING_SOURCE,
            "verified_on": OPENAI_PRICING_VERIFIED_ON,
            "cached_input_policy": "API detail when available; otherwise full input price",
        }
        draft = GeneratedMessage(
            company_id=company_id,
            status=MessageDraftStatus.DRAFT,
            draft_type=draft_type,
            provider=generated.provider,
            model=generated.model,
            prompt_version=DRAFT_TYPES[draft_type],
            generated_content={
                "subject": generated.subject,
                "body": generated.body,
                "safety_notes": generated.safety_notes,
                "evidence_refs": evidence_refs,
            },
            input_snapshot=context,
            usage=recorded_usage,
            requested_by_user_id=actor.id,
            created_at=datetime.now(UTC),
        )
        self.repository.add(draft)
        self.repository.commit()
        return draft

    @staticmethod
    def _start_of_today_utc() -> datetime:
        local_now = datetime.now(AI_USAGE_TIMEZONE)
        return local_now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(UTC)

    def _estimate_cost(self, usage: dict) -> Decimal:
        input_tokens = max(0, int(usage.get("input_tokens", 0)))
        cached_input_tokens = min(input_tokens, max(0, int(usage.get("cached_input_tokens", 0))))
        regular_input_tokens = input_tokens - cached_input_tokens
        output_tokens = max(0, int(usage.get("output_tokens", 0)))
        return (
            Decimal(regular_input_tokens) * self.input_price_per_million_usd
            + Decimal(cached_input_tokens) * self.cached_input_price_per_million_usd
            + Decimal(output_tokens) * self.output_price_per_million_usd
        ) / Decimal(1_000_000)

    def _stored_or_estimated_cost(self, draft: GeneratedMessage) -> Decimal:
        stored = draft.usage.get("estimated_cost_usd")
        if isinstance(stored, int | float | str):
            try:
                return Decimal(str(stored))
            except ArithmeticError:
                pass
        return self._estimate_cost(draft.usage)

    def review(self, draft_id: uuid.UUID, data: DraftReviewInput, actor: User) -> GeneratedMessage:
        draft = self.repository.get_draft(draft_id)
        if draft is None:
            raise MessageDraftValidationError("Rascunho não encontrado.")
        company = self._active_contactable_company(draft.company_id)
        if company.pipeline_status is PipelineStatus.DO_NOT_CONTACT:
            raise MessageDraftValidationError("Empresa marcada como DO_NOT_CONTACT.")
        if draft.status is not MessageDraftStatus.DRAFT:
            raise MessageDraftValidationError("Rascunho já revisado e imutável.")
        reason = " ".join(data.reason.strip().split())
        if not reason or len(reason) > 500:
            raise MessageDraftValidationError("Justificativa de revisão obrigatória.")
        if data.decision not in {MessageDraftStatus.APPROVED, MessageDraftStatus.REJECTED}:
            raise MessageDraftValidationError("Decisão de revisão inválida.")
        reviewed_content = None
        if data.decision is MessageDraftStatus.APPROVED:
            subject = (data.subject or draft.generated_content["subject"]).strip()
            body = (data.body or draft.generated_content["body"]).strip()
            if not subject or len(subject) > 120 or not body or len(body) > 1500:
                raise MessageDraftValidationError("Assunto ou corpo revisado inválido.")
            reviewed_content = {"subject": subject, "body": body}
        draft.status = data.decision
        draft.reviewed_content = reviewed_content
        draft.review_reason = reason
        draft.reviewed_by_user_id = actor.id
        draft.reviewed_at = datetime.now(UTC)
        self.repository.commit()
        return draft

    def _active_contactable_company(self, company_id: uuid.UUID):
        company = self.repository.get_company(company_id)
        if company is None or company.archived_at or company.merged_into_company_id:
            raise MessageDraftValidationError("Empresa ativa não encontrada.")
        if company.pipeline_status is PipelineStatus.DO_NOT_CONTACT:
            raise MessageDraftValidationError("Empresa marcada como DO_NOT_CONTACT.")
        return company
