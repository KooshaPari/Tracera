"""
Service DTOs for data transfer between layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pheno.domain.entities.service import Service
from pheno.domain.value_objects.common import ServiceId
from pheno.domain.value_objects.infrastructure import (
    ServiceName,
    ServicePort,
    ServiceStatus,
)


@dataclass(frozen=True)
class CreateServiceDTO:
    """
    DTO for creating a new service.
    """

    name: str
    port: int
    protocol: str = "http"

    def to_domain_params(self) -> tuple[ServiceName, ServicePort]:
        """
        Convert to domain entity creation parameters.
        """
        return (
            ServiceName(self.name),
            ServicePort(self.port, self.protocol),
        )


@dataclass(frozen=True)
class UpdateServiceDTO:
    """
    DTO for updating a service.
    """

    service_id: str
    status: str | None = None

    def get_service_id(self) -> ServiceId:
        """
        Get the service ID as a domain value object.
        """
        return ServiceId(self.service_id)

    def get_status(self) -> ServiceStatus | None:
        """
        Get the status as a domain value object.
        """
        return ServiceStatus(self.status) if self.status else None


@dataclass(frozen=True)
class ServiceDTO:
    """
    DTO for service data.
    """

    id: str
    name: str
    port: int
    protocol: str
    status: str
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    stopped_at: datetime | None = None

    @classmethod
    def from_entity(cls, service: Service) -> ServiceDTO:
        """
        Create DTO from domain entity.
        """
        return cls(
            id=str(service.id.value),
            name=service.name.value,
            port=service.port.port,
            protocol=service.port.protocol,
            status=service.status.value,
            created_at=service.created_at,
            updated_at=service.updated_at,
            started_at=service.started_at,
            stopped_at=service.stopped_at,
        )


@dataclass(frozen=True)
class ServiceFilterDTO:
    """
    DTO for filtering services.
    """

    name: str | None = None
    status: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class ServiceHealthDTO:
    """
    DTO for service health status.
    """

    total_services: int
    running: int
    stopped: int
    failed: int
    healthy_percentage: float
