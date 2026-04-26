"""Structured logging setup for Phenotype services.

Provides consistent JSON logging configuration using structlog. Configures
both stdlib logging and structlog for structured, machine-readable logs.

Example:
    >>> from phenotype_logging import configure_logging, get_logger
    >>> configure_logging(level="DEBUG", service_name="my-service")
    >>> logger = get_logger(__name__)
    >>> logger.info("service started", version="1.0.0")
"""

import json
import logging
import sys
from typing import Any

import structlog


def configure_logging(
    level: str = "INFO",
    service_name: str | None = None,
    json_output: bool = True,
) -> None:
    """Configure structured logging for the application.

    Sets up both stdlib logging and structlog with JSON output for better
    machine readability and structured processing.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Optional service identifier for all log entries
        json_output: If True, output JSON; otherwise use plaintext format
    """
    # Configure stdlib logging
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    # Set formatter based on output type
    if json_output:
        formatter = StructuredFormatter(service_name=service_name)
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            (
                structlog.processors.JSONRenderer()
                if json_output
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for a module.

    Args:
        name: Module name, typically __name__

    Returns:
        Configured structlog BoundLogger
    """
    return structlog.get_logger(name)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging.

    Converts log records to JSON with consistent structure across services.
    """

    def __init__(self, service_name: str | None = None):
        """Initialize formatter.

        Args:
            service_name: Optional service identifier for all log entries
        """
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log string
        """
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add service name if provided
        if self.service_name:
            log_obj["service"] = self.service_name

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ):
                log_obj[key] = value

        return json.dumps(log_obj)
