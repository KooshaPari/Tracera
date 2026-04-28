"""
Service entity.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime

from pheno.domain.base import AggregateRoot
from pheno.domain.events import (
    ServiceCreated,
    ServiceFailed,
    ServiceStarted,
    ServiceStopped,
)
from pheno.domain.exceptions import (
    InvalidServiceStateError,
    ValidationError,
)
from pheno.domain.value_objects import (
    ServiceId,
    ServiceName,
    ServicePort,
    ServiceStatus,
)
from pheno.domain.value_objects.infrastructure import ServiceStatusEnum


@dataclass
class Service(AggregateRoot):
    """Service aggregate root.

    Represents a running service in the infrastructure.
    Manages service lifecycle and state transitions.

    Business Rules:
        - Service must have unique name
        - Service must have valid port
        - State transitions must follow valid paths
        - Only stopped services can be started
        - Only running services can be stopped
        - Service emits events for all state changes
    """

    name: ServiceName = field(default=None)
    port: ServicePort = field(default=None)
    status: ServiceStatus = field(default=None)
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    error_message: str | None = None

    @classmethod
    def create(
        cls,
        name: ServiceName,
        port: ServicePort,
    ) -> tuple["Service", ServiceCreated]:
        """Factory method to create a new service.

        Args:
            name: Service name
            port: Service port

        Returns:
            Tuple of (Service entity, ServiceCreated event)
        """
        service_id = ServiceId.generate()

        service = cls(
            id=str(service_id),
            name=name,
            port=port,
            status=ServiceStatus(ServiceStatusEnum.STOPPED),
        )

        event = ServiceCreated(
            aggregate_id=str(service_id),
            service_id=str(service_id),
            service_name=str(name),
            port=port.port,
        )

        service.add_event(event)
        return service, event

    def start(self) -> "Service":
        """Start the service.

        Returns:
            Updated service entity

        Raises:
            InvalidServiceStateError: If service cannot be started
        """
        new_status = ServiceStatus(ServiceStatusEnum.STARTING)

        if not self.status.can_transition_to(new_status):
            raise InvalidServiceStateError(str(self.status), str(new_status))

        starting_service = replace(
            self,
            status=new_status,
            updated_at=datetime.utcnow(),
        )

        # Immediately transition to running
        running_status = ServiceStatus(ServiceStatusEnum.RUNNING)
        now = datetime.utcnow()
        running_service = replace(
            starting_service,
            status=running_status,
            started_at=now,
            stopped_at=None,
            error_message=None,
            updated_at=now,
        )

        event = ServiceStarted(
            aggregate_id=str(self.id),
            service_id=str(self.id),
            service_name=str(self.name),
            port=self.port.port,
        )

        running_service.add_event(event)
        return running_service

    def stop(self, reason: str | None = None) -> "Service":
        """Stop the service.

        Args:
            reason: Optional reason for stopping

        Returns:
            Updated service entity

        Raises:
            InvalidServiceStateError: If service cannot be stopped
        """
        new_status = ServiceStatus(ServiceStatusEnum.STOPPING)

        if not self.status.can_transition_to(new_status):
            raise InvalidServiceStateError(str(self.status), str(new_status))

        stopping_service = replace(
            self,
            status=new_status,
            updated_at=datetime.utcnow(),
        )

        # Immediately transition to stopped
        stopped_status = ServiceStatus(ServiceStatusEnum.STOPPED)
        now = datetime.utcnow()
        stopped_service = replace(
            stopping_service,
            status=stopped_status,
            stopped_at=now,
            updated_at=now,
        )

        event = ServiceStopped(
            aggregate_id=str(self.id),
            service_id=str(self.id),
            service_name=str(self.name),
            reason=reason,
        )

        stopped_service.add_event(event)
        return stopped_service

    def fail(self, error_message: str) -> "Service":
        """Mark service as failed.

        Args:
            error_message: Error message describing the failure

        Returns:
            Updated service entity

        Raises:
            ValidationError: If error message is empty
        """
        if not error_message or not error_message.strip():
            raise ValidationError("Error message cannot be empty")

        now = datetime.utcnow()
        failed_service = replace(
            self,
            status=ServiceStatus(ServiceStatusEnum.FAILED),
            error_message=error_message.strip(),
            stopped_at=now,
            updated_at=now,
        )

        event = ServiceFailed(
            aggregate_id=str(self.id),
            service_id=str(self.id),
            service_name=str(self.name),
            error_message=error_message.strip(),
        )

        failed_service.add_event(event)
        return failed_service

    def is_healthy(self) -> bool:
        """
        Check if service is healthy (running).
        """
        return self.status.is_healthy()

    def is_transitioning(self) -> bool:
        """
        Check if service is in a transition state.
        """
        return self.status.is_transitioning()

    def uptime_seconds(self) -> float | None:
        """
        Get service uptime in seconds.
        """
        if not self.started_at:
            return None

        if self.stopped_at:
            return (self.stopped_at - self.started_at).total_seconds()

        return (datetime.utcnow() - self.started_at).total_seconds()

    def __str__(self) -> str:
        return f"Service({self.id}, {self.name}, {self.port}, {self.status})"
