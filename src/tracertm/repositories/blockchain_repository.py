"""Repositories for blockchain-style version tracking and baselines.

Provides data access layer for:
- VersionBlock: Blockchain-style version records
- VersionChainIndex: Fast chain lookup
- Baseline: Merkle tree snapshots
- BaselineItem: Items in baselines
- MerkleProofCache: Cached proofs
- SpecEmbedding: Sentence embeddings

Architecture:
- Async/await with AsyncSession
- Cryptographic hash validation
- Merkle tree operations
- Embedding storage/retrieval
"""

import hashlib
import json
import operator
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.blockchain import (
    Baseline,
    BaselineItem,
    MerkleProofCache,
    SpecEmbedding,
    VersionBlock,
    VersionChainIndex,
)

# =============================================================================
# Version Block Repository
# =============================================================================


class VersionBlockRepository:
    """Repository for blockchain-style version blocks."""

    @staticmethod
    def compute_block_hash(
        previous_block_id: str | None,
        content_hash: str,
        timestamp: datetime,
        author_id: str | None,
        change_type: str,
    ) -> str:
        """Compute SHA-256 hash for a block.

        Note: Timestamps are normalized to UTC and stored as naive datetime
        strings (without timezone suffix) to ensure consistency across
        databases that may strip timezone information.
        """
        # Normalize timestamp: convert to UTC naive datetime for consistent hashing
        # This ensures the hash is the same whether timezone is preserved or not
        ts_utc = timestamp.astimezone(UTC).replace(tzinfo=None) if timestamp.tzinfo is not None else timestamp

        data = json.dumps(
            {
                "previous_block_id": previous_block_id or "",
                "content_hash": content_hash,
                "timestamp": ts_utc.isoformat(),
                "author_id": author_id or "",
                "change_type": change_type,
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def compute_content_hash(content: dict[str, Any]) -> str:
        """Compute SHA-256 hash of content."""
        data = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()

    async def create_genesis_block(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        project_id: str,
        content: dict[str, Any],
        author_id: str | None,
        change_summary: str = "Initial creation",
    ) -> VersionBlock:
        """Create the first block in a version chain."""
        timestamp = datetime.now(UTC)
        content_hash = self.compute_content_hash(content)
        block_id = self.compute_block_hash(None, content_hash, timestamp, author_id, "create")

        block = VersionBlock(
            id=uuid4(),
            block_id=block_id,
            previous_block_id=None,
            spec_id=spec_id,
            spec_type=spec_type,
            project_id=project_id,
            version_number=1,
            timestamp=timestamp,
            author_id=author_id,
            change_type="create",
            change_summary=change_summary,
            content_hash=content_hash,
        )

        db.add(block)
        await db.flush()

        # Create chain index
        chain = VersionChainIndex(
            id=uuid4(),
            spec_id=spec_id,
            spec_type=spec_type,
            project_id=project_id,
            chain_head_id=block_id,
            chain_length=1,
            genesis_block_id=block_id,
        )
        db.add(chain)
        await db.flush()

        return block

    async def add_block(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        project_id: str,
        content: dict[str, Any],
        author_id: str | None,
        change_type: str,
        change_summary: str,
    ) -> VersionBlock:
        """Add a new block to the version chain."""
        # Get current chain head
        chain = await self.get_chain_index(db, spec_id, spec_type)

        if not chain:
            # No chain exists, create genesis
            return await self.create_genesis_block(
                db,
                spec_id,
                spec_type,
                project_id,
                content,
                author_id,
                change_summary,
            )

        timestamp = datetime.now(UTC)
        content_hash = self.compute_content_hash(content)
        block_id = self.compute_block_hash(chain.chain_head_id, content_hash, timestamp, author_id, change_type)

        block = VersionBlock(
            id=uuid4(),
            block_id=block_id,
            previous_block_id=chain.chain_head_id,
            spec_id=spec_id,
            spec_type=spec_type,
            project_id=project_id,
            version_number=chain.chain_length + 1,
            timestamp=timestamp,
            author_id=author_id,
            change_type=change_type,
            change_summary=change_summary,
            content_hash=content_hash,
        )

        db.add(block)

        # Update chain head
        chain.chain_head_id = block_id
        chain.chain_length += 1
        chain.updated_at = timestamp

        await db.flush()
        return block

    async def get_chain_index(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
    ) -> VersionChainIndex | None:
        """Get the chain index for a spec."""
        result = await db.execute(
            select(VersionChainIndex).where(
                and_(
                    VersionChainIndex.spec_id == spec_id,
                    VersionChainIndex.spec_type == spec_type,
                ),
            ),
        )
        return result.scalar_one_or_none()

    async def get_version_chain(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        limit: int = 50,
    ) -> list[VersionBlock]:
        """Get the version chain for a spec, newest first."""
        chain = await self.get_chain_index(db, spec_id, spec_type)
        if not chain:
            return []

        # Traverse chain from head
        blocks: list[Any] = []
        current_id: str | None = chain.chain_head_id

        while current_id and len(blocks) < limit:
            result = await db.execute(select(VersionBlock).where(VersionBlock.block_id == current_id))
            block = result.scalar_one_or_none()
            if not block:
                break
            blocks.append(block)
            current_id = block.previous_block_id

        return blocks

    async def verify_chain_integrity(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
    ) -> tuple[bool, list[str]]:
        """Verify all hash links in the chain are valid."""
        blocks = await self.get_version_chain(db, spec_id, spec_type, limit=10000)
        broken_links = []

        for _i, block in enumerate(blocks[:-1]):  # Skip genesis
            expected_hash = self.compute_block_hash(
                block.previous_block_id,
                block.content_hash,
                block.timestamp,
                block.author_id,
                block.change_type,
            )
            if expected_hash != block.block_id:
                broken_links.append(block.block_id)

        # Update chain validity
        chain = await self.get_chain_index(db, spec_id, spec_type)
        if chain:
            chain.is_valid = len(broken_links) == 0
            chain.last_verified_at = datetime.now(UTC)
            chain.broken_links = broken_links

        return len(broken_links) == 0, broken_links


# =============================================================================
# Baseline Repository
# =============================================================================


class BaselineRepository:
    """Repository for Merkle tree baselines."""

    @staticmethod
    def compute_leaf_hash(item_id: str, content_hash: str) -> str:
        """Compute leaf hash for Merkle tree."""
        data = f"{item_id}:{content_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def compute_pair_hash(left: str, right: str) -> str:
        """Compute hash of two sibling nodes."""
        combined = left + right if left <= right else right + left
        return hashlib.sha256(combined.encode()).hexdigest()

    def build_merkle_tree(self, items: list[tuple[str, str]]) -> tuple[str, dict[str, Any]]:
        """Build Merkle tree from items, return root and tree structure."""
        if not items:
            return "", {}

        # Sort items by id for consistency
        sorted_items = sorted(items, key=operator.itemgetter(0))

        # Compute leaf hashes
        leaves = [
            {"item_id": item_id, "hash": self.compute_leaf_hash(item_id, content_hash)}
            for item_id, content_hash in sorted_items
        ]

        # Build tree bottom-up
        current_level = [leaf["hash"] for leaf in leaves]
        tree_levels = [current_level.copy()]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                next_level.append(self.compute_pair_hash(left, right))
            current_level = next_level
            tree_levels.append(current_level.copy())

        root = current_level[0] if current_level else ""

        return root, {"levels": tree_levels, "leaves": leaves}

    def generate_proof(
        self,
        item_id: str,
        _content_hash: str,
        tree_structure: dict[str, Any],
    ) -> list[dict[str, str]] | None:
        """Generate Merkle proof for an item."""
        if not tree_structure:
            return None

        leaves = tree_structure.get("leaves", [])
        levels = tree_structure.get("levels", [])

        # Find leaf index
        leaf_index = None
        for i, leaf in enumerate(leaves):
            if leaf["item_id"] == item_id:
                leaf_index = i
                break

        if leaf_index is None:
            return None

        # Build proof path
        proof = []
        index = leaf_index

        for level_hashes in levels[:-1]:  # Exclude root
            sibling_index = index ^ 1  # Toggle last bit
            if sibling_index < len(level_hashes):
                # Normal case: sibling exists
                direction = "left" if sibling_index < index else "right"
                proof.append({"hash": level_hashes[sibling_index], "direction": direction})
            else:
                # Odd level: last node is duplicated with itself
                # The sibling is the node itself
                proof.append({"hash": level_hashes[index], "direction": "right"})
            index //= 2

        return proof

    def verify_proof(self, leaf_hash: str, proof: list[dict[str, str]], root_hash: str) -> bool:
        """Verify a Merkle proof."""
        current = leaf_hash

        for step in proof:
            sibling = step["hash"]
            direction = step["direction"]

            if direction == "left":
                current = self.compute_pair_hash(sibling, current)
            else:
                current = self.compute_pair_hash(current, sibling)

        return current == root_hash

    async def create_baseline(
        self,
        db: AsyncSession,
        project_id: str,
        baseline_type: str,
        name: str,
        items: list[tuple[str, str, str]],  # (item_id, item_type, content_hash)
        created_by: str | None,
        description: str | None = None,
        spec_type: str | None = None,
    ) -> Baseline:
        """Create a new baseline with Merkle tree."""
        baseline_id = hashlib.sha256(f"{project_id}:{datetime.now(UTC).isoformat()}:{name}".encode()).hexdigest()[:16]

        # Build Merkle tree
        merkle_items = [(item_id, content_hash) for item_id, _, content_hash in items]
        merkle_root, tree_structure = self.build_merkle_tree(merkle_items)

        baseline = Baseline(
            id=uuid4(),
            baseline_id=baseline_id,
            project_id=project_id,
            spec_type=spec_type,
            merkle_root=merkle_root,
            merkle_tree_json=tree_structure,
            items_count=len(items),
            baseline_type=baseline_type,
            name=name,
            description=description,
            created_by=created_by,
        )

        db.add(baseline)
        await db.flush()

        # Add baseline items
        for i, (item_id, item_type, content_hash) in enumerate(items):
            leaf_hash = self.compute_leaf_hash(item_id, content_hash)
            item = BaselineItem(
                id=uuid4(),
                baseline_id=baseline.id,
                item_id=item_id,
                item_type=item_type,
                content_hash=content_hash,
                leaf_hash=leaf_hash,
                leaf_index=i,
            )
            db.add(item)

        # Pre-compute and cache proofs
        for item_id, _item_type, content_hash in items:
            proof = self.generate_proof(item_id, content_hash, tree_structure)
            if proof is not None:  # Empty list is valid (single item)
                leaf_hash = self.compute_leaf_hash(item_id, content_hash)
                cached_proof = MerkleProofCache(
                    id=uuid4(),
                    baseline_id=baseline.id,
                    item_id=item_id,
                    leaf_hash=leaf_hash,
                    proof_path=proof,
                    root_hash=merkle_root,
                )
                db.add(cached_proof)

        await db.flush()
        return baseline

    async def get_baseline(self, db: AsyncSession, baseline_id: str) -> Baseline | None:
        """Get baseline by ID."""
        result = await db.execute(select(Baseline).where(Baseline.baseline_id == baseline_id))
        return result.scalar_one_or_none()

    async def get_baseline_by_root(self, db: AsyncSession, merkle_root: str) -> Baseline | None:
        """Get baseline by Merkle root."""
        result = await db.execute(select(Baseline).where(Baseline.merkle_root == merkle_root))
        return result.scalar_one_or_none()

    async def get_merkle_proof(self, db: AsyncSession, baseline_id: str, item_id: str) -> MerkleProofCache | None:
        """Get cached Merkle proof for an item."""
        baseline = await self.get_baseline(db, baseline_id)
        if not baseline:
            return None

        result = await db.execute(
            select(MerkleProofCache).where(
                and_(
                    MerkleProofCache.baseline_id == baseline.id,
                    MerkleProofCache.item_id == item_id,
                ),
            ),
        )
        return result.scalar_one_or_none()

    async def verify_item_in_baseline(
        self,
        db: AsyncSession,
        item_id: str,
        current_content_hash: str,
        baseline_root: str,
    ) -> tuple[bool, MerkleProofCache | None]:
        """Verify an item against a baseline."""
        baseline = await self.get_baseline_by_root(db, baseline_root)
        if not baseline:
            return False, None

        # Get baseline item
        result = await db.execute(
            select(BaselineItem).where(
                and_(
                    BaselineItem.baseline_id == baseline.id,
                    BaselineItem.item_id == item_id,
                ),
            ),
        )
        baseline_item = result.scalar_one_or_none()

        if not baseline_item:
            return False, None

        # Check content hash matches
        if baseline_item.content_hash != current_content_hash:
            return False, None

        # Get proof
        proof = await self.get_merkle_proof(db, baseline.baseline_id, item_id)
        if not proof:
            return False, None

        # Verify proof
        is_valid = self.verify_proof(proof.leaf_hash, proof.proof_path, proof.root_hash)

        # Update verification cache
        proof.verified = is_valid
        proof.verified_at = datetime.now(UTC)

        return is_valid, proof


# =============================================================================
# Embedding Repository
# =============================================================================


class SpecEmbeddingRepository:
    """Repository for sentence embeddings."""

    async def store_embedding(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        project_id: str,
        embedding: bytes,
        embedding_dimension: int,
        embedding_model: str,
        content_hash: str,
        source_text_length: int | None = None,
        model_version: str | None = None,
    ) -> SpecEmbedding:
        """Store or update an embedding."""
        # Check if exists
        result = await db.execute(
            select(SpecEmbedding).where(
                and_(
                    SpecEmbedding.spec_id == spec_id,
                    SpecEmbedding.spec_type == spec_type,
                    SpecEmbedding.embedding_model == embedding_model,
                ),
            ),
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update
            existing.embedding = embedding
            existing.content_hash = content_hash
            existing.source_text_length = source_text_length
            existing.model_version = model_version
            existing.updated_at = datetime.now(UTC)
            await db.flush()
            return existing

        # Create new
        emb = SpecEmbedding(
            id=uuid4(),
            spec_id=spec_id,
            spec_type=spec_type,
            project_id=project_id,
            embedding=embedding,
            embedding_dimension=embedding_dimension,
            embedding_model=embedding_model,
            content_hash=content_hash,
            source_text_length=source_text_length,
            model_version=model_version,
        )
        db.add(emb)
        await db.flush()
        return emb

    async def get_embedding(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        embedding_model: str,
    ) -> SpecEmbedding | None:
        """Get embedding for a spec."""
        result = await db.execute(
            select(SpecEmbedding).where(
                and_(
                    SpecEmbedding.spec_id == spec_id,
                    SpecEmbedding.spec_type == spec_type,
                    SpecEmbedding.embedding_model == embedding_model,
                ),
            ),
        )
        return result.scalar_one_or_none()

    async def get_embeddings_for_project(
        self,
        db: AsyncSession,
        project_id: str,
        embedding_model: str,
        spec_type: str | None = None,
    ) -> list[SpecEmbedding]:
        """Get all embeddings for a project."""
        query = select(SpecEmbedding).where(
            and_(
                SpecEmbedding.project_id == project_id,
                SpecEmbedding.embedding_model == embedding_model,
            ),
        )
        if spec_type:
            query = query.where(SpecEmbedding.spec_type == spec_type)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def delete_stale_embeddings(
        self,
        db: AsyncSession,
        spec_id: str,
        spec_type: str,
        current_content_hash: str,
    ) -> int:
        """Delete embeddings with outdated content hash."""
        result = await db.execute(
            select(SpecEmbedding).where(
                and_(
                    SpecEmbedding.spec_id == spec_id,
                    SpecEmbedding.spec_type == spec_type,
                    SpecEmbedding.content_hash != current_content_hash,
                ),
            ),
        )
        stale = list(result.scalars().all())

        for emb in stale:
            await db.delete(emb)

        return len(stale)
