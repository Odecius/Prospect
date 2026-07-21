import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.database.models import CommercialActivity, PipelineStatus, User
from app.database.session import get_database_session
from app.repositories.pipeline import PipelineRepository
from app.services.pipeline import PipelineService, PipelineValidationError

router = APIRouter(prefix="/api", tags=["pipeline"])


class ActivityPayload(BaseModel):
    activity_type: str
    notes: str = Field(min_length=1, max_length=1000)
    outcome: str | None = Field(default=None, max_length=120)
    next_action_at: datetime | None = None


class TransitionPayload(BaseModel):
    new_status: PipelineStatus
    reason: str = Field(min_length=1, max_length=1000)


class ActivityResponse(BaseModel):
    id: uuid.UUID
    activity_type: str
    previous_status: str | None
    new_status: str | None
    notes: str
    outcome: str | None
    next_action_at: datetime | None


def get_pipeline_service(session: Annotated[Session, Depends(get_database_session)]) -> PipelineService:
    return PipelineService(PipelineRepository(session))


def response(item: CommercialActivity) -> ActivityResponse:
    return ActivityResponse(
        id=item.id,
        activity_type=item.activity_type,
        previous_status=item.previous_status,
        new_status=item.new_status,
        notes=item.notes,
        outcome=item.outcome,
        next_action_at=item.next_action_at,
    )


@router.get("/companies/{company_id}/activities", response_model=list[ActivityResponse])
def list_activities(
    company_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> list[ActivityResponse]:
    return [response(item) for item in service.list_activities(company_id)]


@router.post("/companies/{company_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def add_activity(
    company_id: uuid.UUID,
    payload: ActivityPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> ActivityResponse:
    try:
        return response(service.add_activity(company_id, actor=user, **payload.model_dump()))
    except PipelineValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/companies/{company_id}/transition", response_model=ActivityResponse)
def transition(
    company_id: uuid.UUID,
    payload: TransitionPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> ActivityResponse:
    try:
        return response(service.transition(company_id, payload.new_status, payload.reason, user))
    except PipelineValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
