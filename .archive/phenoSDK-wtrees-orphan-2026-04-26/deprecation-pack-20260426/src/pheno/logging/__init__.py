"""
Pheno Logging - Unified Logging & Monitoring Library

A comprehensive logging and monitoring library that consolidates all logging
patterns across the pheno-sdk ecosystem into a single, consistent interface.

Features:
- Unified logging interface with structured logging
- Multi-handler logging system
- Rich console integration
- Security-aware log filtering
- Performance monitoring and metrics
- Distributed tracing support
- Health monitoring and alerting

Usage:
    from pheno_logging import get_logger, Logger, Monitor, MetricsCollector

    # Get logger
    logger = get_logger("my_app")

    # Log with context
    logger.info("User logged in", user_id="123", action="login")

    # Create monitor
    monitor = Monitor("my_service")
    monitor.start()

    # Collect metrics
    metrics = MetricsCollector()
    metrics.increment("requests_total", labels={"method": "GET"})
"""

from .core.interfaces import (
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
from .core.logger import Logger as LoggerImpl
from .core.types import (
    ConfigurationError,
    FormatterError,
    HandlerError,
    LogContext,
    LoggingError,
    LogLevel,
    LogRecord,
)

# from .handlers.registry import HandlerRegistry
# from .formatters.registry import FormatterRegistry
# from .monitoring.registry import MonitorRegistry
from .integration import configure_logging_from_settings

__version__ = "1.0.0"
__all__ = [
    "ConfigurationError",
    "FormatterError",
    "FormatterRegistry",
    "HandlerError",
    # Registries
    "HandlerRegistry",
    "HealthChecker",
    "LogContext",
    "LogFormatter",
    "LogHandler",
    "LogLevel",
    "LogRecord",
    # Core interfaces
    "Logger",
    # Implementations
    "LoggerImpl",
    # Core types
    "LoggingError",
    "MetricsCollector",
    "Monitor",
    "MonitorRegistry",
    "configure_logging_from_settings",
]
