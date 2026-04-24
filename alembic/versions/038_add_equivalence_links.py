"""Add equivalence_links table for cross-perspective equivalence detection.

Stores detected and manual equivalences between items across perspectives
with confidence scoring and provenance tracking.

Revision ID: 038_add_equivalence_links
Revises: 037_add_blockchain_ml_tables
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "038_add_equivalence_links"
down_revision = "037_add_blockchain_ml_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create equivalence_links table for cross-perspective equivalences."""
    op.create_table(
        "equivalence_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Links to items
        sa.Column(
            "item_id_1",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id_2",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Perspectives of linked items
        sa.Column("perspective_1", sa.String(50), nullable=False),
        sa.Column("perspective_2", sa.String(50), nullable=False),
        # Equivalence type
        sa.Column(
            "equivalence_type",
            sa.String(50),
            nullable=False,
            server_default="'same_as'",
        ),  # same_as, represents, manifests_as
        # Confidence and provenance
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column(
            "provenance",
            sa.String(50),
            nullable=False,
            server_default="'manual'",
        ),  # manual, naming, semantic, api_contract, annotation, canonical
        # Detection signals (for debugging/explanation)
        sa.Column(
            "detection_signals",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # User confirmation
        sa.Column("status", sa.String(20), server_default="'auto'", nullable=False),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        # Notes
        sa.Column("notes", sa.Text(), nullable=True),
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
        # Unique constraint: bidirectional, so normalize by ordering IDs
        sa.UniqueConstraint(
            "project_id",
            "item_id_1",
            "item_id_2",
            name="uq_equivalence_links_items",
        ),
    )

    # Create indexes for efficient lookups
    op.create_index("ix_equivalence_links_project_id", "equivalence_links", ["project_id"])
    op.create_index("ix_equivalence_links_item_id_1", "equivalence_links", ["item_id_1"])
    op.create_index("ix_equivalence_links_item_id_2", "equivalence_links", ["item_id_2"])
    op.create_index("ix_equivalence_links_perspective_1", "equivalence_links", ["perspective_1"])
    op.create_index("ix_equivalence_links_perspective_2", "equivalence_links", ["perspective_2"])
    op.create_index(
        "ix_equivalence_links_equivalence_type",
        "equivalence_links",
        ["equivalence_type"],
    )
    op.create_index("ix_equivalence_links_provenance", "equivalence_links", ["provenance"])
    op.create_index("ix_equivalence_links_status", "equivalence_links", ["status"])
    op.create_index("ix_equivalence_links_confidence", "equivalence_links", ["confidence"])
    # Composite index for finding all equivalences of an item
    op.create_index(
        "ix_equivalence_links_item_1_confidence",
        "equivalence_links",
        ["item_id_1", "confidence"],
    )
    op.create_index(
        "ix_equivalence_links_item_2_confidence",
        "equivalence_links",
        ["item_id_2", "confidence"],
    )


def downgrade() -> None:
    """Drop equivalence_links table."""
    op.drop_index("ix_equivalence_links_item_2_confidence", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_item_1_confidence", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_confidence", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_status", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_provenance", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_equivalence_type", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_perspective_2", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_perspective_1", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_item_id_2", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_item_id_1", table_name="equivalence_links")
    op.drop_index("ix_equivalence_links_project_id", table_name="equivalence_links")
    op.drop_table("equivalence_links")
