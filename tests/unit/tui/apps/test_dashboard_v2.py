"""
Comprehensive tests for tracertm.tui.apps.dashboard_v2 module.

Tests EnhancedDashboardApp TUI application including initialization,
widget composition, event handling, sync operations, and callbacks.
Coverage target: 80%+ of 190 statements
"""

from datetime import datetime
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from tracertm.models import Item, Project
from tracertm.storage.sync_engine import SyncState, SyncStatus

# Skip all tests if Textual not available
pytest.importorskip("textual")


def _make_dashboard_app(*args: Any, **kwargs: Any) -> Any:
    """Return EnhancedDashboardApp as Any so tests can assign mocks to attributes."""
    from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]
    return cast(Any, EnhancedDashboardApp(*args, **kwargs))


@pytest.fixture
def mock_storage_adapter():
    """Create mock StorageAdapter."""
    adapter = MagicMock()
    adapter.on_sync_status_change = Mock(return_value=lambda: None)
    adapter.on_conflict_detected = Mock(return_value=lambda: None)
    adapter.on_item_change = Mock(return_value=lambda: None)
    adapter.get_sync_status = Mock(return_value=SyncState(status=SyncStatus.IDLE, pending_changes=0, last_sync=None))
    adapter.get_project = Mock(return_value=None)
    adapter.create_project = Mock(return_value=Project(name="Test", description="Test"))
    adapter.get_project_stats = Mock(
        return_value={
            "total_items": 10,
            "items_by_type": {"epic": 2, "story": 5, "test": 2, "task": 1},
            "items_by_status": {"todo": 3, "in_progress": 4, "done": 3},
            "total_links": 15,
        }
    )
    adapter.list_items = Mock(return_value=[])
    adapter.get_unresolved_conflicts = Mock(return_value=[])
    adapter.trigger_sync = AsyncMock(return_value={"success": True, "entities_synced": 5})
    return adapter


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager."""
    config = MagicMock()
    config.get.return_value = "Test Project"
    return config


class TestDashboardAppInitialization:
    """Test EnhancedDashboardApp initialization."""

    def test_app_initialization(self):
        """Test app initializes with correct attributes."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager") as mock_config:
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter") as mock_adapter:
                app = _make_dashboard_app()

                assert app.project_name is None
                assert app.current_view == "epic"
                assert app._is_syncing is False
                assert app._sync_timer is None

    def test_app_initialization_with_base_dir(self):
        """Test app initializes with custom base directory."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        base_dir = Path("/custom/path")

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter") as mock_adapter:
                app = _make_dashboard_app(base_dir=base_dir)

                mock_adapter.assert_called_once_with(base_dir=base_dir)


class TestDashboardAppComposition:
    """Test widget composition and layout."""

    @pytest.mark.asyncio
    async def test_compose_creates_widgets(self):
        """Test compose method creates all required widgets."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()

                # Run app in test mode to properly initialize compose stack
                async with app.run_test() as pilot:
                    # App is now running with all widgets composed
                    # Query to verify widgets exist
                    assert app.query("Header")  # Has header
                    assert app.query("Footer")  # Has footer
                    # Verify compose was called successfully
                    assert len(app.children) > 0

    def test_bindings_configured(self):
        """Test keyboard bindings are properly configured."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        bindings = EnhancedDashboardApp.BINDINGS

        # Check critical bindings exist
        binding_keys = [b.key for b in bindings]
        assert "q" in binding_keys  # Quit
        assert "v" in binding_keys  # Switch view
        assert "r" in binding_keys  # Refresh
        assert "ctrl+s" in binding_keys  # Sync
        assert "c" in binding_keys  # Conflicts


class TestProjectLoading:
    """Test project loading functionality."""

    def test_load_project_success(self, mock_config_manager):
        """Test loading project from config."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager") as mock_config_cls:
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                mock_config_cls.return_value = mock_config_manager
                app = _make_dashboard_app()

                app.load_project()

                assert app.project_name == "Test Project"

    def test_load_project_no_project_configured(self):
        """Test loading when no project is configured exits app."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager") as mock_config_cls:
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                config = MagicMock()
                config.get.return_value = None
                mock_config_cls.return_value = config

                app = _make_dashboard_app()
                app.exit = Mock()

                app.load_project()

                app.exit.assert_called_once()


class TestViewManagement:
    """Test view switching and management."""

    def test_setup_view_tree(self, mock_storage_adapter):
        """Test view tree setup with all views."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter

                # Mock Tree widget
                mock_tree = MagicMock()
                mock_tree.root.add.return_value = MagicMock(expand=Mock())
                app.query_one = Mock(return_value=mock_tree)

                app.setup_view_tree()

                # Should add 4 views: epic, story, test, task
                assert mock_tree.root.add.call_count == 4

    def test_action_switch_view(self, mock_storage_adapter):
        """Test switching between views."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app.project_name = "Test Project"
                app.current_view = "epic"
                app.refresh_data = Mock()
                app.query_one = Mock(return_value=MagicMock())

                app.action_switch_view()

                assert app.current_view == "story"  # Should cycle to next

                app.action_switch_view()
                assert app.current_view == "test"

                app.action_switch_view()
                assert app.current_view == "task"

                app.action_switch_view()
                assert app.current_view == "epic"  # Cycle back


class TestDataRefresh:
    """Test data refresh operations."""

    def test_refresh_data_no_project(self, mock_storage_adapter):
        """Test refresh_data skips when no project is set."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app.project_name = None
                app.refresh_stats = Mock()
                app.refresh_items = Mock()

                app.refresh_data()

                # Should not call refresh methods
                app.refresh_stats.assert_not_called()
                app.refresh_items.assert_not_called()

    def test_refresh_data_creates_project_if_not_exists(self, mock_storage_adapter):
        """Test refresh_data creates project if it doesn't exist."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app.project_name = "New Project"
                app.refresh_stats = Mock()
                app.refresh_items = Mock()

                app.refresh_data()

                mock_storage_adapter.create_project.assert_called_once_with("New Project")

    def test_refresh_stats(self, mock_storage_adapter):
        """Test refreshing statistics display."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter

                project = Project(name="Test", description="Test")
                mock_table = MagicMock()
                mock_static = MagicMock()
                app.query_one = Mock(side_effect=[mock_table, mock_static])

                app.refresh_stats(project)

                mock_table.clear.assert_called_once()
                mock_table.add_columns.assert_called_once()
                assert mock_table.add_row.call_count >= 4  # Items by type + separator + total

    def test_refresh_items(self, mock_storage_adapter):
        """Test refreshing items table."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app.current_view = "epic"

                project = Project(name="Test", description="Test")
                mock_items = [
                    Item(
                        id="item-1",
                        title="Item 1",
                        status="todo",
                        priority="high",
                        item_metadata={"content_hash": "abc"},
                    ),
                    Item(id="item-2", title="Item 2", status="done", priority="low", item_metadata={}),
                ]
                mock_storage_adapter.list_items.return_value = mock_items

                mock_table = MagicMock()
                app.query_one = Mock(return_value=mock_table)

                app.refresh_items(project)

                mock_table.clear.assert_called_once()
                mock_table.add_columns.assert_called_once()
                assert mock_table.add_row.call_count == 2


class TestSyncOperations:
    """Test sync functionality."""

    def test_update_sync_status(self, mock_storage_adapter):
        """Test updating sync status widget."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter

                sync_state = SyncState(
                    status=SyncStatus.SYNCING, pending_changes=5, last_sync=datetime.now(), conflicts_count=2
                )
                mock_storage_adapter.get_sync_status.return_value = sync_state

                mock_widget = MagicMock()
                app.query_one = Mock(return_value=mock_widget)

                app.update_sync_status()

                mock_widget.set_online.assert_called()
                mock_widget.set_syncing.assert_called_with(True)
                mock_widget.set_pending_changes.assert_called_with(5)

    @pytest.mark.asyncio
    async def test_action_sync_success(self, mock_storage_adapter):
        """Test successful sync action."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app.notify = Mock()
                app.refresh_data = Mock()

                await app.action_sync()

                app.notify.assert_called()
                app.refresh_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_action_sync_already_in_progress(self, mock_storage_adapter):
        """Test sync action when already syncing."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app._is_syncing = True
                app.notify = Mock()

                await app.action_sync()

                # Should notify warning
                assert app.notify.call_count == 1

    @pytest.mark.asyncio
    async def test_action_sync_failure(self, mock_storage_adapter):
        """Test sync action handling failure."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                mock_storage_adapter.trigger_sync = AsyncMock(return_value={"success": False, "error": "Network error"})
                app.notify = Mock()

                await app.action_sync()

                # Should notify error
                app.notify.assert_called()


class TestUserActions:
    """Test user action handlers."""

    def test_action_refresh(self, mock_storage_adapter):
        """Test refresh action."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                app.refresh_data = Mock()
                app.notify = Mock()

                app.action_refresh()

                app.refresh_data.assert_called_once()
                app.notify.assert_called_once()

    def test_action_search(self, mock_storage_adapter):
        """Test search action (not yet implemented)."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.notify = Mock()

                app.action_search()

                app.notify.assert_called_once()

    def test_action_show_conflicts_no_conflicts(self, mock_storage_adapter):
        """Test show conflicts action when no conflicts exist."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                mock_storage_adapter.get_unresolved_conflicts.return_value = []
                app.notify = Mock()
                app.push_screen = Mock()

                app.action_show_conflicts()

                app.notify.assert_called_once()
                app.push_screen.assert_not_called()

    def test_action_show_conflicts_with_conflicts(self, mock_storage_adapter):
        """Test show conflicts action when conflicts exist."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.storage_adapter = mock_storage_adapter
                mock_conflicts = [MagicMock(), MagicMock()]
                mock_storage_adapter.get_unresolved_conflicts.return_value = mock_conflicts
                app.push_screen = Mock()

                app.action_show_conflicts()

                app.push_screen.assert_called_once()

    def test_action_help(self, mock_storage_adapter):
        """Test help action."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.notify = Mock()

                app.action_help()

                app.notify.assert_called_once()


class TestCallbackHandlers:
    """Test callback handlers for storage events."""

    def test_on_sync_status_change_callback(self, mock_storage_adapter):
        """Test sync status change callback."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.call_later = Mock()
                app.notify = Mock()

                state = SyncState(status=SyncStatus.SUCCESS, synced_entities=10, pending_changes=0)
                app._on_sync_status_change(state)

                app.call_later.assert_called()
                app.notify.assert_called()

    def test_on_conflict_detected_callback(self, mock_storage_adapter):
        """Test conflict detection callback."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.call_later = Mock()
                app.notify = Mock()

                conflict = MagicMock(entity_type="item", entity_id="item-123456789")
                app._on_conflict_detected(conflict)

                app.notify.assert_called()
                app.call_later.assert_called()

    def test_on_item_change_callback(self, mock_storage_adapter):
        """Test item change callback."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]

        with patch("tracertm.tui.apps.dashboard_v2.ConfigManager"):
            with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter"):
                app = _make_dashboard_app()
                app.call_later = Mock()

                app._on_item_change("item-123")

                app.call_later.assert_called()
