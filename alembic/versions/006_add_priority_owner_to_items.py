"""Add priority and owner fields to items table.

Revision ID: 006_add_priority_owner
Revises: 005_update_refresh_all_views
Create Date: 2025-01-27

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_add_priority_owner"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    # Check if columns already exist before adding them
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("items")]

    if "priority" not in columns:
        # Add priority column with default 'medium'
        op.add_column("items", sa.Column("priority", sa.String(50), nullable=False, server_default="medium"))
        # Create index on priority for filtering
        op.create_index("idx_items_priority", "items", ["priority"])

    if "owner" not in columns:
        # Add owner column (nullable)
        op.add_column("items", sa.Column("owner", sa.String(255), nullable=True))
        # Create index on owner for filtering
        op.create_index("idx_items_owner", "items", ["owner"])


def downgrade() -> None:
    """Downgrade."""
    # Drop indexes
    op.drop_index("idx_items_owner", table_name="items")
    op.drop_index("idx_items_priority", table_name="items")

    # Drop columns
    op.drop_column("items", "owner")
    op.drop_column("items", "priority")
