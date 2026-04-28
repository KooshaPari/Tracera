from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.service_status import ServicePhase


@dataclass(frozen=True)
class ServiceEvent:
    service_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ServiceStatusChanged(ServiceEvent):
    previous: ServicePhase
    current: ServicePhase
    reason: str | None = None


@dataclass(frozen=True)
class ServiceResourceLinked(ServiceEvent):
    resource_id: str
