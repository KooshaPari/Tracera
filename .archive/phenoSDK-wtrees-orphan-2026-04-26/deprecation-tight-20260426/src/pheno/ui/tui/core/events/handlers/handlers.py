"""
Handler protocols and prioritisation utilities.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Union

if TYPE_CHECKING:
    from ..models import Event


class EventHandler(Protocol):
    """
    Synchronous handler signature.
    """

    def __call__(self, event: Event) -> None:
        """
        Handle a dispatched event.
        """


class AsyncEventHandler(Protocol):
    """
    Asynchronous handler signature.
    """

    async def __call__(self, event: Event) -> None:
        """
        Handle a dispatched event asynchronously.
        """


HandlerCallable = Union[EventHandler, AsyncEventHandler]


@dataclass
class PrioritizedHandler:
    """
    Wrap a handler with priority metadata for ordering.
    """

    handler: HandlerCallable
    priority: int = 0
    once: bool = False

    def __lt__(self, other: PrioritizedHandler) -> bool:
        return self.priority < other.priority

    def __gt__(self, other: PrioritizedHandler) -> bool:
        return self.priority > other.priority

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PrioritizedHandler)
            and self.priority == other.priority
            and self.handler == other.handler
        )

    @property
    def is_async(self) -> bool:
        """
        Return True when the wrapped handler is coroutine based.
        """
        return asyncio.iscoroutinefunction(self.handler)


__all__ = ["AsyncEventHandler", "EventHandler", "HandlerCallable", "PrioritizedHandler"]
