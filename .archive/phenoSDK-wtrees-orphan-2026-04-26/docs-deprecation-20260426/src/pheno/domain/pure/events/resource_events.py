from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.resource_type import ResourceType


@dataclass(frozen=True)
class ResourceEvent:
    service_id: str
    resource_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ResourceAdded(ResourceEvent):
    resource_type: ResourceType | None = None


@dataclass(frozen=True)
class ResourceRemoved(ResourceEvent):
    reason: str | None = None
