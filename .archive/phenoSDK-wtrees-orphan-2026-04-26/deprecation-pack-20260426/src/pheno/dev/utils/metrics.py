"""Unified Metrics Utilities for MCP Projects.

Provides metrics collection, aggregation, and reporting utilities
for tracking application performance and usage.

This module re-exports utilities from specialized metric modules:
- Metric types: Counter, Gauge, Histogram, MetricValue
- Collection: MetricsCollector, MetricsAggregator
- Reporting: MetricsReporter

Usage:
    from pheno.dev.utils.metrics import MetricsCollector, Counter, Timer

    collector = MetricsCollector()
    collector.increment("requests")

    with collector.timer("operation"):
        # Your code here
        pass
"""

# Re-export from specialized modules for backward compatibility
from pheno.dev.utils.metric_types import Counter, Gauge, Histogram, MetricValue
from pheno.dev.utils.metrics_collector import MetricsAggregator, MetricsCollector
from pheno.dev.utils.metrics_reporter import MetricsReporter

__all__ = [
    "Counter",
    "Gauge",
    "Histogram",
    "MetricValue",
    "MetricsAggregator",
    "MetricsCollector",
    "MetricsReporter",
]
