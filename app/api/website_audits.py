import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.core.config import get_settings
from app.database.models import User, WebsiteAudit
from app.database.session import get_database_session
from app.repositories.website_audits import WebsiteAuditRepository
from app.services.external_search import RequestLimiter
from app.services.website_audits import (
    WebsiteAuditFetcher,
    WebsiteAuditService,
    WebsiteAuditValidationError,
)

router = APIRouter(prefix="/api", tags=["website audits"])
_settings = get_settings()
_limiter = RequestLimiter(_settings.website_audit_requests_per_minute)


class WebsiteAuditPayload(BaseModel):
    contact_id: uuid.UUID


class WebsiteAuditResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    contact_id: uuid.UUID
    requested_url: str
    final_url: str | None
    status: str
    http_status: int | None
    duration_ms: int | None
    findings: dict
    error_code: str | None
    created_at: str


def get_website_audit_service(
    session: Annotated[Session, Depends(get_database_session)],
) -> WebsiteAuditService:
    settings = get_settings()
    return WebsiteAuditService(
        WebsiteAuditRepository(session),
        WebsiteAuditFetcher(
            settings.website_audit_timeout_seconds,
            settings.website_audit_max_bytes,
            settings.website_audit_max_redirects,
        ),
        _limiter,
        settings.website_audit_domain_cooldown_seconds,
        settings.website_audit_available,
    )


def response(audit: WebsiteAudit) -> WebsiteAuditResponse:
    return WebsiteAuditResponse(
        id=audit.id,
        company_id=audit.company_id,
        contact_id=audit.contact_id,
        requested_url=audit.requested_url,
        final_url=audit.final_url,
        status=audit.status.value,
        http_status=audit.http_status,
        duration_ms=audit.duration_ms,
        findings=audit.findings,
        error_code=audit.error_code,
        created_at=audit.created_at.isoformat(),
    )


@router.get("/companies/{company_id}/website-audits", response_model=list[WebsiteAuditResponse])
def list_website_audits(
    company_id: uuid.UUID,
    _user: Annotated[User, Depends(require_current_user)],
    service: Annotated[WebsiteAuditService, Depends(get_website_audit_service)],
) -> list[WebsiteAuditResponse]:
    return [response(item) for item in service.list_audits(company_id)]


@router.post(
    "/companies/{company_id}/website-audits",
    response_model=WebsiteAuditResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_website_audit(
    company_id: uuid.UUID,
    payload: WebsiteAuditPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[WebsiteAuditService, Depends(get_website_audit_service)],
) -> WebsiteAuditResponse:
    try:
        return response(service.audit(company_id, payload.contact_id, user))
    except WebsiteAuditValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
