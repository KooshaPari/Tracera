"""Core types and exceptions for pheno-logging.

This module defines the fundamental types and exceptions used throughout the logging and
monitoring system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """
    Log levels in order of severity.
    """

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_string(cls, level: str) -> "LogLevel":
        """
        Create LogLevel from string.
        """
        return cls[level.upper()]


@dataclass
class LogRecord:
    """
    Structured log record.
    """

    level: LogLevel
    message: str
    timestamp: datetime
    logger_name: str
    context: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None
    module: str | None = None
    function: str | None = None
    line_number: int | None = None
    exception: Exception | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.
        """
        return {
            "level": self.level.name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "logger_name": self.logger_name,
            "context": self.context,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "module": self.module,
            "function": self.function,
            "line_number": self.line_number,
            "exception": str(self.exception) if self.exception else None,
            "extra": self.extra,
        }


@dataclass
class LogContext:
    """
    Logging context for structured logging.
    """

    correlation_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None
    session_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    custom: dict[str, Any] = field(default_factory=dict)

    def merge(self, other: "LogContext") -> "LogContext":
        """
        Merge with another context.
        """
        return LogContext(
            correlation_id=other.correlation_id or self.correlation_id,
            user_id=other.user_id or self.user_id,
            request_id=other.request_id or self.request_id,
            session_id=other.session_id or self.session_id,
            trace_id=other.trace_id or self.trace_id,
            span_id=other.span_id or self.span_id,
            custom={**self.custom, **other.custom},
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        result = {}
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.request_id:
            result["request_id"] = self.request_id
        if self.session_id:
            result["session_id"] = self.session_id
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.span_id:
            result["span_id"] = self.span_id
        result.update(self.custom)
        return result


@dataclass
class MetricPoint:
    """
    A single metric data point.
    """

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class HealthStatus:
    """
    Health check status.
    """

    healthy: bool
    message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# Exception hierarchy
class LoggingError(Exception):
    """
    Base exception for logging errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(LoggingError):
    """
    Raised when there's a logging configuration error.
    """


class HandlerError(LoggingError):
    """
    Raised when a log handler error occurs.
    """


class FormatterError(LoggingError):
    """
    Raised when a log formatter error occurs.
    """


class MonitorError(LoggingError):
    """
    Raised when a monitoring error occurs.
    """


class MetricsError(LoggingError):
    """
    Raised when a metrics error occurs.
    """


class HealthCheckError(LoggingError):
    """
    Raised when a health check error occurs.
    """
