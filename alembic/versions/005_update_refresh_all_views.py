"""Update refresh functions to include all 8 materialized views.

Revision ID: 005
Revises: 004
Create Date: 2025-11-21

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Update refresh functions to include all 8 views."""
    # Update incremental refresh function
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_materialized_views_incremental()
        RETURNS void AS $$
        DECLARE
            v_changed_items UUID[];
            v_changed_links UUID[];
            v_has_changes BOOLEAN;
            v_start_time TIMESTAMP;
            v_end_time TIMESTAMP;
        BEGIN
            v_start_time := clock_timestamp();

            -- Get all changed item IDs
            SELECT ARRAY_AGG(DISTINCT record_id)
            INTO v_changed_items
            FROM change_log
            WHERE table_name = 'items'
            AND processed = FALSE;

            -- Get all changed link IDs
            SELECT ARRAY_AGG(DISTINCT record_id)
            INTO v_changed_links
            FROM change_log
            WHERE table_name = 'links'
            AND processed = FALSE;

            -- Check if there are any changes
            v_has_changes := (v_changed_items IS NOT NULL OR v_changed_links IS NOT NULL);

            -- Refresh views if there are changes
            IF v_has_changes THEN
                -- Refresh all 8 materialized views concurrently
                REFRESH MATERIALIZED VIEW CONCURRENTLY traceability_matrix;
                REFRESH MATERIALIZED VIEW CONCURRENTLY impact_analysis;
                REFRESH MATERIALIZED VIEW CONCURRENTLY coverage_analysis;
                REFRESH MATERIALIZED VIEW CONCURRENTLY dependency_graph;
                REFRESH MATERIALIZED VIEW CONCURRENTLY timeline_view;
                REFRESH MATERIALIZED VIEW CONCURRENTLY status_dashboard;
                REFRESH MATERIALIZED VIEW CONCURRENTLY search_index;
                REFRESH MATERIALIZED VIEW CONCURRENTLY agent_interface;

                -- Mark changes as processed
                UPDATE change_log
                SET processed = TRUE
                WHERE processed = FALSE;

                v_end_time := clock_timestamp();

                -- Log refresh
                RAISE NOTICE 'Refreshed all 8 materialized views. Items changed: %, Links changed: %, Duration: %ms',
                    COALESCE(array_length(v_changed_items, 1), 0),
                    COALESCE(array_length(v_changed_links, 1), 0),
                    EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time));
            ELSE
                RAISE NOTICE 'No changes detected. Skipping refresh.';
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Update full refresh function
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_materialized_views_full()
        RETURNS void AS $$
        DECLARE
            v_start_time TIMESTAMP;
            v_end_time TIMESTAMP;
        BEGIN
            v_start_time := clock_timestamp();

            -- Refresh all 8 materialized views
            REFRESH MATERIALIZED VIEW CONCURRENTLY traceability_matrix;
            REFRESH MATERIALIZED VIEW CONCURRENTLY impact_analysis;
            REFRESH MATERIALIZED VIEW CONCURRENTLY coverage_analysis;
            REFRESH MATERIALIZED VIEW CONCURRENTLY dependency_graph;
            REFRESH MATERIALIZED VIEW CONCURRENTLY timeline_view;
            REFRESH MATERIALIZED VIEW CONCURRENTLY status_dashboard;
            REFRESH MATERIALIZED VIEW CONCURRENTLY search_index;
                REFRESH MATERIALIZED VIEW CONCURRENTLY agent_interface;

            -- Mark all changes as processed
            UPDATE change_log SET processed = TRUE WHERE processed = FALSE;

            v_end_time := clock_timestamp();

            RAISE NOTICE 'Full refresh of all 8 materialized views completed in %ms.',
                EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time));
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Add function to get individual view stats
    op.execute("""
        CREATE OR REPLACE FUNCTION get_view_stats()
        RETURNS TABLE(
            view_name TEXT,
            row_count BIGINT,
            size_bytes BIGINT,
            last_refresh TIMESTAMP
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                schemaname || '.' || matviewname as view_name,
                n_live_tup as row_count,
                pg_total_relation_size(schemaname || '.' || matviewname) as size_bytes,
                last_vacuum as last_refresh
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            AND relname IN (
                'traceability_matrix',
                'impact_analysis',
                'coverage_analysis',
                'dependency_graph',
                'timeline_view',
                'status_dashboard',
                'search_index',
                'agent_interface'
            );
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Add function to refresh specific view
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_view(view_name TEXT)
        RETURNS void AS $$
        DECLARE
            v_start_time TIMESTAMP;
            v_end_time TIMESTAMP;
        BEGIN
            v_start_time := clock_timestamp();

            EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', view_name);

            v_end_time := clock_timestamp();

            RAISE NOTICE 'Refreshed view % in %ms',
                view_name,
                EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time));
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Revert to previous refresh functions."""
    op.execute("DROP FUNCTION IF EXISTS refresh_view(TEXT);")
    op.execute("DROP FUNCTION IF EXISTS get_view_stats();")

    # Revert to 3-view refresh functions
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_materialized_views_incremental()
        RETURNS void AS $$
        DECLARE
            v_changed_items UUID[];
            v_changed_links UUID[];
            v_has_changes BOOLEAN;
        BEGIN
            SELECT ARRAY_AGG(DISTINCT record_id)
            INTO v_changed_items
            FROM change_log
            WHERE table_name = 'items'
            AND processed = FALSE;

            SELECT ARRAY_AGG(DISTINCT record_id)
            INTO v_changed_links
            FROM change_log
            WHERE table_name = 'links'
            AND processed = FALSE;

            v_has_changes := (v_changed_items IS NOT NULL OR v_changed_links IS NOT NULL);

            IF v_has_changes THEN
                REFRESH MATERIALIZED VIEW CONCURRENTLY traceability_matrix;
                REFRESH MATERIALIZED VIEW CONCURRENTLY impact_analysis;
                REFRESH MATERIALIZED VIEW CONCURRENTLY coverage_analysis;

                UPDATE change_log
                SET processed = TRUE
                WHERE processed = FALSE;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)
