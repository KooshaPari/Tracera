"""
Event protocol definitions for components.
"""

from __future__ import annotations

from typing import Protocol


class Event(Protocol):
    """
    Structural contract that all component events must satisfy.
    """

    def __init__(self, **kwargs): ...


class EventHandler(Protocol):
    """
    Callable interface expected by the event system.
    """

    def __call__(self, event: Event) -> None: ...


__all__ = ["Event", "EventHandler"]
