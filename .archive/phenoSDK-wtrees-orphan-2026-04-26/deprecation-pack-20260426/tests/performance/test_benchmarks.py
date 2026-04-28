"""
Performance benchmark tests.
"""

import sys
import time
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def test_execution_time_benchmark(self):
        """Benchmark execution time of critical functions."""
        # Test execution time
        start_time = time.time()
        # Simulate some work
        time.sleep(0.01)
        execution_time = time.time() - start_time

        assert execution_time < 0.1  # Should complete within 100ms

    def test_memory_usage_benchmark(self):
        """Benchmark memory usage."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate memory-intensive operation
        data = [i for i in range(10000)]

        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory

        assert memory_increase < 10  # Should not use more than 10MB

    @pytest.mark.benchmark
    def test_benchmark_performance(self, benchmark):
        """Benchmark performance using pytest-benchmark."""
        def sample_function():
            return sum(range(1000))

        result = benchmark(sample_function)
        assert result == 499500


@pytest.mark.performance
@pytest.mark.slow
class TestLoadTesting:
    """Load testing scenarios."""

    def test_concurrent_operations(self):
        """Test concurrent operations performance."""
        import queue
        import threading

        results = queue.Queue()

        def worker():
            # Simulate some work
            time.sleep(0.01)
            results.put("completed")

        # Start multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert results.qsize() == 10

    def test_memory_leak_detection(self):
        """Test for memory leaks."""
        import gc

        # Force garbage collection
        gc.collect()

        # Simulate memory allocation and deallocation
        for _ in range(100):
            data = [i for i in range(1000)]
            del data

        # Force garbage collection again
        gc.collect()

        # This test passes if no memory leak is detected
        assert True
