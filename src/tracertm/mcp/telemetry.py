"""OpenTelemetry instrumentation for MCP tools.

Provides distributed tracing for all MCP tool calls with:
- Automatic span creation for tool execution
- Payload size tracking
- Error tracking with stack traces
- Custom attributes for debugging
"""

from __future__ import annotations

import json
import logging
import time

from fastmcp.server.middleware import Middleware, MiddlewareContext
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)


def setup_telemetry(service_name: str = "tracertm-mcp") -> trace.Tracer:
    """Initialize OpenTelemetry with console exporter.

    Args:
        service_name: Name of the service for tracing

    Returns:
        Configured tracer instance
    """
    current_provider = trace.get_tracer_provider()
    if isinstance(current_provider, TracerProvider):
        logger.info("Tracing already initialized; using existing tracer provider")
        return trace.get_tracer(__name__)

    # Create resource with service information
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "0.2.0",
        "deployment.environment": "development",
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add console exporter for development
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    # Return tracer
    return trace.get_tracer(__name__)


# Global tracer instance
_tracer: trace.Tracer | None = None


def get_tracer() -> trace.Tracer:
    """Get or create the global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = setup_telemetry()
    return _tracer


class TelemetryMiddleware(Middleware):
    """Middleware that instruments MCP tool calls with OpenTelemetry spans."""

    def __init__(self, tracer: trace.Tracer | None = None) -> None:
        """Initialize telemetry middleware.

        Args:
            tracer: OpenTelemetry tracer (creates default if None)
        """
        self.tracer = tracer or get_tracer()

    def _get_payload_size(self, obj: object) -> int:
        """Calculate approximate size of payload in bytes.

        Args:
            obj: Object to measure

        Returns:
            Size in bytes
        """
        try:
            return len(json.dumps(obj, default=str).encode("utf-8"))
        except Exception:
            return 0

    def _sanitize_arguments(self, arguments: dict[str, object]) -> dict[str, object]:
        """Remove sensitive data from arguments for logging.

        Args:
            arguments: Raw arguments

        Returns:
            Sanitized arguments
        """
        sensitive_keys = {
            "password",
            "secret",
            "token",
            "api_key",
            "auth",
            "authorization",
            "credential",
            "private_key",
        }

        sanitized: dict[str, object] = {}
        for key, value in arguments.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        tool_name: str,
        arguments: dict[str, object],
    ) -> None:
        """Instrument tool call with OpenTelemetry span.

        Args:
            ctx: Middleware context
            tool_name: Name of the tool being called
            arguments: Tool arguments
        """
        start_time = time.time()

        # Create span for this tool call
        with self.tracer.start_as_current_span(
            f"mcp.tool.{tool_name}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            try:
                # Add standard attributes
                span.set_attribute("mcp.tool.name", tool_name)
                span.set_attribute("mcp.tool.start_time", start_time)

                # Add argument count and payload size
                sanitized_args = self._sanitize_arguments(arguments)
                span.set_attribute("mcp.tool.arg_count", len(arguments))
                span.set_attribute("mcp.tool.payload_size_bytes", self._get_payload_size(arguments))

                # Add sanitized arguments as event
                span.add_event(
                    "tool.arguments",
                    attributes={"arguments": json.dumps(sanitized_args, default=str)[:1000]},
                )

                # Add auth context if available
                auth = getattr(ctx, "auth", None)
                if isinstance(auth, dict):
                    claims = auth.get("claims", {}) or {}
                    span.set_attribute("mcp.auth.subject", claims.get("sub", "unknown"))
                    span.set_attribute("mcp.auth.client_id", claims.get("client_id", "unknown"))

                # Execute tool
                next_fn = getattr(ctx, "next", None)
                if callable(next_fn):
                    await next_fn()

                # Mark success
                elapsed = time.time() - start_time
                span.set_attribute("mcp.tool.duration_seconds", elapsed)
                span.set_attribute("mcp.tool.success", True)
                span.set_status(Status(StatusCode.OK))

                logger.debug("[TELEMETRY] %s completed in %.3fs", tool_name, elapsed)

            except Exception as e:
                # Mark failure and capture error
                elapsed = time.time() - start_time
                span.set_attribute("mcp.tool.duration_seconds", elapsed)
                span.set_attribute("mcp.tool.success", False)
                span.set_attribute("mcp.tool.error.type", type(e).__name__)
                span.set_attribute("mcp.tool.error.message", str(e))

                # Add exception event
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

                logger.exception("[TELEMETRY] %s failed after %.3fs", tool_name, elapsed)

                # Re-raise to allow other middleware to handle
                raise


class PerformanceMonitoringMiddleware(Middleware):
    """Middleware that tracks performance metrics and warns about slow calls."""

    def __init__(
        self,
        slow_threshold_seconds: float = 5.0,
        very_slow_threshold_seconds: float = 30.0,
    ) -> None:
        """Initialize performance monitoring.

        Args:
            slow_threshold_seconds: Threshold for slow call warning
            very_slow_threshold_seconds: Threshold for very slow call alert
        """
        self.slow_threshold = slow_threshold_seconds
        self.very_slow_threshold = very_slow_threshold_seconds
        self._call_history: list[dict[str, object]] = []

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        tool_name: str,
        _arguments: dict[str, object],
    ) -> None:
        """Monitor tool call performance.

        Args:
            ctx: Middleware context
            tool_name: Name of the tool
            arguments: Tool arguments
        """
        start_time = time.time()

        try:
            next_fn = getattr(ctx, "next", None)
            if callable(next_fn):
                await next_fn()
            elapsed = time.time() - start_time

            # Record call
            self._call_history.append({
                "tool": tool_name,
                "duration": elapsed,
                "timestamp": start_time,
                "success": True,
            })

            # Warn about slow calls
            if elapsed >= self.very_slow_threshold:
                logger.warning(
                    "[PERFORMANCE] VERY SLOW: %s took %.2fs (threshold: %ss)",
                    tool_name,
                    elapsed,
                    self.very_slow_threshold,
                )
            elif elapsed >= self.slow_threshold:
                logger.info(
                    "[PERFORMANCE] Slow: %s took %.2fs (threshold: %ss)", tool_name, elapsed, self.slow_threshold
                )

        except Exception as e:
            elapsed = time.time() - start_time

            # Record failed call
            self._call_history.append({
                "tool": tool_name,
                "duration": elapsed,
                "timestamp": start_time,
                "success": False,
                "error": str(e),
            })

            raise

    def get_statistics(self) -> dict[str, object]:
        """Get performance statistics.

        Returns:
            Statistics about tool call performance
        """
        if not self._call_history:
            return {"calls": 0}

        durations = [
            float(call["duration"]) if isinstance(call["duration"], (int, float)) else 0.0
            for call in self._call_history
        ]
        successes = [call for call in self._call_history if call.get("success")]
        failures = [call for call in self._call_history if not call.get("success")]

        return {
            "total_calls": len(self._call_history),
            "successful_calls": len(successes),
            "failed_calls": len(failures),
            "avg_duration_seconds": sum(durations) / len(durations) if durations else 0.0,
            "min_duration_seconds": min(durations) if durations else 0.0,
            "max_duration_seconds": max(durations) if durations else 0.0,
            "slow_calls": len([d for d in durations if d >= self.slow_threshold]),
            "very_slow_calls": len([d for d in durations if d >= self.very_slow_threshold]),
        }


__all__ = [
    "PerformanceMonitoringMiddleware",
    "TelemetryMiddleware",
    "get_tracer",
    "setup_telemetry",
]
