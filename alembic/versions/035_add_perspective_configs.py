"""Add perspective_configs table for project-level overrides.

Stores project-customizable perspective configurations with
filters, layouts, and entity type mappings.

Revision ID: 035_add_perspective_configs
Revises: 034_add_code_entities
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "035_add_perspective_configs"
down_revision = "034_add_code_entities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create perspective_configs table."""
    op.create_table(
        "perspective_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identity
        sa.Column("perspective_type", sa.String(50), nullable=False),  # product, business, technical, etc.
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # Visual
        sa.Column("icon", sa.String(100), nullable=False),  # Lucide icon name
        sa.Column("color", sa.String(20), nullable=False),  # Hex color
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        # Filtering
        sa.Column(
            "include_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "exclude_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "include_views",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "exclude_views",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Entity type mappings
        sa.Column(
            "entity_type_mappings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Layout
        sa.Column("layout_preference", sa.String(50), server_default="'cose'", nullable=False),
        sa.Column("default_expansion_level", sa.Integer(), server_default="2", nullable=False),
        # Dimension defaults
        sa.Column(
            "default_dimension_filters",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Flags
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_custom", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        # Unique constraint
        sa.UniqueConstraint("project_id", "perspective_type", name="uq_perspective_configs_project_type"),
    )

    # Create indexes
    op.create_index("ix_perspective_configs_project_id", "perspective_configs", ["project_id"])
    op.create_index("ix_perspective_configs_perspective_type", "perspective_configs", ["perspective_type"])
    op.create_index("ix_perspective_configs_is_active", "perspective_configs", ["is_active"])
    op.create_index("ix_perspective_configs_display_order", "perspective_configs", ["display_order"])


def downgrade() -> None:
    """Drop perspective_configs table."""
    op.drop_index("ix_perspective_configs_display_order", table_name="perspective_configs")
    op.drop_index("ix_perspective_configs_is_active", table_name="perspective_configs")
    op.drop_index("ix_perspective_configs_perspective_type", table_name="perspective_configs")
    op.drop_index("ix_perspective_configs_project_id", table_name="perspective_configs")
    op.drop_table("perspective_configs")
