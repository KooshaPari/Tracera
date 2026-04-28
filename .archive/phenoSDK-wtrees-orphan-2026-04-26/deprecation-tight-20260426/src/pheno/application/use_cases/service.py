"""
Service use cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.application.dtos.service import (
    CreateServiceDTO,
    ServiceDTO,
    ServiceFilterDTO,
    ServiceHealthDTO,
)
from pheno.domain.entities.service import Service
from pheno.domain.exceptions.infrastructure import (
    ServiceAlreadyExistsError,
    ServiceNotFoundError,
)
from pheno.domain.value_objects.common import ServiceId

if TYPE_CHECKING:
    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import ServiceRepository


class CreateServiceUseCase:
    """
    Use case for creating a new service.
    """

    def __init__(
        self,
        service_repository: ServiceRepository,
        event_publisher: EventPublisher,
    ):
        self.service_repository = service_repository
        self.event_publisher = event_publisher

    async def execute(self, dto: CreateServiceDTO) -> ServiceDTO:
        """
        Create a new service.
        """
        # Check if service already exists
        name, port = dto.to_domain_params()
        existing_service = await self.service_repository.find_by_name(name)
        if existing_service:
            raise ServiceAlreadyExistsError(name.value)

        # Create service entity
        service = Service.create(name, port)
        if isinstance(service, tuple):
            service = service[0]

        # Save to repository
        await self.service_repository.save(service)

        # Publish domain events
        for event in service.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        service.clear_events()

        return ServiceDTO.from_entity(service)


class StartServiceUseCase:
    """
    Use case for starting a service.
    """

    def __init__(
        self,
        service_repository: ServiceRepository,
        event_publisher: EventPublisher,
    ):
        self.service_repository = service_repository
        self.event_publisher = event_publisher

    async def execute(self, service_id: str) -> ServiceDTO:
        """
        Start a service.
        """
        # Find service
        service = await self.service_repository.find_by_id(ServiceId(service_id))
        if not service:
            raise ServiceNotFoundError(service_id)

        # Start service
        service.start()

        # Save to repository
        await self.service_repository.save(service)

        # Publish domain events
        for event in service.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        service.clear_events()

        return ServiceDTO.from_entity(service)


class StopServiceUseCase:
    """
    Use case for stopping a service.
    """

    def __init__(
        self,
        service_repository: ServiceRepository,
        event_publisher: EventPublisher,
    ):
        self.service_repository = service_repository
        self.event_publisher = event_publisher

    async def execute(self, service_id: str) -> ServiceDTO:
        """
        Stop a service.
        """
        # Find service
        service = await self.service_repository.find_by_id(ServiceId(service_id))
        if not service:
            raise ServiceNotFoundError(service_id)

        # Stop service
        service.stop()

        # Save to repository
        await self.service_repository.save(service)

        # Publish domain events
        for event in service.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        service.clear_events()

        return ServiceDTO.from_entity(service)


class GetServiceUseCase:
    """
    Use case for getting a service by ID.
    """

    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository

    async def execute(self, service_id: str) -> ServiceDTO:
        """
        Get a service by ID.
        """
        service = await self.service_repository.find_by_id(ServiceId(service_id))
        if not service:
            raise ServiceNotFoundError(service_id)

        return ServiceDTO.from_entity(service)


class ListServicesUseCase:
    """
    Use case for listing services.
    """

    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository

    async def execute(self, filter_dto: ServiceFilterDTO) -> list[ServiceDTO]:
        """
        List services with optional filters.
        """
        services = await self.service_repository.find_all(
            limit=filter_dto.limit,
            offset=filter_dto.offset,
        )
        return [ServiceDTO.from_entity(s) for s in services]


class GetServiceHealthUseCase:
    """
    Use case for getting service health status.
    """

    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository

    async def execute(self) -> ServiceHealthDTO:
        """
        Get service health status.
        """
        # Get all services
        all_services = await self.service_repository.find_all(limit=1000, offset=0)
        total = len(all_services)

        # Count by status
        running = sum(1 for s in all_services if s.status.value == "running")
        stopped = sum(1 for s in all_services if s.status.value == "stopped")
        failed = sum(1 for s in all_services if s.status.value == "failed")

        # Calculate health percentage
        healthy_percentage = (running / total * 100) if total > 0 else 0.0

        return ServiceHealthDTO(
            total_services=total,
            running=running,
            stopped=stopped,
            failed=failed,
            healthy_percentage=healthy_percentage,
        )
