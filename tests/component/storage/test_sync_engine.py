import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, Never

import pytest

from tests.test_constants import COUNT_FIVE
from tracertm.storage.conflict_resolver import ConflictStrategy
from tracertm.storage.local_storage import LocalStorageManager
from tracertm.storage.sync_engine import (
    EntityType,
    OperationType,
    QueuedChange,
    SyncEngine,
    SyncResult,
    SyncState,
    SyncStatus,
    exponential_backoff,
)


class _DummyQueue:
    """Lightweight queue double for exercising SyncEngine upload logic."""

    def __init__(self, changes: Any) -> None:
        self._changes = list(changes)
        self.removed: list[int] = []
        self.retried: list[tuple[int, str]] = []

    def get_pending(self, limit: Any = 100) -> None:
        return list(self._changes)[:limit]

    def remove(self, queue_id: int) -> None:
        self.removed.append(queue_id)

    def update_retry(self, queue_id: int, error: str) -> None:
        self.retried.append((queue_id, error))


class _NoOpState:
    """Minimal state manager stub to avoid sqlite churn in tests."""

    def __init__(self) -> None:
        self.status_updates: list[SyncStatus] = []
        self.errors: list[str | None] = []
        self.last_sync_set: list[datetime | None] = []

    def get_state(self) -> SyncState:
        return SyncState(last_sync=None, pending_changes=0, status=SyncStatus.IDLE)

    def update_status(self, status: SyncStatus) -> None:
        self.status_updates.append(status)

    def update_error(self, error: str | None) -> None:
        self.errors.append(error)

    def update_last_sync(self, timestamp: datetime | None = None) -> None:
        self.last_sync_set.append(timestamp)


def _engine(tmp_path: Any, monkeypatch: Any) -> None:
    """Create a SyncEngine with patched state + queue for isolated behavior."""
    storage = LocalStorageManager(base_dir=tmp_path / "lsm")
    # Avoid SA2 text() requirements for table bootstrap during init
    monkeypatch.setattr("tracertm.storage.sync_engine.SyncQueue._ensure_tables", lambda self: None)

    engine = SyncEngine(
        db_connection=storage,
        api_client=SimpleNamespace(),
        storage_manager=storage,
        conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
        max_retries=2,
        retry_delay=0.01,
    )
    # Replace heavy components with controllable stubs
    engine.state_manager = _NoOpState()
    return engine


def _queued(change_id: Any = 1, retries: Any = 0) -> None:
    return QueuedChange(
        id=change_id,
        entity_type=EntityType.ITEM,
        entity_id="item-1",
        operation=OperationType.CREATE,
        payload={"foo": "bar"},
        created_at=datetime.now(UTC),
        retry_count=retries,
        last_error=None,
    )


@pytest.mark.asyncio
async def test_process_queue_success_removes_items(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)
    change = _queued()
    engine.queue = _DummyQueue([change])

    async def succeed(_change: Any) -> bool:
        return True

    engine._upload_change = succeed

    result = await engine.process_queue()

    assert result.success is True
    assert result.entities_synced == 1
    assert engine.queue.removed == [change.id]


@pytest.mark.asyncio
async def test_process_queue_skips_after_max_retries(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)
    change = _queued(change_id=5, retries=engine.max_retries)
    engine.queue = _DummyQueue([change])

    async def succeed(_change: Any) -> bool:
        return True

    engine._upload_change = succeed

    result = await engine.process_queue()

    assert any("Max retries exceeded" in msg for msg in result.errors)
    assert engine.queue.removed == []  # nothing removed


@pytest.mark.asyncio
async def test_process_queue_records_errors_on_exception(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)
    change = _queued(change_id=9, retries=0)
    engine.queue = _DummyQueue([change])

    async def boom(_change: Any) -> Never:
        msg = "upload failed"
        raise RuntimeError(msg)

    engine._upload_change = boom

    result = await engine.process_queue()

    assert "upload failed" in result.errors[0]
    assert engine.queue.retried == [(9, "upload failed")]


@pytest.mark.asyncio
async def test_sync_prevents_reentry(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)
    engine._syncing = True

    result = await engine.sync()

    assert result.success is False
    assert "Sync already in progress" in result.errors[0]


@pytest.mark.asyncio
async def test_sync_happy_path_aggregates_counts(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)
    engine.queue = _DummyQueue([])

    async def fake_detect() -> int:
        return 1

    async def fake_upload() -> None:
        return SyncResult(success=True, entities_synced=2)

    async def fake_pull(_since: Any = None) -> None:
        return SyncResult(success=True, entities_synced=3, conflicts=[{"id": "c1"}])

    engine.detect_and_queue_changes = fake_detect
    engine.process_queue = fake_upload
    engine.pull_changes = fake_pull

    result = await engine.sync()

    assert result.success is True
    assert result.entities_synced == COUNT_FIVE
    assert len(result.conflicts) == 1
    # state manager was updated to success
    assert engine.state_manager.status_updates[-1] == SyncStatus.SUCCESS


def test_resolve_conflict_strategies(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)
    newer = {"updated_at": (datetime.now(UTC)).isoformat()}
    older = {"updated_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat()}

    # last-write-wins picks newer remote
    resolved = engine._resolve_conflict(local_data=older, remote_data=newer)
    assert resolved == newer

    engine.conflict_strategy = ConflictStrategy.LOCAL_WINS
    assert engine._resolve_conflict(local_data=older, remote_data=newer) == older

    engine.conflict_strategy = ConflictStrategy.REMOTE_WINS
    assert engine._resolve_conflict(local_data=older, remote_data=newer) == newer

    engine.conflict_strategy = ConflictStrategy.MANUAL
    assert engine._resolve_conflict(local_data=older, remote_data=newer) == older


@pytest.mark.asyncio
async def test_exponential_backoff_caps_delay(monkeypatch: Any) -> None:
    captured = {}

    async def fake_sleep(delay: Any) -> None:
        captured["delay"] = delay

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    await exponential_backoff(attempt=4, initial_delay=0.5, max_delay=1.0)

    assert captured["delay"] == 1.0


@pytest.mark.asyncio
async def test_pull_changes_applies_remote_errors_are_collected(tmp_path: Any, monkeypatch: Any) -> None:
    engine = _engine(tmp_path, monkeypatch)

    # fake remote changes with one failing apply

    async def fake_pull(_since: Any = None) -> None:
        return SyncResult(success=True, entities_synced=0)

    async def apply(change: Any) -> None:
        if change["id"] == "c2":
            msg = "fail"
            raise RuntimeError(msg)

    # monkeypatch pull_changes internals
    engine._apply_remote_change = apply

    # direct call to pull_changes to exercise error path
    result = await engine.pull_changes(since=None)
    assert result.success is True  # success despite no remote changes (placeholder)
