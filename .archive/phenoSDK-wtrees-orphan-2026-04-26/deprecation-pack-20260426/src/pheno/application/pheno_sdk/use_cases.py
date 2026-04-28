"""Use case entrypoints for the pheno-sdk application layer."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    from .services import (
        HealthMonitoringService,
        PortProvisioningService,
        ServiceLifecycleService,
        TunnelOrchestrationService,
    )


class StartServiceUseCase:
    """Start a service through the lifecycle service."""

    def __init__(self, service: ServiceLifecycleService) -> None:
        self._service = service

    async def execute(self, request: StartServiceRequest) -> ServiceOperationResult:
        """Execute the start service flow."""

        return await self._service.start_service(request)


class StopServiceUseCase:
    """Stop a service and release dependent resources."""

    def __init__(self, service: ServiceLifecycleService) -> None:
        self._service = service

    async def execute(self, request: StopServiceRequest) -> ServiceOperationResult:
        """Execute the stop service flow."""

        return await self._service.stop_service(request)


class CheckHealthUseCase:
    """Single service health check use case."""

    def __init__(self, service: HealthMonitoringService) -> None:
        self._service = service

    async def execute(self, request: HealthCheckRequest) -> HealthCheckResult:
        """Run the health check."""

        return await self._service.check(request)


class CreateTunnelUseCase:
    """Create a tunnel for a service."""

    def __init__(self, service: TunnelOrchestrationService) -> None:
        self._service = service

    async def execute(self, request: CreateTunnelRequest) -> TunnelInfo:
        """Execute the tunnel creation flow."""

        return await self._service.create_tunnel(request)


class AllocatePortUseCase:
    """Allocate or release ports for services."""

    def __init__(self, service: PortProvisioningService) -> None:
        self._service = service

    async def allocate(self, request: AllocatePortRequest) -> PortAllocationResult:
        """Allocate a port via the provisioning service."""

        return await self._service.allocate(request)

    async def release(self, allocation: PortAllocationResult) -> None:
        """Release a previously allocated port."""

        await self._service.release(allocation)


__all__ = [
    "AllocatePortUseCase",
    "CheckHealthUseCase",
    "CreateTunnelUseCase",
    "StartServiceUseCase",
    "StopServiceUseCase",
]
