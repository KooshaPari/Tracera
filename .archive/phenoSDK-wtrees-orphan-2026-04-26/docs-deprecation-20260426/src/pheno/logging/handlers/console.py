"""Console log handler.

This module provides console-based log handling with support for colored output and rich
formatting.
"""

import sys
from typing import Any

from ..core.interfaces import LogHandler
from ..core.types import HandlerError, LogLevel, LogRecord


class ConsoleHandler(LogHandler):
    """
    Console-based log handler.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        super().__init__(name, config.get("level", LogLevel.DEBUG))

        # Console configuration
        self.stream = config.get("stream", sys.stdout)
        self.use_colors = config.get("use_colors", True)
        self.show_timestamp = config.get("show_timestamp", True)
        self.show_level = config.get("show_level", True)
        self.show_logger = config.get("show_logger", False)
        self.show_context = config.get("show_context", False)

        # Color mapping
        self.colors = {
            LogLevel.DEBUG: "\033[36m",  # Cyan
            LogLevel.INFO: "\033[32m",  # Green
            LogLevel.WARNING: "\033[33m",  # Yellow
            LogLevel.ERROR: "\033[31m",  # Red
            LogLevel.CRITICAL: "\033[35m",  # Magenta
        }
        self.reset_color = "\033[0m"

    def emit(self, record: LogRecord) -> None:
        """Emit a log record to console.

        Args:
            record: Log record to emit
        """
        try:
            formatted = self._format_record(record)
            self.stream.write(formatted + "\n")
            self.stream.flush()
        except Exception as e:
            raise HandlerError(f"Failed to emit log record: {e}")

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

    def _format_record(self, record: LogRecord) -> str:
        """
        Format a log record for console output.
        """
        parts = []

        # Timestamp
        if self.show_timestamp:
            timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            parts.append(f"[{timestamp}]")

        # Level
        if self.show_level:
            level_str = record.level.name
            if self.use_colors:
                color = self.colors.get(record.level, "")
                level_str = f"{color}{level_str}{self.reset_color}"
            parts.append(f"[{level_str}]")

        # Logger name
        if self.show_logger:
            parts.append(f"[{record.logger_name}]")

        # Message
        parts.append(record.message)

        # Context
        if self.show_context and record.context:
            context_str = ", ".join(f"{k}={v}" for k, v in record.context.items())
            parts.append(f"({context_str})")

        # Exception
        if record.exception:
            parts.append(f"\nException: {record.exception}")

        return " ".join(parts)
