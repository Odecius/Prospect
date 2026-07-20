import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Category, Company, CompanySourceRef, DataSource


class CompanyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_categories(self) -> list[Category]:
        return list(self.session.scalars(select(Category).where(Category.active.is_(True)).order_by(Category.name)))

    def list_sources(self) -> list[DataSource]:
        return list(
            self.session.scalars(select(DataSource).where(DataSource.active.is_(True)).order_by(DataSource.name))
        )

    def get_category(self, category_id: uuid.UUID) -> Category | None:
        return self.session.get(Category, category_id)

    def get_source(self, source_id: uuid.UUID) -> DataSource | None:
        return self.session.get(DataSource, source_id)

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def list_companies(self) -> list[Company]:
        return list(self.session.scalars(select(Company).order_by(Company.created_at.desc())))

    def find_by_tax_id(self, tax_id: str, excluded_id: uuid.UUID | None = None) -> Company | None:
        query = select(Company).where(Company.tax_id_normalized == tax_id)
        if excluded_id is not None:
            query = query.where(Company.id != excluded_id)
        return self.session.scalar(query)

    def find_name_location_match(
        self, name_normalized: str, city: str, state_code: str, excluded_id: uuid.UUID | None = None
    ) -> Company | None:
        query = select(Company).where(
            Company.name_normalized == name_normalized,
            Company.city == city,
            Company.state_code == state_code,
            Company.archived_at.is_(None),
        )
        if excluded_id is not None:
            query = query.where(Company.id != excluded_id)
        return self.session.scalar(query)

    def add(self, value: Company | CompanySourceRef) -> None:
        self.session.add(value)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
