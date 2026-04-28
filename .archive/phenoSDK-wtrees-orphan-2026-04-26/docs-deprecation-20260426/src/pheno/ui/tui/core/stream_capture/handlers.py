"""
Logging handlers that forward events into the capture system.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from .levels import LogLevel
from .models import CapturedLine

if TYPE_CHECKING:
    from collections.abc import Callable


class LoggingHandler(logging.Handler):
    def __init__(self, callback: Callable[[CapturedLine], None]):
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - exercised indirectly
        try:
            level_map = {
                logging.DEBUG: LogLevel.DEBUG,
                logging.INFO: LogLevel.INFO,
                logging.WARNING: LogLevel.WARNING,
                logging.ERROR: LogLevel.ERROR,
                logging.CRITICAL: LogLevel.CRITICAL,
            }
            level = level_map.get(record.levelno, LogLevel.INFO)
            line = CapturedLine(
                text=self.format(record),
                timestamp=datetime.fromtimestamp(record.created),
                source="logger",
                level=level,
                logger_name=record.name,
                thread_id=record.thread,
                metadata={
                    "module": record.module,
                    "function": record.funcName,
                    "line_no": record.lineno,
                    "pathname": record.pathname,
                },
            )
            self._callback(line)
        except Exception:  # pragma: no cover - defensive guard
            self.handleError(record)


__all__ = ["LoggingHandler"]
