"""
Composable event system primitives for the TUI framework.
"""

from .event_bus.bus import EventBus
from .event_bus.global_bus import (
    emit_event,
    emit_event_async,
    get_global_event_bus,
    get_global_propagation,
    register_handler,
    unregister_handler,
)
from .handlers.handlers import AsyncEventHandler, EventHandler, PrioritizedHandler
from .models import Event
from .propagation.propagation import EventPropagation
from .types import EventPhase, EventType

__all__ = [
    "AsyncEventHandler",
    "Event",
    "EventBus",
    "EventHandler",
    "EventPhase",
    "EventPropagation",
    "EventType",
    "PrioritizedHandler",
    "emit_event",
    "emit_event_async",
    "get_global_event_bus",
    "get_global_propagation",
    "register_handler",
    "unregister_handler",
]
