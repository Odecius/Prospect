"""Register the approved Google Places source.

Revision ID: 20260721_0007
Revises: 20260721_0006
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_0007"
down_revision: str | None = "20260721_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCE_NAME = "Google Places API (New)"


def upgrade() -> None:
    source = sa.table(
        "data_sources",
        sa.column("id"),
        sa.column("name"),
        sa.column("source_type"),
        sa.column("collection_method"),
        sa.column("active"),
    )
    op.bulk_insert(
        source,
        [
            {
                "id": str(uuid.uuid4()),
                "name": SOURCE_NAME,
                "source_type": "EXTERNAL_API",
                "collection_method": "HUMAN_REVIEWED_IMPORT",
                "active": True,
            }
        ],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM data_sources WHERE name = :name").bindparams(name=SOURCE_NAME))
