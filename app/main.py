from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.authentication import router as authentication_router
from app.api.companies import router as companies_router
from app.api.contacts import router as contacts_router
from app.api.external_search import router as external_search_router
from app.api.health import router as health_router
from app.api.message_drafts import router as message_drafts_router
from app.api.pipeline import router as pipeline_router
from app.api.scores import router as scores_router
from app.api.web import router as web_router
from app.api.website_audits import router as website_audits_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Aplicação interna do ABC Prospect.",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.app_secret_key,
        session_cookie="abc_prospect_session",
        max_age=settings.session_max_age_seconds,
        same_site="lax",
        https_only=settings.secure_session_cookie,
    )
    application.include_router(health_router)
    application.include_router(authentication_router)
    application.include_router(companies_router)
    application.include_router(contacts_router)
    application.include_router(external_search_router)
    application.include_router(message_drafts_router)
    application.include_router(scores_router)
    application.include_router(pipeline_router)
    application.include_router(website_audits_router)
    application.include_router(web_router)
    application.mount("/static", StaticFiles(directory="app/static"), name="static")
    return application


app = create_app()
