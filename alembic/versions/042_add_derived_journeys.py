"""Add derived_journeys table for automatic user flow and journey detection.

Stores detected user journeys, data flows, and call chains with
item sequences and confidence scores.

Revision ID: 042_add_derived_journeys
Revises: 041_add_figma_sync_state
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "042_add_derived_journeys"
down_revision = "041_add_figma_sync_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create derived_journeys table for journey detection."""
    op.create_table(
        "derived_journeys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identity
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # Journey type
        sa.Column(
            "journey_type",
            sa.String(50),
            nullable=False,
        ),  # user_flow, data_flow, call_chain, process_flow
        # Perspectives involved
        sa.Column(
            "perspectives",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Sequence of items
        sa.Column(
            "item_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),  # Ordered array of item IDs
        sa.Column("item_count", sa.Integer(), server_default="0", nullable=False),
        # Sequence of links between items
        sa.Column(
            "link_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Entry and exit points
        sa.Column(
            "entry_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "exit_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Detection details
        sa.Column(
            "detection_method",
            sa.String(50),
            nullable=False,
        ),  # graph_traversal, ast_analysis, annotation, manual
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("score", sa.Float(), nullable=True),  # Custom ranking score
        # Statistics
        sa.Column("occurrence_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_occurred_at", sa.DateTime(timezone=True), nullable=True),
        # Metadata and alternatives
        sa.Column(
            "variants",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),  # Alternative paths
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        # User confirmation
        sa.Column("status", sa.String(20), server_default="'auto'", nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
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
        # Unique constraint per project/slug
        sa.UniqueConstraint("project_id", "slug", name="uq_derived_journeys_project_slug"),
    )

    # Create indexes
    op.create_index("ix_derived_journeys_project_id", "derived_journeys", ["project_id"])
    op.create_index("ix_derived_journeys_journey_type", "derived_journeys", ["journey_type"])
    op.create_index("ix_derived_journeys_entry_item_id", "derived_journeys", ["entry_item_id"])
    op.create_index("ix_derived_journeys_exit_item_id", "derived_journeys", ["exit_item_id"])
    op.create_index(
        "ix_derived_journeys_detection_method",
        "derived_journeys",
        ["detection_method"],
    )
    op.create_index("ix_derived_journeys_confidence", "derived_journeys", ["confidence"])
    op.create_index("ix_derived_journeys_status", "derived_journeys", ["status"])
    # GIN index for array searches
    op.create_index(
        "ix_derived_journeys_item_ids",
        "derived_journeys",
        ["item_ids"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_derived_journeys_perspectives",
        "derived_journeys",
        ["perspectives"],
        postgresql_using="gin",
    )
    # Composite indexes
    op.create_index(
        "ix_derived_journeys_project_type",
        "derived_journeys",
        ["project_id", "journey_type"],
    )
    op.create_index(
        "ix_derived_journeys_project_status",
        "derived_journeys",
        ["project_id", "status"],
    )


def downgrade() -> None:
    """Drop derived_journeys table."""
    op.drop_index("ix_derived_journeys_project_status", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_project_type", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_perspectives", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_item_ids", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_status", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_confidence", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_detection_method", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_exit_item_id", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_entry_item_id", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_journey_type", table_name="derived_journeys")
    op.drop_index("ix_derived_journeys_project_id", table_name="derived_journeys")
    op.drop_table("derived_journeys")
