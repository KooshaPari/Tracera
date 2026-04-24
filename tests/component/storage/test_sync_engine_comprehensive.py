"""Comprehensive tests for SyncEngine.

Tests cover:
- Sync queue management
- Change detection
- Upload/download phases
- Conflict handling
- Retry logic
- State management
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from tests.test_constants import COUNT_FIVE
from tracertm.storage.conflict_resolver import ConflictStrategy
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    QueuedChange,
    SyncEngine,
    SyncQueue,
    SyncState,
    SyncStateManager,
    SyncStatus,
    exponential_backoff,
)


class TestChangeDetector:
    """Test change detection functionality."""

    def test_compute_hash_consistent(self) -> None:
        """Test hash computation is consistent."""
        content = "Hello, World!"
        hash1 = ChangeDetector.compute_hash(content)
        hash2 = ChangeDetector.compute_hash(content)
        assert hash1 == hash2

    def test_compute_hash_different_content(self) -> None:
        """Test different content produces different hashes."""
        hash1 = ChangeDetector.compute_hash("content1")
        hash2 = ChangeDetector.compute_hash("content2")
        assert hash1 != hash2

    def test_has_changed_no_stored_hash(self) -> None:
        """Test change detection with no stored hash."""
        assert ChangeDetector.has_changed("new content", None)

    def test_has_changed_same_content(self) -> None:
        """Test no change when content matches."""
        content = "test content"
        stored_hash = ChangeDetector.compute_hash(content)
        assert not ChangeDetector.has_changed(content, stored_hash)

    def test_has_changed_different_content(self) -> None:
        """Test change detected when content differs."""
        stored_hash = ChangeDetector.compute_hash("old content")
        assert ChangeDetector.has_changed("new content", stored_hash)

    def test_detect_changes_in_directory_empty(self, tmp_path: Any) -> None:
        """Test detection in empty directory."""
        changes = ChangeDetector.detect_changes_in_directory(tmp_path, {})
        assert changes == []

    def test_detect_changes_in_directory_new_file(self, tmp_path: Any) -> None:
        """Test detection of new files."""
        # Create markdown file
        md_file = tmp_path / "test.md"
        md_file.write_text("# New File")

        changes = ChangeDetector.detect_changes_in_directory(tmp_path, {})
        assert len(changes) == 1
        assert changes[0][0] == md_file

    def test_detect_changes_in_directory_modified_file(self, tmp_path: Any) -> None:
        """Test detection of modified files."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Original")
        original_hash = ChangeDetector.compute_hash("# Original")

        # Modify file
        md_file.write_text("# Modified")

        stored_hashes = {"test.md": original_hash}
        changes = ChangeDetector.detect_changes_in_directory(tmp_path, stored_hashes)
        assert len(changes) == 1

    def test_detect_changes_in_directory_unchanged_file(self, tmp_path: Any) -> None:
        """Test no detection for unchanged files."""
        md_file = tmp_path / "test.md"
        content = "# Unchanged"
        md_file.write_text(content)
        stored_hash = ChangeDetector.compute_hash(content)

        stored_hashes = {"test.md": stored_hash}
        changes = ChangeDetector.detect_changes_in_directory(tmp_path, stored_hashes)
        assert len(changes) == 0

    def test_detect_changes_in_directory_recursive(self, tmp_path: Any) -> None:
        """Test recursive directory scanning."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        md_file = subdir / "nested.md"
        md_file.write_text("# Nested")

        changes = ChangeDetector.detect_changes_in_directory(tmp_path, {})
        assert len(changes) == 1
        assert changes[0][0] == md_file

    def test_detect_changes_nonexistent_directory(self, tmp_path: Any) -> None:
        """Test handling of non-existent directory."""
        nonexistent = tmp_path / "does_not_exist"
        changes = ChangeDetector.detect_changes_in_directory(nonexistent, {})
        assert changes == []


class TestSyncQueue:
    """Test SyncQueue functionality."""

    @pytest.fixture
    def mock_db(self) -> None:
        """Create mock database connection."""
        db = Mock()
        db.engine = Mock()
        return db

    @pytest.fixture
    def sync_queue(self, mock_db: Any) -> None:
        """Create SyncQueue instance."""
        with patch.object(SyncQueue, "_ensure_tables"):
            return SyncQueue(mock_db)

    def test_enqueue_creates_entry(self, sync_queue: Any, mock_db: Any) -> None:
        """Test enqueueing a change."""
        mock_conn = MagicMock()
        mock_result = Mock()
        mock_result.lastrowid = 1
        mock_conn.__enter__.return_value.execute.return_value = mock_result
        mock_db.engine.connect.return_value = mock_conn

        queue_id = sync_queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Test"})

        assert queue_id == 1
        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_get_pending_returns_changes(self, sync_queue: Any, mock_db: Any) -> None:
        """Test getting pending changes."""
        mock_conn = MagicMock()
        # Make result iterable for the for loop in get_pending
        mock_result = [(1, "item", "item-123", "create", '{"title": "Test"}', "2024-01-01T00:00:00", 0, None)]
        mock_conn.__enter__.return_value.execute.return_value = mock_result
        mock_db.engine.connect.return_value = mock_conn

        changes = sync_queue.get_pending(limit=10)

        assert len(changes) == 1
        assert isinstance(changes[0], QueuedChange)
        assert changes[0].entity_type == EntityType.ITEM
        assert changes[0].entity_id == "item-123"

    def test_get_pending_respects_limit(self, sync_queue: Any, mock_db: Any) -> None:
        """Test limit parameter."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        sync_queue.get_pending(limit=5)

        # Verify limit was passed to query
        call_args = mock_conn.__enter__.return_value.execute.call_args
        assert 5 in call_args[0] or (5,) in call_args[0]

    def test_remove_deletes_entry(self, sync_queue: Any, mock_db: Any) -> None:
        """Test removing a queue entry."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        sync_queue.remove(1)

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_update_retry_increments_count(self, sync_queue: Any, mock_db: Any) -> None:
        """Test retry count update."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        sync_queue.update_retry(1, "Network error")

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_clear_removes_all(self, sync_queue: Any, mock_db: Any) -> None:
        """Test clearing all queue entries."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        sync_queue.clear()

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_get_count_returns_number(self, sync_queue: Any, mock_db: Any) -> None:
        """Test getting count of pending changes."""
        mock_conn = MagicMock()
        mock_result = Mock()
        mock_result.scalar.return_value = 5
        mock_conn.__enter__.return_value.execute.return_value = mock_result
        mock_db.engine.connect.return_value = mock_conn

        count = sync_queue.get_count()
        assert count == COUNT_FIVE


class TestSyncStateManager:
    """Test SyncStateManager functionality."""

    @pytest.fixture
    def mock_db(self) -> None:
        """Create mock database connection."""
        db = Mock()
        db.engine = Mock()
        return db

    @pytest.fixture
    def state_manager(self, mock_db: Any) -> None:
        """Create SyncStateManager instance."""
        return SyncStateManager(mock_db)

    def test_get_state_initial(self, state_manager: Any, mock_db: Any) -> None:
        """Test getting initial state."""
        mock_conn = MagicMock()
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_result.scalar.return_value = 0
        mock_conn.__enter__.return_value.execute.return_value = mock_result
        mock_db.engine.connect.return_value = mock_conn

        state = state_manager.get_state()

        assert isinstance(state, SyncState)
        assert state.last_sync is None
        assert state.pending_changes == 0
        assert state.status == SyncStatus.IDLE

    def test_update_last_sync(self, state_manager: Any, mock_db: Any) -> None:
        """Test updating last sync timestamp."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        state_manager.update_last_sync(timestamp)

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_update_last_sync_default_now(self, state_manager: Any, mock_db: Any) -> None:
        """Test default timestamp is now."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        datetime.now(UTC)
        state_manager.update_last_sync()
        datetime.now(UTC)

        # Verify timestamp was passed (can't check exact value)
        mock_conn.__enter__.return_value.execute.assert_called()

    def test_update_status(self, state_manager: Any, mock_db: Any) -> None:
        """Test updating sync status."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        state_manager.update_status(SyncStatus.SYNCING)

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_update_error(self, state_manager: Any, mock_db: Any) -> None:
        """Test updating error message."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        state_manager.update_error("Connection timeout")

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()

    def test_update_error_clear(self, state_manager: Any, mock_db: Any) -> None:
        """Test clearing error message."""
        mock_conn = MagicMock()
        mock_db.engine.connect.return_value = mock_conn

        state_manager.update_error(None)

        mock_conn.__enter__.return_value.execute.assert_called()
        mock_conn.__enter__.return_value.commit.assert_called_once()


class TestSyncEngine:
    """Test SyncEngine functionality."""

    @pytest.fixture
    def mock_db(self) -> None:
        """Create mock database connection."""
        db = Mock()
        db.engine = Mock()
        return db

    @pytest.fixture
    def mock_api(self) -> None:
        """Create mock API client."""
        return AsyncMock()

    @pytest.fixture
    def mock_storage(self) -> None:
        """Create mock storage manager."""
        return Mock()

    @pytest.fixture
    def sync_engine(self, mock_db: Any, mock_api: Any, mock_storage: Any) -> None:
        """Create SyncEngine instance."""
        with (
            patch.object(SyncQueue, "__init__", return_value=None),
            patch.object(SyncStateManager, "__init__", return_value=None),
        ):
            engine = SyncEngine(mock_db, mock_api, mock_storage, max_retries=3, retry_delay=0.1)
            engine.queue = Mock(spec=SyncQueue)
            engine.state_manager = Mock(spec=SyncStateManager)
            engine.change_detector = ChangeDetector()
            return engine

    @pytest.mark.asyncio
    async def test_sync_success(self, sync_engine: Any) -> None:
        """Test successful sync cycle."""
        # Mock state manager
        mock_state = SyncState(status=SyncStatus.IDLE)
        sync_engine.state_manager.get_state.return_value = mock_state

        # Mock queue
        sync_engine.queue.get_pending.return_value = []

        # Run sync
        result = await sync_engine.sync()

        assert result.success
        assert result.entities_synced >= 0

    @pytest.mark.asyncio
    async def test_sync_already_in_progress(self, sync_engine: Any) -> None:
        """Test sync prevents concurrent runs."""
        sync_engine._syncing = True

        result = await sync_engine.sync()

        assert not result.success
        assert "already in progress" in result.errors[0]

    @pytest.mark.asyncio
    async def test_sync_updates_state(self, sync_engine: Any) -> None:
        """Test sync updates state correctly."""
        mock_state = SyncState(status=SyncStatus.IDLE)
        sync_engine.state_manager.get_state.return_value = mock_state
        sync_engine.queue.get_pending.return_value = []

        await sync_engine.sync()

        # Verify state updates
        sync_engine.state_manager.update_status.assert_called()
        sync_engine.state_manager.update_last_sync.assert_called()

    @pytest.mark.asyncio
    async def test_sync_handles_error(self, sync_engine: Any) -> None:
        """Test error handling during sync."""
        sync_engine.queue.get_pending.side_effect = Exception("Database error")
        sync_engine.state_manager.get_state.return_value = SyncState()

        result = await sync_engine.sync()

        assert not result.success
        assert len(result.errors) > 0
        sync_engine.state_manager.update_status.assert_called()

    def test_queue_change(self, sync_engine: Any) -> None:
        """Test queueing a change."""
        sync_engine.queue.enqueue.return_value = 1

        queue_id = sync_engine.queue_change(EntityType.ITEM, "item-123", OperationType.UPDATE, {"title": "Updated"})

        assert queue_id == 1
        sync_engine.queue.enqueue.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_queue_empty(self, sync_engine: Any) -> None:
        """Test processing empty queue."""
        sync_engine.queue.get_pending.return_value = []

        result = await sync_engine.process_queue()

        assert result.success
        assert result.entities_synced == 0

    @pytest.mark.asyncio
    async def test_process_queue_skips_max_retries(self, sync_engine: Any) -> None:
        """Test skipping changes with too many retries."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={},
            created_at=datetime.now(),
            retry_count=10,  # Exceeds max_retries
        )
        sync_engine.queue.get_pending.return_value = [change]

        result = await sync_engine.process_queue()

        assert len(result.errors) > 0
        assert "Max retries exceeded" in result.errors[0]

    @pytest.mark.asyncio
    async def test_process_queue_successful_upload(self, sync_engine: Any) -> None:
        """Test successful change upload."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(),
            retry_count=0,
        )
        sync_engine.queue.get_pending.return_value = [change]

        with patch.object(sync_engine, "_upload_change", return_value=True):
            result = await sync_engine.process_queue()

        assert result.entities_synced == 1
        sync_engine.queue.remove.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_process_queue_failed_upload_retries(self, sync_engine: Any) -> None:
        """Test retry on failed upload."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={},
            created_at=datetime.now(),
            retry_count=0,
        )
        sync_engine.queue.get_pending.return_value = [change]

        with patch.object(sync_engine, "_upload_change", return_value=False):
            result = await sync_engine.process_queue()

        assert result.entities_synced == 0
        # Should not remove from queue
        sync_engine.queue.remove.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_change_create(self, sync_engine: Any) -> None:
        """Test uploading CREATE operation."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "New Item"},
            created_at=datetime.now(),
        )

        success = await sync_engine._upload_change(change)
        # Current implementation returns True (placeholder)
        assert success is True

    @pytest.mark.asyncio
    async def test_upload_change_update(self, sync_engine: Any) -> None:
        """Test uploading UPDATE operation."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.UPDATE,
            payload={"title": "Updated Item"},
            created_at=datetime.now(),
        )

        success = await sync_engine._upload_change(change)
        assert success is True

    @pytest.mark.asyncio
    async def test_upload_change_delete(self, sync_engine: Any) -> None:
        """Test uploading DELETE operation."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.DELETE,
            payload={},
            created_at=datetime.now(),
        )

        success = await sync_engine._upload_change(change)
        assert success is True

    @pytest.mark.asyncio
    async def test_pull_changes_empty(self, sync_engine: Any) -> None:
        """Test pulling with no remote changes."""
        result = await sync_engine.pull_changes()

        assert result.success
        assert result.entities_synced == 0

    @pytest.mark.asyncio
    async def test_pull_changes_with_timestamp(self, sync_engine: Any) -> None:
        """Test pulling changes since timestamp."""
        since = datetime.now() - timedelta(hours=1)
        result = await sync_engine.pull_changes(since=since)

        assert result.success

    def test_get_status(self, sync_engine: Any) -> None:
        """Test getting sync status."""
        mock_state = SyncState(status=SyncStatus.IDLE, pending_changes=5)
        sync_engine.state_manager.get_state.return_value = mock_state

        state = sync_engine.get_status()

        assert state.status == SyncStatus.IDLE
        assert state.pending_changes == COUNT_FIVE

    def test_is_syncing_true(self, sync_engine: Any) -> None:
        """Test syncing status check."""
        sync_engine._syncing = True
        assert sync_engine.is_syncing()

    def test_is_syncing_false(self, sync_engine: Any) -> None:
        """Test not syncing status."""
        sync_engine._syncing = False
        assert not sync_engine.is_syncing()

    @pytest.mark.asyncio
    async def test_clear_queue(self, sync_engine: Any) -> None:
        """Test clearing sync queue."""
        await sync_engine.clear_queue()
        sync_engine.queue.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_sync_state(self, sync_engine: Any) -> None:
        """Test resetting sync state."""
        await sync_engine.reset_sync_state()

        sync_engine.state_manager.update_last_sync.assert_called_once_with(None)
        sync_engine.state_manager.update_status.assert_called_once_with(SyncStatus.IDLE)
        sync_engine.state_manager.update_error.assert_called_once_with(None)

    def test_resolve_conflict_last_write_wins_local(self, sync_engine: Any) -> None:
        """Test conflict resolution with local newer."""
        local_data = {"updated_at": "2024-01-02T00:00:00"}
        remote_data = {"updated_at": "2024-01-01T00:00:00"}

        resolved = sync_engine._resolve_conflict(local_data, remote_data)
        assert resolved == local_data

    def test_resolve_conflict_last_write_wins_remote(self, sync_engine: Any) -> None:
        """Test conflict resolution with remote newer."""
        local_data = {"updated_at": "2024-01-01T00:00:00"}
        remote_data = {"updated_at": "2024-01-02T00:00:00"}

        resolved = sync_engine._resolve_conflict(local_data, remote_data)
        assert resolved == remote_data

    def test_resolve_conflict_local_wins(self, sync_engine: Any) -> None:
        """Test LOCAL_WINS strategy."""
        sync_engine.conflict_strategy = ConflictStrategy.LOCAL_WINS
        local_data = {"updated_at": "2024-01-01T00:00:00"}
        remote_data = {"updated_at": "2024-01-02T00:00:00"}

        resolved = sync_engine._resolve_conflict(local_data, remote_data)
        assert resolved == local_data

    def test_resolve_conflict_remote_wins(self, sync_engine: Any) -> None:
        """Test REMOTE_WINS strategy."""
        sync_engine.conflict_strategy = ConflictStrategy.REMOTE_WINS
        local_data = {"updated_at": "2024-01-02T00:00:00"}
        remote_data = {"updated_at": "2024-01-01T00:00:00"}

        resolved = sync_engine._resolve_conflict(local_data, remote_data)
        assert resolved == remote_data


class TestExponentialBackoff:
    """Test exponential backoff utility."""

    @pytest.mark.asyncio
    async def test_backoff_increases_exponentially(self) -> None:
        """Test backoff delay increases exponentially."""
        start = asyncio.get_event_loop().time()
        await exponential_backoff(0, initial_delay=0.01)
        delay0 = asyncio.get_event_loop().time() - start

        start = asyncio.get_event_loop().time()
        await exponential_backoff(1, initial_delay=0.01)
        delay1 = asyncio.get_event_loop().time() - start

        # Delay should roughly double
        assert delay1 > delay0

    @pytest.mark.asyncio
    async def test_backoff_respects_max_delay(self) -> None:
        """Test maximum delay cap."""
        start = asyncio.get_event_loop().time()
        await exponential_backoff(10, initial_delay=0.01, max_delay=0.05)
        elapsed = asyncio.get_event_loop().time() - start

        # Should not exceed max_delay significantly
        assert elapsed < 0.1
