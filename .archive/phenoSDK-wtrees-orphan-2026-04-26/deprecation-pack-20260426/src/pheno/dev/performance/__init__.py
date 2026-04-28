"""Performance monitoring and optimization utilities.

This module provides comprehensive performance monitoring capabilities including:
- Real-time performance metrics collection
- Provider performance benchmarking
- Resource usage tracking (CPU, memory)
- Memory leak detection
- Performance decorators for automatic tracking
- Correlation ID support for distributed tracing

Basic usage:
    >>> from pheno.dev.performance import get_performance_monitor, measure_performance
    >>>
    >>> # Using context manager
    >>> monitor = get_performance_monitor()
    >>> with monitor.measure_operation("my_operation") as metrics:
    ...     # perform operation
    ...     metrics.input_tokens = 100
    >>>
    >>> # Using decorator
    >>> @measure_performance("my_function")
    ... def my_function():
    ...     return "result"
"""

from .benchmarking import Benchmarker
from .decorators import measure_method, measure_performance
from .memory import MemoryLeakDetector
from .metrics import OperationStats, PerformanceMetrics, ProviderBenchmark
from .monitor import PerformanceMonitor, get_performance_monitor
from .optimizer import (
    CompressionResult,
    ContextManager,
    GarbageCollector,
    LargeFileHandler,
    MemoryMonitor,
    MemoryOptimizer,
    MemoryStats,
    TextCompressor,
    compress_large_context,
    get_compressed_context,
    get_memory_optimizer,
    get_memory_recommendations,
    optimize_memory_now,
)

__all__ = [
    # Benchmarking
    "Benchmarker",
    "CompressionResult",
    "ContextManager",
    "GarbageCollector",
    "LargeFileHandler",
    # Memory leak detection
    "MemoryLeakDetector",
    # Memory optimization (from optimizer.py)
    "MemoryMonitor",
    "MemoryOptimizer",
    "MemoryStats",
    "OperationStats",
    # Metrics
    "PerformanceMetrics",
    # Core monitoring
    "PerformanceMonitor",
    "ProviderBenchmark",
    "TextCompressor",
    "compress_large_context",
    "get_compressed_context",
    "get_memory_optimizer",
    "get_memory_recommendations",
    "get_performance_monitor",
    "measure_method",
    # Decorators
    "measure_performance",
    "optimize_memory_now",
]
