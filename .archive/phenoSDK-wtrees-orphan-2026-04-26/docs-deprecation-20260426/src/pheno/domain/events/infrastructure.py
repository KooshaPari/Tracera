"""
Infrastructure-related domain events.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ServiceCreated:
    """
    Event emitted when a service is created.
    """

    aggregate_id: str
    service_id: str
    service_name: str
    port: int
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ServiceCreated"


@dataclass(frozen=True)
class ServiceStarted:
    """
    Event emitted when a service starts.
    """

    aggregate_id: str
    service_id: str
    service_name: str
    port: int
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ServiceStarted"


@dataclass(frozen=True)
class ServiceStopped:
    """
    Event emitted when a service stops.
    """

    aggregate_id: str
    service_id: str
    service_name: str
    reason: str | None = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ServiceStopped"


@dataclass(frozen=True)
class ServiceFailed:
    """
    Event emitted when a service fails.
    """

    aggregate_id: str
    service_id: str
    service_name: str
    error_message: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "ServiceFailed"
