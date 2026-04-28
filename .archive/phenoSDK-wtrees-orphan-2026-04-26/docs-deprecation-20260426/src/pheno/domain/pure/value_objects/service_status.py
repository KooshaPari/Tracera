from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable


class ServicePhase(Enum):
    """High-level phases that a service can inhabit."""

    INACTIVE = "inactive"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class ServiceStatus:
    """
    Value object wrapping the phase of a service and providing transition guards.

    The value object embeds transition rules so that aggregates can enforce
    the allowed lifecycle without duplicating logic.
    """

    phase: ServicePhase

    _TRANSITIONS: ClassVar[dict[ServicePhase, set[ServicePhase]]] = {
        ServicePhase.INACTIVE: {ServicePhase.STARTING, ServicePhase.STOPPED},
        ServicePhase.STARTING: {
            ServicePhase.RUNNING,
            ServicePhase.DEGRADED,
            ServicePhase.FAILED,
        },
        ServicePhase.RUNNING: {
            ServicePhase.DEGRADED,
            ServicePhase.STOPPING,
            ServicePhase.FAILED,
        },
        ServicePhase.DEGRADED: {
            ServicePhase.RUNNING,
            ServicePhase.STOPPING,
            ServicePhase.FAILED,
        },
        ServicePhase.STOPPING: {ServicePhase.STOPPED, ServicePhase.FAILED},
        ServicePhase.STOPPED: {ServicePhase.STARTING, ServicePhase.INACTIVE},
        ServicePhase.FAILED: {ServicePhase.STARTING, ServicePhase.STOPPING},
    }

    def can_transition_to(self, target: ServicePhase) -> bool:
        """Return True when the transition to the target phase is allowed."""
        return target in self._TRANSITIONS[self.phase]

    def assert_transition(self, target: ServicePhase) -> None:
        """
        Raise a ValueError if the transition to the target phase is not permitted.
        """
        if not self.can_transition_to(target):
            raise ValueError(
                f"Cannot transition service from {self.phase.value} "
                f"to {target.value}",
            )

    def in_any_of(self, phases: Iterable[ServicePhase]) -> bool:
        """
        Returns True if the current phase is contained in the provided phases.
        """
        return self.phase in set(phases)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.phase.value
