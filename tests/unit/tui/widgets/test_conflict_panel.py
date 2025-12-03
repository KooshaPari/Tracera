"""
Comprehensive tests for tracertm.tui.widgets.conflict_panel module.

Tests ConflictPanel widget including rendering, conflict display,
resolution actions, and event handling.
Coverage target: 80%+ of 101 statements
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

# Skip all tests if Textual not available
pytest.importorskip("textual")

from tracertm.tui.widgets.conflict_panel import ConflictPanel


@pytest.fixture
def mock_conflicts():
    """Create mock conflict objects."""
    conflicts = []
    for i in range(3):
        conflict = MagicMock()
        conflict.entity_type = "item"
        conflict.entity_id = f"item-{i}1234567890"
        conflict.detected_at = datetime(2024, 1, 1 + i, 12, 0)

        # Local version
        local_version = MagicMock()
        local_vector_clock = MagicMock()
        local_vector_clock.version = i + 1
        local_vector_clock.timestamp = datetime(2024, 1, 1, 12, 0)
        local_vector_clock.client_id = "client-local"
        local_version.vector_clock = local_vector_clock
        conflict.local_version = local_version

        # Remote version
        remote_version = MagicMock()
        remote_vector_clock = MagicMock()
        remote_vector_clock.version = i + 2
        remote_vector_clock.timestamp = datetime(2024, 1, 2, 12, 0)
        remote_vector_clock.client_id = "client-remote"
        remote_version.vector_clock = remote_vector_clock
        conflict.remote_version = remote_version

        conflicts.append(conflict)

    return conflicts


class TestConflictPanelInitialization:
    """Test ConflictPanel initialization."""

    def test_init_with_conflicts(self, mock_conflicts):
        """Test panel initializes with conflicts list."""
        panel = ConflictPanel(conflicts=mock_conflicts)

        assert panel.conflicts == mock_conflicts
        assert panel.selected_conflict is None

    def test_init_empty_conflicts(self):
        """Test panel initializes with empty conflicts list."""
        panel = ConflictPanel(conflicts=[])

        assert panel.conflicts == []
        assert panel.selected_conflict is None

    def test_init_default_conflicts(self):
        """Test panel initializes with None defaults to empty list."""
        panel = ConflictPanel()

        assert panel.conflicts == []


class TestConflictPanelComposition:
    """Test widget composition."""

    @pytest.mark.asyncio
    async def test_compose_creates_widgets(self, mock_conflicts, textual_app_context):
        """Test compose method creates all required widgets."""
        async with textual_app_context() as (app, pilot):
            panel = ConflictPanel(conflicts=mock_conflicts)

            # Mount panel in app context to properly initialize compose
            await app.mount(panel)
            await pilot.pause()

            # Verify panel has children widgets
            assert len(panel.children) > 0
            # Check for key widgets like DataTable and Static
            assert panel.query("DataTable")
            assert panel.query("Static")

    def test_bindings_configured(self):
        """Test keyboard bindings are properly configured."""
        bindings = ConflictPanel.BINDINGS

        binding_keys = [b.key for b in bindings]
        assert "l" in binding_keys  # Use local
        assert "r" in binding_keys  # Use remote
        assert "m" in binding_keys  # Merge manually
        assert "escape" in binding_keys  # Close


class TestConflictListDisplay:
    """Test conflict list display functionality."""

    def test_refresh_conflict_list(self, mock_conflicts):
        """Test refreshing conflict list populates table."""
        panel = ConflictPanel(conflicts=mock_conflicts)

        mock_table = MagicMock()
        panel.query_one = Mock(return_value=mock_table)

        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        assert mock_table.add_row.call_count == 3  # 3 conflicts

    def test_refresh_conflict_list_empty(self):
        """Test refreshing empty conflict list."""
        panel = ConflictPanel(conflicts=[])

        mock_table = MagicMock()
        panel.query_one = Mock(return_value=mock_table)

        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_not_called()

    def test_on_mount_refreshes_list(self, mock_conflicts):
        """Test on_mount calls refresh_conflict_list."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.refresh_conflict_list = Mock()

        panel.on_mount()

        panel.refresh_conflict_list.assert_called_once()


class TestConflictSelection:
    """Test conflict selection handling."""

    def test_on_data_table_row_selected(self, mock_conflicts):
        """Test selecting a conflict row."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.show_conflict_detail = Mock()

        # Mock event
        event = MagicMock()
        event.row_index = 1

        panel.on_data_table_row_selected(event)

        assert panel.selected_conflict == mock_conflicts[1]
        panel.show_conflict_detail.assert_called_once_with(mock_conflicts[1])

    def test_on_data_table_row_selected_invalid_index(self, mock_conflicts):
        """Test selecting invalid row index does nothing."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.show_conflict_detail = Mock()

        # Mock event with out-of-bounds index
        event = MagicMock()
        event.row_index = 99

        panel.on_data_table_row_selected(event)

        assert panel.selected_conflict is None
        panel.show_conflict_detail.assert_not_called()


class TestConflictDetailDisplay:
    """Test conflict detail display."""

    def test_show_conflict_detail(self, mock_conflicts):
        """Test showing detailed conflict information."""
        panel = ConflictPanel(conflicts=mock_conflicts)

        mock_static = MagicMock()
        panel.query_one = Mock(return_value=mock_static)

        with patch("tracertm.storage.conflict_resolver.compare_versions") as mock_compare:
            mock_compare.return_value = {
                "modified": ["field1", "field2"],
                "added": ["field3"],
                "removed": ["field4"]
            }

            panel.show_conflict_detail(mock_conflicts[0])

            mock_static.update.assert_called_once()
            # Verify detail text contains key information
            call_args = mock_static.update.call_args[0][0]
            assert "item" in call_args.lower()
            assert "local version" in call_args.lower()
            assert "remote version" in call_args.lower()


class TestResolutionActions:
    """Test conflict resolution actions."""

    def test_action_resolve_local(self, mock_conflicts):
        """Test resolving conflict with local version."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.selected_conflict = mock_conflicts[0]
        panel.post_message = Mock()

        panel.action_resolve_local()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "local"
        assert message.conflict == mock_conflicts[0]

    def test_action_resolve_local_no_selection(self):
        """Test resolve local with no conflict selected does nothing."""
        panel = ConflictPanel(conflicts=[])
        panel.selected_conflict = None
        panel.post_message = Mock()

        panel.action_resolve_local()

        panel.post_message.assert_not_called()

    def test_action_resolve_remote(self, mock_conflicts):
        """Test resolving conflict with remote version."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.selected_conflict = mock_conflicts[0]
        panel.post_message = Mock()

        panel.action_resolve_remote()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "remote"

    def test_action_resolve_manual(self, mock_conflicts):
        """Test resolving conflict manually."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.selected_conflict = mock_conflicts[0]
        panel.post_message = Mock()

        panel.action_resolve_manual()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "manual"

    def test_action_close(self):
        """Test closing conflict panel."""
        panel = ConflictPanel(conflicts=[])
        panel.post_message = Mock()

        panel.action_close()

        panel.post_message.assert_called_once()


class TestButtonHandling:
    """Test button press handling."""

    def test_on_button_pressed_local(self, mock_conflicts):
        """Test pressing 'Use Local' button."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.action_resolve_local = Mock()

        event = MagicMock()
        event.button.id = "btn-local"

        panel.on_button_pressed(event)

        panel.action_resolve_local.assert_called_once()

    def test_on_button_pressed_remote(self, mock_conflicts):
        """Test pressing 'Use Remote' button."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.action_resolve_remote = Mock()

        event = MagicMock()
        event.button.id = "btn-remote"

        panel.on_button_pressed(event)

        panel.action_resolve_remote.assert_called_once()

    def test_on_button_pressed_manual(self, mock_conflicts):
        """Test pressing 'Merge Manually' button."""
        panel = ConflictPanel(conflicts=mock_conflicts)
        panel.action_resolve_manual = Mock()

        event = MagicMock()
        event.button.id = "btn-manual"

        panel.on_button_pressed(event)

        panel.action_resolve_manual.assert_called_once()

    def test_on_button_pressed_close(self):
        """Test pressing 'Close' button."""
        panel = ConflictPanel(conflicts=[])
        panel.action_close = Mock()

        event = MagicMock()
        event.button.id = "btn-close"

        panel.on_button_pressed(event)

        panel.action_close.assert_called_once()
