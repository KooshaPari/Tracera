"""Create materialized views for dashboard metrics.

Creates optimized materialized views for:
- Dashboard metrics (test results, coverage)
- Project statistics (item counts, status distribution)
- User activity summaries
- Refresh strategies (immediate, scheduled)

Revision ID: 057_create_materialized_views
Revises: 056_add_partitioning
Create Date: 2026-02-01
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = "057_create_materialized_views"
down_revision = "056_add_partitioning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create materialized views for performance."""
    conn = op.get_bind()
    has_test_coverage = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_coverage')"),
    ).scalar()

    # =========================================================================
    # MATERIALIZED VIEW: dashboard_metrics
    # =========================================================================

    if has_test_coverage:
        dashboard_metrics_sql = """
            CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_metrics AS
            SELECT
                p.id as project_id,
                p.name as project_name,
                -- Test metrics
                COUNT(DISTINCT CASE WHEN tr.status = 'passed' THEN tr.id END) as tests_passed,
                COUNT(DISTINCT CASE WHEN tr.status = 'failed' THEN tr.id END) as tests_failed,
                COUNT(DISTINCT tr.id) as total_test_runs,
                CASE
                    WHEN COUNT(DISTINCT tr.id) > 0 THEN
                        ROUND(
                            100.0 * COUNT(DISTINCT CASE WHEN tr.status = 'passed' THEN tr.id END) /
                            NULLIF(COUNT(DISTINCT tr.id), 0),
                            2
                        )
                    ELSE 0
                END as pass_rate_percentage,
                -- Coverage metrics
                COALESCE(AVG(tc.line_coverage), 0) as avg_line_coverage,
                COALESCE(AVG(tc.branch_coverage), 0) as avg_branch_coverage,
                -- Timestamps
                MAX(tr.created_at) as last_test_run_at,
                NOW() as refreshed_at
            FROM projects p
            LEFT JOIN test_runs tr ON tr.project_id = p.id
                AND tr.created_at > NOW() - INTERVAL '30 days'
            LEFT JOIN test_coverage tc ON tc.project_id = p.id
            WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_runs')
            GROUP BY p.id, p.name;
        """
    else:
        dashboard_metrics_sql = """
            CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_metrics AS
            SELECT
                p.id as project_id,
                p.name as project_name,
                -- Test metrics
                COUNT(DISTINCT CASE WHEN tr.status = 'passed' THEN tr.id END) as tests_passed,
                COUNT(DISTINCT CASE WHEN tr.status = 'failed' THEN tr.id END) as tests_failed,
                COUNT(DISTINCT tr.id) as total_test_runs,
                CASE
                    WHEN COUNT(DISTINCT tr.id) > 0 THEN
                        ROUND(
                            100.0 * COUNT(DISTINCT CASE WHEN tr.status = 'passed' THEN tr.id END) /
                            NULLIF(COUNT(DISTINCT tr.id), 0),
                            2
                        )
                    ELSE 0
                END as pass_rate_percentage,
                -- Coverage metrics (placeholders)
                0::float as avg_line_coverage,
                0::float as avg_branch_coverage,
                -- Timestamps
                MAX(tr.created_at) as last_test_run_at,
                NOW() as refreshed_at
            FROM projects p
            LEFT JOIN test_runs tr ON tr.project_id = p.id
                AND tr.created_at > NOW() - INTERVAL '30 days'
            WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_runs')
            GROUP BY p.id, p.name;
        """

    op.execute(dashboard_metrics_sql)

    # Create indexes on materialized view
    op.execute("""
        CREATE UNIQUE INDEX ix_dashboard_metrics_project_id
        ON dashboard_metrics(project_id);
    """)

    op.execute("""
        CREATE INDEX ix_dashboard_metrics_pass_rate
        ON dashboard_metrics(pass_rate_percentage DESC);
    """)

    # =========================================================================
    # MATERIALIZED VIEW: project_statistics
    # =========================================================================

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS project_statistics AS
        SELECT
            p.id as project_id,
            p.name as project_name,
            -- Item counts by type
            COUNT(DISTINCT i.id) as total_items,
            COUNT(DISTINCT CASE WHEN i.item_type = 'requirement' THEN i.id END) as requirement_count,
            COUNT(DISTINCT CASE WHEN i.item_type = 'feature' THEN i.id END) as feature_count,
            COUNT(DISTINCT CASE WHEN i.item_type = 'bug' THEN i.id END) as bug_count,
            COUNT(DISTINCT CASE WHEN i.item_type = 'task' THEN i.id END) as task_count,
            COUNT(DISTINCT CASE WHEN i.item_type = 'test' THEN i.id END) as test_count,
            -- Status distribution
            COUNT(DISTINCT CASE WHEN i.status = 'todo' THEN i.id END) as todo_count,
            COUNT(DISTINCT CASE WHEN i.status = 'in_progress' THEN i.id END) as in_progress_count,
            COUNT(DISTINCT CASE WHEN i.status = 'done' THEN i.id END) as done_count,
            COUNT(DISTINCT CASE WHEN i.status = 'blocked' THEN i.id END) as blocked_count,
            -- Priority distribution
            COUNT(DISTINCT CASE WHEN i.priority = 'critical' THEN i.id END) as critical_count,
            COUNT(DISTINCT CASE WHEN i.priority = 'high' THEN i.id END) as high_count,
            COUNT(DISTINCT CASE WHEN i.priority = 'medium' THEN i.id END) as medium_count,
            COUNT(DISTINCT CASE WHEN i.priority = 'low' THEN i.id END) as low_count,
            -- Link statistics
            COUNT(DISTINCT l.id) as total_links,
            COUNT(DISTINCT CASE WHEN l.link_type = 'depends_on' THEN l.id END) as dependency_links,
            COUNT(DISTINCT CASE WHEN l.link_type = 'relates_to' THEN l.id END) as related_links,
            COUNT(DISTINCT CASE WHEN l.link_type = 'blocks' THEN l.id END) as blocking_links,
            -- Timestamps
            MAX(i.created_at) as last_item_created_at,
            MAX(i.updated_at) as last_item_updated_at,
            NOW() as refreshed_at
        FROM projects p
        LEFT JOIN items i ON i.project_id = p.id
            AND i.deleted_at IS NULL
        LEFT JOIN links l ON l.project_id = p.id
        GROUP BY p.id, p.name;
    """)

    # Create indexes on materialized view
    op.execute("""
        CREATE UNIQUE INDEX ix_project_statistics_project_id
        ON project_statistics(project_id);
    """)

    op.execute("""
        CREATE INDEX ix_project_statistics_total_items
        ON project_statistics(total_items DESC);
    """)

    # =========================================================================
    # MATERIALIZED VIEW: user_activity_summary
    # =========================================================================

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_activity_summary AS
        SELECT
            i.owner as user_id,
            p.id as project_id,
            p.name as project_name,
            DATE(i.created_at) as activity_date,
            -- Created items
            COUNT(DISTINCT CASE WHEN DATE(i.created_at) = CURRENT_DATE THEN i.id END) as items_created_today,
            COUNT(DISTINCT CASE WHEN DATE(i.created_at) >= CURRENT_DATE - INTERVAL '7 days' THEN i.id END) as items_created_this_week,
            COUNT(DISTINCT CASE WHEN DATE(i.created_at) >= DATE_TRUNC('month', CURRENT_DATE) THEN i.id END) as items_created_this_month,
            -- Updated items
            COUNT(DISTINCT CASE
                WHEN DATE(i.updated_at) = CURRENT_DATE
                AND DATE(i.created_at) != DATE(i.updated_at)
                THEN i.id
            END) as items_updated_today,
            COUNT(DISTINCT CASE
                WHEN DATE(i.updated_at) >= CURRENT_DATE - INTERVAL '7 days'
                AND DATE(i.created_at) != DATE(i.updated_at)
                THEN i.id
            END) as items_updated_this_week,
            -- Completion metrics
            COUNT(DISTINCT CASE WHEN i.status = 'done' AND DATE(i.updated_at) = CURRENT_DATE THEN i.id END) as items_completed_today,
            COUNT(DISTINCT CASE WHEN i.status = 'done' AND DATE(i.updated_at) >= CURRENT_DATE - INTERVAL '7 days' THEN i.id END) as items_completed_this_week,
            -- Timestamps
            MAX(i.updated_at) as last_activity_at,
            NOW() as refreshed_at
        FROM items i
        JOIN projects p ON p.id = i.project_id
        WHERE i.owner IS NOT NULL
            AND i.deleted_at IS NULL
            AND i.created_at > NOW() - INTERVAL '90 days'
        GROUP BY i.owner, p.id, p.name, DATE(i.created_at);
    """)

    # Create indexes on materialized view
    op.execute("""
        CREATE INDEX ix_user_activity_user_project
        ON user_activity_summary(user_id, project_id, activity_date DESC);
    """)

    op.execute("""
        CREATE INDEX ix_user_activity_date
        ON user_activity_summary(activity_date DESC);
    """)

    # =========================================================================
    # FUNCTION: Refresh all materialized views
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_all_materialized_views(
            concurrent_refresh boolean DEFAULT true
        ) RETURNS void AS $$
        DECLARE
            view_name text;
        BEGIN
            FOR view_name IN
                SELECT matviewname
                FROM pg_matviews
                WHERE schemaname = 'public'
                ORDER BY matviewname
            LOOP
                IF concurrent_refresh THEN
                    EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', view_name);
                    RAISE NOTICE 'Refreshed % concurrently', view_name;
                ELSE
                    EXECUTE format('REFRESH MATERIALIZED VIEW %I', view_name);
                    RAISE NOTICE 'Refreshed %', view_name;
                END IF;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # FUNCTION: Refresh specific view
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_materialized_view(
            view_name text,
            concurrent_refresh boolean DEFAULT true
        ) RETURNS void AS $$
        BEGIN
            IF concurrent_refresh THEN
                EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', view_name);
            ELSE
                EXECUTE format('REFRESH MATERIALIZED VIEW %I', view_name);
            END IF;
            RAISE NOTICE 'Refreshed materialized view: %', view_name;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # FUNCTION: Auto-refresh on data changes (trigger-based)
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION auto_refresh_project_statistics()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Queue async refresh (in production, this would use a job queue)
            -- For now, just log that a refresh is needed
            RAISE NOTICE 'project_statistics needs refresh due to % on %',
                TG_OP, TG_TABLE_NAME;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create triggers for auto-refresh (optional, can be heavy)
    # Uncomment in production with careful consideration
    # op.execute("""
    #     CREATE TRIGGER trigger_refresh_project_stats_on_item_change
    #         AFTER INSERT OR UPDATE OR DELETE ON items
    #         FOR EACH STATEMENT
    #         EXECUTE FUNCTION auto_refresh_project_statistics();
    # """)

    # =========================================================================
    # SCHEDULED REFRESH: Function for periodic refresh
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION scheduled_refresh_materialized_views()
        RETURNS void AS $$
        BEGIN
            -- Refresh dashboard metrics (high priority, frequent updates)
            PERFORM refresh_materialized_view('dashboard_metrics', true);

            -- Refresh project statistics (medium priority)
            PERFORM refresh_materialized_view('project_statistics', true);

            -- Refresh user activity (low priority, less frequent)
            PERFORM refresh_materialized_view('user_activity_summary', true);

            RAISE NOTICE 'Scheduled materialized view refresh completed at %', NOW();
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # REFRESH STRATEGY: On-demand refresh function
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_dashboard_metrics_now()
        RETURNS TABLE(
            project_id uuid,
            project_name varchar,
            pass_rate_percentage numeric,
            refreshed_at timestamp
        ) AS $$
        BEGIN
            -- Refresh the view
            PERFORM refresh_materialized_view('dashboard_metrics', false);

            -- Return refreshed data
            RETURN QUERY SELECT
                dm.project_id,
                dm.project_name,
                dm.pass_rate_percentage,
                dm.refreshed_at
            FROM dashboard_metrics dm
            ORDER BY dm.pass_rate_percentage DESC;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # Initial refresh of all views
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            -- Initial refresh without CONCURRENTLY (views are empty)
            REFRESH MATERIALIZED VIEW dashboard_metrics;
            REFRESH MATERIALIZED VIEW project_statistics;
            REFRESH MATERIALIZED VIEW user_activity_summary;

            RAISE NOTICE 'Initial materialized view refresh completed';
        END $$;
    """)


def downgrade() -> None:
    """Drop materialized views and related functions."""
    # Drop triggers (if created)

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS refresh_dashboard_metrics_now()")
    op.execute("DROP FUNCTION IF EXISTS scheduled_refresh_materialized_views()")
    op.execute("DROP FUNCTION IF EXISTS auto_refresh_project_statistics()")
    op.execute("DROP FUNCTION IF EXISTS refresh_materialized_view(text, boolean)")
    op.execute("DROP FUNCTION IF EXISTS refresh_all_materialized_views(boolean)")

    # Drop materialized views
    op.execute("DROP MATERIALIZED VIEW IF EXISTS user_activity_summary")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS project_statistics")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS dashboard_metrics")
