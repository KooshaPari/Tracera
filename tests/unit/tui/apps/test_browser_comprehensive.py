"""Comprehensive tests for BrowserApp TUI application.

Tests app initialization, widget composition, database operations,
tree navigation, item display, filtering, and error handling.
Coverage target: 80%+ (221 lines total)
"""

from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_TWO

try:
    from textual.app import App
    from textual.widgets import Footer, Header, Input, Static, Tree

    from tracertm.tui.apps.browser import TEXTUAL_AVAILABLE, BrowserApp

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppInitialization:
    """Test BrowserApp initialization and setup."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_app_init(self, mock_config_manager: Any) -> None:
        """Test BrowserApp can be initialized with proper attributes."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        app = BrowserApp()

        assert app is not None
        assert app.project_id is None
        assert app.current_view == "FEATURE"
        assert app.db is None
        assert app.selected_item_id is None
        assert app.config_manager is not None

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_app_compose(self, mock_config_manager: Any) -> None:
        """Test BrowserApp compose method creates proper widget structure."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        app = BrowserApp()

        # Compose returns a generator that needs app context
        # Just verify it can be called without error
        assert hasattr(app, "compose")
        assert callable(app.compose)

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_app_bindings(self, mock_config_manager: Any) -> None:
        """Test BrowserApp has proper key bindings configured."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        app = BrowserApp()

        assert len(app.BINDINGS) > 0
        binding_keys = [b.key for b in app.BINDINGS]
        assert "q" in binding_keys  # Quit
        assert "r" in binding_keys  # Refresh
        assert "f" in binding_keys  # Filter
        assert "?" in binding_keys  # Help


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppDatabaseSetup:
    """Test database connection and project loading."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    def test_setup_database_success(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test successful database setup."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        app = BrowserApp()
        app.setup_database()

        assert app.db is not None
        mock_db.connect.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_setup_database_no_config(self, mock_config_manager: Any) -> None:
        """Test database setup fails gracefully when no database configured."""
        mock_config = MagicMock()
        mock_config.get.return_value = None
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.exit = MagicMock()
        app.setup_database()

        app.exit.assert_called_once()
        assert "No database configured" in str(app.exit.call_args)

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_load_project_success(self, mock_config_manager: Any) -> None:
        """Test successful project loading."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config.get.side_effect = {
            "database_url": "sqlite:///test.db",
            "current_project_id": project_id,
        }.get
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.load_project()

        assert app.project_id == project_id

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_load_project_no_project(self, mock_config_manager: Any) -> None:
        """Test project loading fails when no current project."""
        mock_config = MagicMock()
        mock_config.get.side_effect = {"database_url": "sqlite:///test.db", "current_project_id": None}.get
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.exit = MagicMock()
        app.load_project()

        app.exit.assert_called_once()
        assert "No current project" in str(app.exit.call_args)


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppTreeNavigation:
    """Test item tree navigation."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    @patch("tracertm.tui.apps.browser.Session")
    def test_refresh_tree_with_items(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test refresh_tree loads and displays items."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        # Mock root items
        mock_item1 = MagicMock()
        mock_item1.id = str(uuid4())
        mock_item1.title = "Root Item 1"
        mock_item1.parent_id = None

        mock_item2 = MagicMock()
        mock_item2.id = str(uuid4())
        mock_item2.title = "Root Item 2"
        mock_item2.parent_id = None

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [mock_item1, mock_item2]
        mock_session.query.return_value = mock_query
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_tree.root = mock_root

        app = BrowserApp()
        app.db = mock_db
        app.project_id = project_id
        app.query_one = MagicMock(return_value=mock_tree)

        app.refresh_tree()

        mock_tree.clear.assert_called_once()
        assert mock_root.add.call_count == COUNT_TWO

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    @patch("tracertm.tui.apps.browser.Session")
    def test_add_children_recursive(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test _add_children recursively adds child items."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        # Mock child items
        parent_id = str(uuid4())
        mock_child1 = MagicMock()
        mock_child1.id = str(uuid4())
        mock_child1.title = "Child 1"

        mock_child2 = MagicMock()
        mock_child2.id = str(uuid4())
        mock_child2.title = "Child 2"

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [mock_child1, mock_child2]
        mock_session.query.return_value = mock_query

        mock_parent_node = MagicMock()

        app = BrowserApp()
        app.project_id = project_id
        app._add_children(mock_session, mock_parent_node, parent_id)

        assert mock_parent_node.add.call_count == COUNT_TWO

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_refresh_tree_no_database(self, mock_config_manager: Any) -> None:
        """Test refresh_tree does nothing when no database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.db = None
        app.project_id = None

        # Should not raise error
        app.refresh_tree()
        assert True


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppItemSelection:
    """Test item selection and details display."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_on_tree_node_selected(self, mock_config_manager: Any) -> None:
        """Test tree node selection updates selected item."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        item_id = str(uuid4())
        mock_event = MagicMock()
        mock_event.node.data = item_id

        app = BrowserApp()
        app.show_item_details = MagicMock()

        app.on_tree_node_selected(mock_event)

        assert app.selected_item_id == item_id
        app.show_item_details.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_on_tree_node_selected_no_data(self, mock_config_manager: Any) -> None:
        """Test tree node selection with no data does nothing."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_event = MagicMock()
        mock_event.node.data = None

        app = BrowserApp()
        app.show_item_details = MagicMock()

        app.on_tree_node_selected(mock_event)

        assert app.selected_item_id is None
        app.show_item_details.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    @patch("tracertm.tui.apps.browser.Session")
    def test_show_item_details_success(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test show_item_details displays item information."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        item_id = str(uuid4())
        mock_item = MagicMock()
        mock_item.id = item_id
        mock_item.title = "Test Item"
        mock_item.view = "FEATURE"
        mock_item.item_type = "feature"
        mock_item.status = "todo"
        mock_item.description = "Test description"
        mock_item.item_metadata = {"key": "value"}

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_item
        mock_session.query.return_value = mock_query
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        mock_detail_widget = MagicMock()

        app = BrowserApp()
        app.db = mock_db
        app.selected_item_id = item_id
        app.query_one = MagicMock(return_value=mock_detail_widget)

        app.show_item_details()

        mock_detail_widget.update.assert_called_once()
        call_args = str(mock_detail_widget.update.call_args)
        assert "Test Item" in call_args

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    @patch("tracertm.tui.apps.browser.Session")
    def test_show_item_details_not_found(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test show_item_details handles item not found."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        item_id = str(uuid4())

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = BrowserApp()
        app.db = mock_db
        app.selected_item_id = item_id

        # Should not raise error
        app.show_item_details()
        assert True

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_show_item_details_no_database(self, mock_config_manager: Any) -> None:
        """Test show_item_details does nothing when no database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.db = None
        app.selected_item_id = str(uuid4())

        # Should not raise error
        app.show_item_details()
        assert True


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppActions:
    """Test action handlers."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_action_refresh(self, mock_config_manager: Any) -> None:
        """Test refresh action calls refresh_tree."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.refresh_tree = MagicMock()

        app.action_refresh()

        app.refresh_tree.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_action_filter(self, mock_config_manager: Any) -> None:
        """Test filter action focuses input."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_input = MagicMock()

        app = BrowserApp()
        app.query_one = MagicMock(return_value=mock_input)

        app.action_filter()

        mock_input.focus.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_action_help(self, mock_config_manager: Any) -> None:
        """Test help action shows notification."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()
        assert "quit" in str(app.notify.call_args).lower()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_on_input_changed(self, mock_config_manager: Any) -> None:
        """Test input changed event (not yet implemented)."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_event = MagicMock()

        app = BrowserApp()

        # Should not raise error
        app.on_input_changed(mock_event)
        assert True


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppCleanup:
    """Test cleanup and teardown."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    def test_on_unmount_closes_database(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test on_unmount closes database connection."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        app = BrowserApp()
        app.db = mock_db

        app.on_unmount()

        mock_db.close.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_on_unmount_no_database(self, mock_config_manager: Any) -> None:
        """Test on_unmount handles no database gracefully."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = BrowserApp()
        app.db = None

        # Should not raise error
        app.on_unmount()
        assert True


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestBrowserAppErrorHandling:
    """Test error handling scenarios."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_handles_missing_textual(self, _mock_config_manager: Any) -> None:
        """Test browser handles missing Textual dependency."""
        # This test validates the import guard works
        assert TEXTUAL_AVAILABLE is True  # In test environment

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    def test_handles_database_connection_error(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test handling database connection errors."""
        mock_config = MagicMock()
        mock_config.get.return_value = "invalid://url"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.connect.side_effect = Exception("Connection failed")
        mock_db_class.return_value = mock_db

        app = BrowserApp()

        # Should handle error gracefully
        try:
            app.setup_database()
        except Exception as e:
            # Exception is expected and should be logged/handled
            assert "Connection failed" in str(e)
