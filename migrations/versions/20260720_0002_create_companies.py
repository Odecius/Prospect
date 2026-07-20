"""Create essential company registration.

Revision ID: 20260720_0002
Revises: 20260720_0001
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0002"
down_revision: str | None = "20260720_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

pipeline_status = postgresql.ENUM(
    "NEW",
    "QUALIFIED",
    "CONTACTED",
    "REPLIED",
    "MEETING",
    "PROPOSAL_SENT",
    "NEGOTIATION",
    "WON",
    "LOST",
    "DO_NOT_CONTACT",
    "ARCHIVED",
    name="pipeline_status",
    create_type=False,
)

CATEGORIES = [
    "Alimentação e bebidas",
    "Comércio varejista",
    "Serviços profissionais",
    "Saúde e bem-estar",
    "Beleza e estética",
    "Construção e serviços para imóveis",
    "Automotivo",
    "Educação e cursos",
    "Hospedagem e turismo",
    "Tecnologia e serviços digitais",
    "Cultura, lazer e eventos",
    "Indústria e produção",
    "Transporte e logística",
    "Serviços para animais",
    "Outros",
]


def _slug(value: str) -> str:
    import unicodedata

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return "-".join(normalized.replace("&", " e ").split())


def upgrade() -> None:
    pipeline_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("name_normalized", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(140), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name_normalized"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "data_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("collection_method", sa.String(40), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("legal_or_trade_name", sa.String(200), nullable=False),
        sa.Column("name_normalized", sa.String(200), nullable=False),
        sa.Column("tax_id_normalized", sa.String(14), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("state_code", sa.String(2), nullable=False),
        sa.Column("country_code", sa.String(2), server_default="BR", nullable=False),
        sa.Column("pipeline_status", pipeline_status, server_default="NEW", nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tax_id_normalized"),
    )
    op.create_index("ix_companies_name_normalized", "companies", ["name_normalized"])
    op.create_table(
        "company_source_refs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    category_table = sa.table(
        "categories", sa.column("id"), sa.column("name"), sa.column("name_normalized"), sa.column("slug")
    )
    op.bulk_insert(
        category_table,
        [
            {
                "id": str(__import__("uuid").uuid4()),
                "name": n,
                "name_normalized": _slug(n).replace("-", " "),
                "slug": _slug(n),
            }
            for n in CATEGORIES
        ],
    )
    source_table = sa.table(
        "data_sources", sa.column("id"), sa.column("name"), sa.column("source_type"), sa.column("collection_method")
    )
    op.bulk_insert(
        source_table,
        [
            {
                "id": str(__import__("uuid").uuid4()),
                "name": n,
                "source_type": "MANUAL",
                "collection_method": "HUMAN_ENTRY",
            }
            for n in ["Pesquisa manual", "Indicação", "Website oficial", "Outro"]
        ],
    )


def downgrade() -> None:
    op.drop_table("company_source_refs")
    op.drop_index("ix_companies_name_normalized", table_name="companies")
    op.drop_table("companies")
    op.drop_table("data_sources")
    op.drop_table("categories")
    pipeline_status.drop(op.get_bind(), checkfirst=True)
