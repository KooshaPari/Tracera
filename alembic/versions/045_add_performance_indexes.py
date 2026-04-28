"""Add performance indexes for critical queries.

Adds composite and single-column indexes to optimize:
- Link queries (source_id, target_id)
- Item filtering (project_id, parent_id, status)
- Full-text search
- Timestamp filtering (created_at, updated_at)
- Covering indexes for common access patterns

Revision ID: 045_add_performance_indexes
Revises: 044_add_milestones
Create Date: 2026-01-29
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = "045_add_performance_indexes"
down_revision = "044_add_milestones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes for critical queries."""
    # =========================================================================
    # LINKS TABLE INDEXES (Most Critical for Graph Performance)
    # =========================================================================
    # Single column indexes for lookups by source or target
    op.create_index(
        "ix_links_source_id",
        "links",
        ["source_item_id"],
        postgresql_using="btree",
    )

    op.create_index(
        "ix_links_target_id",
        "links",
        ["target_item_id"],
        postgresql_using="btree",
    )

    # Composite index for queries finding links between specific nodes
    op.create_index(
        "ix_links_source_target",
        "links",
        ["source_item_id", "target_item_id"],
        postgresql_using="btree",
    )

    # Index for link type filtering
    op.create_index(
        "ix_links_type",
        "links",
        ["link_type"],
        postgresql_using="btree",
    )

    # Composite index: find links of specific type between nodes
    op.create_index(
        "ix_links_source_type",
        "links",
        ["source_item_id", "link_type"],
        postgresql_using="btree",
    )

    # =========================================================================
    # ITEMS TABLE INDEXES (Critical for Item Queries)
    # =========================================================================
    # Project filtering - most common query pattern
    # Already created in 000 as idx_items_project_id
    # We'll use different names to avoid conflicts if they are needed,
    # but usually one index is enough. I'll comment out the redundant ones.

    # op.create_index(
    #     "ix_items_project_id",
    #     "items",

    # Hierarchy traversal
    # op.create_index(
    #     "ix_items_parent_id",
    #     "items",

    # Status filtering
    # op.create_index(
    #     "ix_items_status",
    #     "items",

    # Owner/assignee filtering
    # op.create_index(
    #     "ix_items_owner",
    #     "items",

    # Timestamp-based queries (recent items, archived items)
    op.create_index(
        "ix_items_created_at",
        "items",
        ["created_at"],
        postgresql_using="btree",
    )

    op.create_index(
        "ix_items_updated_at",
        "items",
        ["updated_at"],
        postgresql_using="btree",
    )

    # =========================================================================
    # ITEMS TABLE COMPOSITE INDEXES (Covering Indexes)
    # =========================================================================
    # Common query: filter items in project by status
    # op.create_index(
    #     "ix_items_project_status",
    #     "items",

    # Common query: filter items in project by owner
    op.create_index(
        "ix_items_project_owner",
        "items",
        ["project_id", "owner"],
        postgresql_using="btree",
    )

    # Common query: get recent items in project
    op.create_index(
        "ix_items_project_updated",
        "items",
        ["project_id", "updated_at"],
        postgresql_using="btree",
    )

    # Hierarchy with status - common for tree views
    op.create_index(
        "ix_items_parent_status",
        "items",
        ["parent_id", "status"],
        postgresql_using="btree",
    )

    # =========================================================================
    # FULL-TEXT SEARCH INDEXES
    # =========================================================================
    # GIN index for full-text search on name and description
    op.execute(
        """
        CREATE INDEX ix_items_search ON items
        USING gin(to_tsvector('english',
            coalesce(title, '') || ' ' || coalesce(description, '')))
    """,
    )

    # =========================================================================
    # LINKS TABLE METADATA INDEXES
    # =========================================================================
    # Timestamp indexes for change tracking
    op.create_index(
        "ix_links_created_at",
        "links",
        ["created_at"],
        postgresql_using="btree",
    )

    op.create_index(
        "ix_links_updated_at",
        "links",
        ["updated_at"],
        postgresql_using="btree",
    )

    # =========================================================================
    # PROJECT-SCOPED LINK QUERIES
    # =========================================================================
    # Find links in a project by traversing source items
    op.create_index(
        "ix_links_type_created",
        "links",
        ["link_type", "created_at"],
        postgresql_using="btree",
    )

    # =========================================================================
    # ITEMS TABLE ADDITIONAL INDEXES
    # =========================================================================
    # Type filtering (component, feature, bug, task, etc.)
    op.create_index(
        "ix_items_type",
        "items",
        ["item_type"],
        postgresql_using="btree",
    )

    # Priority sorting and filtering
    # op.create_index(
    #     "ix_items_priority",
    #     "items",

    # Combined: common dashboard query
    op.create_index(
        "ix_items_project_status_priority",
        "items",
        ["project_id", "status", "priority"],
        postgresql_using="btree",
    )

    # =========================================================================
    # CHANGE LOG AND AUDIT INDEXES
    # =========================================================================
    # Track changes by entity type for audit trails
    if does_table_exist("change_log"):
        op.create_index(
            "ix_change_log_record_table",
            "change_log",
            ["record_id", "table_name"],
            postgresql_using="btree",
        )


def downgrade() -> None:
    """Drop performance indexes."""
    # Drop links indexes
    op.drop_index("ix_links_source_id", table_name="links")
    op.drop_index("ix_links_target_id", table_name="links")
    op.drop_index("ix_links_source_target", table_name="links")
    op.drop_index("ix_links_type", table_name="links")
    op.drop_index("ix_links_source_type", table_name="links")
    op.drop_index("ix_links_created_at", table_name="links")
    op.drop_index("ix_links_updated_at", table_name="links")
    op.drop_index("ix_links_type_created", table_name="links")

    # Drop items single-column indexes
    op.drop_index("ix_items_project_id", table_name="items")
    op.drop_index("ix_items_parent_id", table_name="items")
    op.drop_index("ix_items_status", table_name="items")
    op.drop_index("ix_items_owner", table_name="items")
    op.drop_index("ix_items_created_at", table_name="items")
    op.drop_index("ix_items_updated_at", table_name="items")
    op.drop_index("ix_items_type", table_name="items")
    op.drop_index("ix_items_priority", table_name="items")

    # Drop items composite indexes
    op.drop_index("ix_items_project_status", table_name="items")
    op.drop_index("ix_items_project_owner", table_name="items")
    op.drop_index("ix_items_project_updated", table_name="items")
    op.drop_index("ix_items_parent_status", table_name="items")
    op.drop_index("ix_items_project_status_priority", table_name="items")

    # Drop full-text search index
    op.drop_index("ix_items_search", table_name="items")

    # Drop change_log index if it exists
    if does_table_exist("change_log"):
        op.drop_index("ix_change_log_record_table", table_name="change_log")


def does_table_exist(table_name: str) -> bool:
    """Check if table exists in current database."""
    bind = op.get_context().bind
    if bind is None:
        return False
    try:
        result = bind.execute(
            sa.text(
                """
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = :table_name
                )
            """,
            ),
            {"table_name": table_name},
        )
        return result.scalar()
    except Exception:
        # If check fails, assume table doesn't exist
        return False
