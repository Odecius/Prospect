import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.database.models import User
from app.database.session import get_database_session
from app.repositories.reporting import ReportingRepository
from app.services.reporting import ExportFilters, ReportingService, ReportingValidationError

router = APIRouter(prefix="/api/reporting", tags=["reporting"])


class DashboardResponse(BaseModel):
    total_active: int
    do_not_contact: int
    without_website: int
    with_score: int
    with_completed_audit: int
    with_approved_content: int
    by_pipeline: dict[str, int]


class ValidationSnapshotResponse(BaseModel):
    started_at: datetime
    ended_at: datetime
    companies_created: int
    companies_scored: int
    companies_with_activity: int
    companies_contacted: int
    companies_replied: int
    companies_with_meeting: int
    companies_progressed: int
    companies_won: int
    companies_marked_do_not_contact: int
    scored_with_positive_progression: int
    contact_response_rate: float | None
    score_progression_rate: float | None


class ExportPayload(BaseModel):
    query: str | None = Field(default=None, max_length=200)
    category_id: uuid.UUID | None = None
    state_code: str | None = Field(default=None, min_length=2, max_length=2)
    pipeline_status: str | None = Field(default=None, max_length=40)


def get_reporting_service(session: Annotated[Session, Depends(get_database_session)]) -> ReportingService:
    return ReportingService(ReportingRepository(session))


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
) -> DashboardResponse:
    return DashboardResponse(**service.dashboard())


@router.get("/validation", response_model=ValidationSnapshotResponse)
def validation_snapshot(
    started_at: datetime,
    ended_at: datetime,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
) -> ValidationSnapshotResponse:
    try:
        snapshot = service.validation_snapshot(started_at, ended_at)
    except ReportingValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ValidationSnapshotResponse(**snapshot)


@router.post("/companies.csv")
def export_companies_csv(
    payload: ExportPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
) -> Response:
    try:
        content = service.export_csv(ExportFilters(**payload.model_dump()), user)
    except (ValueError, ReportingValidationError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="abc-prospect-segmento.csv"'},
    )
