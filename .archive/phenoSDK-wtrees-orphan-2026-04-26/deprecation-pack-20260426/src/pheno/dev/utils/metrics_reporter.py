"""Metrics reporting and formatting for pheno-sdk.

Provides MetricsReporter for formatting and exporting collected metrics in various
formats (text, JSON).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pheno.dev.utils.logging import get_logger

if TYPE_CHECKING:
    from pheno.dev.utils.metrics_collector import MetricsCollector

logger = get_logger(__name__)


class MetricsReporter:
    """Format and report metrics.

    Example:
        collector = MetricsCollector()
        # ... collect metrics ...

        reporter = MetricsReporter(collector)
        print(reporter.format_text())
    """

    def __init__(self, collector: MetricsCollector):
        """Initialize reporter.

        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector

    def format_text(self) -> str:
        """Format metrics as plain text.

        Returns:
            Formatted metrics string
        """
        metrics = self.collector.get_metrics()
        lines = ["=== Metrics Report ===\n"]

        # Counters
        if metrics["counters"]:
            lines.append("Counters:")
            for name, value in metrics["counters"].items():
                lines.append(f"  {name}: {value}")
            lines.append("")

        # Gauges
        if metrics["gauges"]:
            lines.append("Gauges:")
            for name, value in metrics["gauges"].items():
                lines.append(f"  {name}: {value:.2f}")
            lines.append("")

        # Histograms
        if metrics["histograms"]:
            lines.append("Histograms:")
            for name, stats in metrics["histograms"].items():
                lines.append(f"  {name}:")
                lines.append(f"    count: {stats['count']}")
                lines.append(f"    min: {stats['min']:.3f}")
                lines.append(f"    max: {stats['max']:.3f}")
                lines.append(f"    mean: {stats['mean']:.3f}")
                lines.append(f"    median: {stats['median']:.3f}")
                lines.append(f"    p95: {stats['p95']:.3f}")
                lines.append(f"    p99: {stats['p99']:.3f}")
            lines.append("")

        return "\n".join(lines)

    def format_json(self) -> dict[str, Any]:
        """Format metrics as JSON-serializable dict.

        Returns:
            Metrics dictionary
        """
        return self.collector.get_metrics()

    def log_metrics(self):
        """
        Log metrics using logger.
        """
        logger.info(self.format_text())


__all__ = [
    "MetricsReporter",
]
