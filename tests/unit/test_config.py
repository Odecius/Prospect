from app.core.config import Settings


def test_settings_load_infrastructure_values() -> None:
    settings = Settings(database_url="postgresql+psycopg://test:test@localhost/test")
    assert settings.app_name == "ABC Prospect"
    assert settings.app_version == "0.1.0"
    assert settings.app_env == "test"
    assert settings.log_level == "INFO"
    assert settings.session_max_age_seconds == 28_800
    assert settings.secure_session_cookie is False
    assert settings.website_audit_available is True
    assert settings.ai_drafts_available is False
    assert settings.openai_model == "gpt-5.6-luna"


def test_production_audit_requires_confirmed_egress_control() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        app_env="production",
        website_audit_egress_controlled=False,
    )
    assert settings.website_audit_available is False
