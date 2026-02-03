"""OpenTelemetry tracing setup for TraceRTM Python backend.

Provides distributed tracing with OTLP export to Jaeger/Tempo.
"""

import logging
import os
from collections.abc import Callable
from functools import wraps
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore[import-untyped]
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode, Tracer

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Tracer | None = None


def init_tracing(
    service_name: str = "tracertm-python-backend",
    service_version: str = "1.0.0",
    environment: str | None = None,
    otlp_endpoint: str | None = None,
) -> Tracer:
    """Initialize OpenTelemetry tracing with OTLP exporter.

    Args:
        service_name: Name of the service for tracing
        service_version: Version of the service
        environment: Deployment environment (development, staging, production)
        otlp_endpoint: OTLP collector endpoint (defaults to localhost:4317)

    Returns:
        Configured tracer instance
    """
    global _tracer

    # Get configuration from environment with fallbacks
    environment = environment or os.getenv("TRACING_ENVIRONMENT", "development")
    otlp_endpoint = otlp_endpoint or os.getenv("OTLP_ENDPOINT", "localhost:4317")

    logger.info(
        f"Initializing distributed tracing (service: {service_name}, env: {environment}, endpoint: {otlp_endpoint})"
    )

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: service_name,
        "service.version": service_version,
        "deployment.environment": environment,
        "library.language": "python",
    })

    # Create OTLP exporter
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True,  # Use insecure for local development
        )

        # Create tracer provider with batch span processor
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=2048,
                max_export_batch_size=512,
                schedule_delay_millis=5000,
            )
        )

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Create and cache tracer
        _tracer = trace.get_tracer(__name__, service_version)

        logger.info("✅ Distributed tracing initialized successfully")
        return _tracer

    except Exception as e:
        logger.error(f"Failed to initialize tracing: {e}")
        # Return a no-op tracer
        _tracer = trace.get_tracer(__name__)
        return _tracer


def get_tracer() -> Tracer:
    """Get the global tracer instance.

    Returns:
        Tracer instance (initialized or no-op)
    """
    global _tracer
    if _tracer is None:
        _tracer = init_tracing()
    return _tracer


def trace_method(
    span_name: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Callable:
    """Decorator to add tracing to a method.

    Args:
        span_name: Custom span name (defaults to function name)
        attributes: Additional span attributes

    Returns:
        Decorated function

    Example:
        >>> @trace_method(span_name="custom.operation", attributes={"key": "value"})
        ... def my_function(arg1, arg2):
        ...     return arg1 + arg2
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            name = span_name or f"{getattr(func, '__module__', '')}.{getattr(func, '__qualname__', repr(func))}"

            with tracer.start_as_current_span(
                name,
                kind=trace.SpanKind.INTERNAL,
            ) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("function.name", getattr(func, "__name__", ""))
                span.set_attribute("function.module", getattr(func, "__module__", ""))

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            name = span_name or f"{getattr(func, '__module__', '')}.{getattr(func, '__qualname__', repr(func))}"

            with tracer.start_as_current_span(
                name,
                kind=trace.SpanKind.INTERNAL,
            ) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("function.name", getattr(func, "__name__", ""))
                span.set_attribute("function.module", getattr(func, "__module__", ""))

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


__all__ = ["get_tracer", "init_tracing", "trace_method"]
