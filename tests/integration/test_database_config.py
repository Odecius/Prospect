from sqlalchemy.engine import make_url

from app.database.base import Base
from app.database.session import create_database_engine


def test_postgresql_engine_configuration() -> None:
    database_url = "postgresql+psycopg://test:test@localhost/test"
    engine = create_database_engine(database_url)

    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg"
    assert make_url(database_url).database == "test"
    engine.dispose()


def test_sqlalchemy_metadata_contains_authorized_sprint_four_entities() -> None:
    assert set(Base.metadata.tables) == {
        "users",
        "categories",
        "data_sources",
        "companies",
        "company_source_refs",
        "contacts",
        "duplicate_candidates",
        "company_merge_audits",
        "opportunity_scores",
        "commercial_activities",
        "website_audits",
        "generated_messages",
    }
