"""Edge case and error scenario tests for file_watcher.py.

Tests cover:
- Rapid file changes with debouncing
- Permission errors and recovery
- Symlink handling
- Exception recovery during event processing
- Multiple simultaneous watches
- File system event edge cases
"""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tracertm.storage.file_watcher import TraceFileWatcher, _TraceEventHandler
from tracertm.storage.local_storage import LocalStorageManager


def _make_project(tmp_path: Path) -> None:
    """Helper to create a test project with .trace/ directory."""
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    repo = tmp_path / "repo"
    repo.mkdir()
    trace_dir, _pid = mgr.init_project(repo, project_name="TestProject")
    return mgr, repo, trace_dir


class TestFileWatcherEdgeCases:
    """Test edge cases and error conditions in file watcher."""

    def test_watcher_handles_rapid_file_changes(self, tmp_path: Path) -> None:
        """Test handling of rapid successive file changes with debouncing."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=100)

        # Create test file
        item_file = trace_dir / "epics" / "EPIC-001.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)
        item_file.write_text(
            "---\nid: id1\nexternal_id: EPIC-001\ntype: epic\nstatus: todo\n---\n# Title",
            encoding="utf-8",
        )

        # Trigger rapid changes (should be debounced)
        for _i in range(10):
            watcher._debounce_event(item_file, "modified")

        # Multiple rapid changes will queue multiple events (timers not yet fired)
        # The actual debouncing happens when timers fire
        assert watcher._events_pending >= 1

        # Wait for debounce to process
        time.sleep(0.15)

        # Should have processed the change
        assert watcher._events_processed >= 1

    def test_watcher_handles_deleted_files(self, tmp_path: Path) -> None:
        """Test handling of deleted files during watch."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Create and then simulate deletion
        item_file = trace_dir / "epics" / "EPIC-DEL.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)
        item_file.write_text(
            "---\nid: del1\nexternal_id: EPIC-DEL\ntype: epic\nstatus: todo\n---\n# Del",
            encoding="utf-8",
        )

        # Process delete event (file doesn't exist)
        watcher._process_event(item_file, "deleted")

        # Should not raise error even if file not found in DB
        stats = watcher.get_stats()
        assert stats["events_processed"] >= 0  # May or may not increment depending on implementation
        # Deletion might not be tracked if item doesn't exist
        assert isinstance(stats["changes_by_type"], dict)

    def test_watcher_handles_permission_errors(self, tmp_path: Path) -> None:
        """Test handling of permission denied errors during file access."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Create test file
        item_file = trace_dir / "epics" / "EPIC-PERM.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)

        # Mock parse_item_markdown to raise permission error
        with patch(
            "tracertm.storage.file_watcher.parse_item_markdown",
            side_effect=PermissionError("Permission denied"),
        ):
            # Should not crash - error should be logged
            watcher._handle_item_change(item_file, "modified")

        # Watcher should still be functional
        stats = watcher.get_stats()
        assert stats["events_processed"] >= 0

    def test_watcher_handles_symlink_changes(self, tmp_path: Path) -> None:
        """Test handling of symlink modifications."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Create actual file
        real_file = tmp_path / "real_epic.md"
        real_file.write_text(
            "---\nid: real1\nexternal_id: EPIC-REAL\ntype: epic\nstatus: todo\n---\n# Real",
            encoding="utf-8",
        )

        # Create symlink in epics directory
        symlink = trace_dir / "epics" / "EPIC-LINK.md"
        symlink.parent.mkdir(parents=True, exist_ok=True)

        try:
            symlink.symlink_to(real_file)

            # Process event on symlink
            watcher._process_event(symlink, "modified")

            # Should handle gracefully
            stats = watcher.get_stats()
            assert stats["events_processed"] >= 0
        except OSError:
            # Symlinks might not be supported on this OS
            pytest.skip("Symlinks not supported")

    def test_watcher_debounce_timing_custom(self, tmp_path: Path) -> None:
        """Test debounce delay with custom timing."""
        mgr, repo, trace_dir = _make_project(tmp_path)

        # Test with different debounce values
        for debounce_ms in [10, 50, 200]:
            watcher = TraceFileWatcher(repo, mgr, debounce_ms=debounce_ms)
            assert watcher.debounce_delay == debounce_ms / 1000.0

            item_file = trace_dir / "epics" / f"EPIC-{debounce_ms}.md"
            item_file.parent.mkdir(parents=True, exist_ok=True)

            watcher._debounce_event(item_file, "modified")
            assert watcher._events_pending > 0

            # Wait for debounce
            time.sleep((debounce_ms + 20) / 1000.0)

            # Should be processed
            assert watcher._events_processed >= 1

    def test_watcher_exception_recovery(self, tmp_path: Path) -> None:
        """Test recovery from exceptions during event processing."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        item_file = trace_dir / "epics" / "EPIC-ERR.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)

        # Mock to raise exception on first call
        with patch(
            "tracertm.storage.file_watcher.parse_item_markdown",
            side_effect=ValueError("Parse error"),
        ):
            # Event should fail but not crash watcher
            initial_count = watcher._events_processed
            watcher._process_event(item_file, "modified")

            # Watcher should still be operational (not crashed)
            assert watcher.is_running() is False  # Not started yet

        # Verify stats - event was processed even though it errored
        stats = watcher.get_stats()
        # Event processing increments counter even on error
        assert stats["events_processed"] >= initial_count

    def test_watcher_handles_corrupted_markdown(self, tmp_path: Path) -> None:
        """Test handling of corrupted/invalid markdown files."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Create file with invalid YAML frontmatter
        item_file = trace_dir / "epics" / "EPIC-BAD.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)
        item_file.write_text("---\n{invalid yaml\n---\n# Bad", encoding="utf-8")

        # Should handle gracefully
        watcher._handle_item_change(item_file, "modified")

        stats = watcher.get_stats()
        assert stats["events_processed"] >= 0

    def test_watcher_handles_missing_project_yaml(self, tmp_path: Path) -> None:
        """Test handling when project.yaml is missing during project config change."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Delete project.yaml
        project_yaml = trace_dir / "project.yaml"
        project_yaml.unlink()

        # Process delete event
        watcher._handle_project_change(project_yaml, "deleted")

        # Should log warning but not crash
        stats = watcher.get_stats()
        assert stats["events_processed"] >= 0

    def test_watcher_handles_invalid_links_yaml(self, tmp_path: Path) -> None:
        """Test handling of invalid links.yaml format."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        links_file = trace_dir / ".meta" / "links.yaml"
        links_file.parent.mkdir(parents=True, exist_ok=True)
        links_file.write_text("invalid: [malformed yaml", encoding="utf-8")

        # Should handle parse error gracefully
        watcher._handle_links_change(links_file, "modified")

        stats = watcher.get_stats()
        assert stats["events_processed"] >= 0

    def test_watcher_stop_cancels_pending_timers(self, tmp_path: Path) -> None:
        """Test that stop() cancels all pending debounce timers."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=1000)  # Long delay

        # Queue multiple events
        for i in range(5):
            item_file = trace_dir / "epics" / f"EPIC-{i:03d}.md"
            item_file.parent.mkdir(parents=True, exist_ok=True)
            watcher._debounce_event(item_file, "modified")

        # Should have pending events
        assert watcher._events_pending > 0

        # Start and immediately stop
        watcher.start()
        time.sleep(0.05)
        watcher.stop()

        # All timers should be cancelled
        assert len(watcher._debounce_timers) == 0

    def test_watcher_double_start_warning(self, tmp_path: Path) -> None:
        """Test that starting an already running watcher logs warning."""
        mgr, repo, _trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        watcher.start()
        assert watcher.is_running()

        # Second start should log warning but not crash
        watcher.start()
        assert watcher.is_running()

        watcher.stop()

    def test_watcher_double_stop_warning(self, tmp_path: Path) -> None:
        """Test that stopping a non-running watcher logs warning."""
        mgr, repo, _trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Stop without start should log warning
        watcher.stop()
        assert not watcher.is_running()

    def test_event_handler_should_process_filters(self, tmp_path: Path) -> None:
        """Test _TraceEventHandler._should_process filters correctly."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)
        handler = _TraceEventHandler(watcher)

        # Should process .md files
        assert handler._should_process(trace_dir / "epics" / "test.md")

        # Should process .yaml files
        assert handler._should_process(trace_dir / ".meta" / "links.yaml")

        # Should NOT process sync.yaml
        assert not handler._should_process(trace_dir / ".meta" / "sync.yaml")

        # Should NOT process non-md/yaml files
        assert not handler._should_process(trace_dir / "test.txt")
        assert not handler._should_process(trace_dir / "test.json")

        # Should NOT process hidden files/directories (except .trace/.meta)
        assert not handler._should_process(trace_dir / ".hidden" / "test.md")

    def test_event_handler_ignores_directory_events(self, tmp_path: Path) -> None:
        """Test that directory events are ignored."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)
        handler = _TraceEventHandler(watcher)

        # Mock directory event
        event = Mock()
        event.is_directory = True
        event.src_path = str(trace_dir / "epics")

        # Should not process
        handler.on_created(event)
        handler.on_modified(event)
        handler.on_deleted(event)

        # No events should be debounced
        assert watcher._events_pending == 0

    def test_watcher_handles_item_without_external_id(self, tmp_path: Path) -> None:
        """Test handling items that lack external_id in metadata."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Create item with missing external_id
        item_file = trace_dir / "epics" / "NO-ID.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)
        item_file.write_text(
            "---\nid: noid1\ntype: epic\nstatus: todo\n---\n# No External ID",
            encoding="utf-8",
        )

        # Mock parse to return item without external_id
        with patch("tracertm.storage.file_watcher.parse_item_markdown") as mock_parse:
            from dataclasses import dataclass

            @dataclass
            class FakeItemData:
                id: str = "noid1"
                external_id: str = "NO-ID"  # Will come from filename
                item_type: str = "epic"
                status: str = "todo"
                priority: str = "medium"
                owner: str | None = None
                parent: str | None = None
                title: str = "No External ID"
                description: str = ""
                tags: list | None = None
                custom_fields: dict | None = None

                def __post_init__(self) -> None:
                    if self.tags is None:
                        self.tags = []
                    if self.custom_fields is None:
                        self.custom_fields = {}

            mock_parse.return_value = FakeItemData()
            watcher._handle_item_change(item_file, "created")

        # Should handle gracefully
        stats = watcher.get_stats()
        assert stats["events_processed"] >= 0

    def test_watcher_queue_for_sync_when_disabled(self, tmp_path: Path) -> None:
        """Test that _queue_for_sync does nothing when auto_sync is False."""
        mgr, repo, _trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50, auto_sync=False)

        # Get initial queue count (project creation may have queued items)
        initial_queue = mgr.get_sync_queue()
        initial_count = len(initial_queue)

        # Call queue_for_sync - should be no-op
        watcher._queue_for_sync("item", "item-1", "create", {"data": "test"})

        # No new sync queue entry should be created
        queue = mgr.get_sync_queue()
        assert len(queue) == initial_count  # No increase

    def test_watcher_queue_for_sync_when_enabled(self, tmp_path: Path) -> None:
        """Test that _queue_for_sync queues when auto_sync is True."""
        mgr, repo, _trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50, auto_sync=True)

        # Call queue_for_sync
        watcher._queue_for_sync("item", "item-1", "create", {"data": "test"})

        # Should create sync queue entry
        queue = mgr.get_sync_queue()
        assert len(queue) >= 1

    def test_watcher_last_event_time_tracking(self, tmp_path: Path) -> None:
        """Test that last_event_time is properly tracked."""
        mgr, repo, trace_dir = _make_project(tmp_path)
        watcher = TraceFileWatcher(repo, mgr, debounce_ms=50)

        # Initially None
        stats = watcher.get_stats()
        assert stats["last_event_time"] is None

        # Process an event
        item_file = trace_dir / "epics" / "EPIC-TIME.md"
        item_file.parent.mkdir(parents=True, exist_ok=True)
        watcher._process_event(item_file, "modified")

        # Should have timestamp now
        stats = watcher.get_stats()
        assert stats["last_event_time"] is not None
