"""
High level memory optimisation orchestration.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .compression import ContextManager, TextCompressor
from .garbage import GarbageCollector
from .monitoring import MemoryMonitor

if TYPE_CHECKING:
    from .stats import MemoryStats

logger = logging.getLogger(__name__)


class MemoryOptimizer:
    """
    Coordinate memory optimisation strategies.
    """

    def __init__(self):
        self.memory_monitor = MemoryMonitor()
        self.context_manager = ContextManager()
        self.text_compressor = TextCompressor()
        self._optimization_history: list[dict[str, Any]] = []

    def optimize_memory(self) -> dict[str, Any]:
        """
        Execute a full optimisation pass and return results.
        """
        start_time = time.time()
        start_memory = self.memory_monitor.get_current_memory_stats().rss_mb

        optimizations_performed: list[str] = []

        gc_result = GarbageCollector.force_gc()
        optimizations_performed.append(f"GC collected {gc_result['collected']} objects")

        GarbageCollector.optimize_gc_thresholds()
        optimizations_performed.append("Optimized GC thresholds")

        circular_refs = GarbageCollector.find_circular_references()
        if circular_refs:
            optimizations_performed.append(
                f"Found {len(circular_refs)} potential circular references",
            )

        context_usage = self.context_manager.get_memory_usage()
        if context_usage["contexts_count"] > 0:
            optimizations_performed.append(
                f"Managing {context_usage['contexts_count']} compressed contexts",
            )

        end_time = time.time()
        end_memory = self.memory_monitor.get_current_memory_stats().rss_mb
        memory_freed_mb = start_memory - end_memory

        result = {
            "optimizations_performed": optimizations_performed,
            "memory_freed_mb": memory_freed_mb,
            "optimization_time_ms": (end_time - start_time) * 1000,
            "memory_before_mb": start_memory,
            "memory_after_mb": end_memory,
            "gc_stats": GarbageCollector.get_gc_stats(),
            "context_usage": context_usage,
        }

        self._optimization_history.append(result)
        if len(self._optimization_history) > 50:
            self._optimization_history = self._optimization_history[-25:]

        logger.info(
            "Memory optimization completed: %.1fMB freed in %.1fms",
            memory_freed_mb,
            result["optimization_time_ms"],
        )

        return result

    def get_optimization_recommendations(self) -> list[str]:
        """
        Return current optimisation recommendations.
        """
        recommendations: list[str] = []

        pressure = self.memory_monitor.check_memory_pressure()
        recommendations.extend(pressure["recommendations"])
        recommendations.extend(self.memory_monitor.suggest_optimizations())

        if len(self._optimization_history) >= 3:
            recent_optimizations = self._optimization_history[-3:]
            avg_freed = sum(opt["memory_freed_mb"] for opt in recent_optimizations) / len(
                recent_optimizations,
            )

            if avg_freed < 10:
                recommendations.append(
                    "Recent optimizations had limited impact - consider architectural changes",
                )

            if any(len(opt["optimizations_performed"]) > 5 for opt in recent_optimizations):
                recommendations.append(
                    "Frequent optimizations needed - investigate memory usage patterns",
                )

        return list(set(recommendations))

    def get_memory_health_report(self) -> dict[str, Any]:
        """
        Summarise current memory health with a score.
        """
        current_stats = self.memory_monitor.get_current_memory_stats()
        pressure_check = self.memory_monitor.check_memory_pressure()
        context_usage = self.context_manager.get_memory_usage()
        gc_stats = GarbageCollector.get_gc_stats()
        recommendations = self.get_optimization_recommendations()

        return {
            "timestamp": datetime.now().isoformat(),
            "memory_stats": {
                "process_memory_mb": current_stats.rss_mb,
                "system_memory_percent": current_stats.percent,
                "available_memory_mb": current_stats.available_mb,
            },
            "pressure_status": pressure_check["status"],
            "context_compression": context_usage,
            "garbage_collection": {
                "tracked_objects": gc_stats["tracked_objects"],
                "recent_collections": sum(current_stats.gc_collections.values()),
                "recent_collected": sum(current_stats.gc_collected.values()),
            },
            "optimization_history_count": len(self._optimization_history),
            "recommendations": recommendations,
            "health_score": self._calculate_health_score(current_stats, pressure_check),
        }

    def _calculate_health_score(self, stats: MemoryStats, pressure: dict[str, Any]) -> int:
        """
        Compute a crude health score from memory metrics.
        """
        score = 100

        if stats.percent > 90:
            score -= 40
        elif stats.percent > 80:
            score -= 20
        elif stats.percent > 70:
            score -= 10

        if pressure["status"] == "critical":
            score -= 30
        elif pressure["status"] == "warning":
            score -= 15
        elif pressure["status"] == "growing":
            score -= 10

        uncollectable = sum(stats.gc_uncollectable.values())
        if uncollectable > 0:
            score -= min(20, uncollectable * 2)

        return max(0, score)
