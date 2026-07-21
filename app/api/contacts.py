import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.database.models import Contact, ContactType, DuplicateCandidate, DuplicateStatus, User
from app.database.session import get_database_session
from app.repositories.contacts import ContactRepository
from app.services.contacts import ContactService, ContactValidationError

router = APIRouter(prefix="/api", tags=["contacts and duplicates"])


class ContactPayload(BaseModel):
    contact_type: ContactType
    value: str = Field(min_length=1, max_length=500)
    is_primary: bool = False
    person_name: str | None = Field(default=None, max_length=120)
    job_title: str | None = Field(default=None, max_length=120)


class ContactResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    contact_type: str
    value: str
    is_primary: bool
    person_name: str | None
    job_title: str | None
    invalidated: bool


class ReviewPayload(BaseModel):
    status: DuplicateStatus
    reason: str = Field(min_length=1, max_length=500)


class MergePayload(BaseModel):
    survivor_company_id: uuid.UUID
    reason: str = Field(min_length=1, max_length=500)


class CandidateResponse(BaseModel):
    id: uuid.UUID
    company_a_id: uuid.UUID
    company_b_id: uuid.UUID
    level: str
    status: str
    signals: dict
    decision_reason: str | None


def get_contact_service(session: Annotated[Session, Depends(get_database_session)]) -> ContactService:
    return ContactService(ContactRepository(session))


def contact_response(contact: Contact) -> ContactResponse:
    return ContactResponse(
        id=contact.id,
        company_id=contact.company_id,
        contact_type=contact.contact_type.value,
        value=contact.value,
        is_primary=contact.is_primary,
        person_name=contact.person_name,
        job_title=contact.job_title,
        invalidated=contact.invalidated_at is not None,
    )


def candidate_response(candidate: DuplicateCandidate) -> CandidateResponse:
    return CandidateResponse(
        id=candidate.id,
        company_a_id=candidate.company_a_id,
        company_b_id=candidate.company_b_id,
        level=candidate.level.value,
        status=candidate.status.value,
        signals=candidate.signals,
        decision_reason=candidate.decision_reason,
    )


@router.get("/companies/{company_id}/contacts", response_model=list[ContactResponse])
def list_contacts(
    company_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> list[ContactResponse]:
    return [contact_response(item) for item in service.list_contacts(company_id)]


@router.post("/companies/{company_id}/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    company_id: uuid.UUID,
    payload: ContactPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactResponse:
    try:
        return contact_response(service.create_contact(company_id, actor=user, **payload.model_dump()))
    except ContactValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/contacts/{contact_id}/invalidate", response_model=ContactResponse)
def invalidate_contact(
    contact_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactResponse:
    contact = service.invalidate(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado.")
    return contact_response(contact)


@router.get("/duplicate-candidates", response_model=list[CandidateResponse])
def list_duplicate_candidates(
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> list[CandidateResponse]:
    return [candidate_response(item) for item in service.list_candidates()]


@router.post("/duplicate-candidates/{candidate_id}/review", response_model=CandidateResponse)
def review_duplicate_candidate(
    candidate_id: uuid.UUID,
    payload: ReviewPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> CandidateResponse:
    try:
        candidate = service.review_candidate(candidate_id, payload.status, payload.reason, user)
    except ContactValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidato não encontrado.")
    return candidate_response(candidate)


@router.post("/duplicate-candidates/{candidate_id}/merge", status_code=status.HTTP_201_CREATED)
def merge_duplicate_candidate(
    candidate_id: uuid.UUID,
    payload: MergePayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> dict[str, str]:
    try:
        audit = service.merge(candidate_id, payload.survivor_company_id, payload.reason, user)
    except ContactValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"audit_id": str(audit.id), "status": "merged"}
