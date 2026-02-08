"""Add blockchain and ML tables for analytics.

Creates tables for:
- version_blocks: Blockchain-style version history
- version_chains: Fast chain lookup index
- baselines: Merkle tree snapshots
- baseline_items: Items in baselines
- merkle_proofs: Cached proof data
- spec_embeddings: Sentence embeddings for semantic similarity

Revision ID: 037_add_blockchain_ml_tables
Revises: 036_add_component_libraries
Create Date: 2026-01-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "037_add_blockchain_ml_tables"
down_revision = "036_add_component_libraries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create blockchain and ML tables."""
    # ==========================================================================
    # Version Blocks Table (Blockchain-style version history)
    # ==========================================================================
    op.create_table(
        "version_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Blockchain linking
        sa.Column("block_id", sa.String(64), unique=True, nullable=False),
        sa.Column("previous_block_id", sa.String(64), nullable=True),
        # Spec reference
        sa.Column("spec_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Block content
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("author_id", sa.String(255), nullable=True),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column("change_summary", sa.Text, nullable=True),
        # Cryptographic fields
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("merkle_root", sa.String(64), nullable=True),
        sa.Column("digital_signature", sa.String(512), nullable=True),
        sa.Column("nonce", sa.Integer, nullable=True),
        # Metadata and timestamps
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
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
        # Constraints
        sa.ForeignKeyConstraint(
            ["previous_block_id"],
            ["version_blocks.block_id"],
            name="fk_version_blocks_previous",
        ),
        sa.UniqueConstraint("spec_id", "spec_type", "version_number", name="uq_spec_version"),
    )
    op.create_index("ix_version_blocks_block_id", "version_blocks", ["block_id"])
    op.create_index("ix_version_blocks_spec", "version_blocks", ["spec_id", "spec_type"])
    op.create_index("ix_version_blocks_project", "version_blocks", ["project_id"])
    op.create_index("ix_version_blocks_previous", "version_blocks", ["previous_block_id"])
    op.create_index("ix_version_blocks_timestamp", "version_blocks", ["timestamp"])

    # ==========================================================================
    # Version Chains Table (Fast chain lookup index)
    # ==========================================================================
    op.create_table(
        "version_chains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spec_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Chain state
        sa.Column("chain_head_id", sa.String(64), nullable=False),
        sa.Column("chain_length", sa.Integer, nullable=False, server_default="1"),
        sa.Column("genesis_block_id", sa.String(64), nullable=False),
        # Integrity
        sa.Column("is_valid", sa.Boolean, server_default="true"),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("broken_links", postgresql.JSONB, server_default="[]"),
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
        # Constraints
        sa.ForeignKeyConstraint(
            ["chain_head_id"],
            ["version_blocks.block_id"],
            name="fk_version_chains_head",
        ),
        sa.ForeignKeyConstraint(
            ["genesis_block_id"],
            ["version_blocks.block_id"],
            name="fk_version_chains_genesis",
        ),
        sa.UniqueConstraint("spec_id", "spec_type", name="uq_version_chain_spec"),
    )
    op.create_index("ix_version_chains_project", "version_chains", ["project_id"])

    # ==========================================================================
    # Baselines Table (Merkle tree snapshots)
    # ==========================================================================
    op.create_table(
        "baselines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("baseline_id", sa.String(64), unique=True, nullable=False),
        # Scope
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=True),  # null = all types
        # Merkle tree
        sa.Column("merkle_root", sa.String(64), nullable=False),
        sa.Column("merkle_tree_json", postgresql.JSONB, nullable=True),
        sa.Column("items_count", sa.Integer, nullable=False),
        # Metadata
        sa.Column("baseline_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        # Audit
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
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
    op.create_index("ix_baselines_project", "baselines", ["project_id"])
    op.create_index("ix_baselines_root", "baselines", ["merkle_root"])
    op.create_index("ix_baselines_type", "baselines", ["baseline_type"])

    # ==========================================================================
    # Baseline Items Table (Items in baselines)
    # ==========================================================================
    op.create_table(
        "baseline_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "baseline_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        # Item reference
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_type", sa.String(50), nullable=False),
        # Merkle data
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("leaf_hash", sa.String(64), nullable=False),
        sa.Column("leaf_index", sa.Integer, nullable=False),
        # Snapshot data
        sa.Column("version_at_baseline", sa.Integer, nullable=True),
        sa.Column("content_snapshot", postgresql.JSONB, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.ForeignKeyConstraint(
            ["baseline_id"],
            ["baselines.id"],
            name="fk_baseline_items_baseline",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("baseline_id", "item_id", name="uq_baseline_item"),
    )
    op.create_index("ix_baseline_items_baseline", "baseline_items", ["baseline_id"])
    op.create_index("ix_baseline_items_item", "baseline_items", ["item_id", "item_type"])

    # ==========================================================================
    # Merkle Proofs Table (Cached proofs)
    # ==========================================================================
    op.create_table(
        "merkle_proofs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "baseline_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Proof data
        sa.Column("leaf_hash", sa.String(64), nullable=False),
        sa.Column("proof_path", postgresql.JSONB, nullable=False),
        sa.Column("root_hash", sa.String(64), nullable=False),
        # Verification cache
        sa.Column("verified", sa.Boolean, nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamps
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.ForeignKeyConstraint(
            ["baseline_id"],
            ["baselines.id"],
            name="fk_merkle_proofs_baseline",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("baseline_id", "item_id", name="uq_merkle_proof"),
    )
    op.create_index("ix_merkle_proofs_baseline", "merkle_proofs", ["baseline_id"])
    op.create_index("ix_merkle_proofs_item", "merkle_proofs", ["item_id"])

    # ==========================================================================
    # Spec Embeddings Table (Semantic similarity)
    # ==========================================================================
    op.create_table(
        "spec_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spec_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Embedding data
        sa.Column("embedding", sa.LargeBinary, nullable=False),
        sa.Column("embedding_dimension", sa.Integer, nullable=False),
        sa.Column("embedding_model", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=True),
        # Cache validation
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("source_text_length", sa.Integer, nullable=True),
        # Metadata and timestamps
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
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
        # Constraints
        sa.UniqueConstraint("spec_id", "spec_type", "embedding_model", name="uq_spec_embedding"),
    )
    op.create_index("ix_spec_embeddings_spec", "spec_embeddings", ["spec_id", "spec_type"])
    op.create_index("ix_spec_embeddings_project", "spec_embeddings", ["project_id"])
    op.create_index("ix_spec_embeddings_content_hash", "spec_embeddings", ["content_hash"])


def downgrade() -> None:
    """Drop blockchain and ML tables."""
    # Drop in reverse order of creation to handle foreign keys
    op.drop_table("spec_embeddings")
    op.drop_table("merkle_proofs")
    op.drop_table("baseline_items")
    op.drop_table("baselines")
    op.drop_table("version_chains")
    op.drop_table("version_blocks")
