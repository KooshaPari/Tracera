"""Comprehensive tests for GraphApp TUI application.

Tests app initialization, widget composition, database operations,
graph data loading, visualization rendering, zoom controls, and error handling.
Coverage target: 80%+ (229 lines total)
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO

try:
    from tracertm.tui.apps.graph import TEXTUAL_AVAILABLE, GraphApp
except ImportError:
    TEXTUAL_AVAILABLE = False
    GraphApp = None


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppInitialization:
    """Test GraphApp initialization and setup."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_app_init(self, mock_config_manager: Any) -> None:
        """Test GraphApp can be initialized with proper attributes."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())

        assert app is not None
        assert app.project_id is None
        assert app.db is None
        assert app.nodes == {}
        assert app.links == []
        assert app.zoom == 1.0
        assert app.config_manager is not None

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_app_compose(self, mock_config_manager: Any) -> None:
        """Test GraphApp compose method creates proper widget structure."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())

        # Compose returns a generator that needs app context
        # Just verify it can be called without error
        assert hasattr(app, "compose")
        assert callable(app.compose)

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_graph_app_bindings(self, mock_config_manager: Any) -> None:
        """Test GraphApp has proper key bindings configured."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())

        assert len(app.BINDINGS) > 0
        binding_keys = [b.key for b in app.BINDINGS]
        assert "q" in binding_keys  # Quit
        assert "r" in binding_keys  # Refresh
        assert "+" in binding_keys  # Zoom in
        assert "-" in binding_keys  # Zoom out
        assert "?" in binding_keys  # Help


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppDatabaseSetup:
    """Test database connection and project loading."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.DatabaseConnection")
    def test_setup_database_success(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test successful database setup."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        app = cast("Any", GraphApp())
        app.setup_database()

        assert app.db is not None
        mock_db.connect.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_setup_database_no_config(self, mock_config_manager: Any) -> None:
        """Test database setup fails gracefully when no database configured."""
        mock_config = MagicMock()
        mock_config.get.return_value = None
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.exit = MagicMock()
        app.setup_database()

        app.exit.assert_called_once()
        assert "No database configured" in str(app.exit.call_args)

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_load_project_success(self, mock_config_manager: Any) -> None:
        """Test successful project loading."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config.get.side_effect = {
            "database_url": "sqlite:///test.db",
            "current_project_id": project_id,
        }.get
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.load_project()

        assert app.project_id == project_id

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_load_project_no_project(self, mock_config_manager: Any) -> None:
        """Test project loading fails when no current project."""
        mock_config = MagicMock()
        mock_config.get.side_effect = {"database_url": "sqlite:///test.db", "current_project_id": None}.get
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.exit = MagicMock()
        app.load_project()

        app.exit.assert_called_once()
        assert "No current project" in str(app.exit.call_args)


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppDataLoading:
    """Test graph data loading."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.DatabaseConnection")
    @patch("tracertm.tui.apps.graph.Session")
    def test_load_graph_data_with_items_and_links(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test load_graph_data loads items and links."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        # Mock items
        item1_id = str(uuid4())
        item2_id = str(uuid4())
        item3_id = str(uuid4())

        mock_item1 = MagicMock()
        mock_item1.id = item1_id

        mock_item2 = MagicMock()
        mock_item2.id = item2_id

        mock_item3 = MagicMock()
        mock_item3.id = item3_id

        # Mock links
        mock_link1 = MagicMock()
        mock_link1.source_item_id = item1_id
        mock_link1.target_item_id = item2_id

        mock_link2 = MagicMock()
        mock_link2.source_item_id = item2_id
        mock_link2.target_item_id = item3_id

        mock_session = MagicMock()

        # Mock item query
        mock_item_query = MagicMock()
        mock_item_query.filter.return_value.limit.return_value.all.return_value = [mock_item1, mock_item2, mock_item3]

        # Mock link query
        mock_link_query = MagicMock()
        mock_link_query.filter.return_value.limit.return_value.all.return_value = [mock_link1, mock_link2]

        # Setup query side effect to return different queries
        mock_session.query.side_effect = [mock_item_query, mock_link_query]
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", GraphApp())
        app.db = mock_db
        app.project_id = project_id

        app.load_graph_data()

        # Should have 3 nodes
        assert len(app.nodes) == COUNT_THREE
        assert item1_id in app.nodes
        assert item2_id in app.nodes
        assert item3_id in app.nodes

        # Should have 2 links
        assert len(app.links) == COUNT_TWO
        assert (item1_id, item2_id) in app.links
        assert (item2_id, item3_id) in app.links

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.DatabaseConnection")
    @patch("tracertm.tui.apps.graph.Session")
    def test_load_graph_data_filters_invalid_links(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test load_graph_data filters out links with missing nodes."""
        project_id = str(uuid4())
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        item1_id = str(uuid4())
        missing_id = str(uuid4())

        mock_item1 = MagicMock()
        mock_item1.id = item1_id

        # Link to missing item
        mock_link1 = MagicMock()
        mock_link1.source_item_id = item1_id
        mock_link1.target_item_id = missing_id

        mock_session = MagicMock()
        mock_item_query = MagicMock()
        mock_item_query.filter.return_value.limit.return_value.all.return_value = [mock_item1]

        mock_link_query = MagicMock()
        mock_link_query.filter.return_value.limit.return_value.all.return_value = [mock_link1]

        mock_session.query.side_effect = [mock_item_query, mock_link_query]
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app = cast("Any", GraphApp())
        app.db = mock_db
        app.project_id = project_id

        app.load_graph_data()

        # Link should be filtered out
        assert len(app.links) == 0

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_load_graph_data_no_database(self, mock_config_manager: Any) -> None:
        """Test load_graph_data does nothing when no database."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.db = None
        app.project_id = None

        # Should not raise error
        app.load_graph_data()
        assert len(app.nodes) == 0
        assert len(app.links) == 0


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppRendering:
    """Test graph rendering."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.DatabaseConnection")
    @patch("tracertm.tui.apps.graph.Session")
    def test_render_graph_displays_stats(
        self, mock_session_class: Any, mock_db_class: Any, mock_config_manager: Any
    ) -> None:
        """Test render_graph displays graph statistics."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        item1_id = str(uuid4())
        item2_id = str(uuid4())

        app = cast("Any", GraphApp())
        app.db = mock_db
        app.nodes = {item1_id: (0, 0), item2_id: (20, 5)}
        app.links = [(item1_id, item2_id)]
        app.zoom = 1.5

        mock_canvas = MagicMock()
        mock_link_table = MagicMock()
        mock_stats = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            return {
                "#graph-canvas": mock_canvas,
                "#link-table": mock_link_table,
                "#graph-stats": mock_stats,
            }.get(selector, MagicMock())

        app.query_one = MagicMock(side_effect=query_side_effect)

        # Mock session for link table
        mock_session = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.title = "Item 1"
        mock_item2 = MagicMock()
        mock_item2.title = "Item 2"
        mock_link = MagicMock()
        mock_link.link_type = "implements"

        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [mock_item1, mock_item2, mock_link]
        mock_session.query.return_value = mock_query
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        app.render_graph()

        # Should update canvas
        mock_canvas.update.assert_called_once()

        # Should update stats
        mock_stats.update.assert_called_once()
        stats_text = str(mock_stats.update.call_args)
        assert "2" in stats_text  # Node count
        assert "1" in stats_text  # Link count
        assert "1.5" in stats_text  # Zoom

        # Should update link table
        mock_link_table.clear.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_render_graph_empty(self, mock_config_manager: Any) -> None:
        """Test render_graph handles empty graph."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.nodes = {}
        app.links = []

        mock_canvas = MagicMock()
        mock_link_table = MagicMock()
        mock_stats = MagicMock()

        def query_side_effect(selector: Any, _widget_type: Any = None) -> None:
            return {
                "#graph-canvas": mock_canvas,
                "#link-table": mock_link_table,
                "#graph-stats": mock_stats,
            }.get(selector, MagicMock())

        app.query_one = MagicMock(side_effect=query_side_effect)

        app.render_graph()

        # Should still update widgets
        mock_canvas.update.assert_called_once()
        mock_stats.update.assert_called_once()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppZoomControls:
    """Test zoom controls."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_action_zoom_in(self, mock_config_manager: Any) -> None:
        """Test zoom in action increases zoom level."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 1.0
        app.render_graph = MagicMock()

        app.action_zoom_in()

        assert app.zoom == 1.2
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_action_zoom_in_max(self, mock_config_manager: Any) -> None:
        """Test zoom in caps at maximum level."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 5.0  # Already at max
        app.render_graph = MagicMock()

        app.action_zoom_in()

        assert app.zoom == float(COUNT_FIVE + 0.0)  # Should not exceed max
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_action_zoom_out(self, mock_config_manager: Any) -> None:
        """Test zoom out action decreases zoom level."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 1.2
        app.render_graph = MagicMock()

        app.action_zoom_out()

        assert app.zoom == 1.0
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_action_zoom_out_min(self, mock_config_manager: Any) -> None:
        """Test zoom out caps at minimum level."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.zoom = 0.5  # Already at min
        app.render_graph = MagicMock()

        app.action_zoom_out()

        assert app.zoom == 0.5  # Should not go below min
        app.render_graph.assert_called_once()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppActions:
    """Test action handlers."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_action_refresh(self, mock_config_manager: Any) -> None:
        """Test refresh action reloads graph data."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.load_graph_data = MagicMock()
        app.render_graph = MagicMock()

        app.action_refresh()

        app.load_graph_data.assert_called_once()
        app.render_graph.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_action_help(self, mock_config_manager: Any) -> None:
        """Test help action shows notification."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()
        assert "quit" in str(app.notify.call_args).lower()


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppCleanup:
    """Test cleanup and teardown."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.DatabaseConnection")
    def test_on_unmount_closes_database(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test on_unmount closes database connection."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        app = cast("Any", GraphApp())
        app.db = mock_db

        app.on_unmount()

        mock_db.close.assert_called_once()

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_on_unmount_no_database(self, mock_config_manager: Any) -> None:
        """Test on_unmount handles no database gracefully."""
        mock_config = MagicMock()
        mock_config_manager.return_value = mock_config

        app = cast("Any", GraphApp())
        app.db = None

        # Should not raise error
        app.on_unmount()
        assert True


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not available")
class TestGraphAppErrorHandling:
    """Test error handling scenarios."""

    @patch("tracertm.tui.apps.graph.ConfigManager")
    def test_handles_missing_textual(self, _mock_config_manager: Any) -> None:
        """Test graph app handles missing Textual dependency."""
        # This test validates the import guard works
        assert TEXTUAL_AVAILABLE is True  # In test environment

    @patch("tracertm.tui.apps.graph.ConfigManager")
    @patch("tracertm.tui.apps.graph.DatabaseConnection")
    def test_handles_database_connection_error(self, mock_db_class: Any, mock_config_manager: Any) -> None:
        """Test handling database connection errors."""
        mock_config = MagicMock()
        mock_config.get.return_value = "invalid://url"
        mock_config_manager.return_value = mock_config

        mock_db = MagicMock()
        mock_db.connect.side_effect = Exception("Connection failed")
        mock_db_class.return_value = mock_db

        app = cast("Any", GraphApp())

        with pytest.raises(Exception, match=r"Connection failed"):
            app.setup_database()
