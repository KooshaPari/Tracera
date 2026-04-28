"""
Composite component implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .mixins import EventHandling, LifecycleHooks, PluginIntegration, StateManagement
from .textual import TextualComponent, TextualContainer

if TYPE_CHECKING:
    from .environment import ComposeResult


class Component(
    TextualComponent, LifecycleHooks, EventHandling, StateManagement, PluginIntegration,
):
    """
    Fully featured component bundling lifecycle, event, state, and plugins.
    """

    def __init__(self, **kwargs):
        TextualComponent.__init__(self, **kwargs)
        LifecycleHooks.__init__(self)
        EventHandling.__init__(self)
        StateManagement.__init__(self, **kwargs)
        PluginIntegration.__init__(self, **kwargs)

    def compose(self) -> ComposeResult:
        return super().compose()

    def on_mount(self) -> None:
        super().on_mount()
        self.on_create()

    def on_unmount(self) -> None:
        super().on_unmount()
        self.on_destroy()


class ContainerComponent(
    TextualContainer, LifecycleHooks, EventHandling, StateManagement, PluginIntegration,
):
    """
    Container-specific component with the same feature set as :class:`Component`.
    """

    def __init__(self, **kwargs):
        TextualContainer.__init__(self, **kwargs)
        LifecycleHooks.__init__(self)
        EventHandling.__init__(self)
        StateManagement.__init__(self, **kwargs)
        PluginIntegration.__init__(self, **kwargs)

    def compose(self) -> ComposeResult:
        return super().compose()

    def on_mount(self) -> None:
        super().on_mount()
        self.on_create()

    def on_unmount(self) -> None:
        super().on_unmount()
        self.on_destroy()


__all__ = ["Component", "ContainerComponent"]
