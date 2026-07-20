from app.core.config import Settings


def test_settings_load_infrastructure_values() -> None:
    settings = Settings(database_url="postgresql+psycopg://test:test@localhost/test")
    assert settings.app_name == "ABC Prospect"
    assert settings.app_version == "0.1.0"
    assert settings.app_env == "test"
    assert settings.log_level == "INFO"
    assert settings.session_max_age_seconds == 28_800
    assert settings.secure_session_cookie is False
