"""Add item_comments table for per-item discussion threads.

Revision ID: 063_add_item_comments
Revises: 062_add_trace_link_fields
Create Date: 2026-05-28
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "063_add_item_comments"
down_revision = "062_add_trace_link_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create item_comments table."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS item_comments (
            id          VARCHAR(36)  PRIMARY KEY,
            item_id     VARCHAR(255) NOT NULL,
            author_id   VARCHAR(255) NOT NULL,
            author_name VARCHAR(255) NOT NULL DEFAULT '',
            content     TEXT         NOT NULL,
            edited      BOOLEAN      NOT NULL DEFAULT FALSE,
            created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_item_comments_item_id ON item_comments(item_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_item_comments_author_id ON item_comments(author_id)"
    )


def downgrade() -> None:
    """Drop item_comments table."""
    op.execute("DROP TABLE IF EXISTS item_comments")
