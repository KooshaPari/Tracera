"""Comprehensive tests for tracertm.tui.widgets.sync_status module.

Tests SyncStatusWidget and CompactSyncStatus widgets including reactive
attributes, display updates, and time formatting.
Coverage target: 80%+ of 127 statements
"""

from datetime import datetime, timedelta

# Skip all tests if Textual not available
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE

pytest.importorskip("textual")

from tracertm.tui.widgets.sync_status import (
    CompactSyncStatus,
    SyncStatusWidget,
)


class TestSyncStatusWidgetInitialization:
    """Test SyncStatusWidget initialization and reactive attributes."""

    def test_init_default_values(self) -> None:
        """Test widget initializes with default reactive values."""
        widget = SyncStatusWidget()
        # Mock update_display to avoid query_one calls
        widget.update_display = Mock()

        assert widget.is_online is False
        assert widget.is_syncing is False
        assert widget.pending_changes == 0
        assert widget.last_sync is None
        assert widget.conflicts_count == 0
        assert widget.last_error is None

    def test_compose_creates_widgets(self) -> None:
        """Test compose method creates status line widgets."""
        widget = SyncStatusWidget()

        widgets = list(widget.compose())

        # Should have Horizontal container with 3 Static widgets
        assert len(widgets) > 0


class TestSyncStatusWidgetSetters:
    """Test setter methods for updating status."""

    def test_set_online(self) -> None:
        """Test setting online status."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.set_online(True)
        assert widget.is_online is True

        widget.set_online(False)
        assert widget.is_online is False

    def test_set_syncing(self) -> None:
        """Test setting syncing status."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.set_syncing(True)
        assert widget.is_syncing is True

        widget.set_syncing(False)
        assert widget.is_syncing is False

    def test_set_pending_changes(self) -> None:
        """Test setting pending changes count."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.set_pending_changes(5)
        assert widget.pending_changes == COUNT_FIVE

        widget.set_pending_changes(0)
        assert widget.pending_changes == 0

    def test_set_last_sync(self) -> None:
        """Test setting last sync timestamp."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()
        now = datetime.now()

        widget.set_last_sync(now)
        assert widget.last_sync == now

        widget.set_last_sync(None)
        assert widget.last_sync is None

    def test_set_conflicts(self) -> None:
        """Test setting conflicts count."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.set_conflicts(3)
        assert widget.conflicts_count == COUNT_THREE

        widget.set_conflicts(0)
        assert widget.conflicts_count == 0

    def test_set_error(self) -> None:
        """Test setting error message."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.set_error("Connection failed")
        assert widget.last_error == "Connection failed"

        widget.set_error(None)
        assert widget.last_error is None


class TestSyncStatusWidgetWatchers:
    """Test reactive attribute watchers."""

    def test_watch_is_online(self) -> None:
        """Test is_online watcher triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.watch_is_online(True)

        widget.update_display.assert_called_once()

    def test_watch_is_syncing(self) -> None:
        """Test is_syncing watcher triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.watch_is_syncing(True)

        widget.update_display.assert_called_once()

    def test_watch_pending_changes(self) -> None:
        """Test pending_changes watcher triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.watch_pending_changes(5)

        widget.update_display.assert_called_once()

    def test_watch_last_sync(self) -> None:
        """Test last_sync watcher triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.watch_last_sync(datetime.now())

        widget.update_display.assert_called_once()

    def test_watch_conflicts_count(self) -> None:
        """Test conflicts_count watcher triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.watch_conflicts_count(2)

        widget.update_display.assert_called_once()

    def test_watch_last_error(self) -> None:
        """Test last_error watcher triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()

        widget.watch_last_error("Error message")

        widget.update_display.assert_called_once()


class TestSyncStatusWidgetDisplay:
    """Test display update logic."""

    def test_update_display_syncing(self) -> None:
        """Test display when syncing."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()  # Mock initially to avoid errors
        widget.is_syncing = True

        mock_connection = MagicMock()
        mock_sync = MagicMock()
        mock_conflict = MagicMock()

        # Return appropriate mock based on selector ID
        def mock_query_one(selector: Any, *args: Any) -> None:
            if "connection-status" in selector:
                return mock_connection
            if "sync-info" in selector:
                return mock_sync
            if "conflict-info" in selector:
                return mock_conflict
            return MagicMock()

        widget.query_one = Mock(side_effect=mock_query_one)

        # Now call the real update_display
        widget.update_display = SyncStatusWidget.update_display.__get__(widget, SyncStatusWidget)
        widget.update_display()

        # Should show syncing status
        mock_connection.update.assert_called()
        assert "Syncing" in str(mock_connection.update.call_args)

    def test_update_display_online(self) -> None:
        """Test display when online."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()
        widget.is_online = True
        widget.is_syncing = False
        widget.last_error = None

        mock_connection = MagicMock()
        mock_sync = MagicMock()
        mock_conflict = MagicMock()

        def mock_query_one(selector: Any, *args: Any) -> None:
            if "connection-status" in selector:
                return mock_connection
            if "sync-info" in selector:
                return mock_sync
            if "conflict-info" in selector:
                return mock_conflict
            return MagicMock()

        widget.query_one = Mock(side_effect=mock_query_one)

        widget.update_display = SyncStatusWidget.update_display.__get__(widget, SyncStatusWidget)
        widget.update_display()

        # Should show online status
        mock_connection.update.assert_called()
        assert "Online" in str(mock_connection.update.call_args)

    def test_update_display_offline(self) -> None:
        """Test display when offline."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()
        widget.is_online = False
        widget.is_syncing = False
        widget.last_error = None

        mock_connection = MagicMock()
        mock_sync = MagicMock()
        mock_conflict = MagicMock()

        def mock_query_one(selector: Any, *args: Any) -> None:
            if "connection-status" in selector:
                return mock_connection
            if "sync-info" in selector:
                return mock_sync
            if "conflict-info" in selector:
                return mock_conflict
            return MagicMock()

        widget.query_one = Mock(side_effect=mock_query_one)

        widget.update_display = SyncStatusWidget.update_display.__get__(widget, SyncStatusWidget)
        widget.update_display()

        # Should show offline status
        mock_connection.update.assert_called()
        assert "Offline" in str(mock_connection.update.call_args)

    def test_update_display_with_error(self) -> None:
        """Test display when error present."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()
        widget.last_error = "Connection timeout"
        widget.is_syncing = False

        mock_connection = MagicMock()
        mock_sync = MagicMock()
        mock_conflict = MagicMock()

        def mock_query_one(selector: Any, *args: Any) -> None:
            if "connection-status" in selector:
                return mock_connection
            if "sync-info" in selector:
                return mock_sync
            if "conflict-info" in selector:
                return mock_conflict
            return MagicMock()

        widget.query_one = Mock(side_effect=mock_query_one)

        widget.update_display = SyncStatusWidget.update_display.__get__(widget, SyncStatusWidget)
        widget.update_display()

        # Should show error
        mock_connection.update.assert_called()
        assert "Error" in str(mock_connection.update.call_args)

    def test_update_display_pending_changes(self) -> None:
        """Test display with pending changes."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()
        widget.pending_changes = 5

        mock_connection = MagicMock()
        mock_sync = MagicMock()
        mock_conflict = MagicMock()

        def mock_query_one(selector: Any, *args: Any) -> None:
            if "connection-status" in selector:
                return mock_connection
            if "sync-info" in selector:
                return mock_sync
            if "conflict-info" in selector:
                return mock_conflict
            return MagicMock()

        widget.query_one = Mock(side_effect=mock_query_one)

        widget.update_display = SyncStatusWidget.update_display.__get__(widget, SyncStatusWidget)
        widget.update_display()

        # Should show pending count
        mock_sync.update.assert_called()
        assert "5" in str(mock_sync.update.call_args)
        assert "pending" in str(mock_sync.update.call_args)

    def test_update_display_with_conflicts(self) -> None:
        """Test display with conflicts."""
        widget = SyncStatusWidget()
        widget.update_display = Mock()
        widget.conflicts_count = 3

        mock_connection = MagicMock()
        mock_sync = MagicMock()
        mock_conflict = MagicMock()

        def mock_query_one(selector: Any, *args: Any) -> None:
            if "connection-status" in selector:
                return mock_connection
            if "sync-info" in selector:
                return mock_sync
            if "conflict-info" in selector:
                return mock_conflict
            return MagicMock()

        widget.query_one = Mock(side_effect=mock_query_one)

        widget.update_display = SyncStatusWidget.update_display.__get__(widget, SyncStatusWidget)
        widget.update_display()

        # Should show conflict count
        mock_conflict.update.assert_called()
        assert "3" in str(mock_conflict.update.call_args)
        assert "conflict" in str(mock_conflict.update.call_args)


class TestSyncStatusTimeFormatting:
    """Test time formatting functionality."""

    def test_format_time_ago_just_now(self) -> None:
        """Test formatting time less than 1 minute ago."""
        widget = SyncStatusWidget()
        now = datetime.now()

        result = widget._format_time_ago(now)

        assert result == "just now"

    def test_format_time_ago_minutes(self) -> None:
        """Test formatting time in minutes."""
        widget = SyncStatusWidget()
        past = datetime.now() - timedelta(minutes=5)

        result = widget._format_time_ago(past)

        assert result == "5 minutes ago"

    def test_format_time_ago_one_minute(self) -> None:
        """Test formatting exactly 1 minute (singular)."""
        widget = SyncStatusWidget()
        past = datetime.now() - timedelta(minutes=1)

        result = widget._format_time_ago(past)

        assert result == "1 minute ago"

    def test_format_time_ago_hours(self) -> None:
        """Test formatting time in hours."""
        widget = SyncStatusWidget()
        past = datetime.now() - timedelta(hours=2)

        result = widget._format_time_ago(past)

        assert result == "2 hours ago"

    def test_format_time_ago_days(self) -> None:
        """Test formatting time in days."""
        widget = SyncStatusWidget()
        past = datetime.now() - timedelta(days=3)

        result = widget._format_time_ago(past)

        assert result == "3 days ago"


class TestCompactSyncStatus:
    """Test CompactSyncStatus widget."""

    def test_init_default_values(self) -> None:
        """Test compact widget initializes with defaults."""
        widget = CompactSyncStatus()

        assert widget.is_online is False
        assert widget.is_syncing is False
        assert widget.pending_changes == 0
        assert widget.conflicts_count == 0

    def test_render_syncing(self) -> None:
        """Test render when syncing."""
        widget = CompactSyncStatus()
        widget.is_syncing = True

        result = widget.render()

        assert "⟳" in result

    def test_render_online(self) -> None:
        """Test render when online."""
        widget = CompactSyncStatus()
        widget.is_online = True
        widget.is_syncing = False

        result = widget.render()

        assert "●" in result

    def test_render_offline(self) -> None:
        """Test render when offline."""
        widget = CompactSyncStatus()
        widget.is_online = False
        widget.is_syncing = False

        result = widget.render()

        # Should show offline indicator
        assert isinstance(result, str)

    def test_render_with_pending_changes(self) -> None:
        """Test render with pending changes."""
        widget = CompactSyncStatus()
        widget.pending_changes = 5

        result = widget.render()

        assert "5" in result
        assert "pending" in result

    def test_render_with_conflicts(self) -> None:
        """Test render with conflicts."""
        widget = CompactSyncStatus()
        widget.conflicts_count = 2

        result = widget.render()

        assert "⚠" in result
        assert "2" in result

    def test_set_online(self) -> None:
        """Test setting online status on compact widget."""
        widget = CompactSyncStatus()

        widget.set_online(True)
        assert widget.is_online is True

    def test_set_syncing(self) -> None:
        """Test setting syncing status on compact widget."""
        widget = CompactSyncStatus()

        widget.set_syncing(True)
        assert widget.is_syncing is True

    def test_set_pending_changes(self) -> None:
        """Test setting pending changes on compact widget."""
        widget = CompactSyncStatus()

        widget.set_pending_changes(10)
        assert widget.pending_changes == COUNT_TEN

    def test_set_conflicts(self) -> None:
        """Test setting conflicts on compact widget."""
        widget = CompactSyncStatus()

        widget.set_conflicts(5)
        assert widget.conflicts_count == COUNT_FIVE
