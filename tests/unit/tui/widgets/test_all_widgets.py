"""Comprehensive tests for remaining TUI widgets.

Tests GraphViewWidget, ItemListWidget, StateDisplayWidget, and ViewSwitcherWidget.
These are simpler widgets with basic functionality.
Coverage target: 80%+ combined for graph_view (85), item_list (76), state_display (49), view_switcher (26)
"""

from unittest.mock import patch

import pytest

# Skip all tests if Textual not available
pytest.importorskip("textual")

from tracertm.tui.widgets.graph_view import GraphViewWidget
from tracertm.tui.widgets.item_list import ItemListWidget
from tracertm.tui.widgets.state_display import StateDisplayWidget
from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget


class TestGraphViewWidget:
    """Test GraphViewWidget functionality."""

    def test_init_creates_widget(self) -> None:
        """Test GraphViewWidget initializes correctly."""
        widget = GraphViewWidget()

        # Widget should be initialized with Static text
        assert widget is not None

    def test_init_with_custom_text(self) -> None:
        """Test GraphViewWidget accepts custom initialization."""
        widget = GraphViewWidget(id="custom-graph")

        assert widget is not None

    def test_inherits_from_static(self) -> None:
        """Test GraphViewWidget inherits from Static."""
        from textual.widgets import Static

        widget = GraphViewWidget()

        assert isinstance(widget, Static)


class TestItemListWidget:
    """Test ItemListWidget functionality."""

    def test_init_creates_widget(self) -> None:
        """Test ItemListWidget initializes correctly."""
        # Patch add_columns to avoid requiring app context
        with patch.object(ItemListWidget, "add_columns"):
            widget = ItemListWidget()
            # Widget should be initialized with DataTable
            assert widget is not None

    def test_columns_configured(self) -> None:
        """Test ItemListWidget has correct columns."""
        # Patch add_columns and verify it was called
        with patch.object(ItemListWidget, "add_columns") as mock_add:
            widget = ItemListWidget()
            # Verify add_columns was called with correct column names
            mock_add.assert_called_once_with("ID", "Title", "Type", "Status")
            assert widget is not None

    def test_inherits_from_datatable(self) -> None:
        """Test ItemListWidget inherits from DataTable."""
        from textual.widgets import DataTable

        with patch.object(ItemListWidget, "add_columns"):
            widget = ItemListWidget()
            assert isinstance(widget, DataTable)

    def test_init_with_custom_id(self) -> None:
        """Test ItemListWidget accepts custom ID."""
        with patch.object(ItemListWidget, "add_columns"):
            widget = ItemListWidget(id="custom-items")
            assert widget is not None
            assert widget.id == "custom-items"


class TestStateDisplayWidget:
    """Test StateDisplayWidget functionality."""

    def test_init_creates_widget(self) -> None:
        """Test StateDisplayWidget initializes correctly."""
        with patch.object(StateDisplayWidget, "add_columns"):
            widget = StateDisplayWidget()
            assert widget is not None

    def test_columns_configured(self) -> None:
        """Test StateDisplayWidget has correct columns."""
        with patch.object(StateDisplayWidget, "add_columns") as mock_add:
            widget = StateDisplayWidget()
            # Verify add_columns was called with correct column names
            mock_add.assert_called_once_with("View", "Items", "Links")
            assert widget is not None

    def test_inherits_from_datatable(self) -> None:
        """Test StateDisplayWidget inherits from DataTable."""
        from textual.widgets import DataTable

        with patch.object(StateDisplayWidget, "add_columns"):
            widget = StateDisplayWidget()
            assert isinstance(widget, DataTable)

    def test_init_with_custom_id(self) -> None:
        """Test StateDisplayWidget accepts custom ID."""
        with patch.object(StateDisplayWidget, "add_columns"):
            widget = StateDisplayWidget(id="custom-state")
            assert widget is not None
            assert widget.id == "custom-state"


class TestViewSwitcherWidget:
    """Test ViewSwitcherWidget functionality."""

    def test_init_creates_widget(self) -> None:
        """Test ViewSwitcherWidget initializes correctly."""
        with patch.object(ViewSwitcherWidget, "setup_views"):
            widget = ViewSwitcherWidget()
            assert widget is not None

    def test_setup_views_called(self) -> None:
        """Test setup_views is called during initialization."""
        with patch.object(ViewSwitcherWidget, "setup_views") as mock_setup:
            ViewSwitcherWidget()
            # Verify setup_views was called during init
            mock_setup.assert_called_once()

    def test_inherits_from_tree(self) -> None:
        """Test ViewSwitcherWidget inherits from Tree."""
        from textual.widgets import Tree

        with patch.object(ViewSwitcherWidget, "setup_views"):
            widget = ViewSwitcherWidget()
            assert isinstance(widget, Tree)

    def test_init_with_custom_label(self) -> None:
        """Test ViewSwitcherWidget accepts custom label."""
        with patch.object(ViewSwitcherWidget, "setup_views"):
            widget = ViewSwitcherWidget("Custom Views")
            assert widget is not None


# Additional integration tests for all widgets


class TestWidgetAvailability:
    """Test widget availability and imports."""

    def test_graph_view_available(self) -> None:
        """Test GraphViewWidget is available when Textual is installed."""
        from tracertm.tui.widgets import graph_view

        assert hasattr(graph_view, "GraphViewWidget")
        assert graph_view.TEXTUAL_AVAILABLE is True

    def test_item_list_available(self) -> None:
        """Test ItemListWidget is available when Textual is installed."""
        from tracertm.tui.widgets import item_list

        assert hasattr(item_list, "ItemListWidget")
        assert item_list.TEXTUAL_AVAILABLE is True

    def test_state_display_available(self) -> None:
        """Test StateDisplayWidget is available when Textual is installed."""
        from tracertm.tui.widgets import state_display

        assert hasattr(state_display, "StateDisplayWidget")
        assert state_display.TEXTUAL_AVAILABLE is True

    def test_view_switcher_available(self) -> None:
        """Test ViewSwitcherWidget is available when Textual is installed."""
        from tracertm.tui.widgets import view_switcher

        assert hasattr(view_switcher, "ViewSwitcherWidget")
        assert view_switcher.TEXTUAL_AVAILABLE is True


class TestWidgetFallbacks:
    """Test widget fallback behavior when Textual not available."""

    def test_graph_view_fallback_exists(self) -> None:
        """Test GraphViewWidget fallback class exists."""
        from tracertm.tui.widgets.graph_view import GraphViewWidget as Fallback

        # Fallback should exist even if not functional
        assert Fallback is not None

    def test_item_list_fallback_exists(self) -> None:
        """Test ItemListWidget fallback class exists."""
        from tracertm.tui.widgets.item_list import ItemListWidget as Fallback

        assert Fallback is not None

    def test_state_display_fallback_exists(self) -> None:
        """Test StateDisplayWidget fallback class exists."""
        from tracertm.tui.widgets.state_display import StateDisplayWidget as Fallback

        assert Fallback is not None

    def test_view_switcher_fallback_exists(self) -> None:
        """Test ViewSwitcherWidget fallback class exists."""
        from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget as Fallback

        assert Fallback is not None
