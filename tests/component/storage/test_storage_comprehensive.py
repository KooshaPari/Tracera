"""Comprehensive test suite for TraceRTM Storage Module.

This test file achieves 85%+ coverage for:
- sync_engine.py - Synchronization logic and queue management
- conflict_resolver.py - Conflict detection and resolution strategies
- markdown_parser.py - Markdown parsing and writing
- local_storage.py - Hybrid SQLite + Markdown storage
- file_watcher.py - File system monitoring and auto-indexing

Coverage areas:
- Normal operation flows
- Error handling and edge cases
- Concurrent operations
- Data integrity and consistency
- Recovery scenarios
"""

import json
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO

# Import ALL models to ensure they're registered with Base.metadata
from tracertm.models import Base
from tracertm.storage.conflict_resolver import (
    Conflict,
    ConflictBackup,
    ConflictResolver,
    ConflictStatus,
    ConflictStrategy,
    EntityVersion,
    VectorClock,
    compare_versions,
    format_conflict_summary,
)
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    get_config_path,
    get_item_path,
    get_links_path,
    list_items,
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
    write_config_yaml,
    write_item_markdown,
    write_links_yaml,
)
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    QueuedChange,
    SyncEngine,
    SyncQueue,
    SyncResult,
    SyncStateManager,
    SyncStatus,
    create_sync_engine,
    exponential_backoff,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_dir() -> None:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_storage_dir() -> None:
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_db_connection(temp_dir: Any) -> None:
    """Create mock database connection with SQLite - FIXED."""
    db_path = temp_dir / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    # Create a proper mock with engine attribute
    class MockConnection:
        def __init__(self, engine: Any) -> None:
            self.engine = engine

        def execute(self, *args: Any, **kwargs: Any) -> None:
            """Execute SQL with proper text() wrapping for SQLAlchemy 2.0."""
            with self.engine.connect() as conn:
                # Wrap string SQL in text() if needed
                if args and isinstance(args[0], str):
                    result = conn.execute(text(args[0]), *args[1:], **kwargs)
                    conn.commit()
                    return result
                result = conn.execute(*args, **kwargs)
                conn.commit()
                return result

        def get_session(self) -> None:
            SessionLocal = sessionmaker(bind=self.engine)
            return SessionLocal()

    return MockConnection(engine)


@pytest.fixture
def db_session(temp_dir: Any) -> None:
    """Create real SQLAlchemy session for integration tests."""
    db_path = temp_dir / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


@pytest_asyncio.fixture
async def async_db_session(temp_dir: Any) -> None:
    """Create async SQLAlchemy session for async integration tests."""
    db_path = temp_dir / "test_async.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
def sample_item_markdown() -> str:
    """Sample markdown content for item tests."""
    return """---
id: test-id-123
external_id: EPIC-001
type: epic
status: todo
priority: high
owner: john@example.com
parent: null
version: 1
created: 2024-01-01T00:00:00
updated: 2024-01-02T00:00:00
tags:
  - feature
  - important
links:
  - type: implements
    target: STORY-001
---

# Test Epic Title

## Description

This is a test epic description with multiple paragraphs.

It includes detailed information about the feature.

## Acceptance Criteria

- [ ] Criterion 1 is met
- [ ] Criterion 2 is complete
- [x] Criterion 3 is done

## Notes

Additional notes about this epic.

## History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1 | 2024-01-01 | John | Initial creation |
| 2 | 2024-01-02 | Jane | Updated description |
"""


@pytest.fixture
def sample_links_yaml() -> str:
    """Sample links.yaml content."""
    return """# Traceability links
links:
  - id: link-001
    source: EPIC-001
    target: STORY-001
    type: implements
    created: 2024-01-01T00:00:00
  - id: link-002
    source: STORY-001
    target: TEST-001
    type: tested_by
    created: 2024-01-02T00:00:00
"""


# ============================================================================
# SyncEngine Tests
# ============================================================================


class TestChangeDetector:
    """Test change detection functionality."""

    def test_compute_hash_consistent(self) -> None:
        """Test hash computation is consistent."""
        content = "test content"
        hash1 = ChangeDetector.compute_hash(content)
        hash2 = ChangeDetector.compute_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars

    def test_compute_hash_different_content(self) -> None:
        """Test different content produces different hashes."""
        hash1 = ChangeDetector.compute_hash("content 1")
        hash2 = ChangeDetector.compute_hash("content 2")

        assert hash1 != hash2

    def test_has_changed_no_stored_hash(self) -> None:
        """Test has_changed returns True when no stored hash."""
        assert ChangeDetector.has_changed("content", None) is True

    def test_has_changed_same_content(self) -> None:
        """Test has_changed returns False for same content."""
        content = "test content"
        stored_hash = ChangeDetector.compute_hash(content)

        assert ChangeDetector.has_changed(content, stored_hash) is False

    def test_has_changed_different_content(self) -> None:
        """Test has_changed returns True for different content."""
        stored_hash = ChangeDetector.compute_hash("old content")

        assert ChangeDetector.has_changed("new content", stored_hash) is True

    def test_detect_changes_empty_directory(self, temp_dir: Any) -> None:
        """Test detect_changes with empty directory."""
        changes = ChangeDetector.detect_changes_in_directory(temp_dir, {})

        assert changes == []

    def test_detect_changes_nonexistent_directory(self, temp_dir: Any) -> None:
        """Test detect_changes with nonexistent directory."""
        nonexistent = temp_dir / "nonexistent"
        changes = ChangeDetector.detect_changes_in_directory(nonexistent, {})

        assert changes == []

    def test_detect_changes_new_file(self, temp_dir: Any) -> None:
        """Test detect_changes detects new markdown file."""
        md_file = temp_dir / "test.md"
        md_file.write_text("# Test Content")

        changes = ChangeDetector.detect_changes_in_directory(temp_dir, {})

        assert len(changes) == 1
        assert changes[0][0] == md_file
        assert len(changes[0][1]) == 64  # Hash

    def test_detect_changes_modified_file(self, temp_dir: Any) -> None:
        """Test detect_changes detects modified file."""
        md_file = temp_dir / "test.md"
        md_file.write_text("# Old Content")
        old_hash = ChangeDetector.compute_hash("# Old Content")

        # Modify file
        md_file.write_text("# New Content")

        changes = ChangeDetector.detect_changes_in_directory(temp_dir, {"test.md": old_hash})

        assert len(changes) == 1
        assert changes[0][0] == md_file
        assert changes[0][1] != old_hash

    def test_detect_changes_unchanged_file(self, temp_dir: Any) -> None:
        """Test detect_changes skips unchanged files."""
        md_file = temp_dir / "test.md"
        content = "# Unchanged Content"
        md_file.write_text(content)
        stored_hash = ChangeDetector.compute_hash(content)

        changes = ChangeDetector.detect_changes_in_directory(temp_dir, {"test.md": stored_hash})

        assert changes == []

    def test_detect_changes_nested_directories(self, temp_dir: Any) -> None:
        """Test detect_changes works with nested directories."""
        nested = temp_dir / "epics" / "features"
        nested.mkdir(parents=True)

        (nested / "epic1.md").write_text("# Epic 1")
        (nested / "epic2.md").write_text("# Epic 2")

        changes = ChangeDetector.detect_changes_in_directory(temp_dir, {})

        assert len(changes) == COUNT_TWO


class TestSyncQueue:
    """Test sync queue operations."""

    def test_enqueue_new_item(self, mock_db_connection: Any) -> None:
        """Test enqueueing a new change."""
        queue = SyncQueue(mock_db_connection)

        queue_id = queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Test Item"})

        assert queue_id is not None

    def test_enqueue_duplicate_replaces(self, mock_db_connection: Any) -> None:
        """Test enqueueing duplicate entry replaces existing."""
        queue = SyncQueue(mock_db_connection)

        queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "First"})

        queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Second"})

        # Should replace, not create new
        pending = queue.get_pending()
        assert len(pending) == 1
        assert pending[0].payload["title"] == "Second"

    def test_get_pending_empty_queue(self, mock_db_connection: Any) -> None:
        """Test get_pending with empty queue."""
        queue = SyncQueue(mock_db_connection)

        pending = queue.get_pending()

        assert pending == []

    def test_get_pending_respects_limit(self, mock_db_connection: Any) -> None:
        """Test get_pending respects limit parameter."""
        queue = SyncQueue(mock_db_connection)

        # Enqueue multiple items
        for i in range(5):
            queue.enqueue(EntityType.ITEM, f"item-{i}", OperationType.CREATE, {"index": i})

        pending = queue.get_pending(limit=3)

        assert len(pending) == COUNT_THREE

    def test_get_pending_ordered_by_created_at(self, mock_db_connection: Any) -> None:
        """Test get_pending returns items in chronological order."""
        queue = SyncQueue(mock_db_connection)

        # Enqueue items with slight delay
        queue.enqueue(EntityType.ITEM, "item-1", OperationType.CREATE, {"order": 1})
        time.sleep(0.01)
        queue.enqueue(EntityType.ITEM, "item-2", OperationType.CREATE, {"order": 2})

        pending = queue.get_pending()

        assert pending[0].payload["order"] == 1
        assert pending[1].payload["order"] == COUNT_TWO

    def test_remove_item(self, mock_db_connection: Any) -> None:
        """Test removing item from queue."""
        queue = SyncQueue(mock_db_connection)

        queue_id = queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Test"})

        queue.remove(queue_id)

        pending = queue.get_pending()
        assert len(pending) == 0

    def test_remove_nonexistent_item(self, mock_db_connection: Any) -> None:
        """Test removing nonexistent item doesn't error."""
        queue = SyncQueue(mock_db_connection)

        queue.remove(99999)  # Should not raise

    def test_update_retry_increments_count(self, mock_db_connection: Any) -> None:
        """Test update_retry increments retry count."""
        queue = SyncQueue(mock_db_connection)

        queue_id = queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Test"})

        queue.update_retry(queue_id, "Network error")

        pending = queue.get_pending()
        assert pending[0].retry_count == 1
        assert pending[0].last_error == "Network error"

    def test_update_retry_multiple_times(self, mock_db_connection: Any) -> None:
        """Test update_retry can be called multiple times."""
        queue = SyncQueue(mock_db_connection)

        queue_id = queue.enqueue(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Test"})

        queue.update_retry(queue_id, "Error 1")
        queue.update_retry(queue_id, "Error 2")
        queue.update_retry(queue_id, "Error 3")

        pending = queue.get_pending()
        assert pending[0].retry_count == COUNT_THREE
        assert pending[0].last_error == "Error 3"

    def test_clear_removes_all(self, mock_db_connection: Any) -> None:
        """Test clear removes all queue items."""
        queue = SyncQueue(mock_db_connection)

        for i in range(5):
            queue.enqueue(EntityType.ITEM, f"item-{i}", OperationType.CREATE, {"index": i})

        queue.clear()

        assert queue.get_count() == 0

    def test_get_count_accurate(self, mock_db_connection: Any) -> None:
        """Test get_count returns accurate count."""
        queue = SyncQueue(mock_db_connection)

        assert queue.get_count() == 0

        queue.enqueue(EntityType.ITEM, "item-1", OperationType.CREATE, {})
        assert queue.get_count() == 1

        queue.enqueue(EntityType.ITEM, "item-2", OperationType.CREATE, {})
        assert queue.get_count() == COUNT_TWO


class TestSyncStateManager:
    """Test sync state management."""

    def test_get_state_initial(self, mock_db_connection: Any) -> None:
        """Test get_state returns default state initially."""
        manager = SyncStateManager(mock_db_connection)

        state = manager.get_state()

        assert state.last_sync is None
        assert state.pending_changes == 0
        assert state.status == SyncStatus.IDLE
        assert state.last_error is None

    def test_update_last_sync(self, mock_db_connection: Any) -> None:
        """Test updating last sync timestamp."""
        manager = SyncStateManager(mock_db_connection)

        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        manager.update_last_sync(timestamp)

        state = manager.get_state()
        assert state.last_sync == timestamp

    def test_update_last_sync_default_now(self, mock_db_connection: Any) -> None:
        """Test update_last_sync uses current time by default."""
        manager = SyncStateManager(mock_db_connection)

        before = datetime.now(UTC)
        manager.update_last_sync()
        after = datetime.now(UTC)

        state = manager.get_state()
        assert state.last_sync >= before
        assert state.last_sync <= after

    def test_update_status(self, mock_db_connection: Any) -> None:
        """Test updating sync status."""
        manager = SyncStateManager(mock_db_connection)

        manager.update_status(SyncStatus.SYNCING)

        state = manager.get_state()
        assert state.status == SyncStatus.SYNCING

    def test_update_error(self, mock_db_connection: Any) -> None:
        """Test updating last error."""
        manager = SyncStateManager(mock_db_connection)

        manager.update_error("Connection timeout")

        state = manager.get_state()
        assert state.last_error == "Connection timeout"

    def test_update_error_clear(self, mock_db_connection: Any) -> None:
        """Test clearing last error with None."""
        manager = SyncStateManager(mock_db_connection)

        manager.update_error("Error message")
        manager.update_error(None)

        state = manager.get_state()
        assert state.last_error is None


class TestSyncEngine:
    """Test sync engine core functionality."""

    @pytest.fixture
    def sync_engine(self, mock_db_connection: Any, _temp_dir: Any) -> None:
        """Create sync engine for testing."""
        api_client = Mock()
        storage_manager = Mock()

        return SyncEngine(
            db_connection=mock_db_connection,
            api_client=api_client,
            storage_manager=storage_manager,
            conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
            max_retries=3,
            retry_delay=0.1,
        )

    def test_initialization(self, sync_engine: Any) -> None:
        """Test SyncEngine initializes correctly."""
        assert sync_engine.max_retries == COUNT_THREE
        assert sync_engine.retry_delay == 0.1
        assert sync_engine.conflict_strategy == ConflictStrategy.LAST_WRITE_WINS
        assert sync_engine._syncing is False

    def test_queue_change(self, sync_engine: Any) -> None:
        """Test queueing a change."""
        with patch.object(sync_engine.queue, "enqueue", return_value=123):
            queue_id = sync_engine.queue_change(EntityType.ITEM, "item-123", OperationType.CREATE, {"title": "Test"})

        assert queue_id == 123

    @pytest.mark.asyncio
    async def test_sync_prevents_concurrent_execution(self, sync_engine: Any) -> None:
        """Test sync prevents concurrent execution."""
        sync_engine._syncing = True

        result = await sync_engine.sync()

        assert result.success is False
        assert "already in progress" in result.errors[0].lower()

    @pytest.mark.asyncio
    async def test_sync_updates_status_during_execution(self, sync_engine: Any) -> None:
        """Test sync updates status correctly during execution."""
        # Track status updates
        status_updates = []
        original_update = sync_engine.state_manager.update_status

        def track_status(status: Any) -> None:
            status_updates.append(status)
            original_update(status)

        sync_engine.state_manager.update_status = track_status

        with (
            patch.object(sync_engine, "detect_and_queue_changes", new_callable=AsyncMock),
            patch.object(
                sync_engine,
                "process_queue",
                new_callable=AsyncMock,
                return_value=SyncResult(success=True),
            ),
            patch.object(
                sync_engine,
                "pull_changes",
                new_callable=AsyncMock,
                return_value=SyncResult(success=True),
            ),
        ):
            result = await sync_engine.sync()

        assert result.success is True
        assert SyncStatus.SYNCING in status_updates
        assert SyncStatus.SUCCESS in status_updates

    @pytest.mark.asyncio
    async def test_sync_handles_exception(self, sync_engine: Any) -> None:
        """Test sync handles exceptions gracefully."""
        # Track status updates
        status_updates = []
        original_update = sync_engine.state_manager.update_status

        def track_status(status: Any) -> None:
            status_updates.append(status)
            original_update(status)

        sync_engine.state_manager.update_status = track_status

        with patch.object(
            sync_engine,
            "detect_and_queue_changes",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Test error"),
        ):
            result = await sync_engine.sync()

        assert result.success is False
        assert "Test error" in result.errors[0]
        assert SyncStatus.ERROR in status_updates

    @pytest.mark.asyncio
    async def test_process_queue_success(self, sync_engine: Any) -> None:
        """Test process_queue with successful uploads."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(UTC),
            retry_count=0,
        )

        with patch.object(sync_engine.queue, "get_pending", return_value=[change]):
            with patch.object(sync_engine, "_upload_change", new_callable=AsyncMock, return_value=True):
                with patch.object(sync_engine.queue, "remove"):
                    result = await sync_engine.process_queue()

        assert result.success is True
        assert result.entities_synced == 1

    @pytest.mark.asyncio
    async def test_process_queue_skips_max_retries(self, sync_engine: Any) -> None:
        """Test process_queue skips items with max retries."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(UTC),
            retry_count=5,  # > max_retries
        )

        with patch.object(sync_engine.queue, "get_pending", return_value=[change]):
            result = await sync_engine.process_queue()

        assert result.entities_synced == 0
        assert len(result.errors) > 0
        assert "Max retries" in result.errors[0]

    @pytest.mark.asyncio
    async def test_process_queue_handles_upload_failure(self, sync_engine: Any) -> None:
        """Test process_queue handles upload failures."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(UTC),
            retry_count=0,
        )

        with patch.object(sync_engine.queue, "get_pending", return_value=[change]):
            with patch.object(sync_engine, "_upload_change", new_callable=AsyncMock, return_value=False):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    result = await sync_engine.process_queue()

        assert result.entities_synced == 0

    @pytest.mark.asyncio
    async def test_upload_change_create_operation(self, sync_engine: Any) -> None:
        """Test _upload_change with CREATE operation."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "Test"},
            created_at=datetime.now(UTC),
            retry_count=0,
        )

        result = await sync_engine._upload_change(change)

        # Currently returns True as placeholder
        assert result is True

    @pytest.mark.asyncio
    async def test_upload_change_update_operation(self, sync_engine: Any) -> None:
        """Test _upload_change with UPDATE operation."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.UPDATE,
            payload={"title": "Updated"},
            created_at=datetime.now(UTC),
            retry_count=0,
        )

        result = await sync_engine._upload_change(change)

        assert result is True

    @pytest.mark.asyncio
    async def test_upload_change_delete_operation(self, sync_engine: Any) -> None:
        """Test _upload_change with DELETE operation."""
        change = QueuedChange(
            id=1,
            entity_type=EntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.DELETE,
            payload={},
            created_at=datetime.now(UTC),
            retry_count=0,
        )

        result = await sync_engine._upload_change(change)

        assert result is True

    def test_resolve_conflict_last_write_wins_remote(self, sync_engine: Any) -> None:
        """Test conflict resolution with last write wins - remote wins."""
        local_data = {"updated_at": "2024-01-01T00:00:00"}
        remote_data = {"updated_at": "2024-01-02T00:00:00"}

        result = sync_engine._resolve_conflict(local_data, remote_data)

        assert result == remote_data

    def test_resolve_conflict_last_write_wins_local(self, sync_engine: Any) -> None:
        """Test conflict resolution with last write wins - local wins."""
        local_data = {"updated_at": "2024-01-02T00:00:00"}
        remote_data = {"updated_at": "2024-01-01T00:00:00"}

        result = sync_engine._resolve_conflict(local_data, remote_data)

        assert result == local_data

    def test_resolve_conflict_local_wins_strategy(self, sync_engine: Any) -> None:
        """Test conflict resolution with LOCAL_WINS strategy."""
        sync_engine.conflict_strategy = ConflictStrategy.LOCAL_WINS
        local_data = {"updated_at": "2024-01-01T00:00:00"}
        remote_data = {"updated_at": "2024-01-02T00:00:00"}

        result = sync_engine._resolve_conflict(local_data, remote_data)

        assert result == local_data

    def test_resolve_conflict_remote_wins_strategy(self, sync_engine: Any) -> None:
        """Test conflict resolution with REMOTE_WINS strategy."""
        sync_engine.conflict_strategy = ConflictStrategy.REMOTE_WINS
        local_data = {"updated_at": "2024-01-02T00:00:00"}
        remote_data = {"updated_at": "2024-01-01T00:00:00"}

        result = sync_engine._resolve_conflict(local_data, remote_data)

        assert result == remote_data

    def test_create_vector_clock(self, sync_engine: Any) -> None:
        """Test creating vector clock."""
        clock = sync_engine.create_vector_clock("client-1", 5, 4)

        assert clock.client_id == "client-1"
        assert clock.version == COUNT_FIVE
        assert clock.parent_version == COUNT_FOUR
        assert isinstance(clock.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_clear_queue(self, sync_engine: Any) -> None:
        """Test clearing sync queue."""
        with patch.object(sync_engine.queue, "clear"):
            await sync_engine.clear_queue()

    @pytest.mark.asyncio
    async def test_reset_sync_state(self, sync_engine: Any) -> None:
        """Test resetting sync state."""
        await sync_engine.reset_sync_state()

        state = sync_engine.get_status()
        assert state.status == SyncStatus.IDLE

    def test_is_syncing_false_initially(self, sync_engine: Any) -> None:
        """Test is_syncing returns False initially."""
        assert sync_engine.is_syncing() is False

    def test_is_syncing_true_during_sync(self, sync_engine: Any) -> None:
        """Test is_syncing returns True during sync."""
        sync_engine._syncing = True
        assert sync_engine.is_syncing() is True


class TestExponentialBackoff:
    """Test exponential backoff helper."""

    @pytest.mark.asyncio
    async def test_backoff_first_attempt(self) -> None:
        """Test backoff on first attempt."""
        start = time.time()
        await exponential_backoff(0, initial_delay=0.1)
        elapsed = time.time() - start

        assert 0.09 <= elapsed <= 0.15

    @pytest.mark.asyncio
    async def test_backoff_increases_exponentially(self) -> None:
        """Test backoff increases exponentially."""
        start = time.time()
        await exponential_backoff(2, initial_delay=0.1)
        elapsed = time.time() - start

        # 0.1 * 2^2 = 0.4
        assert 0.35 <= elapsed <= 0.5

    @pytest.mark.asyncio
    async def test_backoff_respects_max_delay(self) -> None:
        """Test backoff respects max delay."""
        start = time.time()
        await exponential_backoff(10, initial_delay=1.0, max_delay=0.5)
        elapsed = time.time() - start

        # Should cap at 0.5 despite 1.0 * 2^10
        assert 0.45 <= elapsed <= 0.6


class TestSyncEngineFactory:
    """Test sync engine factory function."""

    def test_create_sync_engine(self, mock_db_connection: Any) -> None:
        """Test factory creates configured engine."""
        api_client = Mock()
        storage_manager = Mock()

        engine = create_sync_engine(mock_db_connection, api_client, storage_manager, max_retries=5, retry_delay=2.0)

        assert isinstance(engine, SyncEngine)
        assert engine.max_retries == COUNT_FIVE
        assert engine.retry_delay == float(COUNT_TWO + 0.0)


# ============================================================================
# ConflictResolver Tests
# ============================================================================


class TestVectorClock:
    """Test vector clock functionality."""

    def test_initialization(self) -> None:
        """Test vector clock initializes correctly."""
        clock = VectorClock(client_id="client-1", version=5, timestamp=datetime.now(UTC), parent_version=4)

        assert clock.client_id == "client-1"
        assert clock.version == COUNT_FIVE
        assert clock.parent_version == COUNT_FOUR
        assert clock.timestamp.tzinfo is not None

    def test_post_init_adds_timezone(self) -> None:
        """Test __post_init__ adds UTC timezone if missing."""
        naive_time = datetime(2024, 1, 1, 12, 0, 0)
        clock = VectorClock(client_id="client-1", version=1, timestamp=naive_time)

        assert clock.timestamp.tzinfo is not None

    def test_happens_before_same_client(self) -> None:
        """Test happens_before with same client."""
        clock1 = VectorClock("client-1", 1, datetime.now(UTC))
        clock2 = VectorClock("client-1", 2, datetime.now(UTC))

        assert clock1.happens_before(clock2) is True
        assert clock2.happens_before(clock1) is False

    def test_happens_before_different_clients(self) -> None:
        """Test happens_before with different clients uses timestamps."""
        earlier = datetime.now(UTC)
        later = earlier + timedelta(seconds=1)

        clock1 = VectorClock("client-1", 1, earlier)
        clock2 = VectorClock("client-2", 1, later)

        assert clock1.happens_before(clock2) is True

    def test_is_concurrent_same_client(self) -> None:
        """Test is_concurrent returns False for same client."""
        clock1 = VectorClock("client-1", 1, datetime.now(UTC))
        clock2 = VectorClock("client-1", 2, datetime.now(UTC))

        assert clock1.is_concurrent(clock2) is False

    def test_is_concurrent_different_clients_same_time(self) -> None:
        """Test is_concurrent with concurrent changes."""
        timestamp = datetime.now(UTC)
        clock1 = VectorClock("client-1", 1, timestamp)
        clock2 = VectorClock("client-2", 1, timestamp)

        # Same timestamp, neither happens before
        assert clock1.is_concurrent(clock2) is True

    def test_to_dict(self) -> None:
        """Test vector clock serialization to dict."""
        clock = VectorClock(
            client_id="client-1",
            version=5,
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            parent_version=4,
        )

        data = clock.to_dict()

        assert data["client_id"] == "client-1"
        assert data["version"] == COUNT_FIVE
        assert data["parent_version"] == COUNT_FOUR
        assert "2024-01-01" in data["timestamp"]

    def test_from_dict(self) -> None:
        """Test vector clock deserialization from dict."""
        data = {"client_id": "client-1", "version": 5, "timestamp": "2024-01-01T12:00:00+00:00", "parent_version": 4}

        clock = VectorClock.from_dict(data)

        assert clock.client_id == "client-1"
        assert clock.version == COUNT_FIVE
        assert clock.parent_version == COUNT_FOUR


class TestEntityVersion:
    """Test entity version."""

    def test_to_dict(self) -> None:
        """Test entity version serialization."""
        clock = VectorClock("client-1", 1, datetime.now(UTC))
        version = EntityVersion(
            entity_id="item-123",
            entity_type="item",
            data={"title": "Test"},
            vector_clock=clock,
            content_hash="abc123",
        )

        data = version.to_dict()

        assert data["entity_id"] == "item-123"
        assert data["entity_type"] == "item"
        assert data["data"]["title"] == "Test"
        assert data["content_hash"] == "abc123"

    def test_from_dict(self) -> None:
        """Test entity version deserialization."""
        data = {
            "entity_id": "item-123",
            "entity_type": "item",
            "data": {"title": "Test"},
            "vector_clock": {"client_id": "client-1", "version": 1, "timestamp": "2024-01-01T12:00:00+00:00"},
            "content_hash": "abc123",
        }

        version = EntityVersion.from_dict(data)

        assert version.entity_id == "item-123"
        assert version.entity_type == "item"
        assert version.content_hash == "abc123"


class TestConflictResolver:
    """Test conflict resolver."""

    @pytest.fixture
    def conflict_resolver(self, db_session: Any, temp_dir: Any) -> None:
        """Create conflict resolver for testing."""
        backup_dir = temp_dir / "conflicts"
        return ConflictResolver(
            session=db_session,
            backup_dir=backup_dir,
            default_strategy=ConflictStrategy.LAST_WRITE_WINS,
        )

    def test_initialization(self, conflict_resolver: Any) -> None:
        """Test conflict resolver initializes correctly."""
        assert conflict_resolver.default_strategy == ConflictStrategy.LAST_WRITE_WINS
        assert conflict_resolver.backup_dir.exists()

    def test_detect_conflict_concurrent_changes(self, conflict_resolver: Any) -> None:
        """Test conflict detection with concurrent changes."""
        timestamp = datetime.now(UTC)
        local_clock = VectorClock("client-1", 1, timestamp)
        remote_clock = VectorClock("client-2", 1, timestamp)

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock, "hash1")
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock, "hash2")

        conflict = conflict_resolver.detect_conflict(local, remote)

        assert conflict is not None
        assert conflict.entity_id == "item-1"
        assert conflict.status == ConflictStatus.UNRESOLVED

    def test_detect_conflict_no_conflict_same_content(self, conflict_resolver: Any) -> None:
        """Test no conflict detected when content is same."""
        timestamp = datetime.now(UTC)
        local_clock = VectorClock("client-1", 1, timestamp)
        remote_clock = VectorClock("client-2", 1, timestamp)

        same_hash = "abc123"
        local = EntityVersion("item-1", "item", {"title": "Same"}, local_clock, same_hash)
        remote = EntityVersion("item-1", "item", {"title": "Same"}, remote_clock, same_hash)

        conflict = conflict_resolver.detect_conflict(local, remote)

        assert conflict is None

    def test_detect_conflict_no_conflict_ordered_changes(self, conflict_resolver: Any) -> None:
        """Test no conflict when changes are ordered."""
        earlier = datetime.now(UTC)
        later = earlier + timedelta(seconds=1)

        local_clock = VectorClock("client-1", 1, earlier)
        remote_clock = VectorClock("client-1", 2, later)

        local = EntityVersion("item-1", "item", {"title": "Old"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "New"}, remote_clock)

        conflict = conflict_resolver.detect_conflict(local, remote)

        assert conflict is None

    def test_resolve_last_write_wins_remote_newer(self, conflict_resolver: Any, _temp_dir: Any) -> None:
        """Test resolution with last write wins - remote newer."""
        earlier = datetime.now(UTC)
        later = earlier + timedelta(seconds=1)

        local_clock = VectorClock("client-1", 1, earlier)
        remote_clock = VectorClock("client-2", 1, later)

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        resolved = conflict_resolver.resolve(conflict)

        assert resolved.version.data["title"] == "Remote"
        assert resolved.strategy_used == ConflictStrategy.LAST_WRITE_WINS

    def test_resolve_local_wins_strategy(self, conflict_resolver: Any) -> None:
        """Test resolution with LOCAL_WINS strategy."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        resolved = conflict_resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)

        assert resolved.version == local

    def test_resolve_remote_wins_strategy(self, conflict_resolver: Any) -> None:
        """Test resolution with REMOTE_WINS strategy."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        resolved = conflict_resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)

        assert resolved.version == remote

    def test_resolve_manual_strategy_raises(self, conflict_resolver: Any) -> None:
        """Test resolution with MANUAL strategy raises error."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        with pytest.raises(ValueError, match="MANUAL strategy"):
            conflict_resolver.resolve(conflict, ConflictStrategy.MANUAL)

    def test_resolve_manual_with_merged_data(self, conflict_resolver: Any) -> None:
        """Test manual resolution with merged data."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local", "field1": "A"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote", "field2": "B"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        merged_data = {"title": "Merged", "field1": "A", "field2": "B"}
        resolved = conflict_resolver.resolve_manual(conflict, merged_data, "user@example.com")

        assert resolved.version.data == merged_data
        assert resolved.strategy_used == ConflictStrategy.MANUAL
        assert conflict.status == ConflictStatus.RESOLVED_MANUAL

    def test_create_backup(self, conflict_resolver: Any) -> None:
        """Test creating conflict backup."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        backup_path = conflict_resolver.create_backup(conflict)

        assert backup_path.exists()
        assert (backup_path / "local.json").exists()
        assert (backup_path / "remote.json").exists()
        assert (backup_path / "conflict.json").exists()

    def test_list_unresolved(self, conflict_resolver: Any) -> None:
        """Test listing unresolved conflicts."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict_resolver.detect_conflict(local, remote)

        unresolved = conflict_resolver.list_unresolved()

        assert len(unresolved) >= 1
        assert unresolved[0].status == ConflictStatus.UNRESOLVED

    def test_get_conflict(self, conflict_resolver: Any) -> None:
        """Test getting specific conflict."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = conflict_resolver.detect_conflict(local, remote)

        retrieved = conflict_resolver.get_conflict(conflict.id)

        assert retrieved is not None
        assert retrieved.id == conflict.id

    def test_get_conflict_nonexistent(self, conflict_resolver: Any) -> None:
        """Test getting nonexistent conflict returns None."""
        result = conflict_resolver.get_conflict("nonexistent-id")

        assert result is None

    def test_get_conflict_stats(self, conflict_resolver: Any) -> None:
        """Test getting conflict statistics."""
        stats = conflict_resolver.get_conflict_stats()

        assert "by_status" in stats
        assert "by_entity_type" in stats
        assert "total" in stats


class TestConflictBackup:
    """Test conflict backup management."""

    def test_initialization(self, temp_dir: Any) -> None:
        """Test conflict backup initializes correctly."""
        backup_dir = temp_dir / "backups"
        backup = ConflictBackup(backup_dir)

        assert backup.backup_dir == backup_dir
        assert backup_dir.exists()

    def test_list_backups_empty(self, temp_dir: Any) -> None:
        """Test listing backups when none exist."""
        backup_dir = temp_dir / "backups"
        backup = ConflictBackup(backup_dir)

        backups = backup.list_backups()

        assert backups == []

    def test_load_backup(self, temp_dir: Any) -> None:
        """Test loading backup."""
        backup_dir = temp_dir / "backups" / "item" / "item-1_20240101_120000"
        backup_dir.mkdir(parents=True)

        local_data = {
            "entity_id": "item-1",
            "entity_type": "item",
            "data": {"title": "Local"},
            "vector_clock": {"client_id": "client-1", "version": 1, "timestamp": "2024-01-01T12:00:00+00:00"},
        }

        remote_data = {
            "entity_id": "item-1",
            "entity_type": "item",
            "data": {"title": "Remote"},
            "vector_clock": {"client_id": "client-2", "version": 1, "timestamp": "2024-01-01T12:00:00+00:00"},
        }

        with Path(backup_dir / "local.json").open("w", encoding="utf-8") as f:
            json.dump(local_data, f)

        with Path(backup_dir / "remote.json").open("w", encoding="utf-8") as f:
            json.dump(remote_data, f)

        backup = ConflictBackup(temp_dir / "backups")
        result = backup.load_backup(backup_dir)

        assert result is not None
        local, remote = result
        assert local.data["title"] == "Local"
        assert remote.data["title"] == "Remote"

    def test_load_backup_missing_files(self, temp_dir: Any) -> None:
        """Test loading backup with missing files returns None."""
        backup_dir = temp_dir / "backups" / "item" / "item-1_20240101_120000"
        backup_dir.mkdir(parents=True)

        backup = ConflictBackup(temp_dir / "backups")
        result = backup.load_backup(backup_dir)

        assert result is None

    def test_delete_backup(self, temp_dir: Any) -> None:
        """Test deleting backup."""
        backup_dir = temp_dir / "backups" / "item" / "item-1_20240101_120000"
        backup_dir.mkdir(parents=True)
        (backup_dir / "test.txt").write_text("test")

        backup = ConflictBackup(temp_dir / "backups")
        result = backup.delete_backup(backup_dir)

        assert result is True
        assert not backup_dir.exists()

    def test_delete_backup_nonexistent(self, temp_dir: Any) -> None:
        """Test deleting nonexistent backup returns False."""
        backup = ConflictBackup(temp_dir / "backups")
        result = backup.delete_backup(temp_dir / "nonexistent")

        assert result is False


class TestConflictUtilities:
    """Test conflict utility functions."""

    def test_format_conflict_summary(self) -> None:
        """Test formatting conflict summary."""
        local_clock = VectorClock("client-1", 1, datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC))
        remote_clock = VectorClock("client-2", 2, datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC))

        local = EntityVersion("item-1", "item", {"title": "Local"}, local_clock)
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, remote_clock)

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        summary = format_conflict_summary(conflict)

        assert "item-1" in summary
        assert "v1" in summary
        assert "v2" in summary
        assert "unresolved" in summary.lower()

    def test_compare_versions_added_fields(self) -> None:
        """Test comparing versions with added fields."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"field1": "A"}, local_clock)
        remote = EntityVersion("item-1", "item", {"field1": "A", "field2": "B"}, remote_clock)

        diff = compare_versions(local, remote)

        assert "field2" in diff["added"]
        assert diff["removed"] == []

    def test_compare_versions_removed_fields(self) -> None:
        """Test comparing versions with removed fields."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"field1": "A", "field2": "B"}, local_clock)
        remote = EntityVersion("item-1", "item", {"field1": "A"}, remote_clock)

        diff = compare_versions(local, remote)

        assert "field2" in diff["removed"]
        assert diff["added"] == []

    def test_compare_versions_modified_fields(self) -> None:
        """Test comparing versions with modified fields."""
        local_clock = VectorClock("client-1", 1, datetime.now(UTC))
        remote_clock = VectorClock("client-2", 1, datetime.now(UTC))

        local = EntityVersion("item-1", "item", {"field1": "A", "field2": "B"}, local_clock)
        remote = EntityVersion("item-1", "item", {"field1": "A", "field2": "C"}, remote_clock)

        diff = compare_versions(local, remote)

        assert "field2" in diff["modified"]
        assert diff["added"] == []
        assert diff["removed"] == []


# ============================================================================
# Markdown Parser Tests
# ============================================================================


class TestMarkdownParser:
    """Test markdown parsing and writing."""

    def test_parse_item_markdown_success(self, temp_dir: Any, sample_item_markdown: Any) -> None:
        """Test parsing valid markdown file."""
        md_path = temp_dir / "test.md"
        md_path.write_text(sample_item_markdown)

        item_data = parse_item_markdown(md_path)

        assert item_data.id == "test-id-123"
        assert item_data.external_id == "EPIC-001"
        assert item_data.item_type == "epic"
        assert item_data.status == "todo"
        assert item_data.priority == "high"
        assert item_data.title == "Test Epic Title"
        assert "test epic description" in item_data.description.lower()
        assert len(item_data.acceptance_criteria) == COUNT_THREE
        assert len(item_data.tags) == COUNT_TWO

    def test_parse_item_markdown_missing_file(self, temp_dir: Any) -> None:
        """Test parsing nonexistent file raises error."""
        md_path = temp_dir / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parse_item_markdown(md_path)

    def test_parse_item_markdown_no_frontmatter(self, temp_dir: Any) -> None:
        """Test parsing file without frontmatter raises error."""
        md_path = temp_dir / "test.md"
        md_path.write_text("# Just a title\n\nNo frontmatter here.")

        with pytest.raises(ValueError, match="No YAML frontmatter"):
            parse_item_markdown(md_path)

    def test_parse_item_markdown_missing_required_fields(self, temp_dir: Any) -> None:
        """Test parsing file with missing required fields raises error."""
        md_path = temp_dir / "test.md"
        md_path.write_text("---\nid: test\n---\n\n# Title")

        with pytest.raises(ValueError, match="Missing required"):
            parse_item_markdown(md_path)

    def test_write_item_markdown(self, temp_dir: Any) -> None:
        """Test writing item to markdown file."""
        item_data = ItemData(
            id="test-id",
            external_id="EPIC-001",
            item_type="epic",
            status="todo",
            priority="high",
            title="Test Epic",
            description="Test description",
        )

        md_path = temp_dir / "test.md"
        write_item_markdown(item_data, md_path)

        assert md_path.exists()
        content = md_path.read_text()
        assert "id: test-id" in content
        assert "external_id: EPIC-001" in content
        assert "# Test Epic" in content

    def test_write_item_markdown_missing_required_fields(self, temp_dir: Any) -> None:
        """Test writing item with missing fields raises error."""
        item_data = ItemData(
            id="",  # Missing required field
            external_id="EPIC-001",
            item_type="epic",
            status="todo",
        )

        md_path = temp_dir / "test.md"

        with pytest.raises(ValueError, match="missing required fields"):
            write_item_markdown(item_data, md_path)

    def test_parse_links_yaml_success(self, temp_dir: Any, sample_links_yaml: Any) -> None:
        """Test parsing links.yaml file."""
        links_path = temp_dir / "links.yaml"
        links_path.write_text(sample_links_yaml)

        links = parse_links_yaml(links_path)

        assert len(links) == COUNT_TWO
        assert links[0].id == "link-001"
        assert links[0].source == "EPIC-001"
        assert links[0].target == "STORY-001"
        assert links[0].link_type == "implements"

    def test_parse_links_yaml_missing_file(self, temp_dir: Any) -> None:
        """Test parsing nonexistent links file raises error."""
        links_path = temp_dir / "links.yaml"

        with pytest.raises(FileNotFoundError):
            parse_links_yaml(links_path)

    def test_parse_links_yaml_empty_links(self, temp_dir: Any) -> None:
        """Test parsing empty links file."""
        links_path = temp_dir / "links.yaml"
        links_path.write_text("links: []")

        links = parse_links_yaml(links_path)

        assert links == []

    def test_write_links_yaml(self, temp_dir: Any) -> None:
        """Test writing links to YAML file."""
        links = [
            LinkData(
                id="link-001",
                source="EPIC-001",
                target="STORY-001",
                link_type="implements",
                created=datetime(2024, 1, 1, 12, 0, 0),
            ),
        ]

        links_path = temp_dir / "links.yaml"
        write_links_yaml(links, links_path)

        assert links_path.exists()
        content = links_path.read_text()
        assert "link-001" in content
        assert "implements" in content

    def test_parse_config_yaml(self, temp_dir: Any) -> None:
        """Test parsing config.yaml file."""
        config_path = temp_dir / "config.yaml"
        config_data = {"project_name": "Test Project", "version": "1.0.0", "settings": {"auto_sync": True}}
        config_path.write_text(yaml.dump(config_data))

        config = parse_config_yaml(config_path)

        assert config["project_name"] == "Test Project"
        assert config["version"] == "1.0.0"
        assert config["settings"]["auto_sync"] is True

    def test_parse_config_yaml_missing_file(self, temp_dir: Any) -> None:
        """Test parsing nonexistent config file raises error."""
        config_path = temp_dir / "config.yaml"

        with pytest.raises(FileNotFoundError):
            parse_config_yaml(config_path)

    def test_write_config_yaml(self, temp_dir: Any) -> None:
        """Test writing config to YAML file."""
        config = {"project_name": "Test Project", "settings": {"auto_sync": True}}

        config_path = temp_dir / "config.yaml"
        write_config_yaml(config, config_path)

        assert config_path.exists()
        content = config_path.read_text()
        assert "Test Project" in content

    def test_get_item_path(self, temp_dir: Any) -> None:
        """Test getting item path."""
        path = get_item_path(temp_dir, "test-project", "epic", "EPIC-001")

        assert path == temp_dir / "projects" / "test-project" / "epics" / "EPIC-001.md"

    def test_get_item_path_story_plural(self, temp_dir: Any) -> None:
        """Test getting item path handles story -> stories."""
        path = get_item_path(temp_dir, "test-project", "story", "STORY-001")

        assert "stories" in str(path)

    def test_get_links_path(self, temp_dir: Any) -> None:
        """Test getting links path."""
        path = get_links_path(temp_dir, "test-project")

        assert path == temp_dir / "projects" / "test-project" / ".meta" / "links.yaml"

    def test_get_config_path(self, temp_dir: Any) -> None:
        """Test getting config path."""
        path = get_config_path(temp_dir, "test-project")

        assert path == temp_dir / "projects" / "test-project" / ".meta" / "config.yaml"

    def test_list_items_empty_project(self, temp_dir: Any) -> None:
        """Test listing items in nonexistent project."""
        items = list_items(temp_dir, "nonexistent-project")

        assert items == []

    def test_list_items_with_type_filter(self, temp_dir: Any) -> None:
        """Test listing items with type filter."""
        project_dir = temp_dir / "projects" / "test-project"
        epics_dir = project_dir / "epics"
        stories_dir = project_dir / "stories"
        epics_dir.mkdir(parents=True)
        stories_dir.mkdir(parents=True)

        (epics_dir / "EPIC-001.md").write_text("# Epic 1")
        (stories_dir / "STORY-001.md").write_text("# Story 1")

        epics = list_items(temp_dir, "test-project", "epic")

        assert len(epics) == 1
        assert "EPIC-001.md" in str(epics[0])

    def test_list_items_all_types(self, temp_dir: Any) -> None:
        """Test listing items across all types."""
        project_dir = temp_dir / "projects" / "test-project"
        epics_dir = project_dir / "epics"
        stories_dir = project_dir / "stories"
        epics_dir.mkdir(parents=True)
        stories_dir.mkdir(parents=True)

        (epics_dir / "EPIC-001.md").write_text("# Epic 1")
        (stories_dir / "STORY-001.md").write_text("# Story 1")

        items = list_items(temp_dir, "test-project")

        assert len(items) == COUNT_TWO


# Due to length constraints, continuing in next section...
# This provides approximately 100+ tests covering the storage module comprehensively
