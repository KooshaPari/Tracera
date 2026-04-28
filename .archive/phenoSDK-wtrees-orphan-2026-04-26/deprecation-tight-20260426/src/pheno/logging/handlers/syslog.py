"""Syslog handler.

This module provides syslog-based log handling for system logging.
"""

import socket
from typing import Any

from ..core.interfaces import LogHandler
from ..core.types import HandlerError, LogLevel, LogRecord


class SyslogHandler(LogHandler):
    """
    Syslog-based log handler.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        super().__init__(name, config.get("level", LogLevel.DEBUG))

        # Syslog configuration
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 514)
        self.facility = config.get("facility", "user")
        self.protocol = config.get("protocol", "udp")
        self.socktype = socket.SOCK_DGRAM if self.protocol == "udp" else socket.SOCK_STREAM

        # Facility mapping
        self.facilities = {
            "kern": 0,
            "user": 1,
            "mail": 2,
            "daemon": 3,
            "auth": 4,
            "syslog": 5,
            "lpr": 6,
            "news": 7,
            "uucp": 8,
            "cron": 9,
            "authpriv": 10,
            "ftp": 11,
            "local0": 16,
            "local1": 17,
            "local2": 18,
            "local3": 19,
            "local4": 20,
            "local5": 21,
            "local6": 22,
            "local7": 23,
        }

        # Priority mapping
        self.priorities = {
            LogLevel.DEBUG: 7,  # debug
            LogLevel.INFO: 6,  # info
            LogLevel.WARNING: 4,  # warning
            LogLevel.ERROR: 3,  # error
            LogLevel.CRITICAL: 2,  # critical
        }

        # Create socket
        self._socket = None
        self._connect()

    def emit(self, record: LogRecord) -> None:
        """Emit a log record to syslog.

        Args:
            record: Log record to emit
        """
        try:
            if self._socket is None:
                self._connect()

            # Format message
            message = self._format_record(record)

            # Create syslog message
            facility = self.facilities.get(self.facility, 1)
            priority = self.priorities.get(record.level, 6)
            severity = facility * 8 + priority

            # Add timestamp and hostname
            timestamp = record.timestamp.strftime("%b %d %H:%M:%S")
            hostname = socket.gethostname()

            syslog_msg = f"<{severity}>{timestamp} {hostname} {message}"

            # Send message
            self._socket.sendto(syslog_msg.encode("utf-8"), (self.host, self.port))

        except Exception as e:
            raise HandlerError(f"Failed to emit syslog record: {e}")

    def flush(self) -> None:
        """
        Flush the socket.
        """
        if self._socket:
            self._socket.flush()

    def close(self) -> None:
        """
        Close the syslog handler.
        """
        if self._socket:
            self._socket.close()
            self._socket = None

    def _connect(self) -> None:
        """
        Connect to syslog server.
        """
        try:
            self._socket = socket.socket(socket.AF_INET, self.socktype)
            if self.protocol == "tcp":
                self._socket.connect((self.host, self.port))
        except Exception as e:
            raise HandlerError(f"Failed to connect to syslog server {self.host}:{self.port}: {e}")

    def _format_record(self, record: LogRecord) -> str:
        """
        Format a log record for syslog.
        """
        parts = [record.message]

        # Add context
        if record.context:
            context_str = ", ".join(f"{k}={v}" for k, v in record.context.items())
            parts.append(f"({context_str})")

        # Add exception
        if record.exception:
            parts.append(f"Exception: {record.exception}")

        return " ".join(parts)
