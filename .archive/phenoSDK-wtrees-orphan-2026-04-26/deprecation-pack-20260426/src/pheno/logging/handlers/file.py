"""File log handler.

This module provides file-based log handling with support for rotation, buffering, and
different file formats.
"""

from pathlib import Path
from typing import Any

from ..core.interfaces import LogHandler
from ..core.types import HandlerError, LogLevel, LogRecord


class FileHandler(LogHandler):
    """
    File-based log handler.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        super().__init__(name, config.get("level", LogLevel.DEBUG))

        # File configuration
        self.filename = Path(config.get("filename", "app.log"))
        self.mode = config.get("mode", "a")
        self.encoding = config.get("encoding", "utf-8")
        self.buffer_size = config.get("buffer_size", 8192)
        self.max_bytes = config.get("max_bytes", 0)  # 0 = no rotation
        self.backup_count = config.get("backup_count", 0)

        # Open file
        self._file = None
        self._open_file()

    def emit(self, record: LogRecord) -> None:
        """Emit a log record to file.

        Args:
            record: Log record to emit
        """
        try:
            if self._file is None:
                self._open_file()

            formatted = self._format_record(record)
            self._file.write(formatted + "\n")
            self._file.flush()

            # Check for rotation
            if self.max_bytes > 0 and self._file.tell() >= self.max_bytes:
                self._rotate_file()

        except Exception as e:
            raise HandlerError(f"Failed to emit log record: {e}")

    def flush(self) -> None:
        """
        Flush the file buffer.
        """
        if self._file:
            self._file.flush()

    def close(self) -> None:
        """
        Close the file handler.
        """
        if self._file:
            self._file.close()
            self._file = None

    def _open_file(self) -> None:
        """
        Open the log file.
        """
        try:
            # Create directory if it doesn't exist
            self.filename.parent.mkdir(parents=True, exist_ok=True)

            # Open file
            self._file = open(
                self.filename, mode=self.mode, encoding=self.encoding, buffering=self.buffer_size,
            )
        except Exception as e:
            raise HandlerError(f"Failed to open log file '{self.filename}': {e}")

    def _rotate_file(self) -> None:
        """
        Rotate the log file.
        """
        if not self._file:
            return

        try:
            # Close current file
            self._file.close()

            # Rotate existing files
            for i in range(self.backup_count - 1, 0, -1):
                old_file = Path(f"{self.filename}.{i}")
                new_file = Path(f"{self.filename}.{i + 1}")
                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)

            # Move current file to .1
            if self.filename.exists():
                backup_file = Path(f"{self.filename}.1")
                if backup_file.exists():
                    backup_file.unlink()
                self.filename.rename(backup_file)

            # Open new file
            self._open_file()

        except Exception as e:
            raise HandlerError(f"Failed to rotate log file: {e}")

    def _format_record(self, record: LogRecord) -> str:
        """
        Format a log record for file output.
        """
        parts = []

        # Timestamp
        timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        parts.append(f"[{timestamp}]")

        # Level
        parts.append(f"[{record.level.name}]")

        # Logger name
        parts.append(f"[{record.logger_name}]")

        # Message
        parts.append(record.message)

        # Context
        if record.context:
            context_str = ", ".join(f"{k}={v}" for k, v in record.context.items())
            parts.append(f"({context_str})")

        # Exception
        if record.exception:
            parts.append(f"\nException: {record.exception}")

        return " ".join(parts)
