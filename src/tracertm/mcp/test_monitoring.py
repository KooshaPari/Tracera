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
import contextlib
import time
from typing import TYPE_CHECKING, ClassVar, Never, cast

if TYPE_CHECKING:
    from fastmcp.server.middleware import MiddlewareContext


async def test_metrics() -> None:
    """Test Prometheus metrics collection."""
    from tracertm.mcp.metrics import (
        MetricsExporter,
        MetricsMiddleware,
    )

    # Create middleware
    middleware = MetricsMiddleware(track_payload_size=True)

    # Simulate tool call context
    class MockContext:
        async def next(self) -> None:
            await asyncio.sleep(0.1)  # Simulate work

    ctx = MockContext()

    # Test successful call (cast: mock context satisfies MiddlewareContext protocol)
    await middleware.on_tool_call(cast("MiddlewareContext", ctx), "test_tool", {"arg1": "value1"})

    # Test failed call
    class FailContext:
        async def next(self) -> Never:
            msg = "Test error"
            raise ValueError(msg)

    fail_ctx = FailContext()

    try:
        await middleware.on_tool_call(cast("MiddlewareContext", fail_ctx), "test_tool", {"arg1": "value1"})
    except ValueError:
        pass  # Expected

    # Export metrics
    metrics = MetricsExporter.export_metrics_text()
    for line in metrics.split("\n")[:20]:
        if line and not line.startswith("#"):
            pass


async def test_telemetry() -> None:
    """Test OpenTelemetry tracing."""
    from tracertm.mcp.telemetry import TelemetryMiddleware

    # Create middleware
    middleware = TelemetryMiddleware()

    # Simulate tool call
    class MockContext:
        auth: ClassVar[dict] = {"claims": {"sub": "test-user", "client_id": "test-client"}}

        async def next(self) -> None:
            await asyncio.sleep(0.05)

    ctx = MockContext()

    # Test successful trace (cast: mock context satisfies MiddlewareContext protocol)
    await middleware.on_tool_call(cast("MiddlewareContext", ctx), "create_project", {"name": "TestProject"})

    # Test failed trace
    class FailContext(MockContext):
        async def next(self) -> Never:
            msg = "Test trace error"
            raise RuntimeError(msg)

    fail_ctx = FailContext()

    try:
        await middleware.on_tool_call(cast("MiddlewareContext", fail_ctx), "query_items", {"query": "test"})
    except RuntimeError:
        pass  # Expected


async def test_performance_monitoring() -> None:
    """Test performance monitoring middleware."""
    from tracertm.mcp.telemetry import PerformanceMonitoringMiddleware

    # Create middleware with low thresholds for testing
    middleware = PerformanceMonitoringMiddleware(
        slow_threshold_seconds=0.05,
        very_slow_threshold_seconds=0.15,
    )

    # Test fast call
    class FastContext:
        async def next(self) -> None:
            await asyncio.sleep(0.01)

    await middleware.on_tool_call(cast("MiddlewareContext", FastContext()), "fast_tool", {})

    # Test slow call
    class SlowContext:
        async def next(self) -> None:
            await asyncio.sleep(0.08)

    await middleware.on_tool_call(cast("MiddlewareContext", SlowContext()), "slow_tool", {})

    # Test very slow call
    class VerySlowContext:
        async def next(self) -> None:
            await asyncio.sleep(0.2)

    await middleware.on_tool_call(cast("MiddlewareContext", VerySlowContext()), "very_slow_tool", {})

    # Get statistics
    middleware.get_statistics()


def test_error_enhancement() -> None:
    """Test error enhancement and LLM-friendly messages."""
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
        if error_dict.get("context"):
            pass


def test_structured_logging() -> None:
    """Test structured logging configuration."""
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


def test_metrics_endpoint() -> None:
    """Test metrics HTTP endpoint."""
    import requests

    from tracertm.mcp.metrics_endpoint import MetricsServer

    # Start server
    server = MetricsServer(host="127.0.0.1", port=19090)
    try:
        server.start()
        time.sleep(0.5)  # Let server start

        # Test health endpoint
        response = requests.get("http://127.0.0.1:19090/health", timeout=2)

        # Test metrics endpoint
        response = requests.get("http://127.0.0.1:19090/metrics", timeout=2)

        lines = response.text.split("\n")[:10]
        for line in lines:
            if line:
                pass

    except Exception:
        pass

    finally:
        server.stop()


async def main() -> None:
    """Run all monitoring tests."""
    # Run tests
    await test_metrics()
    await test_telemetry()
    await test_performance_monitoring()
    test_error_enhancement()
    test_structured_logging()

    # Test metrics endpoint (requires requests)
    with contextlib.suppress(ImportError):
        test_metrics_endpoint()


if __name__ == "__main__":
    asyncio.run(main())
