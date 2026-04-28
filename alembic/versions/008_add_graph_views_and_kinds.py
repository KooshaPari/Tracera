"""Add graph views, node kinds, item views, link types, and external links.

Revision ID: 008_add_graph_views_and_kinds
Revises: 007_add_problems_and_processes
Create Date: 2026-01-28
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import context, op
from tracertm.models.types import JSONType

# revision identifiers, used by Alembic.
revision = "008_add_graph_views_and_kinds"
down_revision = "007_add_problems_and_processes"
branch_labels = None
depends_on = None


def _uuid() -> str:
    return str(uuid.uuid4())


def _create_tables() -> None:
    """Create new tables for views, node kinds, item views, link types, and external links."""
    op.create_table(
        "views",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("view_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_views_project_name", "views", ["project_id", "name"], unique=True)

    op.create_table(
        "node_kinds",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("kind_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_node_kinds_project_name", "node_kinds", ["project_id", "name"], unique=True)

    op.create_table(
        "item_views",
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("view_id", sa.String(length=255), sa.ForeignKey("views.id", ondelete="CASCADE"), primary_key=True),
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
    op.create_index("idx_item_views_item", "item_views", ["item_id"])
    op.create_index("idx_item_views_view", "item_views", ["view_id"])
    op.create_index("idx_item_views_project_view", "item_views", ["project_id", "view_id"])

    op.create_table(
        "link_types",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("link_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_link_types_project_name", "link_types", ["project_id", "name"], unique=True)

    op.create_table(
        "external_links",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("target", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("link_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_external_links_item", "external_links", ["item_id"])
    op.create_index("idx_external_links_project", "external_links", ["project_id"])


def _add_columns() -> None:
    """Add new columns to existing tables."""
    op.add_column(
        "items",
        sa.Column(
            "node_kind_id",
            sa.String(length=255),
            sa.ForeignKey("node_kinds.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("idx_items_project_node_kind", "items", ["project_id", "node_kind_id"])


def _backfill_views_and_kinds(
    conn: sa.engine.Connection,
) -> tuple[dict[tuple[str, str], str], dict[tuple[str, str], str]]:
    """Backfill views and node kinds from existing items data."""
    views_table = sa.table(
        "views",
        sa.column("id", sa.String),
        sa.column("project_id", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("view_metadata", JSONType),
    )
    node_kinds_table = sa.table(
        "node_kinds",
        sa.column("id", sa.String),
        sa.column("project_id", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("kind_metadata", JSONType),
    )

    # Backfill views from items.view
    view_rows = conn.execute(sa.text("select distinct project_id, view from items where view is not null")).fetchall()
    view_id_map: dict[tuple[str, str], str] = {}
    for project_id, view_name in view_rows:
        view_id = _uuid()
        view_id_map[project_id, view_name] = view_id
        conn.execute(
            views_table.insert().values(
                id=view_id,
                project_id=project_id,
                name=view_name,
                description=None,
                view_metadata={},
            ),
        )

    # Backfill node kinds from items.item_type
    kind_rows = conn.execute(
        sa.text("select distinct project_id, item_type from items where item_type is not null"),
    ).fetchall()
    kind_id_map: dict[tuple[str, str], str] = {}
    for project_id, kind_name in kind_rows:
        kind_id = _uuid()
        kind_id_map[project_id, kind_name] = kind_id
        conn.execute(
            node_kinds_table.insert().values(
                id=kind_id,
                project_id=project_id,
                name=kind_name,
                description=None,
                kind_metadata={},
            ),
        )

    return view_id_map, kind_id_map


def _migrate_data(conn: sa.engine.Connection, view_id_map: dict[tuple[str, str], str]) -> None:
    """Migrate existing data to new tables."""
    item_views_table = sa.table(
        "item_views",
        sa.column("item_id", sa.String),
        sa.column("view_id", sa.String),
        sa.column("project_id", sa.String),
        sa.column("is_primary", sa.Boolean),
    )
    link_types_table = sa.table(
        "link_types",
        sa.column("id", sa.String),
        sa.column("project_id", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("link_metadata", JSONType),
    )

    # Update items.node_kind_id using item_type
    conn.execute(
        sa.text(
            """
            update items
            set node_kind_id = nk.id
            from node_kinds nk
            where items.project_id = nk.project_id
              and items.item_type = nk.name
              and items.node_kind_id is null
            """,
        ),
    )

    # Backfill item_views from items.view
    item_rows = conn.execute(sa.text("select id, project_id, view from items where view is not null")).fetchall()
    item_view_inserts = []
    for item_id, project_id, view_name in item_rows:
        view_id = view_id_map.get((project_id, view_name))
        if not view_id:
            continue
        item_view_inserts.append({
            "item_id": item_id,
            "view_id": view_id,
            "project_id": project_id,
            "is_primary": True,
        })
    if item_view_inserts:
        conn.execute(item_views_table.insert(), item_view_inserts)

    # Backfill link types from links.link_type
    link_type_rows = conn.execute(
        sa.text("select distinct project_id, link_type from links where link_type is not null"),
    ).fetchall()
    for project_id, link_type_name in link_type_rows:
        conn.execute(
            link_types_table.insert().values(
                id=_uuid(),
                project_id=project_id,
                name=link_type_name,
                description=None,
                link_metadata={},
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

    view_id_map, _kind_id_map = _backfill_views_and_kinds(conn)
    _migrate_data(conn, view_id_map)


def downgrade() -> None:
    """Downgrade."""
    op.drop_index("idx_items_project_node_kind", table_name="items")
    op.drop_column("items", "node_kind_id")

    op.drop_index("idx_external_links_project", table_name="external_links")
    op.drop_index("idx_external_links_item", table_name="external_links")
    op.drop_table("external_links")

    op.drop_index("idx_link_types_project_name", table_name="link_types")
    op.drop_table("link_types")

    op.drop_index("idx_item_views_project_view", table_name="item_views")
    op.drop_index("idx_item_views_view", table_name="item_views")
    op.drop_index("idx_item_views_item", table_name="item_views")
    op.drop_table("item_views")

    op.drop_index("idx_node_kinds_project_name", table_name="node_kinds")
    op.drop_table("node_kinds")

    op.drop_index("idx_views_project_name", table_name="views")
    op.drop_table("views")
