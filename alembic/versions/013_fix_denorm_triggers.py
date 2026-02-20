"""Fix denorm trigger to preserve provided view when no primary view exists.

Revision ID: 013_fix_denorm
Revises: 012_merge_heads2
Create Date: 2026-01-28
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "013_fix_denorm"
down_revision = "012_merge_heads2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_item_denorm_fields()
        RETURNS trigger AS $$
        DECLARE
            v_view_name text;
        BEGIN
            IF NEW.node_kind_id IS NOT NULL THEN
                SELECT name INTO NEW.item_type FROM node_kinds WHERE id = NEW.node_kind_id;
            END IF;

            SELECT v.name INTO v_view_name
            FROM item_views iv
            JOIN views v ON v.id = iv.view_id
            WHERE iv.item_id = NEW.id AND iv.is_primary = true
            LIMIT 1;

            IF v_view_name IS NOT NULL THEN
                NEW.view = v_view_name;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
    )


def downgrade() -> None:
    """Downgrade."""
