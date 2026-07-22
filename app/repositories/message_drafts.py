import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Category, Company, GeneratedMessage, WebsiteAudit


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

    def add(self, draft: GeneratedMessage) -> None:
        self.session.add(draft)

    def commit(self) -> None:
        self.session.commit()
