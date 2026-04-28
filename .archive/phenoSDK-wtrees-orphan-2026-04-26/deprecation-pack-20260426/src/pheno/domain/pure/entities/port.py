from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.port_number import PortNumber


@dataclass
class Port:
    """
    Entity that records a port reservation belonging to a service.
    """

    service_id: str
    number: PortNumber
    protocol: str = "tcp"
    endpoint: str | None = None
    description: str = ""

    def assign_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def clear_endpoint(self) -> None:
        self.endpoint = None

    def __hash__(self) -> int:  # pragma: no cover - entity identity
        return hash((self.service_id, int(self.number), self.protocol))
