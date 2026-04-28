"""Performance benchmark implementation for pheno-integration.

This module provides comprehensive performance benchmarking tools for validating the
performance of all pheno-sdk libraries.
"""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import psutil


@dataclass
class BenchmarkResult:
    """
    Benchmark result.
    """

    test_name: str
    duration: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    latency: float
    error_rate: float
    iterations: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.
        """
        return {
            "test_name": self.test_name,
            "duration": self.duration,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "throughput": self.throughput,
            "latency": self.latency,
            "error_rate": self.error_rate,
            "iterations": self.iterations,
            "metadata": self.metadata,
        }


@dataclass
class BenchmarkConfig:
    """
    Benchmark configuration.
    """

    iterations: int = 1000
    warmup_iterations: int = 100
    timeout: float = 300.0
    parallel: bool = False
    max_workers: int = 4
    verbose: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """
    Performance benchmark implementation.
    """

    def __init__(self, config: BenchmarkConfig | None = None):
        self.config = config or BenchmarkConfig()
        self._results: list[BenchmarkResult] = []
        self._monitoring = False
        self._monitor_thread = None
        self._monitor_data = []

    def run_performance_tests(self) -> list[BenchmarkResult]:
        """Run comprehensive performance tests.

        Returns:
            List of benchmark results
        """
        results = []

        # Test individual libraries
        library_tests = [
            ("pheno-auth", self._benchmark_auth_library),
            ("pheno-config", self._benchmark_config_library),
            ("pheno-logging", self._benchmark_logging_library),
            ("pheno-errors", self._benchmark_errors_library),
            ("pheno-testing", self._benchmark_testing_library),
            ("pheno-docs", self._benchmark_docs_library),
        ]

        for library_name, test_func in library_tests:
            result = self._run_benchmark(library_name, test_func)
            results.append(result)

        # Test cross-library integration
        integration_result = self._run_benchmark(
            "cross_library_integration", self._benchmark_integration,
        )
        results.append(integration_result)

        # Test overall system performance
        system_result = self._run_benchmark("system_performance", self._benchmark_system)
        results.append(system_result)

        self._results.extend(results)
        return results

    def run_library_benchmark(self, library_name: str, test_func: Callable) -> BenchmarkResult:
        """Run benchmark for a specific library.

        Args:
            library_name: Name of the library
            test_func: Test function to benchmark

        Returns:
            Benchmark result
        """
        return self._run_benchmark(library_name, test_func)

    def run_integration_benchmark(self) -> BenchmarkResult:
        """Run integration benchmark.

        Returns:
            Benchmark result
        """
        return self._run_benchmark("integration", self._benchmark_integration)

    def get_results(self) -> list[BenchmarkResult]:
        """
        Get all benchmark results.
        """
        return self._results

    def get_summary(self) -> dict[str, Any]:
        """
        Get benchmark summary.
        """
        if not self._results:
            return {"total": 0, "average_duration": 0, "average_memory": 0}

        total = len(self._results)
        avg_duration = sum(r.duration for r in self._results) / total
        avg_memory = sum(r.memory_usage for r in self._results) / total
        avg_cpu = sum(r.cpu_usage for r in self._results) / total
        avg_throughput = sum(r.throughput for r in self._results) / total
        avg_latency = sum(r.latency for r in self._results) / total
        avg_error_rate = sum(r.error_rate for r in self._results) / total

        return {
            "total": total,
            "average_duration": avg_duration,
            "average_memory": avg_memory,
            "average_cpu": avg_cpu,
            "average_throughput": avg_throughput,
            "average_latency": avg_latency,
            "average_error_rate": avg_error_rate,
        }

    def _run_benchmark(self, test_name: str, test_func: Callable) -> BenchmarkResult:
        """
        Run a single benchmark.
        """
        time.time()

        # Start monitoring
        self._start_monitoring()

        try:
            # Warmup
            for _ in range(self.config.warmup_iterations):
                test_func()

            # Run benchmark
            benchmark_start = time.time()
            errors = 0

            for _i in range(self.config.iterations):
                try:
                    test_func()
                except Exception:
                    errors += 1

            benchmark_end = time.time()

            # Stop monitoring
            self._stop_monitoring()

            # Calculate metrics
            duration = benchmark_end - benchmark_start
            memory_usage = self._calculate_memory_usage()
            cpu_usage = self._calculate_cpu_usage()
            throughput = self.config.iterations / duration
            latency = duration / self.config.iterations
            error_rate = errors / self.config.iterations

            return BenchmarkResult(
                test_name=test_name,
                duration=duration,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                throughput=throughput,
                latency=latency,
                error_rate=error_rate,
                iterations=self.config.iterations,
                metadata={
                    "warmup_iterations": self.config.warmup_iterations,
                    "errors": errors,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            self._stop_monitoring()
            return BenchmarkResult(
                test_name=test_name,
                duration=0,
                memory_usage=0,
                cpu_usage=0,
                throughput=0,
                latency=0,
                error_rate=1.0,
                iterations=0,
                metadata={"error": str(e)},
            )

    def _start_monitoring(self) -> None:
        """
        Start performance monitoring.
        """
        self._monitoring = True
        self._monitor_data = []
        self._monitor_thread = threading.Thread(target=self._monitor_performance)
        self._monitor_thread.start()

    def _stop_monitoring(self) -> None:
        """
        Stop performance monitoring.
        """
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()

    def _monitor_performance(self) -> None:
        """
        Monitor performance metrics.
        """
        while self._monitoring:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()

                self._monitor_data.append(
                    {
                        "timestamp": time.time(),
                        "memory_rss": memory_info.rss,
                        "memory_vms": memory_info.vms,
                        "cpu_percent": cpu_percent,
                    },
                )

                time.sleep(0.1)  # Monitor every 100ms

            except Exception:
                break

    def _calculate_memory_usage(self) -> float:
        """
        Calculate average memory usage.
        """
        if not self._monitor_data:
            return 0.0

        total_memory = sum(data["memory_rss"] for data in self._monitor_data)
        return total_memory / len(self._monitor_data)

    def _calculate_cpu_usage(self) -> float:
        """
        Calculate average CPU usage.
        """
        if not self._monitor_data:
            return 0.0

        total_cpu = sum(data["cpu_percent"] for data in self._monitor_data)
        return total_cpu / len(self._monitor_data)

    # Library benchmark methods (placeholders)
    def _benchmark_auth_library(self) -> None:
        """
        Benchmark authentication library.
        """
        # This would benchmark actual auth operations
        # For now, simulate some work
        time.sleep(0.001)

    def _benchmark_config_library(self) -> None:
        """
        Benchmark configuration library.
        """
        # This would benchmark actual config operations
        # For now, simulate some work
        time.sleep(0.001)

    def _benchmark_logging_library(self) -> None:
        """
        Benchmark logging library.
        """
        # This would benchmark actual logging operations
        # For now, simulate some work
        time.sleep(0.001)

    def _benchmark_errors_library(self) -> None:
        """
        Benchmark errors library.
        """
        # This would benchmark actual error handling operations
        # For now, simulate some work
        time.sleep(0.001)

    def _benchmark_testing_library(self) -> None:
        """
        Benchmark testing library.
        """
        # This would benchmark actual testing operations
        # For now, simulate some work
        time.sleep(0.001)

    def _benchmark_docs_library(self) -> None:
        """
        Benchmark documentation library.
        """
        # This would benchmark actual documentation operations
        # For now, simulate some work
        time.sleep(0.001)

    def _benchmark_integration(self) -> None:
        """
        Benchmark cross-library integration.
        """
        # This would benchmark actual integration operations
        # For now, simulate some work
        time.sleep(0.002)

    def _benchmark_system(self) -> None:
        """
        Benchmark overall system performance.
        """
        # This would benchmark actual system operations
        # For now, simulate some work
        time.sleep(0.005)
