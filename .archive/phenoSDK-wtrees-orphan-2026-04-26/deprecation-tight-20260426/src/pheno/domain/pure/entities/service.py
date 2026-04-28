from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..value_objects.health_status import HealthState, HealthStatus
from ..value_objects.service_status import ServicePhase, ServiceStatus

if TYPE_CHECKING:
    from ..value_objects.port_number import PortNumber
    from ..value_objects.resource_type import ResourceType
    from .port import Port
    from .process import Process
    from .resource import Resource
    from .tunnel import Tunnel


@dataclass
class Service:
    """
    Aggregate root representing a deployable unit within the platform.
    """

    service_id: str
    name: str
    description: str = ""
    _status: ServiceStatus = field(
        default_factory=lambda: ServiceStatus(ServicePhase.INACTIVE),
    )
    _health: HealthStatus = field(
        default_factory=lambda: HealthStatus(state=HealthState.UNKNOWN),
    )
    _resources: dict[str, Resource] = field(default_factory=dict, init=False)
    _processes: dict[str, Process] = field(default_factory=dict, init=False)
    _ports: dict[int, Port] = field(default_factory=dict, init=False)
    _tunnels: dict[str, Tunnel] = field(default_factory=dict, init=False)

    def register_resource(self, resource: Resource) -> None:
        if resource.service_id != self.service_id:
            raise ValueError("Resource must belong to the service being mutated")
        if resource.resource_id in self._resources:
            raise ValueError(f"Resource {resource.resource_id} already registered")
        self._resources[resource.resource_id] = resource

    def unregister_resource(self, resource_id: str) -> Resource:
        try:
            return self._resources.pop(resource_id)
        except KeyError as exc:
            raise KeyError(f"Resource {resource_id} not found") from exc

    def attach_process(self, process: Process) -> None:
        if process.service_id != self.service_id:
            raise ValueError("Process must belong to the service being mutated")
        if process.process_id in self._processes:
            raise ValueError(f"Process {process.process_id} already registered")
        self._processes[process.process_id] = process

    def detach_process(self, process_id: str) -> Process:
        try:
            return self._processes.pop(process_id)
        except KeyError as exc:
            raise KeyError(f"Process {process_id} not found") from exc

    def reserve_port(self, port: Port) -> None:
        port_number = int(port.number)
        if port_number in self._ports:
            existing = self._ports[port_number]
            if existing.endpoint != port.endpoint:
                raise ValueError(
                    f"Port {port_number} already reserved by endpoint "
                    f"{existing.endpoint}",
                )
            return
        self._ports[port_number] = port

    def release_port(self, port_number: PortNumber) -> Port:
        try:
            return self._ports.pop(int(port_number))
        except KeyError as exc:
            raise KeyError(f"Port {int(port_number)} not reserved") from exc

    def track_tunnel(self, tunnel: Tunnel) -> None:
        if tunnel.service_id != self.service_id:
            raise ValueError("Tunnel must belong to the service being mutated")
        if tunnel.tunnel_id in self._tunnels:
            raise ValueError(f"Tunnel {tunnel.tunnel_id} already tracked")
        self._tunnels[tunnel.tunnel_id] = tunnel

    def remove_tunnel(self, tunnel_id: str) -> Tunnel:
        try:
            return self._tunnels.pop(tunnel_id)
        except KeyError as exc:
            raise KeyError(f"Tunnel {tunnel_id} not found") from exc

    def update_status(self, target: ServicePhase) -> None:
        self._status.assert_transition(target)
        self._status = ServiceStatus(target)

    def reconcile_health(self, status: HealthStatus) -> None:
        self._health = status

    def resources(self) -> tuple[Resource, ...]:
        return tuple(self._resources.values())

    def resources_by_type(self, resource_type: ResourceType) -> tuple[Resource, ...]:
        return tuple(
            resource
            for resource in self._resources.values()
            if resource.resource_type == resource_type
        )

    def processes(self) -> tuple[Process, ...]:
        return tuple(self._processes.values())

    def ports(self) -> tuple[Port, ...]:
        return tuple(self._ports.values())

    def tunnels(self) -> tuple[Tunnel, ...]:
        return tuple(self._tunnels.values())

    @property
    def status(self) -> ServiceStatus:
        return self._status

    @property
    def health(self) -> HealthStatus:
        return self._health

    def resource(self, resource_id: str) -> Resource | None:
        return self._resources.get(resource_id)

    def process(self, process_id: str) -> Process | None:
        return self._processes.get(process_id)

    def port(self, port_number: PortNumber) -> Port | None:
        return self._ports.get(int(port_number))

    def tunnel(self, tunnel_id: str) -> Tunnel | None:
        return self._tunnels.get(tunnel_id)

    def __hash__(self) -> int:  # pragma: no cover - entity identity
        return hash(self.service_id)
