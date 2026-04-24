"""Logging configuration for TraceRTM.

Provides structured logging with both Loguru (for backwards compatibility)
and structlog (for structured log aggregation with Loki).
"""

import logging
import sys

import structlog
from loguru import logger

from tracertm.config import get_settings


def setup_logging() -> None:
    """Configure logging for TraceRTM with both Loguru and structlog."""
    settings = get_settings()

    # Create log directory
    log_dir = settings.data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Configure structlog for structured logging (Loki integration)
    # ========================================================================

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # ========================================================================
    # Configure Loguru (backwards compatibility)
    # ========================================================================

    # Remove default handler
    logger.remove()

    # Console handler with color
    log_format = (
        "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.log_level,
        colorize=True,
    )

    # File handler with rotation
    logger.add(
        log_dir / "tracertm.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="500 MB",
        retention="7 days",
        compression="zip",
    )

    # JSON handler for structured logging
    logger.add(
        log_dir / "tracertm.json",
        format="{message}",
        level="INFO",
        rotation="500 MB",
        retention="7 days",
        compression="zip",
        serialize=True,
    )

    # Error file handler
    logger.add(
        log_dir / "tracertm_errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="500 MB",
        retention="30 days",
        compression="zip",
    )

    logger.info("Logging configured: level=%s, dir=%s", settings.log_level, log_dir)


def get_logger(name: str) -> object:
    """Get a Loguru logger instance for a module."""
    return logger.bind(module=name)


def get_structlog_logger(name: str | None = None) -> object:
    """Get a structlog logger instance for structured logging.

    Usage:
        logger = get_structlog_logger(__name__)
        logger.info("user_login", user_id=user.id, ip=request.client.host)
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()
