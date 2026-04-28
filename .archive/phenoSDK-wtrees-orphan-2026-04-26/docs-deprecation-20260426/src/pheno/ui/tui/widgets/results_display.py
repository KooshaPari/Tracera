"""
Results Display Widget - Rich display for structured output.

Ported from zen-mcp-server patterns for general use.
"""

import json
from typing import Any

from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from textual.widgets import Static


class ResultsDisplay(Static):
    """Rich display for results with syntax highlighting.

    Features:
    - Syntax highlighting (JSON, Python, YAML, etc.)
    - Line numbers
    - Word wrap
    - Multiple themes
    - Auto-formatting

    Example:
        display = ResultsDisplay(title="API Response")
        display.display_json({"status": "success", "data": {...}})
        display.display_log("Server started on port 8000")
    """

    DEFAULT_CSS = """
    ResultsDisplay {
        border: solid $primary;
        padding: 1;
        height: auto;
        background: $surface;
    }
    """

    def __init__(
        self,
        title: str = "Results",
        syntax: str = "json",
        theme: str = "monokai",
        line_numbers: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.syntax_type = syntax
        self.theme = theme
        self.line_numbers = line_numbers
        self.border_title = title
        self._content = ""

    def render(self) -> Syntax:
        """
        Render content with syntax highlighting.
        """
        return Syntax(
            self._content or "No results yet",
            self.syntax_type,
            theme=self.theme,
            line_numbers=self.line_numbers,
            word_wrap=True,
        )

    def update_content(self, content: str, syntax: str | None = None) -> None:
        """
        Update displayed content.
        """
        self._content = content
        if syntax:
            self.syntax_type = syntax
        self.refresh()

    def display_json(self, data: dict | list) -> None:
        """
        Display JSON data with formatting.
        """
        formatted = json.dumps(data, indent=2, sort_keys=True)
        self.update_content(formatted, "json")

    def display_log(self, log_text: str) -> None:
        """
        Display log output.
        """
        self.update_content(log_text, "log")

    def display_python(self, code: str) -> None:
        """
        Display Python code.
        """
        self.update_content(code, "python")

    def display_yaml(self, yaml_text: str) -> None:
        """
        Display YAML content.
        """
        self.update_content(yaml_text, "yaml")

    def display_markdown(self, md_text: str) -> None:
        """
        Display Markdown content.
        """
        self.update_content(md_text, "markdown")

    def clear(self) -> None:
        """
        Clear displayed content.
        """
        self._content = ""
        self.refresh()


class DataTableDisplay(Static):
    """Display data in a formatted table.

    Features:
    - Auto-formatting columns
    - Sortable (when used with DataTable widget)
    - Customizable styling
    - Row highlighting

    Example:
        display = DataTableDisplay(title="Test Results")
        display.set_data(
            headers=["Test", "Status", "Time"],
            rows=[
                ["test_api", "✓ PASS", "0.5s"],
                ["test_db", "✗ FAIL", "1.2s"],
            ]
        )
    """

    DEFAULT_CSS = """
    DataTableDisplay {
        border: solid $primary;
        padding: 1;
        height: auto;
        background: $surface;
    }
    """

    def __init__(self, title: str = "Data", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.headers: list[str] = []
        self.rows: list[list[str]] = []

    def render(self) -> Panel:
        """
        Render data table.
        """
        table = Table(show_header=True, header_style="bold magenta")

        # Add columns
        for header in self.headers:
            table.add_column(header)

        # Add rows
        for row in self.rows:
            table.add_row(*row)

        if not self.rows:
            # Show empty state
            for _ in self.headers:
                table.add_column("")
            table.add_row(*["No data" if i == 0 else "" for i in range(len(self.headers) or 1)])

        return Panel(table, title=f"[bold]{self.title}[/bold]", border_style="cyan")

    def set_data(self, headers: list[str], rows: list[list[str]]):
        """
        Set table data.
        """
        self.headers = headers
        self.rows = rows
        self.refresh()

    def add_row(self, row: list[str]):
        """
        Add a single row.
        """
        self.rows.append(row)
        self.refresh()

    def clear(self):
        """
        Clear all data.
        """
        self.rows.clear()
        self.refresh()


class ProgressTracker(Static):
    """Track and display progress for multiple operations.

    Features:
    - Multiple progress bars
    - Percentage display
    - Status indicators
    - ETA calculation

    Example:
        tracker = ProgressTracker(title="Build Progress")
        tracker.add_task("compile", total=100)
        tracker.update_task("compile", completed=50)
    """

    DEFAULT_CSS = """
    ProgressTracker {
        border: solid $accent;
        padding: 1;
        height: auto;
        background: $surface;
    }
    """

    def __init__(self, title: str = "Progress", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.tasks: dict[str, dict[str, Any]] = {}

    def render(self) -> Panel:
        """
        Render progress tracker.
        """
        from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )

        for task_data in self.tasks.values():
            progress.add_task(
                task_data["description"], total=task_data["total"], completed=task_data["completed"],
            )

        return Panel(progress, title=f"[bold]{self.title}[/bold]", border_style="green")

    def add_task(self, task_id: str, description: str, total: int = 100):
        """
        Add a new task to track.
        """
        self.tasks[task_id] = {"description": description, "total": total, "completed": 0}
        self.refresh()

    def update_task(self, task_id: str, completed: int):
        """
        Update task progress.
        """
        if task_id in self.tasks:
            self.tasks[task_id]["completed"] = completed
            self.refresh()

    def complete_task(self, task_id: str):
        """
        Mark task as complete.
        """
        if task_id in self.tasks:
            self.tasks[task_id]["completed"] = self.tasks[task_id]["total"]
            self.refresh()

    def remove_task(self, task_id: str):
        """
        Remove a task.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.refresh()

    def clear(self):
        """
        Clear all tasks.
        """
        self.tasks.clear()
        self.refresh()
