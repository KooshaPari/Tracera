"""Add component_usage table for tracking component usage in pages.

Records where library components are used, with context, props, and variants.

Revision ID: 039_add_component_usage
Revises: 038_add_equivalence_links
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "039_add_component_usage"
down_revision = "038_add_equivalence_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create component_usage table for tracking component instances."""
    op.create_table(
        "component_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Component reference
        sa.Column(
            "component_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("library_components.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Usage location
        sa.Column(
            "page_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("column_number", sa.Integer(), nullable=True),
        # Context
        sa.Column("usage_context", sa.String(100), nullable=True),  # form-field, navigation, etc.
        sa.Column("parent_component_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Props and variant usage
        sa.Column(
            "props_used",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("variant_used", sa.String(100), nullable=True),
        # Code reference
        sa.Column(
            "code_entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("code_entities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Frequency tracking
        sa.Column("usage_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        # Metadata
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create indexes
    op.create_index("ix_component_usage_project_id", "component_usage", ["project_id"])
    op.create_index("ix_component_usage_component_id", "component_usage", ["component_id"])
    op.create_index("ix_component_usage_page_item_id", "component_usage", ["page_item_id"])
    op.create_index("ix_component_usage_file_path", "component_usage", ["file_path"])
    op.create_index("ix_component_usage_usage_context", "component_usage", ["usage_context"])
    op.create_index(
        "ix_component_usage_parent_component_id",
        "component_usage",
        ["parent_component_id"],
    )
    op.create_index("ix_component_usage_code_entity_id", "component_usage", ["code_entity_id"])
    # Composite index for finding all usages of a component
    op.create_index(
        "ix_component_usage_component_last_seen",
        "component_usage",
        ["component_id", "last_seen_at"],
    )


def downgrade() -> None:
    """Drop component_usage table."""
    op.drop_index("ix_component_usage_component_last_seen", table_name="component_usage")
    op.drop_index("ix_component_usage_code_entity_id", table_name="component_usage")
    op.drop_index("ix_component_usage_parent_component_id", table_name="component_usage")
    op.drop_index("ix_component_usage_usage_context", table_name="component_usage")
    op.drop_index("ix_component_usage_file_path", table_name="component_usage")
    op.drop_index("ix_component_usage_page_item_id", table_name="component_usage")
    op.drop_index("ix_component_usage_component_id", table_name="component_usage")
    op.drop_index("ix_component_usage_project_id", table_name="component_usage")
    op.drop_table("component_usage")
