from typing import Any

"""Tests for file watcher auto-indexing functionality."""

import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from tracertm.storage.file_watcher import TraceFileWatcher
from tracertm.storage.local_storage import LocalStorageManager


@pytest.fixture
def temp_project() -> None:
    """Create a temporary project with .trace/ structure."""
    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        trace_path = project_path / ".trace"
        trace_path.mkdir()

        # Create subdirectories
        (trace_path / "epics").mkdir()
        (trace_path / "stories").mkdir()
        (trace_path / "tests").mkdir()
        (trace_path / "tasks").mkdir()
        (trace_path / ".meta").mkdir()

        # Create initial files
        (trace_path / "project.yaml").write_text(
            """name: test-project
description: Test project for file watcher
version: 1.0.0
""",
        )

        (trace_path / ".meta" / "links.yaml").write_text("links: []\n")

        yield project_path


@pytest.fixture
def storage() -> None:
    """Create a temporary storage manager."""
    with TemporaryDirectory() as tmpdir:
        storage = LocalStorageManager(base_dir=Path(tmpdir))
        yield storage


def test_watcher_initialization(temp_project: Any, storage: Any) -> None:
    """Test file watcher can be initialized."""
    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    assert watcher.project_path.resolve() == temp_project.resolve()
    assert watcher.trace_path.resolve() == (temp_project / ".trace").resolve()
    assert not watcher.is_running()


def test_watcher_start_stop(temp_project: Any, storage: Any) -> None:
    """Test file watcher can start and stop."""
    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    # Start watcher
    watcher.start()
    assert watcher.is_running()

    # Stop watcher
    watcher.stop()
    assert not watcher.is_running()


def test_watcher_stats(temp_project: Any, storage: Any) -> None:
    """Test file watcher statistics."""
    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    stats = watcher.get_stats()
    assert stats["events_processed"] == 0
    assert stats["events_pending"] == 0
    assert stats["last_event_time"] is None
    assert stats["changes_by_type"] == {}
    assert not stats["is_running"]

    watcher.start()
    stats = watcher.get_stats()
    assert stats["is_running"]
    watcher.stop()


def test_watcher_detects_new_item(temp_project: Any, storage: Any) -> None:
    """Test file watcher detects and indexes new items."""
    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    watcher.start()

    try:
        # Create a new epic file
        epic_path = temp_project / ".trace" / "epics" / "EPIC-001.md"
        epic_path.write_text(
            """---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: EPIC-001
type: epic
status: todo
priority: high
version: 1
---

# User Authentication

## Description

Implement user authentication system.
""",
        )

        # Wait for debounce + processing
        time.sleep(0.5)

        # Check if item was indexed
        stats = watcher.get_stats()
        assert stats["events_processed"] > 0

        # Verify item in database
        session = storage.get_session()
        try:
            from tracertm.models import Item

            # Expire all cached objects and reload from database
            session.expire_all()
            item = session.get(Item, "550e8400-e29b-41d4-a716-446655440000")
            assert item is not None
            assert item.title == "User Authentication"
            assert item.item_type == "epic"
            assert item.status == "todo"
        finally:
            session.close()

    finally:
        watcher.stop()


def test_watcher_detects_item_modification(temp_project: Any, storage: Any) -> None:
    """Test file watcher detects and updates modified items."""
    # Create initial item
    epic_path = temp_project / ".trace" / "epics" / "EPIC-001.md"
    epic_path.write_text(
        """---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: EPIC-001
type: epic
status: todo
priority: high
version: 1
---

# User Authentication

## Description

Initial description.
""",
    )

    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    watcher.start()

    try:
        # Wait for initial indexing
        time.sleep(0.5)

        # Modify the file
        epic_path.write_text(
            """---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: EPIC-001
type: epic
status: in_progress
priority: high
version: 2
---

# User Authentication

## Description

Updated description.
""",
        )

        # Wait for debounce + processing
        time.sleep(0.5)

        # Verify item was updated
        session = storage.get_session()
        try:
            from tracertm.models import Item

            # Expire all cached objects and reload from database
            session.expire_all()
            item = session.get(Item, "550e8400-e29b-41d4-a716-446655440000")
            assert item is not None
            assert item.status == "in_progress"
            assert item.description == "Updated description."
        finally:
            session.close()

    finally:
        watcher.stop()


def test_watcher_ignores_sync_yaml(temp_project: Any, storage: Any) -> None:
    """Test file watcher ignores sync.yaml (local-only file)."""
    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    watcher.start()

    try:
        # Create sync.yaml (should be ignored)
        sync_path = temp_project / ".trace" / ".meta" / "sync.yaml"
        sync_path.write_text("last_sync: 2024-11-30T10:00:00Z\n")

        # Wait for potential processing
        time.sleep(0.5)

        # Stats should show no events processed
        stats = watcher.get_stats()
        assert stats["events_processed"] == 0

    finally:
        watcher.stop()


def test_watcher_error_handling(temp_project: Any, storage: Any) -> None:
    """Test file watcher handles invalid files gracefully."""
    watcher = TraceFileWatcher(
        project_path=temp_project,
        storage=storage,
        debounce_ms=100,
    )

    watcher.start()

    try:
        # Create invalid markdown file (missing required fields)
        epic_path = temp_project / ".trace" / "epics" / "INVALID.md"
        epic_path.write_text(
            """---
type: epic
---

# Invalid Item
""",
        )

        # Wait for processing
        time.sleep(0.5)

        # Watcher should still be running (error was handled)
        assert watcher.is_running()

    finally:
        watcher.stop()


def test_watcher_with_no_trace_directory() -> None:
    """Test watcher raises error if no .trace/ directory exists."""
    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        storage = LocalStorageManager()

        with pytest.raises(ValueError, match="No .trace/ directory found"):
            TraceFileWatcher(
                project_path=project_path,
                storage=storage,
            )
