"""
Event bus implementation.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import TYPE_CHECKING, Any

from ..handlers.handlers import HandlerCallable, PrioritizedHandler

if TYPE_CHECKING:
    from ..models import Event

logger = logging.getLogger(__name__)


class EventBus:
    """
    Manage event handlers and dispatch events.
    """

    def __init__(self, *, max_history: int = 1000):
        self._handlers: dict[str, list[PrioritizedHandler]] = {}
        self._event_history: list[Event] = []
        self._max_history = max_history
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Handler management
    # ------------------------------------------------------------------ #
    def register_handler(
        self,
        event_type: str,
        handler: HandlerCallable,
        priority: int = 0,
        once: bool = False,
    ) -> None:
        """
        Register a handler for a specific event type.
        """
        prioritized = PrioritizedHandler(handler, priority, once)
        with self._lock:
            self._handlers.setdefault(event_type, []).append(prioritized)
            self._handlers[event_type].sort(reverse=True)

    def unregister_handler(self, event_type: str, handler: HandlerCallable) -> None:
        """
        Remove a handler previously registered.
        """
        with self._lock:
            if event_type not in self._handlers:
                return
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h.handler != handler
            ]

    def clear_handlers(self, event_type: str | None = None) -> None:
        """
        Clear handlers for a given type or all handlers.
        """
        with self._lock:
            if event_type:
                self._handlers.pop(event_type, None)
            else:
                self._handlers.clear()

    def get_handlers(self, event_type: str) -> list[PrioritizedHandler]:
        """
        Return a copy of handlers for the provided event.
        """
        with self._lock:
            return list(self._handlers.get(event_type, []))

    # ------------------------------------------------------------------ #
    # Event dispatch
    # ------------------------------------------------------------------ #
    def emit(self, event: Event) -> None:
        """
        Emit an event synchronously.
        """
        if event is None:
            return

        self._add_to_history(event)
        handlers = self.get_handlers(event.type)

        to_remove: list[PrioritizedHandler] = []
        for prioritized in handlers:
            if event.propagation_stopped:
                break
            try:
                if prioritized.is_async:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(prioritized.handler(event))  # type: ignore[arg-type]
                    else:
                        loop.run_until_complete(prioritized.handler(event))  # type: ignore[arg-type]
                else:
                    prioritized.handler(event)  # type: ignore[arg-type]
            except Exception as exc:
                logger.exception("Error in event handler for %s", event.type, exc_info=exc)

            if prioritized.once:
                to_remove.append(prioritized)

        if to_remove:
            with self._lock:
                existing = self._handlers.get(event.type, [])
                self._handlers[event.type] = [
                    handler for handler in existing if handler not in to_remove
                ]

    async def emit_async(self, event: Event) -> None:
        """
        Emit an event asynchronously.
        """
        if event is None:
            return

        self._add_to_history(event)
        handlers = self.get_handlers(event.type)
        to_remove: list[PrioritizedHandler] = []

        for prioritized in handlers:
            if event.propagation_stopped:
                break
            try:
                if prioritized.is_async:
                    await prioritized.handler(event)  # type: ignore[arg-type]
                else:
                    prioritized.handler(event)  # type: ignore[arg-type]
            except Exception as exc:
                logger.exception("Error in async event handler for %s", event.type, exc_info=exc)

            if prioritized.once:
                to_remove.append(prioritized)

        if to_remove:
            with self._lock:
                existing = self._handlers.get(event.type, [])
                self._handlers[event.type] = [
                    handler for handler in existing if handler not in to_remove
                ]

    # ------------------------------------------------------------------ #
    # History & stats
    # ------------------------------------------------------------------ #
    def get_event_history(self, event_type: str | None = None) -> list[Event]:
        """
        Return recent events, optionally filtered by type.
        """
        with self._lock:
            if event_type:
                return [event for event in self._event_history if event.type == event_type]
            return list(self._event_history)

    def clear_event_history(self) -> None:
        """
        Clear recorded history.
        """
        with self._lock:
            self._event_history.clear()

    def get_stats(self) -> dict[str, Any]:
        """
        Return diagnostic information about the bus.
        """
        with self._lock:
            total_handlers = sum(len(handlers) for handlers in self._handlers.values())
            return {
                "total_handlers": total_handlers,
                "event_types": len(self._handlers),
                "history_size": len(self._event_history),
                "handlers_by_type": {
                    etype: len(handlers) for etype, handlers in self._handlers.items()
                },
            }

    def _add_to_history(self, event: Event) -> None:
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)


__all__ = ["EventBus"]
