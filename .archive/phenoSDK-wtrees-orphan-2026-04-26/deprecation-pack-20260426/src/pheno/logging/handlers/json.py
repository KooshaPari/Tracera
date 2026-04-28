"""JSON log handler.

This module provides JSON-formatted log handling for structured logging.
"""

import json
import sys
from typing import Any

from ..core.interfaces import LogHandler
from ..core.types import HandlerError, LogLevel, LogRecord


class JSONHandler(LogHandler):
    """
    JSON-formatted log handler.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        super().__init__(name, config.get("level", LogLevel.DEBUG))

        # JSON configuration
        self.stream = config.get("stream", sys.stdout)
        self.indent = config.get("indent")
        self.ensure_ascii = config.get("ensure_ascii", False)
        self.sort_keys = config.get("sort_keys", False)
        self.include_extra = config.get("include_extra", True)
        self.include_context = config.get("include_context", True)

    def emit(self, record: LogRecord) -> None:
        """Emit a log record as JSON.

        Args:
            record: Log record to emit
        """
        try:
            json_data = self._record_to_dict(record)
            json_str = json.dumps(
                json_data,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
                sort_keys=self.sort_keys,
            )
            self.stream.write(json_str + "\n")
            self.stream.flush()
        except Exception as e:
            raise HandlerError(f"Failed to emit JSON log record: {e}")

    def flush(self) -> None:
        """
        Flush the output stream.
        """
        self.stream.flush()

    def close(self) -> None:
        """
        Close the handler.
        """
        if hasattr(self.stream, "close"):
            self.stream.close()

    def _record_to_dict(self, record: LogRecord) -> dict[str, Any]:
        """
        Convert log record to dictionary.
        """
        data = {
            "timestamp": record.timestamp.isoformat(),
            "level": record.level.name,
            "logger": record.logger_name,
            "message": record.message,
        }

        # Add context if enabled
        if self.include_context and record.context:
            data["context"] = record.context

        # Add correlation ID
        if record.correlation_id:
            data["correlation_id"] = record.correlation_id

        # Add user ID
        if record.user_id:
            data["user_id"] = record.user_id

        # Add request ID
        if record.request_id:
            data["request_id"] = record.request_id

        # Add module info
        if record.module:
            data["module"] = record.module

        if record.function:
            data["function"] = record.function

        if record.line_number:
            data["line_number"] = record.line_number

        # Add exception
        if record.exception:
            data["exception"] = {
                "type": type(record.exception).__name__,
                "message": str(record.exception),
            }

        # Add extra fields
        if self.include_extra and record.extra:
            data["extra"] = record.extra

        return data
