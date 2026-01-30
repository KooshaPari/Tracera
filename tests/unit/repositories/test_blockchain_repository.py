"""Unit tests for blockchain repository operations.

Tests:
- MerkleTree: build_merkle_tree, generate_proof, verify_proof
- VersionBlock: compute_block_hash, compute_content_hash
- Chain integrity verification
"""

import pytest
from datetime import datetime, UTC

from tracertm.repositories.blockchain_repository import (
    VersionBlockRepository,
    BaselineRepository,
    SpecEmbeddingRepository,
)


# =============================================================================
# MerkleTree Unit Tests
# =============================================================================


class TestMerkleTreeOperations:
    """Test suite for Merkle tree operations in BaselineRepository."""

    @pytest.fixture
    def baseline_repo(self):
        """Create a BaselineRepository instance."""
        return BaselineRepository()

    def test_compute_leaf_hash(self, baseline_repo):
        """Test leaf hash computation is deterministic."""
        item_id = "REQ-001"
        content_hash = "abc123def456"

        hash1 = baseline_repo.compute_leaf_hash(item_id, content_hash)
        hash2 = baseline_repo.compute_leaf_hash(item_id, content_hash)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest

    def test_compute_leaf_hash_different_inputs(self, baseline_repo):
        """Test different inputs produce different hashes."""
        hash1 = baseline_repo.compute_leaf_hash("REQ-001", "abc123")
        hash2 = baseline_repo.compute_leaf_hash("REQ-002", "abc123")
        hash3 = baseline_repo.compute_leaf_hash("REQ-001", "def456")

        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3

    def test_compute_pair_hash_deterministic(self, baseline_repo):
        """Test pair hash computation is deterministic."""
        left = "a" * 64
        right = "b" * 64

        hash1 = baseline_repo.compute_pair_hash(left, right)
        hash2 = baseline_repo.compute_pair_hash(left, right)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_compute_pair_hash_order_independent(self, baseline_repo):
        """Test pair hash is consistent regardless of argument order."""
        left = "a" * 64
        right = "b" * 64

        # The implementation should sort to ensure consistency
        hash1 = baseline_repo.compute_pair_hash(left, right)
        hash2 = baseline_repo.compute_pair_hash(right, left)

        assert hash1 == hash2

    def test_build_merkle_tree_empty(self, baseline_repo):
        """Test building tree with no items."""
        root, structure = baseline_repo.build_merkle_tree([])

        assert root == ""
        assert structure == {}

    def test_build_merkle_tree_single_item(self, baseline_repo):
        """Test building tree with single item."""
        items = [("item1", "hash1")]

        root, structure = baseline_repo.build_merkle_tree(items)

        assert root != ""
        assert len(root) == 64
        assert "leaves" in structure
        assert len(structure["leaves"]) == 1
        assert structure["leaves"][0]["item_id"] == "item1"

    def test_build_merkle_tree_two_items(self, baseline_repo):
        """Test building tree with two items."""
        items = [("item1", "hash1"), ("item2", "hash2")]

        root, structure = baseline_repo.build_merkle_tree(items)

        assert root != ""
        assert len(root) == 64
        assert "levels" in structure
        assert len(structure["levels"]) == 2  # Leaves + root
        assert len(structure["levels"][0]) == 2  # 2 leaves
        assert len(structure["levels"][1]) == 1  # 1 root

    def test_build_merkle_tree_multiple_items(self, baseline_repo):
        """Test building tree with multiple items."""
        items = [
            ("item1", "hash1"),
            ("item2", "hash2"),
            ("item3", "hash3"),
            ("item4", "hash4"),
        ]

        root, structure = baseline_repo.build_merkle_tree(items)

        assert root != ""
        assert len(structure["leaves"]) == 4
        # For 4 items: level 0 = 4 leaves, level 1 = 2 nodes, level 2 = 1 root
        assert len(structure["levels"]) == 3

    def test_build_merkle_tree_odd_items(self, baseline_repo):
        """Test building tree with odd number of items."""
        items = [
            ("item1", "hash1"),
            ("item2", "hash2"),
            ("item3", "hash3"),
        ]

        root, structure = baseline_repo.build_merkle_tree(items)

        assert root != ""
        assert len(structure["leaves"]) == 3

    def test_build_merkle_tree_sorting(self, baseline_repo):
        """Test that items are sorted by ID for consistency."""
        items1 = [("item1", "hash1"), ("item2", "hash2")]
        items2 = [("item2", "hash2"), ("item1", "hash1")]

        root1, _ = baseline_repo.build_merkle_tree(items1)
        root2, _ = baseline_repo.build_merkle_tree(items2)

        # Same items in different order should produce same root
        assert root1 == root2

    def test_generate_proof_single_item(self, baseline_repo):
        """Test proof generation for single item tree."""
        items = [("item1", "hash1")]
        root, structure = baseline_repo.build_merkle_tree(items)

        proof = baseline_repo.generate_proof("item1", "hash1", structure)

        assert proof is not None
        assert isinstance(proof, list)
        # Single item has empty proof (it IS the root)
        assert len(proof) == 0

    def test_generate_proof_two_items(self, baseline_repo):
        """Test proof generation for two item tree."""
        items = [("item1", "hash1"), ("item2", "hash2")]
        root, structure = baseline_repo.build_merkle_tree(items)

        proof = baseline_repo.generate_proof("item1", "hash1", structure)

        assert proof is not None
        assert len(proof) == 1  # One sibling needed
        assert "hash" in proof[0]
        assert "direction" in proof[0]

    def test_generate_proof_multiple_items(self, baseline_repo):
        """Test proof generation for larger tree."""
        items = [
            ("item1", "hash1"),
            ("item2", "hash2"),
            ("item3", "hash3"),
            ("item4", "hash4"),
        ]
        root, structure = baseline_repo.build_merkle_tree(items)

        proof = baseline_repo.generate_proof("item1", "hash1", structure)

        assert proof is not None
        assert len(proof) == 2  # log2(4) = 2 levels

    def test_generate_proof_nonexistent_item(self, baseline_repo):
        """Test proof generation for item not in tree."""
        items = [("item1", "hash1"), ("item2", "hash2")]
        root, structure = baseline_repo.build_merkle_tree(items)

        proof = baseline_repo.generate_proof("item3", "hash3", structure)

        assert proof is None

    def test_generate_proof_empty_structure(self, baseline_repo):
        """Test proof generation with empty structure."""
        proof = baseline_repo.generate_proof("item1", "hash1", {})

        assert proof is None

    def test_verify_proof_valid(self, baseline_repo):
        """Test verification of valid proof."""
        items = [("item1", "hash1"), ("item2", "hash2")]
        root, structure = baseline_repo.build_merkle_tree(items)

        leaf_hash = baseline_repo.compute_leaf_hash("item1", "hash1")
        proof = baseline_repo.generate_proof("item1", "hash1", structure)

        is_valid = baseline_repo.verify_proof(leaf_hash, proof, root)

        assert is_valid is True

    def test_verify_proof_all_items(self, baseline_repo):
        """Test verification works for all items in tree."""
        items = [
            ("item1", "hash1"),
            ("item2", "hash2"),
            ("item3", "hash3"),
            ("item4", "hash4"),
        ]
        root, structure = baseline_repo.build_merkle_tree(items)

        for item_id, content_hash in items:
            leaf_hash = baseline_repo.compute_leaf_hash(item_id, content_hash)
            proof = baseline_repo.generate_proof(item_id, content_hash, structure)

            is_valid = baseline_repo.verify_proof(leaf_hash, proof, root)
            assert is_valid is True, f"Verification failed for {item_id}"

    def test_verify_proof_invalid_leaf(self, baseline_repo):
        """Test verification fails with wrong leaf hash."""
        items = [("item1", "hash1"), ("item2", "hash2")]
        root, structure = baseline_repo.build_merkle_tree(items)

        wrong_leaf_hash = baseline_repo.compute_leaf_hash("item1", "wrong_hash")
        proof = baseline_repo.generate_proof("item1", "hash1", structure)

        is_valid = baseline_repo.verify_proof(wrong_leaf_hash, proof, root)

        assert is_valid is False

    def test_verify_proof_invalid_root(self, baseline_repo):
        """Test verification fails with wrong root."""
        items = [("item1", "hash1"), ("item2", "hash2")]
        root, structure = baseline_repo.build_merkle_tree(items)

        leaf_hash = baseline_repo.compute_leaf_hash("item1", "hash1")
        proof = baseline_repo.generate_proof("item1", "hash1", structure)
        wrong_root = "f" * 64

        is_valid = baseline_repo.verify_proof(leaf_hash, proof, wrong_root)

        assert is_valid is False

    def test_verify_proof_tampered_proof(self, baseline_repo):
        """Test verification fails with tampered proof."""
        items = [("item1", "hash1"), ("item2", "hash2")]
        root, structure = baseline_repo.build_merkle_tree(items)

        leaf_hash = baseline_repo.compute_leaf_hash("item1", "hash1")
        proof = baseline_repo.generate_proof("item1", "hash1", structure)

        # Tamper with proof
        if proof:
            proof[0]["hash"] = "0" * 64

        is_valid = baseline_repo.verify_proof(leaf_hash, proof, root)

        assert is_valid is False


# =============================================================================
# VersionBlock Unit Tests
# =============================================================================


class TestVersionBlockHashing:
    """Test suite for version block hash operations."""

    @pytest.fixture
    def version_repo(self):
        """Create a VersionBlockRepository instance."""
        return VersionBlockRepository()

    def test_compute_content_hash_deterministic(self, version_repo):
        """Test content hash is deterministic."""
        content = {"name": "test", "value": 123}

        hash1 = version_repo.compute_content_hash(content)
        hash2 = version_repo.compute_content_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_compute_content_hash_different_content(self, version_repo):
        """Test different content produces different hashes."""
        content1 = {"name": "test1"}
        content2 = {"name": "test2"}

        hash1 = version_repo.compute_content_hash(content1)
        hash2 = version_repo.compute_content_hash(content2)

        assert hash1 != hash2

    def test_compute_content_hash_order_independent(self, version_repo):
        """Test dict key order doesn't affect hash."""
        content1 = {"a": 1, "b": 2}
        content2 = {"b": 2, "a": 1}

        hash1 = version_repo.compute_content_hash(content1)
        hash2 = version_repo.compute_content_hash(content2)

        # sorted keys should make these equal
        assert hash1 == hash2

    def test_compute_content_hash_nested(self, version_repo):
        """Test hashing nested content."""
        content = {
            "name": "test",
            "nested": {
                "level1": {
                    "level2": "value"
                }
            },
            "list": [1, 2, 3]
        }

        hash_result = version_repo.compute_content_hash(content)

        assert hash_result is not None
        assert len(hash_result) == 64

    def test_compute_content_hash_with_datetime(self, version_repo):
        """Test hashing content with datetime values."""
        content = {
            "name": "test",
            "timestamp": datetime(2024, 1, 15, 12, 0, 0)
        }

        # Should not raise, datetime gets converted via default=str
        hash_result = version_repo.compute_content_hash(content)

        assert hash_result is not None
        assert len(hash_result) == 64

    def test_compute_block_hash_deterministic(self, version_repo):
        """Test block hash is deterministic."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash1 = version_repo.compute_block_hash(
            previous_block_id="prev123",
            content_hash="content456",
            timestamp=timestamp,
            author_id="user789",
            change_type="update",
        )
        hash2 = version_repo.compute_block_hash(
            previous_block_id="prev123",
            content_hash="content456",
            timestamp=timestamp,
            author_id="user789",
            change_type="update",
        )

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_compute_block_hash_genesis(self, version_repo):
        """Test block hash for genesis block (no previous)."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash_result = version_repo.compute_block_hash(
            previous_block_id=None,
            content_hash="content456",
            timestamp=timestamp,
            author_id="user789",
            change_type="create",
        )

        assert hash_result is not None
        assert len(hash_result) == 64

    def test_compute_block_hash_different_previous(self, version_repo):
        """Test different previous block produces different hash."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash1 = version_repo.compute_block_hash(
            previous_block_id="prev1",
            content_hash="content",
            timestamp=timestamp,
            author_id="user",
            change_type="update",
        )
        hash2 = version_repo.compute_block_hash(
            previous_block_id="prev2",
            content_hash="content",
            timestamp=timestamp,
            author_id="user",
            change_type="update",
        )

        assert hash1 != hash2

    def test_compute_block_hash_different_content(self, version_repo):
        """Test different content produces different hash."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash1 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content1",
            timestamp=timestamp,
            author_id="user",
            change_type="update",
        )
        hash2 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content2",
            timestamp=timestamp,
            author_id="user",
            change_type="update",
        )

        assert hash1 != hash2

    def test_compute_block_hash_different_timestamp(self, version_repo):
        """Test different timestamp produces different hash."""
        hash1 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
            author_id="user",
            change_type="update",
        )
        hash2 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=datetime(2024, 1, 15, 12, 0, 1, tzinfo=UTC),
            author_id="user",
            change_type="update",
        )

        assert hash1 != hash2

    def test_compute_block_hash_different_author(self, version_repo):
        """Test different author produces different hash."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash1 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=timestamp,
            author_id="user1",
            change_type="update",
        )
        hash2 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=timestamp,
            author_id="user2",
            change_type="update",
        )

        assert hash1 != hash2

    def test_compute_block_hash_different_change_type(self, version_repo):
        """Test different change type produces different hash."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash1 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=timestamp,
            author_id="user",
            change_type="create",
        )
        hash2 = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=timestamp,
            author_id="user",
            change_type="update",
        )

        assert hash1 != hash2

    def test_compute_block_hash_null_author(self, version_repo):
        """Test block hash with null author."""
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        hash_result = version_repo.compute_block_hash(
            previous_block_id="prev",
            content_hash="content",
            timestamp=timestamp,
            author_id=None,
            change_type="update",
        )

        assert hash_result is not None
        assert len(hash_result) == 64


# =============================================================================
# Chain Simulation Tests (Pure Logic, No DB)
# =============================================================================


class TestChainLogic:
    """Test chain construction logic without database."""

    @pytest.fixture
    def version_repo(self):
        return VersionBlockRepository()

    def test_chain_link_verification(self, version_repo):
        """Test that consecutive blocks can be verified."""
        # Simulate genesis block
        genesis_content = {"id": "spec-1", "name": "Test Spec", "version": 1}
        genesis_content_hash = version_repo.compute_content_hash(genesis_content)
        genesis_timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        genesis_block_id = version_repo.compute_block_hash(
            previous_block_id=None,
            content_hash=genesis_content_hash,
            timestamp=genesis_timestamp,
            author_id="user1",
            change_type="create",
        )

        # Simulate second block
        second_content = {"id": "spec-1", "name": "Updated Spec", "version": 2}
        second_content_hash = version_repo.compute_content_hash(second_content)
        second_timestamp = datetime(2024, 1, 15, 13, 0, 0, tzinfo=UTC)

        second_block_id = version_repo.compute_block_hash(
            previous_block_id=genesis_block_id,
            content_hash=second_content_hash,
            timestamp=second_timestamp,
            author_id="user2",
            change_type="update",
        )

        # Verify chain: recompute and check
        recomputed_genesis = version_repo.compute_block_hash(
            previous_block_id=None,
            content_hash=genesis_content_hash,
            timestamp=genesis_timestamp,
            author_id="user1",
            change_type="create",
        )

        recomputed_second = version_repo.compute_block_hash(
            previous_block_id=recomputed_genesis,
            content_hash=second_content_hash,
            timestamp=second_timestamp,
            author_id="user2",
            change_type="update",
        )

        assert genesis_block_id == recomputed_genesis
        assert second_block_id == recomputed_second

    def test_tamper_detection(self, version_repo):
        """Test that tampering with a block breaks the chain."""
        # Create original block hash
        original_content = {"id": "spec-1", "value": "original"}
        original_hash = version_repo.compute_content_hash(original_content)
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        original_block_id = version_repo.compute_block_hash(
            previous_block_id=None,
            content_hash=original_hash,
            timestamp=timestamp,
            author_id="user1",
            change_type="create",
        )

        # Tamper with content
        tampered_content = {"id": "spec-1", "value": "tampered"}
        tampered_hash = version_repo.compute_content_hash(tampered_content)

        # Recompute with tampered content
        tampered_block_id = version_repo.compute_block_hash(
            previous_block_id=None,
            content_hash=tampered_hash,
            timestamp=timestamp,
            author_id="user1",
            change_type="create",
        )

        # Block IDs should differ
        assert original_block_id != tampered_block_id


# =============================================================================
# Large Scale Tests
# =============================================================================


class TestLargeScaleMerkleTree:
    """Test Merkle tree with larger datasets."""

    @pytest.fixture
    def baseline_repo(self):
        return BaselineRepository()

    @pytest.mark.parametrize("num_items", [10, 100, 1000])
    def test_build_and_verify_large_tree(self, baseline_repo, num_items):
        """Test building and verifying trees of various sizes."""
        items = [(f"item{i}", f"hash{i}") for i in range(num_items)]

        root, structure = baseline_repo.build_merkle_tree(items)

        assert root != ""
        assert len(structure["leaves"]) == num_items

        # Verify random samples
        import random
        samples = random.sample(items, min(10, num_items))

        for item_id, content_hash in samples:
            leaf_hash = baseline_repo.compute_leaf_hash(item_id, content_hash)
            proof = baseline_repo.generate_proof(item_id, content_hash, structure)

            assert proof is not None
            is_valid = baseline_repo.verify_proof(leaf_hash, proof, root)
            assert is_valid is True

    def test_proof_length_logarithmic(self, baseline_repo):
        """Test that proof length grows logarithmically."""
        import math

        for n in [2, 4, 8, 16, 32, 64]:
            items = [(f"item{i}", f"hash{i}") for i in range(n)]
            root, structure = baseline_repo.build_merkle_tree(items)

            proof = baseline_repo.generate_proof("item0", "hash0", structure)

            expected_length = math.ceil(math.log2(n)) if n > 1 else 0
            assert len(proof) <= expected_length, f"Proof too long for {n} items"
