"""Log entry data model.

Canonical LogEntry class used across all pheno-sdk components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LogEntry:
    """
    A log entry from a process.
    """

    timestamp: datetime
    """
    Log timestamp.
    """

    project: str
    """
    Associated project name.
    """

    process: str
    """
    Process name.
    """

    level: str
    """
    Log level (stdout, stderr, info, warn, error)
    """

    message: str
    """
    Log message.
    """

    metadata: dict[str, Any] = field(default_factory=dict)
    """
    Additional log metadata.
    """
