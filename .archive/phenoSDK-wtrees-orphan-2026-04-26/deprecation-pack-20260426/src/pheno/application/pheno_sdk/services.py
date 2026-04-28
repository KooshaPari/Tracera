"""Application services coordinating pheno-sdk operations."""

from __future__ import annotations

import contextlib
from collections.abc import Mapping
from dataclasses import replace as dc_replace
from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from .ports import (
        HealthCheckPort,
        PortAllocationPort,
        ServiceLifecyclePort,
        TunnelManagementPort,
    )


class ServiceLifecycleService:
    """Coordinate service lifecycle operations across infrastructure ports."""

    def __init__(
        self,
        lifecycle_port: ServiceLifecyclePort,
        *,
        health_port: HealthCheckPort | None = None,
        tunnel_port: TunnelManagementPort | None = None,
        port_allocator: PortAllocationPort | None = None,
    ) -> None:
        self._lifecycle_port = lifecycle_port
        self._health_port = health_port
        self._tunnel_port = tunnel_port
        self._port_allocator = port_allocator

    async def start_service(self, request: StartServiceRequest) -> ServiceOperationResult:
        """Start a service and optionally perform health and tunnel setup."""

        allocation: PortAllocationResult | None = None
        tunnel_info: TunnelInfo | None = None
        updated_request = request

        try:
            if self._port_allocator and request.port_request:
                port_request = _inherit_context(request.port_request, request.context)
                allocation = await self._port_allocator.allocate(port_request)
                updated_request = _attach_port_parameters(request, allocation)

            result = await self._lifecycle_port.start_service(updated_request)
            metadata = _copy_metadata(result.metadata)

            if allocation:
                metadata["port_allocation"] = _allocation_dict(allocation)
                if result.port is None:
                    result = dc_replace(result, port=allocation.port)

            if self._tunnel_port and request.tunnel_request:
                tunnel_info = await self._create_tunnel(request, result, allocation)
                metadata["tunnel"] = _tunnel_dict(tunnel_info)
                result = dc_replace(result, tunnel_url=tunnel_info.tunnel_url)

            if self._health_port and request.wait_for_health:
                health_result = await self._health_port.check(_health_request(request))
                metadata["health"] = health_result.details
                result = dc_replace(result, status=health_result.status)

            return dc_replace(result, metadata=metadata)
        except Exception:
            await _safe_release(self._port_allocator, allocation)
            if tunnel_info:
                await _safe_close(self._tunnel_port, tunnel_info)
            raise

    async def stop_service(self, request: StopServiceRequest) -> ServiceOperationResult:
        """Stop a service, closing any optional dependencies."""

        result = await self._lifecycle_port.stop_service(request)
        metadata = _copy_metadata(result.metadata)

        if request.close_tunnel and self._tunnel_port:
            tunnel_info = _tunnel_from_request(request, result)
            if tunnel_info:
                await _safe_close(self._tunnel_port, tunnel_info)
                metadata["tunnel_closed"] = True

        if request.release_allocated_port and self._port_allocator:
            allocation = _allocation_from_request(request)
            if allocation:
                await _safe_release(self._port_allocator, allocation)
                metadata["port_released"] = allocation.port

        return dc_replace(result, metadata=metadata)

    async def _create_tunnel(
        self,
        request: StartServiceRequest,
        result: ServiceOperationResult,
        allocation: PortAllocationResult | None,
    ) -> TunnelInfo:
        assert self._tunnel_port is not None
        tunnel_request = _inherit_context(request.tunnel_request, request.context)

        if tunnel_request.local_port is None:
            preferred_port = result.port or (allocation.port if allocation else None)
            tunnel_request = dc_replace(tunnel_request, local_port=preferred_port)

        tunnel_info = await self._tunnel_port.create(tunnel_request)
        if allocation and tunnel_info.local_port is None:
            tunnel_info = dc_replace(tunnel_info, local_port=allocation.port)
        return tunnel_info


class HealthMonitoringService:
    """Wrap health checks with a dedicated service."""

    def __init__(self, health_port: HealthCheckPort) -> None:
        self._health_port = health_port

    async def check(self, request: HealthCheckRequest) -> HealthCheckResult:
        """Delegate to the configured health check port."""

        return await self._health_port.check(request)


class TunnelOrchestrationService:
    """Manage tunnel lifecycle operations."""

    def __init__(
        self,
        tunnel_port: TunnelManagementPort,
        *,
        port_allocator: PortAllocationPort | None = None,
    ) -> None:
        self._tunnel_port = tunnel_port
        self._port_allocator = port_allocator

    async def create_tunnel(self, request: CreateTunnelRequest) -> TunnelInfo:
        """Create a tunnel, allocating a local port when needed."""

        allocation: PortAllocationResult | None = None
        effective_request = request

        try:
            if self._port_allocator and request.local_port is None:
                allocation_request = AllocatePortRequest(
                    service_name=request.service_name,
                    environment=request.environment,
                    preferred_port=request.remote_port,
                    protocol=request.protocol,
                    tags={"purpose": "tunnel"},
                    context=request.context,
                )
                allocation = await self._port_allocator.allocate(allocation_request)
                effective_request = dc_replace(request, local_port=allocation.port)

            tunnel_info = await self._tunnel_port.create(effective_request)
            metadata = _copy_metadata(tunnel_info.metadata)
            if allocation:
                metadata["port_allocation"] = _allocation_dict(allocation)
            return dc_replace(tunnel_info, metadata=metadata)
        except Exception:
            await _safe_release(self._port_allocator, allocation)
            raise

    async def close_tunnel(self, tunnel_info: TunnelInfo) -> None:
        """Close a tunnel and release any dynamic port."""

        await self._tunnel_port.close(tunnel_info)
        if not self._port_allocator:
            return

        allocation_meta = tunnel_info.metadata.get("port_allocation")
        if isinstance(allocation_meta, PortAllocationResult):
            await _safe_release(self._port_allocator, allocation_meta)


class PortProvisioningService:
    """Simple wrapper around the port allocation port."""

    def __init__(self, port_allocator: PortAllocationPort) -> None:
        self._port_allocator = port_allocator

    async def allocate(self, request: AllocatePortRequest) -> PortAllocationResult:
        """Allocate a port."""

        return await self._port_allocator.allocate(request)

    async def release(self, allocation: PortAllocationResult) -> None:
        """Release a port allocation."""

        await self._port_allocator.release(allocation)


def _inherit_context(obj: Any, context: Any) -> Any:
    if not hasattr(obj, "context") or obj.context is not None or context is None:
        return obj
    return dc_replace(obj, context=context)


def _attach_port_parameters(
    request: StartServiceRequest,
    allocation: PortAllocationResult,
) -> StartServiceRequest:
    params = dict(request.parameters)
    params.setdefault("allocated_port", allocation.port)
    params.setdefault("protocol", allocation.protocol)
    return dc_replace(request, parameters=params)


def _health_request(request: StartServiceRequest) -> HealthCheckRequest:
    endpoint = request.parameters.get("health_endpoint")
    return HealthCheckRequest(
        service_name=request.service_name,
        environment=request.environment,
        endpoint=endpoint if isinstance(endpoint, str) else None,
        timeout_seconds=request.health_timeout_seconds,
        context=request.context,
    )


def _copy_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(metadata) if isinstance(metadata, Mapping) else {}


def _allocation_from_request(request: StopServiceRequest) -> PortAllocationResult | None:
    value = request.parameters.get("allocation")
    return value if isinstance(value, PortAllocationResult) else None


def _tunnel_from_request(
    request: StopServiceRequest,
    result: ServiceOperationResult,
) -> TunnelInfo | None:
    value = request.parameters.get("tunnel")
    if isinstance(value, TunnelInfo):
        return value
    if result.tunnel_url:
        return TunnelInfo(
            service_name=result.service_name,
            tunnel_url=result.tunnel_url,
            environment=request.environment,
            local_port=result.port,
        )
    return None


async def _safe_release(
    allocator: PortAllocationPort | None,
    allocation: PortAllocationResult | None,
) -> None:
    if allocator and allocation:
        with contextlib.suppress(Exception):
            await allocator.release(allocation)


async def _safe_close(
    tunnel_port: TunnelManagementPort | None,
    tunnel_info: TunnelInfo | None,
) -> None:
    if tunnel_port and tunnel_info:
        with contextlib.suppress(Exception):
            await tunnel_port.close(tunnel_info)


def _allocation_dict(allocation: PortAllocationResult) -> dict[str, Any]:
    return {
        "service_name": allocation.service_name,
        "port": allocation.port,
        "protocol": allocation.protocol,
        "environment": allocation.environment,
        "metadata": allocation.metadata,
    }


def _tunnel_dict(tunnel: TunnelInfo) -> dict[str, Any]:
    return {
        "service_name": tunnel.service_name,
        "tunnel_url": tunnel.tunnel_url,
        "protocol": tunnel.protocol,
        "environment": tunnel.environment,
        "local_port": tunnel.local_port,
        "remote_host": tunnel.remote_host,
        "remote_port": tunnel.remote_port,
        "metadata": tunnel.metadata,
    }


__all__ = [
    "HealthMonitoringService",
    "PortProvisioningService",
    "ServiceLifecycleService",
    "TunnelOrchestrationService",
]
