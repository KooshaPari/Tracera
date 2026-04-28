from __future__ import annotations

from typing import TYPE_CHECKING

from ..entities.port import Port
from ..events.port_events import PortAllocated, PortReleased

if TYPE_CHECKING:
    from ..entities.service import Service
    from ..value_objects.port_number import PortNumber


class PortAllocator:
    """
    Ensures port reservations are unique within a service aggregate.
    """

    @staticmethod
    def allocate(
        service: Service,
        number: PortNumber,
        protocol: str = "tcp",
        endpoint: str | None = None,
        description: str = "",
    ) -> tuple[Port, PortAllocated]:
        if service.port(number):
            raise ValueError(f"Port {int(number)} already allocated for service")
        port = Port(
            service_id=service.service_id,
            number=number,
            protocol=protocol,
            endpoint=endpoint,
            description=description,
        )
        service.reserve_port(port)
        event = PortAllocated(
            service_id=service.service_id,
            number=number,
            protocol=protocol,
            endpoint=endpoint,
        )
        return port, event

    @staticmethod
    def release(service: Service, number: PortNumber, reason: str | None = None) -> PortReleased:
        port = service.release_port(number)
        return PortReleased(
            service_id=service.service_id,
            number=port.number,
            reason=reason,
        )
