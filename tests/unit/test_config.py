from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_load_infrastructure_values() -> None:
    settings = Settings(
        app_env="test",
        app_version="0.1.0",
        app_secret_key="test-only-secret-key-at-least-32-chars",
        database_url="postgresql+psycopg://test:test@localhost/test",
    )
    assert settings.app_name == "ABC Prospect"
    assert settings.app_version == "0.1.0"
    assert settings.app_env == "test"
    assert settings.log_level == "INFO"
    assert settings.session_max_age_seconds == 28_800
    assert settings.secure_session_cookie is False
    assert settings.website_audit_available is True
    assert settings.ai_drafts_available is False
    assert settings.openai_model == "gpt-5.6-luna"
    assert settings.openai_input_price_per_million_usd == Decimal("0.20")
    assert settings.openai_cached_input_price_per_million_usd == Decimal("0.02")
    assert settings.openai_output_price_per_million_usd == Decimal("1.20")


def test_production_audit_requires_confirmed_egress_control() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://abc:strong-password@db/abc",
        app_env="production",
        app_secret_key="a-production-secret-with-more-than-32-characters",
        website_audit_egress_controlled=False,
    )
    assert settings.website_audit_available is False
    assert settings.secure_session_cookie is True


@pytest.mark.parametrize(
    ("secret", "database_url"),
    [
        ("development-only-secret-key-change-me", "postgresql+psycopg://abc:strong@db/abc"),
        ("a-production-secret-with-more-than-32-characters", "sqlite:///production.db"),
        (
            "a-production-secret-with-more-than-32-characters",
            "postgresql+psycopg://abc:development-only-change-me@db/abc",
        ),
    ],
)
def test_production_rejects_unsafe_configuration(secret: str, database_url: str) -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", app_secret_key=secret, database_url=database_url)
