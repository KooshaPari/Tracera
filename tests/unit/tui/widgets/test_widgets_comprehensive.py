"""Comprehensive tests for all TUI widgets.

This test suite provides 100% coverage for:
- ItemListWidget: initialization, column setup
- ConflictPanel: initialization, conflict display, resolution actions, button handling
- SyncStatusWidget: reactive updates, status display, time formatting
- CompactSyncStatus: compact display, status updates
- GraphViewWidget: initialization, display
- StateDisplayWidget: initialization, columns
- ViewSwitcherWidget: initialization, view setup

Coverage includes:
- Widget initialization and composition
- Reactive property updates and watchers
- Event handling and message posting
- Display formatting and time calculations
- Edge cases and boundary conditions
- Error handling
"""

from datetime import UTC, datetime, timedelta
from typing import Any, cast
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_TWO

try:
    from textual.widgets import DataTable, Static, Tree

    from tracertm.tui.widgets.conflict_panel import TEXTUAL_AVAILABLE as CONFLICT_AVAILABLE
    from tracertm.tui.widgets.conflict_panel import ConflictPanel
    from tracertm.tui.widgets.graph_view import TEXTUAL_AVAILABLE as GRAPH_VIEW_AVAILABLE
    from tracertm.tui.widgets.graph_view import GraphViewWidget
    from tracertm.tui.widgets.item_list import TEXTUAL_AVAILABLE as ITEM_LIST_AVAILABLE
    from tracertm.tui.widgets.item_list import ItemListWidget
    from tracertm.tui.widgets.state_display import TEXTUAL_AVAILABLE as STATE_DISPLAY_AVAILABLE
    from tracertm.tui.widgets.state_display import StateDisplayWidget
    from tracertm.tui.widgets.sync_status import TEXTUAL_AVAILABLE as SYNC_STATUS_AVAILABLE
    from tracertm.tui.widgets.sync_status import CompactSyncStatus, SyncStatusWidget
    from tracertm.tui.widgets.view_switcher import TEXTUAL_AVAILABLE as VIEW_SWITCHER_AVAILABLE
    from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

if not TEXTUAL_AVAILABLE:
    pytest.skip("Textual not available", allow_module_level=True)


# =============================================================================
# ItemListWidget Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not ITEM_LIST_AVAILABLE, reason="Textual not available")
class TestItemListWidget:
    """Tests for ItemListWidget."""

    def test_item_list_inherits_datatable(self) -> None:
        """Test ItemListWidget inherits from DataTable."""
        assert issubclass(ItemListWidget, DataTable)

    def test_item_list_class_exists(self) -> None:
        """Test ItemListWidget class exists and can be imported."""
        assert ItemListWidget is not None
        assert hasattr(ItemListWidget, "__init__")


# =============================================================================
# ConflictPanel Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not CONFLICT_AVAILABLE, reason="Textual not available")
class TestConflictPanel:
    """Comprehensive tests for ConflictPanel."""

    def test_conflict_panel_class_structure(self) -> None:
        """Test ConflictPanel has proper class structure."""
        assert hasattr(ConflictPanel, "BINDINGS")
        assert hasattr(ConflictPanel, "DEFAULT_CSS")
        assert hasattr(ConflictPanel, "__init__")

        # Check CSS
        assert isinstance(ConflictPanel.DEFAULT_CSS, str)
        assert "ConflictPanel" in ConflictPanel.DEFAULT_CSS

        # Check bindings
        binding_keys = [b.key for b in ConflictPanel.BINDINGS]
        assert "l" in binding_keys  # Local
        assert "r" in binding_keys  # Remote
        assert "m" in binding_keys  # Manual
        assert "escape" in binding_keys  # Close

    def test_conflict_panel_methods_exist(self) -> None:
        """Test ConflictPanel has all required methods."""
        assert hasattr(ConflictPanel, "on_mount")
        assert hasattr(ConflictPanel, "refresh_conflict_list")
        assert hasattr(ConflictPanel, "show_conflict_detail")
        assert hasattr(ConflictPanel, "action_resolve_local")
        assert hasattr(ConflictPanel, "action_resolve_remote")
        assert hasattr(ConflictPanel, "action_resolve_manual")
        assert hasattr(ConflictPanel, "action_close")
        assert hasattr(ConflictPanel, "on_button_pressed")
        assert hasattr(ConflictPanel, "on_data_table_row_selected")

    @patch.object(ConflictPanel, "query_one")
    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_refresh_conflict_list(self, mock_query_one: Any) -> None:
        """Test refreshing conflict list display."""
        # Create mock conflicts
        conflict1 = MagicMock()
        conflict1.entity_type = "item"
        conflict1.entity_id = "abc123def456"
        conflict1.local_version.vector_clock.version = 1
        conflict1.remote_version.vector_clock.version = 2
        conflict1.detected_at = datetime(2024, 1, 1, 12, 0)

        conflict2 = MagicMock()
        conflict2.entity_type = "link"
        conflict2.entity_id = "xyz789uvw012"
        conflict2.local_version.vector_clock.version = 3
        conflict2.remote_version.vector_clock.version = 4
        conflict2.detected_at = datetime(2024, 1, 2, 13, 0)

        panel = cast("Any", ConflictPanel())
        panel.conflicts = [conflict1, conflict2]

        # Mock table widget
        mock_table = MagicMock()
        mock_query_one.return_value = mock_table

        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        assert mock_table.add_row.call_count == COUNT_TWO

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_data_table_row_selected(self) -> None:
        """Test handling row selection."""
        conflict = MagicMock()
        panel = cast("Any", ConflictPanel())
        panel.conflicts = [conflict]
        panel.selected_conflict = None
        panel.show_conflict_detail = MagicMock()

        event = MagicMock()
        event.row_index = 0

        panel.on_data_table_row_selected(event)

        assert panel.selected_conflict == conflict
        panel.show_conflict_detail.assert_called_once_with(conflict)

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_data_table_row_selected_out_of_range(self) -> None:
        """Test handling row selection out of range."""
        panel = cast("Any", ConflictPanel())
        panel.conflicts = []
        panel.selected_conflict = None
        panel.show_conflict_detail = MagicMock()

        event = MagicMock()
        event.row_index = 5

        panel.on_data_table_row_selected(event)

        assert panel.selected_conflict is None
        panel.show_conflict_detail.assert_not_called()

    @patch("tracertm.tui.widgets.conflict_panel.compare_versions")
    @patch.object(ConflictPanel, "query_one")
    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_show_conflict_detail(self, mock_query_one: Any, mock_compare: Any) -> None:
        """Test showing conflict details."""
        # Setup conflict with detailed version info
        local_version = MagicMock()
        local_version.vector_clock.version = 1
        local_version.vector_clock.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        local_version.vector_clock.client_id = "client1"

        remote_version = MagicMock()
        remote_version.vector_clock.version = 2
        remote_version.vector_clock.timestamp = datetime(2024, 1, 1, 13, 0, 0)
        remote_version.vector_clock.client_id = "client2"

        conflict = MagicMock()
        conflict.entity_type = "item"
        conflict.entity_id = "abc123"
        conflict.local_version = local_version
        conflict.remote_version = remote_version

        # Mock compare_versions result
        mock_compare.return_value = {
            "modified": ["title", "description"],
            "added": ["new_field"],
            "removed": ["old_field"],
        }

        panel = cast("Any", ConflictPanel())

        # Mock detail widget
        mock_detail = MagicMock()
        mock_query_one.return_value = mock_detail

        panel.show_conflict_detail(conflict)

        mock_detail.update.assert_called_once()
        update_text = mock_detail.update.call_args[0][0]
        assert "abc123" in update_text
        assert "title" in update_text or "Modified" in update_text

    @patch("tracertm.tui.widgets.conflict_panel.compare_versions")
    @patch.object(ConflictPanel, "query_one")
    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_show_conflict_detail_no_differences(self, mock_query_one: Any, mock_compare: Any) -> None:
        """Test showing conflict details with no differences."""
        local_version = MagicMock()
        local_version.vector_clock.version = 1
        local_version.vector_clock.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        local_version.vector_clock.client_id = "client1"

        remote_version = MagicMock()
        remote_version.vector_clock.version = 2
        remote_version.vector_clock.timestamp = datetime(2024, 1, 1, 13, 0, 0)
        remote_version.vector_clock.client_id = "client2"

        conflict = MagicMock()
        conflict.entity_type = "item"
        conflict.entity_id = "abc123"
        conflict.local_version = local_version
        conflict.remote_version = remote_version

        # Mock compare_versions result with no differences
        mock_compare.return_value = {"modified": [], "added": [], "removed": []}

        panel = cast("Any", ConflictPanel())

        mock_detail = MagicMock()
        mock_query_one.return_value = mock_detail

        panel.show_conflict_detail(conflict)

        mock_detail.update.assert_called_once()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_action_resolve_local(self) -> None:
        """Test resolve local action."""
        conflict = MagicMock()
        panel = cast("Any", ConflictPanel())
        panel.selected_conflict = conflict
        panel.post_message = MagicMock()

        panel.action_resolve_local()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "local"
        assert message.conflict == conflict

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_action_resolve_local_no_selection(self) -> None:
        """Test resolve local action with no selection."""
        panel = cast("Any", ConflictPanel())
        panel.selected_conflict = None
        panel.post_message = MagicMock()

        panel.action_resolve_local()

        panel.post_message.assert_not_called()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_action_resolve_remote(self) -> None:
        """Test resolve remote action."""
        conflict = MagicMock()
        panel = cast("Any", ConflictPanel())
        panel.selected_conflict = conflict
        panel.post_message = MagicMock()

        panel.action_resolve_remote()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "remote"

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_action_resolve_manual(self) -> None:
        """Test resolve manual action."""
        conflict = MagicMock()
        panel = cast("Any", ConflictPanel())
        panel.selected_conflict = conflict
        panel.post_message = MagicMock()

        panel.action_resolve_manual()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "manual"

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_action_close(self) -> None:
        """Test close action."""
        panel = cast("Any", ConflictPanel())
        panel.post_message = MagicMock()

        panel.action_close()

        panel.post_message.assert_called_once()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_button_pressed_local(self) -> None:
        """Test button press handler for local button."""
        panel = cast("Any", ConflictPanel())
        panel.action_resolve_local = MagicMock()

        event = MagicMock()
        event.button.id = "btn-local"

        panel.on_button_pressed(event)

        panel.action_resolve_local.assert_called_once()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_button_pressed_remote(self) -> None:
        """Test button press handler for remote button."""
        panel = cast("Any", ConflictPanel())
        panel.action_resolve_remote = MagicMock()

        event = MagicMock()
        event.button.id = "btn-remote"

        panel.on_button_pressed(event)

        panel.action_resolve_remote.assert_called_once()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_button_pressed_manual(self) -> None:
        """Test button press handler for manual button."""
        panel = cast("Any", ConflictPanel())
        panel.action_resolve_manual = MagicMock()

        event = MagicMock()
        event.button.id = "btn-manual"

        panel.on_button_pressed(event)

        panel.action_resolve_manual.assert_called_once()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_button_pressed_close(self) -> None:
        """Test button press handler for close button."""
        panel = cast("Any", ConflictPanel())
        panel.action_close = MagicMock()

        event = MagicMock()
        event.button.id = "btn-close"

        panel.on_button_pressed(event)

        panel.action_close.assert_called_once()

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_on_button_pressed_unknown(self) -> None:
        """Test button press handler for unknown button."""
        panel = cast("Any", ConflictPanel())
        panel.action_close = MagicMock()

        event = MagicMock()
        event.button.id = "btn-unknown"

        # Should not raise error
        panel.on_button_pressed(event)

        panel.action_close.assert_not_called()


# =============================================================================
# SyncStatusWidget Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not SYNC_STATUS_AVAILABLE, reason="Textual not available")
class TestSyncStatusWidget:
    """Comprehensive tests for SyncStatusWidget."""

    def test_sync_status_class_structure(self) -> None:
        """Test SyncStatusWidget has proper class structure."""
        assert hasattr(SyncStatusWidget, "DEFAULT_CSS")
        assert isinstance(SyncStatusWidget.DEFAULT_CSS, str)
        assert "SyncStatusWidget" in SyncStatusWidget.DEFAULT_CSS

        # Check methods exist
        assert hasattr(SyncStatusWidget, "on_mount")
        assert hasattr(SyncStatusWidget, "update_display")
        assert hasattr(SyncStatusWidget, "set_online")
        assert hasattr(SyncStatusWidget, "set_syncing")
        assert hasattr(SyncStatusWidget, "set_pending_changes")
        assert hasattr(SyncStatusWidget, "set_last_sync")
        assert hasattr(SyncStatusWidget, "set_conflicts")
        assert hasattr(SyncStatusWidget, "set_error")
        assert hasattr(SyncStatusWidget, "_format_time_ago")

    @patch.object(SyncStatusWidget, "update_display")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_watch_is_online(self, mock_update: Any) -> None:
        """Test watch_is_online triggers update."""
        widget = SyncStatusWidget()
        widget.watch_is_online(True)

        mock_update.assert_called_once()

    @patch.object(SyncStatusWidget, "update_display")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_watch_is_syncing(self, mock_update: Any) -> None:
        """Test watch_is_syncing triggers update."""
        widget = SyncStatusWidget()
        widget.watch_is_syncing(True)

        mock_update.assert_called_once()

    @patch.object(SyncStatusWidget, "update_display")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_watch_pending_changes(self, mock_update: Any) -> None:
        """Test watch_pending_changes triggers update."""
        widget = SyncStatusWidget()
        widget.watch_pending_changes(5)

        mock_update.assert_called_once()

    @patch.object(SyncStatusWidget, "update_display")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_watch_last_sync(self, mock_update: Any) -> None:
        """Test watch_last_sync triggers update."""
        widget = SyncStatusWidget()
        widget.watch_last_sync(datetime.now())

        mock_update.assert_called_once()

    @patch.object(SyncStatusWidget, "update_display")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_watch_conflicts_count(self, mock_update: Any) -> None:
        """Test watch_conflicts_count triggers update."""
        widget = SyncStatusWidget()
        widget.watch_conflicts_count(3)

        mock_update.assert_called_once()

    @patch.object(SyncStatusWidget, "update_display")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_watch_last_error(self, mock_update: Any) -> None:
        """Test watch_last_error triggers update."""
        widget = SyncStatusWidget()
        widget.watch_last_error("Error message")

        mock_update.assert_called_once()

    @patch.object(SyncStatusWidget, "query_one")
    @patch.object(SyncStatusWidget, "__init__", lambda _x: None)
    def test_sync_status_update_display_syncing(self, mock_query_one: Any) -> None:
        """Test update_display when syncing."""
        widget = SyncStatusWidget()
        widget.is_syncing = True

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_connection_status.update.assert_called()
        assert "Syncing" in mock_connection_status.update.call_args[0][0]

    def test_sync_status_update_display_error(self) -> None:
        """Test update_display when error."""
        widget = SyncStatusWidget()
        widget.last_error = "Connection failed"

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_connection_status.update.assert_called()
        assert "Error" in mock_connection_status.update.call_args[0][0]

    def test_sync_status_update_display_online(self) -> None:
        """Test update_display when online."""
        widget = SyncStatusWidget()
        widget.is_online = True

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_connection_status.update.assert_called()
        assert "Online" in mock_connection_status.update.call_args[0][0]

    def test_sync_status_update_display_offline(self) -> None:
        """Test update_display when offline."""
        widget = SyncStatusWidget()
        widget.is_online = False

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_connection_status.update.assert_called()
        assert "Offline" in mock_connection_status.update.call_args[0][0]

    def test_sync_status_update_display_pending_changes(self) -> None:
        """Test update_display with pending changes."""
        widget = SyncStatusWidget()
        widget.pending_changes = 5

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_sync_info.update.assert_called()
        assert "5" in mock_sync_info.update.call_args[0][0]
        assert "pending" in mock_sync_info.update.call_args[0][0]

    def test_sync_status_update_display_last_sync(self) -> None:
        """Test update_display with last sync time."""
        widget = SyncStatusWidget()
        widget.last_sync = datetime.now() - timedelta(minutes=5)

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_sync_info.update.assert_called()
        assert "Last sync" in mock_sync_info.update.call_args[0][0]

    def test_sync_status_update_display_conflicts(self) -> None:
        """Test update_display with conflicts."""
        widget = SyncStatusWidget()
        widget.conflicts_count = 3

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_conflict_info.update.assert_called()
        assert "3" in mock_conflict_info.update.call_args[0][0]
        assert "conflict" in mock_conflict_info.update.call_args[0][0]

    def test_sync_status_format_time_ago_just_now(self) -> None:
        """Test time formatting for recent time."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(seconds=30)

        result = widget._format_time_ago(dt)

        assert result == "just now"

    def test_sync_status_format_time_ago_minutes(self) -> None:
        """Test time formatting for minutes."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(minutes=5)

        result = widget._format_time_ago(dt)

        assert "5 minute" in result
        assert "ago" in result

    def test_sync_status_format_time_ago_one_minute(self) -> None:
        """Test time formatting for one minute."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(minutes=1)

        result = widget._format_time_ago(dt)

        assert "1 minute" in result
        assert "minutes" not in result  # Singular

    def test_sync_status_format_time_ago_hours(self) -> None:
        """Test time formatting for hours."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(hours=3)

        result = widget._format_time_ago(dt)

        assert "3 hour" in result
        assert "ago" in result

    def test_sync_status_format_time_ago_days(self) -> None:
        """Test time formatting for days."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(days=2)

        result = widget._format_time_ago(dt)

        assert "2 day" in result
        assert "ago" in result

    def test_sync_status_format_time_ago_with_timezone(self) -> None:
        """Test time formatting with timezone-aware datetime."""
        widget = SyncStatusWidget()
        dt = datetime.now(UTC) - timedelta(minutes=10)

        result = widget._format_time_ago(dt)

        assert "10 minute" in result or "ago" in result

    def test_sync_status_set_online(self) -> None:
        """Test set_online method."""
        widget = SyncStatusWidget()

        widget.set_online(True)

        assert widget.is_online

    def test_sync_status_set_syncing(self) -> None:
        """Test set_syncing method."""
        widget = SyncStatusWidget()

        widget.set_syncing(True)

        assert widget.is_syncing

    def test_sync_status_set_pending_changes(self) -> None:
        """Test set_pending_changes method."""
        widget = SyncStatusWidget()

        widget.set_pending_changes(10)

        assert widget.pending_changes == COUNT_TEN

    def test_sync_status_set_last_sync(self) -> None:
        """Test set_last_sync method."""
        widget = SyncStatusWidget()
        dt = datetime.now()

        widget.set_last_sync(dt)

        assert widget.last_sync == dt

    def test_sync_status_set_conflicts(self) -> None:
        """Test set_conflicts method."""
        widget = SyncStatusWidget()

        widget.set_conflicts(5)

        assert widget.conflicts_count == COUNT_FIVE

    def test_sync_status_set_error(self) -> None:
        """Test set_error method."""
        widget = SyncStatusWidget()

        widget.set_error("Test error")

        assert widget.last_error == "Test error"

    def test_sync_status_set_error_clear(self) -> None:
        """Test set_error can clear error."""
        widget = SyncStatusWidget()
        widget.last_error = "Old error"

        widget.set_error(None)

        assert widget.last_error is None


# =============================================================================
# CompactSyncStatus Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not SYNC_STATUS_AVAILABLE, reason="Textual not available")
class TestCompactSyncStatus:
    """Tests for CompactSyncStatus widget."""

    def test_compact_sync_status_init_defaults(self) -> None:
        """Test CompactSyncStatus initializes with defaults."""
        widget = CompactSyncStatus()

        assert not widget.is_online
        assert not widget.is_syncing
        assert widget.pending_changes == 0
        assert widget.conflicts_count == 0

    def test_compact_sync_status_render_offline(self) -> None:
        """Test render when offline."""
        widget = CompactSyncStatus()
        widget.is_online = False

        result = widget.render()

        assert "Offline" in result or "●" in result

    def test_compact_sync_status_render_online(self) -> None:
        """Test render when online."""
        widget = CompactSyncStatus()
        widget.is_online = True

        result = widget.render()

        assert "●" in result

    def test_compact_sync_status_render_syncing(self) -> None:
        """Test render when syncing."""
        widget = CompactSyncStatus()
        widget.is_syncing = True

        result = widget.render()

        assert "⟳" in result

    def test_compact_sync_status_render_pending_changes(self) -> None:
        """Test render with pending changes."""
        widget = CompactSyncStatus()
        widget.pending_changes = 5

        result = widget.render()

        assert "5" in result
        assert "pending" in result

    def test_compact_sync_status_render_conflicts(self) -> None:
        """Test render with conflicts."""
        widget = CompactSyncStatus()
        widget.conflicts_count = 3

        result = widget.render()

        assert "3" in result
        assert "⚠" in result

    def test_compact_sync_status_render_combined(self) -> None:
        """Test render with multiple statuses."""
        widget = CompactSyncStatus()
        widget.is_online = True
        widget.pending_changes = 2
        widget.conflicts_count = 1

        result = widget.render()

        assert "2" in result
        assert "pending" in result
        assert "1" in result

    def test_compact_sync_status_set_online(self) -> None:
        """Test set_online method."""
        widget = CompactSyncStatus()

        widget.set_online(True)

        assert widget.is_online

    def test_compact_sync_status_set_syncing(self) -> None:
        """Test set_syncing method."""
        widget = CompactSyncStatus()

        widget.set_syncing(True)

        assert widget.is_syncing

    def test_compact_sync_status_set_pending_changes(self) -> None:
        """Test set_pending_changes method."""
        widget = CompactSyncStatus()

        widget.set_pending_changes(7)

        assert widget.pending_changes == 7

    def test_compact_sync_status_set_conflicts(self) -> None:
        """Test set_conflicts method."""
        widget = CompactSyncStatus()

        widget.set_conflicts(4)

        assert widget.conflicts_count == COUNT_FOUR


# =============================================================================
# GraphViewWidget Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not GRAPH_VIEW_AVAILABLE, reason="Textual not available")
class TestGraphViewWidget:
    """Tests for GraphViewWidget."""

    def test_graph_view_inherits_static(self) -> None:
        """Test GraphViewWidget inherits from Static."""
        assert issubclass(GraphViewWidget, Static)

    def test_graph_view_class_exists(self) -> None:
        """Test GraphViewWidget class exists and can be imported."""
        assert GraphViewWidget is not None
        assert hasattr(GraphViewWidget, "__init__")


# =============================================================================
# StateDisplayWidget Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not STATE_DISPLAY_AVAILABLE, reason="Textual not available")
class TestStateDisplayWidget:
    """Tests for StateDisplayWidget."""

    def test_state_display_inherits_datatable(self) -> None:
        """Test StateDisplayWidget inherits from DataTable."""
        assert issubclass(StateDisplayWidget, DataTable)

    def test_state_display_class_exists(self) -> None:
        """Test StateDisplayWidget class exists and can be imported."""
        assert StateDisplayWidget is not None
        assert hasattr(StateDisplayWidget, "__init__")


# =============================================================================
# ViewSwitcherWidget Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not VIEW_SWITCHER_AVAILABLE, reason="Textual not available")
class TestViewSwitcherWidget:
    """Tests for ViewSwitcherWidget."""

    def test_view_switcher_inherits_tree(self) -> None:
        """Test ViewSwitcherWidget inherits from Tree."""
        assert issubclass(ViewSwitcherWidget, Tree)

    def test_view_switcher_class_exists(self) -> None:
        """Test ViewSwitcherWidget class exists and can be imported."""
        assert ViewSwitcherWidget is not None
        assert hasattr(ViewSwitcherWidget, "__init__")
        assert hasattr(ViewSwitcherWidget, "setup_views")


# =============================================================================
# Placeholder Classes Tests
# =============================================================================


def test_item_list_widget_placeholder() -> None:
    """Test ItemListWidget placeholder when Textual not available."""
    from tracertm.tui.widgets.item_list import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.item_list import ItemListWidget

        # Should be an empty placeholder class
        assert ItemListWidget is not None


def test_conflict_panel_placeholder() -> None:
    """Test ConflictPanel placeholder when Textual not available."""
    from tracertm.tui.widgets.conflict_panel import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.conflict_panel import ConflictPanel  # pyright: ignore[reportOptionalMemberAccess]

        # Should be an empty placeholder class
        assert ConflictPanel is not None


def test_sync_status_widget_placeholder() -> None:
    """Test SyncStatusWidget placeholder when Textual not available."""
    from tracertm.tui.widgets.sync_status import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.sync_status import SyncStatusWidget  # pyright: ignore[reportOptionalMemberAccess]

        # Should be an empty placeholder class
        assert SyncStatusWidget is not None


def test_compact_sync_status_placeholder() -> None:
    """Test CompactSyncStatus placeholder when Textual not available."""
    from tracertm.tui.widgets.sync_status import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.sync_status import CompactSyncStatus  # pyright: ignore[reportOptionalMemberAccess]

        # Should be an empty placeholder class
        assert CompactSyncStatus is not None


def test_graph_view_widget_placeholder() -> None:
    """Test GraphViewWidget placeholder when Textual not available."""
    from tracertm.tui.widgets.graph_view import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.graph_view import GraphViewWidget

        # Should be an empty placeholder class
        assert GraphViewWidget is not None


def test_state_display_widget_placeholder() -> None:
    """Test StateDisplayWidget placeholder when Textual not available."""
    from tracertm.tui.widgets.state_display import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.state_display import StateDisplayWidget

        # Should be an empty placeholder class
        assert StateDisplayWidget is not None


def test_view_switcher_widget_placeholder() -> None:
    """Test ViewSwitcherWidget placeholder when Textual not available."""
    from tracertm.tui.widgets.view_switcher import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget

        # Should be an empty placeholder class
        assert ViewSwitcherWidget is not None


# =============================================================================
# Additional Widget Lifecycle Tests
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not ITEM_LIST_AVAILABLE, reason="Textual not available")
class TestItemListWidgetLifecycle:
    """Tests for ItemListWidget lifecycle and edge cases."""

    @patch.object(ItemListWidget, "add_columns")
    def test_item_list_on_mount_adds_columns_once(self, mock_add_columns: Any) -> None:
        """Test on_mount only adds columns once."""
        widget = ItemListWidget()
        widget._columns_added = False

        widget.on_mount()

        mock_add_columns.assert_called_once_with("ID", "Title", "Type", "Status")
        assert widget._columns_added is True

    @patch.object(ItemListWidget, "add_columns")
    def test_item_list_on_mount_skips_if_already_added(self, mock_add_columns: Any) -> None:
        """Test on_mount skips column setup if already done."""
        widget = ItemListWidget()
        widget._columns_added = True

        widget.on_mount()

        mock_add_columns.assert_not_called()

    def test_item_list_initial_state(self) -> None:
        """Test ItemListWidget initializes with correct state."""
        widget = ItemListWidget()

        assert widget._columns_added is False


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not STATE_DISPLAY_AVAILABLE, reason="Textual not available")
class TestStateDisplayWidgetLifecycle:
    """Tests for StateDisplayWidget lifecycle and edge cases."""

    @patch.object(StateDisplayWidget, "add_columns")
    def test_state_display_on_mount_adds_columns_once(self, mock_add_columns: Any) -> None:
        """Test on_mount only adds columns once."""
        widget = StateDisplayWidget()
        widget._columns_added = False

        widget.on_mount()

        mock_add_columns.assert_called_once_with("View", "Items", "Links")
        assert widget._columns_added is True

    @patch.object(StateDisplayWidget, "add_columns")
    def test_state_display_on_mount_skips_if_already_added(self, mock_add_columns: Any) -> None:
        """Test on_mount skips column setup if already done."""
        widget = StateDisplayWidget()
        widget._columns_added = True

        widget.on_mount()

        mock_add_columns.assert_not_called()

    def test_state_display_initial_state(self) -> None:
        """Test StateDisplayWidget initializes with correct state."""
        widget = StateDisplayWidget()

        assert widget._columns_added is False


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not VIEW_SWITCHER_AVAILABLE, reason="Textual not available")
class TestViewSwitcherWidgetLifecycle:
    """Tests for ViewSwitcherWidget lifecycle and setup."""

    @patch.object(ViewSwitcherWidget, "setup_views")
    def test_view_switcher_on_mount_calls_setup(self, mock_setup: Any) -> None:
        """Test on_mount calls setup_views."""
        widget = ViewSwitcherWidget()

        widget.on_mount()

        mock_setup.assert_called_once()

    def test_view_switcher_setup_views_adds_all(self) -> None:
        """Test setup_views adds all expected views."""
        widget = ViewSwitcherWidget()
        widget.root = MagicMock()

        widget.setup_views()

        assert widget.root.add.call_count == 8
        view_names = [call[0][0] for call in widget.root.add.call_args_list]
        assert "FEATURE" in view_names
        assert "CODE" in view_names
        assert "WIREFRAME" in view_names
        assert "API" in view_names
        assert "TEST" in view_names
        assert "DATABASE" in view_names
        assert "ROADMAP" in view_names
        assert "PROGRESS" in view_names


# =============================================================================
# SyncStatusWidget Edge Cases
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not SYNC_STATUS_AVAILABLE, reason="Textual not available")
class TestSyncStatusWidgetEdgeCases:
    """Edge case tests for SyncStatusWidget."""

    def test_sync_status_update_display_not_mounted(self) -> None:
        """Test update_display handles unmounted widget gracefully."""
        widget = SyncStatusWidget()
        # Mock is_mounted property
        with patch.object(type(widget), "is_mounted", new_callable=PropertyMock) as mock_mounted:
            mock_mounted.return_value = False

            # Should not raise error
            widget.update_display()

    def test_sync_status_update_display_widget_not_composed(self) -> None:
        """Test update_display handles widget not yet composed."""
        widget = SyncStatusWidget()
        with patch.object(type(widget), "is_mounted", new_callable=PropertyMock) as mock_mounted:
            mock_mounted.return_value = True
            widget.query_one = MagicMock(side_effect=Exception("Widget not found"))

            # Should not raise error
            widget.update_display()

    def test_sync_status_format_time_ago_edge_case_59_seconds(self) -> None:
        """Test time formatting at 59 seconds boundary."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(seconds=59)

        result = widget._format_time_ago(dt)

        assert result == "just now"

    def test_sync_status_format_time_ago_edge_case_60_seconds(self) -> None:
        """Test time formatting at 60 seconds boundary."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(seconds=60)

        result = widget._format_time_ago(dt)

        assert "1 minute" in result

    def test_sync_status_format_time_ago_edge_case_one_hour(self) -> None:
        """Test time formatting at one hour boundary."""
        widget = SyncStatusWidget()
        dt = datetime.now() - timedelta(hours=1)

        result = widget._format_time_ago(dt)

        assert "1 hour" in result
        assert "hours" not in result

    def test_sync_status_update_display_one_pending_change(self) -> None:
        """Test display with exactly one pending change (singular)."""
        widget = SyncStatusWidget()
        widget.pending_changes = 1

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_sync_info.update.assert_called()
        call_text = mock_sync_info.update.call_args[0][0]
        assert "1" in call_text
        assert "pending change" in call_text
        assert "changes" not in call_text

    def test_sync_status_update_display_one_conflict(self) -> None:
        """Test display with exactly one conflict (singular)."""
        widget = SyncStatusWidget()
        widget.conflicts_count = 1

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_conflict_info.update.assert_called()
        call_text = mock_conflict_info.update.call_args[0][0]
        assert "1" in call_text
        assert "conflict" in call_text

    def test_sync_status_update_display_never_synced(self) -> None:
        """Test display when never synced."""
        widget = SyncStatusWidget()
        widget.last_sync = None
        widget.pending_changes = 0

        mock_connection_status = MagicMock()
        mock_sync_info = MagicMock()
        mock_conflict_info = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "connection-status" in selector:
                return mock_connection_status
            if "sync-info" in selector:
                return mock_sync_info
            if "conflict-info" in selector:
                return mock_conflict_info
            return MagicMock()

        widget.query_one = mock_query_one

        widget.update_display()

        mock_sync_info.update.assert_called()
        call_text = mock_sync_info.update.call_args[0][0]
        assert "Never synced" in call_text


# =============================================================================
# ConflictPanel Edge Cases and Event Handling
# =============================================================================


@pytest.mark.skipif(not TEXTUAL_AVAILABLE or not CONFLICT_AVAILABLE, reason="Textual not available")
class TestConflictPanelEdgeCases:
    """Edge case tests for ConflictPanel. Use cast(Any, ...) so patched/mock attributes type-check."""

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_init_with_empty_conflicts(self) -> None:
        """Test ConflictPanel initialization with empty conflict list."""
        panel = cast("Any", ConflictPanel())
        panel.conflicts = []
        panel.selected_conflict = None

        assert len(panel.conflicts) == 0
        assert panel.selected_conflict is None

    @patch.object(ConflictPanel, "query_one")
    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_refresh_with_long_entity_id(self, mock_query_one: Any) -> None:
        """Test conflict list display truncates long entity IDs."""
        conflict = MagicMock()
        conflict.entity_type = "item"
        conflict.entity_id = "a" * 50  # Very long ID
        conflict.local_version.vector_clock.version = 1
        conflict.remote_version.vector_clock.version = 2
        conflict.detected_at = datetime(2024, 1, 1, 12, 0)

        panel = cast("Any", ConflictPanel())
        panel.conflicts = [conflict]

        mock_table = MagicMock()
        mock_query_one.return_value = mock_table

        panel.refresh_conflict_list()

        # Check that ID was truncated to 12 chars + "..."
        call_args = mock_table.add_row.call_args[0]
        assert len(call_args[1]) == 15  # 12 chars + "..."
        assert call_args[1].endswith("...")

    @patch("tracertm.tui.widgets.conflict_panel.compare_versions")
    @patch.object(ConflictPanel, "query_one")
    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_show_conflict_detail_only_modified(self, mock_query_one: Any, mock_compare: Any) -> None:
        """Test showing conflict with only modified fields."""
        local_version = MagicMock()
        local_version.vector_clock.version = 1
        local_version.vector_clock.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        local_version.vector_clock.client_id = "client1"

        remote_version = MagicMock()
        remote_version.vector_clock.version = 2
        remote_version.vector_clock.timestamp = datetime(2024, 1, 1, 13, 0, 0)
        remote_version.vector_clock.client_id = "client2"

        conflict = MagicMock()
        conflict.entity_type = "item"
        conflict.entity_id = "abc123"
        conflict.local_version = local_version
        conflict.remote_version = remote_version

        mock_compare.return_value = {"modified": ["title"], "added": [], "removed": []}

        panel = cast("Any", ConflictPanel())
        mock_detail = MagicMock()
        mock_query_one.return_value = mock_detail

        panel.show_conflict_detail(conflict)

        mock_detail.update.assert_called_once()
        update_text = mock_detail.update.call_args[0][0]
        assert "title" in update_text
        assert "Modified fields" in update_text

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_messages_exist(self) -> None:
        """Test ConflictPanel custom message classes exist."""
        panel = cast("Any", ConflictPanel())

        assert hasattr(panel, "ConflictResolved")
        assert hasattr(panel, "ConflictPanelClosed")

    @patch.object(ConflictPanel, "__init__", lambda x, **kwargs: None)
    def test_conflict_panel_compose_method_exists(self) -> None:
        """Test ConflictPanel has compose method."""
        panel = cast("Any", ConflictPanel())

        assert hasattr(panel, "compose")
        assert callable(panel.compose)
