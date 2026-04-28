from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.port_number import PortNumber


@dataclass(frozen=True)
class PortEvent:
    service_id: str
    number: PortNumber
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PortAllocated(PortEvent):
    protocol: str = "tcp"
    endpoint: str | None = None


@dataclass(frozen=True)
class PortReleased(PortEvent):
    reason: str | None = None
