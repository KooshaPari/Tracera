"""Add figma_sync_state table for Figma integration tracking.

Tracks sync status between Figma designs and code/UI items with
versioning and conflict detection.

Revision ID: 041_add_figma_sync_state
Revises: 040_add_design_token_refs
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "041_add_figma_sync_state"
down_revision = "040_add_design_token_refs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create figma_sync_state table for design-code synchronization."""
    op.create_table(
        "figma_sync_state",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # References - can link to items or components
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "component_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("library_components.id", ondelete="CASCADE"),
            nullable=True,
        ),
        # Figma identifiers
        sa.Column("file_key", sa.String(100), nullable=False),
        sa.Column("page_name", sa.String(255), nullable=True),
        sa.Column("node_id", sa.String(100), nullable=False),
        sa.Column("node_name", sa.String(255), nullable=True),
        # Figma metadata
        sa.Column("figma_url", sa.Text(), nullable=True),
        sa.Column("node_type", sa.String(50), nullable=True),  # COMPONENT, FRAME, etc.
        # Sync status
        sa.Column(
            "sync_status",
            sa.String(20),
            nullable=False,
            server_default="'unlinked'",
        ),  # synced, outdated, unlinked, conflict
        sa.Column("sync_direction", sa.String(20), nullable=True),  # auto, manual, bidirectional
        # Timestamps
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("figma_modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("code_modified_at", sa.DateTime(timezone=True), nullable=True),
        # Versioning
        sa.Column("figma_version", sa.String(50), nullable=True),
        sa.Column("code_version", sa.String(50), nullable=True),
        # Sync details
        sa.Column(
            "sync_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        # Conflict tracking
        sa.Column("has_conflict", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("conflict_details", sa.Text(), nullable=True),
        # Code Connect integration (Figma 2024+)
        sa.Column(
            "code_connect_enabled",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("code_connect_url", sa.Text(), nullable=True),
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
        # Unique constraint per file/node combination (per item or component)
        sa.UniqueConstraint(
            "project_id",
            "file_key",
            "node_id",
            "item_id",
            name="uq_figma_sync_item",
        ),
        sa.UniqueConstraint(
            "project_id",
            "file_key",
            "node_id",
            "component_id",
            name="uq_figma_sync_component",
        ),
    )

    # Create indexes
    op.create_index("ix_figma_sync_state_project_id", "figma_sync_state", ["project_id"])
    op.create_index("ix_figma_sync_state_item_id", "figma_sync_state", ["item_id"])
    op.create_index("ix_figma_sync_state_component_id", "figma_sync_state", ["component_id"])
    op.create_index("ix_figma_sync_state_file_key", "figma_sync_state", ["file_key"])
    op.create_index("ix_figma_sync_state_node_id", "figma_sync_state", ["node_id"])
    op.create_index("ix_figma_sync_state_sync_status", "figma_sync_state", ["sync_status"])
    op.create_index("ix_figma_sync_state_has_conflict", "figma_sync_state", ["has_conflict"])
    op.create_index("ix_figma_sync_state_last_synced", "figma_sync_state", ["last_synced_at"])
    # Composite indexes
    op.create_index(
        "ix_figma_sync_state_project_status",
        "figma_sync_state",
        ["project_id", "sync_status"],
    )
    op.create_index(
        "ix_figma_sync_state_file_page",
        "figma_sync_state",
        ["file_key", "page_name"],
    )


def downgrade() -> None:
    """Drop figma_sync_state table."""
    op.drop_index("ix_figma_sync_state_file_page", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_project_status", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_last_synced", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_has_conflict", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_sync_status", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_node_id", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_file_key", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_component_id", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_item_id", table_name="figma_sync_state")
    op.drop_index("ix_figma_sync_state_project_id", table_name="figma_sync_state")
    op.drop_table("figma_sync_state")
