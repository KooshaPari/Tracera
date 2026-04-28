"""
Event propagation utilities for capture/target/bubble phases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..types import EventPhase

if TYPE_CHECKING:
    from ..event_bus.bus import EventBus
    from ..models import Event


class EventPropagation:
    """
    Handle capture and bubble phase dispatch across a propagation path.
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._propagation_path: list[Any] = []

    # ------------------------------------------------------------------ #
    # Path management
    # ------------------------------------------------------------------ #
    def set_propagation_path(self, path: list[Any]) -> None:
        """
        Set the ordered path for propagation (target last).
        """
        self._propagation_path = path

    # ------------------------------------------------------------------ #
    # Synchronous propagation
    # ------------------------------------------------------------------ #
    def propagate_event(self, event: Event) -> None:
        """
        Dispatch an event through capture, target, and bubble phases.
        """
        if not self._propagation_path:
            self.event_bus.emit(event)
            return

        # Capture phase (outer to inner)
        event.phase = EventPhase.CAPTURE
        for target in reversed(self._propagation_path):
            if event.propagation_stopped:
                break
            event.current_target = target
            self.event_bus.emit(event)

        # Target phase
        if not event.propagation_stopped:
            event.phase = EventPhase.TARGET
            event.current_target = self._propagation_path[-1]
            self.event_bus.emit(event)

        # Bubble phase (inner to outer)
        if event.bubbles and not event.propagation_stopped:
            event.phase = EventPhase.BUBBLE
            for target in self._propagation_path[:-1]:
                if event.propagation_stopped:
                    break
                event.current_target = target
                self.event_bus.emit(event)

    # ------------------------------------------------------------------ #
    # Asynchronous propagation
    # ------------------------------------------------------------------ #
    async def propagate_event_async(self, event: Event) -> None:
        """
        Asynchronously dispatch an event across the propagation path.
        """
        if not self._propagation_path:
            await self.event_bus.emit_async(event)
            return

        event.phase = EventPhase.CAPTURE
        for target in reversed(self._propagation_path):
            if event.propagation_stopped:
                break
            event.current_target = target
            await self.event_bus.emit_async(event)

        if not event.propagation_stopped:
            event.phase = EventPhase.TARGET
            event.current_target = self._propagation_path[-1]
            await self.event_bus.emit_async(event)

        if event.bubbles and not event.propagation_stopped:
            event.phase = EventPhase.BUBBLE
            for target in self._propagation_path[:-1]:
                if event.propagation_stopped:
                    break
                event.current_target = target
                await self.event_bus.emit_async(event)


__all__ = ["EventPropagation"]
