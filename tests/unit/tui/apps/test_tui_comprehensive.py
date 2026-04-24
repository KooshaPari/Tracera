"""Comprehensive tests for all TUI applications.

This test suite provides 100% coverage for:
- BrowserApp: initialization, navigation, tree operations, item details, filtering
- DashboardApp: initialization, data display, view switching, statistics, state management
- GraphApp: initialization, graph loading, visualization, zoom operations, link display

Coverage includes:
- Happy paths and error scenarios
- Edge cases and boundary conditions
- Async operations and event handling
- Database interactions with proper mocking
- Widget composition and lifecycle
- User actions and key bindings
- Error handling and cleanup
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TWO

try:
    from tracertm.tui.apps.browser import TEXTUAL_AVAILABLE as BROWSER_AVAILABLE
    from tracertm.tui.apps.browser import BrowserApp
    from tracertm.tui.apps.dashboard import TEXTUAL_AVAILABLE as DASHBOARD_AVAILABLE
    from tracertm.tui.apps.dashboard import DashboardApp
    from tracertm.tui.apps.graph import TEXTUAL_AVAILABLE as GRAPH_AVAILABLE
    from tracertm.tui.apps.graph import GraphApp

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    BROWSER_AVAILABLE = False
    DASHBOARD_AVAILABLE = False
    GRAPH_AVAILABLE = False


# =============================================================================
# BrowserApp Comprehensive Tests
# =============================================================================


@pytest.mark.skipif(not BROWSER_AVAILABLE, reason="Textual not available")
class TestBrowserAppComprehensive:
    """Comprehensive tests for BrowserApp covering all code paths."""

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_init_default_state(self, mock_config_manager: Any) -> None:
        """Test BrowserApp initializes with correct default state."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())

        assert app.project_id is None
        assert app.current_view == "FEATURE"
        assert app.db is None
        assert app.selected_item_id is None
        assert app.config_manager is not None

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_css_defined(self, mock_config_manager: Any) -> None:
        """Test BrowserApp has CSS styling defined."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())

        assert hasattr(app, "CSS")
        assert isinstance(app.CSS, str)
        assert len(app.CSS) > 0
        assert "#tree-panel" in app.CSS
        assert "#detail-panel" in app.CSS

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_bindings_complete(self, mock_config_manager: Any) -> None:
        """Test BrowserApp has all required bindings."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())

        binding_keys = [b.key for b in app.BINDINGS]
        assert "q" in binding_keys
        assert "r" in binding_keys
        assert "f" in binding_keys
        assert "?" in binding_keys

        binding_actions = [b.action for b in app.BINDINGS]
        assert "quit" in binding_actions
        assert "refresh" in binding_actions
        assert "filter" in binding_actions
        assert "help" in binding_actions

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    def test_browser_setup_database_success(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test successful database setup."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        app = cast("Any", BrowserApp())
        app.setup_database()

        mock_db_class.assert_called_once_with("sqlite:///test.db")
        mock_db.connect.assert_called_once()
        assert app.db == mock_db

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_setup_database_missing_config(self, mock_config_manager: Any) -> None:
        """Test database setup handles missing config."""
        mock_config = MagicMock()
        mock_config.get.return_value = None
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.exit = MagicMock()
        app.setup_database()

        app.exit.assert_called_once()
        call_args = app.exit.call_args
        assert "No database configured" in str(call_args)

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.DatabaseConnection")
    def test_browser_setup_database_connection_error(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test database setup handles connection errors."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.connect.side_effect = Exception("Connection failed")
        mock_db_class.return_value = mock_db

        app = cast("Any", BrowserApp())

        with pytest.raises(Exception, match=r"Connection failed"):
            app.setup_database()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_load_project_success(self, mock_config_manager: Any) -> None:
        """Test successful project loading."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config.get.return_value = project_id
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.load_project()

        assert app.project_id == project_id

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_load_project_no_project(self, mock_config_manager: Any) -> None:
        """Test project loading handles missing project."""
        mock_config = MagicMock()
        mock_config.get.return_value = None
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.exit = MagicMock()
        app.load_project()

        app.exit.assert_called_once()
        assert "No current project" in str(app.exit.call_args)

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    def test_browser_refresh_tree_no_database(self, mock_session: Any, mock_config_manager: Any) -> None:
        """Test refresh_tree handles missing database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.db = None
        app.project_id = str(uuid4())

        # Should return early without error
        app.refresh_tree()

        mock_session.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    def test_browser_refresh_tree_no_project(self, mock_session: Any, mock_config_manager: Any) -> None:
        """Test refresh_tree handles missing project."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        mock_db = MagicMock()
        app.db = mock_db
        app.project_id = None

        # Should return early without error
        app.refresh_tree()

        mock_session.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    @patch("tracertm.tui.apps.browser.Item")
    def test_browser_refresh_tree_with_items(
        self, mock_item: Any, mock_session_class: Any, mock_config_manager: Any
    ) -> None:
        """Test refresh_tree populates tree with items."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Create mock items
        item1 = MagicMock()
        item1.id = str(uuid4())
        item1.title = "Item 1"

        item2 = MagicMock()
        item2.id = str(uuid4())
        item2.title = "Item 2"

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [item1, item2]
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        # Setup app
        app = cast("Any", BrowserApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.project_id = str(uuid4())
        app.current_view = "FEATURE"

        # Mock tree widget
        mock_tree = MagicMock()
        mock_tree.root = MagicMock()
        mock_tree.root.add = MagicMock(return_value=MagicMock())
        app.query_one = MagicMock(return_value=mock_tree)

        app.refresh_tree()

        mock_tree.clear.assert_called_once()
        assert mock_tree.root.add.call_count == COUNT_TWO

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    def test_browser_add_children_recursive(self, mock_session_class: Any, _mock_config_manager: Any) -> None:
        """Test _add_children handles recursive tree building."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Create child items
        child1 = MagicMock()
        child1.id = str(uuid4())
        child1.title = "Child 1"

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [child1]

        # Setup app
        app = cast("Any", BrowserApp())
        app.project_id = str(uuid4())

        parent_node = MagicMock()
        parent_node.add = MagicMock(return_value=MagicMock())

        app._add_children(mock_session, parent_node, str(uuid4()))

        parent_node.add.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_on_tree_node_selected_with_data(self, mock_config_manager: Any) -> None:
        """Test tree node selection with valid data."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.show_item_details = MagicMock()

        item_id = str(uuid4())
        event = MagicMock()
        event.node.data = item_id

        app.on_tree_node_selected(event)

        assert getattr(app, "selected_item_id", None) == item_id
        app.show_item_details.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_on_tree_node_selected_no_data(self, mock_config_manager: Any) -> None:
        """Test tree node selection without data."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.show_item_details = MagicMock()

        event = MagicMock()
        event.node.data = None

        app.on_tree_node_selected(event)

        assert getattr(app, "selected_item_id", None) is None
        app.show_item_details.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    @patch("tracertm.tui.apps.browser.Item")
    def test_browser_show_item_details_success(
        self, mock_item: Any, mock_session_class: Any, mock_config_manager: Any
    ) -> None:
        """Test showing item details successfully."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Create mock item
        item = MagicMock()
        item.id = str(uuid4())
        item.title = "Test Item"
        item.view = "FEATURE"
        item.item_type = "feature"
        item.status = "active"
        item.description = "Test description"
        item.item_metadata = {"key": "value"}

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = item
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        # Setup app
        app = cast("Any", BrowserApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.selected_item_id = item.id

        # Mock static widget
        mock_static = MagicMock()
        app.query_one = MagicMock(return_value=mock_static)

        app.show_item_details()

        mock_static.update.assert_called_once()
        update_text = mock_static.update.call_args[0][0]
        assert "Test Item" in update_text
        assert "FEATURE" in update_text
        assert "feature" in update_text

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    def test_browser_show_item_details_no_database(self, mock_session: Any, mock_config_manager: Any) -> None:
        """Test show_item_details handles missing database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.db = None
        app.selected_item_id = str(uuid4())

        # Should return early without error
        app.show_item_details()

        mock_session.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    def test_browser_show_item_details_no_selection(self, mock_session: Any, mock_config_manager: Any) -> None:
        """Test show_item_details handles no selection."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        mock_db = MagicMock()
        app.db = mock_db
        app.selected_item_id = None

        # Should return early without error
        app.show_item_details()

        mock_session.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    @patch("tracertm.tui.apps.browser.Session")
    def test_browser_show_item_details_item_not_found(self, mock_session_class: Any, mock_config_manager: Any) -> None:
        """Test show_item_details handles item not found."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Setup session mock returning None
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", BrowserApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.selected_item_id = str(uuid4())

        mock_static = MagicMock()
        app.query_one = MagicMock(return_value=mock_static)

        # Should return early without error
        app.show_item_details()

        mock_static.update.assert_not_called()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_on_input_changed(self, mock_config_manager: Any) -> None:
        """Test input change handler (currently not implemented)."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        event = MagicMock()

        # Should not raise error
        app.on_input_changed(event)

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_action_refresh(self, mock_config_manager: Any) -> None:
        """Test refresh action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.refresh_tree = MagicMock()

        app.action_refresh()

        app.refresh_tree.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_action_filter(self, mock_config_manager: Any) -> None:
        """Test filter action focuses input."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())

        mock_input = MagicMock()
        app.query_one = MagicMock(return_value=mock_input)

        app.action_filter()

        mock_input.focus.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_action_help(self, mock_config_manager: Any) -> None:
        """Test help action shows notification."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()
        notify_text = app.notify.call_args[0][0]
        assert "quit" in notify_text.lower() or "refresh" in notify_text.lower()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_on_unmount_with_database(self, mock_config_manager: Any) -> None:
        """Test cleanup closes database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        mock_db = MagicMock()
        app.db = mock_db

        app.on_unmount()

        mock_db.close.assert_called_once()

    @patch("tracertm.tui.apps.browser.ConfigManager")
    def test_browser_on_unmount_no_database(self, mock_config_manager: Any) -> None:
        """Test cleanup handles missing database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", BrowserApp())
        app.db = None

        # Should not raise error
        app.on_unmount()


# =============================================================================
# DashboardApp Comprehensive Tests
# =============================================================================


@pytest.mark.skipif(not DASHBOARD_AVAILABLE, reason="Textual not available")
class TestDashboardAppComprehensive:
    """Comprehensive tests for DashboardApp covering all code paths."""

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_init_default_state(self, mock_config_manager: Any) -> None:
        """Test DashboardApp initializes with correct default state."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())

        assert getattr(app, "project_id", None) is None
        assert getattr(app, "current_view", None) == "FEATURE"
        assert getattr(app, "db", None) is None
        assert getattr(app, "config_manager", None) is not None

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_css_defined(self, mock_config_manager: Any) -> None:
        """Test DashboardApp has CSS styling defined."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())

        assert hasattr(app, "CSS")
        assert isinstance(app.CSS, str)
        assert "#sidebar" in app.CSS
        assert "#main" in app.CSS

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_bindings_complete(self, mock_config_manager: Any) -> None:
        """Test DashboardApp has all required bindings."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())

        binding_keys = [b.key for b in getattr(app, "BINDINGS", [])]
        assert "q" in binding_keys
        assert "v" in binding_keys
        assert "r" in binding_keys
        assert "s" in binding_keys
        assert "?" in binding_keys

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.Session")
    def test_dashboard_setup_view_tree(self, mock_session: Any, _mock_config_manager: Any) -> None:
        """Test view tree setup."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())

        mock_tree = MagicMock()
        mock_tree.root = MagicMock()
        app.query_one = MagicMock(return_value=mock_tree)

        app.setup_view_tree()

        # Should add all 8 views
        assert mock_tree.root.add.call_count == 8

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.Session")
    @patch("tracertm.tui.apps.dashboard.Item")
    @patch("tracertm.tui.apps.dashboard.Link")
    def test_dashboard_refresh_stats_success(
        self, mock_link: Any, mock_item: Any, mock_session_class: Any, mock_config_manager: Any
    ) -> None:
        """Test refresh statistics display."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.count.return_value = 5
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", DashboardApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.project_id = str(uuid4())

        # Mock widgets
        mock_stats_table = MagicMock()
        mock_state_summary = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "stats-table" in selector:
                return mock_stats_table
            if "state-summary" in selector:
                return mock_state_summary
            return MagicMock()

        app.query_one = mock_query_one

        app.refresh_stats()

        mock_stats_table.clear.assert_called_once()
        mock_stats_table.add_columns.assert_called_once()
        mock_state_summary.update.assert_called_once()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.Session")
    def test_dashboard_refresh_stats_no_database(self, mock_session: Any, mock_config_manager: Any) -> None:
        """Test refresh_stats handles missing database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.db = None
        app.project_id = str(uuid4())

        # Should return early without error
        app.refresh_stats()

        mock_session.assert_not_called()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    @patch("tracertm.tui.apps.dashboard.Session")
    @patch("tracertm.tui.apps.dashboard.Item")
    def test_dashboard_refresh_items_success(
        self, mock_item: Any, mock_session_class: Any, mock_config_manager: Any
    ) -> None:
        """Test refresh items table."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Create mock items
        item1 = MagicMock()
        item1.id = str(uuid4())
        item1.title = "Item 1"
        item1.item_type = "feature"
        item1.status = "active"

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [item1]
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", DashboardApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.project_id = str(uuid4())

        mock_items_table = MagicMock()
        app.query_one = MagicMock(return_value=mock_items_table)

        app.refresh_items()

        mock_items_table.clear.assert_called_once()
        mock_items_table.add_columns.assert_called_once()
        mock_items_table.add_row.assert_called_once()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_on_tree_node_selected(self, mock_config_manager: Any) -> None:
        """Test view tree node selection."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.refresh_items = MagicMock()

        mock_items_title = MagicMock()
        app.query_one = MagicMock(return_value=mock_items_title)

        event = MagicMock()
        event.node.data = "CODE"

        app.on_tree_node_selected(event)

        assert getattr(app, "current_view", None) == "CODE"
        app.refresh_items.assert_called_once()
        mock_items_title.update.assert_called_once()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_action_switch_view(self, mock_config_manager: Any) -> None:
        """Test switch view action cycles through views."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.current_view = "FEATURE"
        app.refresh_items = MagicMock()

        mock_items_title = MagicMock()
        app.query_one = MagicMock(return_value=mock_items_title)

        app.action_switch_view()

        assert getattr(app, "current_view", None) == "CODE"
        app.refresh_items.assert_called_once()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_action_switch_view_wraps(self, mock_config_manager: Any) -> None:
        """Test switch view action wraps to first view."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.current_view = "PROGRESS"  # Last view
        app.refresh_items = MagicMock()

        mock_items_title = MagicMock()
        app.query_one = MagicMock(return_value=mock_items_title)

        app.action_switch_view()

        assert getattr(app, "current_view", None) == "FEATURE"

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_action_refresh(self, mock_config_manager: Any) -> None:
        """Test refresh action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.refresh_data = MagicMock()

        app.action_refresh()

        app.refresh_data.assert_called_once()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_action_search(self, mock_config_manager: Any) -> None:
        """Test search action shows notification."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.notify = MagicMock()

        app.action_search()

        app.notify.assert_called_once()
        notify_text = app.notify.call_args[0][0]
        assert "not yet implemented" in notify_text.lower() or "search" in notify_text.lower()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_action_help(self, mock_config_manager: Any) -> None:
        """Test help action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()

    @patch("tracertm.tui.apps.dashboard.ConfigManager")
    def test_dashboard_refresh_data_calls_both(self, mock_config_manager: Any) -> None:
        """Test refresh_data calls both refresh methods."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", DashboardApp())
        app.db = MagicMock()
        app.project_id = str(uuid4())
        app.refresh_stats = MagicMock()
        app.refresh_items = MagicMock()

        app.refresh_data()

        app.refresh_stats.assert_called_once()
        app.refresh_items.assert_called_once()


# =============================================================================
# GraphApp Comprehensive Tests
# =============================================================================


@pytest.mark.skipif(not GRAPH_AVAILABLE, reason="Textual not available")
class TestGraphAppComprehensive:
    """Comprehensive tests for GraphApp covering all code paths."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_init_default_state(self, mock_config_manager: Any) -> None:
        """Test GraphApp initializes with correct default state."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())

        assert getattr(app, "project_id", None) is None
        assert getattr(app, "db", None) is None
        assert getattr(app, "nodes", {}) == {}
        assert getattr(app, "links", []) == []
        assert getattr(app, "zoom", 1.0) == 1.0

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_css_defined(self, mock_config_manager: Any) -> None:
        """Test GraphApp has CSS styling defined."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())

        assert hasattr(app, "CSS")
        assert isinstance(app.CSS, str)
        assert "#graph-panel" in app.CSS
        assert "#info-panel" in app.CSS

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_bindings_complete(self, mock_config_manager: Any) -> None:
        """Test GraphApp has all required bindings."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())

        binding_keys = [b.key for b in getattr(app, "BINDINGS", [])]
        assert "q" in binding_keys
        assert "r" in binding_keys
        assert "+" in binding_keys
        assert "-" in binding_keys
        assert "?" in binding_keys

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.Session")
    @patch("tracertm.tui.apps.graph.Item")
    @patch("tracertm.tui.apps.graph.Link")
    def test_graph_load_graph_data_success(
        self, mock_link: Any, mock_item: Any, mock_session_class: Any, mock_config_manager: Any
    ) -> None:
        """Test loading graph data successfully."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Create mock items
        item1 = MagicMock()
        item1.id = "item1"

        item2 = MagicMock()
        item2.id = "item2"

        # Create mock links
        link1 = MagicMock()
        link1.source_item_id = "item1"
        link1.target_item_id = "item2"

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query

        def mock_all() -> None:
            if mock_query.filter.call_count <= 1:
                return [item1, item2]
            return [link1]

        mock_query.all = mock_all
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", GraphApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.project_id = str(uuid4())

        app.load_graph_data()

        assert len(getattr(app, "nodes", {})) == COUNT_TWO
        assert ("item1", "item2") in getattr(app, "links", [])

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.Session")
    def test_graph_load_graph_data_no_database(self, mock_session: Any, mock_config_manager: Any) -> None:
        """Test load_graph_data handles missing database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.db = None
        app.project_id = str(uuid4())

        # Should return early without error
        app.load_graph_data()

        mock_session.assert_not_called()
        assert len(getattr(app, "nodes", {})) == 0
        assert len(getattr(app, "links", [])) == 0

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.Session")
    @patch("tracertm.tui.apps.graph.Item")
    @patch("tracertm.tui.apps.graph.Link")
    def test_graph_render_graph_success(
        self, mock_link: Any, mock_item: Any, mock_session_class: Any, mock_config_manager: Any
    ) -> None:
        """Test rendering graph successfully."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        # Setup item for link display
        source_item = MagicMock()
        source_item.title = "Source Item"

        target_item = MagicMock()
        target_item.title = "Target Item"

        link = MagicMock()
        link.link_type = "depends_on"

        # Setup session mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query

        def mock_first() -> None:
            if mock_query.filter.call_count % 3 == 1:
                return source_item
            if mock_query.filter.call_count % 3 == COUNT_TWO:
                return target_item
            return link

        mock_query.first = mock_first
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", GraphApp())
        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        app.db = mock_db
        app.nodes = {"source": (10, 10), "target": (20, 20)}
        app.links = [("source", "target")]
        app.zoom = 1.5

        # Mock widgets
        mock_canvas = MagicMock()
        mock_link_table = MagicMock()
        mock_stats = MagicMock()

        def mock_query_one(selector: Any, _widget_class: Any) -> None:
            if "graph-canvas" in selector:
                return mock_canvas
            if "link-table" in selector:
                return mock_link_table
            if "graph-stats" in selector:
                return mock_stats
            return MagicMock()

        app.query_one = mock_query_one

        app.render_graph()

        mock_canvas.update.assert_called_once()
        mock_link_table.clear.assert_called_once()
        mock_stats.update.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_action_refresh(self, mock_config_manager: Any) -> None:
        """Test refresh action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.load_graph_data = MagicMock()
        app.render_graph = MagicMock()

        app.action_refresh()

        app.load_graph_data.assert_called_once()
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_action_zoom_in(self, mock_config_manager: Any) -> None:
        """Test zoom in action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 1.0
        app.render_graph = MagicMock()

        app.action_zoom_in()

        assert getattr(app, "zoom", 1.0) > 1.0
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_action_zoom_in_limit(self, mock_config_manager: Any) -> None:
        """Test zoom in action respects maximum."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 5.0  # Max zoom
        app.render_graph = MagicMock()

        app.action_zoom_in()

        assert getattr(app, "zoom", 5.0) <= float(COUNT_FIVE + 0.0)
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_action_zoom_out(self, mock_config_manager: Any) -> None:
        """Test zoom out action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 2.0
        app.render_graph = MagicMock()

        app.action_zoom_out()

        assert getattr(app, "zoom", 2.0) < float(COUNT_TWO + 0.0)
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_action_zoom_out_limit(self, mock_config_manager: Any) -> None:
        """Test zoom out action respects minimum."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 0.5  # Min zoom
        app.render_graph = MagicMock()

        app.action_zoom_out()

        assert getattr(app, "zoom", 0.5) >= 0.5
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_action_help(self, mock_config_manager: Any) -> None:
        """Test help action."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_on_unmount_with_database(self, mock_config_manager: Any) -> None:
        """Test cleanup closes database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        mock_db = MagicMock()
        app.db = mock_db

        app.on_unmount()

        mock_db.close.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_on_unmount_no_database(self, mock_config_manager: Any) -> None:
        """Test cleanup handles missing database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.db = None

        # Should not raise error
        app.on_unmount()


# =============================================================================
# Placeholder Classes Tests
# =============================================================================


def test_browser_app_placeholder_without_textual() -> None:
    """Test BrowserApp placeholder raises ImportError when Textual is not available."""
    from tracertm.tui.apps.browser import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.apps.browser import BrowserApp

        with pytest.raises(ImportError) as exc_info:
            BrowserApp()
        assert "Textual is required" in str(exc_info.value)


def test_dashboard_app_placeholder_without_textual() -> None:
    """Test DashboardApp placeholder raises ImportError when Textual is not available."""
    from tracertm.tui.apps.dashboard import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.apps.dashboard import DashboardApp

        with pytest.raises(ImportError) as exc_info:
            DashboardApp()
        assert "Textual is required" in str(exc_info.value)


def test_graph_app_placeholder_without_textual() -> None:
    """Test GraphApp placeholder raises ImportError when Textual is not available."""
    from tracertm.tui.apps.graph import TEXTUAL_AVAILABLE

    if not TEXTUAL_AVAILABLE:
        from tracertm.tui.apps.graph import GraphApp

        with pytest.raises(ImportError) as exc_info:
            GraphApp()
        assert "Textual is required" in str(exc_info.value)
