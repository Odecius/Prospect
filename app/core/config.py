from decimal import Decimal
from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ABC Prospect"
    app_version: str = "0.1.0"
    app_env: str = "development"
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    database_url: str
    app_secret_key: str = Field(min_length=32)
    session_https_only: bool = False
    session_max_age_seconds: int = Field(default=28_800, ge=300, le=86_400)
    google_places_api_key: str | None = None
    google_places_timeout_seconds: float = Field(default=5.0, ge=1, le=15)
    google_places_max_retries: int = Field(default=2, ge=0, le=3)
    google_places_page_size: int = Field(default=10, ge=1, le=20)
    google_places_max_pages: int = Field(default=2, ge=1, le=3)
    google_places_requests_per_minute: int = Field(default=5, ge=1, le=20)
    website_audit_enabled: bool = True
    website_audit_egress_controlled: bool = False
    website_audit_timeout_seconds: float = Field(default=5.0, ge=1, le=10)
    website_audit_max_bytes: int = Field(default=524_288, ge=65_536, le=1_048_576)
    website_audit_max_redirects: int = Field(default=3, ge=0, le=5)
    website_audit_requests_per_minute: int = Field(default=5, ge=1, le=20)
    website_audit_domain_cooldown_seconds: int = Field(default=60, ge=30, le=3600)
    ai_drafts_enabled: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    # Standard, short-context prices per 1M tokens, verified 2026-07-31.
    # Source: https://developers.openai.com/api/docs/pricing
    openai_input_price_per_million_usd: Decimal = Field(default=Decimal("0.20"), ge=0)
    openai_cached_input_price_per_million_usd: Decimal = Field(default=Decimal("0.02"), ge=0)
    openai_output_price_per_million_usd: Decimal = Field(default=Decimal("1.20"), ge=0)
    openai_timeout_seconds: float = Field(default=15.0, ge=3, le=30)
    openai_max_retries: int = Field(default=1, ge=0, le=2)
    openai_max_output_tokens: int = Field(default=300, ge=100, le=800)
    ai_drafts_requests_per_minute: int = Field(default=3, ge=1, le=10)

    @model_validator(mode="after")
    def reject_unsafe_production_configuration(self) -> "Settings":
        if not self.is_production:
            return self

        secret = self.app_secret_key.lower()
        if any(marker in secret for marker in ("development", "change-me", "test-only")):
            raise ValueError("APP_SECRET_KEY insegura para produção")
        if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL de produção deve usar PostgreSQL")
        if "development-only-change-me" in self.database_url:
            raise ValueError("DATABASE_URL contém credencial de desenvolvimento")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def secure_session_cookie(self) -> bool:
        return self.is_production or self.session_https_only

    @property
    def website_audit_available(self) -> bool:
        return self.website_audit_enabled and (not self.is_production or self.website_audit_egress_controlled)

    @property
    def ai_drafts_available(self) -> bool:
        return self.ai_drafts_enabled and bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
