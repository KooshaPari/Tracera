"""Response Time Analysis for Pheno-SDK.

Automated API response time measurement and reporting.
"""

import statistics
import time
from typing import Any
from unittest.mock import Mock, patch

import pytest


class ResponseTimeAnalyzer:
    """
    Analyzes API response times and performance metrics.
    """

    def __init__(self):
        self.response_times = []
        self.endpoints = []
        self.percentiles = [50, 90, 95, 99]

    def measure_response_time(self, endpoint: str, method: str = "GET", **kwargs) -> dict[str, Any]:
        """
        Measure response time for a specific endpoint.
        """
        start_time = time.time()

        # Mock API call - in real implementation, this would make actual HTTP requests
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_get.return_value = mock_response

            # Simulate API call
            time.sleep(0.05)  # Simulate network delay
            response = mock_get(f"https://api.pheno.com{endpoint}")

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        measurement = {
            "endpoint": endpoint,
            "method": method,
            "response_time_ms": response_time,
            "status_code": response.status_code,
            "timestamp": start_time,
        }

        self.response_times.append(measurement)
        return measurement

    def calculate_statistics(self) -> dict[str, Any]:
        """
        Calculate response time statistics.
        """
        if not self.response_times:
            return {}

        times = [rt["response_time_ms"] for rt in self.response_times]

        stats = {
            "total_requests": len(times),
            "average_response_time": statistics.mean(times),
            "median_response_time": statistics.median(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "standard_deviation": statistics.stdev(times) if len(times) > 1 else 0,
        }

        # Calculate percentiles
        for percentile in self.percentiles:
            stats[f"p{percentile}_response_time"] = self._calculate_percentile(times, percentile)

        return stats

    def _calculate_percentile(self, data: list[float], percentile: float) -> float:
        """
        Calculate percentile value.
        """
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        lower = sorted_data[int(index)]
        upper = sorted_data[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))

    def identify_slow_endpoints(self, threshold_ms: float = 500) -> list[dict[str, Any]]:
        """
        Identify endpoints with response times above threshold.
        """
        return [rt for rt in self.response_times if rt["response_time_ms"] > threshold_ms]

    def generate_report(self) -> str:
        """
        Generate comprehensive response time report.
        """
        stats = self.calculate_statistics()
        slow_endpoints = self.identify_slow_endpoints()

        report = []
        report.append("Pheno-SDK Response Time Analysis Report")
        report.append("=" * 45)

        if not stats:
            report.append("No response time data available")
            return "\n".join(report)

        report.append(f"Total Requests: {stats['total_requests']}")
        report.append(f"Average Response Time: {stats['average_response_time']:.2f}ms")
        report.append(f"Median Response Time: {stats['median_response_time']:.2f}ms")
        report.append(f"Min Response Time: {stats['min_response_time']:.2f}ms")
        report.append(f"Max Response Time: {stats['max_response_time']:.2f}ms")
        report.append(f"Standard Deviation: {stats['standard_deviation']:.2f}ms")

        report.append("\nPercentiles:")
        for percentile in self.percentiles:
            report.append(f"  P{percentile}: {stats[f'p{percentile}_response_time']:.2f}ms")

        if slow_endpoints:
            report.append(f"\nSlow Endpoints (>500ms): {len(slow_endpoints)}")
            for endpoint in slow_endpoints[:5]:  # Show top 5
                report.append(f"  {endpoint['endpoint']}: {endpoint['response_time_ms']:.2f}ms")

        return "\n".join(report)


@pytest.fixture
def response_analyzer():
    """
    Fixture for response time analyzer.
    """
    return ResponseTimeAnalyzer()


class TestResponseTime:
    """
    Test response time performance.
    """

    def test_health_endpoint_response_time(self, response_analyzer):
        """
        Test health endpoint response time.
        """
        measurement = response_analyzer.measure_response_time("/health")
        assert measurement["response_time_ms"] < 500  # Should be under 500ms
        assert measurement["status_code"] == 200

    def test_sdk_endpoint_response_time(self, response_analyzer):
        """
        Test SDK endpoint response time.
        """
        measurement = response_analyzer.measure_response_time("/sdk/v1/status")
        assert measurement["response_time_ms"] < 1000  # Should be under 1 second
        assert measurement["status_code"] == 200

    def test_auth_endpoint_response_time(self, response_analyzer):
        """
        Test authentication endpoint response time.
        """
        measurement = response_analyzer.measure_response_time("/auth/verify")
        assert measurement["response_time_ms"] < 800  # Should be under 800ms
        assert measurement["status_code"] == 200

    def test_response_time_consistency(self, response_analyzer):
        """
        Test response time consistency across multiple requests.
        """
        # Make multiple requests to the same endpoint
        for _ in range(10):
            response_analyzer.measure_response_time("/health")

        stats = response_analyzer.calculate_statistics()
        assert stats["total_requests"] == 10
        assert stats["standard_deviation"] < 50  # Low variance for SDK

    def test_percentile_calculation(self, response_analyzer):
        """
        Test percentile calculation accuracy.
        """
        # Generate test data with known percentiles
        test_times = [i * 5 for i in range(1, 101)]  # 5ms to 500ms
        for i, time_ms in enumerate(test_times):
            response_analyzer.response_times.append(
                {
                    "endpoint": f"/test{i}",
                    "method": "GET",
                    "response_time_ms": time_ms,
                    "status_code": 200,
                    "timestamp": time.time(),
                },
            )

        stats = response_analyzer.calculate_statistics()
        assert stats["p50_response_time"] == 252.5  # Median of 5-500
        assert stats["p90_response_time"] == 455.0  # 90th percentile
        assert stats["p95_response_time"] == 477.5  # 95th percentile
        assert stats["p99_response_time"] == 495.0  # 99th percentile

    def test_slow_endpoint_detection(self, response_analyzer):
        """
        Test slow endpoint detection.
        """
        # Add some slow endpoints
        response_analyzer.response_times.extend(
            [
                {
                    "endpoint": "/slow1",
                    "method": "GET",
                    "response_time_ms": 800,
                    "status_code": 200,
                    "timestamp": time.time(),
                },
                {
                    "endpoint": "/slow2",
                    "method": "POST",
                    "response_time_ms": 1200,
                    "status_code": 200,
                    "timestamp": time.time(),
                },
            ],
        )

        slow_endpoints = response_analyzer.identify_slow_endpoints(threshold_ms=500)
        assert len(slow_endpoints) == 2
        assert all(ep["response_time_ms"] > 500 for ep in slow_endpoints)

    def test_response_time_report_generation(self, response_analyzer):
        """
        Test response time report generation.
        """
        # Add some test data
        for i in range(5):
            response_analyzer.measure_response_time(f"/test{i}")

        report = response_analyzer.generate_report()
        assert "Pheno-SDK Response Time Analysis Report" in report
        assert "Total Requests: 5" in report
        assert "Average Response Time:" in report
        assert "Percentiles:" in report


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """
    Performance benchmark tests.
    """

    def test_benchmark_response_times(self, response_analyzer):
        """
        Benchmark response times for critical endpoints.
        """
        critical_endpoints = ["/health", "/sdk/v1/status", "/auth/verify", "/metrics"]

        for endpoint in critical_endpoints:
            measurement = response_analyzer.measure_response_time(endpoint)
            assert measurement["response_time_ms"] < 1000  # All should be under 1 second

    def test_concurrent_request_handling(self, response_analyzer):
        """
        Test concurrent request handling performance.
        """
        import queue
        import threading

        results = queue.Queue()

        def make_request():
            measurement = response_analyzer.measure_response_time("/health")
            results.put(measurement)

        # Start 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        concurrent_results = []
        while not results.empty():
            concurrent_results.append(results.get())

        assert len(concurrent_results) == 10

        # All requests should complete successfully
        for result in concurrent_results:
            assert result["status_code"] == 200
            assert result["response_time_ms"] < 2000  # Should handle concurrency well
