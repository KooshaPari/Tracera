"""DTOs powering the pheno-sdk application layer use cases."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pheno.domain.value_objects.infrastructure import ServiceStatusEnum


@dataclass(frozen=True)
class OperationContext:
    """Optional metadata about who triggered an operation."""

    actor: str | None = None
    correlation_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def merged(self, extra: Mapping[str, Any]) -> OperationContext:
        """Return a copy with merged metadata."""

        if not extra:
            return self
        combined = dict(self.metadata)
        combined.update(extra)
        return replace(self, metadata=combined)


@dataclass(frozen=True)
class AllocatePortRequest:
    """Parameters for dynamic port allocation."""

    service_name: str
    environment: str | None = None
    preferred_port: int | None = None
    protocol: str = "tcp"
    tags: Mapping[str, Any] = field(default_factory=dict)
    context: OperationContext | None = None


@dataclass(frozen=True)
class CreateTunnelRequest:
    """Parameters to create a connectivity tunnel for a service."""

    service_name: str
    environment: str | None = None
    local_port: int | None = None
    remote_host: str = "localhost"
    remote_port: int | None = None
    protocol: str = "tcp"
    annotations: Mapping[str, Any] = field(default_factory=dict)
    context: OperationContext | None = None


@dataclass(frozen=True)
class StartServiceRequest:
    """Parameters required to start a service."""

    service_name: str
    environment: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    wait_for_health: bool = True
    health_timeout_seconds: float = 30.0
    port_request: AllocatePortRequest | None = None
    tunnel_request: CreateTunnelRequest | None = None
    context: OperationContext | None = None


@dataclass(frozen=True)
class StopServiceRequest:
    """Parameters required to stop a service."""

    service_name: str
    environment: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    force: bool = False
    release_allocated_port: bool = False
    close_tunnel: bool = False
    context: OperationContext | None = None


@dataclass(frozen=True)
class HealthCheckRequest:
    """Parameters to perform a health check against a service."""

    service_name: str
    environment: str | None = None
    endpoint: str | None = None
    timeout_seconds: float = 5.0
    context: OperationContext | None = None


@dataclass(frozen=True)
class ServiceOperationResult:
    """Result metadata returned from service start/stop operations."""

    service_name: str
    status: ServiceStatusEnum
    environment: str | None = None
    pid: int | None = None
    port: int | None = None
    tunnel_url: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def with_status(
        self,
        status: ServiceStatusEnum,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> ServiceOperationResult:
        """Return a copy with updated status and optional metadata merge."""

        new_metadata = dict(self.metadata)
        if metadata:
            new_metadata.update(metadata)
        return replace(self, status=status, metadata=new_metadata)


@dataclass(frozen=True)
class HealthCheckResult:
    """Outcome of a health check."""

    service_name: str
    status: ServiceStatusEnum
    environment: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TunnelInfo:
    """Information describing a created tunnel."""

    service_name: str
    tunnel_url: str
    environment: str | None = None
    local_port: int | None = None
    remote_host: str | None = None
    remote_port: int | None = None
    protocol: str = "tcp"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PortAllocationResult:
    """Information returned from a port allocation request."""

    service_name: str
    port: int
    protocol: str = "tcp"
    environment: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


__all__ = [
    "AllocatePortRequest",
    "CreateTunnelRequest",
    "HealthCheckRequest",
    "HealthCheckResult",
    "OperationContext",
    "PortAllocationResult",
    "ServiceOperationResult",
    "StartServiceRequest",
    "StopServiceRequest",
    "TunnelInfo",
]
