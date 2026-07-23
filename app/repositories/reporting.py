import uuid

from sqlalchemy import case, exists, func, or_, select
from sqlalchemy.orm import Session

from app.database.models import (
    Category,
    Company,
    Contact,
    ContactType,
    ExportAudit,
    GeneratedMessage,
    MessageDraftStatus,
    OpportunityScore,
    PipelineStatus,
    WebsiteAudit,
    WebsiteAuditStatus,
)


class ReportingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def dashboard(self) -> dict:
        active = (Company.archived_at.is_(None), Company.merged_into_company_id.is_(None))
        website_exists = exists().where(
            Contact.company_id == Company.id,
            Contact.contact_type == ContactType.WEBSITE,
            Contact.invalidated_at.is_(None),
        )
        score_exists = exists().where(OpportunityScore.company_id == Company.id)
        audit_exists = exists().where(
            WebsiteAudit.company_id == Company.id, WebsiteAudit.status == WebsiteAuditStatus.COMPLETED
        )
        approved_exists = exists().where(
            GeneratedMessage.company_id == Company.id, GeneratedMessage.status == MessageDraftStatus.APPROVED
        )
        status_rows = self.session.execute(
            select(Company.pipeline_status, func.count()).where(*active).group_by(Company.pipeline_status)
        ).all()
        return {
            "total_active": self.session.scalar(select(func.count()).select_from(Company).where(*active)) or 0,
            "do_not_contact": self.session.scalar(
                select(func.count())
                .select_from(Company)
                .where(*active, Company.pipeline_status == PipelineStatus.DO_NOT_CONTACT)
            )
            or 0,
            "without_website": self.session.scalar(
                select(func.count()).select_from(Company).where(*active, ~website_exists)
            )
            or 0,
            "with_score": self.session.scalar(select(func.count()).select_from(Company).where(*active, score_exists))
            or 0,
            "with_completed_audit": self.session.scalar(
                select(func.count()).select_from(Company).where(*active, audit_exists)
            )
            or 0,
            "with_approved_content": self.session.scalar(
                select(func.count()).select_from(Company).where(*active, approved_exists)
            )
            or 0,
            "by_pipeline": {status.value: count for status, count in status_rows},
        }

    def export_rows(
        self,
        query: str | None,
        category_id: uuid.UUID | None,
        state_code: str | None,
        pipeline_status: str | None,
    ) -> tuple[list[tuple], int]:
        website_present = case(
            (
                exists().where(
                    Contact.company_id == Company.id,
                    Contact.contact_type == ContactType.WEBSITE,
                    Contact.invalidated_at.is_(None),
                ),
                True,
            ),
            else_=False,
        )
        latest_score = (
            select(OpportunityScore.total)
            .where(OpportunityScore.company_id == Company.id)
            .order_by(OpportunityScore.calculated_at.desc(), OpportunityScore.id.desc())
            .limit(1)
            .scalar_subquery()
        )
        statement = (
            select(
                Company.legal_or_trade_name,
                Category.name,
                Company.city,
                Company.state_code,
                Company.pipeline_status,
                website_present,
                latest_score,
            )
            .join(Category, Category.id == Company.category_id)
            .where(Company.archived_at.is_(None), Company.merged_into_company_id.is_(None))
        )
        if query:
            pattern = f"%{query}%"
            statement = statement.where(or_(Company.name_normalized.ilike(pattern), Company.city.ilike(pattern)))
        if category_id:
            statement = statement.where(Company.category_id == category_id)
        if state_code:
            statement = statement.where(Company.state_code == state_code)
        if pipeline_status:
            statement = statement.where(Company.pipeline_status == pipeline_status)
        total = self.session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        rows = self.session.execute(statement.order_by(Company.legal_or_trade_name, Company.id).limit(501)).all()
        return rows, total

    def add_export_audit(self, audit: ExportAudit) -> None:
        self.session.add(audit)

    def commit(self) -> None:
        self.session.commit()
