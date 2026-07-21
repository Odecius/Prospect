"""Create contacts and duplicate review.

Revision ID: 20260721_0003
Revises: 20260720_0002
Create Date: 2026-07-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260721_0003"
down_revision: str | None = "20260720_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

contact_type = postgresql.ENUM("PHONE", "EMAIL", "WEBSITE", "INSTAGRAM", name="contact_type", create_type=False)
duplicate_level = postgresql.ENUM(
    "EXACT", "PROBABLE", "POSSIBLE", "DISTINCT", name="duplicate_level", create_type=False
)
duplicate_status = postgresql.ENUM(
    "OPEN",
    "DISTINCT",
    "CONFIRMED_DUPLICATE",
    "MERGE_REQUESTED",
    "CLOSED",
    name="duplicate_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    contact_type.create(bind, checkfirst=True)
    duplicate_level.create(bind, checkfirst=True)
    duplicate_status.create(bind, checkfirst=True)
    op.add_column("companies", sa.Column("merged_into_company_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_companies_merged_into", "companies", "companies", ["merged_into_company_id"], ["id"], ondelete="RESTRICT"
    )
    op.add_column("company_source_refs", sa.Column("external_id", sa.String(300), nullable=True))
    op.add_column("company_source_refs", sa.Column("raw_name", sa.String(300), nullable=True))
    op.add_column("company_source_refs", sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "uq_source_external_id",
        "company_source_refs",
        ["data_source_id", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )
    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_type", contact_type, nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("value_normalized", sa.String(500), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("person_name", sa.String(120), nullable=True),
        sa.Column("job_title", sa.String(120), nullable=True),
        sa.Column("source_ref_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_ref_id"], ["company_source_refs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "contact_type", "value_normalized", name="uq_company_contact_value"),
    )
    op.create_index(
        "uq_primary_active_contact",
        "contacts",
        ["company_id", "contact_type"],
        unique=True,
        postgresql_where=sa.text("is_primary AND invalidated_at IS NULL"),
    )
    op.create_table(
        "duplicate_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_a_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_b_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", duplicate_level, nullable=False),
        sa.Column("status", duplicate_status, server_default="OPEN", nullable=False),
        sa.Column("signals", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decision_reason", sa.String(500), nullable=True),
        sa.CheckConstraint("company_a_id <> company_b_id", name="ck_duplicate_distinct_companies"),
        sa.ForeignKeyConstraint(["company_a_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_b_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_a_id", "company_b_id", name="uq_duplicate_company_pair"),
    )
    op.create_table(
        "company_merge_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("survivor_company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merged_company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["survivor_company_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["merged_company_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("company_merge_audits")
    op.drop_table("duplicate_candidates")
    op.drop_index("uq_primary_active_contact", table_name="contacts")
    op.drop_table("contacts")
    op.drop_index("uq_source_external_id", table_name="company_source_refs")
    op.drop_column("company_source_refs", "last_verified_at")
    op.drop_column("company_source_refs", "raw_name")
    op.drop_column("company_source_refs", "external_id")
    op.drop_constraint("fk_companies_merged_into", "companies", type_="foreignkey")
    op.drop_column("companies", "merged_into_company_id")
    duplicate_status.drop(op.get_bind(), checkfirst=True)
    duplicate_level.drop(op.get_bind(), checkfirst=True)
    contact_type.drop(op.get_bind(), checkfirst=True)
