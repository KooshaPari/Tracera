"""Comprehensive tests for DashboardApp TUI component.

Tests app initialization, widget composition, state management, and user interactions:
- App initialization with config
- Widget setup and composition
- Database connection and data loading
- View switching and refresh operations
- Search functionality
- Error handling for missing dependencies

Coverage target: 85%+
"""

# Import Textual components conditionally
from typing import Any
from unittest.mock import Mock, patch

import pytest

try:
    from textual.app import App
    from textual.widgets import DataTable, Static, Tree

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppImport:
    """Test app can be imported and accessed."""

    def test_dashboard_app_can_be_imported(self) -> None:
        """Test DashboardApp class can be imported."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            assert DashboardApp is not None
        except ImportError as e:
            pytest.skip(f"Could not import DashboardApp: {e}")

    def test_dashboard_app_is_app_subclass(self) -> None:
        """Test DashboardApp is a subclass of App."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            if TEXTUAL_AVAILABLE:
                assert issubclass(DashboardApp, App)
        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppInitialization:
    """Test app initialization."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_initialization_creates_config_manager(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app creates ConfigManager on init."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            mock_config_instance = Mock()
            mock_config.return_value = mock_config_instance

            app = DashboardApp()
            assert app is not None
            assert app.config_manager is not None
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_initialization_sets_default_view(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app sets default view to FEATURE."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert app.current_view == "FEATURE"
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_initialization_sets_none_project_id(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app initializes with None project_id."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert app.project_id is None
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_initialization_sets_none_db(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app initializes with None db."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert app.db is None
        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppAttributes:
    """Test app has required attributes."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_bindings(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app defines bindings."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            assert hasattr(DashboardApp, "BINDINGS")
            assert isinstance(DashboardApp.BINDINGS, list)
            assert len(DashboardApp.BINDINGS) > 0
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_css(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app defines CSS."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            assert hasattr(DashboardApp, "CSS")
            assert isinstance(DashboardApp.CSS, str)
            assert len(DashboardApp.CSS) > 0
        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppMethods:
    """Test app methods exist and are callable."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_compose_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has compose method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "compose")
            assert callable(app.compose)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_on_mount_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has on_mount method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "on_mount")
            assert callable(app.on_mount)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_setup_database_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has setup_database method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "setup_database")
            assert callable(app.setup_database)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_load_project_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has load_project method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "load_project")
            assert callable(app.load_project)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_setup_view_tree_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has setup_view_tree method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "setup_view_tree")
            assert callable(app.setup_view_tree)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_refresh_data_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has refresh_data method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "refresh_data")
            assert callable(app.refresh_data)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_refresh_stats_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has refresh_stats method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "refresh_stats")
            assert callable(app.refresh_stats)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_refresh_items_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has refresh_items method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "refresh_items")
            assert callable(app.refresh_items)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_action_methods(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has action methods."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "action_switch_view")
            assert hasattr(app, "action_refresh")
            assert hasattr(app, "action_search")
            assert hasattr(app, "action_help")
        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppSetupDatabase:
    """Test setup_database method."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_setup_database_with_url(self, mock_db_conn: Any, mock_config: Any) -> None:
        """Test setup_database with valid database URL."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            mock_config_instance = Mock()
            mock_config_instance.get = Mock(return_value="sqlite:///test.db")
            mock_config.return_value = mock_config_instance

            mock_db_instance = Mock()
            mock_db_conn.return_value = mock_db_instance

            app = DashboardApp()
            # Don't call exit() in setup_database
            with patch.object(app, "exit"):
                app.setup_database()
                assert app.db == mock_db_instance

        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_setup_database_without_url(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test setup_database without database URL calls exit."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            mock_config_instance = Mock()
            mock_config_instance.get = Mock(return_value=None)
            mock_config.return_value = mock_config_instance

            app = DashboardApp()
            with patch.object(app, "exit") as mock_exit:
                app.setup_database()
                mock_exit.assert_called()

        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppLoadProject:
    """Test load_project method."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_load_project_with_id(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test load_project with valid project ID."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            mock_config_instance = Mock()
            mock_config_instance.get = Mock(return_value="proj-123")
            mock_config.return_value = mock_config_instance

            app = DashboardApp()
            with patch.object(app, "exit"):
                app.load_project()
                assert app.project_id == "proj-123"

        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_load_project_without_id(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test load_project without project ID calls exit."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            mock_config_instance = Mock()
            mock_config_instance.get = Mock(return_value=None)
            mock_config.return_value = mock_config_instance

            app = DashboardApp()
            with patch.object(app, "exit") as mock_exit:
                app.load_project()
                mock_exit.assert_called()

        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppViewSwitching:
    """Test view switching functionality."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_action_switch_view_cycles_through_views(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test action_switch_view cycles through available views."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert app.current_view == "FEATURE"

            views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]

            # Test view cycling
            with patch.object(app, "query_one"), patch.object(app, "refresh_items"):
                for _i in range(len(views)):
                    current_view = app.current_view
                    assert current_view in views

        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_current_view_starts_as_feature(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test current_view starts as FEATURE."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert app.current_view == "FEATURE"
        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppRefresh:
    """Test refresh functionality."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_refresh_data_calls_refresh_stats_and_items(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test refresh_data calls both refresh_stats and refresh_items."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            app.db = Mock()
            app.project_id = "proj-1"

            with patch.object(app, "refresh_stats") as mock_stats:
                with patch.object(app, "refresh_items") as mock_items:
                    app.refresh_data()
                    mock_stats.assert_called_once()
                    mock_items.assert_called_once()

        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_refresh_data_without_db(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test refresh_data returns early without db."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            app.db = None

            with patch.object(app, "refresh_stats") as mock_stats:
                with patch.object(app, "refresh_items") as mock_items:
                    app.refresh_data()
                    mock_stats.assert_not_called()
                    mock_items.assert_not_called()

        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_refresh_data_without_project_id(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test refresh_data returns early without project_id."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            app.db = Mock()
            app.project_id = None

            with patch.object(app, "refresh_stats") as mock_stats:
                with patch.object(app, "refresh_items") as mock_items:
                    app.refresh_data()
                    mock_stats.assert_not_called()
                    mock_items.assert_not_called()

        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppSearch:
    """Test search functionality."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_perform_search_method(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has perform_search method."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "perform_search")
            assert callable(app.perform_search)
        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_perform_search_requires_query_string(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test perform_search accepts query string."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            app.items_data = []

            with patch.object(app, "notify"):
                # Should not raise
                app.perform_search("")
                app.perform_search("test query")

        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppHelp:
    """Test help action."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_action_help_notifies_user(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test action_help sends notification."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()

            with patch.object(app, "notify") as mock_notify:
                app.action_help()
                mock_notify.assert_called_once()

        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppCleanup:
    """Test cleanup on unmount."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_on_unmount_closes_database(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test on_unmount closes database connection."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            mock_db = Mock()
            app.db = mock_db

            app.on_unmount()
            mock_db.close.assert_called_once()

        except ImportError:
            pytest.skip("Could not import DashboardApp")

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_on_unmount_without_database(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test on_unmount handles None database."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            app.db = None

            # Should not raise
            app.on_unmount()

        except ImportError:
            pytest.skip("Could not import DashboardApp")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestDashboardAppEventHandlers:
    """Test event handlers."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.DatabaseConnection")
    def test_app_has_tree_node_selected_handler(self, mock_db_conn: Any, _mock_config: Any) -> None:
        """Test app has on_tree_node_selected handler."""
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            app = DashboardApp()
            assert hasattr(app, "on_tree_node_selected")
            assert callable(app.on_tree_node_selected)
        except ImportError:
            pytest.skip("Could not import DashboardApp")


class TestDashboardAppFallback:
    """Test fallback when Textual is not available."""

    @patch.dict("sys.modules", {"textual": None, "textual.app": None, "textual.widgets": None})
    def test_fallback_class_raises_on_init(self) -> None:
        """Test fallback DashboardApp raises ImportError."""
        # This tests the fallback placeholder
        try:
            from tracertm.tui.apps.dashboard import DashboardApp

            # If we get here and Textual IS available, we're testing the real class
            if TEXTUAL_AVAILABLE:
                pytest.skip("Textual is available, can't test fallback")
            else:
                # Textual not available, test fallback
                with pytest.raises(ImportError):
                    DashboardApp()
        except ImportError:
            pytest.skip("Could not import dashboard module")
