"""Blockchain-style models for TraceRTM.

Provides:
- VersionBlock: Blockchain-style version history records
- VersionChainIndex: Fast lookup index for version chains
- Baseline: Merkle tree snapshots for verification
- BaselineItem: Items included in baselines
- MerkleProofCache: Cached Merkle proofs
- SpecEmbedding: Sentence embeddings for semantic similarity
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType

# =============================================================================
# Version Chain Models (Blockchain-style audit trail)
# =============================================================================


class VersionBlock(Base, TimestampMixin):
    """Blockchain-style version record with cryptographic linking.

    Each modification to a spec creates a new block that references
    the previous block via its hash, creating an immutable audit trail.
    """

    __tablename__ = "version_blocks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Blockchain linking
    block_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash of block
    previous_block_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("version_blocks.block_id"),
        nullable=True,
    )

    # Spec reference
    spec_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    spec_type: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Block content
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    author_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'create', 'update', 'delete', 'restore'
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cryptographic fields
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # Hash of spec content
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)  # For baseline linking
    digital_signature: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Optional signing
    nonce: Mapped[int | None] = mapped_column(Integer, nullable=True)  # For proof-of-work if needed

    # Metadata
    extra_data: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict)

    # Self-referential relationship
    previous_block: Mapped["VersionBlock | None"] = relationship(
        "VersionBlock",
        remote_side=[block_id],
        foreign_keys=[previous_block_id],
    )

    __table_args__ = (UniqueConstraint("spec_id", "spec_type", "version_number", name="uq_spec_version"),)


class VersionChainIndex(Base, TimestampMixin):
    """Fast lookup index for version chains.

    Maintains the head pointer and chain metadata for quick access
    without traversing the entire chain.
    """

    __tablename__ = "version_chains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    spec_id: Mapped[str] = mapped_column(String(255), nullable=False)
    spec_type: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Chain state
    chain_head_id: Mapped[str] = mapped_column(String(64), ForeignKey("version_blocks.block_id"), nullable=False)
    chain_length: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    genesis_block_id: Mapped[str] = mapped_column(String(64), ForeignKey("version_blocks.block_id"), nullable=False)

    # Integrity
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    broken_links: Mapped[list[str]] = mapped_column(JSONType, default=list)

    # Relationships
    chain_head: Mapped["VersionBlock"] = relationship("VersionBlock", foreign_keys=[chain_head_id])
    genesis_block: Mapped["VersionBlock"] = relationship("VersionBlock", foreign_keys=[genesis_block_id])

    __table_args__ = (UniqueConstraint("spec_id", "spec_type", name="uq_version_chain_spec"),)


# =============================================================================
# Baseline Models (Merkle tree snapshots)
# =============================================================================


class Baseline(Base, TimestampMixin):
    """Merkle tree snapshot for baseline verification.

    A baseline captures the state of specifications at a point in time,
    enabling verification that items haven't changed since the baseline.
    """

    __tablename__ = "baselines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # Human-readable or generated ID

    # Scope
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    spec_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # null = all types

    # Merkle tree
    merkle_root: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # Root hash
    merkle_tree_json: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)  # Serialized tree
    items_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata
    baseline_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'snapshot', 'release', 'freeze', 'audit'
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONType, default=list)

    # Audit
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    extra_data: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict)

    # Relationships
    items: Mapped[list["BaselineItem"]] = relationship(
        "BaselineItem",
        back_populates="baseline",
        cascade="all, delete-orphan",
    )
    proofs: Mapped[list["MerkleProofCache"]] = relationship(
        "MerkleProofCache",
        back_populates="baseline",
        cascade="all, delete-orphan",
    )


class BaselineItem(Base):
    """Item included in a baseline snapshot.

    Stores the content hash and leaf hash for each item at baseline time.
    """

    __tablename__ = "baseline_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("baselines.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Item reference
    item_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Merkle data
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    leaf_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # Hash(item_id + content_hash)
    leaf_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Snapshot data
    version_at_baseline: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_snapshot: Mapped[dict[str, object] | None] = mapped_column(JSONType, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    baseline: Mapped["Baseline"] = relationship("Baseline", back_populates="items")

    __table_args__ = (UniqueConstraint("baseline_id", "item_id", name="uq_baseline_item"),)


class MerkleProofCache(Base):
    """Cached Merkle proof for a baseline item.

    Proofs are pre-computed and cached to avoid expensive recomputation.
    """

    __tablename__ = "merkle_proofs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("baselines.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Proof data
    leaf_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    proof_path: Mapped[list[dict[str, str]]] = mapped_column(JSONType, nullable=False)  # Array of {hash, direction}
    root_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Verification cache
    verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cache management
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    baseline: Mapped["Baseline"] = relationship("Baseline", back_populates="proofs")

    __table_args__ = (UniqueConstraint("baseline_id", "item_id", name="uq_merkle_proof"),)


# =============================================================================
# Embedding Models (Semantic similarity)
# =============================================================================


class SpecEmbedding(Base, TimestampMixin):
    """Sentence embedding for semantic similarity analysis.

    Stores vector embeddings computed from spec content for finding
    similar specifications.
    """

    __tablename__ = "spec_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    spec_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    spec_type: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Embedding data
    embedding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Serialized numpy array
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 384 for all-MiniLM-L6-v2
    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )  # e.g., 'sentence-transformers/all-MiniLM-L6-v2'
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Cache validation
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # SHA-256 of source content
    source_text_length: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    extra_data: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict)

    __table_args__ = (UniqueConstraint("spec_id", "spec_type", "embedding_model", name="uq_spec_embedding"),)
