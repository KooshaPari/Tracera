"""Initial schema - create base tables.

Revision ID: 000
Revises:
Create Date: 2025-11-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial database schema for TraceRTM."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Enable pg_trgm for full-text search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    # Enable pgcrypto for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Create projects table
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("idx_projects_name", "projects", ["name"])

    # Create items table
    op.create_table(
        "items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("view", sa.String(50), nullable=False),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="todo"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("item_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for items
    op.create_index("idx_items_project_id", "items", ["project_id"])
    op.create_index("idx_items_view", "items", ["view"])
    op.create_index("idx_items_item_type", "items", ["item_type"])
    op.create_index("idx_items_status", "items", ["status"])
    op.create_index("idx_items_priority", "items", ["priority"])
    op.create_index("idx_items_owner", "items", ["owner"])
    op.create_index("idx_items_parent_id", "items", ["parent_id"])
    op.create_index("idx_items_deleted_at", "items", ["deleted_at"])
    op.create_index("idx_items_project_view", "items", ["project_id", "view"])
    op.create_index("idx_items_project_status", "items", ["project_id", "status"])
    op.create_index("idx_items_project_type", "items", ["project_id", "item_type"])

    # Create full-text search index on items
    op.execute("""
        CREATE INDEX idx_items_title_trgm ON items USING gin (title gin_trgm_ops)
    """)
    op.execute("""
        CREATE INDEX idx_items_description_trgm ON items USING gin (description gin_trgm_ops)
    """)

    # Create links table
    op.create_table(
        "links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("link_type", sa.String(50), nullable=False),
        sa.Column("link_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_item_id"], ["items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_item_id"], ["items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for links
    op.create_index("idx_links_project_id", "links", ["project_id"])
    op.create_index("idx_links_source_item_id", "links", ["source_item_id"])
    op.create_index("idx_links_target_item_id", "links", ["target_item_id"])
    op.create_index("idx_links_link_type", "links", ["link_type"])
    op.create_index("idx_links_source_target", "links", ["source_item_id", "target_item_id"])
    op.create_index("idx_links_project_type", "links", ["project_id", "link_type"])

    # Create agents table
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("agent_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("agent_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("last_activity_at", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for agents
    op.create_index("idx_agents_project_id", "agents", ["project_id"])
    op.create_index("idx_agents_project_status", "agents", ["project_id", "status"])

    # Create agent_events table
    op.create_table(
        "agent_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for agent_events
    op.create_index("idx_agent_events_project_id", "agent_events", ["project_id"])
    op.create_index("idx_agent_events_agent_id", "agent_events", ["agent_id"])
    op.create_index("idx_agent_events_item_id", "agent_events", ["item_id"])
    op.create_index("idx_agent_events_project_agent", "agent_events", ["project_id", "agent_id"])
    op.create_index("idx_agent_events_project_type", "agent_events", ["project_id", "event_type"])

    # Create trigger to update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add update triggers to all tables
    for table in ["projects", "items", "links", "agents", "agent_events"]:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    """Drop all tables and extensions."""
    # Drop triggers
    for table in ["projects", "items", "links", "agents", "agent_events"]:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("agent_events")
    op.drop_table("agents")
    op.drop_table("links")
    op.drop_table("items")
    op.drop_table("projects")

    # Drop extensions
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS vector")
