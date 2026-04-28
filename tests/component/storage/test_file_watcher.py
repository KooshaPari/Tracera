import time
from pathlib import Path
from typing import Any

import pytest

from tracertm.storage.file_watcher import TraceFileWatcher
from tracertm.storage.local_storage import LocalStorageManager


def _make_project(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    repo = tmp_path / "repo"
    repo.mkdir()
    trace_dir, _pid = mgr.init_project(repo, project_name="Proj")
    return mgr, repo, trace_dir


def test_init_raises_without_trace(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "g")
    with pytest.raises(ValueError):
        TraceFileWatcher(tmp_path / "missing", mgr)


def test_stats_and_running_flag(tmp_path: Path) -> None:
    mgr, repo, _trace_dir = _make_project(tmp_path)
    watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)
    stats = watcher.get_stats()
    assert stats["is_running"] is False


def test_debounce_process_event_updates_counters(tmp_path: Path) -> None:
    mgr, repo, trace_dir = _make_project(tmp_path)
    watcher = TraceFileWatcher(repo, mgr, debounce_ms=10)

    # create a fake markdown change
    item_file = trace_dir / "items" / "item-1.md"
    item_file.parent.mkdir(parents=True, exist_ok=True)
    item_file.write_text("# title", encoding="utf-8")

    # directly invoke debounce + process without observer thread
    watcher._debounce_event(item_file, "modified")
    time.sleep(0.05)
    stats = watcher.get_stats()
    assert stats["events_processed"] >= 1


def test_process_event_handles_deleted(tmp_path: Path) -> None:
    mgr, repo, trace_dir = _make_project(tmp_path)
    watcher = TraceFileWatcher(repo, mgr, debounce_ms=10)

    item_file = trace_dir / "items" / "gone.md"
    watcher._process_event(item_file, "deleted")  # should not raise
    stats = watcher.get_stats()
    assert stats["events_processed"] >= 0


def test_should_process_skips_hidden_and_sync(tmp_path: Path) -> None:
    mgr, repo, trace_dir = _make_project(tmp_path)
    watcher = TraceFileWatcher(repo, mgr, debounce_ms=10)
    handler = watcher._event_handler

    assert handler._should_process(trace_dir / ".meta" / "sync.yaml") is False
    assert handler._should_process(trace_dir / ".hidden" / "file.md") is False
    assert handler._should_process(trace_dir / "items" / "note.txt") is False
    assert handler._should_process(trace_dir / "items" / "ok.md") is True


def test_auto_sync_queues_when_enabled(tmp_path: Path, monkeypatch: Any) -> None:
    mgr, repo, _trace_dir = _make_project(tmp_path)
    queued = {}

    def fake_queue(entity_type: Any, entity_id: Any, operation: Any, payload: Any) -> None:
        queued["args"] = (entity_type, entity_id, operation, payload)

    monkeypatch.setattr(mgr, "queue_sync", fake_queue)
    watcher = TraceFileWatcher(repo, mgr, debounce_ms=10, auto_sync=True)
    watcher._queue_for_sync("item", "i1", "create", {"foo": "bar"})

    assert queued["args"][0:3] == ("item", "i1", "create")
