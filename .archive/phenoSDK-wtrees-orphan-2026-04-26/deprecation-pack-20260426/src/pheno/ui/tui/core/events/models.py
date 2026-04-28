"""
Event data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .types import EventPhase


@dataclass
class Event:
    """
    Runtime representation of a UI event.
    """

    type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    target: Any | None = None
    current_target: Any | None = None
    phase: EventPhase = EventPhase.TARGET
    bubbles: bool = True
    cancelable: bool = True
    default_prevented: bool = False
    propagation_stopped: bool = False

    def prevent_default(self) -> None:
        """
        Mark the event as having its default action prevented.
        """
        if self.cancelable:
            self.default_prevented = True

    def stop_propagation(self) -> None:
        """
        Stop further propagation after current handlers.
        """
        self.propagation_stopped = True

    def stop_immediate_propagation(self) -> None:
        """
        Alias for stop_propagation to match DOM semantics.
        """
        self.stop_propagation()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the event to a dictionary.
        """
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "target": str(self.target) if self.target else None,
            "current_target": str(self.current_target) if self.current_target else None,
            "phase": self.phase.value,
            "bubbles": self.bubbles,
            "cancelable": self.cancelable,
            "default_prevented": self.default_prevented,
            "propagation_stopped": self.propagation_stopped,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Event:
        """
        Deserialize an event from a dictionary.
        """
        return cls(
            type=payload["type"],
            data=payload.get("data", {}),
            timestamp=(
                datetime.fromisoformat(payload["timestamp"])
                if "timestamp" in payload
                else datetime.now()
            ),
            target=payload.get("target"),
            current_target=payload.get("current_target"),
            phase=EventPhase(payload.get("phase", "target")),
            bubbles=payload.get("bubbles", True),
            cancelable=payload.get("cancelable", True),
            default_prevented=payload.get("default_prevented", False),
            propagation_stopped=payload.get("propagation_stopped", False),
        )


__all__ = ["Event"]
