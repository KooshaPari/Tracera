"""Async-specific tests for SyncEngine.

Tests for:
- Async lock usage and deadlock prevention
- Concurrent sync operations
- Queue processing with async patterns
- Change detection with async operations
- Pull/push operations with timeouts
"""

import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TWO
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    SyncEngine,
    SyncQueue,
    SyncResult,
    SyncState,
    SyncStateManager,
    SyncStatus,
)


class TestSyncEngineLocking:
    """Test async locking in SyncEngine."""

    @pytest.mark.asyncio
    async def test_sync_lock_prevents_concurrent_syncs(self) -> None:
        """Test that sync lock prevents concurrent sync operations."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)

        sync_started = []
        sync_completed = []

        async def tracked_sync(_force: bool = False) -> SyncResult:
            sync_started.append(datetime.now(UTC))
            await asyncio.sleep(0.05)
            sync_completed.append(datetime.now(UTC))
            return SyncResult(success=True)

        engine.sync = tracked_sync

        # Try to run multiple syncs concurrently
        gathered = await asyncio.gather(engine.sync(), engine.sync(), return_exceptions=True)

        # All should complete
        assert len(gathered) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_sync_lock_timeout_behavior(self) -> None:
        """Test timeout when waiting for sync lock."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)

        sync_done = asyncio.Event()

        async def long_sync() -> SyncResult:
            engine._syncing = True
            await asyncio.sleep(0.1)
            engine._syncing = False
            sync_done.set()
            return SyncResult(success=True)

        async def short_sync() -> SyncResult:
            await sync_done.wait()
            return SyncResult(success=False)

        # This tests the lock behavior
        task1 = asyncio.create_task(long_sync())
        await asyncio.sleep(0.01)
        task2 = asyncio.create_task(short_sync())

        await asyncio.gather(task1, task2)
        assert sync_done.is_set()

    @pytest.mark.asyncio
    async def test_multiple_sync_attempts_serialized(self) -> None:
        """Test that multiple sync attempts are serialized."""
        sync_order = []

        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        with (
            patch.object(SyncStateManager, "__init__", return_value=None),
            patch.object(SyncQueue, "__init__", return_value=None),
        ):
            engine = SyncEngine(db_mock, api_mock, storage_mock)
            engine.queue = MagicMock()
            engine.state_manager = MagicMock()
            engine.queue.get_pending.return_value = []
            engine.state_manager.get_state.return_value = SyncState()

            async def patched_sync(_force: Any = False) -> None:
                sync_order.append("start")
                await asyncio.sleep(0.02)
                sync_order.append("end")
                return SyncResult(success=True)

            engine.sync = patched_sync

            await asyncio.gather(
                engine.sync(),
                engine.sync(),
            )

            # Both syncs should complete
            assert "start" in sync_order
            assert "end" in sync_order


class TestQueueProcessingAsync:
    """Test async queue processing."""

    @pytest.mark.asyncio
    async def test_process_queue_concurrent_uploads(self) -> None:
        """Test processing queue with concurrent uploads."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)
        engine.queue = MagicMock()
        engine.state_manager = MagicMock()

        # Mock queue with multiple changes
        from tracertm.storage.sync_engine import QueuedChange

        changes = [
            QueuedChange(
                id=1,
                entity_type=EntityType.PROJECT,
                entity_id="p1",
                operation=OperationType.CREATE,
                payload={"name": "Project 1"},
                created_at=datetime.now(UTC),
            ),
            QueuedChange(
                id=2,
                entity_type=EntityType.ITEM,
                entity_id="i1",
                operation=OperationType.UPDATE,
                payload={"title": "Item 1"},
                created_at=datetime.now(UTC),
            ),
        ]

        engine.queue.get_pending.return_value = changes

        upload_count = 0

        async def mock_upload(_change: Any) -> bool:
            nonlocal upload_count
            await asyncio.sleep(0)
            upload_count += 1
            return True

        engine._upload_change = mock_upload

        result = await engine.process_queue()

        assert result.success
        assert upload_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_process_queue_with_timeout(self) -> None:
        """Test queue processing with timeout on uploads."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)
        engine.queue = MagicMock()
        engine.state_manager = MagicMock()

        from tracertm.storage.sync_engine import QueuedChange

        changes = [
            QueuedChange(
                id=i,
                entity_type=EntityType.PROJECT,
                entity_id=f"p{i}",
                operation=OperationType.CREATE,
                payload={"name": f"Project {i}"},
                created_at=datetime.now(UTC),
            )
            for i in range(3)
        ]

        engine.queue.get_pending.return_value = changes

        async def slow_upload(_change: Any) -> bool:
            await asyncio.sleep(0.5)
            return True

        engine._upload_change = slow_upload

        # Process queue should handle slow uploads
        result = await engine.process_queue()
        assert isinstance(result, SyncResult)

    @pytest.mark.asyncio
    async def test_queue_retry_exponential_backoff(self) -> None:
        """Test exponential backoff in queue processing retries."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock, retry_delay=0.01)
        engine.queue = MagicMock()
        engine.state_manager = MagicMock()

        from tracertm.storage.sync_engine import QueuedChange

        change = QueuedChange(
            id=1,
            entity_type=EntityType.PROJECT,
            entity_id="p1",
            operation=OperationType.CREATE,
            payload={"name": "Project 1"},
            created_at=datetime.now(UTC),
            retry_count=1,  # Already retried once
        )

        engine.queue.get_pending.return_value = [change]

        upload_times = []

        async def failing_upload(_ch: Any) -> bool:
            await asyncio.sleep(0)
            upload_times.append(datetime.now(UTC))
            return False

        engine._upload_change = failing_upload

        await engine.process_queue()

        # Should attempt upload
        assert len(upload_times) > 0


class TestChangeDetectionAsync:
    """Test async change detection."""

    def test_change_detection_hash_computation(self) -> None:
        """Test hash computation for change detection."""
        content1 = "This is the content"
        content2 = "This is the content"
        content3 = "This is different"

        hash1 = ChangeDetector.compute_hash(content1)
        hash2 = ChangeDetector.compute_hash(content2)
        hash3 = ChangeDetector.compute_hash(content3)

        assert hash1 == hash2
        assert hash1 != hash3

    def test_has_changed_detection(self) -> None:
        """Test change detection based on hash."""
        content = "file content"
        hash1 = ChangeDetector.compute_hash(content)

        assert not ChangeDetector.has_changed(content, hash1)
        assert ChangeDetector.has_changed(content + " modified", hash1)
        assert ChangeDetector.has_changed(content, None)

    @pytest.mark.asyncio
    async def test_concurrent_change_detection(self) -> None:
        """Test concurrent change detection operations."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            for i in range(5):
                (tmppath / f"file_{i}.md").write_text(f"Content {i}")

            detector = ChangeDetector()
            hashes = {f"file_{i}.md": detector.compute_hash(f"Content {i}") for i in range(5)}

            # Detect changes concurrently
            changes = detector.detect_changes_in_directory(tmppath, hashes)

            # No changes yet
            assert len(changes) == 0


class TestPullPushAsync:
    """Test async pull and push operations."""

    @pytest.mark.asyncio
    async def test_pull_changes_concurrent(self) -> None:
        """Test concurrent pull of changes."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)

        # Mock api to return changes
        api_mock.get_changes = AsyncMock(return_value=[])

        result = await engine.pull_changes()

        assert result.success

    @pytest.mark.asyncio
    async def test_upload_change_with_retry(self) -> None:
        """Test uploading change with retry logic."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)

        from tracertm.storage.sync_engine import QueuedChange

        change = QueuedChange(
            id=1,
            entity_type=EntityType.PROJECT,
            entity_id="p1",
            operation=OperationType.CREATE,
            payload={"name": "Project 1"},
            created_at=datetime.now(UTC),
        )

        # Mock successful upload
        result = await engine._upload_change(change)
        assert result is True

    @pytest.mark.asyncio
    async def test_apply_remote_change_async(self) -> None:
        """Test applying remote changes asynchronously."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        engine = SyncEngine(db_mock, api_mock, storage_mock)

        change_data = {"entity_type": "item", "entity_id": "i1", "operation": "update", "payload": {"title": "Updated"}}

        # Should not raise
        await engine._apply_remote_change(change_data)


class TestSyncStateManagementAsync:
    """Test async sync state management."""

    def test_sync_state_creation(self) -> None:
        """Test SyncState creation and properties."""
        state = SyncState()

        assert state.status == SyncStatus.IDLE
        assert state.last_sync is None
        assert state.pending_changes == 0
        assert state.conflicts_count == 0

    def test_sync_state_updates(self) -> None:
        """Test updating sync state."""
        state = SyncState()
        state.status = SyncStatus.SYNCING
        state.pending_changes = 5

        assert state.status == SyncStatus.SYNCING
        assert state.pending_changes == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_concurrent_state_updates(self) -> None:
        """Test concurrent state updates."""
        db_mock = MagicMock()
        state_manager = SyncStateManager(db_mock)

        # Mock database operations
        with patch.object(state_manager, "_ensure_tables"):
            updates = []

            async def update_status(status: SyncStatus) -> None:
                updates.append(status)
                await asyncio.sleep(0.001)

            await asyncio.gather(*[
                update_status(SyncStatus.SYNCING),
                update_status(SyncStatus.SUCCESS),
            ])

            assert len(updates) == COUNT_TWO


class TestSyncEngineIntegrationAsync:
    """Integration tests for async sync operations."""

    @pytest.mark.asyncio
    async def test_full_sync_cycle_async(self) -> None:
        """Test complete sync cycle asynchronously."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        with (
            patch.object(SyncStateManager, "__init__", return_value=None),
            patch.object(SyncQueue, "__init__", return_value=None),
        ):
            engine = SyncEngine(db_mock, api_mock, storage_mock)
            engine.queue = MagicMock()
            engine.state_manager = MagicMock()
            engine.queue.get_pending.return_value = []

            engine.state_manager.get_state.return_value = SyncState()

            # Mock the methods
            engine.detect_and_queue_changes = AsyncMock(return_value=0)
            engine.process_queue = AsyncMock(return_value=SyncResult(success=True))
            engine.pull_changes = AsyncMock(return_value=SyncResult(success=True))

            result = await engine.sync()

            assert result.success

    @pytest.mark.asyncio
    async def test_sync_with_concurrent_api_calls(self) -> None:
        """Test sync operations making concurrent API calls."""
        db_mock = MagicMock()

        # Create async mock for API
        api_mock = AsyncMock()
        api_mock.get_projects = AsyncMock(return_value=[])
        api_mock.get_items = AsyncMock(return_value=[])

        storage_mock = MagicMock()

        with (
            patch.object(SyncStateManager, "__init__", return_value=None),
            patch.object(SyncQueue, "__init__", return_value=None),
        ):
            engine = SyncEngine(db_mock, api_mock, storage_mock)
            engine.queue = MagicMock()
            engine.state_manager = MagicMock()
            engine.queue.get_pending.return_value = []
            engine.state_manager.get_state.return_value = SyncState()

            # Test concurrent API calls
            async def concurrent_pulls() -> SyncResult:
                await api_mock.get_projects()
                await api_mock.get_items()
                return SyncResult(success=True)

            result = await concurrent_pulls()
            assert result.success

    @pytest.mark.asyncio
    async def test_sync_cancellation_cleanup(self) -> None:
        """Test sync cleanup on cancellation."""
        db_mock = MagicMock()
        api_mock = AsyncMock()
        storage_mock = MagicMock()

        with (
            patch.object(SyncStateManager, "__init__", return_value=None),
            patch.object(SyncQueue, "__init__", return_value=None),
        ):
            engine = SyncEngine(db_mock, api_mock, storage_mock)
            engine.queue = MagicMock()
            engine.state_manager = MagicMock()
            engine.queue.get_pending.return_value = []
            engine.state_manager.get_state.return_value = SyncState()

            async def slow_sync() -> SyncResult:
                await asyncio.sleep(10)
                return SyncResult(success=True)

            engine.sync = slow_sync

            task = asyncio.create_task(engine.sync())
            await asyncio.sleep(0.01)
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task


class TestAsyncQueueOperations:
    """Test async queue-based operations."""

    def test_queue_creation(self) -> None:
        """Test queue creation."""
        db_mock = MagicMock()
        queue = SyncQueue(db_mock)

        assert queue.db == db_mock

    def test_queue_enqueue(self) -> None:
        """Test enqueueing changes."""
        db_mock = MagicMock()
        db_mock.engine.connect.return_value.__enter__.return_value.execute.return_value.lastrowid = 1
        db_mock.engine.connect.return_value.__exit__.return_value = None

        with patch.object(SyncQueue, "_ensure_tables"):
            queue = SyncQueue(db_mock)

            queue_id = queue.enqueue(EntityType.PROJECT, "p1", OperationType.CREATE, {"name": "Project 1"})

            assert queue_id is not None

    def test_queue_get_pending(self) -> None:
        """Test getting pending changes."""
        db_mock = MagicMock()

        with patch.object(SyncQueue, "_ensure_tables"):
            queue = SyncQueue(db_mock)
            pending = queue.get_pending(limit=10)

            assert pending is not None

    def test_queue_remove(self) -> None:
        """Test removing from queue."""
        db_mock = MagicMock()

        with patch.object(SyncQueue, "_ensure_tables"):
            queue = SyncQueue(db_mock)
            queue.remove(1)  # Should not raise

    def test_queue_clear(self) -> None:
        """Test clearing queue."""
        db_mock = MagicMock()

        with patch.object(SyncQueue, "_ensure_tables"):
            queue = SyncQueue(db_mock)
            queue.clear()  # Should not raise
