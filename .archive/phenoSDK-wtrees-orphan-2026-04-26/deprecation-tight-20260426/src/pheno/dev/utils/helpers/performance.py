"""
Simple performance tracking utilities for test execution.
"""

import time
from typing import Any


class PerformanceTracker:
    """
    Track test execution performance metrics.
    """

    def __init__(self) -> None:
        self.metrics: list[dict[str, Any]] = []
        self.start_time: float | None = None

    def start(self) -> None:
        """
        Start tracking.
        """
        self.start_time = time.time()

    def record(self, test_name: str, duration_ms: int, success: bool) -> None:
        """
        Record a test execution.
        """
        self.metrics.append(
            {
                "test_name": test_name,
                "duration_ms": duration_ms,
                "success": success,
                "timestamp": time.time(),
            },
        )

    def get_stats(self) -> dict[str, Any]:
        """
        Return simple aggregates about tracked tests.
        """
        if not self.metrics:
            return {}

        durations = [metric["duration_ms"] for metric in self.metrics]
        successes = sum(1 for metric in self.metrics if metric["success"])
        total_duration = sum(durations)
        count = len(self.metrics)

        return {
            "total_tests": count,
            "successful_tests": successes,
            "failed_tests": count - successes,
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / count if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "total_elapsed_seconds": time.time() - self.start_time if self.start_time else 0,
        }


__all__ = ["PerformanceTracker"]
