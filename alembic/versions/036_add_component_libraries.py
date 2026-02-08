"""Add component_libraries and library_components tables.

Creates design system tracking with Storybook/Figma integration,
component props, and usage statistics.

Revision ID: 036_add_component_libraries
Revises: 035_add_perspective_configs
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "036_add_component_libraries"
down_revision = "035_add_perspective_configs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create component_libraries and library_components tables."""
    # Create component_libraries table
    op.create_table(
        "component_libraries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identity
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(50), nullable=True),
        # Source
        sa.Column("source", sa.String(50), nullable=False),  # storybook, figma, manual
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_config", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        # Sync status
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String(20), server_default="'never'", nullable=False),
        sa.Column("sync_error", sa.Text(), nullable=True),
        # Statistics
        sa.Column("component_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("token_count", sa.Integer(), server_default="0", nullable=False),
        # Metadata
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        # Constraints
        sa.UniqueConstraint("project_id", "slug", name="uq_component_libraries_project_slug"),
    )

    # Create library_components table
    op.create_table(
        "library_components",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "library_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("component_libraries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identity
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        # Classification
        sa.Column("category", sa.String(50), nullable=False),  # atom, molecule, organism, etc.
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        # Hierarchy
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("child_ids", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        # Code reference
        sa.Column("code_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=True),
        # Storybook integration
        sa.Column("storybook_id", sa.String(255), nullable=True),
        sa.Column("storybook_url", sa.Text(), nullable=True),
        # Figma integration
        sa.Column("figma_node_id", sa.String(100), nullable=True),
        sa.Column("figma_url", sa.Text(), nullable=True),
        # Props/API
        sa.Column("props", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("slots", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("events", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("variants", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        # Visual
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column("preview_url", sa.Text(), nullable=True),
        # Usage
        sa.Column("usage_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("usage_locations", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("token_refs", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        # Status
        sa.Column("status", sa.String(20), server_default="'stable'", nullable=False),
        sa.Column("deprecation_message", sa.Text(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # Foreign keys for library_components
    op.create_foreign_key(
        "fk_library_components_parent",
        "library_components",
        "library_components",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_library_components_code",
        "library_components",
        "code_entities",
        ["code_entity_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Indexes for component_libraries
    op.create_index("ix_component_libraries_project_id", "component_libraries", ["project_id"])
    op.create_index("ix_component_libraries_source", "component_libraries", ["source"])
    op.create_index("ix_component_libraries_sync_status", "component_libraries", ["sync_status"])

    # Indexes for library_components
    op.create_index("ix_library_components_library_id", "library_components", ["library_id"])
    op.create_index("ix_library_components_project_id", "library_components", ["project_id"])
    op.create_index("ix_library_components_category", "library_components", ["category"])
    op.create_index("ix_library_components_parent_id", "library_components", ["parent_id"])
    op.create_index("ix_library_components_status", "library_components", ["status"])
    op.create_index("ix_library_components_storybook_id", "library_components", ["storybook_id"])
    op.create_index("ix_library_components_figma_node_id", "library_components", ["figma_node_id"])


def downgrade() -> None:
    """Drop component_libraries and library_components tables."""
    # Drop library_components first (has FK to component_libraries)
    op.drop_index("ix_library_components_figma_node_id", table_name="library_components")
    op.drop_index("ix_library_components_storybook_id", table_name="library_components")
    op.drop_index("ix_library_components_status", table_name="library_components")
    op.drop_index("ix_library_components_parent_id", table_name="library_components")
    op.drop_index("ix_library_components_category", table_name="library_components")
    op.drop_index("ix_library_components_project_id", table_name="library_components")
    op.drop_index("ix_library_components_library_id", table_name="library_components")
    op.drop_constraint("fk_library_components_code", "library_components", type_="foreignkey")
    op.drop_constraint("fk_library_components_parent", "library_components", type_="foreignkey")
    op.drop_table("library_components")

    # Drop component_libraries
    op.drop_index("ix_component_libraries_sync_status", table_name="component_libraries")
    op.drop_index("ix_component_libraries_source", table_name="component_libraries")
    op.drop_index("ix_component_libraries_project_id", table_name="component_libraries")
    op.drop_table("component_libraries")
