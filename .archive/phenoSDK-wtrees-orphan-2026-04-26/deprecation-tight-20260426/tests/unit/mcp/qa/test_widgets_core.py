"""Core test-related widgets for the TUI dashboard.

This module contains the fundamental widgets for displaying and interacting with tests.
"""

from collections import defaultdict
from typing import Any

from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import RichLog, Static, Tree


class TestTreeWidget(Widget):
    """Collapsible tree view of tests organized by category with DataTable display.

    Features:
    - Hierarchical organization by category
    - Expandable/collapsible nodes
    - Color-coded by test status
    - Click to view details
    """

    DEFAULT_CSS = """
    TestTreeWidget {
        height: auto;
        border: solid $primary;
    }

    TestTreeWidget Tree {
        background: $surface;
    }
    """

    selected_test: reactive[str | None] = reactive(None)
    test_data: reactive[dict[str, Any]] = reactive(dict, layout=True)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._test_results: dict[str, dict[str, Any]] = {}
        self._categories: dict[str, list[str]] = defaultdict(list)

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        yield Tree("Test Suite", id="test-tree")

    def update_tests(self, test_results: dict[str, dict[str, Any]]) -> None:
        """Update the tree with new test results.

        Args:
            test_results: Dictionary mapping test names to their results
        """
        self._test_results = test_results
        self._organize_by_category()
        self._rebuild_tree()

    def _organize_by_category(self) -> None:
        """
        Organize tests by category.
        """
        self._categories.clear()
        for test_name, result in self._test_results.items():
            category = result.get("category", "Uncategorized")
            self._categories[category].append(test_name)

    def _rebuild_tree(self) -> None:
        """
        Rebuild the entire tree structure.
        """
        tree = self.query_one("#test-tree", Tree)
        tree.clear()
        tree.label = f"Test Suite ({len(self._test_results)} tests)"

        for category, tests in sorted(self._categories.items()):
            # Add category node
            category_node = tree.root.add(
                f"[bold]{category}[/bold] ({len(tests)} tests)",
                expand=True,
            )

            # Add test nodes
            for test_name in sorted(tests):
                result = self._test_results[test_name]
                status = result.get("status", "pending")

                # Color code by status
                if status == "passed":
                    icon = "[green]✓[/green]"
                elif status == "failed":
                    icon = "[red]✗[/red]"
                elif status == "skipped":
                    icon = "[yellow]⊘[/yellow]"
                else:
                    icon = "[dim]○[/dim]"

                duration = result.get("duration", 0)
                label = f"{icon} {test_name} ({duration:.2f}s)"

                category_node.add_leaf(label, data={"test_name": test_name})

    @on(Tree.NodeSelected)
    def handle_selection(self, event: Tree.NodeSelected) -> None:
        """
        Handle tree node selection.
        """
        if event.node.data:
            test_name = event.node.data.get("test_name")
            if test_name:
                self.selected_test = test_name
                self.post_message(self.TestSelected(test_name))

    class TestSelected(Widget.Message):
        """
        Posted when a test is selected.
        """

        def __init__(self, test_name: str) -> None:
            super().__init__()
            self.test_name = test_name


class TestDetailWidget(Widget):
    """Detailed test output viewer with syntax highlighting.

    Features:
    - Syntax-highlighted output
    - Stack traces with line numbers
    - Test metadata display
    - Error highlighting
    """

    DEFAULT_CSS = """
    TestDetailWidget {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    TestDetailWidget VerticalScroll {
        height: 100%;
    }
    """

    test_data: reactive[dict[str, Any] | None] = reactive(None, layout=True)

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        with VerticalScroll():
            yield Static(id="detail-content")

    def watch_test_data(self, test_data: dict[str, Any] | None) -> None:
        """
        React to test data changes.
        """
        if test_data:
            self._update_display(test_data)

    def _update_display(self, test_data: dict[str, Any]) -> None:
        """
        Update the detail display with test data.
        """
        content = self.query_one("#detail-content", Static)

        # Build the display
        renderables = []

        # Test header
        test_name = test_data.get("name", "Unknown Test")
        status = test_data.get("status", "pending")

        if status == "passed":
            status_text = "[green]PASSED[/green]"
        elif status == "failed":
            status_text = "[red]FAILED[/red]"
        elif status == "skipped":
            status_text = "[yellow]SKIPPED[/yellow]"
        else:
            status_text = "[dim]PENDING[/dim]"

        header = Text()
        header.append(f"{test_name}\n", style="bold")
        header.append(f"Status: {status_text}\n")
        header.append(f"Duration: {test_data.get('duration', 0):.3f}s\n")
        header.append(f"Category: {test_data.get('category', 'N/A')}\n")

        renderables.append(Panel(header, title="Test Info"))

        # Output
        if output := test_data.get("output"):
            renderables.append(
                Panel(Syntax(output, "python", theme="monokai", line_numbers=True), title="Output"),
            )

        # Error details
        if error := test_data.get("error"):
            error_text = Text()
            error_text.append(f"Error Type: {error.get('type', 'Unknown')}\n", style="bold red")
            error_text.append(f"Message: {error.get('message', 'No message')}\n", style="red")

            if traceback := error.get("traceback"):
                error_text.append("\nTraceback:\n", style="bold")
                renderables.append(Panel(error_text, title="Error", border_style="red"))
                renderables.append(
                    Panel(
                        Syntax(traceback, "python", theme="monokai", line_numbers=True),
                        title="Stack Trace",
                        border_style="red",
                    ),
                )
            else:
                renderables.append(Panel(error_text, title="Error", border_style="red"))

        # Metadata
        if metadata := test_data.get("metadata"):
            meta_table = Table(show_header=False)
            meta_table.add_column("Key", style="cyan")
            meta_table.add_column("Value")

            for key, value in metadata.items():
                meta_table.add_row(key, str(value))

            renderables.append(Panel(meta_table, title="Metadata"))

        # Update the content
        content.update(Panel(renderables[0] if len(renderables) == 1 else renderables))


class SummaryStatsWidget(Widget):
    """Live-updating summary statistics with reactive attributes.

    Features:
    - Real-time test counts
    - Pass/fail ratios
    - Duration tracking
    - Color-coded status
    """

    DEFAULT_CSS = """
    SummaryStatsWidget {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    total_tests: reactive[int] = reactive(0)
    passed_tests: reactive[int] = reactive(0)
    failed_tests: reactive[int] = reactive(0)
    skipped_tests: reactive[int] = reactive(0)
    total_duration: reactive[float] = reactive(0.0)

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        yield Static(id="stats-content")

    def watch_total_tests(self) -> None:
        """
        React to total tests change.
        """
        self._update_display()

    def watch_passed_tests(self) -> None:
        """
        React to passed tests change.
        """
        self._update_display()

    def watch_failed_tests(self) -> None:
        """
        React to failed tests change.
        """
        self._update_display()

    def watch_skipped_tests(self) -> None:
        """
        React to skipped tests change.
        """
        self._update_display()

    def watch_total_duration(self) -> None:
        """
        React to total duration change.
        """
        self._update_display()

    def _update_display(self) -> None:
        """
        Update the statistics display.
        """
        content = self.query_one("#stats-content", Static)

        # Calculate percentages
        if self.total_tests > 0:
            pass_rate = (self.passed_tests / self.total_tests) * 100
            fail_rate = (self.failed_tests / self.total_tests) * 100
            skip_rate = (self.skipped_tests / self.total_tests) * 100
        else:
            pass_rate = fail_rate = skip_rate = 0.0

        # Create summary table
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="white")
        table.add_column("Percentage", style="green")

        table.add_row("Total Tests", str(self.total_tests), "100.0%")
        table.add_row("Passed", str(self.passed_tests), f"{pass_rate:.1f}%")
        table.add_row("Failed", str(self.failed_tests), f"{fail_rate:.1f}%")
        table.add_row("Skipped", str(self.skipped_tests), f"{skip_rate:.1f}%")
        table.add_row("Duration", f"{self.total_duration:.2f}s", "")

        # Determine overall status
        if fail_rate > 0:
            status_color = "red"
            status_text = "FAILING"
        elif pass_rate == 100:
            status_color = "green"
            status_text = "PASSING"
        else:
            status_color = "yellow"
            status_text = "PARTIAL"

        # Create status header
        header = Text()
        header.append("Test Summary: ", style="bold")
        header.append(f"[{status_color}]{status_text}[/{status_color}]")

        content.update(Panel([header, table], title="Statistics"))


class ProgressBarWidget(Widget):
    """Multi-level progress tracking (overall + per-category).

    Features:
    - Overall progress bar
    - Per-category progress
    - Real-time updates
    - Color-coded progress
    """

    DEFAULT_CSS = """
    ProgressBarWidget {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    overall_progress: reactive[float] = reactive(0.0)
    category_progress: reactive[dict[str, float]] = reactive(dict)

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        yield Static(id="progress-content")

    def watch_overall_progress(self) -> None:
        """
        React to overall progress change.
        """
        self._update_display()

    def watch_category_progress(self) -> None:
        """
        React to category progress change.
        """
        self._update_display()

    def _update_display(self) -> None:
        """
        Update the progress display.
        """
        content = self.query_one("#progress-content", Static)

        # Overall progress bar
        overall_width = 40
        overall_filled = int(overall_width * self.overall_progress / 100)
        overall_bar = "█" * overall_filled + "░" * (overall_width - overall_filled)

        overall_text = Text()
        overall_text.append("Overall Progress:\n", style="bold")
        overall_text.append(f"{overall_bar} {self.overall_progress:.1f}%\n")

        # Category progress
        if self.category_progress:
            overall_text.append("\nCategory Progress:\n", style="bold")
            for category, progress in self.category_progress.items():
                cat_width = 30
                cat_filled = int(cat_width * progress / 100)
                cat_bar = "█" * cat_filled + "░" * (cat_width - cat_filled)
                overall_text.append(f"{category}: {cat_bar} {progress:.1f}%\n")

        content.update(Panel(overall_text, title="Progress"))


class LogStreamWidget(Widget):
    """Live log output stream with auto-scroll.

    Features:
    - Real-time log streaming
    - Auto-scroll to latest
    - Log level filtering
    - Search functionality
    """

    DEFAULT_CSS = """
    LogStreamWidget {
        height: auto;
        border: solid $primary;
    }
    """

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        yield RichLog(id="log-stream")

    def add_log(self, message: str, level: str = "INFO") -> None:
        """
        Add a log message.
        """
        log_widget = self.query_one("#log-stream", RichLog)

        # Color code by level
        if level == "ERROR":
            styled_message = f"[red]{message}[/red]"
        elif level == "WARNING":
            styled_message = f"[yellow]{message}[/yellow]"
        elif level == "DEBUG":
            styled_message = f"[dim]{message}[/dim]"
        else:
            styled_message = message

        log_widget.write(styled_message)

    def clear_logs(self) -> None:
        """
        Clear all log messages.
        """
        log_widget = self.query_one("#log-stream", RichLog)
        log_widget.clear()
