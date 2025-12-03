"""
Loguru configuration for TraceRTM.

Provides structured logging with JSON output, file rotation, and filtering.
"""

import sys

from loguru import logger

from tracertm.config import get_settings


def setup_logging() -> None:
    """Configure loguru for TraceRTM."""
    settings = get_settings()

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
    log_dir = settings.data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

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

    logger.info(f"Logging configured: level={settings.log_level}, dir={log_dir}")


def get_logger(name: str) -> "logger":
    """Get a logger instance for a module."""
    return logger.bind(module=name)
