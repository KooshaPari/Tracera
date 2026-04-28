"""
Performance testing fixtures for pytest.

This module provides fixtures specifically for performance testing.
"""

import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import Mock

import psutil
import pytest


@pytest.fixture
def performance_monitor() -> Generator[dict[str, Any], None, None]:
    """Monitor performance during test execution."""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024

    monitor_data = {
        "start_time": start_time,
        "start_memory": start_memory,
        "peak_memory": start_memory,
        "measurements": [],
        "threads": [],
    }

    def measure(name: str, **kwargs):
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024

        measurement = {
            "name": name,
            "timestamp": current_time,
            "memory": current_memory,
            "duration": current_time - start_time,
            **kwargs,
        }

        monitor_data["measurements"].append(measurement)

        monitor_data["peak_memory"] = max(monitor_data["peak_memory"], current_memory)

        return measurement

    def start_thread_monitoring():
        """Start background thread monitoring."""
        def monitor():
            while True:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                monitor_data["peak_memory"] = max(monitor_data["peak_memory"], current_memory)
                time.sleep(0.1)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        monitor_data["threads"].append(thread)

    monitor_data["measure"] = measure
    monitor_data["start_thread_monitoring"] = start_thread_monitoring

    try:
        yield monitor_data
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        monitor_data["end_time"] = end_time
        monitor_data["end_memory"] = end_memory
        monitor_data["total_duration"] = end_time - start_time
        monitor_data["memory_delta"] = end_memory - start_memory


@pytest.fixture
def benchmark_data() -> Generator[dict[str, Any], None, None]:
    """Provide benchmark data for testing."""
    return {
        "iterations": 1000,
        "warmup_iterations": 100,
        "timeout": 60.0,
        "threshold": 1.0,
        "results": [],
    }


@pytest.fixture
def load_test_data() -> Generator[dict[str, Any], None, None]:
    """Provide load test data for testing."""
    return {
        "users": 10,
        "duration": 60,
        "ramp_up": 10,
        "ramp_down": 10,
        "requests_per_second": 100,
        "concurrent_requests": 50,
    }


@pytest.fixture
def memory_profiler() -> Generator[dict[str, Any], None, None]:
    """Provide memory profiling capabilities."""
    profiler_data = {
        "snapshots": [],
        "baseline": None,
        "current": None,
    }

    def take_snapshot(name: str):
        snapshot = {
            "name": name,
            "timestamp": time.time(),
            "memory": psutil.Process().memory_info().rss / 1024 / 1024,
            "memory_percent": psutil.Process().memory_percent(),
            "cpu_percent": psutil.Process().cpu_percent(),
        }
        profiler_data["snapshots"].append(snapshot)
        profiler_data["current"] = snapshot
        return snapshot

    def set_baseline():
        profiler_data["baseline"] = take_snapshot("baseline")

    def get_memory_delta():
        if profiler_data["baseline"] and profiler_data["current"]:
            return profiler_data["current"]["memory"] - profiler_data["baseline"]["memory"]
        return 0

    profiler_data["take_snapshot"] = take_snapshot
    profiler_data["set_baseline"] = set_baseline
    profiler_data["get_memory_delta"] = get_memory_delta

    yield profiler_data


@pytest.fixture
def performance_thresholds() -> dict[str, float]:
    """Provide performance thresholds for testing."""
    return {
        "max_duration": 1.0,  # seconds
        "max_memory": 100.0,  # MB
        "max_cpu": 80.0,  # percent
        "max_memory_delta": 50.0,  # MB
    }


@pytest.fixture
def mock_performance_client() -> Mock:
    """Create a mock performance client for testing."""
    client = Mock()
    client.benchmark = Mock(return_value={"duration": 0.5, "memory": 50.0})
    client.profile = Mock(return_value={"cpu": 10.0, "memory": 50.0})
    client.load_test = Mock(return_value={"throughput": 100.0, "latency": 0.1})
    return client


@contextmanager
def performance_context(name: str, threshold: float = 1.0):
    """Context manager for performance monitoring."""
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
            pytest.fail(f"Performance threshold exceeded for {name}: {duration:.2f}s > {threshold}s")

        print(f"Performance: {name} - Duration: {duration:.2f}s, Memory: {memory_delta:.2f}MB")


@pytest.fixture
def performance_context_factory():
    """Factory for creating performance contexts."""
    return performance_context
