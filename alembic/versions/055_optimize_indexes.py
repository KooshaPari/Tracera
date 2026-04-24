"""Optimize database indexes for performance.

Adds advanced composite indexes, partial indexes, and BRIN indexes
to improve query performance for common access patterns.

Revision ID: 055_optimize_indexes
Revises: 054_add_spatial_gist_index
Create Date: 2026-02-01
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "055_optimize_indexes"
down_revision = "054_add_spatial_gist_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add optimized indexes for performance."""
    # =========================================================================
    # ITEMS TABLE - Advanced Composite Indexes
    # =========================================================================

    # Triple composite for filtered queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_items_project_type_status
        ON items(project_id, item_type, status)
        WHERE deleted_at IS NULL
    """)

    # Timestamp-based ordering with ID for stable pagination
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_items_project_created_id
        ON items(project_id, created_at DESC, id)
        WHERE deleted_at IS NULL
    """)

    # Active items partial index (90% of queries are for non-deleted items)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_items_active
        ON items(project_id, item_type, status, priority, updated_at DESC)
        WHERE deleted_at IS NULL
    """)

    # BRIN index for time-series queries on large tables (>100k rows)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_items_created_at_brin
        ON items USING brin(created_at)
        WITH (pages_per_range = 128)
    """)

    # =========================================================================
    # LINKS TABLE - Advanced Composite Indexes
    # =========================================================================

    # Project-scoped link queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_links_project_type
        ON links(project_id, link_type)
    """)

    # Three-way composite for link traversal
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_links_source_type_target
        ON links(source_item_id, link_type, target_item_id)
    """)

    # Reverse traversal optimization
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_links_target_type_source
        ON links(target_item_id, link_type, source_item_id)
    """)

    # BRIN index for temporal link analysis
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_links_created_at_brin
        ON links USING brin(created_at)
        WITH (pages_per_range = 128)
    """)

    # =========================================================================
    # TEST_RUNS TABLE - Performance Indexes
    # =========================================================================

    # Check if test_runs table exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_runs') THEN
                -- Test suite queries with temporal sorting
                CREATE INDEX IF NOT EXISTS ix_test_runs_suite_created
                ON test_runs(suite_id, created_at DESC);

                -- Active test runs partial index
                CREATE INDEX IF NOT EXISTS ix_test_runs_active
                ON test_runs(status, created_at DESC)
                WHERE status IN ('running', 'pending');

                -- Project-scoped test metrics
                CREATE INDEX IF NOT EXISTS ix_test_runs_project_status
                ON test_runs(project_id, status, created_at DESC);

                -- BRIN index for test history queries
                CREATE INDEX IF NOT EXISTS ix_test_runs_created_at_brin
                ON test_runs USING brin(created_at)
                WITH (pages_per_range = 128);
            END IF;
        END $$;
    """)

    # =========================================================================
    # TEST_CASES TABLE - Coverage Indexes
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_cases') THEN
                -- Project-scoped test case queries
                CREATE INDEX IF NOT EXISTS ix_test_cases_project_type
                ON test_cases(project_id, test_type);
            END IF;
        END $$;
    """)

    # =========================================================================
    # PROJECTS TABLE - Enhanced Indexes
    # =========================================================================

    # Search optimization
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_projects_name_trgm
        ON projects USING gin(name gin_trgm_ops)
    """)

    # Recent projects
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_projects_updated_at
        ON projects(updated_at DESC)
    """)

    # =========================================================================
    # GRAPH_NODES TABLE - Graph Traversal Indexes
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'graph_nodes') THEN
                -- Graph queries by project and kind
                CREATE INDEX IF NOT EXISTS ix_graph_nodes_graph_id
                ON graph_nodes(graph_id);
            END IF;
        END $$;
    """)

    # =========================================================================
    # SPECIFICATIONS TABLE - Spec Queries
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'specifications') THEN
                -- Specification queries by project and type
                CREATE INDEX IF NOT EXISTS ix_specifications_project_type
                ON specifications(project_id, spec_type);

                -- Item linkage
                CREATE INDEX IF NOT EXISTS ix_specifications_item_id
                ON specifications(item_id);
            END IF;
        END $$;
    """)

    # =========================================================================
    # NOTIFICATIONS TABLE - User Queries
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'notifications') THEN
                -- Unread notifications query
                CREATE INDEX IF NOT EXISTS ix_notifications_user_unread
                ON notifications(user_id, created_at DESC)
                WHERE read_at IS NULL;

                -- Notification type filtering
                CREATE INDEX IF NOT EXISTS ix_notifications_user_type
                ON notifications(user_id, type, created_at DESC);
            END IF;
        END $$;
    """)

    # =========================================================================
    # Run ANALYZE to update statistics
    # =========================================================================

    op.execute("ANALYZE items")
    op.execute("ANALYZE links")
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_runs') THEN
                ANALYZE test_runs;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_cases') THEN
                ANALYZE test_cases;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Drop optimized indexes."""
    # Items indexes
    op.execute("DROP INDEX IF EXISTS ix_items_project_type_status")
    op.execute("DROP INDEX IF EXISTS ix_items_project_created_id")
    op.execute("DROP INDEX IF EXISTS ix_items_active")
    op.execute("DROP INDEX IF EXISTS ix_items_created_at_brin")

    # Links indexes
    op.execute("DROP INDEX IF EXISTS ix_links_project_type")
    op.execute("DROP INDEX IF EXISTS ix_links_source_type_target")
    op.execute("DROP INDEX IF EXISTS ix_links_target_type_source")
    op.execute("DROP INDEX IF EXISTS ix_links_created_at_brin")

    # Test runs indexes
    op.execute("DROP INDEX IF EXISTS ix_test_runs_suite_created")
    op.execute("DROP INDEX IF EXISTS ix_test_runs_active")
    op.execute("DROP INDEX IF EXISTS ix_test_runs_project_status")
    op.execute("DROP INDEX IF EXISTS ix_test_runs_created_at_brin")

    # Test cases indexes
    op.execute("DROP INDEX IF EXISTS ix_test_cases_project_type")

    # Projects indexes
    op.execute("DROP INDEX IF EXISTS ix_projects_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_projects_updated_at")

    # Graph nodes indexes
    op.execute("DROP INDEX IF EXISTS ix_graph_nodes_graph_id")

    # Specifications indexes
    op.execute("DROP INDEX IF EXISTS ix_specifications_project_type")
    op.execute("DROP INDEX IF EXISTS ix_specifications_item_id")

    # Notifications indexes
    op.execute("DROP INDEX IF EXISTS ix_notifications_user_unread")
    op.execute("DROP INDEX IF EXISTS ix_notifications_user_type")
