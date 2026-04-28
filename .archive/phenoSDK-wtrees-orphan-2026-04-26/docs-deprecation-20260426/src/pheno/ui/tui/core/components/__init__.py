"""
Composable component toolkit for Pheno's TUI core.
"""

from .base import BaseComponent, ComponentType
from .composite import Component, ContainerComponent
from .environment import (
    HAS_TEXTUAL,
    ComposeResult,
    Container,
    Offset,
    Size,
    Widget,
    reactive,
)
from .events import Event, EventHandler
from .helpers import (
    component_lifecycle,
    create_component,
    mount_component,
    unmount_component,
)
from .lifecycle import ComponentLifecycleState
from .mixins import EventHandling, LifecycleHooks, PluginIntegration, StateManagement
from .state import ComponentStateStore
from .textual import TextualComponent, TextualContainer

# Backwards compatibility aliases
ComponentState = ComponentLifecycleState
ComponentStateData = ComponentStateStore

__all__ = [
    "HAS_TEXTUAL",
    "BaseComponent",
    "Component",
    "ComponentLifecycleState",
    "ComponentState",
    "ComponentStateData",
    "ComponentStateStore",
    "ComponentType",
    "ComposeResult",
    "Container",
    "ContainerComponent",
    "Event",
    "EventHandler",
    "EventHandling",
    "LifecycleHooks",
    "Offset",
    "PluginIntegration",
    "Size",
    "StateManagement",
    "TextualComponent",
    "TextualContainer",
    "Widget",
    "component_lifecycle",
    "create_component",
    "mount_component",
    "reactive",
    "unmount_component",
]
