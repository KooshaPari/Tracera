"""Add remaining materialized views (Dependency, Timeline, Dashboard, Search, Agent).

Revision ID: 004
Revises: 003
Create Date: 2025-11-21

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create remaining 5 materialized views."""
    # Layer 4: Dependency Graph View
    op.execute("""
        CREATE MATERIALIZED VIEW dependency_graph AS
        SELECT
            i.id as item_id,
            i.project_id,
            i.title,
            i.view,
            i.item_type,
            i.status,
            COUNT(DISTINCT l_out.id) as outgoing_links,
            COUNT(DISTINCT l_in.id) as incoming_links,
            ARRAY_AGG(DISTINCT l_out.target_item_id) FILTER (WHERE l_out.id IS NOT NULL) as depends_on,
            ARRAY_AGG(DISTINCT l_in.source_item_id) FILTER (WHERE l_in.id IS NOT NULL) as depended_by,
            CASE
                WHEN COUNT(DISTINCT l_in.id) = 0 THEN 'root'
                WHEN COUNT(DISTINCT l_out.id) = 0 THEN 'leaf'
                ELSE 'intermediate'
            END as node_type
        FROM items i
        LEFT JOIN links l_out ON i.id = l_out.source_item_id
        LEFT JOIN links l_in ON i.id = l_in.target_item_id
        WHERE i.deleted_at IS NULL
        GROUP BY i.id, i.project_id, i.title, i.view, i.item_type, i.status;
    """)

    op.execute("CREATE UNIQUE INDEX idx_dependency_unique ON dependency_graph(item_id);")
    op.execute("CREATE INDEX idx_dependency_project ON dependency_graph(project_id);")
    op.execute("CREATE INDEX idx_dependency_node_type ON dependency_graph(node_type);")
    op.execute("CREATE INDEX idx_dependency_view ON dependency_graph(view);")

    # Layer 5: Timeline View
    op.execute("""
        CREATE MATERIALIZED VIEW timeline_view AS
        SELECT
            e.id as event_id,
            e.project_id,
            e.item_id,
            i.title as item_title,
            i.view as item_view,
            e.event_type,
            e.event_data,
            e.created_at,
            e.agent_id as created_by,
            LAG(e.created_at) OVER (PARTITION BY e.item_id ORDER BY e.created_at) as previous_event_time,
            LEAD(e.created_at) OVER (PARTITION BY e.item_id ORDER BY e.created_at) as next_event_time
        FROM agent_events e
        JOIN items i ON e.item_id = i.id
        WHERE i.deleted_at IS NULL
        ORDER BY e.created_at DESC;
    """)

    op.execute("CREATE UNIQUE INDEX idx_timeline_unique ON timeline_view(event_id);")
    op.execute("CREATE INDEX idx_timeline_project ON timeline_view(project_id);")
    op.execute("CREATE INDEX idx_timeline_item ON timeline_view(item_id);")
    op.execute("CREATE INDEX idx_timeline_created ON timeline_view(created_at DESC);")
    op.execute("CREATE INDEX idx_timeline_event_type ON timeline_view(event_type);")

    # Layer 6: Status Dashboard View
    op.execute("""
        CREATE MATERIALIZED VIEW status_dashboard AS
        SELECT
            p.id as project_id,
            p.name as project_name,
            COUNT(DISTINCT i.id) as total_items,
            COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'todo') as todo_count,
            COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'in_progress') as in_progress_count,
            COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'done') as done_count,
            COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'blocked') as blocked_count,
            COUNT(DISTINCT l.id) as total_links,
            COUNT(DISTINCT i.id) FILTER (WHERE i.view = 'FEATURE') as feature_count,
            COUNT(DISTINCT i.id) FILTER (WHERE i.view = 'CODE') as code_count,
            COUNT(DISTINCT i.id) FILTER (WHERE i.view = 'TEST') as test_count,
            ROUND(
                COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'done')::NUMERIC /
                NULLIF(COUNT(DISTINCT i.id), 0) * 100,
                2
            ) as completion_percentage,
            MAX(i.updated_at) as last_updated
        FROM projects p
        LEFT JOIN items i ON p.id = i.project_id AND i.deleted_at IS NULL
        LEFT JOIN links l ON p.id = l.project_id
        GROUP BY p.id, p.name;
    """)

    op.execute("CREATE UNIQUE INDEX idx_dashboard_unique ON status_dashboard(project_id);")
    op.execute("CREATE INDEX idx_dashboard_completion ON status_dashboard(completion_percentage DESC);")
    op.execute("CREATE INDEX idx_dashboard_updated ON status_dashboard(last_updated DESC);")

    # Layer 7: Search Index View
    op.execute("""
        CREATE MATERIALIZED VIEW search_index AS
        SELECT
            i.id as item_id,
            i.project_id,
            i.title,
            i.description,
            i.view,
            i.item_type,
            i.status,
            i.item_metadata as metadata,
            to_tsvector('english',
                COALESCE(i.title, '') || ' ' ||
                COALESCE(i.description, '') || ' ' ||
                COALESCE(i.item_type, '') || ' ' ||
                COALESCE(i.item_metadata::text, '')
            ) as search_vector,
            i.created_at,
            i.updated_at
        FROM items i
        WHERE i.deleted_at IS NULL;
    """)

    op.execute("CREATE UNIQUE INDEX idx_search_unique ON search_index(item_id);")
    op.execute("CREATE INDEX idx_search_project ON search_index(project_id);")
    op.execute("CREATE INDEX idx_search_vector ON search_index USING gin(search_vector);")
    op.execute("CREATE INDEX idx_search_view ON search_index(view);")
    op.execute("CREATE INDEX idx_search_status ON search_index(status);")

    # Layer 8: Agent Interface View
    op.execute("""
        CREATE MATERIALIZED VIEW agent_interface AS
        SELECT
            i.id as item_id,
            i.project_id,
            i.title,
            i.view,
            i.item_type,
            i.status,
            i.item_metadata as metadata,
            COUNT(DISTINCT l_out.id) as link_count,
            ARRAY_AGG(DISTINCT l_out.link_type) FILTER (WHERE l_out.id IS NOT NULL) as link_types,
            COUNT(DISTINCT e.id) as event_count,
            MAX(e.created_at) as last_event_at,
            i.created_at,
            i.updated_at,
            CASE
                WHEN i.updated_at > NOW() - INTERVAL '1 day' THEN 'recent'
                WHEN i.updated_at > NOW() - INTERVAL '7 days' THEN 'active'
                WHEN i.updated_at > NOW() - INTERVAL '30 days' THEN 'stale'
                ELSE 'inactive'
            END as activity_status
        FROM items i
        LEFT JOIN links l_out ON i.id = l_out.source_item_id
        LEFT JOIN agent_events e ON i.id = e.item_id
        WHERE i.deleted_at IS NULL
        GROUP BY i.id, i.project_id, i.title, i.view, i.item_type, i.status, i.item_metadata, i.created_at, i.updated_at;
    """)

    op.execute("CREATE UNIQUE INDEX idx_agent_unique ON agent_interface(item_id);")
    op.execute("CREATE INDEX idx_agent_project ON agent_interface(project_id);")
    op.execute("CREATE INDEX idx_agent_activity ON agent_interface(activity_status);")
    op.execute("CREATE INDEX idx_agent_updated ON agent_interface(updated_at DESC);")
    op.execute("CREATE INDEX idx_agent_view ON agent_interface(view);")


def downgrade() -> None:
    """Drop remaining materialized views."""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS agent_interface;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS search_index;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS status_dashboard;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS timeline_view;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS dependency_graph;")
