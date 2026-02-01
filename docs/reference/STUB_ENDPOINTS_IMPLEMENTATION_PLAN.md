# Stub Endpoints Implementation Plan

This document outlines the database models, migrations, and service methods required to fully implement the four remaining stub analytics endpoints.

---

## Overview

| Endpoint | Current Status | DB Tables Needed | Effort |
|----------|----------------|------------------|--------|
| `/{spec_type}/{spec_id}/analyze/similarity` | Stub (ML needed) | `spec_embeddings` | High |
| `/{spec_type}/{spec_id}/version-chain` | Stub (DB needed) | `version_blocks`, `version_chains` | Medium |
| `/{spec_type}/{spec_id}/merkle-proof` | Stub (baseline needed) | `baselines`, `baseline_items`, `merkle_proofs` | Medium |
| `/{spec_type}/{spec_id}/verify-baseline` | Stub (DB needed) | Uses baseline tables | Low |

---

## 1. Semantic Similarity Analysis

**Endpoint:** `POST /{spec_type}/{spec_id}/analyze/similarity`

### Purpose
Find specifications with semantically similar content using ML embeddings to identify potential duplicates, related items, or contradictions.

### Database Table: `spec_embeddings`

```sql
CREATE TABLE spec_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spec_id VARCHAR(255) NOT NULL,
    spec_type VARCHAR(50) NOT NULL CHECK (spec_type IN ('requirements', 'tests', 'epics', 'stories', 'tasks', 'defects')),
    project_id VARCHAR(255) NOT NULL,

    -- Embedding data
    embedding BYTEA NOT NULL,                    -- Serialized numpy array
    embedding_dimension INTEGER NOT NULL,         -- e.g., 384 for all-MiniLM-L6-v2
    embedding_model VARCHAR(100) NOT NULL,        -- e.g., 'sentence-transformers/all-MiniLM-L6-v2'
    model_version VARCHAR(50),                    -- For cache invalidation

    -- Cache validation
    content_hash VARCHAR(64) NOT NULL,            -- SHA-256 of source content
    source_text_length INTEGER,

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_spec_embedding UNIQUE (spec_id, spec_type, embedding_model)
);

CREATE INDEX ix_spec_embeddings_spec ON spec_embeddings (spec_id, spec_type);
CREATE INDEX ix_spec_embeddings_project ON spec_embeddings (project_id);
CREATE INDEX ix_spec_embeddings_content_hash ON spec_embeddings (content_hash);
```

### SQLAlchemy Model

```python
# src/tracertm/models/spec_embedding.py

from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from tracertm.models.base import Base
import uuid

class SpecEmbedding(Base):
    __tablename__ = "spec_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spec_id = Column(String(255), nullable=False, index=True)
    spec_type = Column(String(50), nullable=False)
    project_id = Column(String(255), nullable=False, index=True)

    # Embedding data
    embedding = Column(LargeBinary, nullable=False)
    embedding_dimension = Column(Integer, nullable=False)
    embedding_model = Column(String(100), nullable=False)
    model_version = Column(String(50))

    # Cache validation
    content_hash = Column(String(64), nullable=False, index=True)
    source_text_length = Column(Integer)

    # Metadata
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    __table_args__ = (
        UniqueConstraint('spec_id', 'spec_type', 'embedding_model', name='uq_spec_embedding'),
    )
```

### Service Methods

```python
# Add to SpecAnalyticsServiceV2

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None  # Lazy load

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for text."""
        return self.model.encode(text, convert_to_numpy=True)

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings."""
        from numpy.linalg import norm
        return np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))

    async def find_similar(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        project_id: str,
        threshold: float = 0.8,
        limit: int = 10
    ) -> list[SemanticSimilarity]:
        """Find semantically similar specs."""
        # 1. Get or compute source embedding
        # 2. Query all embeddings in project
        # 3. Compute similarities
        # 4. Filter by threshold and return top N
        pass
```

### Dependencies to Add

```toml
# pyproject.toml
[project.optional-dependencies]
ml = [
    "sentence-transformers>=2.2.0",
    "numpy>=1.24.0",
]
```

---

## 2. Version Chain Storage

**Endpoint:** `GET /{spec_type}/{spec_id}/version-chain`

### Purpose
Retrieve blockchain-style version history showing all modifications with cryptographic hash links for audit trails.

### Database Table: `version_blocks`

```sql
CREATE TABLE version_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Blockchain linking
    block_id VARCHAR(64) NOT NULL UNIQUE,         -- SHA-256 hash of block
    previous_block_id VARCHAR(64),                -- Link to previous block (null for genesis)

    -- Spec reference
    spec_id VARCHAR(255) NOT NULL,
    spec_type VARCHAR(50) NOT NULL,
    project_id VARCHAR(255) NOT NULL,

    -- Block content
    version_number INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    author_id VARCHAR(255),
    change_type VARCHAR(50) NOT NULL,             -- 'create', 'update', 'delete', 'restore'
    change_summary TEXT,

    -- Cryptographic fields
    content_hash VARCHAR(64) NOT NULL,            -- Hash of spec content at this version
    merkle_root VARCHAR(64),                      -- For baseline linking
    digital_signature VARCHAR(512),               -- Optional signing
    nonce INTEGER,                                -- For proof-of-work if needed

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_previous_block FOREIGN KEY (previous_block_id) REFERENCES version_blocks(block_id)
);

CREATE INDEX ix_version_blocks_spec ON version_blocks (spec_id, spec_type);
CREATE INDEX ix_version_blocks_project ON version_blocks (project_id);
CREATE INDEX ix_version_blocks_previous ON version_blocks (previous_block_id);
CREATE INDEX ix_version_blocks_timestamp ON version_blocks (timestamp DESC);
```

### Database Table: `version_chains` (Optional Index Table)

```sql
CREATE TABLE version_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spec_id VARCHAR(255) NOT NULL,
    spec_type VARCHAR(50) NOT NULL,
    project_id VARCHAR(255) NOT NULL,

    -- Chain state
    chain_head_id VARCHAR(64) NOT NULL,           -- Latest block_id
    chain_length INTEGER NOT NULL DEFAULT 1,
    genesis_block_id VARCHAR(64) NOT NULL,        -- First block_id

    -- Integrity
    is_valid BOOLEAN DEFAULT TRUE,
    last_verified_at TIMESTAMPTZ,
    broken_links JSONB DEFAULT '[]',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_version_chain_spec UNIQUE (spec_id, spec_type),
    CONSTRAINT fk_chain_head FOREIGN KEY (chain_head_id) REFERENCES version_blocks(block_id),
    CONSTRAINT fk_genesis_block FOREIGN KEY (genesis_block_id) REFERENCES version_blocks(block_id)
);

CREATE INDEX ix_version_chains_project ON version_chains (project_id);
```

### SQLAlchemy Models

```python
# src/tracertm/models/version_chain.py

class VersionBlock(Base):
    __tablename__ = "version_blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(String(64), unique=True, nullable=False, index=True)
    previous_block_id = Column(String(64), ForeignKey("version_blocks.block_id"))

    spec_id = Column(String(255), nullable=False)
    spec_type = Column(String(50), nullable=False)
    project_id = Column(String(255), nullable=False, index=True)

    version_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    author_id = Column(String(255))
    change_type = Column(String(50), nullable=False)
    change_summary = Column(Text)

    content_hash = Column(String(64), nullable=False)
    merkle_root = Column(String(64))
    digital_signature = Column(String(512))
    nonce = Column(Integer)

    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default="now()")

    # Relationships
    previous_block = relationship("VersionBlock", remote_side=[block_id])


class VersionChain(Base):
    __tablename__ = "version_chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spec_id = Column(String(255), nullable=False)
    spec_type = Column(String(50), nullable=False)
    project_id = Column(String(255), nullable=False, index=True)

    chain_head_id = Column(String(64), ForeignKey("version_blocks.block_id"), nullable=False)
    chain_length = Column(Integer, nullable=False, default=1)
    genesis_block_id = Column(String(64), ForeignKey("version_blocks.block_id"), nullable=False)

    is_valid = Column(Boolean, default=True)
    last_verified_at = Column(DateTime(timezone=True))
    broken_links = Column(JSON, default=[])

    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    __table_args__ = (
        UniqueConstraint('spec_id', 'spec_type', name='uq_version_chain_spec'),
    )
```

### Service Methods

```python
# Add to SpecAnalyticsServiceV2

async def record_version(
    self,
    db: AsyncSession,
    spec_id: str,
    spec_type: str,
    project_id: str,
    content: dict,
    author_id: str,
    change_type: str,
    change_summary: str
) -> VersionBlock:
    """Record a new version in the chain."""
    # 1. Get current chain head (if exists)
    # 2. Create new block with hash of previous
    # 3. Update chain head
    # 4. Return new block
    pass

async def get_version_chain(
    self,
    db: AsyncSession,
    spec_id: str,
    spec_type: str,
    limit: int = 50
) -> VersionChainResponse:
    """Retrieve version chain with integrity check."""
    # 1. Get chain metadata
    # 2. Traverse blocks from head
    # 3. Verify hash links
    # 4. Return chain with validity status
    pass

async def verify_chain_integrity(
    self,
    db: AsyncSession,
    spec_id: str,
    spec_type: str
) -> tuple[bool, list[str]]:
    """Verify all hash links in chain."""
    # 1. Load all blocks
    # 2. Recompute hashes
    # 3. Compare with stored hashes
    # 4. Return validity and broken links
    pass
```

---

## 3. Baseline & Merkle Proof Storage

**Endpoints:**
- `GET /{spec_type}/{spec_id}/merkle-proof`
- `POST /{spec_type}/{spec_id}/verify-baseline`

### Purpose
Create baselines (snapshots) of specifications and generate Merkle proofs for verification of item inclusion.

### Database Table: `baselines`

```sql
CREATE TABLE baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id VARCHAR(64) NOT NULL UNIQUE,      -- Human-readable or generated ID

    -- Scope
    project_id VARCHAR(255) NOT NULL,
    spec_type VARCHAR(50),                        -- null = all types

    -- Merkle tree
    merkle_root VARCHAR(64) NOT NULL,             -- Root hash
    merkle_tree_json JSONB,                       -- Serialized tree (optional)
    items_count INTEGER NOT NULL,

    -- Metadata
    baseline_type VARCHAR(50) NOT NULL,           -- 'snapshot', 'release', 'freeze', 'audit'
    name VARCHAR(255),
    description TEXT,
    tags JSONB DEFAULT '[]',

    -- Audit
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,                       -- Optional expiration

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX ix_baselines_project ON baselines (project_id);
CREATE INDEX ix_baselines_root ON baselines (merkle_root);
CREATE INDEX ix_baselines_type ON baselines (baseline_type);
```

### Database Table: `baseline_items`

```sql
CREATE TABLE baseline_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID NOT NULL REFERENCES baselines(id) ON DELETE CASCADE,

    -- Item reference
    item_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL,

    -- Merkle data
    content_hash VARCHAR(64) NOT NULL,
    leaf_hash VARCHAR(64) NOT NULL,               -- Hash(item_id + content_hash)
    leaf_index INTEGER NOT NULL,                  -- Position in tree

    -- Snapshot data
    version_at_baseline INTEGER,
    content_snapshot JSONB,                       -- Optional full content

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_baseline_item UNIQUE (baseline_id, item_id)
);

CREATE INDEX ix_baseline_items_baseline ON baseline_items (baseline_id);
CREATE INDEX ix_baseline_items_item ON baseline_items (item_id, item_type);
```

### Database Table: `merkle_proofs` (Cache)

```sql
CREATE TABLE merkle_proofs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID NOT NULL REFERENCES baselines(id) ON DELETE CASCADE,
    item_id VARCHAR(255) NOT NULL,

    -- Proof data
    leaf_hash VARCHAR(64) NOT NULL,
    proof_path JSONB NOT NULL,                    -- Array of {hash, direction}
    root_hash VARCHAR(64) NOT NULL,

    -- Verification cache
    verified BOOLEAN,
    verified_at TIMESTAMPTZ,

    -- Cache management
    computed_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_merkle_proof UNIQUE (baseline_id, item_id)
);

CREATE INDEX ix_merkle_proofs_baseline ON merkle_proofs (baseline_id);
CREATE INDEX ix_merkle_proofs_item ON merkle_proofs (item_id);
```

### SQLAlchemy Models

```python
# src/tracertm/models/baseline.py

class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id = Column(String(64), unique=True, nullable=False)

    project_id = Column(String(255), nullable=False, index=True)
    spec_type = Column(String(50))  # null = all types

    merkle_root = Column(String(64), nullable=False, index=True)
    merkle_tree_json = Column(JSON)
    items_count = Column(Integer, nullable=False)

    baseline_type = Column(String(50), nullable=False)
    name = Column(String(255))
    description = Column(Text)
    tags = Column(JSON, default=[])

    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default="now()")
    expires_at = Column(DateTime(timezone=True))

    metadata = Column(JSON, default={})

    # Relationships
    items = relationship("BaselineItem", back_populates="baseline", cascade="all, delete-orphan")
    proofs = relationship("MerkleProofCache", back_populates="baseline", cascade="all, delete-orphan")


class BaselineItem(Base):
    __tablename__ = "baseline_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id = Column(UUID(as_uuid=True), ForeignKey("baselines.id", ondelete="CASCADE"), nullable=False)

    item_id = Column(String(255), nullable=False)
    item_type = Column(String(50), nullable=False)

    content_hash = Column(String(64), nullable=False)
    leaf_hash = Column(String(64), nullable=False)
    leaf_index = Column(Integer, nullable=False)

    version_at_baseline = Column(Integer)
    content_snapshot = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default="now()")

    # Relationships
    baseline = relationship("Baseline", back_populates="items")

    __table_args__ = (
        UniqueConstraint('baseline_id', 'item_id', name='uq_baseline_item'),
    )


class MerkleProofCache(Base):
    __tablename__ = "merkle_proofs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id = Column(UUID(as_uuid=True), ForeignKey("baselines.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(255), nullable=False)

    leaf_hash = Column(String(64), nullable=False)
    proof_path = Column(JSON, nullable=False)
    root_hash = Column(String(64), nullable=False)

    verified = Column(Boolean)
    verified_at = Column(DateTime(timezone=True))

    computed_at = Column(DateTime(timezone=True), server_default="now()")

    # Relationships
    baseline = relationship("Baseline", back_populates="proofs")

    __table_args__ = (
        UniqueConstraint('baseline_id', 'item_id', name='uq_merkle_proof'),
    )
```

### Service Methods

```python
# Add to SpecAnalyticsServiceV2

async def create_baseline(
    self,
    db: AsyncSession,
    project_id: str,
    baseline_type: str,
    name: str,
    items: list[tuple[str, str, str]],  # (item_id, item_type, content_hash)
    created_by: str,
    description: str = None
) -> Baseline:
    """Create a new baseline with Merkle tree."""
    # 1. Build Merkle tree from items
    # 2. Store baseline record
    # 3. Store baseline items with leaf hashes
    # 4. Pre-compute and cache proofs
    pass

async def get_merkle_proof(
    self,
    db: AsyncSession,
    item_id: str,
    baseline_id: str
) -> MerkleProofResponse:
    """Get or compute Merkle proof for item."""
    # 1. Check cache
    # 2. If not cached, compute from tree
    # 3. Cache result
    # 4. Return proof
    pass

async def verify_against_baseline(
    self,
    db: AsyncSession,
    item_id: str,
    current_content_hash: str,
    baseline_root: str
) -> MerkleProofResponse:
    """Verify item against a baseline."""
    # 1. Find baseline by root
    # 2. Get proof for item
    # 3. Verify proof
    # 4. Compare content hashes
    # 5. Return result
    pass
```

---

## Migration Plan

### Alembic Migrations

```python
# alembic/versions/036_add_spec_embeddings.py
def upgrade():
    op.create_table(
        "spec_embeddings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("spec_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=False),
        sa.Column("project_id", sa.String(255), nullable=False),
        sa.Column("embedding", sa.LargeBinary, nullable=False),
        sa.Column("embedding_dimension", sa.Integer, nullable=False),
        sa.Column("embedding_model", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(50)),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("source_text_length", sa.Integer),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("spec_id", "spec_type", "embedding_model", name="uq_spec_embedding"),
    )
    op.create_index("ix_spec_embeddings_spec", "spec_embeddings", ["spec_id", "spec_type"])
    op.create_index("ix_spec_embeddings_project", "spec_embeddings", ["project_id"])
    op.create_index("ix_spec_embeddings_content_hash", "spec_embeddings", ["content_hash"])


# alembic/versions/037_add_version_blocks.py
def upgrade():
    op.create_table(
        "version_blocks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("block_id", sa.String(64), unique=True, nullable=False),
        sa.Column("previous_block_id", sa.String(64)),
        sa.Column("spec_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=False),
        sa.Column("project_id", sa.String(255), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("author_id", sa.String(255)),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column("change_summary", sa.Text),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("merkle_root", sa.String(64)),
        sa.Column("digital_signature", sa.String(512)),
        sa.Column("nonce", sa.Integer),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["previous_block_id"], ["version_blocks.block_id"]),
    )
    op.create_index("ix_version_blocks_spec", "version_blocks", ["spec_id", "spec_type"])
    op.create_index("ix_version_blocks_project", "version_blocks", ["project_id"])
    op.create_index("ix_version_blocks_previous", "version_blocks", ["previous_block_id"])
    op.create_index("ix_version_blocks_timestamp", "version_blocks", ["timestamp"])

    op.create_table(
        "version_chains",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("spec_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50), nullable=False),
        sa.Column("project_id", sa.String(255), nullable=False),
        sa.Column("chain_head_id", sa.String(64), nullable=False),
        sa.Column("chain_length", sa.Integer, nullable=False, server_default="1"),
        sa.Column("genesis_block_id", sa.String(64), nullable=False),
        sa.Column("is_valid", sa.Boolean, server_default="true"),
        sa.Column("last_verified_at", sa.DateTime(timezone=True)),
        sa.Column("broken_links", JSONB, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("spec_id", "spec_type", name="uq_version_chain_spec"),
        sa.ForeignKeyConstraint(["chain_head_id"], ["version_blocks.block_id"]),
        sa.ForeignKeyConstraint(["genesis_block_id"], ["version_blocks.block_id"]),
    )
    op.create_index("ix_version_chains_project", "version_chains", ["project_id"])


# alembic/versions/038_add_baselines.py
def upgrade():
    op.create_table(
        "baselines",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("baseline_id", sa.String(64), unique=True, nullable=False),
        sa.Column("project_id", sa.String(255), nullable=False),
        sa.Column("spec_type", sa.String(50)),
        sa.Column("merkle_root", sa.String(64), nullable=False),
        sa.Column("merkle_tree_json", JSONB),
        sa.Column("items_count", sa.Integer, nullable=False),
        sa.Column("baseline_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("tags", JSONB, server_default="[]"),
        sa.Column("created_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", JSONB, server_default="{}"),
    )
    op.create_index("ix_baselines_project", "baselines", ["project_id"])
    op.create_index("ix_baselines_root", "baselines", ["merkle_root"])
    op.create_index("ix_baselines_type", "baselines", ["baseline_type"])

    op.create_table(
        "baseline_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("baseline_id", UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", sa.String(255), nullable=False),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("leaf_hash", sa.String(64), nullable=False),
        sa.Column("leaf_index", sa.Integer, nullable=False),
        sa.Column("version_at_baseline", sa.Integer),
        sa.Column("content_snapshot", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("baseline_id", "item_id", name="uq_baseline_item"),
        sa.ForeignKeyConstraint(["baseline_id"], ["baselines.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_baseline_items_baseline", "baseline_items", ["baseline_id"])
    op.create_index("ix_baseline_items_item", "baseline_items", ["item_id", "item_type"])

    op.create_table(
        "merkle_proofs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("baseline_id", UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", sa.String(255), nullable=False),
        sa.Column("leaf_hash", sa.String(64), nullable=False),
        sa.Column("proof_path", JSONB, nullable=False),
        sa.Column("root_hash", sa.String(64), nullable=False),
        sa.Column("verified", sa.Boolean),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("baseline_id", "item_id", name="uq_merkle_proof"),
        sa.ForeignKeyConstraint(["baseline_id"], ["baselines.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_merkle_proofs_baseline", "merkle_proofs", ["baseline_id"])
    op.create_index("ix_merkle_proofs_item", "merkle_proofs", ["item_id"])
```

---

## Implementation Priority

### Phase 1: Quick Wins (1-2 days)
1. **Baseline tables** - Enable Merkle proof and verification
2. **Wire verify-baseline endpoint** - Uses existing MerkleTree class

### Phase 2: Medium Effort (2-3 days)
3. **Version blocks tables** - Enable version chain storage
4. **Wire version-chain endpoint** - Implement chain traversal

### Phase 3: ML Integration (3-5 days)
5. **Embeddings table** - Store vector embeddings
6. **Add sentence-transformers dependency**
7. **Wire similarity endpoint** - Compute and compare embeddings

---

## Testing Considerations

### Unit Tests
- Test MerkleTree construction and proof generation
- Test version block hash computation
- Test embedding serialization/deserialization

### Integration Tests
- Test baseline creation and retrieval
- Test version chain integrity verification
- Test similarity search with known duplicates

### Performance Tests
- Benchmark Merkle proof generation for large baselines (10K+ items)
- Benchmark embedding computation batch sizes
- Test version chain traversal with deep history (1K+ versions)
