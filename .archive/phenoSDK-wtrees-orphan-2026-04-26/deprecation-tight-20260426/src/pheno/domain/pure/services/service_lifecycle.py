from __future__ import annotations

from typing import TYPE_CHECKING

from ..events.resource_events import ResourceAdded
from ..events.service_events import ServiceResourceLinked, ServiceStatusChanged

if TYPE_CHECKING:
    from ..entities.resource import Resource
    from ..entities.service import Service
    from ..value_objects.health_status import HealthStatus
    from ..value_objects.service_status import ServicePhase


class ServiceLifecycle:
    """
    Domain service coordinating lifecycle changes for a Service aggregate.
    """

    @staticmethod
    def change_status(
        service: Service,
        target: ServicePhase,
        reason: str | None = None,
    ) -> ServiceStatusChanged:
        previous = service.status.phase
        service.update_status(target)
        return ServiceStatusChanged(
            service_id=service.service_id,
            previous=previous,
            current=target,
            reason=reason,
        )

    @staticmethod
    def link_resource(
        service: Service, resource: Resource,
    ) -> tuple[ResourceAdded, ServiceResourceLinked]:
        service.register_resource(resource)
        added = ResourceAdded(
            service_id=service.service_id,
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
        )
        linked = ServiceResourceLinked(
            service_id=service.service_id,
            resource_id=resource.resource_id,
        )
        return added, linked

    @staticmethod
    def update_health(service: Service, status: HealthStatus) -> None:
        service.reconcile_health(status)
