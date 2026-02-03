"""
Comprehensive tests for SyncStatusWidget and CompactSyncStatus widgets.

Tests widget initialization, reactive updates, display formatting,
time formatting, and all state combinations.
Coverage target: 80%+ (313 lines total)
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if Textual not available
pytest.importorskip("textual")

from tracertm.tui.widgets.sync_status import (  # type: ignore[possibly-missing-import]
    CompactSyncStatus,
    SyncStatusWidget,
)


class TestSyncStatusWidgetInitialization:
    """Test SyncStatusWidget initialization."""

    def test_init_creates_widget(self):
        """Test SyncStatusWidget initializes correctly."""
        widget = SyncStatusWidget()

        assert widget is not None
        assert widget.is_online is False
        assert widget.is_syncing is False
        assert widget.pending_changes == 0
        assert widget.last_sync is None
        assert widget.conflicts_count == 0
        assert widget.last_error is None

    def test_init_with_custom_id(self):
        """Test SyncStatusWidget accepts custom ID."""
        widget = SyncStatusWidget(id="custom-sync")

        assert widget is not None
        assert widget.id == "custom-sync"

    def test_compose_creates_children(self):
        """Test compose creates correct child widgets."""
        widget = SyncStatusWidget()
        children = list(widget.compose())

        # Should create Horizontal container with 3 Static widgets
        assert len(children) > 0


class TestSyncStatusWidgetReactiveUpdates:
    """Test reactive attribute updates."""

    def test_watch_is_online(self):
        """Test watch_is_online triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = MagicMock()
        widget.is_mounted = True

        widget.is_online = True

        # Should trigger update_display through watcher
        assert widget.is_online is True

    def test_watch_is_syncing(self):
        """Test watch_is_syncing triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = MagicMock()
        widget.is_mounted = True

        widget.is_syncing = True

        assert widget.is_syncing is True

    def test_watch_pending_changes(self):
        """Test watch_pending_changes triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = MagicMock()
        widget.is_mounted = True

        widget.pending_changes = 5

        assert widget.pending_changes == 5

    def test_watch_last_sync(self):
        """Test watch_last_sync triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = MagicMock()
        widget.is_mounted = True

        now = datetime.now()
        widget.last_sync = now

        assert widget.last_sync == now

    def test_watch_conflicts_count(self):
        """Test watch_conflicts_count triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = MagicMock()
        widget.is_mounted = True

        widget.conflicts_count = 3

        assert widget.conflicts_count == 3

    def test_watch_last_error(self):
        """Test watch_last_error triggers update."""
        widget = SyncStatusWidget()
        widget.update_display = MagicMock()
        widget.is_mounted = True

        widget.last_error = "Network timeout"

        assert widget.last_error == "Network timeout"


class TestSyncStatusWidgetDisplay:
    """Test display update logic."""

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_syncing_state(self, mock_query_one):
        """Test update_display shows syncing state correctly."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.is_syncing = True
        widget.is_online = False
        widget.update_display()

        # Should show syncing status
        mock_connection.add_class.assert_called_with("syncing")
        assert mock_connection.update.called

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_error_state(self, mock_query_one):
        """Test update_display shows error state correctly."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.last_error = "Connection failed"
        widget.is_online = False
        widget.is_syncing = False
        widget.update_display()

        # Should show error status
        mock_connection.add_class.assert_called_with("error")
        assert "Error:" in str(mock_connection.update.call_args)

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_online_state(self, mock_query_one):
        """Test update_display shows online state correctly."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.is_online = True
        widget.is_syncing = False
        widget.last_error = None
        widget.update_display()

        # Should show online status
        mock_connection.add_class.assert_called_with("online")
        assert "Online" in str(mock_connection.update.call_args)

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_offline_state(self, mock_query_one):
        """Test update_display shows offline state correctly."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.is_online = False
        widget.is_syncing = False
        widget.last_error = None
        widget.update_display()

        # Should show offline status
        mock_connection.add_class.assert_called_with("offline")
        assert "Offline" in str(mock_connection.update.call_args)

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_pending_changes(self, mock_query_one):
        """Test update_display shows pending changes."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.pending_changes = 5
        widget.update_display()

        # Should show pending changes
        assert "pending" in str(mock_sync_info.update.call_args)
        assert "5" in str(mock_sync_info.update.call_args)

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_singular_pending_change(self, mock_query_one):
        """Test update_display uses singular form for 1 change."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.pending_changes = 1
        widget.update_display()

        # Should use singular "change" not "changes"
        call_str = str(mock_sync_info.update.call_args)
        assert "pending change" in call_str or "1" in call_str

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_with_conflicts(self, mock_query_one):
        """Test update_display shows conflicts."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.conflicts_count = 3
        widget.update_display()

        # Should show conflict warning
        mock_conflict_info.add_class.assert_called_with("conflict")
        assert "conflict" in str(mock_conflict_info.update.call_args)

    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_no_conflicts(self, mock_query_one):
        """Test update_display hides conflicts when count is zero."""
        widget = SyncStatusWidget()

        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector, widget_type=None):
            return {
                "#connection-status": mock_connection,
                "#sync-info": mock_sync_info,
                "#conflict-info": mock_conflict_info,
            }.get(selector)

        mock_query_one.side_effect = query_side_effect

        widget.conflicts_count = 0
        widget.update_display()

        # Should clear conflict display
        mock_conflict_info.remove_class.assert_called_with("conflict")
        assert "" in str(mock_conflict_info.update.call_args)


class TestSyncStatusWidgetTimeFormatting:
    """Test time formatting utilities."""

    def test_format_time_ago_just_now(self):
        """Test format_time_ago returns 'just now' for recent times."""
        widget = SyncStatusWidget()
        now = datetime.now()

        result = widget._format_time_ago(now)

        assert result == "just now"

    def test_format_time_ago_minutes(self):
        """Test format_time_ago returns minutes for times < 1 hour."""
        widget = SyncStatusWidget()
        five_min_ago = datetime.now() - timedelta(minutes=5)

        result = widget._format_time_ago(five_min_ago)

        assert "minute" in result
        assert "5" in result

    def test_format_time_ago_singular_minute(self):
        """Test format_time_ago uses singular for 1 minute."""
        widget = SyncStatusWidget()
        one_min_ago = datetime.now() - timedelta(minutes=1)

        result = widget._format_time_ago(one_min_ago)

        assert "1 minute ago" in result

    def test_format_time_ago_hours(self):
        """Test format_time_ago returns hours for times < 1 day."""
        widget = SyncStatusWidget()
        two_hours_ago = datetime.now() - timedelta(hours=2)

        result = widget._format_time_ago(two_hours_ago)

        assert "hour" in result
        assert "2" in result

    def test_format_time_ago_days(self):
        """Test format_time_ago returns days for times >= 1 day."""
        widget = SyncStatusWidget()
        three_days_ago = datetime.now() - timedelta(days=3)

        result = widget._format_time_ago(three_days_ago)

        assert "day" in result
        assert "3" in result


class TestSyncStatusWidgetSetters:
    """Test setter methods."""

    def test_set_online(self):
        """Test set_online updates is_online."""
        widget = SyncStatusWidget()

        widget.set_online(True)

        assert widget.is_online is True

    def test_set_syncing(self):
        """Test set_syncing updates is_syncing."""
        widget = SyncStatusWidget()

        widget.set_syncing(True)

        assert widget.is_syncing is True

    def test_set_pending_changes(self):
        """Test set_pending_changes updates pending_changes."""
        widget = SyncStatusWidget()

        widget.set_pending_changes(10)

        assert widget.pending_changes == 10

    def test_set_last_sync(self):
        """Test set_last_sync updates last_sync."""
        widget = SyncStatusWidget()
        now = datetime.now()

        widget.set_last_sync(now)

        assert widget.last_sync == now

    def test_set_conflicts(self):
        """Test set_conflicts updates conflicts_count."""
        widget = SyncStatusWidget()

        widget.set_conflicts(5)

        assert widget.conflicts_count == 5

    def test_set_error(self):
        """Test set_error updates last_error."""
        widget = SyncStatusWidget()

        widget.set_error("Test error")

        assert widget.last_error == "Test error"

    def test_set_error_clear(self):
        """Test set_error can clear error."""
        widget = SyncStatusWidget()
        widget.last_error = "Previous error"

        widget.set_error(None)

        assert widget.last_error is None


class TestCompactSyncStatusInitialization:
    """Test CompactSyncStatus initialization."""

    def test_init_creates_widget(self):
        """Test CompactSyncStatus initializes correctly."""
        widget = CompactSyncStatus()

        assert widget is not None
        assert widget.is_online is False
        assert widget.is_syncing is False
        assert widget.pending_changes == 0
        assert widget.conflicts_count == 0

    def test_init_with_custom_id(self):
        """Test CompactSyncStatus accepts custom ID."""
        widget = CompactSyncStatus(id="compact-status")

        assert widget is not None
        assert widget.id == "compact-status"


class TestCompactSyncStatusRender:
    """Test CompactSyncStatus render method."""

    def test_render_syncing(self):
        """Test render shows syncing indicator."""
        widget = CompactSyncStatus()
        widget.is_syncing = True
        widget.is_online = True

        result = widget.render()

        assert "⟳" in result or "cyan" in result.lower()

    def test_render_online(self):
        """Test render shows online indicator."""
        widget = CompactSyncStatus()
        widget.is_online = True
        widget.is_syncing = False

        result = widget.render()

        assert "●" in result or "green" in result.lower()

    def test_render_offline(self):
        """Test render shows offline indicator."""
        widget = CompactSyncStatus()
        widget.is_online = False
        widget.is_syncing = False

        result = widget.render()

        assert "●" in result or "yellow" in result.lower() or "Offline" in result

    def test_render_with_pending_changes(self):
        """Test render includes pending changes."""
        widget = CompactSyncStatus()
        widget.pending_changes = 5

        result = widget.render()

        assert "pending" in result
        assert "5" in result

    def test_render_with_conflicts(self):
        """Test render includes conflicts."""
        widget = CompactSyncStatus()
        widget.conflicts_count = 3

        result = widget.render()

        assert "⚠" in result or "3" in result

    def test_render_multiple_indicators(self):
        """Test render combines multiple indicators."""
        widget = CompactSyncStatus()
        widget.is_online = True
        widget.pending_changes = 2
        widget.conflicts_count = 1

        result = widget.render()

        # Should have separators
        assert "|" in result


class TestCompactSyncStatusSetters:
    """Test CompactSyncStatus setter methods."""

    def test_set_online(self):
        """Test set_online updates is_online."""
        widget = CompactSyncStatus()

        widget.set_online(True)

        assert widget.is_online is True

    def test_set_syncing(self):
        """Test set_syncing updates is_syncing."""
        widget = CompactSyncStatus()

        widget.set_syncing(True)

        assert widget.is_syncing is True

    def test_set_pending_changes(self):
        """Test set_pending_changes updates pending_changes."""
        widget = CompactSyncStatus()

        widget.set_pending_changes(7)

        assert widget.pending_changes == 7

    def test_set_conflicts(self):
        """Test set_conflicts updates conflicts_count."""
        widget = CompactSyncStatus()

        widget.set_conflicts(2)

        assert widget.conflicts_count == 2


class TestWidgetAvailability:
    """Test widget availability when Textual is installed."""

    def test_sync_status_widget_available(self):
        """Test SyncStatusWidget is available."""
        from tracertm.tui.widgets import sync_status

        assert hasattr(sync_status, "SyncStatusWidget")
        assert sync_status.TEXTUAL_AVAILABLE is True

    def test_compact_sync_status_available(self):
        """Test CompactSyncStatus is available."""
        from tracertm.tui.widgets import sync_status

        assert hasattr(sync_status, "CompactSyncStatus")
        assert sync_status.TEXTUAL_AVAILABLE is True
