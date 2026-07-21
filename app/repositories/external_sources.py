import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Company, CompanySourceRef, DataSource


class ExternalSourceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def google_source(self) -> DataSource | None:
        return self.session.scalar(select(DataSource).where(DataSource.name == "Google Places API (New)"))

    def find_external_id(self, source_id: uuid.UUID, external_id: str) -> CompanySourceRef | None:
        return self.session.scalar(
            select(CompanySourceRef).where(
                CompanySourceRef.data_source_id == source_id,
                CompanySourceRef.external_id == external_id,
            )
        )

    def add(self, reference: CompanySourceRef) -> None:
        self.session.add(reference)

    def commit(self) -> None:
        self.session.commit()
