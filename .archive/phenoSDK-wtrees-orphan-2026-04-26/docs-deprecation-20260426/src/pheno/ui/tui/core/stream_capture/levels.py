"""
Log level enumeration used by stream capture components.
"""

from enum import StrEnum


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


__all__ = ["LogLevel"]
