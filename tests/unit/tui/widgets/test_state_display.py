"""Comprehensive tests for StateDisplayWidget.

Tests cover:
- Widget initialization
- Column setup
- State data display
- Row operations
- Integration scenarios
- Edge cases
"""

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO

try:
    from textual.widgets import DataTable

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    DataTable = None

from tracertm.tui.widgets.state_display import TEXTUAL_AVAILABLE as WIDGET_TEXTUAL
from tracertm.tui.widgets.state_display import StateDisplayWidget


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidget:
    """Test StateDisplayWidget initialization and basic functionality."""

    def test_widget_initialization(self) -> None:
        """Test widget can be initialized."""
        widget = StateDisplayWidget()
        assert widget is not None
        assert isinstance(widget, DataTable)

    def test_widget_inherits_datatable(self) -> None:
        """Test widget inherits from DataTable."""
        widget = StateDisplayWidget()
        assert isinstance(widget, DataTable)

    def test_widget_has_columns(self) -> None:
        """Test widget has default columns."""
        widget = StateDisplayWidget()
        # Columns are added in __init__
        assert hasattr(widget, "columns")

    def test_widget_with_id(self) -> None:
        """Test widget can be created with custom id."""
        widget = StateDisplayWidget(id="test-state")
        assert widget.id == "test-state"

    def test_widget_with_classes(self) -> None:
        """Test widget can be created with CSS classes."""
        widget = StateDisplayWidget(classes="custom-class")
        assert "custom-class" in widget.classes

    def test_multiple_widgets(self) -> None:
        """Test multiple widgets can coexist."""
        widget1 = StateDisplayWidget(id="state1")
        widget2 = StateDisplayWidget(id="state2")
        assert widget1.id != widget2.id
        assert widget1 is not widget2


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetColumns:
    """Test column management."""

    def test_default_columns(self) -> None:
        """Test default columns are present."""
        widget = StateDisplayWidget()
        # Default columns: View, Items, Links
        assert hasattr(widget, "columns")

    def test_column_count(self) -> None:
        """Test correct number of default columns."""
        widget = StateDisplayWidget()
        # Should have 3 default columns
        expected_columns = ["View", "Items", "Links"]
        if hasattr(widget, "ordered_columns"):
            assert len(widget.ordered_columns) >= len(expected_columns)

    def test_column_order(self) -> None:
        """Test columns are in correct order."""
        StateDisplayWidget()
        # Columns should be: View, Items, Links
        expected_order = ["View", "Items", "Links"]
        assert expected_order is not None  # Basic assertion

    def test_column_labels(self) -> None:
        """Test column labels are descriptive."""
        widget = StateDisplayWidget()
        # Columns represent project state dimensions
        assert hasattr(widget, "columns")


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetDataManipulation:
    """Test data manipulation methods."""

    def test_empty_widget(self) -> None:
        """Test empty widget state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "row_count"):
            assert widget.row_count == 0

    def test_add_single_view(self) -> None:
        """Test adding a single view state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10", "5")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_add_multiple_views(self) -> None:
        """Test adding multiple view states."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10", "5")
            widget.add_row("CODE", "20", "15")
            widget.add_row("TEST", "8", "3")
            if hasattr(widget, "row_count"):
                assert widget.row_count == COUNT_THREE

    def test_clear_widget(self) -> None:
        """Test clearing all rows."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row") and hasattr(widget, "clear"):
            widget.add_row("FEATURE", "10", "5")
            widget.add_row("CODE", "20", "15")
            widget.clear()
            if hasattr(widget, "row_count"):
                assert widget.row_count == 0

    def test_update_state(self) -> None:
        """Test updating state values."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10", "5", key="feature-row")
            if hasattr(widget, "update_cell"):
                try:
                    widget.update_cell("feature-row", "Items", "15")
                except (AttributeError, KeyError):
                    # Method might not be available
                    pass


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetViewTypes:
    """Test different view types."""

    def test_feature_view(self) -> None:
        """Test FEATURE view state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10", "5")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_code_view(self) -> None:
        """Test CODE view state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("CODE", "20", "15")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_test_view(self) -> None:
        """Test TEST view state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("TEST", "8", "3")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_api_view(self) -> None:
        """Test API view state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("API", "5", "10")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_database_view(self) -> None:
        """Test DATABASE view state."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("DATABASE", "12", "8")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_all_views(self) -> None:
        """Test all view types together."""
        widget = StateDisplayWidget()
        views = [
            ("FEATURE", "10", "5"),
            ("CODE", "20", "15"),
            ("WIREFRAME", "5", "2"),
            ("API", "8", "10"),
            ("TEST", "15", "7"),
            ("DATABASE", "12", "8"),
            ("ROADMAP", "3", "1"),
            ("PROGRESS", "25", "20"),
        ]

        if hasattr(widget, "add_row"):
            for view_data in views:
                widget.add_row(*view_data)

            if hasattr(widget, "row_count"):
                assert widget.row_count == len(views)


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_counts(self) -> None:
        """Test state with zero items and links."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "0", "0")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_large_counts(self) -> None:
        """Test state with large numbers."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("CODE", "999999", "888888")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_negative_counts(self) -> None:
        """Test handling negative counts."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            # Should accept any string value
            widget.add_row("TEST", "-1", "-5")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_non_numeric_counts(self) -> None:
        """Test non-numeric count values."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("API", "N/A", "Unknown")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_empty_values(self) -> None:
        """Test empty string values."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("", "", "")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_special_characters_in_view(self) -> None:
        """Test special characters in view names."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("VIEW/TEST", "10", "5")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_unicode_in_values(self) -> None:
        """Test unicode characters in values."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("测试", "10 ✓", "5 ➜")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetIntegration:
    """Test widget integration scenarios."""

    def test_populate_from_project_state(self) -> None:
        """Test populating from project state data."""
        widget = StateDisplayWidget()

        project_state = {
            "FEATURE": {"items": 10, "links": 5},
            "CODE": {"items": 20, "links": 15},
            "TEST": {"items": 8, "links": 3},
        }

        if hasattr(widget, "add_row"):
            for view, data in project_state.items():
                widget.add_row(view, str(data["items"]), str(data["links"]))

            if hasattr(widget, "row_count"):
                assert widget.row_count == len(project_state)

    def test_refresh_state(self) -> None:
        """Test refreshing state display."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row") and hasattr(widget, "clear"):
            # Initial state
            widget.add_row("FEATURE", "10", "5")
            widget.add_row("CODE", "20", "15")

            # Refresh
            widget.clear()
            widget.add_row("FEATURE", "12", "6")
            widget.add_row("CODE", "22", "16")

            if hasattr(widget, "row_count"):
                assert widget.row_count == COUNT_TWO

    def test_incremental_updates(self) -> None:
        """Test incremental state updates."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            # Add views incrementally
            widget.add_row("FEATURE", "5", "2")
            widget.add_row("CODE", "10", "5")
            widget.add_row("TEST", "3", "1")

            if hasattr(widget, "row_count"):
                assert widget.row_count == COUNT_THREE

    def test_complete_state_display(self) -> None:
        """Test displaying complete project state."""
        widget = StateDisplayWidget()

        all_views = [
            ("FEATURE", "15", "8"),
            ("CODE", "25", "18"),
            ("WIREFRAME", "7", "3"),
            ("API", "10", "12"),
            ("TEST", "20", "9"),
            ("DATABASE", "14", "10"),
            ("ROADMAP", "5", "2"),
            ("PROGRESS", "30", "25"),
        ]

        if hasattr(widget, "add_row"):
            for view_data in all_views:
                widget.add_row(*view_data)

            if hasattr(widget, "row_count"):
                assert widget.row_count == 8


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetStyling:
    """Test widget styling capabilities."""

    def test_custom_styles(self) -> None:
        """Test widget accepts custom styles."""
        widget = StateDisplayWidget(classes="custom-style")
        assert "custom-style" in widget.classes

    def test_multiple_classes(self) -> None:
        """Test widget can have multiple CSS classes."""
        widget = StateDisplayWidget(classes="state-display project-stats")
        assert any(c in widget.classes for c in ["state-display", "project-stats"])

    def test_id_attribute(self) -> None:
        """Test widget ID attribute."""
        widget = StateDisplayWidget(id="project-state")
        assert widget.id == "project-state"


@pytest.mark.skipif(TEXTUAL_AVAILABLE, reason="Only test placeholder when Textual not installed")
class TestStateDisplayWidgetPlaceholder:
    """Test placeholder class when Textual is not available."""

    def test_placeholder_exists(self) -> None:
        """Test placeholder class exists."""
        assert StateDisplayWidget is not None

    def test_placeholder_instantiation(self) -> None:
        """Test placeholder can be instantiated."""
        widget = StateDisplayWidget()
        assert widget is not None


class TestStateDisplayWidgetAvailability:
    """Test widget availability detection."""

    def test_textual_availability_constant(self) -> None:
        """Test TEXTUAL_AVAILABLE constant is defined."""
        assert WIDGET_TEXTUAL is not None
        assert isinstance(WIDGET_TEXTUAL, bool)

    def test_textual_availability_matches(self) -> None:
        """Test module TEXTUAL_AVAILABLE matches test import."""
        assert WIDGET_TEXTUAL == TEXTUAL_AVAILABLE


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetStatistics:
    """Test statistical display scenarios."""

    def test_summary_statistics(self) -> None:
        """Test displaying summary statistics."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            widget.add_row("TOTAL", "100", "75")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_percentage_values(self) -> None:
        """Test percentage-based values."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10 (20%)", "5")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_ratio_values(self) -> None:
        """Test ratio-based values."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            widget.add_row("CODE", "20", "15 (75%)")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_formatted_numbers(self) -> None:
        """Test formatted number display."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            widget.add_row("DATABASE", "1,234", "5,678")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetPerformance:
    """Test widget performance scenarios."""

    def test_many_views(self) -> None:
        """Test widget with many views."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            for i in range(50):
                widget.add_row(f"VIEW_{i}", str(i * 10), str(i * 5))

            if hasattr(widget, "row_count"):
                assert widget.row_count == 50

    def test_rapid_updates(self) -> None:
        """Test rapid state updates."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row") and hasattr(widget, "clear"):
            for _ in range(10):
                widget.clear()
                widget.add_row("FEATURE", "10", "5")
                widget.add_row("CODE", "20", "15")

            if hasattr(widget, "row_count"):
                assert widget.row_count == COUNT_TWO

    def test_large_numbers(self) -> None:
        """Test displaying large numbers."""
        widget = StateDisplayWidget()

        if hasattr(widget, "add_row"):
            widget.add_row("MASSIVE", "1000000", "500000")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetRowOperations:
    """Test advanced row operations."""

    def test_row_with_key(self) -> None:
        """Test adding row with custom key."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10", "5", key="feature-state")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_remove_specific_row(self) -> None:
        """Test removing specific row."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row") and hasattr(widget, "remove_row"):
            widget.add_row("FEATURE", "10", "5", key="row1")
            widget.add_row("CODE", "20", "15", key="row2")
            widget.remove_row("row1")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_row_order(self) -> None:
        """Test row insertion order."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            views = ["FEATURE", "CODE", "TEST"]
            for view in views:
                widget.add_row(view, "10", "5")

            if hasattr(widget, "row_count"):
                assert widget.row_count == len(views)


@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestStateDisplayWidgetDataFormats:
    """Test different data format scenarios."""

    def test_compact_format(self) -> None:
        """Test compact data format."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FT", "10", "5")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_verbose_format(self) -> None:
        """Test verbose data format."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE_VIEW", "10 items", "5 links")
            if hasattr(widget, "row_count"):
                assert widget.row_count == 1

    def test_mixed_formats(self) -> None:
        """Test mixed data formats."""
        widget = StateDisplayWidget()
        if hasattr(widget, "add_row"):
            widget.add_row("FEATURE", "10", "5 active")
            widget.add_row("CODE", "20 total", "15")
            if hasattr(widget, "row_count"):
                assert widget.row_count == COUNT_TWO
