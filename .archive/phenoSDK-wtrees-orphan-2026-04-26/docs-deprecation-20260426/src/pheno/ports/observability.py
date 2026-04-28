"""
Observability ports - interfaces for telemetry extensibility.

This module defines the contracts (ports) for observability infrastructure,
allowing different implementations (adapters) to be plugged in.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class LogLevel(Enum):
    """Enumerated severity levels for structured logging.

    Values align with conventional logging frameworks so adapters can map them directly
    to backend-specific log levels.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Rich log record exchanged between application code and logging adapters.

    Attributes capture the minimum viable data for downstream aggregation while allowing
    optional service and timestamp hints.
    """

    level: LogLevel
    message: str
    context: dict[str, Any]
    timestamp: float | None = None
    service: str | None = None


# Logging Port
class Logger(Protocol):
    """Logging port describing the minimum contract expected by the application.

    Implementations may forward records to stdout, cloud logging platforms, or
    observability pipelines.
    """

    def log(self, level: LogLevel, message: str, **context) -> None:
        """Emit a log entry with explicit severity.

        Args:
            level: Structured log level value.
            message: Human-readable log message.
            **context: Arbitrary key/value pairs providing structured context.
        """
        ...

    def debug(self, message: str, **context) -> None:
        """Emit a ``DEBUG`` severity log message.

        Args:
            message: Log message body.
            **context: Structured metadata accompanying the log.
        """
        ...

    def info(self, message: str, **context) -> None:
        """Emit an ``INFO`` severity log message.

        Args:
            message: Log message body.
            **context: Structured metadata accompanying the log.
        """
        ...

    def warning(self, message: str, **context) -> None:
        """Emit a ``WARNING`` severity log message.

        Args:
            message: Log message body.
            **context: Structured metadata accompanying the log.
        """
        ...

    def error(self, message: str, **context) -> None:
        """Emit an ``ERROR`` severity log message.

        Args:
            message: Log message body.
            **context: Structured metadata accompanying the log.
        """
        ...

    def critical(self, message: str, **context) -> None:
        """Emit a ``CRITICAL`` severity log message.

        Args:
            message: Log message body.
            **context: Structured metadata accompanying the log.
        """
        ...


class LoggerFactory(Protocol):
    """Factory interface responsible for constructing configured loggers.

    Allows adapters to supply pre-configured logger instances with shared transports,
    filters, or formatters.
    """

    def get_logger(self, name: str, **config) -> Logger:
        """Create and configure a logger with the given name.

        Args:
            name: Logical logger name, often the module or service identifier.
            **config: Implementation-specific configuration overrides.

        Returns:
            Logger instance ready for immediate use.
        """
        ...


# Tracing Port
@dataclass
class SpanContext:
    """Lightweight context carriers used to propagate tracing metadata.

    Fields follow OpenTelemetry conventions so adapters can interoperate with popular
    tracing backends.
    """

    trace_id: str
    span_id: str
    parent_span_id: str | None = None


class Span(Protocol):
    """Span operations defining the tracing surface expected by the SDK.

    Implementers map these calls to underlying tracing libraries.
    Notes:
        Spans created via this interface should be context-manageable to align
        with common tracing DSLs.
    """

    def set_attribute(self, key: str, value: str | float | bool) -> None:
        """Attach a scalar attribute to the span.

        Args:
            key: Attribute name.
            value: Attribute value accepted by tracing backends.
        """
        ...

    def set_attributes(self, attributes: dict[str, str | int | float | bool]) -> None:
        """Attach multiple attributes to the span in a single call.

        Args:
            attributes: Mapping of attribute names to values.
        """
        ...

    def add_event(
        self, name: str, attributes: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Add an event annotation to the span timeline.

        Args:
            name: Event name.
            attributes: Optional structured metadata for the event.
        """
        ...

    def record_exception(
        self,
        exception: Exception,
        attributes: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Record an exception, optionally annotating additional context.

        Args:
            exception: Exception instance to record.
            attributes: Optional structured metadata describing the error.
        """
        ...

    def end(self) -> None:
        """Finalise the span, signalling completion to the tracing backend.

        Returns:
            None.
        """
        ...


class Tracer(Protocol):
    """Entry point for creating and managing spans within a trace.

    Notes:
        Tracers should be safe to share across threads and async tasks.
    """

    def start_span(self, name: str, context: SpanContext | None = None, **attributes) -> Span:
        """Start a new span as a child of ``context`` if supplied.

        Args:
            name: Human-readable span name.
            context: Optional parent span context.
            **attributes: Attributes applied to the span on creation.

        Returns:
            Active span handle.
        """
        ...

    def get_current_span(self) -> Span | None:
        """Retrieve the span currently bound to execution context, if any.

        Returns:
            Active span or ``None`` when no span is bound.
        """
        ...


class TracerProvider(Protocol):
    """Provider interface used to acquire tracer instances for subsystems.

    Notes:
        Typically implemented by OpenTelemetry or custom tracer registries.
    """

    def get_tracer(self, name: str, version: str | None = None) -> Tracer:
        """Retrieve a tracer bound to the supplied instrumentation scope.

        Args:
            name: Instrumentation library or subsystem name.
            version: Optional version string used for telemetry attribution.

        Returns:
            Tracer implementation ready to create spans.
        """
        ...


# Metrics Port
class Counter(Protocol):
    """Counter metric interface for monotonic measurements.

    Notes:
        Counter values should never decrease and are reset only on process restarts.
    """

    def add(self, amount: float = 1, **labels) -> None:
        """Increment the counter by ``amount``.

        Args:
            amount: Amount to add to the counter.
            **labels: Dimension labels applied to the measurement.
        """
        ...

    def increment(self, **labels) -> None:
        """Convenience wrapper that increments the counter by one.

        Args:
            **labels: Dimension labels applied to the measurement.
        """
        ...


class Histogram(Protocol):
    """Histogram metric interface for distribution tracking.

    Notes:
        Histograms should aggregate values into buckets defined by the backend.
    """

    def record(self, value: float, **labels) -> None:
        """Record a measurement sample in the histogram.

        Args:
            value: Sample value.
            **labels: Dimension labels applied to the sample.
        """
        ...


class Gauge(Protocol):
    """Gauge metric interface for instantaneous measurements.

    Notes:
        Gauges can move both up and down, representing current state.
    """

    def set(self, value: float, **labels) -> None:
        """Set the gauge to a specific value.

        Args:
            value: Measurement value.
            **labels: Dimension labels applied to the measurement.
        """
        ...


class Meter(Protocol):
    """Entry point for creating metric instruments scoped to a component.

    Notes:
        Instruments created from a meter share the same resource and exporter settings.
    """

    def create_counter(self, name: str, description: str = "", unit: str = "") -> Counter:
        """Create a counter metric instrument.

        Args:
            name: Metric name.
            description: Human-readable description.
            unit: Metric unit (e.g., ``ms``).

        Returns:
            Counter instrument instance.
        """
        ...

    def create_histogram(self, name: str, description: str = "", unit: str = "") -> Histogram:
        """Create a histogram metric instrument.

        Args:
            name: Metric name.
            description: Human-readable description.
            unit: Metric unit.

        Returns:
            Histogram instrument instance.
        """
        ...

    def create_gauge(self, name: str, description: str = "", unit: str = "") -> Gauge:
        """Create a gauge metric instrument.

        Args:
            name: Metric name.
            description: Human-readable description.
            unit: Metric unit.

        Returns:
            Gauge instrument instance.
        """
        ...


class MeterProvider(Protocol):
    """Provider interface for acquiring meters for instrumentation scopes.

    Notes:
        Typically implemented by observability SDKs like OpenTelemetry.
    """

    def get_meter(self, name: str, version: str | None = None) -> Meter:
        """Retrieve a meter associated with a particular instrumentation scope.

        Args:
            name: Instrumentation scope name.
            version: Optional version string.

        Returns:
            Meter implementation ready to create metrics.
        """
        ...


# Health Check Port
class HealthCheck(Protocol):
    """Contract that individual health checks must implement.

    Health checks are typically lightweight probes executed on demand.
    Notes:
        Checks should be idempotent and inexpensive to avoid impacting services.
    """

    def name(self) -> str:
        """Return the identifier of the health check.

        Returns:
            Human-readable identifier used in reports and logs.
        """
        ...

    def check(self) -> dict[str, Any]:
        """Perform the health check.

        Returns:
            Dict containing 'status' ('healthy'/'unhealthy'), optional 'details', and 'checked_at' timestamp.
        """
        ...


class HealthChecker(Protocol):
    """Manager responsible for registering and executing health checks.

    Notes:
        Implementations may execute checks sequentially or in parallel.
    """

    def add_check(self, check: HealthCheck) -> None:
        """Register a health check with the manager.

        Args:
            check: HealthCheck implementation to add.
        """
        ...

    def remove_check(self, name: str) -> None:
        """Remove a health check by name.

        Args:
            name: Identifier of the health check to remove.
        """
        ...

    def check_all(self) -> dict[str, Any]:
        """Run all health checks.

        Returns:
            Dict with 'status' and 'checks' containing individual check results.
        """
        ...


# Alerting Port (Basic)
class Alert(Protocol):
    """Structured alert representation consumed by alerting adapters.

    Notes:
        Alerts should be immutable snapshots of the triggering condition.
    """

    @property
    def name(self) -> str:
        """Name of the alert.

        Returns:
            Human-readable identifier for the alert.
        """
        ...

    @property
    def severity(self) -> str:
        """Severity level associated with the alert (e.g., ``warning`` or ``critical``).

        Returns:
            Severity string recognised by the alerting backend.
        """
        ...

    @property
    def message(self) -> str:
        """Message content describing the alert condition.

        Returns:
            Rendered alert message.
        """
        ...


class Alerter(Protocol):
    """Port describing how alerts are sent to external notification channels.

    Notes:
        Implementations may integrate with email, chat, or incident platforms.
    """

    def send_alert(self, _alert: Alert) -> None:
        """Dispatch an alert notification.

        Args:
            _alert: Alert payload to send.
        """
        ...


# Bootstrap Port (facilitates hexagonal architecture)
class ObservabilityBootstrapper(Protocol):
    """Bootstrap interface for initialising observability subsystems.

    Implementations typically wire up logging, tracing, metrics, and health checks
    during application startup.
    """

    def setup_logging(self, config: dict[str, Any]) -> None:
        """Configure the logging subsystem using the provided configuration.

        Args:
            config: Logging configuration dictionary.
        """
        ...

    def setup_tracing(self, config: dict[str, Any]) -> None:
        """Configure tracing exporters and instrumentation.

        Args:
            config: Tracing configuration dictionary.
        """
        ...

    def setup_metrics(self, config: dict[str, Any]) -> None:
        """Configure metrics collection and exporters.

        Args:
            config: Metrics configuration dictionary.
        """
        ...

    def setup_health_checks(self, config: dict[str, Any]) -> None:
        """Register health checks based on configuration.

        Args:
            config: Health check configuration dictionary.
        """
        ...

    def add_prometheus_endpoint(self, app, path: str = "/metrics") -> None:
        """Add a Prometheus metrics endpoint to an ASGI application.

        Args:
            app: ASGI application instance.
            path: URL path hosting the metrics endpoint.
        """
        ...


__all__ = [
    # Alerting
    "Alert",
    "Alerter",
    # Metrics
    "Counter",
    "Gauge",
    # Health
    "HealthCheck",
    "HealthChecker",
    "Histogram",
    "LogEntry",
    # Enums and data classes
    "LogLevel",
    # Logging
    "Logger",
    "LoggerFactory",
    "Meter",
    "MeterProvider",
    # Bootstrap
    "ObservabilityBootstrapper",
    # Tracing
    "Span",
    "SpanContext",
    "Tracer",
    "TracerProvider",
]
