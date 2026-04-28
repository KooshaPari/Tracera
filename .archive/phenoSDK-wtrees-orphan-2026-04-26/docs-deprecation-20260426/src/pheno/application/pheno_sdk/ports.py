"""Ports (interfaces) required by the pheno-sdk application services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .dtos import (
        AllocatePortRequest,
        CreateTunnelRequest,
        HealthCheckRequest,
        HealthCheckResult,
        PortAllocationResult,
        ServiceOperationResult,
        StartServiceRequest,
        StopServiceRequest,
        TunnelInfo,
    )


class ServiceLifecyclePort(Protocol):
    """Abstract operations to manage service lifecycles."""

    async def start_service(self, request: StartServiceRequest) -> ServiceOperationResult:
        """Start the target service and return runtime metadata."""

    async def stop_service(self, request: StopServiceRequest) -> ServiceOperationResult:
        """Stop the target service and return the final runtime metadata."""


class HealthCheckPort(Protocol):
    """Port for checking service health."""

    async def check(self, request: HealthCheckRequest) -> HealthCheckResult:
        """Run the health check and return the resulting status."""


class TunnelManagementPort(Protocol):
    """Port for managing tunnels to services."""

    async def create(self, request: CreateTunnelRequest) -> TunnelInfo:
        """Create a tunnel and return connection information."""

    async def close(self, tunnel: TunnelInfo) -> None:
        """Close a previously established tunnel."""


class PortAllocationPort(Protocol):
    """Port responsible for allocating network ports."""

    async def allocate(self, request: AllocatePortRequest) -> PortAllocationResult:
        """Allocate a port that matches the request constraints."""

    async def release(self, allocation: PortAllocationResult) -> None:
        """Release a previously allocated port."""


__all__ = [
    "HealthCheckPort",
    "PortAllocationPort",
    "ServiceLifecyclePort",
    "TunnelManagementPort",
]

