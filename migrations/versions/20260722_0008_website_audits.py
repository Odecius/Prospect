"""Create immutable website audit snapshots.

Revision ID: 20260722_0008
Revises: 20260721_0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260722_0008"
down_revision: str | None = "20260721_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    audit_status = postgresql.ENUM("COMPLETED", "FAILED", name="website_audit_status", create_type=False)
    audit_status_for_create = postgresql.ENUM("COMPLETED", "FAILED", name="website_audit_status")
    audit_status_for_create.create(op.get_bind())
    op.create_table(
        "website_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_url", sa.Text(), nullable=False),
        sa.Column("final_url", sa.Text()),
        sa.Column("status", audit_status, nullable=False),
        sa.Column("http_status", sa.Integer()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("findings", postgresql.JSONB(), nullable=False),
        sa.Column("error_code", sa.String(60)),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_website_audits_company_created", "website_audits", ["company_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_website_audits_company_created", table_name="website_audits")
    op.drop_table("website_audits")
    postgresql.ENUM(name="website_audit_status").drop(op.get_bind())
