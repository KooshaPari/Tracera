"""
Base component abstractions.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

from .lifecycle import ComponentLifecycleState
from .state import ComponentStateStore

if TYPE_CHECKING:
    from .environment import ComposeResult
    from .events import Event, EventHandler

logger = logging.getLogger(__name__)

T = TypeVar("T")
ComponentType = TypeVar("ComponentType", bound="BaseComponent")


class BaseComponent(ABC):
    """
    Abstract foundation for all Pheno TUI components.
    """

    def __init__(self, **kwargs):
        self.state = ComponentStateStore()
        self.component_state = ComponentLifecycleState.UNMOUNTED
        self.event_handlers: dict[str, list[EventHandler]] = {}
        self.children: list[BaseComponent] = []
        self.parent: BaseComponent | None = None
        self.metadata: dict[str, Any] = kwargs

    @abstractmethod
    def compose(self) -> ComposeResult:
        """
        Produce the widget tree rendered by the component.
        """
        ...

    def mount(self) -> None:
        """
        Transition the component into the mounted state and invoke hooks.
        """
        if self.component_state != ComponentLifecycleState.UNMOUNTED:
            return

        self.component_state = ComponentLifecycleState.MOUNTING
        try:
            self.on_mount()
            self.component_state = ComponentLifecycleState.MOUNTED
        except Exception as exc:  # pragma: no cover - defensive logging
            self.component_state = ComponentLifecycleState.ERROR
            logger.exception("Error mounting component %s: %s", self.__class__.__name__, exc)
            raise

    def unmount(self) -> None:
        """
        Gracefully tear down the component and trigger unmount hooks.
        """
        if self.component_state != ComponentLifecycleState.MOUNTED:
            return

        self.component_state = ComponentLifecycleState.UNMOUNTING
        try:
            self.on_unmount()
            self.component_state = ComponentLifecycleState.UNMOUNTED
        except Exception as exc:  # pragma: no cover - defensive logging
            self.component_state = ComponentLifecycleState.ERROR
            logger.exception("Error unmounting component %s: %s", self.__class__.__name__, exc)
            raise

    def on_mount(self) -> None:
        """
        Lifecycle hook invoked after the component has been mounted.
        """

    def on_unmount(self) -> None:
        """
        Lifecycle hook triggered before the component is removed.
        """

    def add_child(self, child: BaseComponent) -> None:
        """
        Attach a child component to this component.
        """
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child: BaseComponent) -> None:
        """
        Remove a previously attached child component.
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def emit_event(self, event_type: str, event: Event) -> None:
        """
        Dispatch an event to all registered handlers for ``event_type``.
        """
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Error in event handler for %s: %s", event_type, exc)

    def add_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """
        Register an event handler for a specific event category.
        """
        self.event_handlers.setdefault(event_type, []).append(handler)

    def remove_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """
        Unregister a previously registered event handler.
        """
        if event_type in self.event_handlers:
            handlers = self.event_handlers[event_type]
            if handler in handlers:
                handlers.remove(handler)

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Convenience proxy to :class:`ComponentStateStore.get`.
        """
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """
        Proxy to :class:`ComponentStateStore.set` for ergonomic overrides.
        """
        self.state.set(key, value)

    def update_state(self, data: dict[str, Any]) -> None:
        """
        Merge multiple state values at once.
        """
        self.state.update(data)


__all__ = ["BaseComponent", "ComponentType"]
