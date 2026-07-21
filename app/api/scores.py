import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.database.models import OpportunityScore, User
from app.database.session import get_database_session
from app.repositories.scores import ScoreRepository
from app.services.scores import ScoreInput, ScoreService, ScoreValidationError

router = APIRouter(prefix="/api", tags=["scores"])


class ScorePayload(BaseModel):
    fit: int | None = Field(default=None, ge=0, le=100)
    reputation: int | None = Field(default=None, ge=0, le=100)
    digital_gap: int | None = Field(default=None, ge=0, le=100)
    rationale: str = Field(min_length=1, max_length=1000)


class ScoreResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    total: int | None
    formula_version: str
    components: dict
    explanation: str


def get_score_service(session: Annotated[Session, Depends(get_database_session)]) -> ScoreService:
    return ScoreService(ScoreRepository(session))


def response(score: OpportunityScore) -> ScoreResponse:
    return ScoreResponse(
        id=score.id,
        company_id=score.company_id,
        total=score.total,
        formula_version=score.formula_version,
        components=score.components,
        explanation=score.explanation,
    )


@router.get("/companies/{company_id}/scores", response_model=list[ScoreResponse])
def list_scores(
    company_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[ScoreService, Depends(get_score_service)],
) -> list[ScoreResponse]:
    return [response(item) for item in service.list_scores(company_id)]


@router.post("/companies/{company_id}/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(
    company_id: uuid.UUID,
    payload: ScorePayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ScoreService, Depends(get_score_service)],
) -> ScoreResponse:
    try:
        return response(service.calculate(company_id, ScoreInput(**payload.model_dump()), user))
    except ScoreValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
