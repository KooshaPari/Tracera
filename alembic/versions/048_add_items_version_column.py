"""Add items.version column if missing (schema sync with Python model).

Databases created by Go backend or older migrations may not have items.version.
This revision is idempotent: it only adds the column when it does not exist.

Revision ID: 048_add_items_version
Revises: d0fa574bb4f6
Create Date: 2026-01-31

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "048_add_items_version"
down_revision: str | None = "d0fa574bb4f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Add items.version if missing (idempotent; safe when column already exists)
    op.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1")


def downgrade() -> None:
    """Downgrade."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'items' AND column_name = 'version'
            """,
        ),
    ).fetchone()
    if result is not None:
        op.drop_column("items", "version")
