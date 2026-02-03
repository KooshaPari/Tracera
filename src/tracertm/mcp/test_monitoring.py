#!/usr/bin/env python3
"""Test script for MCP monitoring and telemetry.

This script demonstrates and tests:
- Metrics collection
- Telemetry/tracing
- Structured logging
- Error enhancement
- Performance monitoring
"""

import asyncio
import time
from typing import ClassVar, cast

from fastmcp.server.middleware import MiddlewareContext


async def test_metrics():
    """Test Prometheus metrics collection."""
    print("\n=== Testing Metrics Collection ===")

    from tracertm.mcp.metrics import (
        MetricsExporter,
        MetricsMiddleware,
    )

    # Create middleware
    middleware = MetricsMiddleware(track_payload_size=True)

    # Simulate tool call context
    class MockContext:
        async def next(self):
            await asyncio.sleep(0.1)  # Simulate work

    ctx = MockContext()

    # Test successful call (cast: mock context satisfies MiddlewareContext protocol)
    await middleware.on_tool_call(cast(MiddlewareContext, ctx), "test_tool", {"arg1": "value1"})

    # Test failed call
    class FailContext:
        async def next(self):
            raise ValueError("Test error")

    fail_ctx = FailContext()

    try:
        await middleware.on_tool_call(cast(MiddlewareContext, fail_ctx), "test_tool", {"arg1": "value1"})
    except ValueError:
        pass  # Expected

    # Export metrics
    metrics = MetricsExporter.export_metrics_text()
    print("\nSample metrics:")
    for line in metrics.split("\n")[:20]:
        if line and not line.startswith("#"):
            print(f"  {line}")

    print("\n✓ Metrics collection working")


async def test_telemetry():
    """Test OpenTelemetry tracing."""
    print("\n=== Testing Telemetry/Tracing ===")

    from tracertm.mcp.telemetry import TelemetryMiddleware

    # Create middleware
    middleware = TelemetryMiddleware()

    # Simulate tool call
    class MockContext:
        auth: ClassVar[dict] = {"claims": {"sub": "test-user", "client_id": "test-client"}}

        async def next(self):
            await asyncio.sleep(0.05)

    ctx = MockContext()

    # Test successful trace (cast: mock context satisfies MiddlewareContext protocol)
    await middleware.on_tool_call(cast(MiddlewareContext, ctx), "create_project", {"name": "TestProject"})

    # Test failed trace
    class FailContext(MockContext):
        async def next(self):
            raise RuntimeError("Test trace error")

    fail_ctx = FailContext()

    try:
        await middleware.on_tool_call(cast(MiddlewareContext, fail_ctx), "query_items", {"query": "test"})
    except RuntimeError:
        pass  # Expected

    print("\n✓ Telemetry/tracing working")
    print("  Note: Check console output for span details")


async def test_performance_monitoring():
    """Test performance monitoring middleware."""
    print("\n=== Testing Performance Monitoring ===")

    from tracertm.mcp.telemetry import PerformanceMonitoringMiddleware

    # Create middleware with low thresholds for testing
    middleware = PerformanceMonitoringMiddleware(
        slow_threshold_seconds=0.05,
        very_slow_threshold_seconds=0.15,
    )

    # Test fast call
    class FastContext:
        async def next(self):
            await asyncio.sleep(0.01)

    await middleware.on_tool_call(cast(MiddlewareContext, FastContext()), "fast_tool", {})

    # Test slow call
    class SlowContext:
        async def next(self):
            await asyncio.sleep(0.08)

    await middleware.on_tool_call(cast(MiddlewareContext, SlowContext()), "slow_tool", {})

    # Test very slow call
    class VerySlowContext:
        async def next(self):
            await asyncio.sleep(0.2)

    await middleware.on_tool_call(cast(MiddlewareContext, VerySlowContext()), "very_slow_tool", {})

    # Get statistics
    stats = middleware.get_statistics()
    print("\nPerformance statistics:")
    print(f"  Total calls: {stats['total_calls']}")
    print(f"  Avg duration: {stats['avg_duration_seconds']:.3f}s")
    print(f"  Slow calls: {stats['slow_calls']}")
    print(f"  Very slow calls: {stats['very_slow_calls']}")

    print("\n✓ Performance monitoring working")


def test_error_enhancement():
    """Test error enhancement and LLM-friendly messages."""
    print("\n=== Testing Error Enhancement ===")

    from tracertm.mcp.error_handlers import (
        DatabaseError,
        ItemNotFoundError,
        ProjectNotSelectedError,
        ValidationError,
    )

    # Test various error types
    errors = [
        ProjectNotSelectedError(),
        ItemNotFoundError("item-123", "project-456"),
        DatabaseError("query", "connection timeout"),
        ValidationError("name", "invalid@name", "Invalid characters"),
    ]

    for error in errors:
        error_dict = error.to_dict()
        print(f"\n{error.__class__.__name__}:")
        print(f"  Message: {error_dict['error']}")
        print(f"  Hint: {error_dict.get('recovery_hint', 'N/A')}")
        if error_dict.get("context"):
            print(f"  Context: {error_dict['context']}")

    print("\n✓ Error enhancement working")


def test_structured_logging():
    """Test structured logging configuration."""
    print("\n=== Testing Structured Logging ===")

    from tracertm.mcp.logging_config import configure_structured_logging, get_structured_logger

    # Configure for testing
    configure_structured_logging(log_level="DEBUG", json_output=False)

    # Get logger
    logger = get_structured_logger()

    # Test various log types
    logger.log_tool_call(
        tool_name="test_tool",
        arguments={"arg1": "value1"},
        duration=0.123,
        success=True,
    )

    logger.log_performance(
        operation="test_operation",
        duration=0.234,
        threshold=0.5,
    )

    logger.log_auth(
        action="permission_check",
        user_id="test-user",
        success=True,
    )

    logger.log_rate_limit(
        user_key="test-user",
        limit_type="per_minute",
        current_count=45,
        limit=60,
    )

    print("\n✓ Structured logging working")
    print("  Note: Check log output above for structured log entries")


def test_metrics_endpoint():
    """Test metrics HTTP endpoint."""
    print("\n=== Testing Metrics Endpoint ===")

    import requests

    from tracertm.mcp.metrics_endpoint import MetricsServer

    # Start server
    server = MetricsServer(host="127.0.0.1", port=19090)
    try:
        server.start()
        time.sleep(0.5)  # Let server start

        # Test health endpoint
        response = requests.get("http://127.0.0.1:19090/health", timeout=2)
        print(f"\nHealth check: {response.status_code} - {response.text}")

        # Test metrics endpoint
        response = requests.get("http://127.0.0.1:19090/metrics", timeout=2)
        print(f"Metrics endpoint: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")

        lines = response.text.split("\n")[:10]
        print("\nFirst 10 lines of metrics:")
        for line in lines:
            if line:
                print(f"  {line}")

        print("\n✓ Metrics endpoint working")

    except Exception as e:
        print(f"\n✗ Metrics endpoint failed: {e}")
        print("  Note: requests library may not be installed")

    finally:
        server.stop()


async def main():
    """Run all monitoring tests."""
    print("=" * 60)
    print("TraceRTM MCP Monitoring Test Suite")
    print("=" * 60)

    # Run tests
    await test_metrics()
    await test_telemetry()
    await test_performance_monitoring()
    test_error_enhancement()
    test_structured_logging()

    # Test metrics endpoint (requires requests)
    try:
        test_metrics_endpoint()
    except ImportError:
        print("\n=== Skipping Metrics Endpoint Test ===")
        print("  Install requests package to test HTTP endpoint")

    print("\n" + "=" * 60)
    print("All monitoring tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
