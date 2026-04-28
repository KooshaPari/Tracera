"""
Memory profiling utilities for tests.
"""

import os

import psutil


class MemoryProfiler:
    """Memory profiling for tests."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()

    def get_memory_usage(self) -> dict[str, float]:
        """Get current memory usage."""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent(),
        }

    def get_memory_delta(self) -> dict[str, float]:
        """Get memory usage delta since initialization."""
        current = self.get_memory_usage()
        return {
            "rss_delta": current["rss"] - self.initial_memory["rss"],
            "vms_delta": current["vms"] - self.initial_memory["vms"],
            "percent_delta": current["percent"] - self.initial_memory["percent"],
        }

    def assert_memory_usage(self, max_mb: float):
        """Assert memory usage is within limits."""
        current = self.get_memory_usage()
        assert current["rss"] < max_mb, f"Memory usage {current['rss']:.1f}MB exceeds limit {max_mb}MB"


@pytest.fixture
def memory_profiler():
    """Memory profiler fixture."""
    return MemoryProfiler()
