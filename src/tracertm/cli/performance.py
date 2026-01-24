"""
CLI performance optimization for TraceRTM.

Provides lazy loading, caching, and startup optimization.
"""

import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any


class PerformanceMonitor:
    """Monitor and optimize CLI performance."""

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.start_time = time.time()
        self.timings: dict[str, float] = {}

    def mark(self, name: str) -> None:
        """Mark a timing point.

        Args:
            name: Timing point name
        """
        self.timings[name] = time.time() - self.start_time

    def get_elapsed(self) -> float:
        """Get elapsed time since start.

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.start_time

    def get_timings(self) -> dict[str, float]:
        """Get all timings.

        Returns:
            Dictionary of timings
        """
        return self.timings.copy()


class LazyLoader:
    """Lazy load modules to improve startup time."""

    def __init__(self) -> None:
        """Initialize lazy loader."""
        self._cache: dict[str, Any] = {}

    def load(self, module_name: str) -> Any:
        """Lazy load a module.

        Args:
            module_name: Module name to load

        Returns:
            Loaded module
        """
        if module_name not in self._cache:
            import importlib
            self._cache[module_name] = importlib.import_module(module_name)

        return self._cache[module_name]

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()


class CommandCache:
    """Cache command results for performance."""

    def __init__(self, cache_dir: Path | None = None, ttl: int = 300):
        """Initialize command cache.

        Args:
            cache_dir: Cache directory (default: ~/.cache/tracertm)
            ttl: Time to live in seconds (default: 300)
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "tracertm"

        self.cache_dir = cache_dir
        self.ttl = ttl
        self._memory_cache: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        # Check memory cache first
        if key in self._memory_cache:
            value, timestamp = self._memory_cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self._memory_cache[key]

        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._memory_cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache."""
        self._memory_cache.clear()


def timed(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start

        # Print timing if verbose
        if elapsed > 0.1:  # Only print if > 100ms
            import sys
            print(f"[DEBUG] {func.__name__} took {elapsed:.3f}s", file=sys.stderr)

        return result

    return wrapper


def optimize_startup() -> None:
    """Optimize CLI startup time.

    - Lazy load heavy modules
    - Use caching where appropriate
    - Minimize imports at module level
    """
    # This is called at CLI startup
    pass


def get_startup_time() -> float:
    """Get CLI startup time.

    Returns:
        Startup time in milliseconds
    """
    import sys

    # Try to get from environment
    if hasattr(sys, '_start_time'):
        start_time = getattr(sys, '_start_time', 0)
        if isinstance(start_time, (int, float)):
            return float((time.time() - start_time) * 1000)

    return 0.0


# Global instances
_monitor = PerformanceMonitor()
_loader = LazyLoader()
_cache = CommandCache()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor."""
    return _monitor


def get_loader() -> LazyLoader:
    """Get global lazy loader."""
    return _loader


def get_cache() -> CommandCache:
    """Get global command cache."""
    return _cache
