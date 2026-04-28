"""
Auxiliary mixins for component behaviour.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from .environment import Offset, Size
    from .events import Event

logger = logging.getLogger(__name__)


class LifecycleHooks:
    """
    Optional mixin exposing granular lifecycle callbacks for UI components.
    """

    def on_create(self) -> None:
        """
        Invoked once after a component mounts and completes initialization.
        """

    def on_destroy(self) -> None:
        """
        Executed during teardown just before the component is unmounted.
        """

    def on_show(self) -> None:
        """
        Called when the component transitions from hidden to visible.
        """

    def on_hide(self) -> None:
        """
        Called when the component transitions from visible to hidden.
        """

    def on_focus(self) -> None:
        """
        Trigger fired when the component gains input focus.
        """

    def on_blur(self) -> None:
        """
        Trigger fired when the component loses input focus.
        """

    def on_resize(self, size: Size) -> None:
        """
        React to layout recalculations that change the component's size.
        """

    def on_move(self, offset: Offset) -> None:
        """
        Respond to positional changes in the layout.
        """


class EventHandling:
    """
    Mixin exposing default event handler entry points.
    """

    def handle_click(self, event: Event) -> None:
        """
        Process pointer click interactions.
        """

    def handle_key(self, event: Event) -> None:
        """
        Process keyboard events such as key presses and releases.
        """

    def handle_mouse(self, event: Event) -> None:
        """
        Process low-level mouse events (move, wheel, etc.).
        """

    def handle_focus(self, event: Event) -> None:
        """
        Respond to focus events dispatched by the UI framework.
        """

    def handle_blur(self, event: Event) -> None:
        """
        Respond to blur events dispatched by the UI framework.
        """


class StateManagement:
    """
    Mixin that augments components with observer-friendly state operations.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._state_subscribers: list[Callable[[str, Any, Any], None]] = []

    def subscribe_to_state(self, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Register a callback that runs whenever a state key changes.
        """
        self._state_subscribers.append(callback)

    def unsubscribe_from_state(self, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Remove a previously registered state change callback.
        """
        if callback in self._state_subscribers:
            self._state_subscribers.remove(callback)

    def set_state(self, key: str, value: Any) -> None:
        """
        Update a single state key and notify subscribers of the change.
        """
        old_value = self.get_state(key)
        super().set_state(key, value)

        for callback in list(self._state_subscribers):
            try:
                callback(key, old_value, value)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Error in state subscriber: %s", exc)

    def update_state(self, data: dict[str, Any]) -> None:
        """
        Apply multiple state mutations and emit notifications per key.
        """
        for key, value in data.items():
            self.set_state(key, value)


class PluginIntegration:
    """
    Mixin that provides a lightweight plugin registry.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plugins: dict[str, Any] = {}

    def register_plugin(self, name: str, plugin: Any) -> None:
        """
        Register or replace a plugin implementation.
        """
        self.plugins[name] = plugin

    def unregister_plugin(self, name: str) -> None:
        """
        Remove a plugin from the component.
        """
        if name in self.plugins:
            del self.plugins[name]

    def get_plugin(self, name: str) -> Any | None:
        """
        Retrieve a plugin instance by name.
        """
        return self.plugins.get(name)

    def has_plugin(self, name: str) -> bool:
        """
        Determine whether a plugin has been registered.
        """
        return name in self.plugins


__all__ = ["EventHandling", "LifecycleHooks", "PluginIntegration", "StateManagement"]
