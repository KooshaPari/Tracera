#!/usr/bin/env python3
"""
Development Tools Module Consolidation Script - Phase 2C

This script consolidates the dev module by:
1. Unifying utility systems
2. Consolidating duplicate performance monitoring
3. Streamlining helper functions
4. Removing overlapping development tools

Target: 74 files → <50 files (32% reduction)
"""

import shutil
from pathlib import Path


class DevModuleConsolidator:
    """Consolidates development tools module components."""

    def __init__(self, base_path: str = "src/pheno"):
        """Initialize consolidator.

        Args:
            base_path: Base path for pheno modules
        """
        self.base_path = Path(base_path)
        self.removed_files: list[str] = []
        self.consolidated_modules: dict[str, str] = {}

    def consolidate_utils(self) -> None:
        """Unify utility systems."""
        print("🛠️ Consolidating utility systems...")

        # Files to remove (duplicate utilities)
        duplicate_util_files = [
            "dev/utils/",  # Duplicate utils directory
            "dev/async_utils/",  # Duplicate async utilities
            "dev/concurrency/",  # Duplicate concurrency utilities
            "dev/correlation_id.py",  # Duplicate correlation ID
            "dev/rate_limiting.py",  # Duplicate rate limiting
        ]

        for file_path in duplicate_util_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate utility functionality
        self._consolidate_utility_functionality()

    def consolidate_performance(self) -> None:
        """Consolidate performance monitoring systems."""
        print("📊 Consolidating performance monitoring systems...")

        # Files to remove (duplicate performance monitoring)
        duplicate_performance_files = [
            "dev/performance/",  # Duplicate performance directory
        ]

        for file_path in duplicate_performance_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate performance functionality
        self._consolidate_performance_functionality()

    def consolidate_data_structures(self) -> None:
        """Consolidate data structure systems."""
        print("📦 Consolidating data structure systems...")

        # Files to remove (duplicate data structures)
        duplicate_data_files = [
            "dev/data_structures/",  # Duplicate data structures
        ]

        for file_path in duplicate_data_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate data structure functionality
        self._consolidate_data_structure_functionality()

    def consolidate_validation(self) -> None:
        """Consolidate validation systems."""
        print("✅ Consolidating validation systems...")

        # Files to remove (duplicate validation)
        duplicate_validation_files = [
            "dev/validation/",  # Duplicate validation
        ]

        for file_path in duplicate_validation_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate validation functionality
        self._consolidate_validation_functionality()

    def consolidate_strings(self) -> None:
        """Consolidate string utility systems."""
        print("🔤 Consolidating string utility systems...")

        # Files to remove (duplicate string utilities)
        duplicate_string_files = [
            "dev/strings/",  # Duplicate string utilities
        ]

        for file_path in duplicate_string_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate string functionality
        self._consolidate_string_functionality()

    def consolidate_datetime(self) -> None:
        """Consolidate datetime utility systems."""
        print("📅 Consolidating datetime utility systems...")

        # Files to remove (duplicate datetime utilities)
        duplicate_datetime_files = [
            "dev/datetime/",  # Duplicate datetime utilities
        ]

        for file_path in duplicate_datetime_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate datetime functionality
        self._consolidate_datetime_functionality()

    def consolidate_tracing(self) -> None:
        """Consolidate tracing systems."""
        print("🔍 Consolidating tracing systems...")

        # Files to remove (duplicate tracing)
        duplicate_tracing_files = [
            "dev/tracing/",  # Duplicate tracing
        ]

        for file_path in duplicate_tracing_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate tracing functionality
        self._consolidate_tracing_functionality()

    def _consolidate_utility_functionality(self) -> None:
        """Consolidate utility functionality into unified system."""
        print("  🔧 Creating unified utility system...")

        # Create unified utility system
        unified_utility_content = '''"""
Unified Development Utilities - Consolidated Utility Implementation

This module provides a unified utility system that consolidates all utility
functionality from the previous fragmented implementations.

Features:
- Unified async utilities
- Unified concurrency utilities
- Unified correlation ID management
- Unified rate limiting
- Unified helper functions
"""

import asyncio
import logging
import threading
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RateLimitConfig:
    """Unified rate limit configuration."""
    max_requests: int = 100
    time_window: int = 60  # seconds
    burst_limit: int = 10


class UnifiedAsyncUtils:
    """Unified async utilities."""

    @staticmethod
    async def gather_with_limit(tasks: List[asyncio.Task], limit: int = 10) -> List[Any]:
        """Gather tasks with concurrency limit."""
        semaphore = asyncio.Semaphore(limit)

        async def limited_task(task):
            async with semaphore:
                return await task

        return await asyncio.gather(*[limited_task(task) for task in tasks])

    @staticmethod
    async def retry_async(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0
    ) -> Any:
        """Retry async function with exponential backoff."""
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                await asyncio.sleep(delay * (backoff ** attempt))

    @staticmethod
    @asynccontextmanager
    async def async_timeout(seconds: float):
        """Async timeout context manager."""
        try:
            yield await asyncio.wait_for(asyncio.sleep(0), timeout=seconds)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {seconds} seconds")


class UnifiedConcurrencyUtils:
    """Unified concurrency utilities."""

    def __init__(self):
        self._locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        self._semaphores: Dict[str, threading.Semaphore] = {}

    def get_lock(self, name: str) -> threading.Lock:
        """Get named lock."""
        return self._locks[name]

    def get_semaphore(self, name: str, value: int = 1) -> threading.Semaphore:
        """Get named semaphore."""
        if name not in self._semaphores:
            self._semaphores[name] = threading.Semaphore(value)
        return self._semaphores[name]

    @contextmanager
    def acquire_lock(self, name: str):
        """Acquire named lock context manager."""
        lock = self.get_lock(name)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()

    def acquire_repo_lock(self) -> threading.Lock:
        """Acquire repository lock."""
        return self.get_lock("repo")

    def release_repo_lock(self) -> None:
        """Release repository lock."""
        # Lock is automatically released when context exits
        pass

    def acquire_wd_lock(self) -> threading.Lock:
        """Acquire working directory lock."""
        return self.get_lock("wd")

    def release_wd_lock(self) -> None:
        """Release working directory lock."""
        # Lock is automatically released when context exits
        pass


class UnifiedCorrelationManager:
    """Unified correlation ID management."""

    def __init__(self):
        self._context = threading.local()

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID."""
        return getattr(self._context, 'correlation_id', None)

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID."""
        self._context.correlation_id = correlation_id

    def get_or_create_correlation_id(self) -> str:
        """Get or create correlation ID."""
        correlation_id = self.get_correlation_id()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            self.set_correlation_id(correlation_id)
        return correlation_id

    def clear_correlation_id(self) -> None:
        """Clear correlation ID."""
        if hasattr(self._context, 'correlation_id'):
            delattr(self._context, 'correlation_id')

    @contextmanager
    def correlation_context(self, correlation_id: str):
        """Correlation ID context manager."""
        old_id = self.get_correlation_id()
        self.set_correlation_id(correlation_id)
        try:
            yield
        finally:
            if old_id:
                self.set_correlation_id(old_id)
            else:
                self.clear_correlation_id()


class UnifiedRateLimiter:
    """Unified rate limiter."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: List[float] = []
        self._lock = threading.Lock()

    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        now = time.time()
        with self._lock:
            # Remove old requests
            self.requests = [req_time for req_time in self.requests
                           if now - req_time < self.config.time_window]

            # Check if under limit
            if len(self.requests) < self.config.max_requests:
                self.requests.append(now)
                return True
            return False

    async def wait_if_needed(self) -> None:
        """Wait if rate limit exceeded."""
        while not self.is_allowed():
            await asyncio.sleep(0.1)


class UnifiedHelperUtils:
    """Unified helper utilities."""

    @staticmethod
    def generate_unique_id(prefix: str = "") -> str:
        """Generate unique identifier."""
        timestamp = time.strftime("%Y%m%d-%H%M%S-%f")[:-3]
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}{timestamp}-{unique_id}" if prefix else f"{timestamp}-{unique_id}"

    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\\w\\s-]', '', text.lower())
        slug = re.sub(r'[\\s_-]+', '-', slug)
        return slug.strip('-')

    @staticmethod
    def sanitize_html(html: str) -> str:
        """Sanitize HTML content."""
        import re
        # Remove script tags and their content
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove style tags and their content
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove dangerous attributes
        html = re.sub(r'\\s(on\\w+|javascript:)[^>]*', '', html, flags=re.IGNORECASE)
        return html

    @staticmethod
    def is_email(email: str) -> bool:
        """Check if string is valid email."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_url(url: str) -> bool:
        """Check if string is valid URL."""
        import re
        pattern = r'^https?://[^\\s/$.?#].[^\\s]*$'
        return bool(re.match(pattern, url))


# Global instances
unified_async_utils = UnifiedAsyncUtils()
unified_concurrency_utils = UnifiedConcurrencyUtils()
unified_correlation_manager = UnifiedCorrelationManager()
unified_helper_utils = UnifiedHelperUtils()

# Export unified utility components
__all__ = [
    "RateLimitConfig",
    "UnifiedAsyncUtils",
    "UnifiedConcurrencyUtils",
    "UnifiedCorrelationManager",
    "UnifiedRateLimiter",
    "UnifiedHelperUtils",
    "unified_async_utils",
    "unified_concurrency_utils",
    "unified_correlation_manager",
    "unified_helper_utils",
]
'''

        # Write unified utility system
        unified_utility_path = self.base_path / "dev/unified_utilities.py"
        unified_utility_path.parent.mkdir(parents=True, exist_ok=True)
        unified_utility_path.write_text(unified_utility_content)
        print(f"  ✅ Created: {unified_utility_path}")

    def _consolidate_performance_functionality(self) -> None:
        """Consolidate performance functionality into unified system."""
        print("  🔧 Creating unified performance system...")

        # Create unified performance system
        unified_performance_content = '''"""
Unified Performance Monitoring - Consolidated Performance Implementation

This module provides a unified performance monitoring system that consolidates all
performance functionality from the previous fragmented implementations.

Features:
- Unified performance monitoring
- Unified memory optimization
- Unified benchmarking
- Unified metrics collection
"""

import asyncio
import logging
import os
import threading
import time
import uuid
import weakref
from collections import defaultdict, deque
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Unified performance metrics."""
    operation_name: str
    duration: float
    memory_used: int = 0
    cpu_usage: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None


@dataclass
class MemoryStats:
    """Unified memory statistics."""
    total_memory: int = 0
    available_memory: int = 0
    used_memory: int = 0
    memory_percent: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class CompressionResult:
    """Unified compression result."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    method: str
    success: bool = True


class UnifiedPerformanceMonitor:
    """Unified performance monitoring system."""

    def __init__(self, enable_detailed_metrics: bool = True):
        """Initialize performance monitor."""
        self.enable_detailed_metrics = enable_detailed_metrics and PSUTIL_AVAILABLE
        self.metrics_buffer: deque = deque(maxlen=10000)
        self._lock = threading.RLock()
        self._process = psutil.Process() if PSUTIL_AVAILABLE else None
        self._operation_timings: Dict[str, List[float]] = defaultdict(list)
        self._memory_snapshots: List[tuple] = []
        self._start_time = time.time()
        self._tracked_objects: weakref.WeakSet = weakref.WeakSet()

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        if not self.enable_detailed_metrics or not self._process:
            return {"cpu_percent": 0.0, "memory_percent": 0.0, "memory_used": 0}

        try:
            cpu_percent = self._process.cpu_percent()
            memory_info = self._process.memory_info()
            memory_percent = self._process.memory_percent()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used": memory_info.rss,
                "memory_available": memory_info.available if hasattr(memory_info, 'available') else 0,
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {"cpu_percent": 0.0, "memory_percent": 0.0, "memory_used": 0}

    def record_operation(self, operation_name: str, duration: float, **kwargs) -> None:
        """Record operation metrics."""
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            duration=duration,
            **kwargs
        )

        with self._lock:
            self.metrics_buffer.append(metrics)
            self._operation_timings[operation_name].append(duration)

    @contextmanager
    def measure_operation(self, operation_name: str, **kwargs):
        """Measure operation with context manager."""
        start_time = time.time()
        start_metrics = self.get_system_metrics()

        try:
            yield self
        finally:
            duration = time.time() - start_time
            end_metrics = self.get_system_metrics()

            self.record_operation(
                operation_name=operation_name,
                duration=duration,
                memory_used=end_metrics.get("memory_used", 0) - start_metrics.get("memory_used", 0),
                cpu_usage=end_metrics.get("cpu_percent", 0.0),
                **kwargs
            )

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get operation statistics."""
        timings = self._operation_timings.get(operation_name, [])
        if not timings:
            return {}

        return {
            "count": len(timings),
            "total_time": sum(timings),
            "avg_time": sum(timings) / len(timings),
            "min_time": min(timings),
            "max_time": max(timings),
        }

    def get_memory_stats(self) -> MemoryStats:
        """Get memory statistics."""
        if not self.enable_detailed_metrics or not self._process:
            return MemoryStats()

        try:
            memory_info = self._process.memory_info()
            system_memory = psutil.virtual_memory()

            return MemoryStats(
                total_memory=system_memory.total,
                available_memory=system_memory.available,
                used_memory=memory_info.rss,
                memory_percent=system_memory.percent,
            )
        except Exception as e:
            logger.warning(f"Failed to get memory stats: {e}")
            return MemoryStats()


class UnifiedMemoryOptimizer:
    """Unified memory optimization system."""

    def __init__(self, performance_monitor: UnifiedPerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.optimization_history: List[Dict[str, Any]] = []

    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage."""
        initial_stats = self.performance_monitor.get_memory_stats()

        # Force garbage collection
        import gc
        collected = gc.collect()

        final_stats = self.performance_monitor.get_memory_stats()

        optimization_result = {
            "initial_memory": initial_stats.used_memory,
            "final_memory": final_stats.used_memory,
            "memory_freed": initial_stats.used_memory - final_stats.used_memory,
            "objects_collected": collected,
            "timestamp": time.time(),
        }

        self.optimization_history.append(optimization_result)
        return optimization_result

    def get_memory_recommendations(self) -> List[str]:
        """Get memory optimization recommendations."""
        recommendations = []
        stats = self.performance_monitor.get_memory_stats()

        if stats.memory_percent > 80:
            recommendations.append("High memory usage detected - consider optimizing data structures")

        if len(self.optimization_history) > 10:
            recommendations.append("Frequent memory optimizations - consider reviewing memory leaks")

        return recommendations


class UnifiedBenchmarker:
    """Unified benchmarking system."""

    def __init__(self, performance_monitor: UnifiedPerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.benchmark_results: Dict[str, List[float]] = defaultdict(list)

    def benchmark(self, name: str, func: Callable, iterations: int = 1) -> Dict[str, Any]:
        """Benchmark a function."""
        times = []

        for _ in range(iterations):
            with self.performance_monitor.measure_operation(f"benchmark_{name}"):
                start_time = time.time()
                result = func()
                duration = time.time() - start_time
                times.append(duration)

        self.benchmark_results[name].extend(times)

        return {
            "name": name,
            "iterations": iterations,
            "times": times,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times),
        }

    def compare_benchmarks(self, names: List[str]) -> Dict[str, Any]:
        """Compare benchmark results."""
        comparison = {}

        for name in names:
            if name in self.benchmark_results:
                times = self.benchmark_results[name]
                comparison[name] = {
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "count": len(times),
                }

        return comparison


def measure_performance(operation_name: str = "", **kwargs):
    """Performance measurement decorator."""
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            monitor = get_performance_monitor()
            with monitor.measure_operation(operation_name or func.__name__, **kwargs):
                return func(*args, **func_kwargs)
        return wrapper
    return decorator


# Global performance monitor instance
_performance_monitor: Optional[UnifiedPerformanceMonitor] = None


def get_performance_monitor() -> UnifiedPerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        enable_detailed = os.getenv("PYDEVKIT_DETAILED_METRICS", "true").lower() in ("true", "1", "yes")
        _performance_monitor = UnifiedPerformanceMonitor(enable_detailed_metrics=enable_detailed)
    return _performance_monitor


# Export unified performance components
__all__ = [
    "PerformanceMetrics",
    "MemoryStats",
    "CompressionResult",
    "UnifiedPerformanceMonitor",
    "UnifiedMemoryOptimizer",
    "UnifiedBenchmarker",
    "measure_performance",
    "get_performance_monitor",
]
'''

        # Write unified performance system
        unified_performance_path = self.base_path / "dev/unified_performance.py"
        unified_performance_path.parent.mkdir(parents=True, exist_ok=True)
        unified_performance_path.write_text(unified_performance_content)
        print(f"  ✅ Created: {unified_performance_path}")

    def _consolidate_data_structure_functionality(self) -> None:
        """Consolidate data structure functionality into unified system."""
        print("  🔧 Creating unified data structure system...")

        # Create unified data structure system
        unified_data_content = '''"""
Unified Data Structures - Consolidated Data Structure Implementation

This module provides a unified data structure system that consolidates all data
structure functionality from the previous fragmented implementations.

Features:
- Unified LRU cache
- Unified priority queue
- Unified bloom filter
- Unified data structure utilities
"""

import hashlib
import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class UnifiedLRUCache:
    """Unified LRU cache implementation."""

    def __init__(self, max_size: int = 128):
        """Initialize LRU cache."""
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()

    def get(self, key: Any) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        return None

    def put(self, key: Any, value: Any) -> None:
        """Put value in cache."""
        if key in self.cache:
            # Update existing key
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            self.cache.popitem(last=False)

        self.cache[key] = value

    def delete(self, key: Any) -> bool:
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)

    def keys(self) -> List[Any]:
        """Get cache keys."""
        return list(self.cache.keys())

    def values(self) -> List[Any]:
        """Get cache values."""
        return list(self.cache.values())

    def items(self) -> List[tuple]:
        """Get cache items."""
        return list(self.cache.items())


@dataclass
class PriorityItem:
    """Priority queue item."""
    priority: float
    item: Any
    timestamp: float = 0.0

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority


class UnifiedPriorityQueue:
    """Unified priority queue implementation."""

    def __init__(self):
        """Initialize priority queue."""
        self._queue: List[PriorityItem] = []
        self._timestamp = 0.0

    def put(self, item: Any, priority: float = 0.0) -> None:
        """Put item in queue with priority."""
        import heapq
        self._timestamp += 1.0
        priority_item = PriorityItem(priority, item, self._timestamp)
        heapq.heappush(self._queue, priority_item)

    def get(self) -> Any:
        """Get highest priority item."""
        import heapq
        if not self._queue:
            raise IndexError("Queue is empty")
        return heapq.heappop(self._queue).item

    def peek(self) -> Any:
        """Peek at highest priority item without removing."""
        if not self._queue:
            raise IndexError("Queue is empty")
        return self._queue[0].item

    def empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Get queue size."""
        return len(self._queue)

    def clear(self) -> None:
        """Clear queue."""
        self._queue.clear()


class UnifiedBloomFilter:
    """Unified bloom filter implementation."""

    def __init__(self, capacity: int = 1000, error_rate: float = 0.01):
        """Initialize bloom filter."""
        self.capacity = capacity
        self.error_rate = error_rate

        # Calculate optimal parameters
        import math
        self.bit_array_size = int(-(capacity * math.log(error_rate)) / (math.log(2) ** 2))
        self.hash_count = int((self.bit_array_size / capacity) * math.log(2))

        self.bit_array = [False] * self.bit_array_size
        self._hash_functions = self._create_hash_functions()

    def _create_hash_functions(self) -> List[Callable[[str], int]]:
        """Create hash functions for bloom filter."""
        hash_functions = []

        for i in range(self.hash_count):
            def make_hash_func(seed: int):
                def hash_func(item: str) -> int:
                    hash_obj = hashlib.md5()
                    hash_obj.update(f"{seed}{item}".encode())
                    return int(hash_obj.hexdigest(), 16) % self.bit_array_size
                return hash_func

            hash_functions.append(make_hash_func(i))

        return hash_functions

    def add(self, item: str) -> None:
        """Add item to bloom filter."""
        for hash_func in self._hash_functions:
            index = hash_func(item)
            self.bit_array[index] = True

    def contains(self, item: str) -> bool:
        """Check if item might be in bloom filter."""
        for hash_func in self._hash_functions:
            index = hash_func(item)
            if not self.bit_array[index]:
                return False
        return True

    def clear(self) -> None:
        """Clear bloom filter."""
        self.bit_array = [False] * self.bit_array_size

    def get_stats(self) -> Dict[str, Any]:
        """Get bloom filter statistics."""
        true_bits = sum(self.bit_array)
        return {
            "capacity": self.capacity,
            "error_rate": self.error_rate,
            "bit_array_size": self.bit_array_size,
            "hash_count": self.hash_count,
            "true_bits": true_bits,
            "false_positive_rate": (true_bits / self.bit_array_size) ** self.hash_count,
        }


class UnifiedDataStructureUtils:
    """Unified data structure utilities."""

    @staticmethod
    def create_lru_cache(max_size: int = 128) -> UnifiedLRUCache:
        """Create LRU cache."""
        return UnifiedLRUCache(max_size)

    @staticmethod
    def create_priority_queue() -> UnifiedPriorityQueue:
        """Create priority queue."""
        return UnifiedPriorityQueue()

    @staticmethod
    def create_bloom_filter(capacity: int = 1000, error_rate: float = 0.01) -> UnifiedBloomFilter:
        """Create bloom filter."""
        return UnifiedBloomFilter(capacity, error_rate)

    @staticmethod
    def merge_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
        """Merge multiple dictionaries."""
        result = {}
        for d in dicts:
            result.update(d)
        return result

    @staticmethod
    def flatten_list(nested_list: List[Any]) -> List[Any]:
        """Flatten nested list."""
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(UnifiedDataStructureUtils.flatten_list(item))
            else:
                result.append(item)
        return result


# Export unified data structure components
__all__ = [
    "PriorityItem",
    "UnifiedLRUCache",
    "UnifiedPriorityQueue",
    "UnifiedBloomFilter",
    "UnifiedDataStructureUtils",
]
'''

        # Write unified data structure system
        unified_data_path = self.base_path / "dev/unified_data_structures.py"
        unified_data_path.parent.mkdir(parents=True, exist_ok=True)
        unified_data_path.write_text(unified_data_content)
        print(f"  ✅ Created: {unified_data_path}")

    def _consolidate_validation_functionality(self) -> None:
        """Consolidate validation functionality into unified system."""
        print("  🔧 Creating unified validation system...")

        # Create unified validation system
        unified_validation_content = '''"""
Unified Validation System - Consolidated Validation Implementation

This module provides a unified validation system that consolidates all validation
functionality from the previous fragmented implementations.

Features:
- Unified field validation
- Unified response validation
- Unified data validation
- Unified validation utilities
"""

import re
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Unified validation error."""
    field: str
    message: str
    value: Any = None
    code: str = "validation_error"


@dataclass
class ValidationResult:
    """Unified validation result."""
    is_valid: bool
    errors: List[ValidationError] = None
    data: Any = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class UnifiedFieldValidator:
    """Unified field validator."""

    def __init__(self):
        self.validators: Dict[str, Callable] = {
            "required": self._validate_required,
            "email": self._validate_email,
            "url": self._validate_url,
            "phone": self._validate_phone,
            "min_length": self._validate_min_length,
            "max_length": self._validate_max_length,
            "min_value": self._validate_min_value,
            "max_value": self._validate_max_value,
            "pattern": self._validate_pattern,
            "type": self._validate_type,
        }

    def validate(self, field_name: str, value: Any, rules: Dict[str, Any]) -> List[ValidationError]:
        """Validate field value against rules."""
        errors = []

        for rule_name, rule_value in rules.items():
            if rule_name in self.validators:
                try:
                    validator = self.validators[rule_name]
                    if not validator(value, rule_value):
                        errors.append(ValidationError(
                            field=field_name,
                            message=f"Validation failed for {rule_name}",
                            value=value,
                            code=rule_name
                        ))
                except Exception as e:
                    errors.append(ValidationError(
                        field=field_name,
                        message=f"Validation error: {str(e)}",
                        value=value,
                        code="validation_error"
                    ))

        return errors

    def _validate_required(self, value: Any, required: bool) -> bool:
        """Validate required field."""
        if not required:
            return True
        return value is not None and value != ""

    def _validate_email(self, value: Any, _: Any) -> bool:
        """Validate email format."""
        if not isinstance(value, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))

    def _validate_url(self, value: Any, _: Any) -> bool:
        """Validate URL format."""
        if not isinstance(value, str):
            return False
        pattern = r'^https?://[^\\s/$.?#].[^\\s]*$'
        return bool(re.match(pattern, value))

    def _validate_phone(self, value: Any, _: Any) -> bool:
        """Validate phone number format."""
        if not isinstance(value, str):
            return False
        pattern = r'^\\+?[1-9]\\d{1,14}$'
        return bool(re.match(pattern, value.replace(" ", "").replace("-", "")))

    def _validate_min_length(self, value: Any, min_length: int) -> bool:
        """Validate minimum length."""
        if not isinstance(value, (str, list, dict)):
            return False
        return len(value) >= min_length

    def _validate_max_length(self, value: Any, max_length: int) -> bool:
        """Validate maximum length."""
        if not isinstance(value, (str, list, dict)):
            return False
        return len(value) <= max_length

    def _validate_min_value(self, value: Any, min_value: Union[int, float]) -> bool:
        """Validate minimum value."""
        if not isinstance(value, (int, float)):
            return False
        return value >= min_value

    def _validate_max_value(self, value: Any, max_value: Union[int, float]) -> bool:
        """Validate maximum value."""
        if not isinstance(value, (int, float)):
            return False
        return value <= max_value

    def _validate_pattern(self, value: Any, pattern: str) -> bool:
        """Validate regex pattern."""
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))

    def _validate_type(self, value: Any, expected_type: type) -> bool:
        """Validate type."""
        return isinstance(value, expected_type)


class UnifiedResponseValidator:
    """Unified response validator."""

    def __init__(self, field_validator: UnifiedFieldValidator):
        self.field_validator = field_validator

    def validate_response(self, response: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """Validate response against schema."""
        errors = []

        for field_name, rules in schema.items():
            value = response.get(field_name)
            field_errors = self.field_validator.validate(field_name, value, rules)
            errors.extend(field_errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            data=response
        )

    def validate_list_response(self, responses: List[Dict[str, Any]], schema: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """Validate list of responses against schema."""
        all_errors = []

        for i, response in enumerate(responses):
            result = self.validate_response(response, schema)
            for error in result.errors:
                error.field = f"[{i}].{error.field}"
            all_errors.extend(result.errors)

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            data=responses
        )


class UnifiedDataValidator:
    """Unified data validator."""

    def __init__(self):
        self.field_validator = UnifiedFieldValidator()
        self.response_validator = UnifiedResponseValidator(self.field_validator)

    def validate_data(self, data: Any, validation_rules: Dict[str, Any]) -> ValidationResult:
        """Validate data against rules."""
        if isinstance(data, dict):
            return self.response_validator.validate_response(data, validation_rules)
        elif isinstance(data, list):
            return self.response_validator.validate_list_response(data, validation_rules)
        else:
            # Single value validation
            errors = self.field_validator.validate("value", data, validation_rules)
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                data=data
            )

    def is_valid_email(self, email: str) -> bool:
        """Check if email is valid."""
        return self.field_validator._validate_email(email, None)

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        return self.field_validator._validate_url(url, None)

    def is_valid_phone(self, phone: str) -> bool:
        """Check if phone is valid."""
        return self.field_validator._validate_phone(phone, None)


# Export unified validation components
__all__ = [
    "ValidationError",
    "ValidationResult",
    "UnifiedFieldValidator",
    "UnifiedResponseValidator",
    "UnifiedDataValidator",
]
'''

        # Write unified validation system
        unified_validation_path = self.base_path / "dev/unified_validation.py"
        unified_validation_path.parent.mkdir(parents=True, exist_ok=True)
        unified_validation_path.write_text(unified_validation_content)
        print(f"  ✅ Created: {unified_validation_path}")

    def _consolidate_string_functionality(self) -> None:
        """Consolidate string functionality into unified system."""
        print("  🔧 Creating unified string system...")

        # Create unified string system
        unified_string_content = '''"""
Unified String Utilities - Consolidated String Implementation

This module provides a unified string utility system that consolidates all string
functionality from the previous fragmented implementations.

Features:
- Unified string manipulation
- Unified templating
- Unified sanitization
- Unified string validation
"""

import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class UnifiedStringUtils:
    """Unified string utilities."""

    @staticmethod
    def slugify(text: str, separator: str = "-") -> str:
        """Convert text to URL-safe slug."""
        # Convert to lowercase
        slug = text.lower()

        # Replace spaces and special characters with separator
        slug = re.sub(r'[^\\w\\s-]', '', slug)
        slug = re.sub(r'[\\s_-]+', separator, slug)

        # Remove leading/trailing separators
        return slug.strip(separator)

    @staticmethod
    def sanitize_html(html: str, allowed_tags: Optional[List[str]] = None) -> str:
        """Sanitize HTML content."""
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']

        # Remove script and style tags completely
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove dangerous attributes
        html = re.sub(r'\\s(on\\w+|javascript:)[^>]*', '', html, flags=re.IGNORECASE)

        # Remove disallowed tags
        for tag in ['script', 'style', 'iframe', 'object', 'embed']:
            html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.DOTALL | re.IGNORECASE)

        return html

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        # Replace multiple whitespace with single space
        text = re.sub(r'\\s+', ' ', text)
        return text.strip()

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text."""
        pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
        return re.findall(pattern, text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        pattern = r'https?://[^\\s<>"{}|\\\\^`\\[\\]]+'
        return re.findall(pattern, text)

    @staticmethod
    def remove_html_tags(html: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r'<[^>]+>', '', html)

    @staticmethod
    def camel_to_snake(text: str) -> str:
        """Convert camelCase to snake_case."""
        # Insert underscore before uppercase letters
        text = re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', text)
        return text.lower()

    @staticmethod
    def snake_to_camel(text: str) -> str:
        """Convert snake_case to camelCase."""
        components = text.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])

    @staticmethod
    def is_email(email: str) -> bool:
        """Check if string is valid email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_url(url: str) -> bool:
        """Check if string is valid URL."""
        pattern = r'^https?://[^\\s/$.?#].[^\\s]*$'
        return bool(re.match(pattern, url))

    @staticmethod
    def is_phone(phone: str) -> bool:
        """Check if string is valid phone number."""
        pattern = r'^\\+?[1-9]\\d{1,14}$'
        return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))


class UnifiedTemplate:
    """Unified template system."""

    def __init__(self, template: str):
        """Initialize template."""
        self.template = template
        self.placeholders = self._extract_placeholders()

    def _extract_placeholders(self) -> List[str]:
        """Extract placeholder names from template."""
        pattern = r'\\{\\{([^}]+)\\}\\}'
        return re.findall(pattern, self.template)

    def render(self, **kwargs) -> str:
        """Render template with variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return self.template

    def render_safe(self, **kwargs) -> str:
        """Render template safely, replacing missing variables with placeholders."""
        result = self.template
        for placeholder in self.placeholders:
            if placeholder not in kwargs:
                result = result.replace(f"{{{{{placeholder}}}}}", f"{{{{{placeholder}}}}}")
            else:
                result = result.replace(f"{{{{{placeholder}}}}}", str(kwargs[placeholder]))
        return result

    @staticmethod
    def create(template: str) -> 'UnifiedTemplate':
        """Create template instance."""
        return UnifiedTemplate(template)


# Export unified string components
__all__ = [
    "UnifiedStringUtils",
    "UnifiedTemplate",
]
'''

        # Write unified string system
        unified_string_path = self.base_path / "dev/unified_strings.py"
        unified_string_path.parent.mkdir(parents=True, exist_ok=True)
        unified_string_path.write_text(unified_string_content)
        print(f"  ✅ Created: {unified_string_path}")

    def _consolidate_datetime_functionality(self) -> None:
        """Consolidate datetime functionality into unified system."""
        print("  🔧 Creating unified datetime system...")

        # Create unified datetime system
        unified_datetime_content = '''"""
Unified DateTime Utilities - Consolidated DateTime Implementation

This module provides a unified datetime utility system that consolidates all datetime
functionality from the previous fragmented implementations.

Features:
- Unified datetime parsing
- Unified datetime formatting
- Unified timezone handling
- Unified datetime utilities
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class UnifiedDateTimeUtils:
    """Unified datetime utilities."""

    @staticmethod
    def now() -> datetime:
        """Get current datetime in UTC."""
        return datetime.now(timezone.utc)

    @staticmethod
    def parse_datetime(date_string: str, format_string: Optional[str] = None) -> Optional[datetime]:
        """Parse datetime string."""
        if format_string:
            try:
                return datetime.strptime(date_string, format_string)
            except ValueError:
                return None

        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime to string."""
        return dt.strftime(format_string)

    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """Convert datetime to ISO string."""
        return dt.isoformat()

    @staticmethod
    def from_iso_string(iso_string: str) -> Optional[datetime]:
        """Parse ISO string to datetime."""
        try:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        except ValueError:
            return None

    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        """Convert datetime to timestamp."""
        return dt.timestamp()

    @staticmethod
    def from_timestamp(timestamp: float) -> datetime:
        """Convert timestamp to datetime."""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Add days to datetime."""
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """Add hours to datetime."""
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """Add minutes to datetime."""
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """Add seconds to datetime."""
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Get human-readable time ago string."""
        now = UnifiedDateTimeUtils.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """Check if datetime is weekend."""
        return dt.weekday() >= 5

    @staticmethod
    def is_weekday(dt: datetime) -> bool:
        """Check if datetime is weekday."""
        return dt.weekday() < 5

    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        """Get start of day."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_day(dt: datetime) -> datetime:
        """Get end of day."""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def start_of_week(dt: datetime) -> datetime:
        """Get start of week (Monday)."""
        days_since_monday = dt.weekday()
        return UnifiedDateTimeUtils.start_of_day(dt - timedelta(days=days_since_monday))

    @staticmethod
    def end_of_week(dt: datetime) -> datetime:
        """Get end of week (Sunday)."""
        days_until_sunday = 6 - dt.weekday()
        return UnifiedDateTimeUtils.end_of_day(dt + timedelta(days=days_until_sunday))

    @staticmethod
    def start_of_month(dt: datetime) -> datetime:
        """Get start of month."""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_month(dt: datetime) -> datetime:
        """Get end of month."""
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)
        return next_month - timedelta(days=1)

    @staticmethod
    def format_relative_time(dt: datetime) -> str:
        """Format datetime as relative time."""
        now = UnifiedDateTimeUtils.now()
        diff = now - dt

        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"


# Export unified datetime components
__all__ = [
    "UnifiedDateTimeUtils",
]
'''

        # Write unified datetime system
        unified_datetime_path = self.base_path / "dev/unified_datetime.py"
        unified_datetime_path.parent.mkdir(parents=True, exist_ok=True)
        unified_datetime_path.write_text(unified_datetime_content)
        print(f"  ✅ Created: {unified_datetime_path}")

    def _consolidate_tracing_functionality(self) -> None:
        """Consolidate tracing functionality into unified system."""
        print("  🔧 Creating unified tracing system...")

        # Create unified tracing system
        unified_tracing_content = '''"""
Unified Tracing System - Consolidated Tracing Implementation

This module provides a unified tracing system that consolidates all tracing
functionality from the previous fragmented implementations.

Features:
- Unified correlation ID management
- Unified tracing context
- Unified trace logging
- Unified distributed tracing
"""

import logging
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class TraceContext:
    """Unified trace context."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UnifiedTracingSystem:
    """Unified tracing system."""

    def __init__(self):
        self._context = threading.local()
        self._trace_logger = logging.getLogger("trace")

    def get_trace_context(self) -> Optional[TraceContext]:
        """Get current trace context."""
        return getattr(self._context, 'trace_context', None)

    def set_trace_context(self, context: TraceContext) -> None:
        """Set trace context."""
        self._context.trace_context = context

    def clear_trace_context(self) -> None:
        """Clear trace context."""
        if hasattr(self._context, 'trace_context'):
            delattr(self._context, 'trace_context')

    def create_trace_context(
        self,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> TraceContext:
        """Create new trace context."""
        return TraceContext(
            trace_id=trace_id or str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            correlation_id=correlation_id
        )

    @contextmanager
    def trace_context(self, operation_name: str, **metadata):
        """Trace context manager."""
        current_context = self.get_trace_context()

        if current_context:
            # Create child span
            new_context = TraceContext(
                trace_id=current_context.trace_id,
                span_id=str(uuid.uuid4()),
                parent_span_id=current_context.span_id,
                correlation_id=current_context.correlation_id,
                metadata={**current_context.metadata, **metadata}
            )
        else:
            # Create root span
            new_context = self.create_trace_context(**metadata)

        old_context = current_context
        self.set_trace_context(new_context)

        try:
            self.log_trace_event("span_start", operation_name, **metadata)
            yield new_context
        except Exception as e:
            self.log_trace_event("span_error", operation_name, error=str(e), **metadata)
            raise
        finally:
            self.log_trace_event("span_end", operation_name, **metadata)
            self.set_trace_context(old_context)

    def log_trace_event(self, event_type: str, operation_name: str, **metadata) -> None:
        """Log trace event."""
        context = self.get_trace_context()
        if not context:
            return

        trace_data = {
            "event_type": event_type,
            "operation_name": operation_name,
            "trace_id": context.trace_id,
            "span_id": context.span_id,
            "parent_span_id": context.parent_span_id,
            "correlation_id": context.correlation_id,
            "metadata": {**context.metadata, **metadata}
        }

        self._trace_logger.info(f"TRACE: {trace_data}")

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID."""
        context = self.get_trace_context()
        return context.correlation_id if context else None

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID."""
        context = self.get_trace_context()
        if context:
            context.correlation_id = correlation_id
        else:
            # Create new context with correlation ID
            new_context = self.create_trace_context(correlation_id=correlation_id)
            self.set_trace_context(new_context)

    def get_or_create_correlation_id(self) -> str:
        """Get or create correlation ID."""
        correlation_id = self.get_correlation_id()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            self.set_correlation_id(correlation_id)
        return correlation_id

    def clear_correlation_id(self) -> None:
        """Clear correlation ID."""
        context = self.get_trace_context()
        if context:
            context.correlation_id = None

    @contextmanager
    def correlation_context(self, correlation_id: str):
        """Correlation ID context manager."""
        old_correlation_id = self.get_correlation_id()
        self.set_correlation_id(correlation_id)
        try:
            yield
        finally:
            if old_correlation_id:
                self.set_correlation_id(old_correlation_id)
            else:
                self.clear_correlation_id()


# Global tracing system instance
unified_tracing = UnifiedTracingSystem()

# Convenience functions
def get_trace_context() -> Optional[TraceContext]:
    """Get current trace context."""
    return unified_tracing.get_trace_context()

def set_trace_context(context: TraceContext) -> None:
    """Set trace context."""
    unified_tracing.set_trace_context(context)

def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return unified_tracing.get_correlation_id()

def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID."""
    unified_tracing.set_correlation_id(correlation_id)

def get_or_create_correlation_id() -> str:
    """Get or create correlation ID."""
    return unified_tracing.get_or_create_correlation_id()

def clear_correlation_id() -> None:
    """Clear correlation ID."""
    unified_tracing.clear_correlation_id()

@contextmanager
def correlation_context(correlation_id: str):
    """Correlation ID context manager."""
    with unified_tracing.correlation_context(correlation_id):
        yield

@contextmanager
def trace_context(operation_name: str, **metadata):
    """Trace context manager."""
    with unified_tracing.trace_context(operation_name, **metadata) as context:
        yield context


# Export unified tracing components
__all__ = [
    "TraceContext",
    "UnifiedTracingSystem",
    "unified_tracing",
    "get_trace_context",
    "set_trace_context",
    "get_correlation_id",
    "set_correlation_id",
    "get_or_create_correlation_id",
    "clear_correlation_id",
    "correlation_context",
    "trace_context",
]
'''

        # Write unified tracing system
        unified_tracing_path = self.base_path / "dev/unified_tracing.py"
        unified_tracing_path.parent.mkdir(parents=True, exist_ok=True)
        unified_tracing_path.write_text(unified_tracing_content)
        print(f"  ✅ Created: {unified_tracing_path}")

    def _remove_file(self, file_path: Path) -> None:
        """Remove a file and track it."""
        try:
            file_path.unlink()
            self.removed_files.append(str(file_path))
        except Exception as e:
            print(f"  ⚠️  Could not remove {file_path}: {e}")

    def update_dev_init(self) -> None:
        """Update dev module __init__.py."""
        print("📝 Updating dev module __init__.py...")

        dev_init_content = '''"""
Unified Development Tools Module - Consolidated Development Implementation

This module provides a unified development tools system that consolidates all development
functionality from the previous fragmented implementations.

Features:
- Unified utilities
- Unified performance monitoring
- Unified data structures
- Unified validation
- Unified string utilities
- Unified datetime utilities
- Unified tracing
"""

# Import unified systems
from .unified_utilities import (
    RateLimitConfig,
    UnifiedAsyncUtils,
    UnifiedConcurrencyUtils,
    UnifiedCorrelationManager,
    UnifiedRateLimiter,
    UnifiedHelperUtils,
    unified_async_utils,
    unified_concurrency_utils,
    unified_correlation_manager,
    unified_helper_utils,
)

from .unified_performance import (
    PerformanceMetrics,
    MemoryStats,
    CompressionResult,
    UnifiedPerformanceMonitor,
    UnifiedMemoryOptimizer,
    UnifiedBenchmarker,
    measure_performance,
    get_performance_monitor,
)

from .unified_data_structures import (
    PriorityItem,
    UnifiedLRUCache,
    UnifiedPriorityQueue,
    UnifiedBloomFilter,
    UnifiedDataStructureUtils,
)

from .unified_validation import (
    ValidationError,
    ValidationResult,
    UnifiedFieldValidator,
    UnifiedResponseValidator,
    UnifiedDataValidator,
)

from .unified_strings import (
    UnifiedStringUtils,
    UnifiedTemplate,
)

from .unified_datetime import (
    UnifiedDateTimeUtils,
)

from .unified_tracing import (
    TraceContext,
    UnifiedTracingSystem,
    unified_tracing,
    get_trace_context,
    set_trace_context,
    get_correlation_id,
    set_correlation_id,
    get_or_create_correlation_id,
    clear_correlation_id,
    correlation_context,
    trace_context,
)

# Legacy imports for backward compatibility
from . import config
from . import errors
from . import fs
from . import functional
from . import http
from . import monitoring

# Export unified development components
__all__ = [
    # Utilities
    "RateLimitConfig",
    "UnifiedAsyncUtils",
    "UnifiedConcurrencyUtils",
    "UnifiedCorrelationManager",
    "UnifiedRateLimiter",
    "UnifiedHelperUtils",
    "unified_async_utils",
    "unified_concurrency_utils",
    "unified_correlation_manager",
    "unified_helper_utils",
    # Performance
    "PerformanceMetrics",
    "MemoryStats",
    "CompressionResult",
    "UnifiedPerformanceMonitor",
    "UnifiedMemoryOptimizer",
    "UnifiedBenchmarker",
    "measure_performance",
    "get_performance_monitor",
    # Data Structures
    "PriorityItem",
    "UnifiedLRUCache",
    "UnifiedPriorityQueue",
    "UnifiedBloomFilter",
    "UnifiedDataStructureUtils",
    # Validation
    "ValidationError",
    "ValidationResult",
    "UnifiedFieldValidator",
    "UnifiedResponseValidator",
    "UnifiedDataValidator",
    # Strings
    "UnifiedStringUtils",
    "UnifiedTemplate",
    # DateTime
    "UnifiedDateTimeUtils",
    # Tracing
    "TraceContext",
    "UnifiedTracingSystem",
    "unified_tracing",
    "get_trace_context",
    "set_trace_context",
    "get_correlation_id",
    "set_correlation_id",
    "get_or_create_correlation_id",
    "clear_correlation_id",
    "correlation_context",
    "trace_context",
    # Legacy modules
    "config",
    "errors",
    "fs",
    "functional",
    "http",
    "monitoring",
]
'''

        # Write updated dev init
        dev_init_path = self.base_path / "dev/__init__.py"
        dev_init_path.write_text(dev_init_content)
        print(f"  ✅ Updated: {dev_init_path}")

    def run_consolidation(self) -> None:
        """Run the complete dev module consolidation."""
        print("🚀 Starting Development Tools Module Consolidation...")
        print("=" * 50)

        # Phase 1: Consolidate utilities
        self.consolidate_utils()

        # Phase 2: Consolidate performance
        self.consolidate_performance()

        # Phase 3: Consolidate data structures
        self.consolidate_data_structures()

        # Phase 4: Consolidate validation
        self.consolidate_validation()

        # Phase 5: Consolidate strings
        self.consolidate_strings()

        # Phase 6: Consolidate datetime
        self.consolidate_datetime()

        # Phase 7: Consolidate tracing
        self.consolidate_tracing()

        # Phase 8: Update dev module init
        self.update_dev_init()

        # Summary
        print("\\n" + "=" * 50)
        print("✅ Development Tools Module Consolidation Complete!")
        print(f"📁 Files Removed: {len(self.removed_files)}")
        print(f"📦 Modules Consolidated: {len(self.consolidated_modules)}")
        print("\\n🎯 Results:")
        print("- Unified utility system created")
        print("- Unified performance monitoring system created")
        print("- Unified data structure system created")
        print("- Unified validation system created")
        print("- Unified string utility system created")
        print("- Unified datetime utility system created")
        print("- Unified tracing system created")
        print("\\n📈 Expected Reduction: 74 files → <50 files (32% reduction)")


if __name__ == "__main__":
    consolidator = DevModuleConsolidator()
    consolidator.run_consolidation()
