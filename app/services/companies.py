import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError

from app.database.models import Category, Company, CompanySourceRef, DataSource, PipelineStatus, User
from app.domain.normalization import normalize_cnpj, normalize_state_code, normalize_text
from app.repositories.companies import CompanyRepository


class CompanyValidationError(Exception):
    pass


class ExactDuplicateError(Exception):
    def __init__(self, company_id: uuid.UUID, reason: str) -> None:
        self.company_id = company_id
        self.reason = reason


class PossibleDuplicateError(Exception):
    def __init__(self, company_id: uuid.UUID, reason: str) -> None:
        self.company_id = company_id
        self.reason = reason


@dataclass(frozen=True)
class CompanyInput:
    name: str
    category_id: uuid.UUID
    city: str
    state_code: str
    source_id: uuid.UUID
    tax_id: str | None = None
    source_url: str | None = None
    confirm_possible_duplicate: bool = False


class CompanyService:
    def __init__(self, repository: CompanyRepository) -> None:
        self.repository = repository

    def list_categories(self) -> list[Category]:
        return self.repository.list_categories()

    def list_sources(self) -> list[DataSource]:
        return self.repository.list_sources()

    def list_companies(self) -> list[Company]:
        return self.repository.list_companies()

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.repository.get_company(company_id)

    def _validated(self, data: CompanyInput) -> tuple[str, str, str, str | None, Category, DataSource]:
        name = " ".join(data.name.strip().split())
        city = " ".join(data.city.strip().split())
        if not name or len(name) > 200 or not city or len(city) > 120:
            raise CompanyValidationError("Nome e cidade são obrigatórios e devem respeitar os limites.")
        try:
            state_code = normalize_state_code(data.state_code)
            tax_id = normalize_cnpj(data.tax_id)
        except ValueError as error:
            raise CompanyValidationError(str(error)) from error
        category = self.repository.get_category(data.category_id)
        source = self.repository.get_source(data.source_id)
        if category is None or not category.active:
            raise CompanyValidationError("Categoria ativa obrigatória.")
        if source is None or not source.active:
            raise CompanyValidationError("Origem ativa obrigatória.")
        if data.source_url and not data.source_url.startswith(("http://", "https://")):
            raise CompanyValidationError("A URL da origem deve começar com http:// ou https://.")
        return name, city, state_code, tax_id, category, source

    def _check_duplicates(
        self,
        name_normalized: str,
        city: str,
        state_code: str,
        tax_id: str | None,
        confirm: bool,
        excluded_id: uuid.UUID | None = None,
    ) -> None:
        if tax_id:
            exact = self.repository.find_by_tax_id(tax_id, excluded_id)
            if exact:
                raise ExactDuplicateError(exact.id, "CNPJ normalizado já cadastrado.")
        probable = self.repository.find_name_location_match(name_normalized, city, state_code, excluded_id)
        if probable and not confirm:
            raise PossibleDuplicateError(probable.id, "Nome normalizado, cidade e UF coincidem.")

    def create(self, data: CompanyInput, actor: User) -> Company:
        name, city, state_code, tax_id, _category, _source = self._validated(data)
        name_normalized = normalize_text(name)
        self._check_duplicates(name_normalized, city, state_code, tax_id, data.confirm_possible_duplicate)
        company = Company(
            legal_or_trade_name=name,
            name_normalized=name_normalized,
            tax_id_normalized=tax_id,
            category_id=data.category_id,
            city=city,
            state_code=state_code,
            country_code="BR",
            pipeline_status=PipelineStatus.NEW,
            created_by_user_id=actor.id,
            updated_by_user_id=actor.id,
        )
        try:
            self.repository.add(company)
            self.repository.flush()
            self.repository.add(
                CompanySourceRef(
                    company_id=company.id,
                    data_source_id=data.source_id,
                    source_url=data.source_url,
                    observed_at=datetime.now(UTC),
                )
            )
            self.repository.commit()
        except IntegrityError as error:
            self.repository.rollback()
            raise CompanyValidationError("Não foi possível guardar a empresa devido a um conflito de dados.") from error
        return company

    def update(self, company_id: uuid.UUID, data: CompanyInput, actor: User) -> Company | None:
        company = self.repository.get_company(company_id)
        if company is None:
            return None
        name, city, state_code, tax_id, _category, _source = self._validated(data)
        normalized = normalize_text(name)
        self._check_duplicates(normalized, city, state_code, tax_id, data.confirm_possible_duplicate, company.id)
        company.legal_or_trade_name = name
        company.name_normalized = normalized
        company.tax_id_normalized = tax_id
        company.category_id = data.category_id
        company.city = city
        company.state_code = state_code
        company.updated_by_user_id = actor.id
        self.repository.add(
            CompanySourceRef(
                company_id=company.id,
                data_source_id=data.source_id,
                source_url=data.source_url,
                observed_at=datetime.now(UTC),
            )
        )
        self.repository.commit()
        return company

    def archive(self, company_id: uuid.UUID, actor: User) -> Company | None:
        company = self.repository.get_company(company_id)
        if company is None:
            return None
        company.archived_at = datetime.now(UTC)
        company.pipeline_status = PipelineStatus.ARCHIVED
        company.updated_by_user_id = actor.id
        self.repository.commit()
        return company
