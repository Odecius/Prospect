import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database.models import Category, CommercialActivity, Company, CompanySourceRef, DataSource


class CompanyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_categories(self) -> list[Category]:
        return list(self.session.scalars(select(Category).where(Category.active.is_(True)).order_by(Category.name)))

    def list_sources(self) -> list[DataSource]:
        return list(
            self.session.scalars(
                select(DataSource)
                .where(DataSource.active.is_(True), DataSource.collection_method == "HUMAN_ENTRY")
                .order_by(DataSource.name)
            )
        )

    def get_category(self, category_id: uuid.UUID) -> Category | None:
        return self.session.get(Category, category_id)

    def get_source(self, source_id: uuid.UUID) -> DataSource | None:
        return self.session.get(DataSource, source_id)

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def list_companies(self) -> list[Company]:
        return list(self.session.scalars(select(Company).order_by(Company.created_at.desc())))

    def search_companies(
        self,
        query: str | None,
        category_id: uuid.UUID | None,
        state_code: str | None,
        pipeline_status: str | None,
        include_archived: bool,
        sort: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Company], int]:
        statement = select(Company)
        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                or_(
                    Company.name_normalized.ilike(pattern),
                    Company.city.ilike(pattern),
                    Company.tax_id_normalized == query,
                )
            )
        if category_id:
            statement = statement.where(Company.category_id == category_id)
        if state_code:
            statement = statement.where(Company.state_code == state_code)
        if pipeline_status:
            statement = statement.where(Company.pipeline_status == pipeline_status)
        if not include_archived:
            statement = statement.where(Company.archived_at.is_(None))
        total = self.session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        ordering = {
            "name": Company.legal_or_trade_name.asc(),
            "newest": Company.created_at.desc(),
            "oldest": Company.created_at.asc(),
            "city": Company.city.asc(),
        }[sort]
        items = list(
            self.session.scalars(
                statement.order_by(ordering, Company.id).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total

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

    def add(self, value: Company | CompanySourceRef | CommercialActivity) -> None:
        self.session.add(value)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
