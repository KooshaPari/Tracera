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
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "correlation_id",
                "request_id",
                "exc_info",
                "exc_text",
            }:
                continue
            event[key] = self._coerce(value)
        return json.dumps(event, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def _coerce(value: Any) -> Any:
        try:
            json.dumps(value)
            return value
        except TypeError:
            return str(value)


def configure_api_logging() -> None:
    """Configure root and ``tracertm`` loggers with a JSON formatter."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    formatter = JSONFormatter()
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = []
    root.addHandler(handler)
    root.propagate = False

    app_logger = logging.getLogger("tracertm")
    app_logger.setLevel(logging.INFO)
    app_logger.handlers = [handler]
    app_logger.propagate = False
    _LOGGING_CONFIGURED = True


def log_request_metrics(logger: logging.Logger, *, method: str, path: str, status: int, elapsed_ms: float) -> None:
    """Log a single request completion event with timing metadata."""
    logger.info(
        "request_complete",
        extra={
            "method": method,
            "path": path,
            "status": status,
            "elapsed_ms": round(elapsed_ms, 2),
        },
    )

