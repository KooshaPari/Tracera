"""Add spatial GIST index for graph viewport queries.

Revision ID: 054_add_spatial_gist_index
Revises: 053_add_test_suites_runs_if_not_exists
Create Date: 2026-02-01

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "054_add_spatial_gist_index"
down_revision = "053_add_test_suites_runs_if_not_exists"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Add position columns if they don't exist
    # Using sa.text to handle conditional logic in raw SQL
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'items' AND column_name = 'position_x'
            ) THEN
                ALTER TABLE items ADD COLUMN position_x NUMERIC(10,2) DEFAULT 0;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'items' AND column_name = 'position_y'
            ) THEN
                ALTER TABLE items ADD COLUMN position_y NUMERIC(10,2) DEFAULT 0;
            END IF;
        END $$;
        """,
    )

    # Enable PostGIS extension if not already enabled (for advanced spatial operations)

    # Create spatial GIST index for graph viewport queries
    # This index allows efficient rectangular range queries on item positions
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_items_spatial
        ON items USING GIST (
            box(point(position_x, position_y), point(position_x, position_y))
        )
        WHERE deleted_at IS NULL
        """,
    )


def downgrade() -> None:
    """Downgrade."""
    # Drop the spatial index
    op.execute("DROP INDEX IF EXISTS idx_items_spatial")

    # Drop position columns
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'items' AND column_name = 'position_x'
            ) THEN
                ALTER TABLE items DROP COLUMN position_x;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'items' AND column_name = 'position_y'
            ) THEN
                ALTER TABLE items DROP COLUMN position_y;
            END IF;
        END $$;
        """,
    )
