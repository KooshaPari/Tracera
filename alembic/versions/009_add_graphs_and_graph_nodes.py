"""Add graph registry and graph node memberships, add graph_id to links.

Revision ID: 009_add_graphs_and_graph_nodes
Revises: 008_add_graph_views_and_kinds
Create Date: 2026-01-28
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import context, op
from tracertm.models.types import JSONType

# revision identifiers, used by Alembic.
revision = "009_add_graphs_and_graph_nodes"
down_revision = "008_add_graph_views_and_kinds"
branch_labels = None
depends_on = None


def _uuid() -> str:
    return str(uuid.uuid4())


def _create_tables() -> None:
    """Create new tables for graphs and graph nodes."""
    op.create_table(
        "graphs",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("graph_type", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "root_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("graph_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_graphs_project_type", "graphs", ["project_id", "graph_type"])
    op.create_index("idx_graphs_project_name", "graphs", ["project_id", "name"], unique=True)

    op.create_table(
        "graph_nodes",
        sa.Column("graph_id", sa.String(length=255), sa.ForeignKey("graphs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_graph_nodes_graph", "graph_nodes", ["graph_id"])
    op.create_index("idx_graph_nodes_item", "graph_nodes", ["item_id"])
    op.create_index("idx_graph_nodes_project_graph", "graph_nodes", ["project_id", "graph_id"])


def _add_columns() -> None:
    """Add new columns to existing tables."""
    op.add_column(
        "links",
        sa.Column("graph_id", sa.String(length=255), sa.ForeignKey("graphs.id", ondelete="CASCADE"), nullable=True),
    )
    op.create_index("idx_links_project_graph", "links", ["project_id", "graph_id"])


def _backfill_graphs_from_views(conn: sa.engine.Connection) -> dict[tuple[str, str], str]:
    """Create graphs from existing views."""
    graphs_table = sa.table(
        "graphs",
        sa.column("id", sa.String),
        sa.column("project_id", sa.String),
        sa.column("name", sa.String),
        sa.column("graph_type", sa.String),
        sa.column("description", sa.Text),
        sa.column("root_item_id", sa.String),
        sa.column("graph_metadata", JSONType),
    )

    view_rows = conn.execute(sa.text("select id, project_id, name from views")).fetchall()
    graph_ids: dict[tuple[str, str], str] = {}

    for _view_id, project_id, view_name in view_rows:
        graph_id = _uuid()
        graph_ids[project_id, view_name] = graph_id
        conn.execute(
            graphs_table.insert().values(
                id=graph_id,
                project_id=project_id,
                name=f"{view_name} graph",
                graph_type=view_name,
                description=None,
                root_item_id=None,
                graph_metadata={},
            ),
        )

    return graph_ids


def _migrate_graph_nodes(conn: sa.engine.Connection, graph_ids: dict[tuple[str, str], str]) -> None:
    """Migrate item_views to graph_nodes."""
    graph_nodes_table = sa.table(
        "graph_nodes",
        sa.column("graph_id", sa.String),
        sa.column("item_id", sa.String),
        sa.column("project_id", sa.String),
        sa.column("is_primary", sa.Boolean),
    )

    # Backfill graph_nodes using existing item_views
    item_view_rows = conn.execute(sa.text("select item_id, project_id, view_id, is_primary from item_views")).fetchall()

    graph_node_inserts = []
    for item_id, project_id, view_id, is_primary in item_view_rows:
        # Find the view name for this view_id
        view_name = conn.execute(
            sa.text("select name from views where id = :vid"),
            {"vid": view_id},
        ).scalar()
        if not view_name:
            continue
        graph_id = graph_ids.get((project_id, view_name))
        if not graph_id:
            continue
        graph_node_inserts.append({
            "graph_id": graph_id,
            "item_id": item_id,
            "project_id": project_id,
            "is_primary": is_primary,
        })

    if graph_node_inserts:
        conn.execute(graph_nodes_table.insert(), graph_node_inserts)


def _update_link_graphs(conn: sa.engine.Connection) -> None:
    """Update links.graph_id based on source item's primary view graph."""
    conn.execute(
        sa.text(
            """
            update links l
            set graph_id = g.id
            from items i
            join item_views iv on iv.item_id = i.id and iv.is_primary = true
            join views v on v.id = iv.view_id
            join graphs g on g.project_id = i.project_id and g.graph_type = v.name
            where l.graph_id is null
              and l.source_item_id = i.id
            """,
        ),
    )


def upgrade() -> None:
    """Upgrade."""
    _create_tables()
    _add_columns()

    if context.is_offline_mode():
        return

    conn = op.get_bind()
    if conn is None:
        return

    graph_ids = _backfill_graphs_from_views(conn)
    _migrate_graph_nodes(conn, graph_ids)
    _update_link_graphs(conn)


def downgrade() -> None:
    """Downgrade."""
    op.drop_index("idx_links_project_graph", table_name="links")
    op.drop_column("links", "graph_id")

    op.drop_index("idx_graph_nodes_project_graph", table_name="graph_nodes")
    op.drop_index("idx_graph_nodes_item", table_name="graph_nodes")
    op.drop_index("idx_graph_nodes_graph", table_name="graph_nodes")
    op.drop_table("graph_nodes")

    op.drop_index("idx_graphs_project_name", table_name="graphs")
    op.drop_index("idx_graphs_project_type", table_name="graphs")
    op.drop_table("graphs")
