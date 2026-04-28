#!/usr/bin/env python3
"""
Advanced Performance Testing Infrastructure
Comprehensive performance testing with benchmarks, load testing, and optimization.
"""

import argparse
import concurrent.futures
import json
import statistics
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import psutil


@dataclass
class PerformanceMetric:
    """Performance metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: float
    category: str
    percentile_50: float | None = None
    percentile_95: float | None = None
    percentile_99: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    std_dev: float | None = None


@dataclass
class PerformanceTestResult:
    """Performance test result."""
    test_name: str
    status: str  # "pass", "fail", "warning"
    duration: float
    metrics: list[PerformanceMetric]
    throughput: float
    latency: float
    error_rate: float
    recommendations: list[str]
    baseline_comparison: dict[str, Any] | None = None


@dataclass
class LoadTestConfig:
    """Load test configuration."""
    name: str
    duration: int  # seconds
    concurrent_users: int
    ramp_up_time: int  # seconds
    target_throughput: float  # requests per second
    max_response_time: float  # milliseconds
    error_threshold: float  # percentage


class AdvancedPerformanceProfiler:
    """Advanced performance profiler with detailed metrics."""

    def __init__(self):
        self.metrics = []
        self.start_time = time.time()
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval: float = 0.1) -> None:
        """Start continuous performance monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True,
        )
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self, interval: float) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._collect_metrics()
                time.sleep(interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(interval)

    def _collect_metrics(self) -> None:
        """Collect comprehensive performance metrics."""
        timestamp = time.time()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

        self.metrics.append(PerformanceMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            timestamp=timestamp,
            category="system",
        ))

        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics.append(PerformanceMetric(
            name="memory_usage",
            value=memory.percent,
            unit="percent",
            timestamp=timestamp,
            category="system",
        ))

        self.metrics.append(PerformanceMetric(
            name="memory_available",
            value=memory.available / 1024 / 1024,  # MB
            unit="MB",
            timestamp=timestamp,
            category="system",
        ))

        # Disk metrics
        disk = psutil.disk_usage("/")
        self.metrics.append(PerformanceMetric(
            name="disk_usage",
            value=(disk.used / disk.total) * 100,
            unit="percent",
            timestamp=timestamp,
            category="system",
        ))

        # Network metrics
        try:
            net_io = psutil.net_io_counters()
            self.metrics.append(PerformanceMetric(
                name="network_bytes_sent",
                value=net_io.bytes_sent,
                unit="bytes",
                timestamp=timestamp,
                category="network",
            ))

            self.metrics.append(PerformanceMetric(
                name="network_bytes_recv",
                value=net_io.bytes_recv,
                unit="bytes",
                timestamp=timestamp,
                category="network",
            ))
        except Exception:
            pass  # Network metrics may not be available

    def get_summary_metrics(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics:
            return {}

        summary = {}
        metrics_by_name = {}

        # Group metrics by name
        for metric in self.metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric.value)

        # Calculate statistics for each metric
        for name, values in metrics_by_name.items():
            if values:
                summary[name] = {
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "p50": np.percentile(values, 50),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99),
                    "count": len(values),
                }

        return summary


class LoadTester:
    """Advanced load testing with multiple scenarios."""

    def __init__(self, max_workers: int = 100):
        self.max_workers = max_workers
        self.results = []
        self.profiler = AdvancedPerformanceProfiler()

    def run_load_test(self, func: Callable, config: LoadTestConfig) -> PerformanceTestResult:
        """Run load test with given configuration."""
        print(f"🔥 Running load test: {config.name}")
        print(f"   Duration: {config.duration}s, Users: {config.concurrent_users}")

        # Start monitoring
        self.profiler.start_monitoring()

        start_time = time.time()
        results = []
        errors = 0

        # Create thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.concurrent_users) as executor:
            # Submit tasks
            futures = []
            for i in range(config.concurrent_users):
                future = executor.submit(self._run_single_request, func, i)
                futures.append(future)

            # Collect results
            for future in concurrent.futures.as_completed(futures, timeout=config.duration):
                try:
                    result = future.result(timeout=1)
                    results.append(result)
                except Exception as e:
                    errors += 1
                    print(f"Request failed: {e}")

        # Stop monitoring
        self.profiler.stop_monitoring()

        end_time = time.time()
        duration = end_time - start_time

        # Calculate metrics
        if results:
            response_times = [r["response_time"] for r in results]
            throughput = len(results) / duration
            avg_latency = statistics.mean(response_times)
            error_rate = (errors / (len(results) + errors)) * 100
        else:
            response_times = []
            throughput = 0
            avg_latency = 0
            error_rate = 100

        # Create performance metrics
        metrics = self._create_performance_metrics(response_times, duration)

        # Determine test status
        status = self._evaluate_test_status(
            throughput, avg_latency, error_rate, config,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            throughput, avg_latency, error_rate, config,
        )

        return PerformanceTestResult(
            test_name=config.name,
            status=status,
            duration=duration,
            metrics=metrics,
            throughput=throughput,
            latency=avg_latency,
            error_rate=error_rate,
            recommendations=recommendations,
        )

    def _run_single_request(self, func: Callable, request_id: int) -> dict[str, Any]:
        """Run a single request and measure performance."""
        start_time = time.time()

        try:
            # Execute the function
            result = func()

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "request_id": request_id,
                "response_time": response_time,
                "success": True,
                "result": result,
            }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "request_id": request_id,
                "response_time": response_time,
                "success": False,
                "error": str(e),
            }

    def _create_performance_metrics(self, response_times: list[float],
                                  duration: float) -> list[PerformanceMetric]:
        """Create performance metrics from test results."""
        metrics = []
        timestamp = time.time()

        if response_times:
            # Response time metrics
            metrics.append(PerformanceMetric(
                name="response_time_avg",
                value=statistics.mean(response_times),
                unit="ms",
                timestamp=timestamp,
                category="performance",
                percentile_50=np.percentile(response_times, 50),
                percentile_95=np.percentile(response_times, 95),
                percentile_99=np.percentile(response_times, 99),
                min_value=min(response_times),
                max_value=max(response_times),
                std_dev=statistics.stdev(response_times) if len(response_times) > 1 else 0,
            ))

            # Throughput metrics
            metrics.append(PerformanceMetric(
                name="throughput",
                value=len(response_times) / duration,
                unit="requests/second",
                timestamp=timestamp,
                category="performance",
            ))

        # System metrics from profiler
        profiler_metrics = self.profiler.get_summary_metrics()
        for name, stats in profiler_metrics.items():
            metrics.append(PerformanceMetric(
                name=name,
                value=stats["avg"],
                unit="percent" if "usage" in name else "MB" if "memory" in name else "bytes",
                timestamp=timestamp,
                category="system",
                percentile_50=stats["p50"],
                percentile_95=stats["p95"],
                percentile_99=stats["p99"],
                min_value=stats["min"],
                max_value=stats["max"],
                std_dev=stats["std"],
            ))

        return metrics

    def _evaluate_test_status(self, throughput: float, latency: float,
                            error_rate: float, config: LoadTestConfig) -> str:
        """Evaluate test status based on performance criteria."""
        if error_rate > config.error_threshold:
            return "fail"

        if latency > config.max_response_time:
            return "fail"

        if throughput < config.target_throughput * 0.8:  # 80% of target
            return "warning"

        return "pass"

    def _generate_recommendations(self, throughput: float, latency: float,
                                error_rate: float, config: LoadTestConfig) -> list[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        if error_rate > config.error_threshold:
            recommendations.append(f"High error rate ({error_rate:.1f}%) - investigate error causes")

        if latency > config.max_response_time:
            recommendations.append(f"High latency ({latency:.1f}ms) - optimize response time")

        if throughput < config.target_throughput * 0.8:
            recommendations.append(f"Low throughput ({throughput:.1f} req/s) - optimize performance")

        if latency > config.max_response_time * 0.8:
            recommendations.append("Consider caching or database optimization")

        if throughput < config.target_throughput:
            recommendations.append("Consider horizontal scaling or performance tuning")

        return recommendations


class StressTester:
    """Advanced stress testing with resource exhaustion scenarios."""

    def __init__(self):
        self.profiler = AdvancedPerformanceProfiler()

    def run_stress_test(self, func: Callable, duration: int = 300,
                       max_workers: int = 200) -> PerformanceTestResult:
        """Run stress test to find breaking points."""
        print(f"💥 Running stress test for {duration}s with {max_workers} workers")

        # Start monitoring
        self.profiler.start_monitoring()

        start_time = time.time()
        results = []
        errors = 0

        # Create thread pool with high concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit continuous tasks
            futures = []
            task_id = 0

            while time.time() - start_time < duration:
                # Submit new tasks
                for _ in range(min(10, max_workers - len(futures))):
                    future = executor.submit(self._run_stress_request, func, task_id)
                    futures.append(future)
                    task_id += 1

                # Collect completed tasks
                completed_futures = []
                for future in futures:
                    if future.done():
                        try:
                            result = future.result(timeout=0.1)
                            results.append(result)
                            if not result["success"]:
                                errors += 1
                        except Exception:
                            errors += 1
                        completed_futures.append(future)

                # Remove completed futures
                for future in completed_futures:
                    futures.remove(future)

                time.sleep(0.1)  # Small delay to prevent overwhelming

        # Stop monitoring
        self.profiler.stop_monitoring()

        end_time = time.time()
        test_duration = end_time - start_time

        # Calculate metrics
        if results:
            response_times = [r["response_time"] for r in results]
            throughput = len(results) / test_duration
            avg_latency = statistics.mean(response_times)
            error_rate = (errors / (len(results) + errors)) * 100
        else:
            response_times = []
            throughput = 0
            avg_latency = 0
            error_rate = 100

        # Create performance metrics
        metrics = self._create_stress_metrics(response_times, test_duration)

        # Determine test status
        status = self._evaluate_stress_status(throughput, avg_latency, error_rate)

        # Generate recommendations
        recommendations = self._generate_stress_recommendations(
            throughput, avg_latency, error_rate, len(results),
        )

        return PerformanceTestResult(
            test_name="stress_test",
            status=status,
            duration=test_duration,
            metrics=metrics,
            throughput=throughput,
            latency=avg_latency,
            error_rate=error_rate,
            recommendations=recommendations,
        )

    def _run_stress_request(self, func: Callable, request_id: int) -> dict[str, Any]:
        """Run a single stress test request."""
        start_time = time.time()

        try:
            result = func()
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "request_id": request_id,
                "response_time": response_time,
                "success": True,
                "result": result,
            }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "request_id": request_id,
                "response_time": response_time,
                "success": False,
                "error": str(e),
            }

    def _create_stress_metrics(self, response_times: list[float],
                             duration: float) -> list[PerformanceMetric]:
        """Create stress test performance metrics."""
        metrics = []
        timestamp = time.time()

        if response_times:
            # Response time metrics
            metrics.append(PerformanceMetric(
                name="stress_response_time_avg",
                value=statistics.mean(response_times),
                unit="ms",
                timestamp=timestamp,
                category="stress",
                percentile_50=np.percentile(response_times, 50),
                percentile_95=np.percentile(response_times, 95),
                percentile_99=np.percentile(response_times, 99),
                min_value=min(response_times),
                max_value=max(response_times),
                std_dev=statistics.stdev(response_times) if len(response_times) > 1 else 0,
            ))

            # Throughput metrics
            metrics.append(PerformanceMetric(
                name="stress_throughput",
                value=len(response_times) / duration,
                unit="requests/second",
                timestamp=timestamp,
                category="stress",
            ))

        # System metrics from profiler
        profiler_metrics = self.profiler.get_summary_metrics()
        for name, stats in profiler_metrics.items():
            metrics.append(PerformanceMetric(
                name=f"stress_{name}",
                value=stats["avg"],
                unit="percent" if "usage" in name else "MB" if "memory" in name else "bytes",
                timestamp=timestamp,
                category="stress",
                percentile_50=stats["p50"],
                percentile_95=stats["p95"],
                percentile_99=stats["p99"],
                min_value=stats["min"],
                max_value=stats["max"],
                std_dev=stats["std"],
            ))

        return metrics

    def _evaluate_stress_status(self, throughput: float, latency: float,
                              error_rate: float) -> str:
        """Evaluate stress test status."""
        if error_rate > 50:  # More than 50% errors
            return "fail"

        if latency > 5000:  # More than 5 seconds
            return "fail"

        if error_rate > 20:  # More than 20% errors
            return "warning"

        return "pass"

    def _generate_stress_recommendations(self, throughput: float, latency: float,
                                       error_rate: float, total_requests: int) -> list[str]:
        """Generate stress test recommendations."""
        recommendations = []

        if error_rate > 50:
            recommendations.append("System failed under stress - implement better error handling")

        if latency > 5000:
            recommendations.append("System too slow under stress - optimize performance")

        if error_rate > 20:
            recommendations.append("High error rate under stress - improve stability")

        if total_requests < 100:
            recommendations.append("Low request count - system may be overwhelmed")

        recommendations.append("Consider implementing circuit breakers")
        recommendations.append("Add rate limiting and throttling")
        recommendations.append("Implement graceful degradation")

        return recommendations


class PerformanceTestingFramework:
    """Comprehensive performance testing framework."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "performance"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.load_tester = LoadTester()
        self.stress_tester = StressTester()
        self.test_results = []

        # Performance test configurations
        self.load_test_configs = [
            LoadTestConfig(
                name="light_load",
                duration=60,
                concurrent_users=10,
                ramp_up_time=10,
                target_throughput=5.0,
                max_response_time=1000,
                error_threshold=5.0,
            ),
            LoadTestConfig(
                name="medium_load",
                duration=120,
                concurrent_users=50,
                ramp_up_time=20,
                target_throughput=25.0,
                max_response_time=2000,
                error_threshold=10.0,
            ),
            LoadTestConfig(
                name="heavy_load",
                duration=180,
                concurrent_users=100,
                ramp_up_time=30,
                target_throughput=50.0,
                max_response_time=5000,
                error_threshold=15.0,
            ),
        ]

    def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run comprehensive performance test suite."""
        print("🚀 Running Comprehensive Performance Test Suite...")

        # Run load tests
        for config in self.load_test_configs:
            print(f"\n📊 Running {config.name} test...")
            result = self._run_load_test_scenario(config)
            self.test_results.append(result)

        # Run stress test
        print("\n💥 Running stress test...")
        stress_result = self._run_stress_test_scenario()
        self.test_results.append(stress_result)

        # Run memory leak test
        print("\n🧠 Running memory leak test...")
        memory_result = self._run_memory_leak_test()
        self.test_results.append(memory_result)

        # Run CPU intensive test
        print("\n⚡ Running CPU intensive test...")
        cpu_result = self._run_cpu_intensive_test()
        self.test_results.append(cpu_result)

        # Generate comprehensive report
        return self._generate_performance_report()

    def _run_load_test_scenario(self, config: LoadTestConfig) -> PerformanceTestResult:
        """Run a specific load test scenario."""
        # Define test function (simulate API call)
        def test_function():
            # Simulate some work
            time.sleep(0.01)  # 10ms of work
            return {"status": "success", "data": "test_data"}

        return self.load_tester.run_load_test(test_function, config)

    def _run_stress_test_scenario(self) -> PerformanceTestResult:
        """Run stress test scenario."""
        def stress_function():
            # Simulate CPU intensive work
            result = 0
            for i in range(1000):
                result += i * i
            return {"result": result}

        return self.stress_tester.run_stress_test(stress_function, duration=60, max_workers=50)

    def _run_memory_leak_test(self) -> PerformanceTestResult:
        """Run memory leak detection test."""
        print("  🔍 Testing for memory leaks...")

        start_memory = psutil.virtual_memory().used
        start_time = time.time()

        # Simulate memory allocation
        data_structures = []
        for i in range(100):
            # Allocate memory
            data = [0] * 10000
            data_structures.append(data)
            time.sleep(0.01)

        # Check memory usage
        end_memory = psutil.virtual_memory().used
        end_time = time.time()

        memory_increase = end_memory - start_memory
        duration = end_time - start_time

        # Create metrics
        metrics = [
            PerformanceMetric(
                name="memory_start",
                value=start_memory / 1024 / 1024,  # MB
                unit="MB",
                timestamp=start_time,
                category="memory",
            ),
            PerformanceMetric(
                name="memory_end",
                value=end_memory / 1024 / 1024,  # MB
                unit="MB",
                timestamp=end_time,
                category="memory",
            ),
            PerformanceMetric(
                name="memory_increase",
                value=memory_increase / 1024 / 1024,  # MB
                unit="MB",
                timestamp=end_time,
                category="memory",
            ),
        ]

        # Determine status
        if memory_increase > 50 * 1024 * 1024:  # More than 50MB increase
            status = "fail"
            recommendations = ["Potential memory leak detected", "Implement proper cleanup"]
        else:
            status = "pass"
            recommendations = ["Memory usage within acceptable limits"]

        return PerformanceTestResult(
            test_name="memory_leak_test",
            status=status,
            duration=duration,
            metrics=metrics,
            throughput=0,
            latency=0,
            error_rate=0,
            recommendations=recommendations,
        )

    def _run_cpu_intensive_test(self) -> PerformanceTestResult:
        """Run CPU intensive performance test."""
        print("  ⚡ Testing CPU performance...")

        start_time = time.time()

        # CPU intensive calculation
        result = 0
        for i in range(1000000):
            result += i * i * i

        end_time = time.time()
        duration = end_time - start_time

        # Create metrics
        metrics = [
            PerformanceMetric(
                name="cpu_calculation_time",
                value=duration,
                unit="seconds",
                timestamp=end_time,
                category="cpu",
            ),
            PerformanceMetric(
                name="cpu_operations_per_second",
                value=1000000 / duration,
                unit="ops/second",
                timestamp=end_time,
                category="cpu",
            ),
        ]

        # Determine status
        if duration > 10:  # More than 10 seconds
            status = "fail"
            recommendations = ["CPU performance below expectations", "Consider optimization"]
        elif duration > 5:  # More than 5 seconds
            status = "warning"
            recommendations = ["CPU performance could be improved"]
        else:
            status = "pass"
            recommendations = ["CPU performance is good"]

        return PerformanceTestResult(
            test_name="cpu_intensive_test",
            status=status,
            duration=duration,
            metrics=metrics,
            throughput=1000000 / duration,
            latency=duration * 1000,
            error_rate=0,
            recommendations=recommendations,
        )

    def _generate_performance_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        print("📊 Generating Performance Report...")

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "pass"])
        failed_tests = len([r for r in self.test_results if r.status == "fail"])
        warning_tests = len([r for r in self.test_results if r.status == "warning"])

        # Calculate average metrics
        avg_throughput = statistics.mean([r.throughput for r in self.test_results if r.throughput > 0])
        avg_latency = statistics.mean([r.latency for r in self.test_results if r.latency > 0])
        avg_error_rate = statistics.mean([r.error_rate for r in self.test_results])

        # Generate recommendations
        all_recommendations = []
        for result in self.test_results:
            all_recommendations.extend(result.recommendations)

        # Remove duplicates
        unique_recommendations = list(set(all_recommendations))

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_throughput": round(avg_throughput, 2),
                "average_latency": round(avg_latency, 2),
                "average_error_rate": round(avg_error_rate, 2),
            },
            "test_results": [asdict(result) for result in self.test_results],
            "recommendations": unique_recommendations,
            "performance_insights": self._generate_performance_insights(),
        }

        # Save report
        self._save_performance_report(report)

        return report

    def _generate_performance_insights(self) -> list[str]:
        """Generate performance insights and recommendations."""
        insights = []

        # Analyze throughput
        throughputs = [r.throughput for r in self.test_results if r.throughput > 0]
        if throughputs:
            max_throughput = max(throughputs)
            insights.append(f"Maximum throughput achieved: {max_throughput:.1f} req/s")

        # Analyze latency
        latencies = [r.latency for r in self.test_results if r.latency > 0]
        if latencies:
            max_latency = max(latencies)
            insights.append(f"Maximum latency observed: {max_latency:.1f} ms")

        # Analyze error rates
        error_rates = [r.error_rate for r in self.test_results]
        if error_rates:
            max_error_rate = max(error_rates)
            insights.append(f"Maximum error rate: {max_error_rate:.1f}%")

        # General insights
        insights.append("Consider implementing caching for better performance")
        insights.append("Monitor memory usage during peak loads")
        insights.append("Implement proper error handling and recovery")
        insights.append("Consider horizontal scaling for high throughput requirements")

        return insights

    def _save_performance_report(self, report: dict[str, Any]) -> None:
        """Save performance report."""
        # Save JSON report
        json_file = self.reports_dir / f"performance_report_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"performance_summary_{int(time.time())}.md"
        self._save_performance_summary(report, summary_file)

        print("📊 Performance reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")

    def _save_performance_summary(self, report: dict[str, Any], file_path: Path) -> None:
        """Save markdown summary report."""
        summary = report["summary"]

        content = f"""# Performance Testing Report

**Generated**: {report['timestamp']}
**Success Rate**: {summary['success_rate']:.1f}%

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary['total_tests']} |
| Passed Tests | {summary['passed_tests']} |
| Failed Tests | {summary['failed_tests']} |
| Warning Tests | {summary['warning_tests']} |
| Success Rate | {summary['success_rate']:.1f}% |
| Average Throughput | {summary['average_throughput']:.1f} req/s |
| Average Latency | {summary['average_latency']:.1f} ms |
| Average Error Rate | {summary['average_error_rate']:.1f}% |

## Test Results

"""

        for result in report["test_results"]:
            status_emoji = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⚠️"
            content += f"### {status_emoji} {result['test_name']}\n\n"
            content += f"- **Status**: {result['status']}\n"
            content += f"- **Duration**: {result['duration']:.1f}s\n"
            content += f"- **Throughput**: {result['throughput']:.1f} req/s\n"
            content += f"- **Latency**: {result['latency']:.1f} ms\n"
            content += f"- **Error Rate**: {result['error_rate']:.1f}%\n\n"

            if result["recommendations"]:
                content += "**Recommendations**:\n"
                for rec in result["recommendations"]:
                    content += f"- {rec}\n"
                content += "\n"

        if report["recommendations"]:
            content += "## Overall Recommendations\n\n"
            for rec in report["recommendations"]:
                content += f"- {rec}\n"

        if report["performance_insights"]:
            content += "\n## Performance Insights\n\n"
            for insight in report["performance_insights"]:
                content += f"- {insight}\n"

        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Advanced Performance Testing")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--load-test", help="Run specific load test")
    parser.add_argument("--stress-test", action="store_true", help="Run stress test")
    parser.add_argument("--memory-test", action="store_true", help="Run memory leak test")
    parser.add_argument("--cpu-test", action="store_true", help="Run CPU intensive test")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    framework = PerformanceTestingFramework(args.project_root)

    if args.load_test:
        # Run specific load test
        config = next((c for c in framework.load_test_configs if c.name == args.load_test), None)
        if config:
            result = framework._run_load_test_scenario(config)
            report = {"test_result": asdict(result)}
        else:
            report = {"error": f"Load test '{args.load_test}' not found"}
    elif args.stress_test:
        # Run stress test
        result = framework._run_stress_test_scenario()
        report = {"test_result": asdict(result)}
    elif args.memory_test:
        # Run memory test
        result = framework._run_memory_leak_test()
        report = {"test_result": asdict(result)}
    elif args.cpu_test:
        # Run CPU test
        result = framework._run_cpu_intensive_test()
        report = {"test_result": asdict(result)}
    else:
        # Run comprehensive tests
        report = framework.run_comprehensive_tests()

    if args.json:
        output = json.dumps(report, indent=2)
    # Pretty print format
    elif "summary" in report:
        summary = report["summary"]
        output = f"""
🚀 ADVANCED PERFORMANCE TESTING REPORT
{'=' * 60}
Success Rate: {summary['success_rate']:.1f}%
Total Tests: {summary['total_tests']}
Passed: {summary['passed_tests']}
Failed: {summary['failed_tests']}
Warning: {summary['warning_tests']}

Performance Metrics:
  Average Throughput: {summary['average_throughput']:.1f} req/s
  Average Latency: {summary['average_latency']:.1f} ms
  Average Error Rate: {summary['average_error_rate']:.1f}%

Test Results:
"""
        for result in report.get("test_results", []):
            status_emoji = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⚠️"
            output += f"  {status_emoji} {result['test_name']}: {result['status']}\n"
    else:
        output = f"📊 Report: {json.dumps(report, indent=2)}"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
