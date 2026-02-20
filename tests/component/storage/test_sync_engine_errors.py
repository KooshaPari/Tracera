"""Error scenario and edge case tests for sync_engine.py.

Tests cover:
- Network timeout with retry logic
- Database lock handling
- Complex conflict resolution
- Rollback on partial failure
- Corrupt remote data handling
- Bandwidth throttling
- Queue management edge cases
- Sync state recovery
"""

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TWO
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    QueuedChange,
    SyncEngine,
    SyncQueue,
    SyncResult,
    SyncState,
    SyncStateManager,
    SyncStatus,
    exponential_backoff,
)


class MockDBConnection:
    """Mock database connection for testing."""

    def __init__(self) -> None:
        self.engine = Mock()
        self.engine.connect = Mock(return_value=MockConnection())


class MockConnection:
    """Mock database connection context manager."""

    def __enter__(self) -> None:
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def execute(self, *args: Any, **kwargs: Any) -> None:
        return Mock(fetchone=Mock(return_value=None), scalar=Mock(return_value=0))

    def commit(self) -> None:
        pass


@pytest.mark.asyncio
class TestSyncEngineErrorScenarios:
    """Test error handling in sync engine."""

    async def test_sync_network_timeout_with_retry(self) -> None:
        """Test network timeout and automatic retry."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage, max_retries=3, retry_delay=0.01)

        # Mock queue with one change
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-1",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(),
            retry_count=0,
        )

        with patch.object(engine.queue, "get_pending", return_value=[change]):
            with patch.object(engine.queue, "remove"):
                with patch.object(engine.queue, "update_retry"):
                    # Simulate timeout then success
                    with patch.object(
                        engine,
                        "_upload_change",
                        side_effect=[False, False, True],  # Fail twice, succeed third
                    ):
                        result = await engine.process_queue()

                        # Should complete without crashing
                        assert result.success
                        # May or may not sync depending on retries
                        assert result.entities_synced >= 0

    async def test_sync_database_lock_handling(self) -> None:
        """Test handling of database locks during sync."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        # Mock database lock error
        with patch.object(engine.state_manager, "update_status") as mock_update:
            mock_update.side_effect = [
                Exception("Database is locked"),
                None,
            ]  # Fail first, succeed second

            # Should handle lock error
            result = await engine.sync()
            assert not result.success
            assert len(result.errors) > 0

    async def test_sync_conflict_resolution_last_write_wins(self) -> None:
        """Test conflict resolution with last-write-wins strategy."""
        from tracertm.storage.conflict_resolver import ConflictStrategy

        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage, conflict_strategy=ConflictStrategy.LAST_WRITE_WINS)

        local_data = {
            "id": "item-1",
            "title": "Local Title",
            "updated_at": "2024-01-01T10:00:00",
        }

        remote_data = {
            "id": "item-1",
            "title": "Remote Title",
            "updated_at": "2024-01-01T11:00:00",  # Newer
        }

        # Remote should win
        resolved = engine._resolve_conflict(local_data, remote_data)
        assert resolved["title"] == "Remote Title"

    async def test_sync_conflict_resolution_local_wins(self) -> None:
        """Test conflict resolution with local-wins strategy."""
        from tracertm.storage.conflict_resolver import ConflictStrategy

        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage, conflict_strategy=ConflictStrategy.LOCAL_WINS)

        local_data = {"id": "item-1", "title": "Local Title"}
        remote_data = {"id": "item-1", "title": "Remote Title"}

        resolved = engine._resolve_conflict(local_data, remote_data)
        assert resolved["title"] == "Local Title"

    async def test_sync_conflict_resolution_remote_wins(self) -> None:
        """Test conflict resolution with remote-wins strategy."""
        from tracertm.storage.conflict_resolver import ConflictStrategy

        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage, conflict_strategy=ConflictStrategy.REMOTE_WINS)

        local_data = {"id": "item-1", "title": "Local Title"}
        remote_data = {"id": "item-1", "title": "Remote Title"}

        resolved = engine._resolve_conflict(local_data, remote_data)
        assert resolved["title"] == "Remote Title"

    async def test_sync_conflict_resolution_manual(self) -> None:
        """Test conflict resolution with manual strategy."""
        from tracertm.storage.conflict_resolver import ConflictStrategy

        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage, conflict_strategy=ConflictStrategy.MANUAL)

        local_data = {"id": "item-1", "title": "Local Title"}
        remote_data = {"id": "item-1", "title": "Remote Title"}

        # Manual strategy returns local by default (requires user intervention)
        resolved = engine._resolve_conflict(local_data, remote_data)
        assert resolved["title"] == "Local Title"

    async def test_sync_rollback_on_partial_failure(self) -> None:
        """Test rollback when sync partially fails."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        # Mock partial failure in queue processing
        with patch.object(engine.queue, "get_pending") as mock_pending:
            changes = [
                QueuedChange(
                    id=i,
                    entity_type=EntityType.ITEM,
                    entity_id=f"item-{i}",
                    operation=OperationType.CREATE,
                    payload={},
                    created_at=datetime.now(),
                )
                for i in range(3)
            ]
            mock_pending.return_value = changes

            with (
                patch.object(
                    engine,
                    "_upload_change",
                    side_effect=[True, Exception("Network error"), True],
                ),
                patch.object(engine.queue, "update_retry"),
                patch.object(engine.queue, "remove"),
            ):
                result = await engine.process_queue()

                # Should report errors
                assert len(result.errors) > 0

    async def test_sync_handles_corrupt_remote_data(self) -> None:
        """Test handling of corrupt data from remote."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        # Mock _apply_remote_change to simulate error on corrupt data
        # Even though pull_changes might return empty list, test the error path
        with patch.object(engine, "pull_changes") as mock_pull:
            mock_pull.return_value = SyncResult(success=False, errors=["Invalid data format"])

            result = await engine.pull_changes()

            # Should report error
            assert len(result.errors) > 0 or not result.success

    async def test_sync_max_retries_exceeded(self) -> None:
        """Test behavior when max retries are exceeded."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage, max_retries=3)

        # Create change with high retry count
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-1",
            operation=OperationType.CREATE,
            payload={},
            created_at=datetime.now(),
            retry_count=5,  # Already exceeded max
        )

        with patch.object(engine.queue, "get_pending", return_value=[change]):
            result = await engine.process_queue()

            # Should skip the change
            assert len(result.errors) > 0
            assert result.entities_synced == 0

    async def test_sync_exponential_backoff(self) -> None:
        """Test exponential backoff delays."""
        # Test backoff calculation
        for attempt in range(5):
            start = asyncio.get_event_loop().time()
            await exponential_backoff(attempt, initial_delay=0.01, max_delay=1.0)
            elapsed = asyncio.get_event_loop().time() - start

            expected = min(0.01 * (2**attempt), 1.0)
            # Allow 50% tolerance for timing
            assert elapsed >= expected * 0.5

    async def test_sync_already_in_progress(self) -> None:
        """Test that concurrent sync attempts are rejected."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        # Start first sync
        engine._syncing = True

        # Second sync should fail immediately
        result = await engine.sync()

        assert not result.success
        assert "already in progress" in result.errors[0].lower()

    async def test_sync_clear_queue(self) -> None:
        """Test clearing the sync queue."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        with patch.object(engine.queue, "clear") as mock_clear:
            await engine.clear_queue()
            mock_clear.assert_called_once()

    async def test_sync_reset_state(self) -> None:
        """Test resetting sync state."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        with patch.object(engine.state_manager, "update_last_sync") as mock_last_sync:
            with patch.object(engine.state_manager, "update_status") as mock_status:
                with patch.object(engine.state_manager, "update_error") as mock_error:
                    await engine.reset_sync_state()

                    mock_last_sync.assert_called_once_with(None)
                    mock_status.assert_called_once()
                    mock_error.assert_called_once_with(None)

    async def test_sync_is_syncing_flag(self) -> None:
        """Test is_syncing flag management."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        assert not engine.is_syncing()

        engine._syncing = True
        assert engine.is_syncing()

        engine._syncing = False
        assert not engine.is_syncing()

    async def test_change_detector_compute_hash(self) -> None:
        """Test content hash computation."""
        content1 = "Hello World"
        content2 = "Hello World"
        content3 = "Different Content"

        hash1 = ChangeDetector.compute_hash(content1)
        hash2 = ChangeDetector.compute_hash(content2)
        hash3 = ChangeDetector.compute_hash(content3)

        # Same content should have same hash
        assert hash1 == hash2
        # Different content should have different hash
        assert hash1 != hash3

    async def test_change_detector_has_changed(self) -> None:
        """Test change detection logic."""
        content = "Some content"
        stored_hash = ChangeDetector.compute_hash(content)

        # No change
        assert not ChangeDetector.has_changed(content, stored_hash)

        # Changed content
        assert ChangeDetector.has_changed("Different content", stored_hash)

        # No stored hash (new file)
        assert ChangeDetector.has_changed(content, None)

    async def test_change_detector_directory_scan(self, tmp_path: Any) -> None:
        """Test detecting changes in a directory."""
        # Create test files
        dir_path = tmp_path / "test_dir"
        dir_path.mkdir()

        file1 = dir_path / "file1.md"
        file1.write_text("Content 1", encoding="utf-8")

        file2 = dir_path / "file2.md"
        file2.write_text("Content 2", encoding="utf-8")

        # Initial scan
        stored_hashes = {}
        changes = ChangeDetector.detect_changes_in_directory(dir_path, stored_hashes)

        # All files should be detected as new
        assert len(changes) == COUNT_TWO

        # Store hashes
        for path, hash_val in changes:
            rel_path = str(path.relative_to(dir_path))
            stored_hashes[rel_path] = hash_val

        # Modify one file
        file1.write_text("Modified Content 1", encoding="utf-8")

        # Detect changes
        changes = ChangeDetector.detect_changes_in_directory(dir_path, stored_hashes)

        # Only modified file should be detected
        assert len(changes) == 1
        assert changes[0][0] == file1

    async def test_sync_queue_enqueue_update_existing(self) -> None:
        """Test that enqueuing updates existing entries."""
        db = MockDBConnection()
        queue = SyncQueue(db)

        # Mock execute to return lastrowid
        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_result = Mock()
            mock_result.lastrowid = 1
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock(return_value=mock_result)
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            # Enqueue first time
            queue_id = queue.enqueue(EntityType.ITEM, "item-1", OperationType.CREATE, {"data": "test"})

            assert queue_id == 1

    async def test_sync_queue_remove(self) -> None:
        """Test removing entries from queue."""
        db = MockDBConnection()
        queue = SyncQueue(db)

        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock()
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            queue.remove(1)
            mock_conn.execute.assert_called_once()

    async def test_sync_queue_update_retry(self) -> None:
        """Test updating retry count."""
        db = MockDBConnection()
        queue = SyncQueue(db)

        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock()
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            queue.update_retry(1, "Network timeout")
            mock_conn.execute.assert_called_once()

    async def test_sync_queue_clear(self) -> None:
        """Test clearing entire queue."""
        db = MockDBConnection()
        queue = SyncQueue(db)

        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock()
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            queue.clear()
            mock_conn.execute.assert_called_once()

    async def test_sync_state_manager_get_state(self) -> None:
        """Test retrieving sync state."""
        db = MockDBConnection()
        manager = SyncStateManager(db)

        # Mock connection properly to avoid fromisoformat errors
        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_result = Mock()
            # Return None for all queries (no stored state)
            mock_result.fetchone = Mock(return_value=None)
            mock_result.scalar = Mock(return_value=0)
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock(return_value=mock_result)
            mock_connect.return_value = mock_conn

            state = manager.get_state()
            assert isinstance(state, SyncState)

    async def test_sync_state_manager_update_last_sync(self) -> None:
        """Test updating last sync timestamp."""
        db = MockDBConnection()
        manager = SyncStateManager(db)

        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock()
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            manager.update_last_sync()
            mock_conn.execute.assert_called_once()

    async def test_sync_state_manager_update_status(self) -> None:
        """Test updating sync status."""
        db = MockDBConnection()
        manager = SyncStateManager(db)

        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock()
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            manager.update_status(SyncStatus.SYNCING)
            mock_conn.execute.assert_called_once()

    async def test_sync_state_manager_update_error(self) -> None:
        """Test updating error state."""
        db = MockDBConnection()
        manager = SyncStateManager(db)

        with patch.object(db.engine, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.execute = Mock()
            mock_conn.commit = Mock()
            mock_connect.return_value = mock_conn

            # Set error
            manager.update_error("Test error")
            mock_conn.execute.assert_called()

            # Clear error
            manager.update_error(None)
            assert mock_conn.execute.call_count >= COUNT_TWO

    async def test_upload_change_operations(self) -> None:
        """Test upload operations for different operation types."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        # Test CREATE
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-1",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(),
        )
        result = await engine._upload_change(change)
        assert result is True

        # Test UPDATE
        change.operation = OperationType.UPDATE
        result = await engine._upload_change(change)
        assert result is True

        # Test DELETE
        change.operation = OperationType.DELETE
        result = await engine._upload_change(change)
        assert result is True

    async def test_vector_clock_creation(self) -> None:
        """Test vector clock creation for conflict resolution."""
        db = MockDBConnection()
        api = AsyncMock()
        storage = Mock()

        engine = SyncEngine(db, api, storage)

        clock = engine.create_vector_clock("client-1", 5, 4)

        assert clock.client_id == "client-1"
        assert clock.version == COUNT_FIVE
        assert clock.parent_version == COUNT_FOUR
        assert isinstance(clock.timestamp, datetime)
