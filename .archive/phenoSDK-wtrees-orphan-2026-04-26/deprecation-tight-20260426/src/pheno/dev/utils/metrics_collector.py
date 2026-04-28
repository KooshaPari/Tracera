"""Metrics collection and aggregation for pheno-sdk.

Provides MetricsCollector for collecting metrics and MetricsAggregator for time-windowed
aggregation.
"""

from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any

from pheno.dev.utils.metric_types import Counter, Gauge, Histogram, MetricValue


class MetricsCollector:
    """Central metrics collector with multiple metric types.

    Example:
        collector = MetricsCollector()

        # Counter
        collector.increment("requests")
        collector.increment("requests", tags={"method": "GET"})

        # Gauge
        collector.set_gauge("memory", 1024)

        # Histogram
        collector.observe("latency", 0.123)

        # Timer
        with collector.timer("operation"):
            # Code to time
            pass

        # Get metrics
        metrics = collector.get_metrics()
    """

    def __init__(self):
        """
        Initialize metrics collector.
        """
        self._counters: dict[str, Counter] = defaultdict(lambda: Counter(""))
        self._gauges: dict[str, Gauge] = defaultdict(lambda: Gauge(""))
        self._histograms: dict[str, Histogram] = defaultdict(lambda: Histogram(""))
        self._timers: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, amount: int = 1, tags: dict[str, str] | None = None):
        """Increment a counter.

        Args:
            name: Counter name
            amount: Amount to increment
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        counter = self._counters[key]
        counter.name = name
        counter.increment(amount)

    def decrement(self, name: str, amount: int = 1, tags: dict[str, str] | None = None):
        """Decrement a counter.

        Args:
            name: Counter name
            amount: Amount to decrement
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        counter = self._counters[key]
        counter.name = name
        counter.decrement(amount)

    def set_gauge(self, name: str, value: float, tags: dict[str, str] | None = None):
        """Set a gauge value.

        Args:
            name: Gauge name
            value: Gauge value
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        gauge = self._gauges[key]
        gauge.name = name
        gauge.set(value)

    def observe(self, name: str, value: float, tags: dict[str, str] | None = None):
        """Record a histogram observation.

        Args:
            name: Histogram name
            value: Observed value
            tags: Optional tags
        """
        key = self._make_key(name, tags)
        histogram = self._histograms[key]
        histogram.name = name
        histogram.observe(value)

    @contextmanager
    def timer(self, name: str, tags: dict[str, str] | None = None):
        """Context manager for timing operations.

        Args:
            name: Timer name
            tags: Optional tags

        Example:
            with collector.timer("database_query"):
                result = db.query()
        """
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.observe(name, duration, tags)

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics.

        Returns:
            Dictionary with counters, gauges, and histograms
        """
        return {
            "counters": {key: counter.value for key, counter in self._counters.items()},
            "gauges": {key: gauge.value for key, gauge in self._gauges.items()},
            "histograms": {
                key: histogram.statistics() for key, histogram in self._histograms.items()
            },
        }

    def reset(self):
        """
        Reset all metrics.
        """
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()

    @staticmethod
    def _make_key(name: str, tags: dict[str, str] | None = None) -> str:
        """
        Create metric key from name and tags.
        """
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"


class MetricsAggregator:
    """Aggregate metrics over time windows.

    Example:
        aggregator = MetricsAggregator(window_seconds=60)

        # Record metrics
        for i in range(100):
            aggregator.record("requests", 1)

        # Get aggregated stats
        stats = aggregator.aggregate("requests")
    """

    def __init__(self, window_seconds: int = 60):
        """Initialize aggregator.

        Args:
            window_seconds: Time window for aggregation
        """
        self.window_seconds = window_seconds
        self._metrics: dict[str, list[MetricValue]] = defaultdict(list)

    def record(self, name: str, value: float, tags: dict[str, str] | None = None):
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags
        """
        metric = MetricValue(name=name, value=value, tags=tags or {})
        self._metrics[name].append(metric)

        # Clean old metrics
        self._clean_old_metrics(name)

    def aggregate(self, name: str) -> dict[str, Any]:
        """Aggregate metrics for a name.

        Args:
            name: Metric name

        Returns:
            Aggregated statistics
        """
        self._clean_old_metrics(name)

        values = [m.value for m in self._metrics[name]]

        if not values:
            return {
                "count": 0,
                "sum": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
            }

        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
        }

    def _clean_old_metrics(self, name: str):
        """
        Remove metrics outside time window.
        """
        cutoff = time.time() - self.window_seconds
        self._metrics[name] = [m for m in self._metrics[name] if m.timestamp > cutoff]


__all__ = [
    "MetricsAggregator",
    "MetricsCollector",
]
