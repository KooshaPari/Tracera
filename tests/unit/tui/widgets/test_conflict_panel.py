"""Comprehensive tests for tracertm.tui.widgets.conflict_panel module.

Tests ConflictPanel widget including rendering, conflict display,
resolution actions, and event handling.
Coverage target: 80%+ of 101 statements
"""

from datetime import datetime
from typing import Any, cast
from unittest.mock import MagicMock, Mock, patch

import pytest

from tests.test_constants import COUNT_THREE

# Skip all tests if Textual not available
pytest.importorskip("textual")

from tracertm.tui.widgets.conflict_panel import ConflictPanel


def _panel(*args: Any, **kwargs: Any) -> Any:
    """Return ConflictPanel as Any so tests can assign mocks and access attributes without type errors."""
    return cast("Any", ConflictPanel(*args, **kwargs))


@pytest.fixture
def mock_conflicts() -> None:
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

    def test_init_with_conflicts(self, mock_conflicts: Any) -> None:
        """Test panel initializes with conflicts list."""
        panel = _panel(conflicts=mock_conflicts)

        assert getattr(panel, "conflicts", None) == mock_conflicts
        assert getattr(panel, "selected_conflict", None) is None

    def test_init_empty_conflicts(self) -> None:
        """Test panel initializes with empty conflicts list."""
        panel = _panel(conflicts=[])

        assert getattr(panel, "conflicts", None) == []
        assert getattr(panel, "selected_conflict", None) is None

    def test_init_default_conflicts(self) -> None:
        """Test panel initializes with None defaults to empty list."""
        panel = _panel()

        assert getattr(panel, "conflicts", None) == []


class TestConflictPanelComposition:
    """Test widget composition."""

    @pytest.mark.asyncio
    async def test_compose_creates_widgets(self, mock_conflicts: Any, textual_app_context: Any) -> None:
        """Test compose method creates all required widgets."""
        async with textual_app_context() as (app, pilot):
            panel = _panel(conflicts=mock_conflicts)

            # Mount panel in app context to properly initialize compose
            await app.mount(panel)
            await pilot.pause()

            # Verify panel has children widgets
            assert len(panel.children) > 0
            # Check for key widgets like DataTable and Static
            assert panel.query("DataTable")
            assert panel.query("Static")

    def test_bindings_configured(self) -> None:
        """Test keyboard bindings are properly configured."""
        bindings = getattr(ConflictPanel, "BINDINGS", [])

        binding_keys = [b.key for b in bindings]
        assert "l" in binding_keys  # Use local
        assert "r" in binding_keys  # Use remote
        assert "m" in binding_keys  # Merge manually
        assert "escape" in binding_keys  # Close


class TestConflictListDisplay:
    """Test conflict list display functionality."""

    def test_refresh_conflict_list(self, mock_conflicts: Any) -> None:
        """Test refreshing conflict list populates table."""
        panel = _panel(conflicts=mock_conflicts)

        mock_table = MagicMock()
        panel.query_one = Mock(return_value=mock_table)

        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        assert mock_table.add_row.call_count == COUNT_THREE  # 3 conflicts

    def test_refresh_conflict_list_empty(self) -> None:
        """Test refreshing empty conflict list."""
        panel = _panel(conflicts=[])

        mock_table = MagicMock()
        panel.query_one = Mock(return_value=mock_table)

        panel.refresh_conflict_list()

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_not_called()

    def test_on_mount_refreshes_list(self, mock_conflicts: Any) -> None:
        """Test on_mount calls refresh_conflict_list."""
        panel = _panel(conflicts=mock_conflicts)
        panel.refresh_conflict_list = Mock()

        panel.on_mount()

        panel.refresh_conflict_list.assert_called_once()


class TestConflictSelection:
    """Test conflict selection handling."""

    def test_on_data_table_row_selected(self, mock_conflicts: Any) -> None:
        """Test selecting a conflict row."""
        panel = _panel(conflicts=mock_conflicts)
        panel.show_conflict_detail = Mock()

        # Mock event
        event = MagicMock()
        event.row_index = 1

        panel.on_data_table_row_selected(event)

        assert panel.selected_conflict == mock_conflicts[1]
        panel.show_conflict_detail.assert_called_once_with(mock_conflicts[1])

    def test_on_data_table_row_selected_invalid_index(self, mock_conflicts: Any) -> None:
        """Test selecting invalid row index does nothing."""
        panel = _panel(conflicts=mock_conflicts)
        panel.show_conflict_detail = Mock()

        # Mock event with out-of-bounds index
        event = MagicMock()
        event.row_index = 99

        panel.on_data_table_row_selected(event)

        assert panel.selected_conflict is None
        panel.show_conflict_detail.assert_not_called()


class TestConflictDetailDisplay:
    """Test conflict detail display."""

    def test_show_conflict_detail(self, mock_conflicts: Any) -> None:
        """Test showing detailed conflict information."""
        panel = _panel(conflicts=mock_conflicts)

        mock_static = MagicMock()
        panel.query_one = Mock(return_value=mock_static)

        with patch("tracertm.storage.conflict_resolver.compare_versions") as mock_compare:
            mock_compare.return_value = {"modified": ["field1", "field2"], "added": ["field3"], "removed": ["field4"]}

            panel.show_conflict_detail(mock_conflicts[0])

            mock_static.update.assert_called_once()
            # Verify detail text contains key information
            call_args = mock_static.update.call_args[0][0]
            assert "item" in call_args.lower()
            assert "local version" in call_args.lower()
            assert "remote version" in call_args.lower()


class TestResolutionActions:
    """Test conflict resolution actions."""

    def test_action_resolve_local(self, mock_conflicts: Any) -> None:
        """Test resolving conflict with local version."""
        panel = _panel(conflicts=mock_conflicts)
        panel.selected_conflict = mock_conflicts[0]
        panel.post_message = Mock()

        panel.action_resolve_local()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "local"
        assert message.conflict == mock_conflicts[0]

    def test_action_resolve_local_no_selection(self) -> None:
        """Test resolve local with no conflict selected does nothing."""
        panel = _panel(conflicts=[])
        panel.selected_conflict = None
        panel.post_message = Mock()

        panel.action_resolve_local()

        panel.post_message.assert_not_called()

    def test_action_resolve_remote(self, mock_conflicts: Any) -> None:
        """Test resolving conflict with remote version."""
        panel = _panel(conflicts=mock_conflicts)
        panel.selected_conflict = mock_conflicts[0]
        panel.post_message = Mock()

        panel.action_resolve_remote()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "remote"

    def test_action_resolve_manual(self, mock_conflicts: Any) -> None:
        """Test resolving conflict manually."""
        panel = _panel(conflicts=mock_conflicts)
        panel.selected_conflict = mock_conflicts[0]
        panel.post_message = Mock()

        panel.action_resolve_manual()

        panel.post_message.assert_called_once()
        message = panel.post_message.call_args[0][0]
        assert message.strategy == "manual"

    def test_action_close(self) -> None:
        """Test closing conflict panel."""
        panel = _panel(conflicts=[])
        panel.post_message = Mock()

        panel.action_close()

        panel.post_message.assert_called_once()


class TestButtonHandling:
    """Test button press handling."""

    def test_on_button_pressed_local(self, mock_conflicts: Any) -> None:
        """Test pressing 'Use Local' button."""
        panel = _panel(conflicts=mock_conflicts)
        panel.action_resolve_local = Mock()

        event = MagicMock()
        event.button.id = "btn-local"

        panel.on_button_pressed(event)

        panel.action_resolve_local.assert_called_once()

    def test_on_button_pressed_remote(self, mock_conflicts: Any) -> None:
        """Test pressing 'Use Remote' button."""
        panel = _panel(conflicts=mock_conflicts)
        panel.action_resolve_remote = Mock()

        event = MagicMock()
        event.button.id = "btn-remote"

        panel.on_button_pressed(event)

        panel.action_resolve_remote.assert_called_once()

    def test_on_button_pressed_manual(self, mock_conflicts: Any) -> None:
        """Test pressing 'Merge Manually' button."""
        panel = _panel(conflicts=mock_conflicts)
        panel.action_resolve_manual = Mock()

        event = MagicMock()
        event.button.id = "btn-manual"

        panel.on_button_pressed(event)

        panel.action_resolve_manual.assert_called_once()

    def test_on_button_pressed_close(self) -> None:
        """Test pressing 'Close' button."""
        panel = _panel(conflicts=[])
        panel.action_close = Mock()

        event = MagicMock()
        event.button.id = "btn-close"

        panel.on_button_pressed(event)

        panel.action_close.assert_called_once()
