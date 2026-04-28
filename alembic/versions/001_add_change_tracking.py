"""Add change tracking infrastructure.

Revision ID: 001
Revises:
Create Date: 2025-11-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = "000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add change_log table and triggers for change tracking."""
    # Create change_log table
    op.create_table(
        "change_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("table_name", sa.String(50), nullable=False),
        sa.Column("operation", sa.String(10), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("metadata", postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        "idx_change_log_processed",
        "change_log",
        ["processed"],
        postgresql_where=sa.text("processed = FALSE"),
    )
    op.create_index("idx_change_log_table", "change_log", ["table_name"])
    op.create_index("idx_change_log_record_id", "change_log", ["record_id"])
    op.create_index("idx_change_log_project_id", "change_log", ["project_id"])
    op.create_index("idx_change_log_changed_at", "change_log", ["changed_at"])

    # Create trigger function for items
    op.execute("""
        CREATE OR REPLACE FUNCTION log_item_change()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO change_log (table_name, operation, record_id, project_id)
            VALUES (
                'items',
                TG_OP,
                COALESCE(NEW.id, OLD.id),
                COALESCE(NEW.project_id, OLD.project_id)
            );
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for items table
    op.execute("""
        CREATE TRIGGER item_change_trigger
        AFTER INSERT OR UPDATE OR DELETE ON items
        FOR EACH ROW EXECUTE FUNCTION log_item_change();
    """)

    # Create trigger function for links
    op.execute("""
        CREATE OR REPLACE FUNCTION log_link_change()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO change_log (table_name, operation, record_id, project_id)
            VALUES (
                'links',
                TG_OP,
                COALESCE(NEW.id, OLD.id),
                COALESCE(NEW.project_id, OLD.project_id)
            );
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for links table
    op.execute("""
        CREATE TRIGGER link_change_trigger
        AFTER INSERT OR UPDATE OR DELETE ON links
        FOR EACH ROW EXECUTE FUNCTION log_link_change();
    """)


def downgrade() -> None:
    """Remove change tracking infrastructure."""
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS item_change_trigger ON items;")
    op.execute("DROP TRIGGER IF EXISTS link_change_trigger ON links;")

    # Drop trigger functions
    op.execute("DROP FUNCTION IF EXISTS log_item_change();")
    op.execute("DROP FUNCTION IF EXISTS log_link_change();")

    # Drop indexes
    op.drop_index("idx_change_log_changed_at", "change_log")
    op.drop_index("idx_change_log_project_id", "change_log")
    op.drop_index("idx_change_log_record_id", "change_log")
    op.drop_index("idx_change_log_table", "change_log")
    op.drop_index("idx_change_log_processed", "change_log")

    # Drop table
    op.drop_table("change_log")
