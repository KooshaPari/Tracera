from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable


class HealthState(Enum):
    """Possible health states for domain entities."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class HealthStatus:
    """
    Value object carrying health information.

    Stores the qualitative state plus optional contextual details.
    """

    state: HealthState
    details: tuple[str, ...] = ()

    _SEVERITY: ClassVar[dict[HealthState, int]] = {
        HealthState.HEALTHY: 0,
        HealthState.UNKNOWN: 1,
        HealthState.DEGRADED: 2,
        HealthState.UNHEALTHY: 3,
    }

    def worsen(self, message: str) -> HealthStatus:
        """
        Return a new status that is one severity level worse with appended detail.
        """
        severity = self._SEVERITY[self.state]
        max_severity = max(self._SEVERITY.values())
        if severity >= max_severity:
            return HealthStatus(state=self.state, details=(*self.details, message))

        target_severity = min(severity + 1, max_severity)
        worse_state = next(
            state for state, level in self._SEVERITY.items() if level == target_severity
        )
        return HealthStatus(state=worse_state, details=(*self.details, message))

    def combine(self, others: Iterable[HealthStatus]) -> HealthStatus:
        """
        Combine several health statuses by selecting the worst severity.
        """
        candidate_states = [self.state]
        candidate_details = list(self.details)
        for status in others:
            candidate_states.append(status.state)
            candidate_details.extend(status.details)

        worst_state = max(candidate_states, key=self._SEVERITY.get)
        return HealthStatus(state=worst_state, details=tuple(candidate_details))

    def is_healthy(self) -> bool:
        return self.state is HealthState.HEALTHY

    def is_unknown(self) -> bool:
        return self.state is HealthState.UNKNOWN

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.state.value
