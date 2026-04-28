"""
Garbage collection utilities.
"""

from __future__ import annotations

import gc
import logging
from typing import Any

from .monitoring import MemoryMonitor

logger = logging.getLogger(__name__)


class GarbageCollector:
    """
    Convenience helpers around Python's GC.
    """

    @staticmethod
    def force_gc(generation: int | None = None) -> dict[str, int]:
        """
        Run garbage collection for a given generation (or all).
        """
        if generation is not None:
            collected = gc.collect(generation)
            return {"collected": collected, "generation": generation}
        collected = gc.collect()
        return {"collected": collected, "generation": "all"}

    @staticmethod
    def find_circular_references() -> list[Any]:
        """
        Locate objects that may participate in circular references.
        """
        gc.collect()
        circular_objects: list[Any] = []

        for obj in gc.get_objects():
            if gc.is_tracked(obj):
                referents = gc.get_referents(obj)
                for referent in referents:
                    if obj in gc.get_referents(referent):
                        circular_objects.append(obj)
                        break

        return circular_objects

    @staticmethod
    def get_gc_stats() -> dict[str, Any]:
        """
        Return a structured view of GC statistics.
        """
        stats = gc.get_stats()
        return {
            "generations": len(stats),
            "generation_stats": stats,
            "gc_counts": gc.get_count(),
            "gc_threshold": gc.get_threshold(),
            "tracked_objects": len(gc.get_objects()),
        }

    @staticmethod
    def optimize_gc_thresholds():
        """
        Adjust GC thresholds based on current memory pressure.
        """
        current_thresholds = gc.get_threshold()
        memory_monitor = MemoryMonitor()
        pressure = memory_monitor.check_memory_pressure()

        if pressure["status"] == "normal":
            new_thresholds = tuple(int(value * 1.5) for value in current_thresholds)
            gc.set_threshold(*new_thresholds)
            logger.debug("Increased GC thresholds: %s -> %s", current_thresholds, new_thresholds)
        elif pressure["status"] in {"warning", "critical"}:
            new_thresholds = tuple(max(100, int(value * 0.7)) for value in current_thresholds)
            gc.set_threshold(*new_thresholds)
            logger.debug("Decreased GC thresholds: %s -> %s", current_thresholds, new_thresholds)
