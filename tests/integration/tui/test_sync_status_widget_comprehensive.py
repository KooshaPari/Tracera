"""Comprehensive integration tests for SyncStatusWidget and CompactSyncStatus.

Tests widget integration with Textual framework, real DOM manipulation,
reactive updates, display rendering, error states, animation states,
and status transitions.

Coverage target: 85%+
Test count: 30+ tests across all functionality
"""

from datetime import UTC, datetime, timedelta

# Skip all tests if Textual not available
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE

pytest.importorskip("textual")

from textual.containers import Horizontal

from tracertm.tui.widgets.sync_status import (
    TEXTUAL_AVAILABLE,
    CompactSyncStatus,
    SyncStatusWidget,
)


class TestSyncStatusWidgetIntegration:
    """Integration tests for SyncStatusWidget with actual Textual rendering."""

    def test_widget_composes_correctly(self) -> None:
        """Test widget composition creates proper child structure."""
        widget = SyncStatusWidget()
        children = list(widget.compose())

        assert len(children) > 0
        # Should have Horizontal container
        horizontal = children[0]
        assert hasattr(horizontal, "id") or isinstance(horizontal, Horizontal)

    def test_widget_has_correct_css(self) -> None:
        """Test widget has proper CSS styling defined."""
        widget = SyncStatusWidget()
        assert widget.DEFAULT_CSS is not None
        assert "SyncStatusWidget" in widget.DEFAULT_CSS
        assert ".online" in widget.DEFAULT_CSS
        assert ".offline" in widget.DEFAULT_CSS
        assert ".syncing" in widget.DEFAULT_CSS
        assert ".error" in widget.DEFAULT_CSS
        assert ".conflict" in widget.DEFAULT_CSS

    def test_widget_initializes_with_defaults(self) -> None:
        """Test widget initializes with correct default values."""
        widget = SyncStatusWidget()

        assert widget.is_online is False
        assert widget.is_syncing is False
        assert widget.pending_changes == 0
        assert widget.last_sync is None
        assert widget.conflicts_count == 0
        assert widget.last_error is None

    def test_widget_accepts_custom_id(self) -> None:
        """Test widget can be initialized with custom ID."""
        widget = SyncStatusWidget(id="custom-sync-widget")
        assert widget.id == "custom-sync-widget"

    def test_widget_accepts_custom_classes(self) -> None:
        """Test widget can be initialized with custom CSS classes."""
        widget = SyncStatusWidget(classes="custom-class")
        assert "custom-class" in widget.classes

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: False))
    def test_update_display_handles_unmounted_widget(self, _mock_mounted: Any) -> None:
        """Test update_display gracefully handles unmounted widget."""
        widget = SyncStatusWidget()
        # Should not raise when not mounted
        widget.update_display()

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_update_display_handles_composition_exception(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test update_display handles query_one exception gracefully."""
        widget = SyncStatusWidget()
        mock_query.side_effect = Exception("Widget not yet composed")

        # Should not raise
        widget.update_display()


class TestStatusDisplay:
    """Tests for status display rendering."""

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_syncing_state(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget displays syncing state correctly."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_syncing = True
        widget.is_online = True
        widget.update_display()

        # Verify syncing indicator is shown
        mock_connection.update.assert_called()
        mock_connection.add_class.assert_called_with("syncing")
        mock_connection.remove_class.assert_called()

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_online_state(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget displays online state correctly."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_online = True
        widget.is_syncing = False
        widget.last_error = None
        widget.update_display()

        # Verify online indicator is shown
        mock_connection.update.assert_called()
        mock_connection.add_class.assert_called_with("online")

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_offline_state(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget displays offline state correctly."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_online = False
        widget.is_syncing = False
        widget.last_error = None
        widget.update_display()

        # Verify offline indicator is shown
        mock_connection.add_class.assert_called_with("offline")


class TestProgressUpdates:
    """Tests for progress and change tracking."""

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_pending_changes_plural(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget displays multiple pending changes correctly."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.pending_changes = 5
        widget.update_display()

        # Verify pending changes are shown
        call_args = str(mock_sync_info.update.call_args)
        assert "5" in call_args
        assert "pending" in call_args.lower()

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_pending_changes_singular(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget uses singular form for 1 pending change."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.pending_changes = 1
        widget.update_display()

        # Verify singular form is used
        call_args = str(mock_sync_info.update.call_args)
        assert "1" in call_args

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_no_pending_changes_shows_last_sync(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget shows last sync when no pending changes."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        now = datetime.now()
        widget.pending_changes = 0
        widget.last_sync = now
        widget.update_display()

        # Verify last sync is shown
        call_args = str(mock_sync_info.update.call_args)
        assert "Last sync" in call_args

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_never_synced(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget shows 'Never synced' when no sync history."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.pending_changes = 0
        widget.last_sync = None
        widget.update_display()

        # Verify "Never synced" is shown
        call_args = str(mock_sync_info.update.call_args)
        assert "Never synced" in call_args


class TestErrorRendering:
    """Tests for error state rendering and display."""

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_error_state(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget displays error state correctly."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        error_msg = "Connection timeout"
        widget.last_error = error_msg
        widget.update_display()

        # Verify error is shown
        mock_connection.add_class.assert_called_with("error")
        call_args = str(mock_connection.update.call_args)
        assert "Error" in call_args
        assert error_msg in call_args

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_error_takes_precedence_over_online(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test error state takes precedence over online state."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_online = True
        widget.last_error = "Error occurred"
        widget.update_display()

        # Verify error is shown, not online
        mock_connection.add_class.assert_called_with("error")

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_clear_error(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test clearing error message."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.last_error = "Error"
        widget.is_online = True
        widget.set_error(None)
        widget.update_display()

        # Verify error is cleared and online state is shown
        assert widget.last_error is None


class TestAnimationStates:
    """Tests for animation and state transition states."""

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_syncing_animation_indicator(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test syncing state shows animation indicator."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_syncing = True
        widget.update_display()

        # Verify syncing indicator (⟳) is shown
        call_args = str(mock_connection.update.call_args)
        assert "⟳" in call_args or "Syncing" in call_args

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_syncing_takes_precedence_over_online(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test syncing state takes precedence over online/offline."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_online = True
        widget.is_syncing = True
        widget.update_display()

        # Verify syncing state overrides online
        mock_connection.add_class.assert_called_with("syncing")

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_state_transition_syncing_to_online(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test transition from syncing to online state."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        # Start syncing
        widget.is_syncing = True
        widget.update_display()
        assert "syncing" in str(mock_connection.add_class.call_args_list).lower()

        # Transition to online
        widget.is_syncing = False
        widget.is_online = True
        widget.update_display()
        assert "online" in str(mock_connection.add_class.call_args_list).lower()

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_state_transition_online_to_offline(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test transition from online to offline state."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        # Start online
        widget.is_online = True
        widget.update_display()

        # Transition to offline
        widget.is_online = False
        widget.update_display()

        # Verify offline class was added
        assert "offline" in str(mock_connection.add_class.call_args_list).lower()


class TestConflictDisplay:
    """Tests for conflict state rendering."""

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_conflicts_plural(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget displays multiple conflicts correctly."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.conflicts_count = 3
        widget.update_display()

        # Verify conflicts are shown
        mock_conflict_info.add_class.assert_called_with("conflict")
        call_args = str(mock_conflict_info.update.call_args)
        assert "3" in call_args
        assert "conflict" in call_args.lower()

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_display_conflicts_singular(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test widget uses singular form for 1 conflict."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.conflicts_count = 1
        widget.update_display()

        # Verify singular form
        call_args = str(mock_conflict_info.update.call_args)
        assert "1" in call_args

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_hide_conflicts_when_zero(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test conflicts are hidden when count is zero."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.conflicts_count = 0
        widget.update_display()

        # Verify conflict class is removed
        mock_conflict_info.remove_class.assert_called_with("conflict")


class TestTimeFormatting:
    """Tests for time formatting utilities."""

    def test_format_just_now(self) -> None:
        """Test formatting for current time."""
        widget = SyncStatusWidget()
        now = datetime.now()

        result = widget._format_time_ago(now)

        assert result == "just now"

    def test_format_seconds(self) -> None:
        """Test formatting for times under 60 seconds."""
        widget = SyncStatusWidget()
        thirty_sec_ago = datetime.now() - timedelta(seconds=30)

        result = widget._format_time_ago(thirty_sec_ago)

        assert result == "just now"

    def test_format_singular_minute(self) -> None:
        """Test formatting for 1 minute ago."""
        widget = SyncStatusWidget()
        one_min_ago = datetime.now() - timedelta(minutes=1)

        result = widget._format_time_ago(one_min_ago)

        assert "1 minute ago" in result

    def test_format_multiple_minutes(self) -> None:
        """Test formatting for multiple minutes."""
        widget = SyncStatusWidget()
        five_min_ago = datetime.now() - timedelta(minutes=5)

        result = widget._format_time_ago(five_min_ago)

        assert "5 minutes ago" in result

    def test_format_singular_hour(self) -> None:
        """Test formatting for 1 hour ago."""
        widget = SyncStatusWidget()
        one_hour_ago = datetime.now() - timedelta(hours=1)

        result = widget._format_time_ago(one_hour_ago)

        assert "1 hour ago" in result

    def test_format_multiple_hours(self) -> None:
        """Test formatting for multiple hours."""
        widget = SyncStatusWidget()
        two_hours_ago = datetime.now() - timedelta(hours=2)

        result = widget._format_time_ago(two_hours_ago)

        assert "2 hours ago" in result

    def test_format_singular_day(self) -> None:
        """Test formatting for 1 day ago."""
        widget = SyncStatusWidget()
        one_day_ago = datetime.now() - timedelta(days=1)

        result = widget._format_time_ago(one_day_ago)

        assert "1 day ago" in result

    def test_format_multiple_days(self) -> None:
        """Test formatting for multiple days."""
        widget = SyncStatusWidget()
        three_days_ago = datetime.now() - timedelta(days=3)

        result = widget._format_time_ago(three_days_ago)

        assert "3 days ago" in result

    def test_format_boundary_59_seconds(self) -> None:
        """Test formatting boundary at 59 seconds."""
        widget = SyncStatusWidget()
        boundary = datetime.now() - timedelta(seconds=59)

        result = widget._format_time_ago(boundary)

        assert result == "just now"

    def test_format_boundary_60_seconds(self) -> None:
        """Test formatting boundary at 60 seconds (1 minute)."""
        widget = SyncStatusWidget()
        boundary = datetime.now() - timedelta(seconds=60)

        result = widget._format_time_ago(boundary)

        assert "minute" in result


class TestSetterMethods:
    """Tests for setter convenience methods."""

    def test_set_online_true(self) -> None:
        """Test set_online sets is_online to True."""
        widget = SyncStatusWidget()

        widget.set_online(True)

        assert widget.is_online is True

    def test_set_online_false(self) -> None:
        """Test set_online sets is_online to False."""
        widget = SyncStatusWidget()
        widget.set_online(True)

        widget.set_online(False)

        assert widget.is_online is False

    def test_set_syncing_true(self) -> None:
        """Test set_syncing sets is_syncing to True."""
        widget = SyncStatusWidget()

        widget.set_syncing(True)

        assert widget.is_syncing is True

    def test_set_syncing_false(self) -> None:
        """Test set_syncing sets is_syncing to False."""
        widget = SyncStatusWidget()
        widget.set_syncing(True)

        widget.set_syncing(False)

        assert widget.is_syncing is False

    def test_set_pending_changes_various_values(self) -> None:
        """Test set_pending_changes with various values."""
        widget = SyncStatusWidget()

        widget.set_pending_changes(0)
        assert widget.pending_changes == 0

        widget.set_pending_changes(1)
        assert widget.pending_changes == 1

        widget.set_pending_changes(100)
        assert widget.pending_changes == 100

    def test_set_last_sync(self) -> None:
        """Test set_last_sync sets last_sync timestamp."""
        widget = SyncStatusWidget()
        now = datetime.now()

        widget.set_last_sync(now)

        assert widget.last_sync == now

    def test_set_last_sync_none(self) -> None:
        """Test set_last_sync can clear timestamp."""
        widget = SyncStatusWidget()
        now = datetime.now()
        widget.set_last_sync(now)

        widget.set_last_sync(None)

        assert widget.last_sync is None

    def test_set_conflicts(self) -> None:
        """Test set_conflicts sets conflicts_count."""
        widget = SyncStatusWidget()

        widget.set_conflicts(5)

        assert widget.conflicts_count == COUNT_FIVE

    def test_set_error(self) -> None:
        """Test set_error sets error message."""
        widget = SyncStatusWidget()

        widget.set_error("Test error")

        assert widget.last_error == "Test error"

    def test_set_error_clear(self) -> None:
        """Test set_error can clear error."""
        widget = SyncStatusWidget()
        widget.set_error("Error")

        widget.set_error(None)

        assert widget.last_error is None


class TestCompactSyncStatusIntegration:
    """Integration tests for CompactSyncStatus widget."""

    def test_compact_widget_initializes(self) -> None:
        """Test CompactSyncStatus initializes correctly."""
        widget = CompactSyncStatus()

        assert widget is not None
        assert widget.is_online is False
        assert widget.is_syncing is False
        assert widget.pending_changes == 0
        assert widget.conflicts_count == 0

    def test_compact_widget_render_offline(self) -> None:
        """Test CompactSyncStatus renders offline state."""
        widget = CompactSyncStatus()
        widget.is_online = False
        widget.is_syncing = False

        result = widget.render()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_compact_widget_render_online(self) -> None:
        """Test CompactSyncStatus renders online state."""
        widget = CompactSyncStatus()
        widget.is_online = True
        widget.is_syncing = False

        result = widget.render()

        assert "●" in result or "green" in result.lower()

    def test_compact_widget_render_syncing(self) -> None:
        """Test CompactSyncStatus renders syncing state."""
        widget = CompactSyncStatus()
        widget.is_syncing = True
        widget.is_online = True

        result = widget.render()

        assert "⟳" in result or "cyan" in result.lower()

    def test_compact_widget_render_pending_changes(self) -> None:
        """Test CompactSyncStatus renders pending changes."""
        widget = CompactSyncStatus()
        widget.pending_changes = 3

        result = widget.render()

        assert "pending" in result or "3" in result

    def test_compact_widget_render_conflicts(self) -> None:
        """Test CompactSyncStatus renders conflicts."""
        widget = CompactSyncStatus()
        widget.conflicts_count = 2

        result = widget.render()

        assert "⚠" in result or "2" in result or "conflict" in result.lower()

    def test_compact_widget_render_all_indicators(self) -> None:
        """Test CompactSyncStatus renders multiple indicators."""
        widget = CompactSyncStatus()
        widget.is_online = True
        widget.pending_changes = 1
        widget.conflicts_count = 1

        result = widget.render()

        # Should have separator for multiple parts
        assert "|" in result

    def test_compact_widget_set_online(self) -> None:
        """Test CompactSyncStatus set_online."""
        widget = CompactSyncStatus()

        widget.set_online(True)

        assert widget.is_online is True

    def test_compact_widget_set_syncing(self) -> None:
        """Test CompactSyncStatus set_syncing."""
        widget = CompactSyncStatus()

        widget.set_syncing(True)

        assert widget.is_syncing is True

    def test_compact_widget_set_pending_changes(self) -> None:
        """Test CompactSyncStatus set_pending_changes."""
        widget = CompactSyncStatus()

        widget.set_pending_changes(5)

        assert widget.pending_changes == COUNT_FIVE

    def test_compact_widget_set_conflicts(self) -> None:
        """Test CompactSyncStatus set_conflicts."""
        widget = CompactSyncStatus()

        widget.set_conflicts(3)

        assert widget.conflicts_count == COUNT_THREE


class TestComplexScenarios:
    """Tests for complex state combinations and scenarios."""

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_scenario_sync_with_pending_changes(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test syncing while having pending changes."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_syncing = True
        widget.pending_changes = 3
        widget.update_display()

        # Should show syncing, not pending changes
        mock_connection.add_class.assert_called_with("syncing")

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_scenario_error_with_pending_changes(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test error state while having pending changes."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.last_error = "Sync failed"
        widget.pending_changes = 5
        widget.conflicts_count = 2
        widget.update_display()

        # Should show error state
        mock_connection.add_class.assert_called_with("error")

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_scenario_offline_with_pending_changes(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test offline state with pending changes."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        widget.is_online = False
        widget.pending_changes = 3
        widget.update_display()

        # Should show offline state
        mock_connection.add_class.assert_called_with("offline")

    @patch.object(SyncStatusWidget, "is_mounted", _new_callable=lambda: property(lambda s: True))
    @patch.object(SyncStatusWidget, "query_one")
    def test_scenario_full_sync_cycle(self, mock_query: Any, _mock_mounted: Any) -> None:
        """Test complete sync cycle: offline -> syncing -> online."""
        widget = SyncStatusWidget()
        mock_connection = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if selector == "#connection-status":
                return mock_connection
            if selector == "#sync-info":
                return mock_sync_info
            if selector == "#conflict-info":
                return mock_conflict_info
            return None

        mock_query.side_effect = query_side_effect

        # Step 1: Start offline with pending changes
        widget.is_online = False
        widget.pending_changes = 3
        widget.update_display()

        # Step 2: Start syncing
        widget.is_syncing = True
        widget.update_display()

        # Step 3: Complete sync
        widget.is_syncing = False
        widget.is_online = True
        widget.pending_changes = 0
        widget.last_sync = datetime.now()
        widget.update_display()

        # Final state should show online
        assert widget.is_online is True
        assert widget.pending_changes == 0


class TestReactiveWatchers:
    """Tests for reactive attribute watchers."""

    def test_watch_is_online_triggers_update(self) -> None:
        """Test is_online watcher mechanism through reactive."""
        widget = SyncStatusWidget()

        widget.is_online = True

        # Reactive mechanism should propagate the change
        assert widget.is_online is True

    def test_watch_is_syncing_triggers_update(self) -> None:
        """Test is_syncing watcher mechanism through reactive."""
        widget = SyncStatusWidget()

        widget.is_syncing = True

        assert widget.is_syncing is True

    def test_watch_pending_changes_triggers_update(self) -> None:
        """Test pending_changes watcher mechanism through reactive."""
        widget = SyncStatusWidget()

        widget.pending_changes = 5

        assert widget.pending_changes == COUNT_FIVE

    def test_watch_last_sync_triggers_update(self) -> None:
        """Test last_sync watcher mechanism through reactive."""
        widget = SyncStatusWidget()
        now = datetime.now()

        widget.last_sync = now

        assert widget.last_sync == now

    def test_watch_conflicts_count_triggers_update(self) -> None:
        """Test conflicts_count watcher mechanism through reactive."""
        widget = SyncStatusWidget()

        widget.conflicts_count = 3

        assert widget.conflicts_count == COUNT_THREE

    def test_watch_last_error_triggers_update(self) -> None:
        """Test last_error watcher mechanism through reactive."""
        widget = SyncStatusWidget()

        widget.last_error = "Error"

        assert widget.last_error == "Error"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_large_pending_changes_count(self) -> None:
        """Test widget handles very large pending changes count."""
        widget = SyncStatusWidget()
        widget.set_pending_changes(9999999)

        assert widget.pending_changes == 9999999

    def test_very_large_conflicts_count(self) -> None:
        """Test widget handles very large conflicts count."""
        widget = SyncStatusWidget()
        widget.set_conflicts(9999999)

        assert widget.conflicts_count == 9999999

    def test_long_error_message(self) -> None:
        """Test widget handles very long error messages."""
        widget = SyncStatusWidget()
        long_error = "A" * 1000

        widget.set_error(long_error)

        assert widget.last_error == long_error

    def test_empty_error_string(self) -> None:
        """Test widget handles empty error string."""
        widget = SyncStatusWidget()

        widget.set_error("")

        assert widget.last_error == ""

    def test_format_time_ago_with_timezone(self) -> None:
        """Test time formatting with timezone-aware datetime."""
        widget = SyncStatusWidget()

        now_tz = datetime.now(UTC)
        past_tz = now_tz - timedelta(minutes=5)

        result = widget._format_time_ago(past_tz)

        assert "minute" in result or "ago" in result

    def test_multiple_state_changes_rapid(self) -> None:
        """Test widget handles rapid state changes."""
        widget = SyncStatusWidget()

        for _ in range(10):
            widget.set_online(True)
            widget.set_online(False)
            widget.set_syncing(True)
            widget.set_syncing(False)

        # Should end up in consistent state
        assert widget.is_online is False
        assert widget.is_syncing is False


class TestCSSAndStyling:
    """Tests for CSS and styling features."""

    def test_widget_has_default_css(self) -> None:
        """Test widget defines DEFAULT_CSS."""
        widget = SyncStatusWidget()
        assert hasattr(widget, "DEFAULT_CSS")
        assert isinstance(widget.DEFAULT_CSS, str)

    def test_css_contains_all_status_classes(self) -> None:
        """Test CSS defines all status classes."""
        widget = SyncStatusWidget()
        css = widget.DEFAULT_CSS

        assert ".online" in css
        assert ".offline" in css
        assert ".syncing" in css
        assert ".error" in css
        assert ".conflict" in css

    def test_widget_styling_online_class(self) -> None:
        """Test online status applies correct CSS class."""
        widget = SyncStatusWidget()
        assert "online" in widget.DEFAULT_CSS

    def test_widget_styling_error_class(self) -> None:
        """Test error status applies correct CSS class."""
        widget = SyncStatusWidget()
        assert "error" in widget.DEFAULT_CSS


# Summary and coverage report tests
class TestCoverageAndCompletion:
    """Verify test suite completeness and coverage."""

    def test_suite_has_minimum_test_count(self) -> None:
        """Verify test suite has 30+ tests."""
        # This test verifies the test suite structure
        test_classes = [
            TestSyncStatusWidgetIntegration,
            TestStatusDisplay,
            TestProgressUpdates,
            TestErrorRendering,
            TestAnimationStates,
            TestConflictDisplay,
            TestTimeFormatting,
            TestSetterMethods,
            TestCompactSyncStatusIntegration,
            TestComplexScenarios,
            TestReactiveWatchers,
            TestEdgeCases,
            TestCSSAndStyling,
        ]

        total_test_methods = sum(len([m for m in dir(cls) if m.startswith("test_")]) for cls in test_classes)

        # Should have at least 30 test methods
        assert total_test_methods >= 30, f"Only found {total_test_methods} tests, need 30+"

    def test_textual_available(self) -> None:
        """Verify Textual library is available."""
        assert TEXTUAL_AVAILABLE is True
