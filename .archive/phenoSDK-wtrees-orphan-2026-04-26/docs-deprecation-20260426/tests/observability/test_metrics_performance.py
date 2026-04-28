"""Performance tests for advanced metrics collection.

Verifies that metrics collection has <1ms overhead per operation.
"""

from __future__ import annotations

import time

import pytest

from pheno.observability.metrics.advanced import (
    AdvancedMetricsCollector,
    get_metrics_collector,
    reset_metrics_collector,
)


class TestMetricsPerformance:
    """
    Performance tests for metrics collection.
    """

    def setup_method(self) -> None:
        """
        Reset collector before each test.
        """
        reset_metrics_collector()

    def test_token_usage_recording_overhead(self) -> None:
        """
        Test token usage recording overhead is <1ms.
        """
        collector = get_metrics_collector()
        iterations = 10000

        # Warmup
        for _ in range(100):
            collector.record_token_usage(100, 50)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            collector.record_token_usage(100, 50, model="gpt-4")
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nToken usage recording: {avg_overhead_ms:.4f}ms per call")

        # Assert <1ms overhead
        assert avg_overhead_ms < 1.0, f"Overhead {avg_overhead_ms:.4f}ms exceeds 1ms threshold"

    def test_quality_metrics_recording_overhead(self) -> None:
        """
        Test quality metrics recording overhead is <1ms.
        """
        collector = get_metrics_collector()
        iterations = 10000

        # Warmup
        for _ in range(100):
            collector.record_quality_metrics(quality_score=0.9)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            collector.record_quality_metrics(
                quality_score=0.9,
                accuracy_score=0.85,
                relevance_score=0.92,
                confidence_score=0.88,
            )
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nQuality metrics recording: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 1.0, f"Overhead {avg_overhead_ms:.4f}ms exceeds 1ms threshold"

    def test_performance_metrics_recording_overhead(self) -> None:
        """
        Test performance metrics recording overhead is <1ms.
        """
        collector = get_metrics_collector()
        iterations = 10000

        # Warmup
        for _ in range(100):
            collector.record_performance(100.0, success=True)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            collector.record_performance(
                latency_ms=125.5,
                success=True,
                throughput_rps=10.5,
            )
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nPerformance metrics recording: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 1.0, f"Overhead {avg_overhead_ms:.4f}ms exceeds 1ms threshold"

    def test_routing_metrics_recording_overhead(self) -> None:
        """
        Test routing metrics recording overhead is <1ms.
        """
        collector = get_metrics_collector()
        iterations = 10000

        # Warmup
        for _ in range(100):
            collector.record_routing("gpt-4", 0.9, success=True)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            collector.record_routing(
                model="gpt-4",
                confidence=0.92,
                success=True,
                is_fallback=False,
                routing_latency_ms=5.2,
                method_votes={"quality": "gpt-4", "cost": "gpt-3.5-turbo"},
            )
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nRouting metrics recording: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 1.0, f"Overhead {avg_overhead_ms:.4f}ms exceeds 1ms threshold"

    def test_custom_metric_recording_overhead(self) -> None:
        """
        Test custom metric recording overhead is <1ms.
        """
        collector = get_metrics_collector()
        iterations = 10000

        # Warmup
        for _ in range(100):
            collector.record_custom_metric("test_metric", 42.0)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            collector.record_custom_metric("test_metric", 42.0)
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nCustom metric recording: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 1.0, f"Overhead {avg_overhead_ms:.4f}ms exceeds 1ms threshold"

    def test_combined_metrics_recording_overhead(self) -> None:
        """
        Test combined metrics recording overhead is <5ms total.
        """
        collector = get_metrics_collector()
        iterations = 1000

        # Warmup
        for _ in range(100):
            collector.record_token_usage(100, 50)
            collector.record_quality_metrics(quality_score=0.9)
            collector.record_performance(100.0, success=True)
            collector.record_routing("gpt-4", 0.9, success=True)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            collector.record_token_usage(100, 50, model="gpt-4")
            collector.record_quality_metrics(quality_score=0.9)
            collector.record_performance(100.0, success=True)
            collector.record_routing("gpt-4", 0.9, success=True)
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nCombined metrics recording: {avg_overhead_ms:.4f}ms per call")

        # Combined should be <5ms (4 operations * <1ms each)
        assert avg_overhead_ms < 5.0, f"Overhead {avg_overhead_ms:.4f}ms exceeds 5ms threshold"

    def test_export_metrics_overhead(self) -> None:
        """
        Test metrics export overhead.
        """
        collector = get_metrics_collector()

        # Add some metrics
        for _ in range(100):
            collector.record_token_usage(100, 50, model="gpt-4")
            collector.record_quality_metrics(quality_score=0.9)
            collector.record_performance(100.0, success=True)

        iterations = 1000

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            metrics = collector.export_metrics()
            assert len(metrics) > 0
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nMetrics export: {avg_overhead_ms:.4f}ms per call")

        # Export should be relatively fast
        assert avg_overhead_ms < 10.0, f"Export overhead {avg_overhead_ms:.4f}ms exceeds 10ms"

    def test_get_summary_overhead(self) -> None:
        """
        Test summary generation overhead.
        """
        collector = get_metrics_collector()

        # Add metrics
        for _ in range(100):
            collector.record_token_usage(100, 50, model="gpt-4")
            collector.record_quality_metrics(quality_score=0.9)
            collector.record_performance(100.0, success=True)
            collector.record_routing("gpt-4", 0.9, success=True)

        iterations = 1000

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            summary = collector.get_summary()
            assert "token_usage" in summary
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nSummary generation: {avg_overhead_ms:.4f}ms per call")

        # Summary generation should be fast
        assert avg_overhead_ms < 5.0, f"Summary overhead {avg_overhead_ms:.4f}ms exceeds 5ms"

    def test_anomaly_detection_overhead(self) -> None:
        """
        Test anomaly detection overhead.
        """
        collector = get_metrics_collector()

        # Configure thresholds
        collector.configure_thresholds(
            {
                "latency_max_ms": 1000.0,
                "quality_min": 0.7,
            }
        )

        iterations = 1000

        # Benchmark with anomalies
        start = time.perf_counter()
        for _ in range(iterations):
            # These should trigger anomaly detection
            collector.record_performance(2000.0, success=True)  # High latency
            collector.record_quality_metrics(quality_score=0.5)  # Low quality
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nAnomaly detection: {avg_overhead_ms:.4f}ms per call")

        # Anomaly detection adds some overhead but should still be <2ms
        assert avg_overhead_ms < 2.0, f"Anomaly overhead {avg_overhead_ms:.4f}ms exceeds 2ms"

    def test_memory_efficiency(self) -> None:
        """
        Test that metrics don't consume excessive memory.
        """
        import sys

        collector = get_metrics_collector()

        # Get initial size
        initial_size = sys.getsizeof(collector)

        # Add 1000 metrics
        for i in range(1000):
            collector.record_token_usage(100, 50, model=f"model-{i % 5}")
            collector.record_quality_metrics(quality_score=0.9)
            collector.record_performance(100.0, success=True)

        # Get final size
        final_size = sys.getsizeof(collector)
        growth = final_size - initial_size

        print(f"\nMemory growth for 1000 metrics: {growth:,} bytes")

        # Should not grow excessively (allow up to 1MB)
        assert growth < 1_000_000, f"Memory growth {growth:,} bytes exceeds 1MB"

    def test_concurrent_recording_overhead(self) -> None:
        """
        Test overhead with concurrent metric recording.
        """
        import concurrent.futures

        collector = get_metrics_collector()
        iterations_per_thread = 100
        num_threads = 10

        def record_metrics() -> None:
            """
            Record metrics in thread.
            """
            for _ in range(iterations_per_thread):
                collector.record_token_usage(100, 50)
                collector.record_performance(100.0, success=True)

        # Benchmark
        start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(record_metrics) for _ in range(num_threads)]
            concurrent.futures.wait(futures)
        elapsed = time.perf_counter() - start

        total_operations = iterations_per_thread * num_threads * 2  # 2 metrics per iteration
        avg_overhead_ms = (elapsed / total_operations) * 1000

        print(f"\nConcurrent recording: {avg_overhead_ms:.4f}ms per operation")

        # Should still maintain reasonable overhead under concurrency
        assert avg_overhead_ms < 5.0, f"Concurrent overhead {avg_overhead_ms:.4f}ms exceeds 5ms"


class TestBackendPerformance:
    """
    Performance tests for backend adapters.
    """

    @pytest.mark.asyncio
    async def test_prometheus_export_overhead(self) -> None:
        """
        Test Prometheus export overhead.
        """
        from pheno.observability.metrics.advanced import PrometheusBackend
        from pheno.observability.ports import MetricData, MetricType

        backend = PrometheusBackend()

        # Create test metrics
        metrics = [
            MetricData(f"test_metric_{i}", float(i), MetricType.GAUGE, time.time())
            for i in range(100)
        ]

        iterations = 100

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            data = await backend.export(metrics)
            assert len(data) > 0
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nPrometheus export: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 10.0, f"Export overhead {avg_overhead_ms:.4f}ms exceeds 10ms"

    @pytest.mark.asyncio
    async def test_opentelemetry_export_overhead(self) -> None:
        """
        Test OpenTelemetry export overhead.
        """
        from pheno.observability.metrics.advanced import OpenTelemetryBackend
        from pheno.observability.ports import MetricData, MetricType

        backend = OpenTelemetryBackend()

        # Create test metrics
        metrics = [
            MetricData(f"test_metric_{i}", float(i), MetricType.GAUGE, time.time())
            for i in range(100)
        ]

        iterations = 100

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            data = await backend.export(metrics)
            assert "resourceMetrics" in data
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nOpenTelemetry export: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 10.0, f"Export overhead {avg_overhead_ms:.4f}ms exceeds 10ms"

    @pytest.mark.asyncio
    async def test_cloudwatch_export_overhead(self) -> None:
        """
        Test CloudWatch export overhead.
        """
        from pheno.observability.metrics.advanced import CloudWatchBackend
        from pheno.observability.ports import MetricData, MetricType

        backend = CloudWatchBackend()

        # Create test metrics
        metrics = [
            MetricData(f"test_metric_{i}", float(i), MetricType.GAUGE, time.time())
            for i in range(100)
        ]

        iterations = 100

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            data = await backend.export(metrics)
            assert isinstance(data, list)
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nCloudWatch export: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 10.0, f"Export overhead {avg_overhead_ms:.4f}ms exceeds 10ms"

    @pytest.mark.asyncio
    async def test_datadog_export_overhead(self) -> None:
        """
        Test Datadog export overhead.
        """
        from pheno.observability.metrics.advanced import DatadogBackend
        from pheno.observability.ports import MetricData, MetricType

        backend = DatadogBackend()

        # Create test metrics
        metrics = [
            MetricData(f"test_metric_{i}", float(i), MetricType.GAUGE, time.time())
            for i in range(100)
        ]

        iterations = 100

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            data = await backend.export(metrics)
            assert "series" in data
        elapsed = time.perf_counter() - start

        avg_overhead_ms = (elapsed / iterations) * 1000
        print(f"\nDatadog export: {avg_overhead_ms:.4f}ms per call")

        assert avg_overhead_ms < 10.0, f"Export overhead {avg_overhead_ms:.4f}ms exceeds 10ms"
