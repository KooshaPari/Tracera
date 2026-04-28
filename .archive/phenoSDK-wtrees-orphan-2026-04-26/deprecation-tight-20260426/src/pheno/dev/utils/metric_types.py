"""Metric types for pheno-sdk metrics collection.

Defines the core metric data structures including Counter, Gauge, Histogram, and the
base MetricValue class.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricValue:
    """Base metric value with metadata.

    Attributes:
        name: Metric name
        value: Metric value
        timestamp: Unix timestamp
        tags: Optional tags for filtering
    """

    name: str
    value: int | float
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
        }


class Counter:
    """Simple counter metric.

    Example:
        counter = Counter("requests")
        counter.increment()
        counter.increment(5)
        print(counter.value)  # 6
    """

    def __init__(self, name: str, initial: int = 0):
        """Initialize counter.

        Args:
            name: Metric name
            initial: Initial value
        """
        self.name = name
        self._value = initial

    def increment(self, amount: int = 1):
        """
        Increment counter.
        """
        self._value += amount

    def decrement(self, amount: int = 1):
        """
        Decrement counter.
        """
        self._value -= amount

    def reset(self):
        """
        Reset counter to zero.
        """
        self._value = 0

    @property
    def value(self) -> int:
        """
        Get current value.
        """
        return self._value


class Gauge:
    """Gauge metric (can go up or down).

    Example:
        gauge = Gauge("memory_usage")
        gauge.set(1024)
        gauge.increment(512)
        print(gauge.value)  # 1536
    """

    def __init__(self, name: str, initial: float = 0.0):
        """Initialize gauge.

        Args:
            name: Metric name
            initial: Initial value
        """
        self.name = name
        self._value = initial

    def set(self, value: float):
        """
        Set gauge value.
        """
        self._value = value

    def increment(self, amount: float = 1.0):
        """
        Increment gauge.
        """
        self._value += amount

    def decrement(self, amount: float = 1.0):
        """
        Decrement gauge.
        """
        self._value -= amount

    @property
    def value(self) -> float:
        """
        Get current value.
        """
        return self._value


class Histogram:
    """Histogram metric for tracking distributions.

    Example:
        histogram = Histogram("response_time")
        histogram.observe(0.123)
        histogram.observe(0.456)
        stats = histogram.statistics()
    """

    def __init__(self, name: str):
        """Initialize histogram.

        Args:
            name: Metric name
        """
        self.name = name
        self._values: list[float] = []

    def observe(self, value: float):
        """
        Record an observation.
        """
        self._values.append(value)

    def reset(self):
        """
        Clear all observations.
        """
        self._values.clear()

    @property
    def count(self) -> int:
        """
        Number of observations.
        """
        return len(self._values)

    def statistics(self) -> dict[str, float]:
        """Calculate statistics.

        Returns:
            Dictionary with min, max, mean, median, p95, p99
        """
        if not self._values:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        sorted_values = sorted(self._values)
        count = len(sorted_values)

        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "median": sorted_values[count // 2],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)],
        }


__all__ = [
    "Counter",
    "Gauge",
    "Histogram",
    "MetricValue",
]
