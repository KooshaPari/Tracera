"""Add canonical_projections junction table.

Links canonical concepts to items across perspectives with
confidence scores and provenance tracking.

Revision ID: 032_add_canonical_projections
Revises: 031_add_canonical_concepts
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "032_add_canonical_projections"
down_revision = "031_add_canonical_concepts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create canonical_projections junction table."""
    op.create_table(
        "canonical_projections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Links
        sa.Column(
            "canonical_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("canonical_concepts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Perspective context
        sa.Column("perspective", sa.String(50), nullable=False),
        sa.Column("role", sa.String(50), nullable=True),  # primary, related, derived
        # Confidence and provenance
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("provenance", sa.String(50), server_default="'manual'", nullable=False),
        # User confirmation
        sa.Column("status", sa.String(20), server_default="'auto'", nullable=False),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
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
        # Unique constraint: one projection per concept-item pair
        sa.UniqueConstraint("canonical_id", "item_id", name="uq_canonical_projections_concept_item"),
    )

    # Create indexes for efficient lookups
    op.create_index("ix_canonical_projections_project_id", "canonical_projections", ["project_id"])
    op.create_index("ix_canonical_projections_canonical_id", "canonical_projections", ["canonical_id"])
    op.create_index("ix_canonical_projections_item_id", "canonical_projections", ["item_id"])
    op.create_index("ix_canonical_projections_perspective", "canonical_projections", ["perspective"])
    op.create_index("ix_canonical_projections_provenance", "canonical_projections", ["provenance"])
    op.create_index("ix_canonical_projections_status", "canonical_projections", ["status"])
    # Composite index for perspective-based queries
    op.create_index(
        "ix_canonical_projections_project_perspective",
        "canonical_projections",
        ["project_id", "perspective"],
    )


def downgrade() -> None:
    """Drop canonical_projections table."""
    op.drop_index("ix_canonical_projections_project_perspective", table_name="canonical_projections")
    op.drop_index("ix_canonical_projections_status", table_name="canonical_projections")
    op.drop_index("ix_canonical_projections_provenance", table_name="canonical_projections")
    op.drop_index("ix_canonical_projections_perspective", table_name="canonical_projections")
    op.drop_index("ix_canonical_projections_item_id", table_name="canonical_projections")
    op.drop_index("ix_canonical_projections_canonical_id", table_name="canonical_projections")
    op.drop_index("ix_canonical_projections_project_id", table_name="canonical_projections")
    op.drop_table("canonical_projections")
