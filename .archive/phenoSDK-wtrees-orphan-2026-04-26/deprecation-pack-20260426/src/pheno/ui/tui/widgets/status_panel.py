"""
Status Panel Widget - Reusable status display with health indicators.

Ported from zen-mcp-server patterns for general use.
"""

from rich.panel import Panel
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static


class StatusPanel(Static):
    """Live status display with color-coded health indicators.

    Features:
    - Color-coded status (success, error, warning, info)
    - Visual indicators (●, ✗, ○, ◐)
    - Reactive updates
    - Customizable styling

    Example:
        panel = StatusPanel(title="API Server")
        panel.set_success("Server running on port 8000")
        panel.set_error("Connection failed")
        panel.set_warning("High memory usage")
    """

    DEFAULT_CSS = """
    StatusPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
        background: $surface;
    }

    StatusPanel.success {
        border: solid $success;
    }

    StatusPanel.error {
        border: solid $error;
    }

    StatusPanel.warning {
        border: solid $warning;
    }
    """

    status_text = reactive("")
    status_type = reactive("info")  # info, success, error, warning
    detail_text = reactive("")

    def __init__(
        self,
        title: str = "Status",
        initial_status: str = "Ready",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.status_text = initial_status
        self.border_title = title

    def render(self) -> Panel:
        """
        Render status panel with current state.
        """
        # Style mapping
        style_map = {
            "info": "blue",
            "success": "green",
            "error": "red",
            "warning": "yellow",
        }

        # Indicator mapping
        indicator_map = {
            "info": "○",
            "success": "●",
            "error": "✗",
            "warning": "⚠",
            "starting": "◐",
            "checking": "◔",
        }

        style = style_map.get(self.status_type, "blue")
        indicator = indicator_map.get(self.status_type, "○")

        # Build content
        content = Text()
        content.append(f"{indicator} ", style=f"bold {style}")
        content.append(self.status_text, style=style)

        if self.detail_text:
            content.append("\n")
            content.append(self.detail_text, style="dim")

        return Panel(content, title=self.title, border_style=style)

    def update_status(self, text: str, status_type: str = "info", detail: str = "") -> None:
        """
        Update status display.
        """
        self.status_text = text
        self.status_type = status_type
        self.detail_text = detail
        self.set_class(status_type in ["success", "error", "warning"], status_type)

    def set_success(self, text: str, detail: str = "") -> None:
        """
        Set success status.
        """
        self.update_status(text, "success", detail)

    def set_error(self, text: str, detail: str = "") -> None:
        """
        Set error status.
        """
        self.update_status(text, "error", detail)

    def set_warning(self, text: str, detail: str = "") -> None:
        """
        Set warning status.
        """
        self.update_status(text, "warning", detail)

    def set_info(self, text: str, detail: str = "") -> None:
        """
        Set info status.
        """
        self.update_status(text, "info", detail)

    def set_starting(self, text: str, detail: str = "") -> None:
        """
        Set starting status.
        """
        self.update_status(text, "starting", detail)

    def set_checking(self, text: str, detail: str = "") -> None:
        """
        Set checking status.
        """
        self.update_status(text, "checking", detail)


class StatusCard(Static):
    """Compact status card with health indicator.

    Similar to StatusPanel but more compact, designed for dashboard grids.

    Example:
        card = StatusCard("MCP Server")
        card.update_status("running", "PID 12345 | Port 8001")
    """

    DEFAULT_CSS = """
    StatusCard {
        border: round $accent-lighten-1;
        padding: 1 2;
        height: auto;
        min-height: 6;
        margin-bottom: 1;
        color: $text;
        background: $surface;
    }
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.status = "stopped"
        self.detail = "Not started"

    def render(self) -> Panel:
        """
        Render compact status card.
        """
        # Color palette
        palette = {
            "running": "bright_green",
            "starting": "bright_yellow",
            "stopping": "yellow",
            "stopped": "bright_black",
            "error": "bright_red",
            "checking": "cyan",
            "ready": "bright_green",
        }
        color = palette.get(self.status, "white")

        # Indicators
        indicators = {
            "running": "●",
            "starting": "◐",
            "stopping": "◑",
            "stopped": "○",
            "error": "✗",
            "checking": "◔",
            "ready": "●",
        }
        indicator = indicators.get(self.status, "○")

        # Build content
        content = Text()
        content.append(f"{indicator} ", style=f"bold {color}")
        content.append(self.status.upper(), style=f"bold {color}")

        if self.detail:
            content.append("\n")
            content.append(self.detail, style="dim")

        return Panel(content, title=f"[bold]{self.name}[/bold]", border_style=color, padding=(0, 1))

    def update_status(self, status: str, detail: str = ""):
        """
        Update status display.
        """
        self.status = status
        self.detail = detail
        self.refresh()


class MetricsPanel(Static):
    """Display system metrics and statistics.

    Features:
    - Key-value metric display
    - Auto-formatting (percentages, bytes, time)
    - Customizable metrics
    - Real-time updates

    Example:
        panel = MetricsPanel(title="System Metrics")
        panel.update_metrics({
            "CPU Usage": "45.2%",
            "Memory": "2.3GB / 8GB",
            "Uptime": "2h 15m",
            "Requests": "1,234"
        })
    """

    DEFAULT_CSS = """
    MetricsPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
        background: $surface;
    }
    """

    def __init__(self, title: str = "Metrics", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.metrics: dict[str, str] = {}

    def render(self) -> Panel:
        """
        Render metrics panel.
        """
        from rich.table import Table

        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold bright_cyan")
        table.add_column()

        for key, value in self.metrics.items():
            table.add_row(f"{key}:", value)

        if not self.metrics:
            table.add_row("No metrics", "")

        return Panel(
            table,
            title=f"[bold bright_magenta]{self.title}[/bold bright_magenta]",
            border_style="bright_blue",
        )

    def update_metrics(self, metrics: dict[str, str]):
        """
        Update displayed metrics.
        """
        self.metrics = metrics
        self.refresh()

    def set_metric(self, key: str, value: str):
        """
        Set a single metric.
        """
        self.metrics[key] = value
        self.refresh()

    def clear_metrics(self):
        """
        Clear all metrics.
        """
        self.metrics.clear()
        self.refresh()
