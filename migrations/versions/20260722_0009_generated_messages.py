"""Create human-reviewed AI message drafts.

Revision ID: 20260722_0009
Revises: 20260722_0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260722_0009"
down_revision: str | None = "20260722_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    status_for_create = postgresql.ENUM("DRAFT", "APPROVED", "REJECTED", name="message_draft_status")
    status_for_create.create(op.get_bind())
    status = postgresql.ENUM("DRAFT", "APPROVED", "REJECTED", name="message_draft_status", create_type=False)
    op.create_table(
        "generated_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("draft_type", sa.String(40), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(80), nullable=False),
        sa.Column("prompt_version", sa.String(40), nullable=False),
        sa.Column("generated_content", postgresql.JSONB(), nullable=False),
        sa.Column("reviewed_content", postgresql.JSONB()),
        sa.Column("input_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("usage", postgresql.JSONB(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewed_by_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("review_reason", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_generated_messages_company_created", "generated_messages", ["company_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_generated_messages_company_created", table_name="generated_messages")
    op.drop_table("generated_messages")
    postgresql.ENUM(name="message_draft_status").drop(op.get_bind())
