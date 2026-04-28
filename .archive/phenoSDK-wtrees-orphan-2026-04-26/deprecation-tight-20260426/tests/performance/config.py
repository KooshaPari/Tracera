"""
Performance testing configuration.
"""

import pytest
from pytest_benchmark.fixture import BenchmarkFixture


@pytest.fixture(scope="session")
def performance_config():
    """Performance testing configuration."""
    return {
        "max_execution_time": 1.0,  # seconds
        "memory_limit_mb": 100,
        "cpu_usage_limit": 80,  # percentage
        "benchmark_rounds": 5,
        "warmup_rounds": 2,
    }


@pytest.fixture
def benchmark_config(benchmark: BenchmarkFixture):
    """Configure benchmark settings."""
    benchmark.min_rounds = 5
    benchmark.warmup = True
    benchmark.warmup_iterations = 2
    return benchmark


class PerformanceTestBase:
    """Base class for performance tests."""

    def assert_performance(self, func, max_time: float, *args, **kwargs):
        """Assert function performance meets requirements."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        assert execution_time < max_time, f"Performance test failed: {execution_time:.3f}s > {max_time}s"
        return result
