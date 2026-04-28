"""Core logging interfaces and types.

This module provides the foundational interfaces and types for the pheno-logging
library, ensuring consistency across all logging implementations.
"""

from .interfaces import (
    HealthChecker,
    LogContext,
    LogFormatter,
    Logger,
    LogHandler,
    LogLevel,
    LogRecord,
    MetricsCollector,
    Monitor,
)
from .logger import Logger as LoggerImpl
from .types import (
    ConfigurationError,
    FormatterError,
    HandlerError,
    LogContext,
    LoggingError,
    LogLevel,
    LogRecord,
)

__all__ = [
    "ConfigurationError",
    "FormatterError",
    "HandlerError",
    "HealthChecker",
    "LogContext",
    "LogFormatter",
    "LogHandler",
    "LogLevel",
    "LogRecord",
    "Logger",
    "LoggerImpl",
    "LoggingError",
    "MetricsCollector",
    "Monitor",
]
