"""
Utility helpers for component lifecycle management.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

    from .base import BaseComponent, ComponentType


def create_component(component_class: type[ComponentType], **kwargs) -> ComponentType:
    """
    Instantiate a component while forwarding constructor kwargs.
    """
    return component_class(**kwargs)


def mount_component(component: BaseComponent) -> None:
    """
    Convenience helper that calls :meth:`BaseComponent.mount`.
    """
    component.mount()


def unmount_component(component: BaseComponent) -> None:
    """
    Convenience helper that calls :meth:`BaseComponent.unmount`.
    """
    component.unmount()


@contextmanager
def component_lifecycle(component: BaseComponent) -> Generator[BaseComponent, None, None]:
    """
    Context manager that mounts a component for the duration of the block.
    """
    try:
        component.mount()
        yield component
    finally:
        component.unmount()


__all__ = ["component_lifecycle", "create_component", "mount_component", "unmount_component"]
