import uuid
from datetime import date, datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database.models import Category, Company, GeneratedMessage, OpportunityScore, WebsiteAudit


class MessageDraftRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def get_category(self, category_id: uuid.UUID) -> Category | None:
        return self.session.get(Category, category_id)

    def latest_website_audit(self, company_id: uuid.UUID) -> WebsiteAudit | None:
        return self.session.scalar(
            select(WebsiteAudit)
            .where(WebsiteAudit.company_id == company_id)
            .order_by(WebsiteAudit.created_at.desc(), WebsiteAudit.id.desc())
            .limit(1)
        )

    def latest_score(self, company_id: uuid.UUID) -> OpportunityScore | None:
        return self.session.scalar(
            select(OpportunityScore)
            .where(OpportunityScore.company_id == company_id)
            .order_by(OpportunityScore.calculated_at.desc(), OpportunityScore.id.desc())
            .limit(1)
        )

    def get_draft(self, draft_id: uuid.UUID) -> GeneratedMessage | None:
        return self.session.get(GeneratedMessage, draft_id)

    def list_for_company(self, company_id: uuid.UUID) -> list[GeneratedMessage]:
        return list(
            self.session.scalars(
                select(GeneratedMessage)
                .where(GeneratedMessage.company_id == company_id)
                .order_by(GeneratedMessage.created_at.desc(), GeneratedMessage.id.desc())
                .limit(50)
            )
        )

    def list_openai_created_since(self, started_at: datetime) -> list[GeneratedMessage]:
        return list(
            self.session.scalars(
                select(GeneratedMessage)
                .where(
                    GeneratedMessage.provider == "openai",
                    GeneratedMessage.created_at >= started_at,
                )
                .order_by(GeneratedMessage.created_at.asc(), GeneratedMessage.id.asc())
            )
        )

    def acquire_generation_locks(self, usage_day: date, diagnostic_company_id: uuid.UUID | None) -> None:
        lock_names = [f"abc-prospect:ai-usage:{usage_day.isoformat()}"]
        if diagnostic_company_id is not None:
            lock_names.append(f"abc-prospect:ai-diagnostic:{diagnostic_company_id}")
        for lock_name in lock_names:
            self.session.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_name, 0))"),
                {"lock_name": lock_name},
            )

    def has_diagnostic_for_company(self, company_id: uuid.UUID) -> bool:
        return (
            self.session.scalar(
                select(GeneratedMessage.id)
                .where(
                    GeneratedMessage.company_id == company_id,
                    GeneratedMessage.draft_type == "COMMERCIAL_DIAGNOSTIC",
                )
                .limit(1)
            )
            is not None
        )

    def add(self, draft: GeneratedMessage) -> None:
        self.session.add(draft)

    def commit(self) -> None:
        self.session.commit()
