"""Core interfaces for pheno-logging.

This module defines the abstract base classes that all logging implementations must
follow, ensuring consistency across the system.
"""

from abc import ABC, abstractmethod
from typing import Any

from .types import (
    HealthStatus,
    LogContext,
    LogLevel,
    LogRecord,
    MetricPoint,
)


class Logger(ABC):
    """
    Base interface for loggers.
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self._context: LogContext = LogContext()

    @abstractmethod
    def debug(self, message: str, **context: Any) -> None:
        """
        Log a debug message.
        """

    @abstractmethod
    def info(self, message: str, **context: Any) -> None:
        """
        Log an info message.
        """

    @abstractmethod
    def warning(self, message: str, **context: Any) -> None:
        """
        Log a warning message.
        """

    @abstractmethod
    def error(self, message: str, **context: Any) -> None:
        """
        Log an error message.
        """

    @abstractmethod
    def critical(self, message: str, **context: Any) -> None:
        """
        Log a critical message.
        """

    @abstractmethod
    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        """
        Log a message at the specified level.
        """

    @abstractmethod
    def bind(self, **context: Any) -> "Logger":
        """
        Bind context to this logger.
        """

    @abstractmethod
    def set_level(self, level: LogLevel) -> None:
        """
        Set the logging level.
        """

    @abstractmethod
    def add_handler(self, handler: "LogHandler") -> None:
        """
        Add a log handler.
        """

    @abstractmethod
    def remove_handler(self, handler: "LogHandler") -> None:
        """
        Remove a log handler.
        """

    def is_enabled_for(self, level: LogLevel) -> bool:
        """
        Check if logging is enabled for the given level.
        """
        return level.value >= self.level.value


class LogHandler(ABC):
    """
    Base interface for log handlers.
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.DEBUG):
        self.name = name
        self.level = level

    @abstractmethod
    def emit(self, record: LogRecord) -> None:
        """Emit a log record.

        Args:
            record: Log record to emit
        """

    @abstractmethod
    def flush(self) -> None:
        """
        Flush any buffered records.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the handler.
        """

    def should_emit(self, record: LogRecord) -> bool:
        """
        Check if the record should be emitted.
        """
        return record.level.value >= self.level.value


class LogFormatter(ABC):
    """
    Base interface for log formatters.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Format a log record.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """

    @abstractmethod
    def format_exception(self, exc_info) -> str:
        """Format exception information.

        Args:
            exc_info: Exception information tuple

        Returns:
            Formatted exception string
        """


class Monitor(ABC):
    """
    Base interface for monitors.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config
        self._running = False

    @abstractmethod
    def start(self) -> None:
        """
        Start monitoring.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Stop monitoring.
        """

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics.

        Returns:
            Dictionary of metrics
        """

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the monitored system is healthy.

        Returns:
            True if healthy
        """

    @property
    def is_running(self) -> bool:
        """
        Check if monitor is running.
        """
        return self._running


class MetricsCollector(ABC):
    """
    Base interface for metrics collectors.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    def increment(self, name: str, value: float = 1.0, **labels: str) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name
            value: Increment value
            labels: Metric labels
        """

    @abstractmethod
    def set(self, name: str, value: float, **labels: str) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name
            value: Metric value
            labels: Metric labels
        """

    @abstractmethod
    def observe(self, name: str, value: float, **labels: str) -> None:
        """Observe a histogram/summary metric.

        Args:
            name: Metric name
            value: Observed value
            labels: Metric labels
        """

    @abstractmethod
    def get_metrics(self) -> list[MetricPoint]:
        """Get all collected metrics.

        Returns:
            List of metric points
        """


class HealthChecker(ABC):
    """
    Base interface for health checkers.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    def check_health(self) -> HealthStatus:
        """Perform a health check.

        Returns:
            Health status
        """

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the system is healthy.

        Returns:
            True if healthy
        """
