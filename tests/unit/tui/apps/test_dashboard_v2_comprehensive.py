"""
Comprehensive tests for EnhancedDashboardApp.

Tests cover:
- App initialization
- Widget composition
- Event handling
- Storage adapter integration
- Sync operations
- View switching
- State management
- Error handling
"""

import tempfile
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, Mock, patch

import pytest

try:
    from textual.widgets import Footer, Header  # type: ignore[unresolved-import,possibly-missing-import]

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from tracertm.tui.apps.dashboard_v2 import TEXTUAL_AVAILABLE as APP_TEXTUAL
from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp  # type: ignore[possibly-missing-import]


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppInitialization:
    """Test app initialization."""

    def test_app_creation(self):
        """Test app can be created."""
        app = cast(Any, EnhancedDashboardApp())
        assert app is not None

    def test_app_with_base_dir(self):
        """Test app with custom base directory."""
        base_dir = Path(tempfile.gettempdir()) / "test"
        app = EnhancedDashboardApp(base_dir=base_dir)
        assert app is not None

    def test_app_attributes_initialized(self):
        """Test app attributes are initialized."""
        app = cast(Any, EnhancedDashboardApp())
        assert hasattr(app, "config_manager")
        assert hasattr(app, "storage_adapter")
        assert hasattr(app, "current_view")
        assert app.current_view == "epic"

    def test_storage_adapter_created(self):
        """Test storage adapter is created."""
        app = cast(Any, EnhancedDashboardApp())
        assert app.storage_adapter is not None

    def test_sync_state_initialized(self):
        """Test sync state tracking is initialized."""
        app = cast(Any, EnhancedDashboardApp())
        assert hasattr(app, "_is_syncing")
        assert app._is_syncing is False
        assert hasattr(app, "_sync_timer")
        assert app._sync_timer is None


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppComposition:
    """Test widget composition."""

    def test_compose_returns_widgets(self):
        """Test compose returns widgets."""
        app = cast(Any, EnhancedDashboardApp())
        widgets = list(app.compose())
        assert len(widgets) > 0

    def test_has_header(self):
        """Test app has header."""
        app = cast(Any, EnhancedDashboardApp())
        widgets = list(app.compose())
        has_header = any(isinstance(w, Header) for w in widgets)
        assert has_header

    def test_has_footer(self):
        """Test app has footer."""
        app = cast(Any, EnhancedDashboardApp())
        widgets = list(app.compose())
        has_footer = any(isinstance(w, Footer) for w in widgets)
        assert has_footer

    def test_compose_structure(self):
        """Test compose creates proper structure."""
        app = cast(Any, EnhancedDashboardApp())
        widgets = list(app.compose())
        # Should have Header, containers, Footer
        assert len(widgets) >= 3


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppBindings:
    """Test keyboard bindings."""

    def test_has_bindings(self):
        """Test app has keyboard bindings."""
        app = cast(Any, EnhancedDashboardApp())
        assert hasattr(app, "BINDINGS")
        assert len(cast(list, app.BINDINGS)) > 0

    def test_quit_binding(self):
        """Test quit binding exists."""
        app = cast(Any, EnhancedDashboardApp())
        bindings = [b.key for b in app.BINDINGS]
        assert "q" in bindings

    def test_refresh_binding(self):
        """Test refresh binding exists."""
        app = cast(Any, EnhancedDashboardApp())
        bindings = [b.key for b in app.BINDINGS]
        assert "r" in bindings

    def test_sync_binding(self):
        """Test sync binding exists."""
        app = cast(Any, EnhancedDashboardApp())
        bindings = [b.key for b in app.BINDINGS]
        assert "ctrl+s" in bindings

    def test_view_switch_binding(self):
        """Test view switch binding exists."""
        app = cast(Any, EnhancedDashboardApp())
        bindings = [b.key for b in app.BINDINGS]
        assert "v" in bindings

    def test_conflicts_binding(self):
        """Test conflicts binding exists."""
        app = cast(Any, EnhancedDashboardApp())
        bindings = [b.key for b in app.BINDINGS]
        assert "c" in bindings

    def test_help_binding(self):
        """Test help binding exists."""
        app = cast(Any, EnhancedDashboardApp())
        bindings = [b.key for b in app.BINDINGS]
        assert "?" in bindings


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppViews:
    """Test view management."""

    def test_default_view(self):
        """Test default view is set."""
        app = cast(Any, EnhancedDashboardApp())
        assert app.current_view == "epic"

    def test_view_types(self):
        """Test expected view types."""
        app = cast(Any, EnhancedDashboardApp())
        expected_views = ["epic", "story", "test", "task"]
        # App should support these views
        assert app.current_view in expected_views

    @patch.object(EnhancedDashboardApp, "query_one")
    @patch.object(EnhancedDashboardApp, "refresh_data")
    def test_switch_view_action(self, mock_refresh, mock_query):
        """Test switching views."""
        app = cast(Any, EnhancedDashboardApp())
        app.current_view = "epic"

        # Mock the Static widget
        mock_widget = Mock()
        mock_query.return_value = mock_widget

        app.action_switch_view()

        # View should change
        assert app.current_view in ["epic", "story", "test", "task"]
        mock_refresh.assert_called_once()

    def test_view_cycle(self):
        """Test view cycling."""
        app = cast(Any, EnhancedDashboardApp())
        views = ["epic", "story", "test", "task"]

        with patch.object(app, "refresh_data"), patch.object(app, "query_one"):
            for _ in range(len(views) + 1):
                app.action_switch_view()
                assert app.current_view in views


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppStorageIntegration:
    """Test storage adapter integration."""

    def test_storage_adapter_exists(self):
        """Test storage adapter is created."""
        app = cast(Any, EnhancedDashboardApp())
        assert app.storage_adapter is not None

    @patch("tracertm.tui.apps.dashboard_v2.StorageAdapter")
    def test_storage_adapter_initialization(self, mock_adapter):
        """Test storage adapter is initialized with base_dir."""
        base_dir = Path(tempfile.gettempdir()) / "test"
        EnhancedDashboardApp(base_dir=base_dir)
        mock_adapter.assert_called_once()

    def test_setup_storage_callbacks(self):
        """Test storage callbacks are setup."""
        app = cast(Any, EnhancedDashboardApp())
        # Mock storage adapter
        app.storage_adapter = Mock()
        app.storage_adapter.on_sync_status_change = Mock()
        app.storage_adapter.on_conflict_detected = Mock()
        app.storage_adapter.on_item_change = Mock()

        app.setup_storage_callbacks()

        app.storage_adapter.on_sync_status_change.assert_called_once()
        app.storage_adapter.on_conflict_detected.assert_called_once()
        app.storage_adapter.on_item_change.assert_called_once()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppSyncOperations:
    """Test sync operations."""

    @pytest.mark.asyncio
    async def test_sync_action_success(self):
        """Test successful sync action."""
        app = cast(Any, EnhancedDashboardApp())
        app.storage_adapter = Mock()
        app.storage_adapter.trigger_sync = AsyncMock(return_value={"success": True, "entities_synced": 10})
        app.notify = Mock()
        app.refresh_data = Mock()

        await app.action_sync()

        app.storage_adapter.trigger_sync.assert_called_once()
        app.refresh_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_action_failure(self):
        """Test failed sync action."""
        app = cast(Any, EnhancedDashboardApp())
        app.storage_adapter = Mock()
        app.storage_adapter.trigger_sync = AsyncMock(return_value={"success": False, "error": "Connection failed"})
        app.notify = Mock()

        await app.action_sync()

        app.storage_adapter.trigger_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_already_in_progress(self):
        """Test sync when already syncing."""
        app = cast(Any, EnhancedDashboardApp())
        app._is_syncing = True
        app.notify = Mock()
        app.storage_adapter = Mock()
        app.storage_adapter.trigger_sync = AsyncMock()

        await app.action_sync()

        # Should not call trigger_sync
        app.storage_adapter.trigger_sync.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_error_handling(self):
        """Test sync error handling."""
        app = cast(Any, EnhancedDashboardApp())
        app.storage_adapter = Mock()
        app.storage_adapter.trigger_sync = AsyncMock(side_effect=Exception("Test error"))
        app.notify = Mock()

        await app.action_sync()

        # Should handle exception gracefully
        assert app._is_syncing is False


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppActions:
    """Test action methods."""

    @patch.object(EnhancedDashboardApp, "refresh_data")
    @patch.object(EnhancedDashboardApp, "notify")
    def test_action_refresh(self, mock_notify, mock_refresh):
        """Test refresh action."""
        app = cast(Any, EnhancedDashboardApp())
        app.action_refresh()

        mock_refresh.assert_called_once()
        mock_notify.assert_called_once()

    @patch.object(EnhancedDashboardApp, "notify")
    def test_action_search(self, mock_notify):
        """Test search action."""
        app = cast(Any, EnhancedDashboardApp())
        app.action_search()

        # Search not yet implemented
        mock_notify.assert_called_once()

    @patch.object(EnhancedDashboardApp, "notify")
    def test_action_help(self, mock_notify):
        """Test help action."""
        app = cast(Any, EnhancedDashboardApp())
        app.action_help()

        mock_notify.assert_called_once()

    @patch.object(EnhancedDashboardApp, "push_screen")
    @patch.object(EnhancedDashboardApp, "notify")
    def test_action_show_conflicts_with_conflicts(self, mock_notify, mock_push):
        """Test show conflicts when conflicts exist."""
        app = cast(Any, EnhancedDashboardApp())
        app.storage_adapter = Mock()
        app.storage_adapter.get_unresolved_conflicts = Mock(return_value=[Mock(entity_id="123", entity_type="item")])

        app.action_show_conflicts()

        mock_push.assert_called_once()

    @patch.object(EnhancedDashboardApp, "notify")
    def test_action_show_conflicts_without_conflicts(self, mock_notify):
        """Test show conflicts when no conflicts."""
        app = cast(Any, EnhancedDashboardApp())
        app.storage_adapter = Mock()
        app.storage_adapter.get_unresolved_conflicts = Mock(return_value=[])

        app.action_show_conflicts()

        mock_notify.assert_called_once()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppDataRefresh:
    """Test data refresh functionality."""

    @patch.object(EnhancedDashboardApp, "refresh_stats")
    @patch.object(EnhancedDashboardApp, "refresh_items")
    def test_refresh_data_with_project(self, mock_items, mock_stats):
        """Test refresh data with existing project."""
        app = cast(Any, EnhancedDashboardApp())
        app.project_name = "test-project"
        app.storage_adapter = Mock()

        mock_project = Mock()
        app.storage_adapter.get_project = Mock(return_value=mock_project)

        app.refresh_data()

        app.storage_adapter.get_project.assert_called_once_with("test-project")
        mock_stats.assert_called_once_with(mock_project)
        mock_items.assert_called_once_with(mock_project)

    @patch.object(EnhancedDashboardApp, "refresh_stats")
    @patch.object(EnhancedDashboardApp, "refresh_items")
    def test_refresh_data_creates_project(self, mock_items, mock_stats):
        """Test refresh data creates project if missing."""
        app = cast(Any, EnhancedDashboardApp())
        app.project_name = "test-project"
        app.storage_adapter = Mock()

        mock_project = Mock()
        app.storage_adapter.get_project = Mock(return_value=None)
        app.storage_adapter.create_project = Mock(return_value=mock_project)

        app.refresh_data()

        app.storage_adapter.create_project.assert_called_once_with("test-project")

    def test_refresh_data_without_project(self):
        """Test refresh data without project name."""
        app = cast(Any, EnhancedDashboardApp())
        app.project_name = None

        # Should return early without error
        app.refresh_data()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppCallbacks:
    """Test callback handlers."""

    @patch.object(EnhancedDashboardApp, "call_later")
    @patch.object(EnhancedDashboardApp, "notify")
    def test_on_sync_status_change_success(self, mock_notify, mock_call_later):
        """Test sync status change callback for success."""
        from tracertm.storage.sync_engine import SyncStatus

        app = cast(Any, EnhancedDashboardApp())
        state = Mock()
        state.status = SyncStatus.SUCCESS
        state.synced_entities = 10

        app._on_sync_status_change(state)

        mock_call_later.assert_called_once()
        mock_notify.assert_called_once()

    @patch.object(EnhancedDashboardApp, "call_later")
    @patch.object(EnhancedDashboardApp, "notify")
    def test_on_sync_status_change_error(self, mock_notify, mock_call_later):
        """Test sync status change callback for error."""
        from tracertm.storage.sync_engine import SyncStatus

        app = cast(Any, EnhancedDashboardApp())
        state = Mock()
        state.status = SyncStatus.ERROR
        state.last_error = "Test error"

        app._on_sync_status_change(state)

        mock_call_later.assert_called_once()
        mock_notify.assert_called_once()

    @patch.object(EnhancedDashboardApp, "call_later")
    @patch.object(EnhancedDashboardApp, "notify")
    def test_on_conflict_detected(self, mock_notify, mock_call_later):
        """Test conflict detected callback."""
        app = cast(Any, EnhancedDashboardApp())
        conflict = Mock()
        conflict.entity_type = "item"
        conflict.entity_id = "123456789012"

        app._on_conflict_detected(conflict)

        mock_notify.assert_called_once()
        mock_call_later.assert_called_once()

    @patch.object(EnhancedDashboardApp, "call_later")
    def test_on_item_change(self, mock_call_later):
        """Test item change callback."""
        app = cast(Any, EnhancedDashboardApp())
        item_id = "test-item-id"

        app._on_item_change(item_id)

        mock_call_later.assert_called_once()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppTreeEvents:
    """Test tree event handling."""

    @patch.object(EnhancedDashboardApp, "refresh_items")
    @patch.object(EnhancedDashboardApp, "query_one")
    def test_on_tree_node_selected(self, mock_query, mock_refresh):
        """Test tree node selection."""
        app = cast(Any, EnhancedDashboardApp())
        app.project_name = "test-project"
        app.storage_adapter = Mock()
        app.storage_adapter.get_project = Mock(return_value=Mock())

        # Mock the Static widget
        mock_widget = Mock()
        mock_query.return_value = mock_widget

        # Mock event
        event = Mock()
        event.node = Mock()
        event.node.data = "story"

        app.on_tree_node_selected(event)

        assert app.current_view == "story"
        mock_refresh.assert_called_once()

    def test_on_tree_node_selected_without_data(self):
        """Test tree node selection without data."""
        app = cast(Any, EnhancedDashboardApp())

        # Mock event without data
        event = Mock()
        event.node = Mock()
        event.node.data = None

        # Should not crash
        app.on_tree_node_selected(event)


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppCSS:
    """Test CSS styling."""

    def test_has_css(self):
        """Test app has CSS defined."""
        app = cast(Any, EnhancedDashboardApp())
        assert hasattr(app, "CSS")
        assert isinstance(app.CSS, str)
        assert len(app.CSS) > 0

    def test_css_defines_sidebar(self):
        """Test CSS defines sidebar."""
        app = cast(Any, EnhancedDashboardApp())
        assert "#sidebar" in app.CSS

    def test_css_defines_main(self):
        """Test CSS defines main panel."""
        app = cast(Any, EnhancedDashboardApp())
        assert "#main" in app.CSS

    def test_css_defines_sync_status(self):
        """Test CSS defines sync status panel."""
        app = cast(Any, EnhancedDashboardApp())
        assert "#sync-status-panel" in app.CSS


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppEdgeCases:
    """Test edge cases and error handling."""

    @patch("tracertm.tui.apps.dashboard_v2.ConfigManager")
    def test_no_current_project(self, mock_config):
        """Test behavior when no current project."""
        mock_config_instance = Mock()
        mock_config_instance.get = Mock(return_value=None)
        mock_config.return_value = mock_config_instance

        app = cast(Any, EnhancedDashboardApp())
        app.exit = Mock()

        app.load_project()

        # Should exit when no project
        app.exit.assert_called_once()

    def test_unmount_cleanup(self):
        """Test cleanup on unmount."""
        app = cast(Any, EnhancedDashboardApp())
        app._sync_timer = Mock()
        app._sync_timer.stop = Mock()

        app.on_unmount()

        app._sync_timer.stop.assert_called_once()

    def test_unmount_without_timer(self):
        """Test unmount without sync timer."""
        app = cast(Any, EnhancedDashboardApp())
        app._sync_timer = None

        # Should not crash
        app.on_unmount()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestEnhancedDashboardAppSyncStatusUpdates:
    """Test sync status update functionality."""

    @patch.object(EnhancedDashboardApp, "query_one")
    def test_update_sync_status(self, mock_query):
        """Test sync status update."""
        from tracertm.storage.sync_engine import SyncStatus

        app = cast(Any, EnhancedDashboardApp())
        app.storage_adapter = Mock()

        state = Mock()
        state.status = SyncStatus.SUCCESS
        state.pending_changes = 5
        state.last_sync = "2024-01-01"
        state.conflicts_count = 0
        state.last_error = None

        app.storage_adapter.get_sync_status = Mock(return_value=state)

        mock_sync_widget = Mock()
        mock_query.return_value = mock_sync_widget

        app.update_sync_status()

        mock_sync_widget.set_online.assert_called_once()
        mock_sync_widget.set_syncing.assert_called_once()
        mock_sync_widget.set_pending_changes.assert_called_once_with(5)

    @patch.object(EnhancedDashboardApp, "set_interval")
    def test_start_sync_status_updates(self, mock_interval):
        """Test starting periodic sync status updates."""
        app = cast(Any, EnhancedDashboardApp())
        app.start_sync_status_updates()

        mock_interval.assert_called_once()


@pytest.mark.skipif(TEXTUAL_AVAILABLE, reason="Only test when Textual not installed")
class TestEnhancedDashboardAppPlaceholder:
    """Test placeholder when Textual is not available."""

    def test_placeholder_raises_import_error(self):
        """Test placeholder raises ImportError."""
        with pytest.raises(ImportError):
            EnhancedDashboardApp()


class TestEnhancedDashboardAppAvailability:
    """Test app availability detection."""

    def test_textual_availability_constant(self):
        """Test TEXTUAL_AVAILABLE constant is defined."""
        assert APP_TEXTUAL is not None
        assert isinstance(APP_TEXTUAL, bool)

    def test_textual_availability_matches(self):
        """Test module TEXTUAL_AVAILABLE matches test import."""
        assert APP_TEXTUAL == TEXTUAL_AVAILABLE
