import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.openai_responses import OpenAIConfigurationError, OpenAIResponseError, OpenAIResponsesClient
from app.api.authentication import require_csrf_token, require_current_user
from app.core.config import get_settings
from app.database.models import GeneratedMessage, MessageDraftStatus, User
from app.database.session import get_database_session
from app.repositories.message_drafts import MessageDraftRepository
from app.services.external_search import RequestLimiter
from app.services.message_drafts import DraftReviewInput, MessageDraftService, MessageDraftValidationError

router = APIRouter(prefix="/api", tags=["AI message drafts"])
_settings = get_settings()
_limiter = RequestLimiter(_settings.ai_drafts_requests_per_minute)


class DraftResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    status: str
    draft_type: str
    provider: str
    model: str
    prompt_version: str
    generated_content: dict
    reviewed_content: dict | None
    input_snapshot: dict
    usage: dict
    review_reason: str | None
    created_at: str
    reviewed_at: str | None


class DraftReviewPayload(BaseModel):
    decision: MessageDraftStatus
    reason: str = Field(min_length=1, max_length=500)
    subject: str | None = Field(default=None, max_length=120)
    body: str | None = Field(default=None, max_length=1500)


def get_message_draft_service(
    session: Annotated[Session, Depends(get_database_session)],
) -> MessageDraftService:
    settings = get_settings()
    provider = OpenAIResponsesClient(
        settings.openai_api_key,
        settings.openai_model,
        settings.openai_timeout_seconds,
        settings.openai_max_retries,
        settings.openai_max_output_tokens,
    )
    return MessageDraftService(
        MessageDraftRepository(session),
        provider,
        _limiter,
        settings.ai_drafts_available,
    )


def response(draft: GeneratedMessage) -> DraftResponse:
    return DraftResponse(
        id=draft.id,
        company_id=draft.company_id,
        status=draft.status.value,
        draft_type=draft.draft_type,
        provider=draft.provider,
        model=draft.model,
        prompt_version=draft.prompt_version,
        generated_content=draft.generated_content,
        reviewed_content=draft.reviewed_content,
        input_snapshot=draft.input_snapshot,
        usage=draft.usage,
        review_reason=draft.review_reason,
        created_at=draft.created_at.isoformat(),
        reviewed_at=draft.reviewed_at.isoformat() if draft.reviewed_at else None,
    )


@router.get("/companies/{company_id}/message-drafts", response_model=list[DraftResponse])
def list_message_drafts(
    company_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[MessageDraftService, Depends(get_message_draft_service)],
) -> list[DraftResponse]:
    return [response(item) for item in service.list_drafts(company_id)]


@router.post(
    "/companies/{company_id}/message-drafts",
    response_model=DraftResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message_draft(
    company_id: uuid.UUID,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[MessageDraftService, Depends(get_message_draft_service)],
) -> DraftResponse:
    try:
        return response(service.generate(company_id, user))
    except MessageDraftValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except OpenAIConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except OpenAIResponseError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.post("/message-drafts/{draft_id}/review", response_model=DraftResponse)
def review_message_draft(
    draft_id: uuid.UUID,
    payload: DraftReviewPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[MessageDraftService, Depends(get_message_draft_service)],
) -> DraftResponse:
    try:
        return response(service.review(draft_id, DraftReviewInput(**payload.model_dump()), user))
    except MessageDraftValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
