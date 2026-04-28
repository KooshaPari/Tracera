"""
Environment shims for Textual integration.
"""

from __future__ import annotations

try:  # pragma: no cover - optional dependency detection
    from textual.app import ComposeResult
    from textual.containers import Container
    from textual.geometry import Offset, Size
    from textual.reactive import reactive
    from textual.widget import Widget

    HAS_TEXTUAL = True
except ImportError:  # pragma: no cover - fallback behaviour
    ComposeResult = object  # type: ignore[assignment]
    Container = object  # type: ignore[assignment]
    Offset = object  # type: ignore[assignment]
    Size = object  # type: ignore[assignment]

    def reactive(value):  # type: ignore[override]
        return value

    Widget = object  # type: ignore[assignment]
    HAS_TEXTUAL = False

__all__ = [
    "HAS_TEXTUAL",
    "ComposeResult",
    "Container",
    "Offset",
    "Size",
    "Widget",
    "reactive",
]
