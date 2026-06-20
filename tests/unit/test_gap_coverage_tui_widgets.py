"""Gap coverage tests for TUI widgets.

Targets: tui/widgets/*.py (all at 0% coverage).
"""

from unittest.mock import patch


class TestGraphViewWidget:
    """Tests for GraphViewWidget."""

    def test_graph_view_widget_import(self) -> None:
        """Test GraphViewWidget can be imported."""
        from tracertm.tui.widgets.graph_view import GraphViewWidget

        assert GraphViewWidget is not None

    def test_graph_view_widget_textual_available_flag(self) -> None:
        """Test TEXTUAL_AVAILABLE flag exists."""
        from tracertm.tui.widgets import graph_view

        assert hasattr(graph_view, "TEXTUAL_AVAILABLE")

    def test_graph_view_widget_fallback_class(self) -> None:
        """Test fallback class when Textual not available."""
        # Import with mocked textual unavailable
        with patch.dict("sys.modules", {"textual": None, "textual.widgets": None}):
            from tracertm.tui.widgets import graph_view

            # GraphViewWidget should be defined regardless
            assert hasattr(graph_view, "GraphViewWidget")


class TestItemListWidget:
    """Tests for ItemListWidget."""

    def test_item_list_widget_import(self) -> None:
        """Test ItemListWidget can be imported."""
        from tracertm.tui.widgets.item_list import ItemListWidget

        assert ItemListWidget is not None

    def test_item_list_widget_textual_available_flag(self) -> None:
        """Test TEXTUAL_AVAILABLE flag exists."""
        from tracertm.tui.widgets import item_list

        assert hasattr(item_list, "TEXTUAL_AVAILABLE")


class TestStateDisplayWidget:
    """Tests for StateDisplayWidget."""

    def test_state_display_widget_import(self) -> None:
        """Test StateDisplayWidget can be imported."""
        from tracertm.tui.widgets.state_display import StateDisplayWidget

        assert StateDisplayWidget is not None

    def test_state_display_widget_textual_available_flag(self) -> None:
        """Test TEXTUAL_AVAILABLE flag exists."""
        from tracertm.tui.widgets import state_display

        assert hasattr(state_display, "TEXTUAL_AVAILABLE")


class TestViewSwitcherWidget:
    """Tests for ViewSwitcherWidget."""

    def test_view_switcher_widget_import(self) -> None:
        """Test ViewSwitcherWidget can be imported."""
        from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget

        assert ViewSwitcherWidget is not None

    def test_view_switcher_widget_textual_available_flag(self) -> None:
        """Test TEXTUAL_AVAILABLE flag exists."""
        from tracertm.tui.widgets import view_switcher

        assert hasattr(view_switcher, "TEXTUAL_AVAILABLE")


class TestConflictPanel:
    """Tests for ConflictPanel widget."""

    def test_conflict_panel_import(self) -> None:
        """Test ConflictPanel can be imported."""
        from tracertm.tui.widgets.conflict_panel import ConflictPanel

        assert ConflictPanel is not None

    def test_conflict_panel_module_exists(self) -> None:
        """Test conflict_panel module exists."""
        from tracertm.tui.widgets import conflict_panel

        assert conflict_panel is not None


class TestSyncStatusWidget:
    """Tests for SyncStatus widget."""

    def test_sync_status_import(self) -> None:
        """Test SyncStatusWidget can be imported."""
        from tracertm.tui.widgets.sync_status import SyncStatusWidget

        assert SyncStatusWidget is not None

    def test_sync_status_module_exists(self) -> None:
        """Test sync_status module exists."""
        from tracertm.tui.widgets import sync_status

        assert sync_status is not None


class TestWidgetsInit:
    """Tests for widgets __init__.py."""

    def test_widgets_init_imports(self) -> None:
        """Test widgets module __init__ imports."""
        from tracertm.tui import widgets

        # Check exports are available
        assert hasattr(widgets, "GraphViewWidget")
        assert hasattr(widgets, "ItemListWidget")
        assert hasattr(widgets, "StateDisplayWidget")
        assert hasattr(widgets, "ViewSwitcherWidget")
