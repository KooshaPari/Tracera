"""Enforce graph integrity, add registries, snapshots, and rules.

Revision ID: 011_graph_integrity
Revises: 010_merge_heads
Create Date: 2026-01-28
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from tracertm.models.types import JSONType

# revision identifiers, used by Alembic.
revision = "011_graph_integrity"
down_revision = "010_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # Graph metadata additions
    op.add_column(
        "graphs",
        sa.Column("graph_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "graphs",
        sa.Column("graph_rules", JSONType, nullable=False, server_default=sa.text("'{}'")),
    )

    # Registries
    op.create_table(
        "graph_types",
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
        sa.Column("type_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_graph_types_project_name", "graph_types", ["project_id", "name"], unique=True)

    op.create_table(
        "edge_types",
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
        sa.Column("edge_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_edge_types_project_name", "edge_types", ["project_id", "name"], unique=True)

    op.create_table(
        "node_kind_rules",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "node_kind_id",
            sa.String(length=255),
            sa.ForeignKey("node_kinds.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rule_metadata", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_node_kind_rules_project_kind", "node_kind_rules", ["project_id", "node_kind_id"])

    op.create_table(
        "graph_snapshots",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "graph_id",
            sa.String(length=255),
            sa.ForeignKey("graphs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("snapshot_json", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("snapshot_hash", sa.String(length=128), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_graph_snapshots_project_graph", "graph_snapshots", ["project_id", "graph_id"])
    op.create_index("idx_graph_snapshots_project_version", "graph_snapshots", ["project_id", "version"])

    op.create_table(
        "graph_changes",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "graph_id",
            sa.String(length=255),
            sa.ForeignKey("graphs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("change_type", sa.String(length=100), nullable=False),
        sa.Column("change_payload", JSONType, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_graph_changes_project_graph", "graph_changes", ["project_id", "graph_id"])
    op.create_index("idx_graph_changes_project_type", "graph_changes", ["project_id", "change_type"])

    # Enforce primary view uniqueness (partial unique index)
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_item_views_primary
        ON item_views (item_id)
        WHERE is_primary = true;
        """,
    )

    # Backfill node_kind_id if missing
    op.execute(
        """
        INSERT INTO node_kinds (id, project_id, name, description, kind_metadata, created_at, updated_at)
        SELECT
            md5(random()::text || clock_timestamp()::text),
            i.project_id,
            COALESCE(NULLIF(i.item_type, ''), 'unknown') as name,
            NULL,
            '{}'::jsonb,
            now(),
            now()
        FROM items i
        LEFT JOIN node_kinds nk
          ON nk.project_id = i.project_id AND nk.name = COALESCE(NULLIF(i.item_type, ''), 'unknown')
        WHERE nk.id IS NULL;
        """,
    )
    op.execute(
        """
        UPDATE items i
        SET node_kind_id = nk.id
        FROM node_kinds nk
        WHERE i.node_kind_id IS NULL
          AND nk.project_id = i.project_id
          AND nk.name = COALESCE(NULLIF(i.item_type, ''), 'unknown');
        """,
    )

    # Backfill links.graph_id for any remaining NULLs
    op.execute(
        """
        UPDATE links l
        SET graph_id = g.id
        FROM items i
        JOIN item_views iv ON iv.item_id = i.id AND iv.is_primary = true
        JOIN views v ON v.id = iv.view_id
        JOIN graphs g ON g.project_id = i.project_id AND g.graph_type = v.name
        WHERE l.graph_id IS NULL
          AND l.source_item_id = i.id;
        """,
    )

    # Ensure all links have graph_id, create fallback graph per project if needed
    op.execute(
        """
        INSERT INTO graphs (id, project_id, name, graph_type, description, root_item_id, graph_metadata, graph_rules, graph_version, created_at, updated_at)
        SELECT
            md5(random()::text || clock_timestamp()::text),
            p.id,
            'default graph',
            'default',
            NULL,
            NULL,
            '{}'::jsonb,
            '{}'::jsonb,
            1,
            now(),
            now()
        FROM projects p
        LEFT JOIN graphs g ON g.project_id = p.id AND g.graph_type = 'default'
        WHERE g.id IS NULL;
        """,
    )
    op.execute(
        """
        UPDATE links l
        SET graph_id = g.id
        FROM graphs g
        WHERE l.graph_id IS NULL
          AND g.project_id = l.project_id
          AND g.graph_type = 'default';
        """,
    )

    # Enforce NOT NULL on links.graph_id and items.node_kind_id
    op.alter_column("links", "graph_id", nullable=False)
    op.alter_column("items", "node_kind_id", nullable=False)

    # Seed graph_types registry from existing graphs
    op.execute(
        """
        WITH distinct_graph_types AS (
            SELECT DISTINCT g.project_id, g.graph_type
            FROM graphs g
            LEFT JOIN graph_types gt ON gt.project_id = g.project_id AND gt.name = g.graph_type
            WHERE gt.id IS NULL
        )
        INSERT INTO graph_types (id, project_id, name, description, type_metadata, created_at, updated_at)
        SELECT
            md5(random()::text || clock_timestamp()::text),
            d.project_id,
            d.graph_type,
            NULL,
            '{}'::jsonb,
            now(),
            now()
        FROM distinct_graph_types d;
        """,
    )

    # Seed edge_types registry from existing links
    op.execute(
        """
        WITH distinct_edge_types AS (
            SELECT DISTINCT l.project_id, l.link_type
            FROM links l
            LEFT JOIN edge_types et ON et.project_id = l.project_id AND et.name = l.link_type
            WHERE et.id IS NULL
        )
        INSERT INTO edge_types (id, project_id, name, description, edge_metadata, created_at, updated_at)
        SELECT
            md5(random()::text || clock_timestamp()::text),
            d.project_id,
            d.link_type,
            NULL,
            '{}'::jsonb,
            now(),
            now()
        FROM distinct_edge_types d;
        """,
    )

    # Seed node_kind_rules default allow-all
    op.execute(
        """
        INSERT INTO node_kind_rules (id, project_id, node_kind_id, name, description, rule_metadata, created_at, updated_at)
        SELECT
            md5(random()::text || clock_timestamp()::text),
            nk.project_id,
            nk.id,
            'default',
            NULL,
            '{"allowed_edges": ["*"]}'::jsonb,
            now(),
            now()
        FROM node_kinds nk
        LEFT JOIN node_kind_rules nkr ON nkr.node_kind_id = nk.id
        WHERE nkr.id IS NULL;
        """,
    )

    # Create graph_edges view for fast projection reads
    op.execute(
        """
        CREATE OR REPLACE VIEW graph_edges AS
        SELECT
            l.id,
            l.project_id,
            l.graph_id,
            l.link_type,
            l.source_item_id,
            l.target_item_id,
            l.link_metadata,
            l.created_at,
            l.updated_at
        FROM links l;
        """,
    )

    # Denormalization triggers to keep items.view and items.item_type in sync
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_item_denorm_fields()
        RETURNS trigger AS $$
        BEGIN
            IF NEW.node_kind_id IS NOT NULL THEN
                SELECT name INTO NEW.item_type FROM node_kinds WHERE id = NEW.node_kind_id;
            END IF;

            IF NEW.id IS NOT NULL THEN
                SELECT v.name INTO NEW.view
                FROM item_views iv
                JOIN views v ON v.id = iv.view_id
                WHERE iv.item_id = NEW.id AND iv.is_primary = true
                LIMIT 1;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_items_sync_denorm ON items;
        CREATE TRIGGER trg_items_sync_denorm
        BEFORE INSERT OR UPDATE ON items
        FOR EACH ROW EXECUTE FUNCTION sync_item_denorm_fields();
        """,
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_item_view_from_item_views()
        RETURNS trigger AS $$
        BEGIN
            UPDATE items i
            SET view = v.name
            FROM views v
            WHERE i.id = NEW.item_id AND NEW.is_primary = true AND v.id = NEW.view_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_item_views_sync ON item_views;
        CREATE TRIGGER trg_item_views_sync
        AFTER INSERT OR UPDATE ON item_views
        FOR EACH ROW EXECUTE FUNCTION sync_item_view_from_item_views();
        """,
    )


def downgrade() -> None:
    """Downgrade."""
    op.execute("DROP VIEW IF EXISTS graph_edges")

    op.execute("DROP TRIGGER IF EXISTS trg_item_views_sync ON item_views")
    op.execute("DROP FUNCTION IF EXISTS sync_item_view_from_item_views")
    op.execute("DROP TRIGGER IF EXISTS trg_items_sync_denorm ON items")
    op.execute("DROP FUNCTION IF EXISTS sync_item_denorm_fields")

    op.drop_index("idx_graph_changes_project_type", table_name="graph_changes")
    op.drop_index("idx_graph_changes_project_graph", table_name="graph_changes")
    op.drop_table("graph_changes")

    op.drop_index("idx_graph_snapshots_project_version", table_name="graph_snapshots")
    op.drop_index("idx_graph_snapshots_project_graph", table_name="graph_snapshots")
    op.drop_table("graph_snapshots")

    op.drop_index("idx_node_kind_rules_project_kind", table_name="node_kind_rules")
    op.drop_table("node_kind_rules")

    op.drop_index("idx_edge_types_project_name", table_name="edge_types")
    op.drop_table("edge_types")

    op.drop_index("idx_graph_types_project_name", table_name="graph_types")
    op.drop_table("graph_types")

    op.drop_column("graphs", "graph_rules")
    op.drop_column("graphs", "graph_version")
