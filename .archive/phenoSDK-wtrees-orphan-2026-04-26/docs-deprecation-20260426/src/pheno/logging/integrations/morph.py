"""
Morph logging integration helpers.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from pheno.config.integration import MorphIntegrationSettings, get_morph_settings
from pheno.logging.core.logger import get_logger as get_pheno_logger

if TYPE_CHECKING:
    from collections.abc import Iterator


class _JsonFormatter(logging.Formatter):
    """
    Simple JSON formatter for Morph compatibility.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "component"):
            payload["component"] = record.component
        if hasattr(record, "operation"):
            payload["operation"] = record.operation
        if hasattr(record, "metadata"):
            payload["metadata"] = record.metadata
        if hasattr(record, "trace_id"):
            payload["trace_id"] = record.trace_id
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_morph_logging(settings: MorphIntegrationSettings | None = None) -> logging.Logger:
    """Configure Python logging according to Morph integration settings.

    Returns the configured root Morph logger for convenience.
    """
    settings = settings or get_morph_settings()
    logger = logging.getLogger("morph")
    logger.handlers.clear()
    level = getattr(logging, settings.logging_level.upper(), logging.INFO)
    logger.setLevel(level)

    formatter: logging.Formatter
    if settings.logging_format.lower() == "json":
        formatter = _JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    if settings.logging_enable_console:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        logger.addHandler(console)

    if settings.logging_enable_file and settings.logging_file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.logging_file_path,
            maxBytes=settings.logging_max_file_size,
            backupCount=settings.logging_backup_count,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_morph_logger(name: str) -> logging.Logger:
    """
    Return a namespaced Morph logger (config must be applied separately).
    """
    return logging.getLogger(f"morph.{name}")


@contextmanager
def morph_log_context(
    *,
    component: str | None = None,
    operation: str | None = None,
    trace_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Iterator[logging.LoggerAdapter]:
    """
    Context manager that yields a logging adapter attaching Morph-specific fields.
    """
    extra = {
        "component": component,
        "operation": operation,
        "trace_id": trace_id,
        "metadata": metadata or {},
    }
    base_logger = get_morph_logger("context")
    adapter = logging.LoggerAdapter(base_logger, extra={k: v for k, v in extra.items() if v})
    yield adapter


def get_pheno_structured_logger(name: str) -> Any:
    """
    Convenience helper to access pheno's core structured logger with Morph namespace.
    """
    return get_pheno_logger(f"morph.{name}")
