"""Tests for the Sync Engine module.

Tests basic functionality of the sync engine including:
- Change detection
- Queue management
- Sync state tracking
- Basic sync operations
"""

import hashlib
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.storage import (
    ChangeDetector,
    EntityType,
    OperationType,
    SyncEngine,
    SyncQueue,
    SyncStateManager,
    SyncStatus,
)


class TestChangeDetector:
    """Test the ChangeDetector class."""

    def test_compute_hash(self) -> None:
        """Test hash computation."""
        detector = ChangeDetector()

        content1 = "Hello, World!"
        hash1 = detector.compute_hash(content1)

        # Hash should be SHA-256 hex digest
        expected_hash = hashlib.sha256(content1.encode("utf-8")).hexdigest()
        assert hash1 == expected_hash

        # Same content = same hash
        hash2 = detector.compute_hash(content1)
        assert hash1 == hash2

        # Different content = different hash
        content2 = "Hello, World!!"
        hash3 = detector.compute_hash(content2)
        assert hash1 != hash3

    def test_has_changed(self) -> None:
        """Test change detection."""
        detector = ChangeDetector()

        content = "Some content"
        stored_hash = detector.compute_hash(content)

        # No change
        assert not detector.has_changed(content, stored_hash)

        # Content changed
        new_content = "Different content"
        assert detector.has_changed(new_content, stored_hash)

        # No stored hash = always changed
        assert detector.has_changed(content, None)

    def test_detect_changes_in_directory(self, tmp_path: Any) -> None:
        """Test directory change detection."""
        detector = ChangeDetector()

        # Create test markdown files
        md_dir = tmp_path / "epics"
        md_dir.mkdir()

        file1 = md_dir / "EPIC-001.md"
        file1.write_text("# Epic 1")

        file2 = md_dir / "EPIC-002.md"
        file2.write_text("# Epic 2")

        # No stored hashes = all files are changed
        changes = detector.detect_changes_in_directory(tmp_path, {})
        assert len(changes) == COUNT_TWO

        # With correct hashes = no changes
        stored_hashes = {
            str(Path("epics/EPIC-001.md")): detector.compute_hash("# Epic 1"),
            str(Path("epics/EPIC-002.md")): detector.compute_hash("# Epic 2"),
        }
        changes = detector.detect_changes_in_directory(tmp_path, stored_hashes)
        assert len(changes) == 0

        # Modify one file
        file1.write_text("# Epic 1 Modified")
        changes = detector.detect_changes_in_directory(tmp_path, stored_hashes)
        assert len(changes) == 1
        assert changes[0][0] == file1


class TestSyncQueue:
    """Test the SyncQueue class."""

    @pytest.fixture
    def mock_db(self) -> None:
        """Create a mock database connection."""
        db = MagicMock()
        db.engine = MagicMock()
        return db

    def test_enqueue_change(self, mock_db: Any) -> None:
        """Test enqueueing a change."""
        # Mock database connection
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.lastrowid = 1
        mock_conn.execute.return_value = mock_result
        mock_db.engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_db.engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        queue = SyncQueue(mock_db)

        # Queue a change
        queue_id = queue.enqueue(
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "New Item"},
        )

        assert queue_id == 1
        assert mock_conn.execute.called


class TestSyncStateManager:
    """Test the SyncStateManager class."""

    @pytest.fixture
    def mock_db(self) -> None:
        """Create a mock database connection."""
        db = MagicMock()
        db.engine = MagicMock()
        return db

    def test_update_status(self, mock_db: Any) -> None:
        """Test updating sync status."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_db.engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        manager = SyncStateManager(mock_db)
        manager.update_status(SyncStatus.SYNCING)

        assert mock_conn.execute.called


class TestSyncEngine:
    """Test the SyncEngine class."""

    @pytest.fixture
    def mock_db(self) -> None:
        """Create a mock database connection."""
        db = MagicMock()
        db.engine = MagicMock()

        # Mock connection for table creation
        mock_conn = MagicMock()
        db.engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        db.engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        return db

    @pytest.fixture
    def mock_api(self) -> None:
        """Create a mock API client."""
        return MagicMock()

    @pytest.fixture
    def mock_storage(self) -> None:
        """Create a mock storage manager."""
        return MagicMock()

    def test_sync_engine_initialization(self, mock_db: Any, mock_api: Any, mock_storage: Any) -> None:
        """Test sync engine initialization."""
        engine = SyncEngine(db_connection=mock_db, api_client=mock_api, storage_manager=mock_storage)

        assert engine.db == mock_db
        assert engine.api == mock_api
        assert engine.storage == mock_storage
        assert not engine._syncing
        assert engine.max_retries == COUNT_THREE

    def test_queue_change(self, mock_db: Any, mock_api: Any, mock_storage: Any) -> None:
        """Test queuing a change."""
        # Setup mock
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.lastrowid = 1
        mock_conn.execute.return_value = mock_result
        mock_db.engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_db.engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        engine = SyncEngine(db_connection=mock_db, api_client=mock_api, storage_manager=mock_storage)

        queue_id = engine.queue_change(
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.UPDATE,
            payload={"status": "done"},
        )

        assert queue_id == 1

    def test_is_syncing(self, mock_db: Any, mock_api: Any, mock_storage: Any) -> None:
        """Test syncing status check."""
        engine = SyncEngine(db_connection=mock_db, api_client=mock_api, storage_manager=mock_storage)

        assert not engine.is_syncing()

        engine._syncing = True
        assert engine.is_syncing()

    # Note: Async tests require pytest-asyncio to be installed
    # Uncomment when pytest-asyncio is available
    # @pytest.mark.asyncio
    # async def test_clear_queue(self, mock_db, mock_api, mock_storage):
    #     """Test clearing the sync queue."""
    #     mock_conn = MagicMock()
    #     mock_db.engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
    #     mock_db.engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    #
    #     engine = SyncEngine(
    #         db_connection=mock_db,
    #         api_client=mock_api,
    #         storage_manager=mock_storage
    #     )
    #
    #     await engine.clear_queue()
    #     assert mock_conn.execute.called
    #
    # @pytest.mark.asyncio
    # async def test_reset_sync_state(self, mock_db, mock_api, mock_storage):
    #     """Test resetting sync state."""
    #     mock_conn = MagicMock()
    #     mock_db.engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
    #     mock_db.engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    #
    #     engine = SyncEngine(
    #         db_connection=mock_db,
    #         api_client=mock_api,
    #         storage_manager=mock_storage
    #     )
    #
    #     await engine.reset_sync_state()
    #     # Should have called update methods
    #     assert mock_conn.execute.called


class TestEnums:
    """Test enum definitions."""

    def test_operation_type(self) -> None:
        """Test OperationType enum."""
        assert OperationType.CREATE.value == "create"
        assert OperationType.UPDATE.value == "update"
        assert OperationType.DELETE.value == "delete"

    def test_entity_type(self) -> None:
        """Test EntityType enum."""
        assert EntityType.PROJECT.value == "project"
        assert EntityType.ITEM.value == "item"
        assert EntityType.LINK.value == "link"
        assert EntityType.AGENT.value == "agent"

    def test_sync_status(self) -> None:
        """Test SyncStatus enum."""
        assert SyncStatus.IDLE.value == "idle"
        assert SyncStatus.SYNCING.value == "syncing"
        assert SyncStatus.SUCCESS.value == "success"
        assert SyncStatus.ERROR.value == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
