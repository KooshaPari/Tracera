"""Observability helpers for the FastAPI API.

The module intentionally keeps setup lightweight and dependency-free so the
observability path can initialize safely during import and in tests.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from tracertm.api.middleware.request_id import request_id_var


_LOGGING_CONFIGURED = False


class CorrelationIdFilter(logging.Filter):
    """Attach request correlation metadata into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        request_id = request_id_var.get()
        record.correlation_id = request_id
        record.request_id = request_id
        return True


class JSONFormatter(logging.Formatter):
    """A compact JSON formatter for machine ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "request_id": getattr(record, "request_id", None),
            "pid": record.process,
            "thread": record.threadName,
        }
        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "elapsed_ms"):
            event["elapsed_ms"] = getattr(record, "elapsed_ms")
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
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
                "taskName",
                "correlation_id",
                "request_id",
                "elapsed_ms",
            }:
                continue
            event[key] = value
        return json.dumps(event)


def configure_api_logging() -> None:
    """Set up structured JSON logging on stdout for the API logger."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return
    _LOGGING_CONFIGURED = True

    logger = logging.getLogger("tracertm")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.addFilter(CorrelationIdFilter())
    logger.addHandler(handler)
    # silence noisy deps
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def log_request_metrics(
    logger: logging.Logger,
    method: str,
    path: str,
    status: int,
    elapsed_ms: float,
) -> None:
    """Log a request completion with elapsed time."""
    logger.info(
        f"{method} {path} {status}",
        extra={
            "elapsed_ms": round(elapsed_ms, 2),
            "http_method": method,
            "http_path": path,
            "http_status": status,
        },
    )
