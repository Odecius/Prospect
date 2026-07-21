"""Create commercial activity timeline.

Revision ID: 20260721_0006
Revises: 20260721_0005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260721_0006"
down_revision: str | None = "20260721_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "commercial_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type", sa.String(40), nullable=False),
        sa.Column("previous_status", sa.String(40), nullable=True),
        sa.Column("new_status", sa.String(40), nullable=True),
        sa.Column("outcome", sa.String(120), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=False),
        sa.Column("next_action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_company_date", "commercial_activities", ["company_id", "created_at"])
    op.create_index("ix_activities_next_action", "commercial_activities", ["next_action_at"])


def downgrade() -> None:
    op.drop_index("ix_activities_next_action", table_name="commercial_activities")
    op.drop_index("ix_activities_company_date", table_name="commercial_activities")
    op.drop_table("commercial_activities")
