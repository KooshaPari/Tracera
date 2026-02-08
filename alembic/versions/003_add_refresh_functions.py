"""Add materialized view refresh functions.

Revision ID: 003
Revises: 002
Create Date: 2025-11-21

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create refresh functions for materialized views."""
    # Create incremental refresh function
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_materialized_views_incremental()
        RETURNS void AS $$
        DECLARE
            v_changed_items UUID[];
            v_changed_links UUID[];
            v_has_changes BOOLEAN;
        BEGIN
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
                -- Refresh all materialized views concurrently
                REFRESH MATERIALIZED VIEW CONCURRENTLY traceability_matrix;
                REFRESH MATERIALIZED VIEW CONCURRENTLY impact_analysis;
                REFRESH MATERIALIZED VIEW CONCURRENTLY coverage_analysis;

                -- Mark changes as processed
                UPDATE change_log
                SET processed = TRUE
                WHERE processed = FALSE;

                -- Log refresh
                RAISE NOTICE 'Refreshed materialized views. Items changed: %, Links changed: %',
                    COALESCE(array_length(v_changed_items, 1), 0),
                    COALESCE(array_length(v_changed_links, 1), 0);
            ELSE
                RAISE NOTICE 'No changes detected. Skipping refresh.';
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create full refresh function
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_materialized_views_full()
        RETURNS void AS $$
        BEGIN
            -- Refresh all materialized views
            REFRESH MATERIALIZED VIEW CONCURRENTLY traceability_matrix;
            REFRESH MATERIALIZED VIEW CONCURRENTLY impact_analysis;
            REFRESH MATERIALIZED VIEW CONCURRENTLY coverage_analysis;

            -- Mark all changes as processed
            UPDATE change_log SET processed = TRUE WHERE processed = FALSE;

            RAISE NOTICE 'Full refresh of all materialized views completed.';
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create function to get view staleness
    op.execute("""
        CREATE OR REPLACE FUNCTION get_view_staleness()
        RETURNS TABLE(
            view_name TEXT,
            unprocessed_changes BIGINT,
            oldest_change TIMESTAMP,
            staleness_seconds NUMERIC
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                'materialized_views'::TEXT as view_name,
                COUNT(*)::BIGINT as unprocessed_changes,
                MIN(changed_at) as oldest_change,
                EXTRACT(EPOCH FROM (NOW() - MIN(changed_at)))::NUMERIC as staleness_seconds
            FROM change_log
            WHERE processed = FALSE;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create function to clean old change log entries
    op.execute("""
        CREATE OR REPLACE FUNCTION cleanup_change_log(days_to_keep INTEGER DEFAULT 30)
        RETURNS BIGINT AS $$
        DECLARE
            v_deleted_count BIGINT;
        BEGIN
            DELETE FROM change_log
            WHERE processed = TRUE
            AND changed_at < NOW() - (days_to_keep || ' days')::INTERVAL;

            GET DIAGNOSTICS v_deleted_count = ROW_COUNT;

            RAISE NOTICE 'Deleted % old change log entries', v_deleted_count;

            RETURN v_deleted_count;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Drop refresh functions."""
    op.execute("DROP FUNCTION IF EXISTS cleanup_change_log(INTEGER);")
    op.execute("DROP FUNCTION IF EXISTS get_view_staleness();")
    op.execute("DROP FUNCTION IF EXISTS refresh_materialized_views_full();")
    op.execute("DROP FUNCTION IF EXISTS refresh_materialized_views_incremental();")
