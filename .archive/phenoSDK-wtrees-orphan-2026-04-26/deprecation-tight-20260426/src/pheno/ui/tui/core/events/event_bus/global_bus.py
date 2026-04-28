"""
Global event bus accessors and convenience helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Event
from ..propagation.propagation import EventPropagation
from .bus import EventBus

if TYPE_CHECKING:
    from ..handlers.handlers import HandlerCallable

_global_event_bus: EventBus | None = None
_global_propagation: EventPropagation | None = None


def get_global_event_bus() -> EventBus:
    """
    Return a process-wide event bus instance.
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def get_global_propagation() -> EventPropagation:
    """
    Return a global propagation helper bound to the global bus.
    """
    global _global_propagation
    if _global_propagation is None:
        _global_propagation = EventPropagation(get_global_event_bus())
    return _global_propagation


def emit_event(event_type: str, data: dict | None = None, **kwargs) -> None:
    """
    Emit an event synchronously through the global bus.
    """
    event = Event(type=event_type, data=data or {}, **kwargs)
    get_global_event_bus().emit(event)


async def emit_event_async(event_type: str, data: dict | None = None, **kwargs) -> None:
    """
    Emit an event asynchronously through the global bus.
    """
    event = Event(type=event_type, data=data or {}, **kwargs)
    await get_global_event_bus().emit_async(event)


def register_handler(
    event_type: str, handler: HandlerCallable, priority: int = 0, once: bool = False,
) -> None:
    """
    Register a handler on the global bus.
    """
    get_global_event_bus().register_handler(event_type, handler, priority, once)


def unregister_handler(event_type: str, handler: HandlerCallable) -> None:
    """
    Remove a handler from the global bus.
    """
    get_global_event_bus().unregister_handler(event_type, handler)


__all__ = [
    "emit_event",
    "emit_event_async",
    "get_global_event_bus",
    "get_global_propagation",
    "register_handler",
    "unregister_handler",
]
