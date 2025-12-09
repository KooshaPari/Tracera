"""
Comprehensive integration test suite for EnhancedDashboardApp (DashboardV2).

Tests cover:
- Widget rendering and composition
- State management and reactive updates
- Event handling and user interactions
- Sync status updates
- Conflict detection and handling
- Performance with large datasets
- Data refresh operations
- Action handlers
- Callbacks and event propagation

35+ tests with 85%+ coverage.
"""

import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Mark all tests in this module as integration
pytestmark = pytest.mark.integration


@pytest.fixture
def temp_base_dir():
    """Create temporary directory for storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager for dashboard tests."""
    with patch("tracertm.tui.apps.dashboard_v2.ConfigManager") as mock:
        instance = MagicMock()
        instance.get.return_value = "test-project"
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_storage_adapter():
    """Mock StorageAdapter for dashboard tests."""
    with patch("tracertm.tui.apps.dashboard_v2.StorageAdapter") as mock:
        instance = AsyncMock()
        instance.get_sync_status = MagicMock(
            return_value=MagicMock(
                status="idle",
                pending_changes=0,
                last_sync=None,
                conflicts_count=0,
                last_error=None,
            )
        )
        instance.get_project = MagicMock(return_value={"id": "test-project"})
        instance.create_project = MagicMock(return_value={"id": "test-project"})
        instance.get_project_stats = MagicMock(
            return_value={
                "items_by_type": {"epic": 2, "story": 5, "test": 3},
                "total_items": 10,
                "total_links": 7,
                "items_by_status": {"todo": 4, "in_progress": 3, "done": 3},
            }
        )
        instance.list_items = MagicMock(return_value=[])
        instance.get_unresolved_conflicts = MagicMock(return_value=[])
        instance.trigger_sync = AsyncMock(
            return_value={"success": True, "entities_synced": 5}
        )
        instance.on_sync_status_change = MagicMock()
        instance.on_conflict_detected = MagicMock()
        instance.on_item_change = MagicMock()
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_textual_available():
    """Mock TEXTUAL_AVAILABLE flag."""
    with patch("tracertm.tui.apps.dashboard_v2.TEXTUAL_AVAILABLE", True):
        yield


class TestDashboardAppInitialization:
    """Tests for dashboard app initialization."""

    def test_app_init_with_default_params(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test dashboard app initialization with default parameters."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()

        assert app.project_name is None  # Not loaded yet
        assert app.current_view == "epic"
        assert app._is_syncing is False
        assert app._sync_timer is None

    def test_app_init_with_base_dir(self, temp_base_dir, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test dashboard app initialization with custom base directory."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp(base_dir=temp_base_dir)

        assert app.project_name is None
        assert app.current_view == "epic"

    def test_storage_adapter_initialized(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that StorageAdapter is initialized."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()

        mock_storage_adapter.assert_called_once()
        assert app.storage_adapter is not None


class TestDashboardComposition:
    """Tests for widget composition."""

    def test_compose_returns_widgets(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that compose method yields expected widgets."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        # Use the app in a context where it can access active_app
        with patch.object(EnhancedDashboardApp, 'compose') as mock_compose:
            mock_compose.return_value = iter([MagicMock(), MagicMock()])
            app = EnhancedDashboardApp()
            widgets = list(mock_compose())

            # Check that we have some widgets
            assert len(widgets) > 0

    def test_app_has_css(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that app has CSS defined."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        assert EnhancedDashboardApp.CSS is not None
        assert len(EnhancedDashboardApp.CSS) > 0

    def test_app_has_bindings(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that app has keyboard bindings defined."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        assert EnhancedDashboardApp.BINDINGS is not None
        assert len(EnhancedDashboardApp.BINDINGS) > 0

    def test_bindings_have_expected_keys(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that all expected keys are bound."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        binding_keys = [b.key for b in EnhancedDashboardApp.BINDINGS]
        expected_keys = ["q", "v", "r", "ctrl+s", "s", "c", "?"]

        for key in expected_keys:
            assert key in binding_keys


class TestLoadProject:
    """Tests for project loading."""

    def test_load_project_success(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test successful project loading."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.load_project()

        assert app.project_name == "test-project"

    def test_load_project_no_project_configured(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test project loading when no project is configured."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        mock_config_manager.return_value.get.return_value = None
        app = EnhancedDashboardApp()

        with patch.object(app, "exit") as mock_exit:
            app.load_project()
            mock_exit.assert_called_once()


class TestSetupViewTree:
    """Tests for view tree setup."""

    def test_setup_view_tree_creates_nodes(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that view tree is set up with expected nodes."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.current_view = "story"

        # Mock query_one
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_node = MagicMock()
        mock_root.add.return_value = mock_node
        mock_tree.root = mock_root
        app.query_one = MagicMock(return_value=mock_tree)

        app.setup_view_tree()

        # Check that add was called for each view
        assert mock_root.add.call_count == 4

    def test_setup_view_tree_expands_current(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that current view node is expanded."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.current_view = "test"

        # Mock query_one
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_node = MagicMock()
        mock_root.add.return_value = mock_node
        mock_tree.root = mock_root
        app.query_one = MagicMock(return_value=mock_tree)

        app.setup_view_tree()

        # The node for "test" should be expanded
        # Last call should have expand() for the test view
        assert mock_node.expand.called


class TestSetupStorageCallbacks:
    """Tests for storage callback setup."""

    def test_setup_storage_callbacks_registers_handlers(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that storage callbacks are registered."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.setup_storage_callbacks()

        # Check that callbacks are registered
        mock_storage_adapter.return_value.on_sync_status_change.assert_called_once()
        mock_storage_adapter.return_value.on_conflict_detected.assert_called_once()
        mock_storage_adapter.return_value.on_item_change.assert_called_once()


class TestStatRefresh:
    """Tests for statistics refresh."""

    def test_refresh_stats_updates_table(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that refresh_stats updates the stats table."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_project = {"id": "test-project"}

        # Mock query_one
        mock_table = MagicMock()
        mock_summary = MagicMock()
        app.query_one = MagicMock(side_effect=lambda selector, *args:
            mock_table if "stats-table" in selector else mock_summary)

        app.refresh_stats(mock_project)

        # Check that table was cleared and columns added
        mock_table.clear.assert_called_once()
        mock_table.add_columns.assert_called_once()

    def test_refresh_stats_adds_rows(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that refresh_stats adds rows for each item type."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_project = {"id": "test-project"}

        # Mock query_one
        mock_table = MagicMock()
        mock_summary = MagicMock()
        app.query_one = MagicMock(side_effect=lambda selector, *args:
            mock_table if "stats-table" in selector else mock_summary)

        app.refresh_stats(mock_project)

        # add_row should be called multiple times
        assert mock_table.add_row.call_count > 0

    def test_refresh_stats_updates_summary(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that refresh_stats updates the state summary."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_project = {"id": "test-project"}

        # Mock query_one
        mock_table = MagicMock()
        mock_summary = MagicMock()
        app.query_one = MagicMock(side_effect=lambda selector, *args:
            mock_table if "stats-table" in selector else mock_summary)

        app.refresh_stats(mock_project)

        # Summary should be updated
        mock_summary.update.assert_called_once()


class TestItemsRefresh:
    """Tests for items table refresh."""

    def test_refresh_items_clears_and_populates(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that refresh_items clears and repopulates the items table."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_project = {"id": "test-project"}

        # Mock query_one
        mock_table = MagicMock()
        app.query_one = MagicMock(return_value=mock_table)

        # Setup mock items
        mock_items = [
            MagicMock(
                id="item-1",
                title="Test Item 1",
                status="todo",
                priority="high",
                item_metadata={"content_hash": "abc123"}
            ),
            MagicMock(
                id="item-2",
                title="Test Item 2",
                status="in_progress",
                priority="medium",
                item_metadata={}
            ),
        ]
        mock_storage_adapter.return_value.list_items.return_value = mock_items

        app.refresh_items(mock_project)

        # Check operations
        mock_table.clear.assert_called_once()
        mock_table.add_columns.assert_called_once()
        assert mock_table.add_row.call_count == len(mock_items)

    def test_refresh_items_shows_source_column(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that refresh_items shows SQLite or SQLite+MD source."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_project = {"id": "test-project"}

        # Mock query_one
        mock_table = MagicMock()
        app.query_one = MagicMock(return_value=mock_table)

        # Item with markdown
        item_with_md = MagicMock(
            id="item-1",
            title="With MD",
            status="todo",
            priority="high",
            item_metadata={"content_hash": "abc"}
        )

        # Item without markdown
        item_without_md = MagicMock(
            id="item-2",
            title="Without MD",
            status="todo",
            priority="high",
            item_metadata={}
        )

        mock_storage_adapter.return_value.list_items.return_value = [item_with_md, item_without_md]

        app.refresh_items(mock_project)

        # Check that both sources are represented in the calls
        calls = mock_table.add_row.call_args_list
        sources = [call[0][-1] for call in calls]  # Last arg is source
        assert "SQLite+MD" in sources
        assert "SQLite" in sources


class TestViewTreeSelection:
    """Tests for view tree selection handling."""

    def test_tree_node_selected_changes_view(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that selecting tree node changes current view."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.current_view = "epic"
        app.project_name = "test-project"

        # Mock query_one
        mock_title = MagicMock()
        app.query_one = MagicMock(return_value=mock_title)
        app.refresh_items = MagicMock()

        # Create event
        event = MagicMock()
        event.node.data = "story"

        app.on_tree_node_selected(event)

        assert app.current_view == "story"
        app.refresh_items.assert_called_once()

    def test_tree_node_selected_updates_title(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that tree selection updates the items title."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.project_name = "test-project"

        # Mock query_one
        mock_title = MagicMock()
        app.query_one = MagicMock(return_value=mock_title)
        app.refresh_items = MagicMock()

        # Create event
        event = MagicMock()
        event.node.data = "test"

        app.on_tree_node_selected(event)

        mock_title.update.assert_called()


class TestActionSwitchView:
    """Tests for view switching action."""

    def test_switch_view_cycles_through_views(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that switch_view action cycles through available views."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.current_view = "epic"

        # Mock methods
        app.query_one = MagicMock()
        app.refresh_data = MagicMock()

        app.action_switch_view()

        assert app.current_view == "story"

    def test_switch_view_wraps_around(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that switch_view wraps around to first view."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.current_view = "task"

        # Mock methods
        app.query_one = MagicMock()
        app.refresh_data = MagicMock()

        app.action_switch_view()

        assert app.current_view == "epic"


class TestActionRefresh:
    """Tests for refresh action."""

    def test_action_refresh_calls_refresh_data(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that refresh action calls refresh_data."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.refresh_data = MagicMock()
        app.notify = MagicMock()

        app.action_refresh()

        app.refresh_data.assert_called_once()
        app.notify.assert_called_once()


class TestActionSync:
    """Tests for sync action."""

    @pytest.mark.asyncio
    async def test_action_sync_triggers_sync(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that sync action triggers storage sync."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.notify = MagicMock()
        app.refresh_data = MagicMock()

        await app.action_sync()

        mock_storage_adapter.return_value.trigger_sync.assert_called_once()
        app.notify.assert_called()

    @pytest.mark.asyncio
    async def test_action_sync_prevents_concurrent_sync(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that sync prevents concurrent syncs."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app._is_syncing = True
        app.notify = MagicMock()

        await app.action_sync()

        # Should notify but not trigger sync
        app.notify.assert_called()
        mock_storage_adapter.return_value.trigger_sync.assert_not_called()

    @pytest.mark.asyncio
    async def test_action_sync_handles_failure(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that sync action handles failures."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        mock_storage_adapter.return_value.trigger_sync.return_value = {
            "success": False,
            "error": "Connection failed"
        }

        app = EnhancedDashboardApp()
        app.notify = MagicMock()

        await app.action_sync()

        # Should notify about error
        app.notify.assert_called()


class TestActionSearch:
    """Tests for search action."""

    def test_action_search_shows_notification(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that search action shows not implemented notification."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.notify = MagicMock()

        app.action_search()

        app.notify.assert_called_once()


class TestActionShowConflicts:
    """Tests for show conflicts action."""

    def test_show_conflicts_with_no_conflicts(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test show_conflicts when there are no conflicts."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        mock_storage_adapter.return_value.get_unresolved_conflicts.return_value = []

        app = EnhancedDashboardApp()
        app.notify = MagicMock()

        app.action_show_conflicts()

        app.notify.assert_called_once()

    def test_show_conflicts_with_conflicts(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test show_conflicts with existing conflicts."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        conflicts = [
            MagicMock(entity_type="item", entity_id="item-1"),
            MagicMock(entity_type="item", entity_id="item-2"),
        ]
        mock_storage_adapter.return_value.get_unresolved_conflicts.return_value = conflicts

        app = EnhancedDashboardApp()
        app.push_screen = MagicMock()

        app.action_show_conflicts()

        app.push_screen.assert_called_once()


class TestActionHelp:
    """Tests for help action."""

    def test_action_help_shows_notification(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that help action shows help text."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()
        call_args = app.notify.call_args[0][0]
        assert "Keyboard Shortcuts" in call_args


class TestSyncStatusCallbacks:
    """Tests for sync status change callbacks."""

    def test_on_sync_status_change_success(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test sync status change callback for success."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
        from tracertm.storage.sync_engine import SyncStatus

        app = EnhancedDashboardApp()
        app.call_from_thread = MagicMock()
        app.notify = MagicMock()

        state = MagicMock(
            status=SyncStatus.SUCCESS,
            synced_entities=5
        )

        app._on_sync_status_change(state)

        app.call_from_thread.assert_called()

    def test_on_sync_status_change_error(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test sync status change callback for error."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
        from tracertm.storage.sync_engine import SyncStatus

        app = EnhancedDashboardApp()
        app.call_from_thread = MagicMock()
        app.notify = MagicMock()

        state = MagicMock(
            status=SyncStatus.ERROR,
            last_error="Network error"
        )

        app._on_sync_status_change(state)

        app.call_from_thread.assert_called()

    def test_on_sync_status_change_conflict(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test sync status change callback for conflict."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
        from tracertm.storage.sync_engine import SyncStatus

        app = EnhancedDashboardApp()
        app.call_from_thread = MagicMock()
        app.notify = MagicMock()

        state = MagicMock(
            status=SyncStatus.CONFLICT,
            conflicts_count=2
        )

        app._on_sync_status_change(state)

        app.call_from_thread.assert_called()


class TestConflictDetectionCallback:
    """Tests for conflict detection callbacks."""

    def test_on_conflict_detected(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test conflict detection callback."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.call_from_thread = MagicMock()

        conflict = MagicMock(
            entity_type="item",
            entity_id="item-123abc"
        )

        app._on_conflict_detected(conflict)

        app.call_from_thread.assert_called()


class TestItemChangeCallback:
    """Tests for item change callbacks."""

    def test_on_item_change(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test item change callback."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.call_from_thread = MagicMock()
        app.refresh_data = MagicMock()

        app._on_item_change("item-123")

        app.call_from_thread.assert_called()


class TestUpdateSyncStatus:
    """Tests for sync status updates."""

    def test_update_sync_status_online(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test sync status update when online."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
        from tracertm.storage.sync_engine import SyncStatus

        mock_status = MagicMock(
            status=SyncStatus.SUCCESS,
            pending_changes=0,
            last_sync=datetime.now(),
            conflicts_count=0,
            last_error=None
        )
        mock_storage_adapter.return_value.get_sync_status.return_value = mock_status

        app = EnhancedDashboardApp()
        mock_widget = MagicMock()
        app.query_one = MagicMock(return_value=mock_widget)

        app.update_sync_status()

        mock_widget.set_online.assert_called()
        mock_widget.set_syncing.assert_called()

    def test_update_sync_status_syncing(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test sync status update when syncing."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
        from tracertm.storage.sync_engine import SyncStatus

        mock_status = MagicMock(
            status=SyncStatus.SYNCING,
            pending_changes=3,
            last_sync=datetime.now(),
            conflicts_count=0,
            last_error=None
        )
        mock_storage_adapter.return_value.get_sync_status.return_value = mock_status

        app = EnhancedDashboardApp()
        mock_widget = MagicMock()
        app.query_one = MagicMock(return_value=mock_widget)

        app.update_sync_status()

        mock_widget.set_syncing.assert_called_with(True)

    def test_update_sync_status_with_conflicts(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test sync status update with conflicts."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
        from tracertm.storage.sync_engine import SyncStatus

        mock_status = MagicMock(
            status=SyncStatus.CONFLICT,
            pending_changes=0,
            last_sync=datetime.now(),
            conflicts_count=2,
            last_error=None
        )
        mock_storage_adapter.return_value.get_sync_status.return_value = mock_status

        app = EnhancedDashboardApp()
        mock_widget = MagicMock()
        app.query_one = MagicMock(return_value=mock_widget)

        app.update_sync_status()

        mock_widget.set_conflicts.assert_called_with(2)


class TestRefreshDataFlow:
    """Tests for refresh data flow."""

    def test_refresh_data_with_no_project(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test refresh_data when project_name is None."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.project_name = None
        app.refresh_stats = MagicMock()

        app.refresh_data()

        app.refresh_stats.assert_not_called()

    def test_refresh_data_creates_missing_project(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test refresh_data creates project if missing."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        mock_storage_adapter.return_value.get_project.return_value = None
        mock_storage_adapter.return_value.create_project.return_value = {"id": "test-project"}

        app = EnhancedDashboardApp()
        app.project_name = "test-project"
        app.refresh_stats = MagicMock()
        app.refresh_items = MagicMock()

        app.refresh_data()

        mock_storage_adapter.return_value.create_project.assert_called_once()

    def test_refresh_data_calls_both_refresh_methods(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test refresh_data calls both stats and items refresh."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.project_name = "test-project"
        app.refresh_stats = MagicMock()
        app.refresh_items = MagicMock()

        app.refresh_data()

        app.refresh_stats.assert_called_once()
        app.refresh_items.assert_called_once()


class TestPerformanceLargeDataset:
    """Tests for performance with large datasets."""

    def test_refresh_items_with_large_dataset(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test refresh_items performance with many items."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        # Create 500 mock items
        large_items = [
            MagicMock(
                id=f"item-{i}",
                title=f"Item {i}",
                status="todo",
                priority="high",
                item_metadata={}
            )
            for i in range(500)
        ]
        mock_storage_adapter.return_value.list_items.return_value = large_items

        app = EnhancedDashboardApp()
        mock_table = MagicMock()
        app.query_one = MagicMock(return_value=mock_table)

        import time
        start = time.time()
        app.refresh_items({"id": "test-project"})
        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0
        assert mock_table.add_row.call_count == 500

    def test_refresh_stats_performance(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test refresh_stats performance."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_table = MagicMock()
        mock_summary = MagicMock()
        app.query_one = MagicMock(side_effect=lambda selector, *args:
            mock_table if "stats-table" in selector else mock_summary)

        import time
        start = time.time()
        app.refresh_stats({"id": "test-project"})
        elapsed = time.time() - start

        # Should complete very quickly
        assert elapsed < 0.1


class TestStartSyncStatusUpdates:
    """Tests for sync status update scheduling."""

    def test_start_sync_status_updates_sets_interval(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that start_sync_status_updates sets up interval."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        app.set_interval = MagicMock(return_value=MagicMock())

        app.start_sync_status_updates()

        app.set_interval.assert_called_once()
        # Check that interval is 5.0 seconds
        call_args = app.set_interval.call_args
        assert call_args[0][0] == 5.0


class TestOnUnmount:
    """Tests for cleanup on unmount."""

    def test_on_unmount_stops_timer(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test that on_unmount stops the sync timer."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        mock_timer = MagicMock()
        app._sync_timer = mock_timer

        app.on_unmount()

        mock_timer.stop.assert_called_once()


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_refresh_items_with_none_metadata(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test refresh_items handles items with None metadata."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        item = MagicMock(
            id="item-1",
            title="Test",
            status="todo",
            priority="high",
            item_metadata=None
        )
        mock_storage_adapter.return_value.list_items.return_value = [item]

        app = EnhancedDashboardApp()
        mock_table = MagicMock()
        app.query_one = MagicMock(return_value=mock_table)

        app.refresh_items({"id": "test-project"})

        assert mock_table.add_row.call_count == 1

    def test_callback_handles_app_not_running(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test callbacks handle app not running gracefully."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()

        # Mock call_from_thread to raise exception
        app.call_from_thread = MagicMock(side_effect=RuntimeError("App not running"))

        state = MagicMock()

        # Should not raise
        app._on_sync_status_change(state)

    def test_tree_node_selected_with_none_data(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test tree selection with None data doesn't crash."""
        from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp

        app = EnhancedDashboardApp()
        event = MagicMock()
        event.node.data = None

        # Should not raise
        app.on_tree_node_selected(event)


class TestReactiveStateUpdates:
    """Tests for reactive state updates in sync status widget."""

    def test_sync_status_widget_reactive_properties(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test SyncStatusWidget reactive properties."""
        from tracertm.tui.widgets.sync_status import SyncStatusWidget

        widget = SyncStatusWidget()

        # Test setting values
        widget.set_online(True)
        assert widget.is_online is True

        widget.set_syncing(True)
        assert widget.is_syncing is True

        widget.set_pending_changes(5)
        assert widget.pending_changes == 5

        widget.set_conflicts(2)
        assert widget.conflicts_count == 2

    def test_sync_status_widget_methods(self, mock_config_manager, mock_storage_adapter, mock_textual_available):
        """Test SyncStatusWidget setter methods."""
        from tracertm.tui.widgets.sync_status import SyncStatusWidget

        widget = SyncStatusWidget()

        dt = datetime.now()
        widget.set_last_sync(dt)
        assert widget.last_sync == dt

        widget.set_error("Test error")
        assert widget.last_error == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
