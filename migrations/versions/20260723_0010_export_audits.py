"""Create manual export audit trail.

Revision ID: 20260723_0010
Revises: 20260722_0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260723_0010"
down_revision: str | None = "20260722_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "export_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("export_type", sa.String(40), nullable=False),
        sa.Column("filters", postgresql.JSONB(), nullable=False),
        sa.Column("fields", postgresql.JSONB(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("row_count >= 0", name="ck_export_audits_row_count"),
    )
    op.create_index("ix_export_audits_created_at", "export_audits", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_export_audits_created_at", table_name="export_audits")
    op.drop_table("export_audits")
