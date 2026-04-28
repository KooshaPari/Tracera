"""Structured logging configuration for MCP tools.

Provides:
- JSON-formatted logging for log aggregation
- Configurable log levels
- Request/response logging
- Performance logging
- Error logging with context
"""

from __future__ import annotations

import logging
import sys
import time
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from structlog.typing import EventDict, Processor


def add_timestamp(_logger: logging.Logger, _method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO timestamp to log entries.

    Args:
        logger: Logger instance
        method_name: Log method name
        event_dict: Event dictionary

    Returns:
        Modified event dictionary
    """
    event_dict["timestamp"] = time.time()
    event_dict["timestamp_iso"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    return event_dict


def add_log_level(_logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event.

    Args:
        logger: Logger instance
        method_name: Log method name
        event_dict: Event dictionary

    Returns:
        Modified event dictionary
    """
    event_dict["level"] = method_name.upper()
    return event_dict


def add_logger_name(logger: logging.Logger, _method_name: str, event_dict: EventDict) -> EventDict:
    """Add logger name to event.

    Args:
        logger: Logger instance
        method_name: Log method name
        event_dict: Event dictionary

    Returns:
        Modified event dictionary
    """
    event_dict["logger"] = logger.name
    return event_dict


def censor_sensitive_data(_logger: logging.Logger, _method_name: str, event_dict: EventDict) -> EventDict:
    """Remove sensitive data from logs.

    Args:
        logger: Logger instance
        method_name: Log method name
        event_dict: Event dictionary

    Returns:
        Modified event dictionary with sensitive data censored
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
        "jwt",
    }

    def _censor_dict(data: dict[str, object]) -> dict[str, object]:
        """Recursively censor dictionary values."""
        censored: dict[str, object] = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                censored[key] = "[REDACTED]"
            elif isinstance(value, dict):
                censored[key] = _censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [_censor_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                censored[key] = value
        return censored

    return _censor_dict(dict(event_dict))


def configure_structured_logging(
    log_level: str = "INFO",
    json_output: bool = True,
    log_file: str | None = None,
) -> None:
    """Configure structured logging for MCP server.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Output logs in JSON format
        log_file: Optional log file path
    """
    # Configure structlog
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_timestamp,
        add_log_level,
        add_logger_name,
        censor_sensitive_data,
    ]

    # Add JSON or console renderer
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        if json_output:
            file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.root.addHandler(file_handler)


class StructuredLogger:
    """Structured logger wrapper for MCP operations."""

    def __init__(self, name: str = "tracertm.mcp") -> None:
        """Initialize structured logger.

        Args:
            name: Logger name
        """
        self.logger = structlog.get_logger(name)

    def log_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, object],
        duration: float | None = None,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Log a tool call with structured data.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            duration: Execution duration in seconds
            success: Whether the call succeeded
            error: Error message if failed
        """
        log_data = {
            "event": "tool_call",
            "tool": tool_name,
            "arg_count": len(arguments),
            "success": success,
        }

        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)

        if error:
            log_data["error"] = error

        if success:
            self.logger.info("tool_call_succeeded", **log_data)
        else:
            self.logger.error("tool_call_failed", **log_data)

    def log_performance(
        self,
        operation: str,
        duration: float,
        threshold: float | None = None,
    ) -> None:
        """Log performance metrics.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            threshold: Warning threshold in seconds
        """
        log_data = {
            "event": "performance",
            "operation": operation,
            "duration_seconds": round(duration, 3),
        }

        if threshold and duration >= threshold:
            log_data["slow"] = True
            self.logger.warning("slow_operation", **log_data)
        else:
            self.logger.debug("operation_completed", **log_data)

    def log_error(
        self,
        error: Exception,
        context: dict[str, object] | None = None,
    ) -> None:
        """Log an error with context.

        Args:
            error: Exception that occurred
            context: Additional context
        """
        log_data: dict[str, object] = {
            "event": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        if context:
            log_data.update(context)

        self.logger.error("error_occurred", **log_data)

    def log_auth(
        self,
        action: str,
        user_id: str | None = None,
        success: bool = True,
        reason: str | None = None,
    ) -> None:
        """Log authentication/authorization events.

        Args:
            action: Auth action (login, logout, permission_check, etc.)
            user_id: User identifier
            success: Whether the action succeeded
            reason: Failure reason if applicable
        """
        log_data = {
            "event": "auth",
            "action": action,
            "success": success,
        }

        if user_id:
            log_data["user_id"] = user_id

        if reason:
            log_data["reason"] = reason

        if success:
            self.logger.info("auth_succeeded", **log_data)
        else:
            self.logger.warning("auth_failed", **log_data)

    def log_rate_limit(
        self,
        user_key: str,
        limit_type: str,
        current_count: int,
        limit: int,
    ) -> None:
        """Log rate limit events.

        Args:
            user_key: User identifier
            limit_type: Type of limit (per_minute, per_hour)
            current_count: Current call count
            limit: Rate limit threshold
        """
        log_data = {
            "event": "rate_limit",
            "user_key": user_key,
            "limit_type": limit_type,
            "current_count": current_count,
            "limit": limit,
            "exceeded": current_count >= limit,
        }

        if current_count >= limit:
            self.logger.warning("rate_limit_exceeded", **log_data)
        elif current_count >= limit * 0.8:
            self.logger.info("rate_limit_warning", **log_data)


# Global logger instance
_structured_logger: StructuredLogger | None = None


def get_structured_logger() -> StructuredLogger:
    """Get or create global structured logger instance."""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredLogger()
    return _structured_logger


__all__ = [
    "StructuredLogger",
    "configure_structured_logging",
    "get_structured_logger",
]
