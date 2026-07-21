"""Create versioned opportunity scores.

Revision ID: 20260721_0005
Revises: 20260721_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260721_0005"
down_revision: str | None = "20260721_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "opportunity_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total", sa.Integer(), nullable=True),
        sa.Column("formula_version", sa.String(40), nullable=False),
        sa.Column("components", postgresql.JSONB(), nullable=False),
        sa.Column("explanation", sa.String(1000), nullable=False),
        sa.Column("calculated_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("total IS NULL OR (total >= 0 AND total <= 100)", name="ck_score_total_range"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["calculated_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_opportunity_scores_company_date", "opportunity_scores", ["company_id", "calculated_at"])
    op.create_index("ix_opportunity_scores_total", "opportunity_scores", ["total"])


def downgrade() -> None:
    op.drop_index("ix_opportunity_scores_total", table_name="opportunity_scores")
    op.drop_index("ix_opportunity_scores_company_date", table_name="opportunity_scores")
    op.drop_table("opportunity_scores")
