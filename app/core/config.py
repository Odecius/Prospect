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

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def secure_session_cookie(self) -> bool:
        return self.is_production or self.session_https_only


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
