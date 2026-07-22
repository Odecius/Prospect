import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Company, Contact, WebsiteAudit


class WebsiteAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def get_contact(self, contact_id: uuid.UUID) -> Contact | None:
        return self.session.get(Contact, contact_id)

    def latest_for_contact(self, contact_id: uuid.UUID) -> WebsiteAudit | None:
        return self.session.scalar(
            select(WebsiteAudit)
            .where(WebsiteAudit.contact_id == contact_id)
            .order_by(WebsiteAudit.created_at.desc(), WebsiteAudit.id.desc())
            .limit(1)
        )

    def list_for_company(self, company_id: uuid.UUID) -> list[WebsiteAudit]:
        return list(
            self.session.scalars(
                select(WebsiteAudit)
                .where(WebsiteAudit.company_id == company_id)
                .order_by(WebsiteAudit.created_at.desc(), WebsiteAudit.id.desc())
                .limit(50)
            )
        )

    def add(self, audit: WebsiteAudit) -> None:
        self.session.add(audit)

    def commit(self) -> None:
        self.session.commit()

    def now(self) -> datetime:
        from datetime import UTC

        return datetime.now(UTC)
