"""Process information data model.

Canonical ProcessInfo class used across all pheno-sdk components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ProcessInfo:
    """
    Information about a monitored process.
    """

    name: str
    """
    Process/service name.
    """

    project: str
    """
    Associated project name.
    """

    pid: int | None = None
    """
    Process ID.
    """

    port: int | None = None
    """
    Port number.
    """

    state: str = "unknown"
    """
    Process state (running, stopped, starting, error)
    """

    tunnel_url: str | None = None
    """
    Tunnel URL if applicable.
    """

    start_time: datetime | None = None
    """
    Process start time.
    """

    metadata: dict[str, Any] = field(default_factory=dict)
    """
    Additional process metadata.
    """
