#!/usr/bin/env python3
"""
Comprehensive Performance Testing Framework
Implements load testing, stress testing, and performance benchmarking.
"""

import argparse
import json
import statistics
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil


@dataclass
class PerformanceMetric:
    """Performance metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: float
    metadata: dict[str, Any] = None


@dataclass
class PerformanceTestResult:
    """Result of a performance test."""
    test_name: str
    status: str  # "pass", "fail", "warning"
    duration: float
    metrics: list[PerformanceMetric]
    error_message: str | None = None
    recommendations: list[str] = None


class PerformanceProfiler:
    """Performance profiler for monitoring system resources."""

    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        self.initial_cpu = self.get_cpu_usage()

    def get_memory_usage(self) -> dict[str, float]:
        """Get current memory usage."""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent(),
        }

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()

    def get_system_metrics(self) -> dict[str, Any]:
        """Get comprehensive system metrics."""
        return {
            "memory": self.get_memory_usage(),
            "cpu": self.get_cpu_usage(),
            "threads": self.process.num_threads(),
            "open_files": len(self.process.open_files()),
            "connections": len(self.process.connections()),
        }


class LoadTester:
    """Load testing framework."""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.results = []

    def run_load_test(self, func: Callable, iterations: int,
                     concurrent_users: int = 1) -> PerformanceTestResult:
        """Run load test with specified parameters."""
        print(f"🔄 Running load test: {iterations} iterations, {concurrent_users} concurrent users")

        start_time = time.time()
        profiler = PerformanceProfiler()

        # Run load test
        if concurrent_users == 1:
            # Sequential execution
            results = self._run_sequential(func, iterations)
        else:
            # Concurrent execution
            results = self._run_concurrent(func, iterations, concurrent_users)

        end_time = time.time()
        duration = end_time - start_time

        # Calculate metrics
        metrics = self._calculate_metrics(results, duration, profiler)

        # Determine status
        status = self._evaluate_performance(metrics)

        return PerformanceTestResult(
            test_name="load_test",
            status=status,
            duration=duration,
            metrics=metrics,
            recommendations=self._generate_recommendations(metrics),
        )

    def _run_sequential(self, func: Callable, iterations: int) -> list[float]:
        """Run function sequentially."""
        results = []
        for _ in range(iterations):
            start = time.time()
            try:
                func()
                end = time.time()
                results.append(end - start)
            except Exception as e:
                print(f"Error in load test: {e}")
                results.append(float("inf"))
        return results

    def _run_concurrent(self, func: Callable, iterations: int,
                       concurrent_users: int) -> list[float]:
        """Run function concurrently."""
        results = []
        threads = []
        results_lock = threading.Lock()

        def worker():
            for _ in range(iterations // concurrent_users):
                start = time.time()
                try:
                    func()
                    end = time.time()
                    with results_lock:
                        results.append(end - start)
                except Exception as e:
                    print(f"Error in concurrent test: {e}")
                    with results_lock:
                        results.append(float("inf"))

        # Start threads
        for _ in range(concurrent_users):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        return results

    def _calculate_metrics(self, results: list[float], duration: float,
                          profiler: PerformanceProfiler) -> list[PerformanceMetric]:
        """Calculate performance metrics."""
        metrics = []

        # Filter out failed tests
        valid_results = [r for r in results if r != float("inf")]

        if valid_results:
            metrics.extend([
                PerformanceMetric(
                    name="avg_response_time",
                    value=statistics.mean(valid_results),
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="min_response_time",
                    value=min(valid_results),
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="max_response_time",
                    value=max(valid_results),
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="median_response_time",
                    value=statistics.median(valid_results),
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="p95_response_time",
                    value=statistics.quantiles(valid_results, n=20)[18] if len(valid_results) > 1 else valid_results[0],
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="throughput",
                    value=len(valid_results) / duration,
                    unit="requests/second",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="success_rate",
                    value=(len(valid_results) / len(results)) * 100,
                    unit="percent",
                    timestamp=time.time(),
                ),
            ])

        # Add system metrics
        system_metrics = profiler.get_system_metrics()
        metrics.extend([
            PerformanceMetric(
                name="memory_usage_mb",
                value=system_metrics["memory"]["rss"],
                unit="MB",
                timestamp=time.time(),
            ),
            PerformanceMetric(
                name="cpu_usage_percent",
                value=system_metrics["cpu"],
                unit="percent",
                timestamp=time.time(),
            ),
        ])

        return metrics

    def _evaluate_performance(self, metrics: list[PerformanceMetric]) -> str:
        """Evaluate performance and determine status."""
        # Get key metrics
        avg_response_time = next((m.value for m in metrics if m.name == "avg_response_time"), 0)
        throughput = next((m.value for m in metrics if m.name == "throughput"), 0)
        success_rate = next((m.value for m in metrics if m.name == "success_rate"), 0)

        # Performance thresholds
        if success_rate < 95:
            return "fail"
        if avg_response_time > 5.0 or throughput < 10:
            return "warning"
        return "pass"

    def _generate_recommendations(self, metrics: list[PerformanceMetric]) -> list[str]:
        """Generate performance recommendations."""
        recommendations = []

        avg_response_time = next((m.value for m in metrics if m.name == "avg_response_time"), 0)
        throughput = next((m.value for m in metrics if m.name == "throughput"), 0)
        memory_usage = next((m.value for m in metrics if m.name == "memory_usage_mb"), 0)

        if avg_response_time > 2.0:
            recommendations.append("Consider optimizing response time - current average is high")

        if throughput < 50:
            recommendations.append("Throughput is low - consider performance optimization")

        if memory_usage > 500:
            recommendations.append("High memory usage detected - consider memory optimization")

        return recommendations


class StressTester:
    """Stress testing framework."""

    def __init__(self):
        self.results = []

    def run_stress_test(self, func: Callable, duration: int = 60,
                       max_workers: int = 50) -> PerformanceTestResult:
        """Run stress test for specified duration."""
        print(f"💪 Running stress test: {duration}s duration, {max_workers} workers")

        start_time = time.time()
        profiler = PerformanceProfiler()
        results = []
        stop_event = threading.Event()

        def worker():
            while not stop_event.is_set():
                try:
                    start = time.time()
                    func()
                    end = time.time()
                    results.append(end - start)
                except Exception as e:
                    print(f"Error in stress test: {e}")
                    results.append(float("inf"))

        # Start worker threads
        threads = []
        for _ in range(max_workers):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Run for specified duration
        time.sleep(duration)
        stop_event.set()

        # Wait for threads to finish
        for thread in threads:
            thread.join()

        end_time = time.time()
        test_duration = end_time - start_time

        # Calculate metrics
        metrics = self._calculate_stress_metrics(results, test_duration, profiler)

        # Determine status
        status = self._evaluate_stress_performance(metrics)

        return PerformanceTestResult(
            test_name="stress_test",
            status=status,
            duration=test_duration,
            metrics=metrics,
            recommendations=self._generate_stress_recommendations(metrics),
        )

    def _calculate_stress_metrics(self, results: list[float], duration: float,
                                 profiler: PerformanceProfiler) -> list[PerformanceMetric]:
        """Calculate stress test metrics."""
        metrics = []

        valid_results = [r for r in results if r != float("inf")]

        if valid_results:
            metrics.extend([
                PerformanceMetric(
                    name="total_requests",
                    value=len(results),
                    unit="count",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="successful_requests",
                    value=len(valid_results),
                    unit="count",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="failed_requests",
                    value=len(results) - len(valid_results),
                    unit="count",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="avg_response_time",
                    value=statistics.mean(valid_results),
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="max_response_time",
                    value=max(valid_results),
                    unit="seconds",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="requests_per_second",
                    value=len(results) / duration,
                    unit="requests/second",
                    timestamp=time.time(),
                ),
                PerformanceMetric(
                    name="error_rate",
                    value=((len(results) - len(valid_results)) / len(results)) * 100,
                    unit="percent",
                    timestamp=time.time(),
                ),
            ])

        # Add system metrics
        system_metrics = profiler.get_system_metrics()
        metrics.extend([
            PerformanceMetric(
                name="peak_memory_mb",
                value=system_metrics["memory"]["rss"],
                unit="MB",
                timestamp=time.time(),
            ),
            PerformanceMetric(
                name="peak_cpu_percent",
                value=system_metrics["cpu"],
                unit="percent",
                timestamp=time.time(),
            ),
        ])

        return metrics

    def _evaluate_stress_performance(self, metrics: list[PerformanceMetric]) -> str:
        """Evaluate stress test performance."""
        error_rate = next((m.value for m in metrics if m.name == "error_rate"), 0)
        avg_response_time = next((m.value for m in metrics if m.name == "avg_response_time"), 0)

        if error_rate > 10:
            return "fail"
        if error_rate > 5 or avg_response_time > 10:
            return "warning"
        return "pass"

    def _generate_stress_recommendations(self, metrics: list[PerformanceMetric]) -> list[str]:
        """Generate stress test recommendations."""
        recommendations = []

        error_rate = next((m.value for m in metrics if m.name == "error_rate"), 0)
        avg_response_time = next((m.value for m in metrics if m.name == "avg_response_time"), 0)
        peak_memory = next((m.value for m in metrics if m.name == "peak_memory_mb"), 0)

        if error_rate > 5:
            recommendations.append(f"High error rate ({error_rate:.1f}%) - investigate stability issues")

        if avg_response_time > 5:
            recommendations.append(f"High response time ({avg_response_time:.2f}s) - optimize performance")

        if peak_memory > 1000:
            recommendations.append(f"High memory usage ({peak_memory:.1f}MB) - consider memory optimization")

        return recommendations


class PerformanceTestingFramework:
    """Main performance testing framework."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "performance"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.load_tester = LoadTester()
        self.stress_tester = StressTester()
        self.results = []

    def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run comprehensive performance tests."""
        print("🚀 Running Comprehensive Performance Tests...")

        # Define test functions
        test_functions = {
            "basic_math": lambda: sum(range(1000)),
            "string_operations": lambda: "test" * 1000,
            "list_operations": lambda: [i for i in range(1000)],
            "file_operations": self._test_file_operations,
            "memory_intensive": self._test_memory_intensive,
        }

        # Run load tests
        for test_name, test_func in test_functions.items():
            print(f"\n📊 Running load test: {test_name}")
            result = self.load_tester.run_load_test(test_func, iterations=100, concurrent_users=5)
            result.test_name = f"load_{test_name}"
            self.results.append(result)

        # Run stress tests
        for test_name, test_func in test_functions.items():
            print(f"\n💪 Running stress test: {test_name}")
            result = self.stress_tester.run_stress_test(test_func, duration=30, max_workers=10)
            result.test_name = f"stress_{test_name}"
            self.results.append(result)

        # Generate report
        return self._generate_report()

    def _test_file_operations(self) -> None:
        """Test file operations performance."""
        temp_file = self.project_root / "temp_test_file.txt"
        try:
            with open(temp_file, "w") as f:
                f.write("test data" * 100)
            with open(temp_file) as f:
                f.read()
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def _test_memory_intensive(self) -> None:
        """Test memory-intensive operations."""
        data = []
        for _ in range(1000):
            data.append([i for i in range(100)])
        # Process data
        result = sum(len(item) for item in data)
        del data

    def _generate_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "pass")
        failed_tests = sum(1 for r in self.results if r.status == "fail")
        warning_tests = sum(1 for r in self.results if r.status == "warning")

        # Calculate overall score
        if total_tests == 0:
            score = 100
        else:
            score = ((passed_tests + warning_tests * 0.5) / total_tests) * 100

        # Generate detailed results
        detailed_results = []
        for result in self.results:
            detailed_results.append({
                "test_name": result.test_name,
                "status": result.status,
                "duration": result.duration,
                "metrics": [asdict(m) for m in result.metrics],
                "error_message": result.error_message,
                "recommendations": result.recommendations or [],
            })

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "score": round(score, 1),
            },
            "results": detailed_results,
            "recommendations": self._generate_overall_recommendations(),
        }

        # Save report
        report_file = self.reports_dir / f"performance_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Performance report saved to: {report_file}")

        return report

    def _generate_overall_recommendations(self) -> list[str]:
        """Generate overall performance recommendations."""
        recommendations = []

        # Analyze all results
        all_metrics = []
        for result in self.results:
            all_metrics.extend(result.metrics)

        # Check for common issues
        avg_response_times = [m.value for m in all_metrics if m.name == "avg_response_time"]
        if avg_response_times and statistics.mean(avg_response_times) > 2.0:
            recommendations.append("Overall response times are high - consider performance optimization")

        memory_usage = [m.value for m in all_metrics if m.name == "memory_usage_mb"]
        if memory_usage and max(memory_usage) > 500:
            recommendations.append("High memory usage detected - consider memory optimization")

        error_rates = [m.value for m in all_metrics if m.name == "error_rate"]
        if error_rates and any(rate > 5 for rate in error_rates):
            recommendations.append("High error rates detected - investigate stability issues")

        return recommendations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Performance Testing Framework")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    framework = PerformanceTestingFramework(args.project_root)
    report = framework.run_comprehensive_tests()

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Pretty print format
        summary = report["summary"]
        output = f"""
🚀 PERFORMANCE TEST RESULTS
{'=' * 50}
Total Tests: {summary['total_tests']}
Passed: {summary['passed']}
Failed: {summary['failed']}
Warnings: {summary['warnings']}
Score: {summary['score']}/100

Recommendations:
"""
        for rec in report["recommendations"]:
            output += f"  • {rec}\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
