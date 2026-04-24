"""Comprehensive tests for ConflictPanel widget.

Tests panel initialization, conflict display, conflict selection,
detail view, resolution actions, and event handling.
Coverage target: 80%+ (270 lines total)
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_TWO

# Skip all tests if Textual not available
pytest.importorskip("textual")

from tracertm.tui.widgets.conflict_panel import ConflictPanel


def _panel(*args: Any, **kwargs: Any) -> Any:
    """Return a ConflictPanel; typed as Any so tests can assign mocks and access attributes."""
    return ConflictPanel(*args, **kwargs)


class TestConflictPanelInitialization:
    """Test ConflictPanel initialization."""

    def test_init_creates_panel(self) -> None:
        """Test ConflictPanel initializes correctly."""
        panel = _panel()

        assert panel is not None
        assert panel.conflicts == []
        assert panel.selected_conflict is None

    def test_init_with_conflicts(self) -> None:
        """Test ConflictPanel accepts conflicts list."""
        mock_conflict1 = MagicMock()
        mock_conflict2 = MagicMock()
        conflicts = [mock_conflict1, mock_conflict2]

        panel = _panel(conflicts=conflicts)

        assert len(panel.conflicts) == COUNT_TWO
        assert panel.conflicts[0] == mock_conflict1

    def test_init_with_custom_id(self) -> None:
        """Test ConflictPanel accepts custom ID."""
        panel = _panel(id="custom-conflict-panel")

        assert panel is not None
        assert panel.id == "custom-conflict-panel"

    def test_bindings_configured(self) -> None:
        """Test ConflictPanel has correct key bindings."""
        panel = _panel()

        binding_keys = [b.key for b in panel.BINDINGS]
        assert "l" in binding_keys  # Use local
        assert "r" in binding_keys  # Use remote
        assert "m" in binding_keys  # Merge manually
        assert "escape" in binding_keys  # Close

    def test_compose_creates_children(self) -> None:
        """Test compose creates correct child widgets."""
        panel = _panel()
        children = list(panel.compose())

        # Should create title, list, detail sections, and buttons
        assert len(children) > 0


class TestConflictPanelDisplay:
    """Test conflict list display."""

    @patch.object(ConflictPanel, "query_one")
    def test_refresh_conflict_list_empty(self, mock_query_one: Any) -> None:
        """Test refresh_conflict_list with no conflicts."""
        mock_table = MagicMock()
        mock_query_one.return_value = mock_table

        panel = _panel(conflicts=[])
        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_not_called()

    @patch.object(ConflictPanel, "query_one")
    def test_refresh_conflict_list_with_conflicts(self, mock_query_one: Any) -> None:
        """Test refresh_conflict_list displays conflicts."""
        mock_table = MagicMock()
        mock_query_one.return_value = mock_table

        # Create mock conflicts
        mock_conflict1 = MagicMock()
        mock_conflict1.entity_type = "Item"
        mock_conflict1.entity_id = str(uuid4())
        mock_conflict1.local_version.vector_clock.version = 1
        mock_conflict1.remote_version.vector_clock.version = 2
        mock_conflict1.detected_at = datetime.now()

        mock_conflict2 = MagicMock()
        mock_conflict2.entity_type = "Link"
        mock_conflict2.entity_id = str(uuid4())
        mock_conflict2.local_version.vector_clock.version = 3
        mock_conflict2.remote_version.vector_clock.version = 4
        mock_conflict2.detected_at = datetime.now()

        panel = _panel(conflicts=[mock_conflict1, mock_conflict2])
        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        assert mock_table.add_row.call_count == COUNT_TWO


class TestConflictPanelSelection:
    """Test conflict selection and detail view."""

    def test_on_data_table_row_selected_valid(self) -> None:
        """Test selecting a conflict from the table."""
        mock_conflict = MagicMock()
        panel = _panel(conflicts=[mock_conflict])
        show_detail_mock = MagicMock()
        panel.show_conflict_detail = show_detail_mock

        mock_event = MagicMock()
        mock_event.row_index = 0

        panel.on_data_table_row_selected(mock_event)

        assert panel.selected_conflict == mock_conflict
        show_detail_mock.assert_called_once_with(mock_conflict)

    def test_on_data_table_row_selected_invalid_index(self) -> None:
        """Test selecting invalid row index does nothing."""
        mock_conflict = MagicMock()
        panel = _panel(conflicts=[mock_conflict])
        show_detail_mock = MagicMock()
        panel.show_conflict_detail = show_detail_mock

        mock_event = MagicMock()
        mock_event.row_index = 99  # Out of bounds

        panel.on_data_table_row_selected(mock_event)

        assert panel.selected_conflict is None
        show_detail_mock.assert_not_called()


class TestConflictPanelDetailView:
    """Test conflict detail display."""

    @patch("tracertm.tui.widgets.conflict_panel.compare_versions")
    @patch.object(ConflictPanel, "query_one")
    def test_show_conflict_detail(self, mock_query_one: Any, mock_compare: Any) -> None:
        """Test show_conflict_detail displays conflict details."""
        mock_detail_content = MagicMock()
        mock_query_one.return_value = mock_detail_content

        # Create mock conflict
        mock_conflict = MagicMock()
        mock_conflict.entity_type = "Item"
        mock_conflict.entity_id = str(uuid4())

        mock_local = MagicMock()
        mock_local.vector_clock.version = 1
        mock_local.vector_clock.timestamp = datetime.now()
        mock_local.vector_clock.client_id = "client-1"

        mock_remote = MagicMock()
        mock_remote.vector_clock.version = 2
        mock_remote.vector_clock.timestamp = datetime.now()
        mock_remote.vector_clock.client_id = "client-2"

        mock_conflict.local_version = mock_local
        mock_conflict.remote_version = mock_remote

        mock_compare.return_value = {
            "modified": ["title", "status"],
            "added": ["description"],
            "removed": ["old_field"],
        }

        panel = _panel()
        panel.show_conflict_detail(mock_conflict)

        mock_detail_content.update.assert_called_once()
        # Check that detail text includes key information
        call_args = str(mock_detail_content.update.call_args)
        assert "Entity:" in call_args or "Version:" in call_args or "Data Differences:" in call_args

    @patch("tracertm.tui.widgets.conflict_panel.compare_versions")
    @patch.object(ConflictPanel, "query_one")
    def test_show_conflict_detail_with_differences(self, mock_query_one: Any, mock_compare: Any) -> None:
        """Test show_conflict_detail includes difference information."""
        mock_detail_content = MagicMock()
        mock_query_one.return_value = mock_detail_content

        mock_conflict = MagicMock()
        mock_conflict.entity_type = "Item"
        mock_conflict.entity_id = str(uuid4())

        mock_local = MagicMock()
        mock_local.vector_clock.version = 1
        mock_local.vector_clock.timestamp = datetime.now()
        mock_local.vector_clock.client_id = "client-1"

        mock_remote = MagicMock()
        mock_remote.vector_clock.version = 2
        mock_remote.vector_clock.timestamp = datetime.now()
        mock_remote.vector_clock.client_id = "client-2"

        mock_conflict.local_version = mock_local
        mock_conflict.remote_version = mock_remote

        mock_compare.return_value = {"modified": ["title"], "added": ["description"], "removed": []}

        panel = _panel()
        panel.show_conflict_detail(mock_conflict)

        # Should call compare_versions
        mock_compare.assert_called_once_with(mock_local, mock_remote)


class TestConflictPanelResolutionActions:
    """Test conflict resolution actions."""

    def test_action_resolve_local(self) -> None:
        """Test action_resolve_local posts message."""
        mock_conflict = MagicMock()
        panel = _panel(conflicts=[mock_conflict])
        panel.selected_conflict = mock_conflict
        post_message_mock = MagicMock()
        panel.post_message = post_message_mock

        panel.action_resolve_local()

        post_message_mock.assert_called_once()
        # Check message type and strategy
        message = post_message_mock.call_args[0][0]
        assert hasattr(message, "conflict")
        assert hasattr(message, "strategy")
        assert message.strategy == "local"

    def test_action_resolve_local_no_selection(self) -> None:
        """Test action_resolve_local does nothing without selection."""
        panel = _panel()
        panel.selected_conflict = None
        post_message_mock = MagicMock()
        panel.post_message = post_message_mock

        panel.action_resolve_local()

        post_message_mock.assert_not_called()

    def test_action_resolve_remote(self) -> None:
        """Test action_resolve_remote posts message."""
        mock_conflict = MagicMock()
        panel = _panel(conflicts=[mock_conflict])
        panel.selected_conflict = mock_conflict
        post_message_mock = MagicMock()
        panel.post_message = post_message_mock

        panel.action_resolve_remote()

        post_message_mock.assert_called_once()
        message = post_message_mock.call_args[0][0]
        assert message.strategy == "remote"

    def test_action_resolve_manual(self) -> None:
        """Test action_resolve_manual posts message."""
        mock_conflict = MagicMock()
        panel = _panel(conflicts=[mock_conflict])
        panel.selected_conflict = mock_conflict
        post_message_mock = MagicMock()
        panel.post_message = post_message_mock

        panel.action_resolve_manual()

        post_message_mock.assert_called_once()
        message = post_message_mock.call_args[0][0]
        assert message.strategy == "manual"

    def test_action_close(self) -> None:
        """Test action_close posts close message."""
        panel = _panel()
        post_message_mock = MagicMock()
        panel.post_message = post_message_mock

        panel.action_close()

        post_message_mock.assert_called_once()


class TestConflictPanelButtonHandling:
    """Test button press handling."""

    def test_on_button_pressed_local(self) -> None:
        """Test button press triggers local resolution."""
        panel = _panel()
        action_mock = MagicMock()
        panel.action_resolve_local = action_mock

        mock_button = MagicMock()
        mock_button.id = "btn-local"
        mock_event = MagicMock()
        mock_event.button = mock_button

        panel.on_button_pressed(mock_event)

        action_mock.assert_called_once()

    def test_on_button_pressed_remote(self) -> None:
        """Test button press triggers remote resolution."""
        panel = _panel()
        action_mock = MagicMock()
        panel.action_resolve_remote = action_mock

        mock_button = MagicMock()
        mock_button.id = "btn-remote"
        mock_event = MagicMock()
        mock_event.button = mock_button

        panel.on_button_pressed(mock_event)

        action_mock.assert_called_once()

    def test_on_button_pressed_manual(self) -> None:
        """Test button press triggers manual resolution."""
        panel = _panel()
        action_mock = MagicMock()
        panel.action_resolve_manual = action_mock

        mock_button = MagicMock()
        mock_button.id = "btn-manual"
        mock_event = MagicMock()
        mock_event.button = mock_button

        panel.on_button_pressed(mock_event)

        action_mock.assert_called_once()

    def test_on_button_pressed_close(self) -> None:
        """Test button press triggers close."""
        panel = _panel()
        action_mock = MagicMock()
        panel.action_close = action_mock

        mock_button = MagicMock()
        mock_button.id = "btn-close"
        mock_event = MagicMock()
        mock_event.button = mock_button

        panel.on_button_pressed(mock_event)

        action_mock.assert_called_once()

    def test_on_button_pressed_unknown(self) -> None:
        """Test button press with unknown button ID does nothing."""
        panel = _panel()
        action_local_mock = MagicMock()
        action_remote_mock = MagicMock()
        action_manual_mock = MagicMock()
        action_close_mock = MagicMock()
        panel.action_resolve_local = action_local_mock
        panel.action_resolve_remote = action_remote_mock
        panel.action_resolve_manual = action_manual_mock
        panel.action_close = action_close_mock

        mock_button = MagicMock()
        mock_button.id = "unknown-button"
        mock_event = MagicMock()
        mock_event.button = mock_button

        panel.on_button_pressed(mock_event)

        # None of the actions should be called
        action_local_mock.assert_not_called()
        action_remote_mock.assert_not_called()
        action_manual_mock.assert_not_called()
        action_close_mock.assert_not_called()


class TestConflictPanelMessages:
    """Test custom message classes."""

    def test_conflict_resolved_message(self) -> None:
        """Test ConflictResolved message structure."""
        mock_conflict = MagicMock()
        panel = _panel()
        message = type(panel).ConflictResolved(conflict=mock_conflict, strategy="local")

        assert message.conflict == mock_conflict
        assert message.strategy == "local"

    def test_conflict_panel_closed_message(self) -> None:
        """Test ConflictPanelClosed message can be created."""
        panel = _panel()
        message = type(panel).ConflictPanelClosed()

        assert message is not None


class TestConflictPanelIntegration:
    """Integration tests for ConflictPanel."""

    @patch.object(ConflictPanel, "query_one")
    def test_on_mount_refreshes_list(self, mock_query_one: Any) -> None:
        """Test on_mount calls refresh_conflict_list."""
        mock_table = MagicMock()
        mock_query_one.return_value = mock_table

        panel = _panel()
        panel.on_mount()

        mock_table.clear.assert_called_once()

    @patch("tracertm.tui.widgets.conflict_panel.compare_versions")
    @patch.object(ConflictPanel, "query_one")
    def test_full_workflow_selection_to_resolution(self, mock_query_one: Any, mock_compare: Any) -> None:
        """Test full workflow from selection to resolution."""
        # Setup mocks
        mock_table = MagicMock()
        mock_detail = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            if "table" in selector:
                return mock_table
            if "detail" in selector:
                return mock_detail
            return MagicMock()

        mock_query_one.side_effect = query_side_effect

        mock_compare.return_value = {"modified": [], "added": [], "removed": []}

        # Create conflict
        mock_conflict = MagicMock()
        mock_conflict.entity_type = "Item"
        mock_conflict.entity_id = str(uuid4())
        mock_conflict.local_version.vector_clock.version = 1
        mock_conflict.local_version.vector_clock.timestamp = datetime.now()
        mock_conflict.local_version.vector_clock.client_id = "client-1"
        mock_conflict.remote_version.vector_clock.version = 2
        mock_conflict.remote_version.vector_clock.timestamp = datetime.now()
        mock_conflict.remote_version.vector_clock.client_id = "client-2"
        mock_conflict.detected_at = datetime.now()

        panel = _panel(conflicts=[mock_conflict])
        post_message_mock = MagicMock()
        panel.post_message = post_message_mock

        # Select conflict
        mock_event = MagicMock()
        mock_event.row_index = 0
        panel.on_data_table_row_selected(mock_event)

        assert panel.selected_conflict == mock_conflict

        # Resolve conflict
        panel.action_resolve_local()

        post_message_mock.assert_called_once()


class TestConflictPanelAvailability:
    """Test widget availability."""

    def test_conflict_panel_available(self) -> None:
        """Test ConflictPanel is available when Textual is installed."""
        from tracertm.tui.widgets import conflict_panel

        assert hasattr(conflict_panel, "ConflictPanel")
        assert conflict_panel.TEXTUAL_AVAILABLE is True
