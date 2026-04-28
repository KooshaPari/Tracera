"""Integration tests for baseline management.

Tests full workflow including:
- Creating baselines with multiple items
- Retrieving baselines and their items
- Verifying items against baselines
- Merkle proof generation and verification
- Baseline deletion and cascade
"""

from typing import Any

import pytest
import pytest_asyncio

from tests.test_constants import COUNT_FIVE, COUNT_THREE
from tracertm.models.blockchain import (
    BaselineItem,
    MerkleProofCache,
)
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.repositories.blockchain_repository import BaselineRepository

pytestmark = pytest.mark.integration


class TestBaselineCreation:
    """Test baseline creation with database persistence."""

    @pytest_asyncio.fixture
    async def project_with_items(self, db_session: Any) -> None:
        """Create project with items for baseline testing."""
        project = Project(id="baseline-test-project", name="Baseline Test")
        db_session.add(project)

        items = []
        for i in range(5):
            item = Item(
                id=f"SPEC-{i:03d}",
                project_id="baseline-test-project",
                title=f"Specification {i}",
                view="REQUIREMENT",
                item_type="requirement",
                status="approved",
            )
            db_session.add(item)
            items.append(item)

        await db_session.commit()
        return project, items

    @pytest.mark.asyncio
    async def test_create_baseline_basic(self, db_session: Any, project_with_items: Any) -> None:
        """Test creating a simple baseline."""
        project, items = project_with_items
        repo = BaselineRepository()

        # Prepare items for baseline (item_id, item_type, content_hash)
        baseline_items = [(item.id, item.item_type, f"hash-{item.id}") for item in items]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id=project.id,
            baseline_type="release",
            name="v1.0.0",
            items=baseline_items,
            created_by="test-user",
            description="Initial release baseline",
        )

        assert baseline is not None
        assert baseline.name == "v1.0.0"
        assert baseline.items_count == COUNT_FIVE
        assert baseline.merkle_root != ""
        assert len(baseline.merkle_root) == 64

    @pytest.mark.asyncio
    async def test_baseline_items_persisted(self, db_session: Any, project_with_items: Any) -> None:
        """Test that baseline items are persisted correctly."""
        project, items = project_with_items
        repo = BaselineRepository()

        baseline_items = [(item.id, item.item_type, f"hash-{item.id}") for item in items]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id=project.id,
            baseline_type="snapshot",
            name="Sprint 1 Snapshot",
            items=baseline_items,
            created_by="test-user",
        )

        await db_session.commit()

        # Query baseline items directly
        from sqlalchemy import select

        result = await db_session.execute(select(BaselineItem).where(BaselineItem.baseline_id == baseline.id))
        persisted_items = list(result.scalars().all())

        assert len(persisted_items) == COUNT_FIVE
        item_ids = {item.item_id for item in persisted_items}
        expected_ids = {f"SPEC-{i:03d}" for i in range(5)}
        assert item_ids == expected_ids

    @pytest.mark.asyncio
    async def test_merkle_proofs_cached(self, db_session: Any, project_with_items: Any) -> None:
        """Test that Merkle proofs are pre-computed and cached."""
        project, items = project_with_items
        repo = BaselineRepository()

        baseline_items = [(item.id, item.item_type, f"hash-{item.id}") for item in items]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id=project.id,
            baseline_type="release",
            name="v1.0.0",
            items=baseline_items,
            created_by="test-user",
        )

        await db_session.commit()

        # Query cached proofs
        from sqlalchemy import select

        result = await db_session.execute(select(MerkleProofCache).where(MerkleProofCache.baseline_id == baseline.id))
        cached_proofs = list(result.scalars().all())

        # Should have one proof per item
        assert len(cached_proofs) == COUNT_FIVE

        # Each proof should have valid structure
        for proof_cache in cached_proofs:
            assert proof_cache.leaf_hash != ""
            assert len(proof_cache.leaf_hash) == 64
            assert proof_cache.root_hash == baseline.merkle_root
            assert isinstance(proof_cache.proof_path, list)


class TestBaselineRetrieval:
    """Test baseline retrieval operations."""

    @pytest_asyncio.fixture
    async def baseline_with_items(self, db_session: Any) -> None:
        """Create a baseline for retrieval tests."""
        project = Project(id="retrieval-test-project", name="Retrieval Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()
        baseline_items = [(f"ITEM-{i}", "requirement", f"content-hash-{i}") for i in range(3)]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="retrieval-test-project",
            baseline_type="milestone",
            name="M1",
            items=baseline_items,
            created_by="test-user",
        )

        await db_session.commit()
        return baseline

    @pytest.mark.asyncio
    async def test_get_baseline_by_id(self, db_session: Any, baseline_with_items: Any) -> None:
        """Test retrieving baseline by ID."""
        baseline = baseline_with_items
        repo = BaselineRepository()

        retrieved = await repo.get_baseline(db_session, baseline.baseline_id)

        assert retrieved is not None
        assert retrieved.id == baseline.id
        assert retrieved.name == "M1"
        assert retrieved.items_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_get_baseline_by_merkle_root(self, db_session: Any, baseline_with_items: Any) -> None:
        """Test retrieving baseline by Merkle root."""
        baseline = baseline_with_items
        repo = BaselineRepository()

        retrieved = await repo.get_baseline_by_root(db_session, baseline.merkle_root)

        assert retrieved is not None
        assert retrieved.baseline_id == baseline.baseline_id

    @pytest.mark.asyncio
    async def test_get_merkle_proof(self, db_session: Any, baseline_with_items: Any) -> None:
        """Test retrieving cached Merkle proof."""
        baseline = baseline_with_items
        repo = BaselineRepository()

        proof = await repo.get_merkle_proof(db_session, baseline.baseline_id, "ITEM-0")

        assert proof is not None
        assert proof.item_id == "ITEM-0"
        assert isinstance(proof.proof_path, list)


class TestBaselineVerification:
    """Test item verification against baselines."""

    @pytest_asyncio.fixture
    async def verifiable_baseline(self, db_session: Any) -> None:
        """Create baseline for verification tests."""
        project = Project(id="verify-test-project", name="Verify Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()
        baseline_items = [
            ("REQ-001", "requirement", "original-hash-001"),
            ("REQ-002", "requirement", "original-hash-002"),
            ("REQ-003", "requirement", "original-hash-003"),
        ]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="verify-test-project",
            baseline_type="release",
            name="Verified Release",
            items=baseline_items,
            created_by="test-user",
        )

        await db_session.commit()
        return baseline

    @pytest.mark.asyncio
    async def test_verify_unchanged_item(self, db_session: Any, verifiable_baseline: Any) -> None:
        """Test verification succeeds for unchanged item."""
        baseline = verifiable_baseline
        repo = BaselineRepository()

        is_valid, proof = await repo.verify_item_in_baseline(
            db=db_session,
            item_id="REQ-001",
            current_content_hash="original-hash-001",
            baseline_root=baseline.merkle_root,
        )

        assert is_valid is True
        assert proof is not None
        assert proof.verified is True

    @pytest.mark.asyncio
    async def test_verify_modified_item(self, db_session: Any, verifiable_baseline: Any) -> None:
        """Test verification fails for modified item."""
        baseline = verifiable_baseline
        repo = BaselineRepository()

        is_valid, _proof = await repo.verify_item_in_baseline(
            db=db_session,
            item_id="REQ-001",
            current_content_hash="modified-hash-001",  # Different hash
            baseline_root=baseline.merkle_root,
        )

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_verify_nonexistent_item(self, db_session: Any, verifiable_baseline: Any) -> None:
        """Test verification fails for item not in baseline."""
        baseline = verifiable_baseline
        repo = BaselineRepository()

        is_valid, proof = await repo.verify_item_in_baseline(
            db=db_session,
            item_id="REQ-999",  # Not in baseline
            current_content_hash="any-hash",
            baseline_root=baseline.merkle_root,
        )

        assert is_valid is False
        assert proof is None


class TestBaselineMerkleIntegrity:
    """Test Merkle tree integrity in database context."""

    @pytest.mark.asyncio
    async def test_merkle_tree_consistency(self, db_session: Any) -> None:
        """Test that Merkle tree remains consistent after persistence."""
        project = Project(id="merkle-test-project", name="Merkle Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()

        # Create baseline with known items
        items = [
            (f"DOC-{i:03d}", "document", f"doc-hash-{i}")
            for i in range(7)  # Use 7 items for non-power-of-2 test
        ]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="merkle-test-project",
            baseline_type="archive",
            name="Document Archive",
            items=items,
            created_by="archivist",
        )

        await db_session.commit()

        # Rebuild tree from stored structure and verify root matches
        stored_tree = baseline.merkle_tree_json
        assert stored_tree is not None
        tree = stored_tree
        rebuilt_items = [
            (leaf["item_id"], items[i][2])  # Use original content hash
            for i, leaf in enumerate(tree["leaves"])
        ]
        rebuilt_root, _ = repo.build_merkle_tree(rebuilt_items)

        assert rebuilt_root == baseline.merkle_root

    @pytest.mark.asyncio
    async def test_all_items_verifiable(self, db_session: Any) -> None:
        """Test that all items in baseline can be verified."""
        project = Project(id="all-verify-project", name="All Verify Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()

        items = [(f"FEAT-{i}", "feature", f"feat-hash-{i}") for i in range(10)]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="all-verify-project",
            baseline_type="snapshot",
            name="Feature Snapshot",
            items=items,
            created_by="pm",
        )

        await db_session.commit()

        # Verify every item
        for item_id, _, content_hash in items:
            is_valid, proof = await repo.verify_item_in_baseline(
                db=db_session,
                item_id=item_id,
                current_content_hash=content_hash,
                baseline_root=baseline.merkle_root,
            )
            assert is_valid is True, f"Verification failed for {item_id}"
            assert proof is not None


class TestBaselineEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_baseline(self, db_session: Any) -> None:
        """Test creating baseline with no items."""
        project = Project(id="empty-test-project", name="Empty Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="empty-test-project",
            baseline_type="empty",
            name="Empty Baseline",
            items=[],
            created_by="test",
        )

        assert baseline is not None
        assert baseline.items_count == 0
        assert baseline.merkle_root == ""

    @pytest.mark.asyncio
    async def test_single_item_baseline(self, db_session: Any) -> None:
        """Test baseline with single item."""
        project = Project(id="single-test-project", name="Single Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="single-test-project",
            baseline_type="single",
            name="Single Item",
            items=[("SOLO-001", "item", "solo-hash")],
            created_by="test",
        )

        assert baseline is not None
        assert baseline.items_count == 1

        # Flush to ensure all data is persisted within the session
        await db_session.flush()

        # Single item should be verifiable
        is_valid, _ = await repo.verify_item_in_baseline(
            db=db_session,
            item_id="SOLO-001",
            current_content_hash="solo-hash",
            baseline_root=baseline.merkle_root,
        )
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_large_baseline(self, db_session: Any) -> None:
        """Test baseline with many items."""
        project = Project(id="large-test-project", name="Large Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()

        # Create 100 items
        items = [(f"LARGE-{i:04d}", "item", f"large-hash-{i}") for i in range(100)]

        baseline = await repo.create_baseline(
            db=db_session,
            project_id="large-test-project",
            baseline_type="large",
            name="Large Baseline",
            items=items,
            created_by="test",
        )

        assert baseline is not None
        assert baseline.items_count == 100

        # Verify random samples
        import random

        samples = random.sample(items, 10)
        for item_id, _, content_hash in samples:
            is_valid, _ = await repo.verify_item_in_baseline(
                db=db_session,
                item_id=item_id,
                current_content_hash=content_hash,
                baseline_root=baseline.merkle_root,
            )
            assert is_valid is True

    @pytest.mark.asyncio
    async def test_get_nonexistent_baseline(self, db_session: Any) -> None:
        """Test retrieving baseline that doesn't exist."""
        repo = BaselineRepository()

        baseline = await repo.get_baseline(db_session, "nonexistent-id")
        assert baseline is None

    @pytest.mark.asyncio
    async def test_duplicate_item_ids_rejected(self, db_session: Any) -> None:
        """Test baseline rejects duplicate item IDs due to unique constraint."""
        project = Project(id="dup-test-project", name="Duplicate Test")
        db_session.add(project)
        await db_session.flush()

        repo = BaselineRepository()

        # Same item ID with different hashes - should fail due to unique constraint
        items = [
            ("DUP-001", "item", "hash-v1"),
            ("DUP-001", "item", "hash-v2"),  # Duplicate ID
        ]

        # The unique constraint on (baseline_id, item_id) should prevent this
        import pytest
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await repo.create_baseline(
                db=db_session,
                project_id="dup-test-project",
                baseline_type="dup",
                name="Dup Test",
                items=items,
                created_by="test",
            )
            await db_session.flush()
