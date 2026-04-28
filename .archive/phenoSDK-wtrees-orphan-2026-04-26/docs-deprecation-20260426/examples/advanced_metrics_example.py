"""Advanced Metrics Example.

This example demonstrates how to use the advanced metrics and observability framework
with multiple backends, anomaly detection, and alerting.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from pheno.observability.metrics.advanced import (
    AdvancedMetricsCollector,
    CloudWatchBackend,
    DatadogBackend,
    OpenTelemetryBackend,
    PrometheusBackend,
    get_metrics_collector,
    reset_metrics_collector,
)
from pheno.observability.ports import Alert, AlertSeverity

# =============================================================================
# Example 1: Basic Metrics Collection
# =============================================================================


def example_basic_metrics() -> None:
    """
    Demonstrate basic metrics collection.
    """
    print("=" * 80)
    print("Example 1: Basic Metrics Collection")
    print("=" * 80)

    # Get the global metrics collector
    collector = get_metrics_collector()

    # Record token usage
    print("\n1. Recording token usage...")
    collector.record_token_usage(
        input_tokens=1500,
        output_tokens=500,
        model="gpt-4",
        cached_tokens=300,
        savings_tokens=200,
        compression_ratio=0.87,
    )

    # Record quality metrics
    print("2. Recording quality metrics...")
    collector.record_quality_metrics(
        quality_score=0.92,
        accuracy_score=0.88,
        relevance_score=0.95,
        confidence_score=0.90,
    )

    # Record performance metrics
    print("3. Recording performance metrics...")
    collector.record_performance(
        latency_ms=125.5,
        success=True,
        throughput_rps=10.5,
    )

    # Record routing metrics
    print("4. Recording routing metrics...")
    collector.record_routing(
        model="gpt-4",
        confidence=0.92,
        success=True,
        is_fallback=False,
        routing_latency_ms=5.2,
        method_votes={
            "quality": "gpt-4",
            "cost": "gpt-3.5-turbo",
            "latency": "gpt-4",
        },
    )

    # Get summary
    print("\n5. Metrics Summary:")
    summary = collector.get_summary()
    print(f"   Token usage: {summary['token_usage']}")
    print(f"   Quality: {summary['quality']}")
    print(f"   Performance: {summary['performance']}")
    print(f"   Routing: {summary['routing']}")


# =============================================================================
# Example 2: Multi-Backend Export
# =============================================================================


async def example_multi_backend() -> None:
    """
    Demonstrate exporting to multiple backends.
    """
    print("\n" + "=" * 80)
    print("Example 2: Multi-Backend Export")
    print("=" * 80)

    # Initialize backends
    prometheus_backend = PrometheusBackend(endpoint="http://localhost:9091")
    otel_backend = OpenTelemetryBackend(endpoint="http://localhost:4318")
    cloudwatch_backend = CloudWatchBackend(
        namespace="PhenoSDK",
        region="us-east-1",
    )
    datadog_backend = DatadogBackend(
        api_key="dummy_key",  # Replace with real key
        site="datadoghq.com",
    )

    # Collect some metrics
    collector = get_metrics_collector()
    collector.record_token_usage(100, 50, model="gpt-4")
    collector.record_performance(100.0, success=True)

    # Export metrics
    metrics = collector.export_metrics()
    print(f"\nExported {len(metrics)} metrics:")
    for metric in metrics:
        print(f"  - {metric.name}: {metric.value} ({metric.metric_type.value})")

    # Push to Prometheus
    print("\n1. Pushing to Prometheus...")
    prometheus_data = await prometheus_backend.export(metrics)
    print(f"   Prometheus format:\n{prometheus_data[:200]}...")

    # Push to OpenTelemetry
    print("\n2. Pushing to OpenTelemetry...")
    otel_data = await otel_backend.export(metrics)
    print(f"   OTLP format: {len(otel_data['resourceMetrics'])} resources")

    # Push to CloudWatch
    print("\n3. Pushing to CloudWatch...")
    cw_data = await cloudwatch_backend.export(metrics)
    print(f"   CloudWatch format: {len(cw_data)} metric data points")

    # Push to Datadog
    print("\n4. Pushing to Datadog...")
    dd_data = await datadog_backend.export(metrics)
    print(f"   Datadog format: {len(dd_data['series'])} series")


# =============================================================================
# Example 3: Anomaly Detection and Alerting
# =============================================================================


def example_anomaly_detection() -> None:
    """
    Demonstrate anomaly detection and alerting.
    """
    print("\n" + "=" * 80)
    print("Example 3: Anomaly Detection and Alerting")
    print("=" * 80)

    # Reset collector for clean state
    reset_metrics_collector()
    collector = get_metrics_collector()

    # Configure custom thresholds
    print("\n1. Configuring anomaly thresholds...")
    collector.configure_thresholds(
        {
            "latency_max_ms": 200.0,  # Alert if latency > 200ms
            "quality_min": 0.8,  # Alert if quality < 80%
            "success_rate_min_pct": 95.0,  # Alert if success rate < 95%
        }
    )

    # Record normal metrics (no alerts)
    print("\n2. Recording normal metrics...")
    collector.record_performance(150.0, success=True)
    collector.record_quality_metrics(quality_score=0.85)

    # Record anomalous metrics (will trigger alerts)
    print("\n3. Recording anomalous metrics...")
    collector.record_performance(350.0, success=True)  # High latency
    collector.record_quality_metrics(quality_score=0.65)  # Low quality
    collector.record_performance(100.0, success=False)  # Failed request

    # Get alerts
    print("\n4. Checking alerts...")
    alerts = collector.get_alerts(limit=10)
    print(f"   Found {len(alerts)} alerts:")
    for alert in alerts:
        print(f"\n   - Type: {alert.alert_type}")
        print(f"     Severity: {alert.severity.value}")
        print(f"     Message: {alert.message}")
        print(f"     Metadata: {alert.metadata}")


# =============================================================================
# Example 4: Custom Metric Handlers
# =============================================================================


def example_custom_handlers() -> None:
    """
    Demonstrate custom metric handlers.
    """
    print("\n" + "=" * 80)
    print("Example 4: Custom Metric Handlers")
    print("=" * 80)

    reset_metrics_collector()
    collector = get_metrics_collector()

    # Define custom handler
    def handle_high_cost(value: float) -> None:
        """
        Alert on high cost.
        """
        if value > 100.0:
            print(f"\n   ⚠️  HIGH COST ALERT: ${value:.2f}")
        else:
            print(f"   ✓ Cost within budget: ${value:.2f}")

    # Register handler
    print("\n1. Registering custom metric handler...")
    collector.register_custom_metric_handler("total_cost_usd", handle_high_cost)

    # Record custom metrics
    print("\n2. Recording custom metrics...")
    collector.record_custom_metric("total_cost_usd", 85.50)  # OK
    collector.record_custom_metric("total_cost_usd", 125.00)  # Alert!

    # Check custom metrics in summary
    print("\n3. Custom metrics summary:")
    summary = collector.get_summary()
    print(f"   Custom metrics: {summary['custom']}")


# =============================================================================
# Example 5: Dashboard Data Generation
# =============================================================================


async def example_dashboard_data() -> None:
    """
    Demonstrate dashboard data generation.
    """
    print("\n" + "=" * 80)
    print("Example 5: Dashboard Data Generation")
    print("=" * 80)

    reset_metrics_collector()
    collector = get_metrics_collector()

    # Simulate some activity
    print("\n1. Simulating metric collection...")
    for i in range(10):
        collector.record_token_usage(
            input_tokens=100 + i * 10,
            output_tokens=50 + i * 5,
            model="gpt-4",
            compression_ratio=0.8 + i * 0.01,
        )
        collector.record_quality_metrics(
            quality_score=0.85 + i * 0.01,
            confidence_score=0.90 + i * 0.005,
        )
        collector.record_performance(
            latency_ms=100.0 + i * 5,
            success=True,
        )

    # Generate dashboard data
    print("\n2. Generating dashboard data...")
    dashboard_data = await collector.get_dashboard_data()

    print(f"\n   Overview:")
    print(f"   - Uptime: {dashboard_data['overview']['uptime_hours']:.2f} hours")
    print(f"   - Last updated: {dashboard_data['overview']['last_updated']}")

    print(f"\n   Token Usage:")
    print(f"   - Total requests: {dashboard_data['token_usage']['total_requests']}")
    print(f"   - Input tokens: {dashboard_data['token_usage']['total_input_tokens']}")
    print(f"   - Output tokens: {dashboard_data['token_usage']['total_output_tokens']}")

    print(f"\n   Quality:")
    print(f"   - Average: {dashboard_data['quality']['average_quality']:.2%}")
    print(f"   - Confidence: {dashboard_data['quality']['average_confidence']:.2%}")

    print(f"\n   Performance:")
    print(f"   - Average latency: {dashboard_data['performance']['average_latency_ms']:.1f}ms")
    print(f"   - Success rate: {dashboard_data['performance']['success_rate_pct']:.1f}%")

    print(f"\n   Trends (last 50 values):")
    print(f"   - Quality scores: {len(dashboard_data['trends']['quality_scores'])} points")
    print(f"   - Latencies: {len(dashboard_data['trends']['latencies'])} points")


# =============================================================================
# Example 6: Real-World Simulation
# =============================================================================


async def example_real_world_simulation() -> None:
    """
    Simulate real-world metrics collection.
    """
    print("\n" + "=" * 80)
    print("Example 6: Real-World Simulation")
    print("=" * 80)

    reset_metrics_collector()
    collector = get_metrics_collector()

    # Configure realistic thresholds
    collector.configure_thresholds(
        {
            "latency_max_ms": 1000.0,
            "quality_min": 0.7,
            "success_rate_min_pct": 90.0,
        }
    )

    # Simulate 100 LLM requests
    print("\n1. Simulating 100 LLM requests...")
    models = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"]

    for i in range(100):
        # Simulate request
        model = models[i % len(models)]
        input_tokens = 100 + (i % 50) * 10
        output_tokens = 50 + (i % 30) * 5
        latency_ms = 100.0 + (i % 20) * 25.0
        quality_score = 0.75 + (i % 25) * 0.01
        success = i % 10 != 0  # 10% failure rate

        # Record metrics
        collector.record_token_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cached_tokens=int(input_tokens * 0.2),  # 20% cache hit
            savings_tokens=int(input_tokens * 0.15),  # 15% savings
            compression_ratio=0.85,
        )

        collector.record_quality_metrics(
            quality_score=quality_score,
            accuracy_score=quality_score - 0.05,
            relevance_score=quality_score + 0.05,
            confidence_score=0.88,
        )

        collector.record_performance(
            latency_ms=latency_ms,
            success=success,
            throughput_rps=10.0,
        )

        collector.record_routing(
            model=model,
            confidence=0.90,
            success=success,
            is_fallback=not success,
            routing_latency_ms=5.0,
        )

        # Print progress
        if (i + 1) % 25 == 0:
            print(f"   Processed {i + 1}/100 requests...")

    # Generate comprehensive report
    print("\n2. Comprehensive Metrics Report:")
    summary = collector.get_summary()

    print(f"\n   Token Usage & Cost:")
    token_usage = summary["token_usage"]
    print(f"   - Total requests: {token_usage['total_requests']}")
    print(f"   - Input tokens: {token_usage['total_input_tokens']:,}")
    print(f"   - Output tokens: {token_usage['total_output_tokens']:,}")
    print(f"   - Token savings: {token_usage['token_savings_pct']:.1f}%")
    print(f"   - Cost saved: ${token_usage['cost_saved_usd']:.2f}")
    print(f"   - Total cost: ${token_usage['total_cost_usd']:.2f}")

    print(f"\n   Model Breakdown:")
    for model, counts in token_usage["model_breakdown"].items():
        print(f"   - {model}:")
        print(f"     Input: {counts['input']:,} tokens")
        print(f"     Output: {counts['output']:,} tokens")

    print(f"\n   Quality Metrics:")
    quality = summary["quality"]
    print(f"   - Average quality: {quality['average_quality']:.2%}")
    print(f"   - Quality improvement: {quality['quality_improvement_pct']:.1f}%")
    print(f"   - Confidence: {quality['average_confidence']:.2%}")
    print(f"   - Measurements: {quality['total_measurements']}")

    print(f"\n   Performance:")
    perf = summary["performance"]
    print(f"   - Total requests: {perf['total_requests']}")
    print(f"   - Success rate: {perf['success_rate_pct']:.1f}%")
    print(f"   - Average latency: {perf['average_latency_ms']:.1f}ms")
    print(f"   - P50 latency: {perf['p50_latency_ms']:.1f}ms")
    print(f"   - P95 latency: {perf['p95_latency_ms']:.1f}ms")
    print(f"   - P99 latency: {perf['p99_latency_ms']:.1f}ms")

    print(f"\n   Routing:")
    routing = summary["routing"]
    print(f"   - Total routes: {routing['total_routes']}")
    print(f"   - Success rate: {routing['success_rate_pct']:.1f}%")
    print(f"   - Fallback rate: {routing['fallback_rate_pct']:.1f}%")
    print(f"   - Average confidence: {routing['average_confidence']:.2%}")
    print(f"   - Routing latency: {routing['average_routing_latency_ms']:.1f}ms")

    # Export to backends
    print("\n3. Exporting to backends...")
    metrics = collector.export_metrics()
    print(f"   Exported {len(metrics)} metrics")

    # Show alerts
    alerts = collector.get_alerts(limit=5)
    if alerts:
        print(f"\n4. Recent Alerts ({len(alerts)}):")
        for alert in alerts:
            print(f"   - [{alert.severity.value.upper()}] {alert.message}")
    else:
        print("\n4. No alerts detected")


# =============================================================================
# Example 7: Performance Benchmarking
# =============================================================================


def example_performance_benchmark() -> None:
    """
    Benchmark metrics collection overhead.
    """
    print("\n" + "=" * 80)
    print("Example 7: Performance Benchmarking")
    print("=" * 80)

    reset_metrics_collector()
    collector = get_metrics_collector()

    # Benchmark token usage recording
    print("\n1. Benchmarking token usage recording...")
    iterations = 10000
    start = time.perf_counter()

    for _ in range(iterations):
        collector.record_token_usage(100, 50, model="gpt-4")

    elapsed = time.perf_counter() - start
    avg_overhead_us = (elapsed / iterations) * 1_000_000

    print(f"   Iterations: {iterations:,}")
    print(f"   Total time: {elapsed:.3f}s")
    print(f"   Average overhead: {avg_overhead_us:.2f}µs ({avg_overhead_us / 1000:.3f}ms)")
    print(f"   ✓ Target: <1ms (achieved: {avg_overhead_us < 1000})")

    # Benchmark all metric types
    print("\n2. Benchmarking all metric types...")
    start = time.perf_counter()

    for _ in range(iterations):
        collector.record_token_usage(100, 50)
        collector.record_quality_metrics(quality_score=0.9)
        collector.record_performance(100.0, success=True)
        collector.record_routing("gpt-4", 0.9, success=True)

    elapsed = time.perf_counter() - start
    avg_overhead_us = (elapsed / iterations) * 1_000_000

    print(f"   Iterations: {iterations:,}")
    print(f"   Total time: {elapsed:.3f}s")
    print(f"   Average overhead: {avg_overhead_us:.2f}µs ({avg_overhead_us / 1000:.3f}ms)")


# =============================================================================
# Main Execution
# =============================================================================


async def main() -> None:
    """
    Run all examples.
    """
    # Example 1: Basic metrics
    example_basic_metrics()

    # Example 2: Multi-backend export
    await example_multi_backend()

    # Example 3: Anomaly detection
    example_anomaly_detection()

    # Example 4: Custom handlers
    example_custom_handlers()

    # Example 5: Dashboard data
    await example_dashboard_data()

    # Example 6: Real-world simulation
    await example_real_world_simulation()

    # Example 7: Performance benchmark
    example_performance_benchmark()

    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
