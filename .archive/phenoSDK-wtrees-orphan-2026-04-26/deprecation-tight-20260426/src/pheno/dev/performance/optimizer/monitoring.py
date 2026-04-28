"""
Memory monitoring primitives.
"""

from __future__ import annotations

import gc
import logging
import threading
from collections import deque
from typing import Any

import psutil

from .stats import MemoryStats

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """
    Track process and system level memory usage.
    """

    def __init__(self, warning_threshold_mb: float = 1000.0, critical_threshold_mb: float = 2000.0):
        self.warning_threshold_mb = warning_threshold_mb
        self.critical_threshold_mb = critical_threshold_mb
        self.process = psutil.Process()
        self.memory_history: deque[MemoryStats] = deque(maxlen=100)
        self._lock = threading.RLock()

    def get_current_memory_stats(self) -> MemoryStats:
        """
        Return the latest memory statistics.
        """
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            system_memory = psutil.virtual_memory()

            gc_collections: dict[int, int] = {}
            gc_collected: dict[int, int] = {}
            gc_uncollectable: dict[int, int] = {}

            stats_by_generation = gc.get_stats()
            for generation in range(3):
                generation_stats = stats_by_generation[generation] if stats_by_generation else {}
                gc_collections[generation] = generation_stats.get("collections", 0)
                gc_collected[generation] = generation_stats.get("collected", 0)
                gc_uncollectable[generation] = generation_stats.get("uncollectable", 0)

            snapshot = MemoryStats(
                rss_mb=memory_info.rss / 1024 / 1024,
                vms_mb=memory_info.vms / 1024 / 1024,
                percent=memory_percent,
                total_mb=system_memory.total / 1024 / 1024,
                available_mb=system_memory.available / 1024 / 1024,
                used_mb=system_memory.used / 1024 / 1024,
                gc_collections=gc_collections,
                gc_collected=gc_collected,
                gc_uncollectable=gc_uncollectable,
            )

            with self._lock:
                self.memory_history.append(snapshot)

            return snapshot
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to get memory stats: %s", exc)
            return MemoryStats()

    def check_memory_pressure(self) -> dict[str, Any]:
        """
        Evaluate whether the process is under memory pressure.
        """
        stats = self.get_current_memory_stats()

        status = "normal"
        recommendations: list[str] = []

        if stats.rss_mb > self.critical_threshold_mb:
            status = "critical"
            recommendations.extend(
                [
                    "Immediate garbage collection required",
                    "Consider reducing context window size",
                    "Clear unnecessary caches",
                ],
            )
        elif stats.rss_mb > self.warning_threshold_mb:
            status = "warning"
            recommendations.extend(
                [
                    "Monitor memory usage closely",
                    "Consider enabling compression",
                    "Run garbage collection",
                ],
            )

        if len(self.memory_history) >= 5:
            recent_points = [point.rss_mb for point in list(self.memory_history)[-5:]]
            if recent_points[-1] > recent_points[0] * 1.5:
                status = max(
                    status,
                    "growing",
                    key=["normal", "growing", "warning", "critical"].index,
                )
                recommendations.append("Memory usage is growing rapidly")

        return {
            "status": status,
            "current_memory_mb": stats.rss_mb,
            "system_available_mb": stats.available_mb,
            "memory_percent": stats.percent,
            "recommendations": recommendations,
            "thresholds": {
                "warning_mb": self.warning_threshold_mb,
                "critical_mb": self.critical_threshold_mb,
            },
        }

    def suggest_optimizations(self) -> list[str]:
        """
        Return practical hints based on current metrics.
        """
        stats = self.get_current_memory_stats()
        suggestions: list[str] = []

        total_collections = sum(stats.gc_collections.values())
        total_collected = sum(stats.gc_collected.values())

        if total_collections > 0 and total_collected / total_collections < 0.1:
            suggestions.append("Low garbage collection efficiency - check for circular references")

        if stats.gc_uncollectable.get(2, 0) > 0:
            suggestions.append("Uncollectable objects detected - investigate circular references")

        if stats.rss_mb > 500:
            suggestions.extend(
                [
                    "Enable text compression for large contexts",
                    "Use streaming for large file operations",
                    "Implement context chunking strategies",
                ],
            )

        if stats.percent > 80:
            suggestions.extend(
                [
                    "System memory usage is high",
                    "Consider reducing concurrent operations",
                    "Clear unused caches and buffers",
                ],
            )

        return suggestions
