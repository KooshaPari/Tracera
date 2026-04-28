from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.port_number import PortNumber


@dataclass(frozen=True)
class TunnelEvent:
    service_id: str
    tunnel_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class TunnelEstablished(TunnelEvent):
    source_port: PortNumber
    target_host: str
    target_port: PortNumber


@dataclass(frozen=True)
class TunnelClosed(TunnelEvent):
    reason: str | None = None
