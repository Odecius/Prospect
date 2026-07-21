"""Add company search indexes.

Revision ID: 20260721_0004
Revises: 20260721_0003
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260721_0004"
down_revision: str | None = "20260721_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_companies_search_location", "companies", ["state_code", "city"])
    op.create_index("ix_companies_search_category_status", "companies", ["category_id", "pipeline_status"])
    op.create_index("ix_companies_created_at", "companies", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_companies_created_at", table_name="companies")
    op.drop_index("ix_companies_search_category_status", table_name="companies")
    op.drop_index("ix_companies_search_location", table_name="companies")
