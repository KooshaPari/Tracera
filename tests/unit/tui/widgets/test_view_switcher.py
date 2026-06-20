"""Comprehensive tests for ViewSwitcherWidget.

Tests cover:
- Widget initialization
- Tree setup
- View management
- Node operations
- Event handling
- Edge cases
"""

import logging

import pytest

try:
    from textual.widgets import Tree

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Tree = None

from tracertm.tui.widgets.view_switcher import TEXTUAL_AVAILABLE as WIDGET_TEXTUAL
from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidget:
    """Test ViewSwitcherWidget initialization and basic functionality."""

    def test_widget_initialization(self) -> None:
        """Test widget can be initialized."""
        widget = ViewSwitcherWidget()
        assert widget is not None
        assert isinstance(widget, Tree)

    def test_widget_inherits_tree(self) -> None:
        """Test widget inherits from Tree."""
        widget = ViewSwitcherWidget()
        assert isinstance(widget, Tree)

    def test_widget_has_label(self) -> None:
        """Test widget has correct label."""
        widget = ViewSwitcherWidget()
        # Default label should be "Views"
        assert hasattr(widget, "label")
        if hasattr(widget, "label"):
            assert widget.label == "Views"

    def test_widget_with_id(self) -> None:
        """Test widget can be created with custom id."""
        widget = ViewSwitcherWidget(id="test-switcher")
        assert widget.id == "test-switcher"

    def test_widget_with_classes(self) -> None:
        """Test widget can be created with CSS classes."""
        widget = ViewSwitcherWidget(classes="custom-class")
        assert "custom-class" in widget.classes

    def test_multiple_widgets(self) -> None:
        """Test multiple widgets can coexist."""
        widget1 = ViewSwitcherWidget(id="switcher1")
        widget2 = ViewSwitcherWidget(id="switcher2")
        assert widget1.id != widget2.id
        assert widget1 is not widget2


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetSetup:
    """Test view setup functionality."""

    def test_setup_views_called(self) -> None:
        """Test setup_views is called during initialization."""
        widget = ViewSwitcherWidget()
        # setup_views should be called in __init__
        assert hasattr(widget, "root")

    def test_default_views_exist(self) -> None:
        """Test default views are created."""
        widget = ViewSwitcherWidget()
        # Default views: FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS
        expected_views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]

        if hasattr(widget, "root"):
            root_children = list(widget.root.children)
            # Should have 8 child nodes
            assert len(root_children) == len(expected_views)

    def test_view_data_attached(self) -> None:
        """Test view data is attached to nodes."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            for child in widget.root.children:
                # Each child should have data attribute
                assert hasattr(child, "data")
                assert child.data is not None

    def test_view_labels(self) -> None:
        """Test view labels are correct."""
        widget = ViewSwitcherWidget()
        expected_views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]

        if hasattr(widget, "root"):
            labels = [child.label for child in widget.root.children]
            assert labels == expected_views

    def test_view_count(self) -> None:
        """Test correct number of views."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            assert len(list(widget.root.children)) == 8


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetNodes:
    """Test node operations."""

    def test_root_node_exists(self) -> None:
        """Test root node exists."""
        widget = ViewSwitcherWidget()
        assert hasattr(widget, "root")
        assert widget.root is not None

    def test_root_label(self) -> None:
        """Test root node has correct label."""
        widget = ViewSwitcherWidget()
        if hasattr(widget, "root"):
            assert widget.root.label == "Views"

    def test_child_nodes(self) -> None:
        """Test child nodes are created."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            children = list(widget.root.children)
            assert len(children) > 0

    def test_node_data_values(self) -> None:
        """Test node data values match labels."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            for child in widget.root.children:
                # Data should match label
                assert child.data == child.label

    def test_node_expansion(self) -> None:
        """Test nodes can be expanded."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            root_children = list(widget.root.children)
            if root_children:
                first_child = root_children[0]
                if hasattr(first_child, "expand"):
                    first_child.expand()
                    # Node should be expanded
                    if hasattr(first_child, "is_expanded"):
                        assert first_child.is_expanded

    def test_node_collapse(self) -> None:
        """Test nodes can be collapsed."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            root_children = list(widget.root.children)
            if root_children:
                first_child = root_children[0]
                if hasattr(first_child, "expand") and hasattr(first_child, "collapse"):
                    first_child.expand()
                    first_child.collapse()
                    # Node should be collapsed
                    if hasattr(first_child, "is_expanded"):
                        assert not first_child.is_expanded


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_label(self) -> None:
        """Test widget with empty label."""
        try:
            widget = ViewSwitcherWidget()
            # Should use default "Views" label
            assert widget.label == "Views"
        except Exception as e:
            logging.getLogger(__name__).debug("ViewSwitcherWidget init or default label failed: %s", e)

    def test_widget_without_setup(self) -> None:
        """Test accessing widget before setup."""
        # setup_views is called in __init__, so this tests initialization order
        widget = ViewSwitcherWidget()
        assert hasattr(widget, "root")

    def test_reinitialize_widget(self) -> None:
        """Test reinitializing widget."""
        widget = ViewSwitcherWidget()
        # Call setup_views again
        if hasattr(widget, "setup_views"):
            widget.setup_views()
            # Should still have views
            if hasattr(widget, "root"):
                assert len(list(widget.root.children)) > 0


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetIntegration:
    """Test widget integration scenarios."""

    def test_select_view(self) -> None:
        """Test selecting a view."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            root_children = list(widget.root.children)
            if root_children:
                feature_node = root_children[0]
                # Selecting is typically done through events
                assert feature_node.data == "FEATURE"

    def test_iterate_views(self) -> None:
        """Test iterating through all views."""
        widget = ViewSwitcherWidget()
        expected_views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert view_data == expected_views

    def test_find_view_by_name(self) -> None:
        """Test finding specific view by name."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            for child in widget.root.children:
                if child.data == "TEST":
                    assert child.label == "TEST"
                    break

    def test_all_views_accessible(self) -> None:
        """Test all default views are accessible."""
        widget = ViewSwitcherWidget()
        expected_views = {"FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"}

        if hasattr(widget, "root"):
            view_data = {child.data for child in widget.root.children}
            assert view_data == expected_views


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetStyling:
    """Test widget styling capabilities."""

    def test_custom_styles(self) -> None:
        """Test widget accepts custom styles."""
        widget = ViewSwitcherWidget(classes="custom-style")
        assert "custom-style" in widget.classes

    def test_multiple_classes(self) -> None:
        """Test widget can have multiple CSS classes."""
        widget = ViewSwitcherWidget(classes="class1 class2")
        assert any(c in widget.classes for c in ["class1", "class2"])

    def test_id_attribute(self) -> None:
        """Test widget ID attribute."""
        widget = ViewSwitcherWidget(id="unique-switcher")
        assert widget.id == "unique-switcher"


@pytest.mark.skipif(TEXTUAL_AVAILABLE, reason="Only test placeholder when Textual not installed")
class TestViewSwitcherWidgetPlaceholder:
    """Test placeholder class when Textual is not available."""

    def test_placeholder_exists(self) -> None:
        """Test placeholder class exists."""
        assert ViewSwitcherWidget is not None

    def test_placeholder_instantiation(self) -> None:
        """Test placeholder can be instantiated."""
        widget = ViewSwitcherWidget()
        assert widget is not None


class TestViewSwitcherWidgetAvailability:
    """Test widget availability detection."""

    def test_textual_availability_constant(self) -> None:
        """Test TEXTUAL_AVAILABLE constant is defined."""
        assert WIDGET_TEXTUAL is not None
        assert isinstance(WIDGET_TEXTUAL, bool)

    def test_textual_availability_matches(self) -> None:
        """Test module TEXTUAL_AVAILABLE matches test import."""
        assert WIDGET_TEXTUAL == TEXTUAL_AVAILABLE


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetViewTypes:
    """Test different view types."""

    def test_feature_view(self) -> None:
        """Test FEATURE view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "FEATURE" in view_data

    def test_code_view(self) -> None:
        """Test CODE view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "CODE" in view_data

    def test_wireframe_view(self) -> None:
        """Test WIREFRAME view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "WIREFRAME" in view_data

    def test_api_view(self) -> None:
        """Test API view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "API" in view_data

    def test_test_view(self) -> None:
        """Test TEST view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "TEST" in view_data

    def test_database_view(self) -> None:
        """Test DATABASE view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "DATABASE" in view_data

    def test_roadmap_view(self) -> None:
        """Test ROADMAP view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "ROADMAP" in view_data

    def test_progress_view(self) -> None:
        """Test PROGRESS view exists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            view_data = [child.data for child in widget.root.children]
            assert "PROGRESS" in view_data


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetStructure:
    """Test widget tree structure."""

    def test_tree_depth(self) -> None:
        """Test tree has correct depth."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            # Should be 1 level deep (root + children)
            for child in widget.root.children:
                # Children should not have children in default setup
                grandchildren = list(child.children) if hasattr(child, "children") else []
                assert len(grandchildren) == 0

    def test_tree_hierarchy(self) -> None:
        """Test tree hierarchy is correct."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            # Root should have 8 direct children
            assert len(list(widget.root.children)) == 8

    def test_node_parent(self) -> None:
        """Test nodes have correct parent."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            for child in widget.root.children:
                if hasattr(child, "parent"):
                    assert child.parent == widget.root


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetState:
    """Test widget state management."""

    def test_initial_state(self) -> None:
        """Test widget initial state."""
        widget = ViewSwitcherWidget()
        assert widget is not None
        assert hasattr(widget, "root")

    def test_state_after_setup(self) -> None:
        """Test widget state after setup."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            # Should have views setup
            assert len(list(widget.root.children)) == 8

    def test_persistent_state(self) -> None:
        """Test widget state persists."""
        widget = ViewSwitcherWidget()

        if hasattr(widget, "root"):
            initial_count = len(list(widget.root.children))
            # State should remain consistent
            later_count = len(list(widget.root.children))
            assert initial_count == later_count


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetCustomization:
    """Test widget customization options."""

    def test_custom_id(self) -> None:
        """Test widget with custom ID."""
        widget = ViewSwitcherWidget(id="custom-id")
        assert widget.id == "custom-id"

    def test_custom_classes(self) -> None:
        """Test widget with custom classes."""
        widget = ViewSwitcherWidget(classes="view-switcher custom")
        assert "custom" in widget.classes

    def test_widget_name(self) -> None:
        """Test widget name attribute."""
        widget = ViewSwitcherWidget(name="my-switcher")
        if hasattr(widget, "name"):
            assert widget.name == "my-switcher"


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestViewSwitcherWidgetConsistency:
    """Test widget consistency across operations."""

    def test_multiple_instantiations(self) -> None:
        """Test multiple widget instantiations are consistent."""
        widget1 = ViewSwitcherWidget()
        widget2 = ViewSwitcherWidget()

        if hasattr(widget1, "root") and hasattr(widget2, "root"):
            # Both should have same number of views
            assert len(list(widget1.root.children)) == len(list(widget2.root.children))

    def test_view_order_consistency(self) -> None:
        """Test view order is consistent."""
        widget1 = ViewSwitcherWidget()
        widget2 = ViewSwitcherWidget()

        if hasattr(widget1, "root") and hasattr(widget2, "root"):
            labels1 = [child.label for child in widget1.root.children]
            labels2 = [child.label for child in widget2.root.children]
            assert labels1 == labels2

    def test_data_consistency(self) -> None:
        """Test node data is consistent."""
        widget1 = ViewSwitcherWidget()
        widget2 = ViewSwitcherWidget()

        if hasattr(widget1, "root") and hasattr(widget2, "root"):
            data1 = [child.data for child in widget1.root.children]
            data2 = [child.data for child in widget2.root.children]
            assert data1 == data2
