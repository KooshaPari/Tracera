"""Prometheus metrics for MCP tools.

Provides comprehensive metrics collection:
- Tool execution duration histograms
- Tool call counters
- Error counters by type
- Payload size tracking
- Rate limit tracking
"""

from __future__ import annotations

import logging
import time

from fastmcp.server.middleware import Middleware, MiddlewareContext
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logger = logging.getLogger(__name__)


# Create a custom registry for MCP metrics
mcp_registry = CollectorRegistry()


# Tool execution duration histogram
tool_duration_seconds = Histogram(
    "mcp_tool_duration_seconds",
    "Duration of MCP tool execution in seconds",
    labelnames=["tool_name", "status"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
    registry=mcp_registry,
)


# Tool call counter
tool_calls_total = Counter(
    "mcp_tool_calls_total",
    "Total number of MCP tool calls",
    labelnames=["tool_name", "status"],
    registry=mcp_registry,
)


# Tool error counter by type
tool_errors_total = Counter(
    "mcp_tool_errors_total",
    "Total number of MCP tool errors by error type",
    labelnames=["tool_name", "error_type"],
    registry=mcp_registry,
)


# Tool payload size histogram
tool_payload_size_bytes = Histogram(
    "mcp_tool_payload_size_bytes",
    "Size of tool request payload in bytes",
    labelnames=["tool_name"],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
    registry=mcp_registry,
)


# Tool response size histogram
tool_response_size_bytes = Histogram(
    "mcp_tool_response_size_bytes",
    "Size of tool response payload in bytes",
    labelnames=["tool_name"],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
    registry=mcp_registry,
)


# Active tool calls gauge
active_tool_calls = Gauge(
    "mcp_active_tool_calls",
    "Number of currently active tool calls",
    labelnames=["tool_name"],
    registry=mcp_registry,
)


# Rate limit hits counter
rate_limit_hits_total = Counter(
    "mcp_rate_limit_hits_total",
    "Total number of rate limit violations",
    labelnames=["user_key", "limit_type"],
    registry=mcp_registry,
)


# Auth failures counter
auth_failures_total = Counter(
    "mcp_auth_failures_total",
    "Total number of authentication failures",
    labelnames=["failure_type"],
    registry=mcp_registry,
)


class MetricsMiddleware(Middleware):
    """Middleware that collects Prometheus metrics for all MCP tool calls."""

    def __init__(self, track_payload_size: bool = True) -> None:
        """Initialize metrics middleware.

        Args:
            track_payload_size: Whether to track payload sizes (can be expensive)
        """
        self.track_payload_size = track_payload_size

    def _calculate_size(self, obj: object) -> int:
        """Calculate approximate size of object in bytes.

        Args:
            obj: Object to measure

        Returns:
            Size in bytes
        """
        if not self.track_payload_size:
            return 0

        try:
            import json

            return len(json.dumps(obj, default=str).encode("utf-8"))
        except Exception:
            return 0

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        tool_name: str,
        arguments: dict[str, object],
    ) -> None:
        """Collect metrics for tool call.

        Args:
            ctx: Middleware context
            tool_name: Name of the tool
            arguments: Tool arguments
        """
        start_time = time.time()

        # Track active calls
        active_tool_calls.labels(tool_name=tool_name).inc()

        # Track payload size
        if self.track_payload_size:
            payload_size = self._calculate_size(arguments)
            tool_payload_size_bytes.labels(tool_name=tool_name).observe(payload_size)

        try:
            # Execute tool
            next_fn = getattr(ctx, "next", None)
            if next_fn is not None and callable(next_fn):
                await next_fn()

            # Track success metrics
            elapsed = time.time() - start_time
            tool_duration_seconds.labels(tool_name=tool_name, status="success").observe(elapsed)
            tool_calls_total.labels(tool_name=tool_name, status="success").inc()

            logger.debug("[METRICS] %s succeeded in %.3fs", tool_name, elapsed)

        except Exception as e:
            # Track failure metrics
            elapsed = time.time() - start_time
            error_type = type(e).__name__

            tool_duration_seconds.labels(tool_name=tool_name, status="error").observe(elapsed)
            tool_calls_total.labels(tool_name=tool_name, status="error").inc()
            tool_errors_total.labels(tool_name=tool_name, error_type=error_type).inc()

            logger.debug("[METRICS] %s failed in %.3fs with %s", tool_name, elapsed, error_type)

            # Re-raise
            raise

        finally:
            # Decrement active calls
            active_tool_calls.labels(tool_name=tool_name).dec()


class MetricsExporter:
    """Utility for exporting Prometheus metrics."""

    @staticmethod
    def export_metrics(registry: CollectorRegistry = mcp_registry) -> bytes:
        """Export metrics in Prometheus format.

        Args:
            registry: Registry to export from

        Returns:
            Metrics in Prometheus text format
        """
        return generate_latest(registry)

    @staticmethod
    def export_metrics_text(registry: CollectorRegistry = mcp_registry) -> str:
        """Export metrics as text string.

        Args:
            registry: Registry to export from

        Returns:
            Metrics as UTF-8 string
        """
        return generate_latest(registry).decode("utf-8")


def track_rate_limit_hit(user_key: str, limit_type: str) -> None:
    """Track a rate limit violation.

    Args:
        user_key: User identifier
        limit_type: Type of limit (per_minute, per_hour)
    """
    rate_limit_hits_total.labels(user_key=user_key, limit_type=limit_type).inc()


def track_auth_failure(failure_type: str) -> None:
    """Track an authentication failure.

    Args:
        failure_type: Type of failure (expired_token, missing_scope, etc.)
    """
    auth_failures_total.labels(failure_type=failure_type).inc()


__all__ = [
    "MetricsExporter",
    "MetricsMiddleware",
    "active_tool_calls",
    "auth_failures_total",
    "mcp_registry",
    "rate_limit_hits_total",
    "tool_calls_total",
    "tool_duration_seconds",
    "tool_errors_total",
    "tool_payload_size_bytes",
    "tool_response_size_bytes",
    "track_auth_failure",
    "track_rate_limit_hit",
]
