"""
Performance testing plugin for pytest.

This plugin provides performance testing capabilities including:
- Benchmark testing
- Memory profiling
- Performance regression detection
- Load testing utilities
"""

import threading
import time
from collections.abc import Callable
from contextlib import contextmanager

import psutil
import pytest


class PerformancePlugin:
    """Pytest plugin for performance testing."""

    def __init__(self, config):
        self.config = config
        self.benchmark_threshold = config.getoption("--benchmark-threshold", default=1.0)
        self.memory_threshold = config.getoption("--memory-threshold", default=100)  # MB
        self.performance_data = {}

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_setup(self, item):
        """Setup performance monitoring for each test."""
        if hasattr(item, "get_closest_marker") and item.get_closest_marker("performance"):
            self.performance_data[item.nodeid] = {
                "start_time": time.time(),
                "start_memory": psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                "peak_memory": 0,
            }

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_teardown(self, item):
        """Teardown performance monitoring for each test."""
        if item.nodeid in self.performance_data:
            data = self.performance_data[item.nodeid]
            data["end_time"] = time.time()
            data["duration"] = data["end_time"] - data["start_time"]
            data["end_memory"] = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            data["memory_delta"] = data["end_memory"] - data["start_memory"]

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_call(self, item):
        """Monitor performance during test execution."""
        if item.nodeid in self.performance_data:
            # Monitor memory usage during test execution
            def monitor_memory():
                while item.nodeid in self.performance_data:
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    self.performance_data[item.nodeid]["peak_memory"] = max(self.performance_data[item.nodeid]["peak_memory"], current_memory)
                    time.sleep(0.1)

            monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
            monitor_thread.start()

    def pytest_collection_modifyitems(self, config, items):
        """Add performance validation tests."""
        performance_items = []

        # Add benchmark validation
        performance_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_benchmark_performance",
                callobj=self._test_benchmark_performance,
                markers=[pytest.mark.performance, pytest.mark.benchmark],
            ),
        )

        # Add memory usage validation
        performance_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_memory_usage",
                callobj=self._test_memory_usage,
                markers=[pytest.mark.performance, pytest.mark.memory],
            ),
        )

        items.extend(performance_items)

    def _test_benchmark_performance(self):
        """Test that benchmark performance meets thresholds."""
        violations = []

        for test_id, data in self.performance_data.items():
            if "duration" in data and data["duration"] > self.benchmark_threshold:
                violations.append(f"{test_id}: {data['duration']:.2f}s (threshold: {self.benchmark_threshold}s)")

        if violations:
            pytest.fail("Benchmark performance violations found:\n" + "\n".join(violations))

    def _test_memory_usage(self):
        """Test that memory usage is within thresholds."""
        violations = []

        for test_id, data in self.performance_data.items():
            if "peak_memory" in data and data["peak_memory"] > self.memory_threshold:
                violations.append(f"{test_id}: {data['peak_memory']:.2f}MB (threshold: {self.memory_threshold}MB)")

        if violations:
            pytest.fail("Memory usage violations found:\n" + "\n".join(violations))


@contextmanager
def performance_monitor(test_name: str, threshold: float = 1.0):
    """Context manager for monitoring performance of code blocks."""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024

    try:
        yield
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        memory_delta = end_memory - start_memory

        if duration > threshold:
            pytest.fail(f"Performance threshold exceeded: {duration:.2f}s > {threshold}s")

        print(f"Performance: {test_name} - Duration: {duration:.2f}s, Memory: {memory_delta:.2f}MB")


def benchmark_test(func: Callable) -> Callable:
    """Decorator for marking functions as benchmark tests."""
    return pytest.mark.performance(func)


def memory_test(func: Callable) -> Callable:
    """Decorator for marking functions as memory tests."""
    return pytest.mark.memory(func)


def load_test(users: int = 10, duration: int = 60) -> Callable:
    """Decorator for marking functions as load tests."""
    return pytest.mark.performance(pytest.mark.parametrize("load_users", [users])(func))


def pytest_addoption(parser):
    """Add command line options for performance testing."""
    parser.addoption(
        "--benchmark-threshold",
        type=float,
        default=1.0,
        help="Maximum allowed execution time for benchmark tests (seconds)",
    )
    parser.addoption(
        "--memory-threshold",
        type=float,
        default=100,
        help="Maximum allowed memory usage (MB)",
    )


def pytest_configure(config):
    """Configure the performance plugin."""
    config.pluginmanager.register(PerformancePlugin(config), "performance")
