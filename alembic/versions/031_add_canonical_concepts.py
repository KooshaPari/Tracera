"""Add canonical_concepts table for multi-dimensional traceability.

Creates canonical_concepts table with pgvector embeddings for semantic
similarity search and GIN indexes for tags/metadata.

Revision ID: 031_add_canonical_concepts
Revises: 030_enhance_item_specs_blockchain
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "031_add_canonical_concepts"
down_revision = "030_enhance_item_specs_blockchain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create canonical_concepts table with pgvector support."""
    # Ensure pgvector extension is enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create canonical_concepts table
    op.create_table(
        "canonical_concepts",
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
        # Domain classification
        sa.Column("domain", sa.String(100), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Embeddings for semantic similarity (1536 dimensions for OpenAI/Voyage)
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=True),
        sa.Column("embedding_updated_at", sa.DateTime(timezone=True), nullable=True),
        # Statistics
        sa.Column("projection_count", sa.Integer(), server_default="0", nullable=False),
        # Related concepts (graph structure)
        sa.Column(
            "related_concept_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("parent_concept_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "child_concept_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Confidence and provenance
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("source", sa.String(50), server_default="'manual'", nullable=False),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        # Constraints
        sa.UniqueConstraint("project_id", "slug", name="uq_canonical_concepts_project_slug"),
    )

    # Create indexes
    op.create_index(
        "ix_canonical_concepts_project_id",
        "canonical_concepts",
        ["project_id"],
    )
    op.create_index(
        "ix_canonical_concepts_domain",
        "canonical_concepts",
        ["domain"],
    )
    op.create_index(
        "ix_canonical_concepts_category",
        "canonical_concepts",
        ["category"],
    )
    op.create_index(
        "ix_canonical_concepts_source",
        "canonical_concepts",
        ["source"],
    )
    # GIN index for tags array search
    op.create_index(
        "ix_canonical_concepts_tags",
        "canonical_concepts",
        ["tags"],
        postgresql_using="gin",
    )
    # Self-referential foreign key for parent concept
    op.create_foreign_key(
        "fk_canonical_concepts_parent",
        "canonical_concepts",
        "canonical_concepts",
        ["parent_concept_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Drop canonical_concepts table."""
    op.drop_constraint(
        "fk_canonical_concepts_parent",
        "canonical_concepts",
        type_="foreignkey",
    )
    op.drop_index("ix_canonical_concepts_tags", table_name="canonical_concepts")
    op.drop_index("ix_canonical_concepts_source", table_name="canonical_concepts")
    op.drop_index("ix_canonical_concepts_category", table_name="canonical_concepts")
    op.drop_index("ix_canonical_concepts_domain", table_name="canonical_concepts")
    op.drop_index("ix_canonical_concepts_project_id", table_name="canonical_concepts")
    op.drop_table("canonical_concepts")
