from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.port_number import PortNumber


@dataclass
class Tunnel:
    """
    Entity representing a network tunnel bound to a service.
    """

    tunnel_id: str
    service_id: str
    source_port: PortNumber
    target_host: str
    target_port: PortNumber
    description: str = ""
    _active: bool = field(default=False, init=False)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activated_at: datetime | None = None

    def activate(self) -> None:
        self._active = True
        self.last_activated_at = datetime.utcnow()

    def deactivate(self) -> None:
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    def __hash__(self) -> int:  # pragma: no cover - entity identity
        return hash(self.tunnel_id)
