"""Add composite performance indexes for optimized query patterns.

This migration adds strategic composite indexes that improve query performance
for common filtering patterns that aren't covered by existing single-column indexes.

Key additions:
- Composite index on items(deleted_at, project_id) for soft-delete filtering
- Composite index on items(project_id, deleted_at, type) for filtered item lists

Revision ID: 046_add_composite_performance_indexes
Revises: 045_add_performance_indexes
Create Date: 2026-01-30
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "046_add_composite_performance_indexes"
down_revision = "045_add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add composite performance indexes for critical query patterns."""
    # =========================================================================
    # ITEMS TABLE - Soft Delete Filtering Optimization
    # =========================================================================
    # Critical for queries like: WHERE deleted_at IS NULL AND project_id = ?
    # This pattern is used in almost every item list query to filter out deleted items
    op.create_index(
        "ix_items_deleted_project",
        "items",
        ["deleted_at", "project_id"],
        unique=False,
        postgresql_using="btree",
    )

    # =========================================================================
    # ITEMS TABLE - Complete Item Filtering Optimization
    # =========================================================================
    # Composite index for the most common query pattern:
    # WHERE project_id = ? AND deleted_at IS NULL AND item_type = ?
    # This covers filtering active items by type within a project
    op.create_index(
        "ix_items_project_deleted_type",
        "items",
        ["project_id", "deleted_at", "item_type"],
        unique=False,
        postgresql_using="btree",
    )


def downgrade() -> None:
    """Drop composite performance indexes."""
    op.drop_index("ix_items_project_deleted_type", table_name="items")
    op.drop_index("ix_items_deleted_project", table_name="items")
