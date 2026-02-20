"""Performance tests for blockchain-style version tracking.

Tests:
- Large baseline creation and verification
- Version chain growth scalability
- Merkle proof generation at scale
- Hash computation throughput
"""

import time
from itertools import starmap
from typing import Any

import pytest
import pytest_asyncio

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.models.project import Project
from tracertm.repositories.blockchain_repository import (
    BaselineRepository,
    VersionBlockRepository,
)

pytestmark = pytest.mark.integration


class TestMerkleTreePerformance:
    """Performance tests for Merkle tree operations."""

    @pytest.fixture
    def baseline_repo(self) -> None:
        return BaselineRepository()

    def test_merkle_tree_build_1000_items(self, baseline_repo: Any) -> None:
        """Test building Merkle tree with 1000 items."""
        items = [(f"item-{i:04d}", f"hash-{i:04d}") for i in range(1000)]

        start = time.perf_counter()
        root, structure = baseline_repo.build_merkle_tree(items)
        elapsed = time.perf_counter() - start

        assert root != ""
        assert len(structure["leaves"]) == 1000
        # Should complete in under 1 second
        assert elapsed < 1.0, f"Tree build took {elapsed:.3f}s, expected < 1.0s"

    def test_merkle_tree_build_10000_items(self, baseline_repo: Any) -> None:
        """Test building Merkle tree with 10000 items."""
        items = [(f"item-{i:05d}", f"hash-{i:05d}") for i in range(10000)]

        start = time.perf_counter()
        root, structure = baseline_repo.build_merkle_tree(items)
        elapsed = time.perf_counter() - start

        assert root != ""
        assert len(structure["leaves"]) == 10000
        # Should complete in under 5 seconds
        assert elapsed < float(COUNT_FIVE + 0.0), f"Tree build took {elapsed:.3f}s, expected < float(COUNT_FIVE + 0.0)s"

    def test_merkle_proof_generation_batch(self, baseline_repo: Any) -> None:
        """Test generating proofs for all items in a large tree."""
        items = [(f"item-{i:04d}", f"hash-{i:04d}") for i in range(1000)]
        _root, structure = baseline_repo.build_merkle_tree(items)

        start = time.perf_counter()
        proofs = []
        for item_id, content_hash in items:
            proof = baseline_repo.generate_proof(item_id, content_hash, structure)
            proofs.append(proof)
        elapsed = time.perf_counter() - start

        assert len(proofs) == 1000
        assert all(p is not None for p in proofs)
        # Should generate 1000 proofs in under 2 seconds
        assert elapsed < float(COUNT_TWO + 0.0), (
            f"Proof generation took {elapsed:.3f}s, expected < float(COUNT_TWO + 0.0)s"
        )

    def test_merkle_proof_verification_batch(self, baseline_repo: Any) -> None:
        """Test verifying proofs for all items in a large tree."""
        items = [(f"item-{i:04d}", f"hash-{i:04d}") for i in range(1000)]
        root, structure = baseline_repo.build_merkle_tree(items)

        # Pre-generate proofs and leaf hashes
        verification_data = []
        for item_id, content_hash in items:
            leaf_hash = baseline_repo.compute_leaf_hash(item_id, content_hash)
            proof = baseline_repo.generate_proof(item_id, content_hash, structure)
            verification_data.append((leaf_hash, proof))

        start = time.perf_counter()
        results = []
        for leaf_hash, proof in verification_data:
            is_valid = baseline_repo.verify_proof(leaf_hash, proof, root)
            results.append(is_valid)
        elapsed = time.perf_counter() - start

        assert all(results)
        # Should verify 1000 proofs in under 1 second
        assert elapsed < 1.0, f"Proof verification took {elapsed:.3f}s, expected < 1.0s"


class TestHashingPerformance:
    """Performance tests for hash computation."""

    @pytest.fixture
    def version_repo(self) -> None:
        return VersionBlockRepository()

    @pytest.fixture
    def baseline_repo(self) -> None:
        return BaselineRepository()

    def test_content_hash_throughput(self, version_repo: Any) -> None:
        """Test throughput of content hash computation."""
        contents = [{"id": f"item-{i}", "name": f"Item {i}", "value": i} for i in range(1000)]

        start = time.perf_counter()
        hashes = [version_repo.compute_content_hash(c) for c in contents]
        elapsed = time.perf_counter() - start

        assert len(hashes) == 1000
        assert len(set(hashes)) == 1000  # All unique
        # Should hash 1000 items in under 0.5 seconds
        assert elapsed < 0.5, f"Hashing took {elapsed:.3f}s, expected < 0.5s"

    def test_leaf_hash_throughput(self, baseline_repo: Any) -> None:
        """Test throughput of leaf hash computation."""
        items = [(f"item-{i:04d}", f"hash-{i:04d}") for i in range(10000)]

        start = time.perf_counter()
        hashes = list(starmap(baseline_repo.compute_leaf_hash, items))
        elapsed = time.perf_counter() - start

        assert len(hashes) == 10000
        # Should hash 10000 items in under 1 second
        assert elapsed < 1.0, f"Leaf hashing took {elapsed:.3f}s, expected < 1.0s"

    def test_block_hash_throughput(self, version_repo: Any) -> None:
        """Test throughput of block hash computation."""
        from datetime import UTC, datetime

        timestamp = datetime.now(UTC)

        start = time.perf_counter()
        hashes = []
        for i in range(1000):
            h = version_repo.compute_block_hash(
                previous_block_id=f"prev-{i}",
                content_hash=f"content-{i}",
                timestamp=timestamp,
                author_id=f"author-{i}",
                change_type="update",
            )
            hashes.append(h)
        elapsed = time.perf_counter() - start

        assert len(hashes) == 1000
        # Should hash 1000 blocks in under 0.5 seconds
        assert elapsed < 0.5, f"Block hashing took {elapsed:.3f}s, expected < 0.5s"


class TestDatabasePerformance:
    """Performance tests for database operations."""

    @pytest_asyncio.fixture
    async def large_project(self, db_session: Any) -> None:
        """Create a project for performance testing."""
        project = Project(id="perf-test-project", name="Performance Test")
        db_session.add(project)
        await db_session.commit()
        return project

    @pytest.mark.asyncio
    async def test_baseline_creation_500_items(self, db_session: Any, large_project: Any) -> None:
        """Test creating baseline with 500 items."""
        repo = BaselineRepository()

        items = [(f"ITEM-{i:04d}", "requirement", f"hash-{i:04d}") for i in range(500)]

        start = time.perf_counter()
        baseline = await repo.create_baseline(
            db=db_session,
            project_id=large_project.id,
            baseline_type="performance",
            name="Large Baseline",
            items=items,
            created_by="perf-tester",
        )
        await db_session.flush()
        elapsed = time.perf_counter() - start

        assert baseline is not None
        assert baseline.items_count == HTTP_INTERNAL_SERVER_ERROR
        # Should complete in under 5 seconds
        assert elapsed < float(COUNT_FIVE + 0.0), (
            f"Baseline creation took {elapsed:.3f}s, expected < float(COUNT_FIVE + 0.0)s"
        )

    @pytest.mark.asyncio
    async def test_chain_growth_100_blocks(self, db_session: Any, large_project: Any) -> None:
        """Test growing version chain to 100 blocks."""
        repo = VersionBlockRepository()

        start = time.perf_counter()

        # Create genesis
        await repo.create_genesis_block(
            db=db_session,
            spec_id="PERF-001",
            spec_type="performance",
            project_id=large_project.id,
            content={"version": 1},
            author_id="user-1",
        )

        # Add 99 more blocks
        for i in range(2, 101):
            await repo.add_block(
                db=db_session,
                spec_id="PERF-001",
                spec_type="performance",
                project_id=large_project.id,
                content={"version": i},
                author_id=f"user-{i}",
                change_type="update",
                change_summary=f"Update {i}",
            )

        await db_session.flush()
        elapsed = time.perf_counter() - start

        # Verify chain length
        chain = await repo.get_chain_index(db_session, "PERF-001", "performance")
        assert chain is not None
        assert chain.chain_length == 100

        # Should complete in under 10 seconds
        assert elapsed < float(COUNT_TEN + 0.0), f"Chain growth took {elapsed:.3f}s, expected < float(COUNT_TEN + 0.0)s"

    @pytest.mark.asyncio
    async def test_chain_retrieval_100_blocks(self, db_session: Any, large_project: Any) -> None:
        """Test retrieving a 100-block chain."""
        repo = VersionBlockRepository()

        # Create chain of 100 blocks
        await repo.create_genesis_block(
            db=db_session,
            spec_id="RETR-001",
            spec_type="retrieval",
            project_id=large_project.id,
            content={"version": 1},
            author_id="user-1",
        )

        for i in range(2, 101):
            await repo.add_block(
                db=db_session,
                spec_id="RETR-001",
                spec_type="retrieval",
                project_id=large_project.id,
                content={"version": i},
                author_id=f"user-{i}",
                change_type="update",
                change_summary=f"Update {i}",
            )

        await db_session.flush()

        # Time retrieval
        start = time.perf_counter()
        chain = await repo.get_version_chain(
            db=db_session,
            spec_id="RETR-001",
            spec_type="retrieval",
            limit=100,
        )
        elapsed = time.perf_counter() - start

        assert len(chain) == 100
        # Should retrieve in under 1 second
        assert elapsed < 1.0, f"Chain retrieval took {elapsed:.3f}s, expected < 1.0s"

    @pytest.mark.asyncio
    async def test_chain_verification_100_blocks(self, db_session: Any, large_project: Any) -> None:
        """Test verifying a 100-block chain."""
        repo = VersionBlockRepository()

        # Create chain of 100 blocks
        await repo.create_genesis_block(
            db=db_session,
            spec_id="VERIFY-001",
            spec_type="verification",
            project_id=large_project.id,
            content={"version": 1},
            author_id="user-1",
        )

        for i in range(2, 101):
            await repo.add_block(
                db=db_session,
                spec_id="VERIFY-001",
                spec_type="verification",
                project_id=large_project.id,
                content={"version": i},
                author_id=f"user-{i}",
                change_type="update",
                change_summary=f"Update {i}",
            )

        await db_session.flush()

        # Time verification
        start = time.perf_counter()
        is_valid, broken = await repo.verify_chain_integrity(
            db=db_session,
            spec_id="VERIFY-001",
            spec_type="verification",
        )
        elapsed = time.perf_counter() - start

        assert is_valid is True
        assert broken == []
        # Should verify in under 2 seconds
        assert elapsed < float(COUNT_TWO + 0.0), (
            f"Chain verification took {elapsed:.3f}s, expected < float(COUNT_TWO + 0.0)s"
        )


class TestMemoryUsage:
    """Tests for memory-efficient operations."""

    @pytest.fixture
    def baseline_repo(self) -> None:
        return BaselineRepository()

    def test_large_tree_proof_memory(self, baseline_repo: Any) -> None:
        """Test that proof size scales logarithmically."""
        import math

        sizes = [100, 1000, 10000]
        proof_lengths = []

        for size in sizes:
            items = [(f"item-{i}", f"hash-{i}") for i in range(size)]
            _root, structure = baseline_repo.build_merkle_tree(items)
            proof = baseline_repo.generate_proof("item-0", "hash-0", structure)
            proof_lengths.append(len(proof))

        # Verify logarithmic scaling
        # For n=100, log2(100) ≈ 7
        # For n=1000, log2(1000) ≈ 10
        # For n=10000, log2(10000) ≈ 14
        for _i, (size, length) in enumerate(zip(sizes, proof_lengths, strict=False)):
            expected_max = math.ceil(math.log2(size)) + 1
            assert length <= expected_max, f"Proof length {length} for {size} items exceeds expected max {expected_max}"

    def test_tree_structure_size_reasonable(self, baseline_repo: Any) -> None:
        """Test that tree structure size is reasonable."""
        import json

        items = [(f"item-{i:04d}", f"hash-{i:04d}") for i in range(1000)]
        _root, structure = baseline_repo.build_merkle_tree(items)

        # Serialize to JSON to measure size
        structure_json = json.dumps(structure)
        size_kb = len(structure_json) / 1024

        # For 1000 items, structure should be under 500KB
        assert size_kb < HTTP_INTERNAL_SERVER_ERROR, f"Structure size {size_kb:.1f}KB exceeds 500KB limit"


class TestScalabilityLimits:
    """Tests to establish scalability limits."""

    @pytest.fixture
    def baseline_repo(self) -> None:
        return BaselineRepository()

    @pytest.fixture
    def version_repo(self) -> None:
        return VersionBlockRepository()

    def test_merkle_tree_very_large(self, baseline_repo: Any) -> None:
        """Test Merkle tree with 50000 items."""
        items = [(f"item-{i:06d}", f"hash-{i:06d}") for i in range(50000)]

        start = time.perf_counter()
        root, structure = baseline_repo.build_merkle_tree(items)
        elapsed = time.perf_counter() - start

        assert root != ""
        assert len(structure["leaves"]) == 50000
        # Should complete in under 30 seconds
        assert elapsed < 30.0, f"Large tree build took {elapsed:.3f}s, expected < 30.0s"

    def test_hash_computation_stress(self, version_repo: Any) -> None:
        """Stress test hash computation with 10000 operations."""
        from datetime import UTC, datetime

        timestamp = datetime.now(UTC)

        start = time.perf_counter()
        for i in range(10000):
            version_repo.compute_block_hash(
                previous_block_id=f"prev-{i}",
                content_hash=f"content-{i}",
                timestamp=timestamp,
                author_id=f"author-{i}",
                change_type="update",
            )
        elapsed = time.perf_counter() - start

        throughput = 10000 / elapsed
        # Should achieve at least 5000 hashes/second
        assert throughput > 5000, f"Throughput {throughput:.0f}/s below 5000/s"
