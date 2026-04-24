"""OpenTelemetry tracing setup for TraceRTM Python backend.

Provides distributed tracing with OTLP export to the shared Phenotype collector.
"""

import logging
import os
import threading
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode, Tracer

logger = logging.getLogger(__name__)

# Global tracer instance and init state
_tracer: Tracer | None = None
_tracing_initialized = False
_tracing_init_calls = 0
_tracing_init_lock = threading.Lock()

# Try to import exporter - will fail if not installed
if TYPE_CHECKING:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    _exporter_available = True
else:
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        _exporter_available = True
    except ImportError:
        logger.warning(
            "APM instrumentation not available: No module named 'opentelemetry.exporter'. "
            "Install with: pip install 'tracertm[observability]'",
        )
        _exporter_available = False

        # Create a stub class when exporter is not available
        class OTLPSpanExporter:
            """Stub class for type checking when exporter is not installed."""

            def __init__(self, **kwargs: object) -> None:
                pass


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
        otlp_endpoint: OTLP collector endpoint (defaults to the Phenotype gRPC collector)

    Returns:
        Configured tracer instance
    """
    global _tracer, _tracing_initialized, _tracing_init_calls

    with _tracing_init_lock:
        _tracing_init_calls += 1
        if _tracing_initialized and _tracer is not None:
            logger.warning("init_tracing called more than once; using existing tracer")
            return _tracer

        if _tracer is not None:
            _tracing_initialized = True
            return _tracer

        # Check if exporter is available
        if not _exporter_available:
            msg = (
                "Distributed tracing is enabled but OpenTelemetry exporter is not installed. "
                "Install with: pip install 'tracertm[observability]'"
            )
            raise RuntimeError(
                msg,
            )

        # Get configuration from environment with fallbacks
        environment = environment or os.getenv("TRACING_ENVIRONMENT", "development")
        otlp_endpoint = (
            otlp_endpoint
            or os.getenv("PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT")
            or "127.0.0.1:4317"
        )

        logger.info(
            "Initializing distributed tracing (service: %s, env: %s, endpoint: %s)",
            service_name,
            environment,
            otlp_endpoint,
        )

        current_provider = trace.get_tracer_provider()
        if isinstance(current_provider, TracerProvider):
            logger.info("Tracing already initialized; skipping reinitialization")
            _tracer = trace.get_tracer(__name__, service_version)
            _tracing_initialized = True
            return _tracer

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
                insecure=True,  # Use insecure for native local development
            )

            # Create tracer provider with batch span processor
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(
                BatchSpanProcessor(
                    otlp_exporter,
                    max_queue_size=2048,
                    max_export_batch_size=512,
                    schedule_delay_millis=5000,
                ),
            )

            # Set as global tracer provider
            trace.set_tracer_provider(provider)

            # Create and cache tracer
            _tracer = trace.get_tracer(__name__, service_version)
            _tracing_initialized = True

            logger.info("✅ Distributed tracing initialized successfully")
        except Exception as e:
            msg = f"Failed to initialize tracing: {e}"
            raise RuntimeError(msg) from e
        else:
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
) -> Callable[..., Any]:
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

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def sync_wrapper(*args: object, **kwargs: object) -> object:
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
                except Exception as e:
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
                else:
                    return result

        @wraps(func)
        async def async_wrapper(*args: object, **kwargs: object) -> object:
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
                except Exception as e:
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
                else:
                    return result

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


__all__ = ["get_tracer", "init_tracing", "trace_method"]
