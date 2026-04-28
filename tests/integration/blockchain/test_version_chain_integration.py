"""Integration tests for version chain management.

Tests full workflow including:
- Creating genesis blocks
- Adding blocks to chains
- Chain traversal and retrieval
- Chain integrity verification
- Version history queries
"""

from typing import Any

import pytest
import pytest_asyncio

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.models.project import Project
from tracertm.repositories.blockchain_repository import VersionBlockRepository

pytestmark = pytest.mark.integration


class TestGenesisBlockCreation:
    """Test creating genesis (first) blocks in version chains."""

    @pytest_asyncio.fixture
    async def project(self, db_session: Any) -> None:
        """Create a test project."""
        project = Project(id="chain-test-project", name="Chain Test")
        db_session.add(project)
        await db_session.commit()
        return project

    @pytest.mark.asyncio
    async def test_create_genesis_block(self, db_session: Any, project: Any) -> None:
        """Test creating a genesis block."""
        repo = VersionBlockRepository()

        content = {"id": "SPEC-001", "name": "First Spec", "version": 1}

        block = await repo.create_genesis_block(
            db=db_session,
            spec_id="SPEC-001",
            spec_type="requirement",
            project_id=project.id,
            content=content,
            author_id="user-1",
            change_summary="Initial creation",
        )

        assert block is not None
        assert block.spec_id == "SPEC-001"
        assert block.spec_type == "requirement"
        assert block.version_number == 1
        assert block.change_type == "create"
        assert block.previous_block_id is None
        assert len(block.block_id) == 64
        assert len(block.content_hash) == 64

    @pytest.mark.asyncio
    async def test_genesis_creates_chain_index(self, db_session: Any, project: Any) -> None:
        """Test that genesis block creates a chain index."""
        repo = VersionBlockRepository()

        content = {"id": "SPEC-002", "name": "Second Spec"}

        await repo.create_genesis_block(
            db=db_session,
            spec_id="SPEC-002",
            spec_type="feature",
            project_id=project.id,
            content=content,
            author_id="user-1",
        )

        await db_session.flush()

        # Get the chain index
        chain = await repo.get_chain_index(db_session, "SPEC-002", "feature")

        assert chain is not None
        assert chain.spec_id == "SPEC-002"
        assert chain.spec_type == "feature"
        assert chain.chain_length == 1
        assert chain.chain_head_id is not None
        assert chain.genesis_block_id == chain.chain_head_id

    @pytest.mark.asyncio
    async def test_genesis_block_hash_deterministic(self, db_session: Any, project: Any) -> None:
        """Test that block hash is deterministic based on inputs."""
        repo = VersionBlockRepository()

        content = {"id": "SPEC-003", "name": "Test Spec"}

        # Create block
        block = await repo.create_genesis_block(
            db=db_session,
            spec_id="SPEC-003",
            spec_type="test",
            project_id=project.id,
            content=content,
            author_id="user-1",
        )

        # Recompute content hash
        expected_content_hash = repo.compute_content_hash(content)

        assert block.content_hash == expected_content_hash


class TestChainGrowth:
    """Test adding blocks to existing chains."""

    @pytest_asyncio.fixture
    async def chain_with_genesis(self, db_session: Any) -> None:
        """Create a project with a genesis block."""
        project = Project(id="growth-test-project", name="Growth Test")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        genesis = await repo.create_genesis_block(
            db=db_session,
            spec_id="GROW-001",
            spec_type="document",
            project_id="growth-test-project",
            content={"version": 1, "text": "Initial content"},
            author_id="author-1",
        )

        await db_session.commit()
        return project, genesis

    @pytest.mark.asyncio
    async def test_add_block_to_chain(self, db_session: Any, chain_with_genesis: Any) -> None:
        """Test adding a block to an existing chain."""
        project, genesis = chain_with_genesis
        repo = VersionBlockRepository()

        new_block = await repo.add_block(
            db=db_session,
            spec_id="GROW-001",
            spec_type="document",
            project_id=project.id,
            content={"version": 2, "text": "Updated content"},
            author_id="author-2",
            change_type="update",
            change_summary="Updated text",
        )

        assert new_block is not None
        assert new_block.version_number == COUNT_TWO
        assert new_block.previous_block_id == genesis.block_id
        assert new_block.change_type == "update"

    @pytest.mark.asyncio
    async def test_chain_length_increases(self, db_session: Any, chain_with_genesis: Any) -> None:
        """Test that chain length increases with each block."""
        project, _genesis = chain_with_genesis
        repo = VersionBlockRepository()

        # Add multiple blocks
        for i in range(3):
            await repo.add_block(
                db=db_session,
                spec_id="GROW-001",
                spec_type="document",
                project_id=project.id,
                content={"version": i + 2, "text": f"Version {i + 2}"},
                author_id=f"author-{i}",
                change_type="update",
                change_summary=f"Update {i + 1}",
            )

        await db_session.flush()

        chain = await repo.get_chain_index(db_session, "GROW-001", "document")
        assert chain is not None
        assert chain.chain_length == COUNT_FOUR  # 1 genesis + 3 updates

    @pytest.mark.asyncio
    async def test_chain_head_updated(self, db_session: Any, chain_with_genesis: Any) -> None:
        """Test that chain head is updated after adding block."""
        project, genesis = chain_with_genesis
        repo = VersionBlockRepository()

        new_block = await repo.add_block(
            db=db_session,
            spec_id="GROW-001",
            spec_type="document",
            project_id=project.id,
            content={"version": 2},
            author_id="author-2",
            change_type="update",
            change_summary="Update",
        )

        await db_session.flush()

        chain = await repo.get_chain_index(db_session, "GROW-001", "document")
        assert chain is not None
        assert chain.chain_head_id == new_block.block_id
        assert chain.genesis_block_id == genesis.block_id

    @pytest.mark.asyncio
    async def test_add_block_creates_chain_if_missing(self, db_session: Any) -> None:
        """Test that add_block creates genesis if no chain exists."""
        project = Project(id="auto-genesis-project", name="Auto Genesis")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        # Add block without existing chain - should create genesis
        block = await repo.add_block(
            db=db_session,
            spec_id="AUTO-001",
            spec_type="auto",
            project_id="auto-genesis-project",
            content={"value": "first"},
            author_id="user",
            change_type="update",  # Will be overridden to "create"
            change_summary="First",
        )

        # Should have created a genesis block
        assert block.version_number == 1
        assert block.previous_block_id is None


class TestChainTraversal:
    """Test traversing and querying version chains."""

    @pytest_asyncio.fixture
    async def populated_chain(self, db_session: Any) -> None:
        """Create a chain with multiple blocks."""
        project = Project(id="traverse-test-project", name="Traverse Test")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        # Create genesis
        genesis = await repo.create_genesis_block(
            db=db_session,
            spec_id="TRAV-001",
            spec_type="traversable",
            project_id="traverse-test-project",
            content={"version": 1},
            author_id="user-1",
        )

        blocks = [genesis]

        # Add 4 more blocks
        for i in range(2, 6):
            block = await repo.add_block(
                db=db_session,
                spec_id="TRAV-001",
                spec_type="traversable",
                project_id="traverse-test-project",
                content={"version": i},
                author_id=f"user-{i}",
                change_type="update",
                change_summary=f"Version {i}",
            )
            blocks.append(block)

        await db_session.commit()
        return project, blocks

    @pytest.mark.asyncio
    async def test_get_version_chain(self, db_session: Any, populated_chain: Any) -> None:
        """Test retrieving full version chain."""
        _project, _original_blocks = populated_chain
        repo = VersionBlockRepository()

        chain = await repo.get_version_chain(
            db=db_session,
            spec_id="TRAV-001",
            spec_type="traversable",
        )

        # Should return blocks newest first
        assert len(chain) == COUNT_FIVE
        assert chain[0].version_number == COUNT_FIVE  # Newest
        assert chain[-1].version_number == 1  # Genesis

    @pytest.mark.asyncio
    async def test_chain_links_valid(self, db_session: Any, populated_chain: Any) -> None:
        """Test that chain links are correctly formed."""
        _project, _original_blocks = populated_chain
        repo = VersionBlockRepository()

        chain = await repo.get_version_chain(
            db=db_session,
            spec_id="TRAV-001",
            spec_type="traversable",
        )

        # Verify chain linkage (newest to oldest)
        for i in range(len(chain) - 1):
            current = chain[i]
            previous = chain[i + 1]
            assert current.previous_block_id == previous.block_id

        # Genesis has no previous
        assert chain[-1].previous_block_id is None

    @pytest.mark.asyncio
    async def test_chain_limit(self, db_session: Any, populated_chain: Any) -> None:
        """Test limiting chain retrieval."""
        _project, _ = populated_chain
        repo = VersionBlockRepository()

        chain = await repo.get_version_chain(
            db=db_session,
            spec_id="TRAV-001",
            spec_type="traversable",
            limit=3,
        )

        assert len(chain) == COUNT_THREE
        assert chain[0].version_number == COUNT_FIVE
        assert chain[-1].version_number == COUNT_THREE


class TestChainIntegrity:
    """Test chain integrity verification."""

    @pytest_asyncio.fixture
    async def verified_chain(self, db_session: Any) -> None:
        """Create a chain for integrity testing."""
        project = Project(id="integrity-test-project", name="Integrity Test")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        await repo.create_genesis_block(
            db=db_session,
            spec_id="INT-001",
            spec_type="integrity",
            project_id="integrity-test-project",
            content={"version": 1},
            author_id="user-1",
        )

        await repo.add_block(
            db=db_session,
            spec_id="INT-001",
            spec_type="integrity",
            project_id="integrity-test-project",
            content={"version": 2},
            author_id="user-2",
            change_type="update",
            change_summary="Update",
        )

        # Use flush instead of commit to keep objects in session
        await db_session.flush()
        return project

    @pytest.mark.asyncio
    async def test_verify_valid_chain(self, db_session: Any, _verified_chain: Any) -> None:
        """Test that valid chain passes verification."""
        repo = VersionBlockRepository()

        is_valid, broken_links = await repo.verify_chain_integrity(
            db=db_session,
            spec_id="INT-001",
            spec_type="integrity",
        )

        assert is_valid is True
        assert broken_links == []

    @pytest.mark.asyncio
    async def test_verification_updates_chain_index(self, db_session: Any, _verified_chain: Any) -> None:
        """Test that verification updates chain index metadata."""
        repo = VersionBlockRepository()

        await repo.verify_chain_integrity(
            db=db_session,
            spec_id="INT-001",
            spec_type="integrity",
        )

        await db_session.flush()

        chain = await repo.get_chain_index(db_session, "INT-001", "integrity")
        assert chain is not None
        assert chain.is_valid is True
        assert chain.last_verified_at is not None


class TestMultipleChains:
    """Test managing multiple independent chains."""

    @pytest.mark.asyncio
    async def test_separate_chains_independent(self, db_session: Any) -> None:
        """Test that separate chains don't interfere."""
        project = Project(id="multi-chain-project", name="Multi Chain")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        # Create two separate chains
        await repo.create_genesis_block(
            db=db_session,
            spec_id="CHAIN-A",
            spec_type="type-a",
            project_id="multi-chain-project",
            content={"chain": "A", "version": 1},
            author_id="user-1",
        )

        await repo.create_genesis_block(
            db=db_session,
            spec_id="CHAIN-B",
            spec_type="type-b",
            project_id="multi-chain-project",
            content={"chain": "B", "version": 1},
            author_id="user-2",
        )

        # Add block to chain A only
        await repo.add_block(
            db=db_session,
            spec_id="CHAIN-A",
            spec_type="type-a",
            project_id="multi-chain-project",
            content={"chain": "A", "version": 2},
            author_id="user-1",
            change_type="update",
            change_summary="A update",
        )

        await db_session.flush()

        # Check chains are independent
        chain_a = await repo.get_chain_index(db_session, "CHAIN-A", "type-a")
        chain_b = await repo.get_chain_index(db_session, "CHAIN-B", "type-b")
        assert chain_a is not None
        assert chain_b is not None
        assert chain_a.chain_length == COUNT_TWO
        assert chain_b.chain_length == 1

    @pytest.mark.asyncio
    async def test_same_spec_id_different_types(self, db_session: Any) -> None:
        """Test that same spec_id with different types creates separate chains."""
        project = Project(id="same-id-project", name="Same ID")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        # Same spec_id but different spec_types
        await repo.create_genesis_block(
            db=db_session,
            spec_id="SPEC-001",
            spec_type="requirement",
            project_id="same-id-project",
            content={"type": "requirement"},
            author_id="user-1",
        )

        await repo.create_genesis_block(
            db=db_session,
            spec_id="SPEC-001",
            spec_type="test",
            project_id="same-id-project",
            content={"type": "test"},
            author_id="user-1",
        )

        await db_session.flush()

        req_chain = await repo.get_chain_index(db_session, "SPEC-001", "requirement")
        test_chain = await repo.get_chain_index(db_session, "SPEC-001", "test")

        assert req_chain is not None
        assert test_chain is not None
        assert req_chain.id != test_chain.id


class TestVersionBlockMetadata:
    """Test version block metadata and hashing."""

    @pytest.mark.asyncio
    async def test_author_tracking(self, db_session: Any) -> None:
        """Test that author IDs are tracked correctly."""
        project = Project(id="author-test-project", name="Author Test")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        genesis = await repo.create_genesis_block(
            db=db_session,
            spec_id="AUTH-001",
            spec_type="authored",
            project_id="author-test-project",
            content={"v": 1},
            author_id="alice",
        )

        update = await repo.add_block(
            db=db_session,
            spec_id="AUTH-001",
            spec_type="authored",
            project_id="author-test-project",
            content={"v": 2},
            author_id="bob",
            change_type="update",
            change_summary="Bob's update",
        )

        assert genesis.author_id == "alice"
        assert update.author_id == "bob"

    @pytest.mark.asyncio
    async def test_timestamp_ordering(self, db_session: Any) -> None:
        """Test that timestamps are properly ordered."""
        project = Project(id="time-test-project", name="Time Test")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        blocks = []
        for i in range(3):
            if i == 0:
                block = await repo.create_genesis_block(
                    db=db_session,
                    spec_id="TIME-001",
                    spec_type="timed",
                    project_id="time-test-project",
                    content={"v": i + 1},
                    author_id="user",
                )
            else:
                block = await repo.add_block(
                    db=db_session,
                    spec_id="TIME-001",
                    spec_type="timed",
                    project_id="time-test-project",
                    content={"v": i + 1},
                    author_id="user",
                    change_type="update",
                    change_summary=f"V{i + 1}",
                )
            blocks.append(block)

        # Each timestamp should be >= the previous
        for i in range(1, len(blocks)):
            assert blocks[i].timestamp >= blocks[i - 1].timestamp

    @pytest.mark.asyncio
    async def test_null_author_allowed(self, db_session: Any) -> None:
        """Test that null author is allowed (e.g., system changes)."""
        project = Project(id="null-author-project", name="Null Author")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        block = await repo.create_genesis_block(
            db=db_session,
            spec_id="NULL-001",
            spec_type="system",
            project_id="null-author-project",
            content={"v": 1},
            author_id=None,  # No author
        )

        assert block.author_id is None
        # Block should still have valid hash
        assert len(block.block_id) == 64


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_empty_chain_retrieval(self, db_session: Any) -> None:
        """Test retrieving chain that doesn't exist."""
        repo = VersionBlockRepository()

        chain = await repo.get_version_chain(
            db=db_session,
            spec_id="NONEXISTENT",
            spec_type="fake",
        )

        assert chain == []

    @pytest.mark.asyncio
    async def test_verify_nonexistent_chain(self, db_session: Any) -> None:
        """Test verifying chain that doesn't exist."""
        repo = VersionBlockRepository()

        is_valid, broken_links = await repo.verify_chain_integrity(
            db=db_session,
            spec_id="NONEXISTENT",
            spec_type="fake",
        )

        # Non-existent chain has nothing to verify (no broken links)
        assert is_valid is True
        assert broken_links == []

    @pytest.mark.asyncio
    async def test_large_content_hashing(self, db_session: Any) -> None:
        """Test hashing large content."""
        project = Project(id="large-content-project", name="Large Content")
        db_session.add(project)
        await db_session.flush()

        repo = VersionBlockRepository()

        # Create block with large content
        large_content = {
            "id": "LARGE-001",
            "description": "x" * 10000,
            "items": [{"id": i, "value": f"item-{i}"} for i in range(100)],
        }

        block = await repo.create_genesis_block(
            db=db_session,
            spec_id="LARGE-001",
            spec_type="large",
            project_id="large-content-project",
            content=large_content,
            author_id="user",
        )

        assert block is not None
        assert len(block.content_hash) == 64
