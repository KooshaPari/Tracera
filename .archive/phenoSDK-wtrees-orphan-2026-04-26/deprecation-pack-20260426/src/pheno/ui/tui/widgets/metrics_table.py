"""
MetricsTable Widget - Live updating metrics display.

Provides real-time metrics tracking with:
- Auto-updating values
- Color-coded thresholds
- Sparkline charts
- Historical tracking
"""

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field

try:
    from rich.panel import Panel
    from rich.table import Table
    from textual.app import ComposeResult
    from textual.reactive import reactive
    from textual.widgets import DataTable, Static

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    DataTable = object
    def reactive(x):
        return x
    ComposeResult = object
    Panel = object
    Table = object


@dataclass
class MetricRow:
    """
    Single metric row data.
    """

    metric_name: str
    current_value: float
    unit: str = ""
    warning_threshold: float | None = None
    critical_threshold: float | None = None
    history: deque = field(default_factory=lambda: deque(maxlen=20))
    format_spec: str = ".2f"

    def add_value(self, value: float) -> None:
        """
        Add a new value to history.
        """
        self.current_value = value
        self.history.append((time.time(), value))

    @property
    def status_color(self) -> str:
        """
        Get status color based on thresholds.
        """
        if self.critical_threshold is not None and self.current_value >= self.critical_threshold:
            return "red"
        if self.warning_threshold is not None and self.current_value >= self.warning_threshold:
            return "yellow"
        return "green"

    @property
    def formatted_value(self) -> str:
        """
        Get formatted current value.
        """
        return f"{self.current_value:{self.format_spec}}{self.unit}"

    @property
    def trend(self) -> str:
        """
        Calculate trend (up, down, stable).
        """
        if len(self.history) < 2:
            return "→"

        recent = list(self.history)[-5:]
        values = [v[1] for v in recent]

        if len(values) < 2:
            return "→"

        avg_early = sum(values[: len(values) // 2]) / (len(values) // 2)
        avg_late = sum(values[len(values) // 2 :]) / (len(values) - len(values) // 2)

        diff = avg_late - avg_early
        threshold = abs(avg_early) * 0.05  # 5% threshold

        if abs(diff) < threshold:
            return "→"
        if diff > 0:
            return "↑"
        return "↓"

    def get_sparkline(self, width: int = 10) -> str:
        """
        Generate simple sparkline chart.
        """
        if len(self.history) < 2:
            return "─" * width

        values = [v[1] for v in self.history]
        if not values:
            return "─" * width

        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return "─" * width

        # Map values to sparkline characters
        chars = " ▁▂▃▄▅▆▇█"

        sparkline = ""
        step = len(values) / width

        for i in range(width):
            idx = int(i * step)
            if idx >= len(values):
                idx = len(values) - 1

            normalized = (values[idx] - min_val) / (max_val - min_val)
            char_idx = int(normalized * (len(chars) - 1))
            sparkline += chars[char_idx]

        return sparkline


class MetricsTable(Static):
    """Live metrics table widget.

    Features:
    - Real-time metric updates
    - Color-coded status based on thresholds
    - Trend indicators
    - Sparkline charts
    - Historical data tracking
    """

    update_count = reactive(0)

    def __init__(
        self,
        auto_refresh: bool = True,
        refresh_interval: float = 1.0,
        show_sparklines: bool = True,
        show_trends: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.auto_refresh = auto_refresh
        self.refresh_interval = refresh_interval
        self.show_sparklines = show_sparklines
        self.show_trends = show_trends
        self._metrics: dict[str, MetricRow] = {}
        self._callbacks: list[Callable[[dict[str, MetricRow]], None]] = []
        self._last_refresh = time.time()

    def add_metric(
        self,
        name: str,
        initial_value: float = 0.0,
        unit: str = "",
        warning_threshold: float | None = None,
        critical_threshold: float | None = None,
        format_spec: str = ".2f",
    ) -> MetricRow:
        """
        Add a new metric to track.
        """
        metric = MetricRow(
            metric_name=name,
            current_value=initial_value,
            unit=unit,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            format_spec=format_spec,
        )

        metric.add_value(initial_value)
        self._metrics[name] = metric
        self.refresh()

        return metric

    def update_metric(self, name: str, value: float) -> None:
        """
        Update a metric value.
        """
        if name not in self._metrics:
            # Auto-create metric if it doesn't exist
            self.add_metric(name, value)
        else:
            self._metrics[name].add_value(value)
            self.update_count += 1

            # Auto-refresh if enabled and interval passed
            if self.auto_refresh and (time.time() - self._last_refresh >= self.refresh_interval):
                self.refresh()
                self._last_refresh = time.time()

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(self._metrics)
            except Exception as e:
                print(f"Metrics callback error: {e}")

    def update_metrics(self, metrics: dict[str, float]) -> None:
        """
        Update multiple metrics at once.
        """
        for name, value in metrics.items():
            if name not in self._metrics:
                self.add_metric(name, value)
            else:
                self._metrics[name].add_value(value)

        self.update_count += 1

        if self.auto_refresh and (time.time() - self._last_refresh >= self.refresh_interval):
            self.refresh()
            self._last_refresh = time.time()

    def render(self) -> Panel:
        """
        Render metrics table.
        """
        if not self._metrics:
            return Panel("[dim]No metrics configured[/dim]", title="Metrics", border_style="blue")

        table = self._create_table()
        self._add_metric_rows(table)

        return Panel(table, title=f"Metrics (Updates: {self.update_count})", border_style="blue")

    def _create_table(self) -> Table:
        """
        Create and configure the metrics table.
        """
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Metric", width=25)
        table.add_column("Value", width=15, justify="right")

        if self.show_trends:
            table.add_column("Trend", width=5, justify="center")

        if self.show_sparklines:
            table.add_column("History", width=12)

        table.add_column("Status", width=8)
        return table

    def _add_metric_rows(self, table: Table) -> None:
        """
        Add rows for all metrics to the table.
        """
        for name in sorted(self._metrics.keys()):
            metric = self._metrics[name]
            row = self._build_metric_row(metric)
            table.add_row(*row)

    def _build_metric_row(self, metric: MetricRow) -> list[str]:
        """
        Build a single metric row.
        """
        row = [
            metric.metric_name,
            f"[{metric.status_color}]{metric.formatted_value}[/{metric.status_color}]",
        ]

        if self.show_trends:
            row.append(self._format_trend(metric))

        if self.show_sparklines:
            row.append(self._format_sparkline(metric))

        row.append(self._format_status(metric))
        return row

    def _format_trend(self, metric: MetricRow) -> str:
        """
        Format trend column for a metric.
        """
        trend = metric.trend
        trend_color = "green" if trend == "↑" else "red" if trend == "↓" else "dim"
        return f"[{trend_color}]{trend}[/{trend_color}]"

    def _format_sparkline(self, metric: MetricRow) -> str:
        """
        Format sparkline column for a metric.
        """
        sparkline = metric.get_sparkline(10)
        return f"[dim]{sparkline}[/dim]"

    def _format_status(self, metric: MetricRow) -> str:
        """
        Format status column for a metric.
        """
        if metric.current_value >= (metric.critical_threshold or float("inf")):
            return "[red]CRITICAL[/red]"
        if metric.current_value >= (metric.warning_threshold or float("inf")):
            return "[yellow]WARNING[/yellow]"
        return "[green]OK[/green]"

    def get_metric(self, name: str) -> MetricRow | None:
        """
        Get metric by name.
        """
        return self._metrics.get(name)

    def get_all_metrics(self) -> dict[str, MetricRow]:
        """
        Get all metrics.
        """
        return self._metrics.copy()

    def get_metric_value(self, name: str) -> float | None:
        """
        Get current value of a metric.
        """
        metric = self._metrics.get(name)
        return metric.current_value if metric else None

    def get_metric_history(self, name: str) -> list[tuple[float, float]]:
        """
        Get history for a metric.
        """
        metric = self._metrics.get(name)
        return list(metric.history) if metric else []

    def remove_metric(self, name: str) -> None:
        """
        Remove a metric.
        """
        if name in self._metrics:
            del self._metrics[name]
            self.refresh()

    def clear_metrics(self) -> None:
        """
        Clear all metrics.
        """
        self._metrics.clear()
        self.update_count = 0
        self.refresh()

    def add_callback(self, callback: Callable[[dict[str, MetricRow]], None]) -> None:
        """
        Add callback for metric updates.
        """
        self._callbacks.append(callback)

    def export_to_dict(self) -> dict[str, dict]:
        """
        Export metrics to dictionary.
        """
        return {
            name: {
                "current_value": metric.current_value,
                "unit": metric.unit,
                "status": metric.status_color,
                "trend": metric.trend,
                "history": list(metric.history),
            }
            for name, metric in self._metrics.items()
        }
