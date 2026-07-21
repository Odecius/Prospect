import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import CommercialActivity, Company


class PipelineRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def list_activities(self, company_id: uuid.UUID) -> list[CommercialActivity]:
        return list(
            self.session.scalars(
                select(CommercialActivity)
                .where(CommercialActivity.company_id == company_id)
                .order_by(CommercialActivity.created_at.desc(), CommercialActivity.id.desc())
            )
        )

    def add(self, activity: CommercialActivity) -> None:
        self.session.add(activity)

    def commit(self) -> None:
        self.session.commit()
