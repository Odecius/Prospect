from functools import lru_cache

from pydantic import Field
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

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def secure_session_cookie(self) -> bool:
        return self.is_production or self.session_https_only

    @property
    def website_audit_available(self) -> bool:
        return self.website_audit_enabled and (not self.is_production or self.website_audit_egress_controlled)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
