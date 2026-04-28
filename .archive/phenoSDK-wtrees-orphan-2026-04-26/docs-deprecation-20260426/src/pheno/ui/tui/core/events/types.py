"""
Enumerations for the TUI event system.
"""

from __future__ import annotations

from enum import Enum


class EventType(Enum):
    """
    Logical event categories emitted within the TUI.
    """

    CUSTOM = "custom"
    CLICK = "click"
    KEY = "key"
    MOUSE = "mouse"
    FOCUS = "focus"
    BLUR = "blur"
    RESIZE = "resize"
    MOVE = "move"
    SHOW = "show"
    HIDE = "hide"
    MOUNT = "mount"
    UNMOUNT = "unmount"


class EventPhase(Enum):
    """
    Propagation phase for event dispatch.
    """

    CAPTURE = "capture"
    TARGET = "target"
    BUBBLE = "bubble"


__all__ = ["EventPhase", "EventType"]
