import os
import uuid

import pytest
from sqlalchemy.orm import Session

from app.database.models import (
    Category,
    Company,
    Contact,
    ContactType,
    OpportunityScore,
    PipelineStatus,
    User,
)
from app.database.session import create_database_engine
from app.repositories.reporting import ReportingRepository

pytestmark = pytest.mark.skipif(os.getenv("RUN_DATABASE_TESTS") != "true", reason="requer PostgreSQL descartável")


def test_reporting_queries_reconcile_against_postgresql() -> None:
    engine = create_database_engine(os.environ["DATABASE_URL"])
    suffix = uuid.uuid4().hex
    with Session(engine) as session:
        user = User(
            email_normalized=f"reporting-{suffix}@example.invalid",
            display_name="Teste de reporting",
            password_hash="test-only-hash",
        )
        category = Category(name=f"Categoria {suffix}", name_normalized=f"categoria {suffix}", slug=f"cat-{suffix}")
        session.add_all([user, category])
        session.flush()
        new_company = Company(
            legal_or_trade_name="Empresa com site",
            name_normalized=f"empresa com site {suffix}",
            category_id=category.id,
            city="Recife",
            state_code="PE",
            pipeline_status=PipelineStatus.NEW,
            created_by_user_id=user.id,
            updated_by_user_id=user.id,
        )
        blocked_company = Company(
            legal_or_trade_name="Empresa sem site",
            name_normalized=f"empresa sem site {suffix}",
            category_id=category.id,
            city="Recife",
            state_code="PE",
            pipeline_status=PipelineStatus.DO_NOT_CONTACT,
            created_by_user_id=user.id,
            updated_by_user_id=user.id,
        )
        session.add_all([new_company, blocked_company])
        session.flush()
        session.add_all(
            [
                Contact(
                    company_id=new_company.id,
                    contact_type=ContactType.WEBSITE,
                    value="https://example.invalid",
                    value_normalized="example.invalid",
                    is_primary=True,
                    created_by_user_id=user.id,
                ),
                OpportunityScore(
                    company_id=blocked_company.id,
                    total=75,
                    formula_version="test-v1",
                    components={},
                    explanation="Dado fictício.",
                    calculated_by_user_id=user.id,
                ),
            ]
        )
        session.flush()

        repository = ReportingRepository(session)
        dashboard = repository.dashboard()
        rows, total = repository.export_rows(None, category.id, "PE", None)

        assert dashboard["total_active"] >= 2
        assert dashboard["do_not_contact"] >= 1
        assert dashboard["without_website"] >= 1
        assert dashboard["with_score"] >= 1
        assert total == 2
        assert {row[0] for row in rows} == {"Empresa com site", "Empresa sem site"}
        session.rollback()
    engine.dispose()
