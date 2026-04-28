"""
Memory optimization toolkit for handling large contexts efficiently.
"""

from typing import Any

from .compression import CompressionResult, ContextManager, TextCompressor
from .coordinator import MemoryOptimizer
from .files import LargeFileHandler
from .garbage import GarbageCollector
from .monitoring import MemoryMonitor
from .stats import MemoryStats

__all__ = [
    "CompressionResult",
    "ContextManager",
    "GarbageCollector",
    "LargeFileHandler",
    "MemoryMonitor",
    "MemoryOptimizer",
    "MemoryStats",
    "TextCompressor",
]

# Lazily instantiated singleton used by the public module-level helpers.
_memory_optimizer: MemoryOptimizer | None = None


def get_memory_optimizer() -> MemoryOptimizer:
    """
    Return the shared memory optimizer instance.
    """
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer


def optimize_memory_now() -> dict[str, Any]:
    """
    Trigger an immediate memory optimization run.
    """
    optimizer = get_memory_optimizer()
    return optimizer.optimize_memory()


def get_memory_recommendations() -> list[str]:
    """
    Return recommendations from the shared memory optimizer.
    """
    optimizer = get_memory_optimizer()
    return optimizer.get_optimization_recommendations()


def compress_large_context(text: str, context_id: str | None = None) -> str | None:
    """
    Compress text when beneficial and return its context identifier.
    """
    if not context_id:
        context_id = TextCompressor.create_context_id(text)

    optimizer = get_memory_optimizer()
    if optimizer.context_manager.compress_context(context_id, text):
        return context_id
    return None


def get_compressed_context(context_id: str) -> str | None:
    """
    Retrieve a previously compressed context.
    """
    optimizer = get_memory_optimizer()
    return optimizer.context_manager.get_context(context_id)


__all__.extend(
    [
        "compress_large_context",
        "get_compressed_context",
        "get_memory_optimizer",
        "get_memory_recommendations",
        "optimize_memory_now",
    ],
)
