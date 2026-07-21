import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.authentication import require_csrf_token, require_current_user
from app.core.config import get_settings
from app.database.models import User
from app.database.session import get_database_session
from app.external.google_places import (
    GooglePlacesAuthenticationError,
    GooglePlacesClient,
    GooglePlacesConfigurationError,
    GooglePlacesError,
    GooglePlacesTemporaryError,
)
from app.repositories.external_sources import ExternalSourceRepository
from app.services.external_search import (
    ExternalImportConflictError,
    ExternalSearchInput,
    ExternalSearchService,
    ExternalSearchValidationError,
    RequestLimiter,
)

router = APIRouter(prefix="/api/external", tags=["external search"])
_settings = get_settings()
_limiter = RequestLimiter(_settings.google_places_requests_per_minute)


class ExternalPlaceResponse(BaseModel):
    external_id: str
    name: str | None
    formatted_address: str | None
    city: str | None
    state_code: str | None
    latitude: float | None
    longitude: float | None
    primary_type: str | None
    types: list[str]
    business_status: str | None
    rating: float | None
    user_rating_count: int | None
    website_uri: str | None
    google_maps_uri: str | None
    attributions: list[str]


class ExternalSearchResponse(BaseModel):
    items: list[ExternalPlaceResponse]
    next_cursor: str | None
    provider_attribution: str
    temporary: bool
    retention_seconds: int = 0


class ExternalSearchPayload(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=120)
    state_code: str = Field(min_length=2, max_length=2)
    cursor: str | None = Field(default=None, max_length=4096)
    south: float | None = None
    west: float | None = None
    north: float | None = None
    east: float | None = None


class LinkPlacePayload(BaseModel):
    company_id: uuid.UUID
    place_id: str = Field(min_length=1, max_length=300)


class LinkPlaceResponse(BaseModel):
    company_id: uuid.UUID
    source_reference_id: uuid.UUID
    place_id: str


def get_external_search_service(
    session: Annotated[Session, Depends(get_database_session)],
) -> ExternalSearchService:
    settings = get_settings()
    provider = GooglePlacesClient(
        settings.google_places_api_key,
        settings.google_places_timeout_seconds,
        settings.google_places_max_retries,
    )
    return ExternalSearchService(
        provider,
        ExternalSourceRepository(session),
        settings.app_secret_key,
        settings.google_places_page_size,
        settings.google_places_max_pages,
        _limiter,
    )


def translate_error(error: Exception) -> HTTPException:
    if isinstance(error, GooglePlacesConfigurationError):
        return HTTPException(status_code=503, detail="Pesquisa externa não configurada.")
    if isinstance(error, GooglePlacesAuthenticationError):
        return HTTPException(status_code=502, detail="Credencial do provedor externo rejeitada.")
    if isinstance(error, GooglePlacesTemporaryError):
        return HTTPException(status_code=503, detail=str(error))
    if isinstance(error, GooglePlacesError):
        return HTTPException(status_code=502, detail=str(error))
    return HTTPException(status_code=422, detail=str(error))


@router.post("/google-places/search", response_model=ExternalSearchResponse)
def search_google_places(
    payload: ExternalSearchPayload,
    user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ExternalSearchService, Depends(get_external_search_service)],
) -> ExternalSearchResponse:
    try:
        result = service.search(ExternalSearchInput(**payload.model_dump()), user.id)
        return ExternalSearchResponse(**result.__dict__)
    except (ExternalSearchValidationError, GooglePlacesError) as error:
        raise translate_error(error) from error


@router.post("/google-places/link", response_model=LinkPlaceResponse, status_code=status.HTTP_201_CREATED)
def link_google_place(
    payload: LinkPlacePayload,
    _user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
    service: Annotated[ExternalSearchService, Depends(get_external_search_service)],
) -> LinkPlaceResponse:
    try:
        reference = service.link_place(payload.company_id, payload.place_id)
    except ExternalImportConflictError as error:
        raise HTTPException(
            status_code=409,
            detail={"type": "external_id_conflict", "company_id": str(error.company_id)},
        ) from error
    except ExternalSearchValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return LinkPlaceResponse(
        company_id=reference.company_id,
        source_reference_id=reference.id,
        place_id=reference.external_id or "",
    )
