import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Company, OpportunityScore


class ScoreRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def list_scores(self, company_id: uuid.UUID) -> list[OpportunityScore]:
        return list(
            self.session.scalars(
                select(OpportunityScore)
                .where(OpportunityScore.company_id == company_id)
                .order_by(OpportunityScore.calculated_at.desc(), OpportunityScore.id.desc())
            )
        )

    def add(self, score: OpportunityScore) -> None:
        self.session.add(score)

    def commit(self) -> None:
        self.session.commit()
