"""Main logger implementation for pheno-logging.

This module provides the central Logger class that orchestrates all logging operations
across handlers and formatters.
"""

import sys
import uuid
from datetime import datetime
from typing import Any

from .interfaces import LogFormatter, Logger, LogHandler
from .types import LogContext, LogLevel, LogRecord


class LoggerImpl(Logger):
    """
    Main logger implementation.
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        super().__init__(name, level)
        self._handlers: list[LogHandler] = []
        self._formatters: list[LogFormatter] = []
        self._context: LogContext = LogContext()

    def debug(self, message: str, **context: Any) -> None:
        """
        Log a debug message.
        """
        self.log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> None:
        """
        Log an info message.
        """
        self.log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """
        Log a warning message.
        """
        self.log(LogLevel.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> None:
        """
        Log an error message.
        """
        self.log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context: Any) -> None:
        """
        Log a critical message.
        """
        self.log(LogLevel.CRITICAL, message, **context)

    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        """Log a message at the specified level.

        Args:
            level: Log level
            message: Log message
            **context: Additional context
        """
        if not self.is_enabled_for(level):
            return

        try:
            # Create log record
            record = self._create_record(level, message, context)

            # Emit to all handlers
            for handler in self._handlers:
                if handler.should_emit(record):
                    handler.emit(record)

        except Exception as e:
            # Fallback to stderr if logging fails
            print(f"Logging error: {e}", file=sys.stderr)

    def bind(self, **context: Any) -> "Logger":
        """Bind context to this logger.

        Args:
            **context: Context to bind

        Returns:
            New logger with bound context
        """
        new_logger = LoggerImpl(self.name, self.level)
        new_logger._handlers = self._handlers.copy()
        new_logger._formatters = self._formatters.copy()

        # Merge context
        new_logger._context = self._context.merge(LogContext(custom=context))

        return new_logger

    def set_level(self, level: LogLevel) -> None:
        """
        Set the logging level.
        """
        self.level = level

    def add_handler(self, handler: LogHandler) -> None:
        """
        Add a log handler.
        """
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler: LogHandler) -> None:
        """
        Remove a log handler.
        """
        if handler in self._handlers:
            self._handlers.remove(handler)

    def _create_record(self, level: LogLevel, message: str, context: dict[str, Any]) -> LogRecord:
        """
        Create a log record.
        """
        # Get current frame info
        frame = sys._getframe(2)  # Skip this method and log method

        # Extract exception info if present
        exc_info = None
        if "exc_info" in context:
            exc_info = context.pop("exc_info")
        elif level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            exc_info = sys.exc_info()

        # Merge context with logger context
        merged_context = {**self._context.to_dict(), **context}

        # Generate correlation ID if not present
        correlation_id = merged_context.get("correlation_id")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            merged_context["correlation_id"] = correlation_id

        return LogRecord(
            level=level,
            message=message,
            timestamp=datetime.now(),
            logger_name=self.name,
            context=merged_context,
            correlation_id=correlation_id,
            user_id=merged_context.get("user_id"),
            request_id=merged_context.get("request_id"),
            module=frame.f_globals.get("__name__"),
            function=frame.f_code.co_name,
            line_number=frame.f_lineno,
            exception=exc_info[1] if exc_info else None,
            extra=context,
        )


# Global logger registry
_loggers: dict[str, LoggerImpl] = {}


def get_logger(name: str, level: LogLevel = LogLevel.INFO) -> LoggerImpl:
    """Get or create a logger.

    Args:
        name: Logger name
        level: Log level

    Returns:
        Logger instance
    """
    if name not in _loggers:
        _loggers[name] = LoggerImpl(name, level)
    return _loggers[name]


def configure_logging(config: dict[str, Any]) -> None:
    """Configure global logging.

    Args:
        config: Logging configuration
    """
    # This would configure global logging settings
    # For now, it's a placeholder


def shutdown_logging() -> None:
    """
    Shutdown all loggers and handlers.
    """
    for logger in _loggers.values():
        for handler in logger._handlers:
            handler.close()
    _loggers.clear()
