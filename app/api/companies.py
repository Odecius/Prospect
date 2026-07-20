import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.database.models import Company, User
from app.database.session import get_database_session
from app.repositories.companies import CompanyRepository
from app.services.companies import (
    CompanyInput,
    CompanyService,
    CompanyValidationError,
    ExactDuplicateError,
    PossibleDuplicateError,
)

router = APIRouter(prefix="/api", tags=["companies"])


class ReferenceResponse(BaseModel):
    id: uuid.UUID
    name: str


class CompanyPayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category_id: uuid.UUID
    city: str = Field(min_length=1, max_length=120)
    state_code: str = Field(min_length=2, max_length=2)
    source_id: uuid.UUID
    tax_id: str | None = Field(default=None, max_length=30)
    source_url: str | None = Field(default=None, max_length=2048)
    confirm_possible_duplicate: bool = False


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    tax_id: str | None
    category_id: uuid.UUID
    city: str
    state_code: str
    country_code: str
    pipeline_status: str
    archived: bool


def get_company_service(session: Annotated[Session, Depends(get_database_session)]) -> CompanyService:
    return CompanyService(CompanyRepository(session))


def company_input(payload: CompanyPayload) -> CompanyInput:
    return CompanyInput(**payload.model_dump())


def company_response(company: Company) -> CompanyResponse:
    return CompanyResponse(
        id=company.id,
        name=company.legal_or_trade_name,
        tax_id=company.tax_id_normalized,
        category_id=company.category_id,
        city=company.city,
        state_code=company.state_code,
        country_code=company.country_code,
        pipeline_status=company.pipeline_status.value,
        archived=company.archived_at is not None,
    )


def translate_company_error(error: Exception) -> HTTPException:
    if isinstance(error, ExactDuplicateError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": "exact_duplicate", "reason": error.reason, "company_id": str(error.company_id)},
        )
    if isinstance(error, PossibleDuplicateError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": "possible_duplicate", "reason": error.reason, "company_id": str(error.company_id)},
        )
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


@router.get("/categories", response_model=list[ReferenceResponse])
def categories(
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> list[ReferenceResponse]:
    return [ReferenceResponse(id=item.id, name=item.name) for item in service.list_categories()]


@router.get("/sources", response_model=list[ReferenceResponse])
def sources(
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> list[ReferenceResponse]:
    return [ReferenceResponse(id=item.id, name=item.name) for item in service.list_sources()]


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> list[CompanyResponse]:
    return [company_response(item) for item in service.list_companies()]


@router.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    company = service.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return company_response(company)


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    try:
        return company_response(service.create(company_input(payload), user))
    except (CompanyValidationError, ExactDuplicateError, PossibleDuplicateError) as error:
        raise translate_company_error(error) from error


@router.put("/companies/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: uuid.UUID,
    payload: CompanyPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    try:
        company = service.update(company_id, company_input(payload), user)
    except (CompanyValidationError, ExactDuplicateError, PossibleDuplicateError) as error:
        raise translate_company_error(error) from error
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return company_response(company)


@router.post("/companies/{company_id}/archive", response_model=CompanyResponse)
def archive_company(
    company_id: uuid.UUID,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyResponse:
    company = service.archive(company_id, user)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return company_response(company)
