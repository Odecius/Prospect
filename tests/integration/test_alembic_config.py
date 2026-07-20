from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_linear_company_registration_revision() -> None:
    config = Config("alembic.ini")
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_heads() == ["20260720_0002"]
    assert scripts.get_bases() == ["20260720_0001"]
