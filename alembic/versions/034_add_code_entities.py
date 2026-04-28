"""Add code_entities table for code indexing.

Creates code entities with AST references, symbol types, and
cross-file dependency tracking for multi-language support.

Revision ID: 034_add_code_entities
Revises: 033_add_doc_entities
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "034_add_code_entities"
down_revision = "033_add_doc_entities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create code_entities table with AST references."""
    op.create_table(
        "code_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Symbol identity
        sa.Column("symbol_name", sa.String(500), nullable=False),
        sa.Column("qualified_name", sa.Text(), nullable=True),  # Fully qualified name
        sa.Column("symbol_type", sa.String(50), nullable=False),  # function, class, method, variable, etc.
        # File location
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("repository", sa.String(255), nullable=True),
        sa.Column("branch", sa.String(255), nullable=True),
        sa.Column("commit_sha", sa.String(40), nullable=True),
        # AST position
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("start_column", sa.Integer(), nullable=True),
        sa.Column("end_column", sa.Integer(), nullable=True),
        # Language and framework
        sa.Column("language", sa.String(50), nullable=False),
        sa.Column("framework", sa.String(100), nullable=True),
        # Hierarchy
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scope", sa.String(50), nullable=True),  # module, class, function
        sa.Column(
            "path",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Dependencies
        sa.Column(
            "imports",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "exports",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "calls",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "called_by",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        # Annotations and comments
        sa.Column(
            "annotations",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("docstring", sa.Text(), nullable=True),
        # Linked items
        sa.Column("linked_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("canonical_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Embeddings
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=True),
        # Metadata
        sa.Column("signature", sa.Text(), nullable=True),  # Function/method signature
        sa.Column("complexity", sa.Integer(), nullable=True),  # Cyclomatic complexity
        sa.Column("line_count", sa.Integer(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Self-referential foreign key
    op.create_foreign_key(
        "fk_code_entities_parent",
        "code_entities",
        "code_entities",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_code_entities_item",
        "code_entities",
        "items",
        ["linked_item_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_code_entities_canonical",
        "code_entities",
        "canonical_concepts",
        ["canonical_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create indexes
    op.create_index("ix_code_entities_project_id", "code_entities", ["project_id"])
    op.create_index("ix_code_entities_symbol_name", "code_entities", ["symbol_name"])
    op.create_index("ix_code_entities_symbol_type", "code_entities", ["symbol_type"])
    op.create_index("ix_code_entities_file_path", "code_entities", ["file_path"])
    op.create_index("ix_code_entities_language", "code_entities", ["language"])
    op.create_index("ix_code_entities_parent_id", "code_entities", ["parent_id"])
    op.create_index("ix_code_entities_linked_item_id", "code_entities", ["linked_item_id"])
    op.create_index("ix_code_entities_canonical_id", "code_entities", ["canonical_id"])
    # GIN indexes for array searches
    op.create_index("ix_code_entities_imports", "code_entities", ["imports"], postgresql_using="gin")
    op.create_index("ix_code_entities_calls", "code_entities", ["calls"], postgresql_using="gin")
    # Composite index
    op.create_index("ix_code_entities_project_file", "code_entities", ["project_id", "file_path"])


def downgrade() -> None:
    """Drop code_entities table."""
    op.drop_index("ix_code_entities_project_file", table_name="code_entities")
    op.drop_index("ix_code_entities_calls", table_name="code_entities")
    op.drop_index("ix_code_entities_imports", table_name="code_entities")
    op.drop_index("ix_code_entities_canonical_id", table_name="code_entities")
    op.drop_index("ix_code_entities_linked_item_id", table_name="code_entities")
    op.drop_index("ix_code_entities_parent_id", table_name="code_entities")
    op.drop_index("ix_code_entities_language", table_name="code_entities")
    op.drop_index("ix_code_entities_file_path", table_name="code_entities")
    op.drop_index("ix_code_entities_symbol_type", table_name="code_entities")
    op.drop_index("ix_code_entities_symbol_name", table_name="code_entities")
    op.drop_index("ix_code_entities_project_id", table_name="code_entities")
    op.drop_constraint("fk_code_entities_canonical", "code_entities", type_="foreignkey")
    op.drop_constraint("fk_code_entities_item", "code_entities", type_="foreignkey")
    op.drop_constraint("fk_code_entities_parent", "code_entities", type_="foreignkey")
    op.drop_table("code_entities")
