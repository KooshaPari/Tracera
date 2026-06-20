"""Add design_token_refs table for design system token tracking.

Links components and items to design tokens (colors, typography, spacing, etc.)
with Figma integration.

Revision ID: 040_add_design_token_refs
Revises: 039_add_component_usage
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "040_add_design_token_refs"
down_revision = "039_add_component_usage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create design_token_refs table for design system tokens."""
    op.create_table(
        "design_token_refs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # References - can link to components or items
        sa.Column(
            "component_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("library_components.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=True,
        ),
        # Token identity
        sa.Column("token_type", sa.String(50), nullable=False),  # color, typography, spacing, shadow, border, motion
        sa.Column("token_path", sa.String(500), nullable=False),  # e.g., "colors.primary.500", "typography.heading.lg"
        sa.Column("token_name", sa.String(255), nullable=False),
        # Resolved value
        sa.Column("resolved_value", sa.String(255), nullable=True),  # e.g., "#3b82f6", "16px"
        sa.Column(
            "resolved_value_type",
            sa.String(50),
            nullable=True,
        ),  # hex, rgb, px, rem, etc.
        # Figma integration
        sa.Column("figma_style_id", sa.String(100), nullable=True),
        sa.Column("figma_file_key", sa.String(100), nullable=True),
        # Usage context
        sa.Column("usage_property", sa.String(100), nullable=True),  # e.g., "backgroundColor", "fontSize"
        sa.Column("usage_context", sa.String(100), nullable=True),  # where it's used
        # Sync status
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String(20), server_default="'synced'", nullable=False),
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
    op.create_index("ix_design_token_refs_project_id", "design_token_refs", ["project_id"])
    op.create_index("ix_design_token_refs_component_id", "design_token_refs", ["component_id"])
    op.create_index("ix_design_token_refs_item_id", "design_token_refs", ["item_id"])
    op.create_index("ix_design_token_refs_token_type", "design_token_refs", ["token_type"])
    op.create_index("ix_design_token_refs_token_path", "design_token_refs", ["token_path"])
    op.create_index("ix_design_token_refs_token_name", "design_token_refs", ["token_name"])
    op.create_index("ix_design_token_refs_figma_style_id", "design_token_refs", ["figma_style_id"])
    op.create_index("ix_design_token_refs_sync_status", "design_token_refs", ["sync_status"])
    # Composite indexes
    op.create_index(
        "ix_design_token_refs_project_type",
        "design_token_refs",
        ["project_id", "token_type"],
    )
    op.create_index(
        "ix_design_token_refs_component_type",
        "design_token_refs",
        ["component_id", "token_type"],
    )


def downgrade() -> None:
    """Drop design_token_refs table."""
    op.drop_index("ix_design_token_refs_component_type", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_project_type", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_sync_status", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_figma_style_id", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_token_name", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_token_path", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_token_type", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_item_id", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_component_id", table_name="design_token_refs")
    op.drop_index("ix_design_token_refs_project_id", table_name="design_token_refs")
    op.drop_table("design_token_refs")
