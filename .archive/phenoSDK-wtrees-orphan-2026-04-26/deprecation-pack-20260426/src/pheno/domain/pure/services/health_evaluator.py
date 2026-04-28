from __future__ import annotations

from typing import TYPE_CHECKING

from ..value_objects.health_status import HealthState, HealthStatus

if TYPE_CHECKING:
    from ..entities.service import Service


class HealthEvaluator:
    """
    Aggregates the health of service participants into a single status.
    """

    @staticmethod
    def evaluate(service: Service) -> HealthStatus:
        process_statuses = [process.health for process in service.processes()]
        if not process_statuses:
            return HealthStatus(HealthState.UNKNOWN, details=("no process data",))

        global_status = process_statuses[0]
        if len(process_statuses) > 1:
            global_status = global_status.combine(process_statuses[1:])

        return global_status

    @staticmethod
    def derive_service_health(service: Service) -> HealthStatus:
        """
        Provide a convenience hook for updating the aggregate health.
        """
        status = HealthEvaluator.evaluate(service)
        service.reconcile_health(status)
        return status
