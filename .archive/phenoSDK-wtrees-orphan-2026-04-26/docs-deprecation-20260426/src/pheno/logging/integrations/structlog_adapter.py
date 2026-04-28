"""Structlog integration for pheno-logging.

This module provides a bridge between pheno-logging and structlog,
allowing you to use structlog's powerful structured logging features
with pheno-logging's interface.

Migrated from: src/pheno/observability/logging.py
"""

from __future__ import annotations

import logging
from typing import Any

from ..core.interfaces import Logger
from ..core.types import LogLevel

__all__ = [
    "StructlogAdapter",
    "configure_structlog_for_pheno",
    "get_structlog_logger",
]


class StructlogAdapter(Logger):
    """Adapter to use structlog with pheno-logging interface.

    This allows you to use structlog loggers through the pheno-logging
    Logger interface, providing compatibility with both systems.

    Example:
        logger = StructlogAdapter("my_service")
        logger.info("User logged in", user_id=123, ip="192.168.1.1")
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        super().__init__(name, level)
        import structlog

        self._logger = structlog.get_logger(name)

    def debug(self, message: str, **context: Any) -> None:
        """
        Log a debug message.
        """
        if self.is_enabled_for(LogLevel.DEBUG):
            self._logger.debug(message, **context)

    def info(self, message: str, **context: Any) -> None:
        """
        Log an info message.
        """
        if self.is_enabled_for(LogLevel.INFO):
            self._logger.info(message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """
        Log a warning message.
        """
        if self.is_enabled_for(LogLevel.WARNING):
            self._logger.warning(message, **context)

    def error(self, message: str, **context: Any) -> None:
        """
        Log an error message.
        """
        if self.is_enabled_for(LogLevel.ERROR):
            self._logger.error(message, **context)

    def critical(self, message: str, **context: Any) -> None:
        """
        Log a critical message.
        """
        if self.is_enabled_for(LogLevel.CRITICAL):
            self._logger.critical(message, **context)

    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        """
        Log a message at the specified level.
        """
        if self.is_enabled_for(level):
            level_name = level.name.lower()
            getattr(self._logger, level_name)(message, **context)

    def bind(self, **context: Any) -> StructlogAdapter:
        """
        Bind context to this logger.
        """
        self._logger = self._logger.bind(**context)
        return self

    def set_level(self, level: LogLevel) -> None:
        """
        Set the logging level.
        """
        self.level = level

    def add_handler(self, handler: Any) -> None:
        """
        Add a log handler (not applicable for structlog).
        """
        # Structlog uses processors, not handlers

    def remove_handler(self, handler: Any) -> None:
        """
        Remove a log handler (not applicable for structlog).
        """
        # Structlog uses processors, not handlers


def configure_structlog_for_pheno(
    *,
    service_name: str,
    environment: str = "dev",
    log_level: str = "INFO",
    json_logs: bool | None = None,
    add_correlation_id: bool = True,
    add_callsite: bool = True,
) -> None:
    """Configure structlog with environment-appropriate settings for pheno-logging.

    This function sets up structlog with sensible defaults for different
    environments (dev, staging, prod) and integrates with pheno-logging's
    context management.

    Args:
        service_name: Name of the service (added to all log entries)
        environment: Environment name (dev, staging, prod)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON format (auto-detected based on environment if None)
        add_correlation_id: Add correlation_id and request_id from context
        add_callsite: Add callsite information (file, line, function)

    Example:
        configure_structlog_for_pheno(
            service_name="my-api",
            environment="prod",
            log_level="INFO",
            json_logs=True
        )

        logger = get_structlog_logger("my_module")
        logger.info("Server started", port=8000)
    """
    import structlog

    # Auto-detect JSON logs for production environments
    if json_logs is None:
        json_logs = environment in ("staging", "prod", "production")

    # Build processor pipeline
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    # Add correlation ID and service context
    def _add_context(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Add correlation IDs and service context to log entries.
        """
        try:
            import contextvars

            # Add correlation ID if available
            correlation_id_var = contextvars.ContextVar("correlation_id", default=None)
            correlation_id = correlation_id_var.get()
            if correlation_id:
                event_dict["correlation_id"] = correlation_id

            # Add request ID if available
            request_id_var = contextvars.ContextVar("request_id", default=None)
            request_id = request_id_var.get()
            if request_id:
                event_dict["request_id"] = request_id
        except Exception:
            # Silently ignore context errors
            pass

        # Always add service and environment
        event_dict["service"] = service_name
        event_dict["environment"] = environment
        return event_dict

    if add_correlation_id:
        processors.append(_add_context)

    # Add callsite information (file, line, function)
    if add_callsite:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                },
            ),
        )

    # Add renderer (JSON for prod, console for dev)
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO),
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Recreate stdlib defaults for compatibility
    structlog.stdlib.recreate_defaults()


def get_structlog_logger(name: str | None = None) -> Any:
    """Get a structlog logger.

    This is a convenience function that returns a structlog logger directly.
    For pheno-logging interface compatibility, use StructlogAdapter instead.

    Args:
        name: Logger name (optional)

    Returns:
        Structlog logger instance

    Example:
        logger = get_structlog_logger("my_module")
        logger.info("Processing request", request_id="abc123")
    """
    import structlog

    return structlog.get_logger(name)


# Backward compatibility aliases
configure_structlog = configure_structlog_for_pheno
get_logger = get_structlog_logger
