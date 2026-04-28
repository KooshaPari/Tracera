"""
Lifecycle enums for component state tracking.
"""

from __future__ import annotations

from enum import Enum


class ComponentLifecycleState(Enum):
    """
    Enumerated lifecycle states emitted by components.
    """

    UNMOUNTED = "unmounted"
    MOUNTING = "mounting"
    MOUNTED = "mounted"
    UNMOUNTING = "unmounting"
    ERROR = "error"


__all__ = ["ComponentLifecycleState"]
