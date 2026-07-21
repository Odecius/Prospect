import uuid
from datetime import datetime

from app.database.models import CommercialActivity, PipelineStatus, User
from app.repositories.pipeline import PipelineRepository

NEXT = {
    PipelineStatus.NEW: {PipelineStatus.QUALIFIED, PipelineStatus.LOST},
    PipelineStatus.QUALIFIED: {PipelineStatus.CONTACTED, PipelineStatus.LOST},
    PipelineStatus.CONTACTED: {PipelineStatus.REPLIED, PipelineStatus.LOST},
    PipelineStatus.REPLIED: {PipelineStatus.MEETING, PipelineStatus.LOST},
    PipelineStatus.MEETING: {PipelineStatus.PROPOSAL_SENT, PipelineStatus.LOST},
    PipelineStatus.PROPOSAL_SENT: {PipelineStatus.NEGOTIATION, PipelineStatus.LOST},
    PipelineStatus.NEGOTIATION: {PipelineStatus.WON, PipelineStatus.LOST},
    PipelineStatus.WON: {PipelineStatus.NEW},
    PipelineStatus.LOST: {PipelineStatus.NEW},
    PipelineStatus.DO_NOT_CONTACT: {PipelineStatus.NEW},
    PipelineStatus.ARCHIVED: {PipelineStatus.NEW},
}
ACTIVE = set(PipelineStatus) - {PipelineStatus.DO_NOT_CONTACT, PipelineStatus.ARCHIVED}


class PipelineValidationError(Exception):
    pass


class PipelineService:
    def __init__(self, repository: PipelineRepository) -> None:
        self.repository = repository

    def list_activities(self, company_id: uuid.UUID) -> list[CommercialActivity]:
        return self.repository.list_activities(company_id)

    def add_activity(
        self,
        company_id: uuid.UUID,
        activity_type: str,
        notes: str,
        actor: User,
        outcome: str | None = None,
        next_action_at: datetime | None = None,
    ) -> CommercialActivity:
        company = self.repository.get_company(company_id)
        if company is None or company.merged_into_company_id:
            raise PipelineValidationError("Empresa não encontrada.")
        if company.pipeline_status is PipelineStatus.DO_NOT_CONTACT and activity_type == "CONTACT":
            raise PipelineValidationError("DO_NOT_CONTACT impede novos registros de abordagem.")
        if activity_type not in {"NOTE", "RESEARCH", "CONTACT", "RESPONSE", "MEETING", "NEXT_STEP"}:
            raise PipelineValidationError("Tipo de atividade inválido.")
        clean_notes = notes.strip()
        if not clean_notes or len(clean_notes) > 1000:
            raise PipelineValidationError("Descrição obrigatória com até 1000 caracteres.")
        activity = CommercialActivity(
            company_id=company_id,
            activity_type=activity_type,
            notes=clean_notes,
            outcome=outcome.strip()[:120] if outcome else None,
            next_action_at=next_action_at,
            performed_by_user_id=actor.id,
        )
        self.repository.add(activity)
        self.repository.commit()
        return activity

    def transition(
        self, company_id: uuid.UUID, new_status: PipelineStatus, reason: str, actor: User
    ) -> CommercialActivity:
        company = self.repository.get_company(company_id)
        if company is None or company.merged_into_company_id:
            raise PipelineValidationError("Empresa não encontrada.")
        previous = company.pipeline_status
        allowed = set(NEXT[previous])
        if previous in ACTIVE:
            allowed.update({PipelineStatus.DO_NOT_CONTACT, PipelineStatus.ARCHIVED})
        if new_status not in allowed:
            raise PipelineValidationError(f"Transição {previous.value} → {new_status.value} não permitida.")
        clean_reason = reason.strip()
        if not clean_reason or len(clean_reason) > 1000:
            raise PipelineValidationError("Justificativa obrigatória com até 1000 caracteres.")
        company.pipeline_status = new_status
        company.archived_at = datetime.now().astimezone() if new_status is PipelineStatus.ARCHIVED else None
        company.updated_by_user_id = actor.id
        activity = CommercialActivity(
            company_id=company_id,
            activity_type="STATUS_CHANGE",
            previous_status=previous.value,
            new_status=new_status.value,
            notes=clean_reason,
            performed_by_user_id=actor.id,
        )
        self.repository.add(activity)
        self.repository.commit()
        return activity
