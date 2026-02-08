"""Add doc_entities table for documentation indexing.

Creates hierarchical documentation entities: document → section → chunk
with code reference extraction and embeddings.

Revision ID: 033_add_doc_entities
Revises: 032_add_canonical_projections
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "033_add_doc_entities"
down_revision = "032_add_canonical_projections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create doc_entities table with hierarchical structure."""
    op.create_table(
        "doc_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Hierarchy
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(50), nullable=False),  # document, section, chunk
        sa.Column("depth", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "path",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Source
        sa.Column("source_path", sa.Text(), nullable=False),  # File path
        sa.Column("source_url", sa.Text(), nullable=True),  # Optional URL
        sa.Column("source_repo", sa.String(255), nullable=True),  # Repository
        # Content
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("heading", sa.String(500), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(50), nullable=True),  # heading, paragraph, code_block, etc.
        # Position in document
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column("heading_level", sa.Integer(), nullable=True),
        # Code references extracted from content
        sa.Column(
            "code_refs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Linked items
        sa.Column(
            "linked_item_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Embeddings
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=True),
        sa.Column("embedding_updated_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Self-referential foreign key for parent
    op.create_foreign_key(
        "fk_doc_entities_parent",
        "doc_entities",
        "doc_entities",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Create indexes
    op.create_index("ix_doc_entities_project_id", "doc_entities", ["project_id"])
    op.create_index("ix_doc_entities_parent_id", "doc_entities", ["parent_id"])
    op.create_index("ix_doc_entities_entity_type", "doc_entities", ["entity_type"])
    op.create_index("ix_doc_entities_source_path", "doc_entities", ["source_path"])
    op.create_index("ix_doc_entities_depth", "doc_entities", ["depth"])
    # GIN index for code_refs array
    op.create_index("ix_doc_entities_code_refs", "doc_entities", ["code_refs"], postgresql_using="gin")
    # Composite for project+type queries
    op.create_index("ix_doc_entities_project_type", "doc_entities", ["project_id", "entity_type"])


def downgrade() -> None:
    """Drop doc_entities table."""
    op.drop_index("ix_doc_entities_project_type", table_name="doc_entities")
    op.drop_index("ix_doc_entities_code_refs", table_name="doc_entities")
    op.drop_index("ix_doc_entities_depth", table_name="doc_entities")
    op.drop_index("ix_doc_entities_source_path", table_name="doc_entities")
    op.drop_index("ix_doc_entities_entity_type", table_name="doc_entities")
    op.drop_index("ix_doc_entities_parent_id", table_name="doc_entities")
    op.drop_index("ix_doc_entities_project_id", table_name="doc_entities")
    op.drop_constraint("fk_doc_entities_parent", "doc_entities", type_="foreignkey")
    op.drop_table("doc_entities")
