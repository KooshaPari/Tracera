from __future__ import annotations

from dataclasses import dataclass, field

from ..value_objects.health_status import HealthState, HealthStatus


@dataclass
class Process:
    """
    Entity representing a long running activity owned by a service.
    """

    process_id: str
    service_id: str
    name: str
    resource_id: str | None = None
    command: str | None = None
    _health: HealthStatus = field(
        default_factory=lambda: HealthStatus(HealthState.UNKNOWN),
    )

    def mark_started(self) -> None:
        self._health = HealthStatus(HealthState.HEALTHY)

    def mark_degraded(self, reason: str) -> None:
        self._health = HealthStatus(HealthState.DEGRADED, details=(reason,))

    def mark_stopped(self, reason: str = "") -> None:
        details = (reason,) if reason else ()
        self._health = HealthStatus(HealthState.UNKNOWN, details=details)

    def mark_crashed(self, reason: str) -> None:
        self._health = HealthStatus(HealthState.UNHEALTHY, details=(reason,))

    @property
    def health(self) -> HealthStatus:
        return self._health

    def __hash__(self) -> int:  # pragma: no cover - entity identity
        return hash(self.process_id)
