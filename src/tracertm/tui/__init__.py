"""Textual TUI (Terminal User Interface) for TraceRTM."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tracertm.tui.apps.browser import BrowserApp
    from tracertm.tui.apps.dashboard_compat import EnhancedDashboardApp
    from tracertm.tui.apps.graph import GraphApp

__all__ = ["BrowserApp", "DashboardApp", "EnhancedDashboardApp", "GraphApp"]


def __getattr__(name: str) -> object:
    """Lazy-load apps so optional Textual is not required for widget utilities."""
    if name in {"BrowserApp"}:
        from tracertm.tui.apps.browser import BrowserApp

        return BrowserApp
    if name in {"DashboardApp", "EnhancedDashboardApp"}:
        from tracertm.tui.apps.dashboard_compat import EnhancedDashboardApp

        return EnhancedDashboardApp
    if name == "GraphApp":
        from tracertm.tui.apps.graph import GraphApp

        return GraphApp
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
