"""Textual TUI (Terminal User Interface) for TraceRTM."""

from tracertm.tui.apps.browser import BrowserApp  # type: ignore[possibly-missing-import]
from tracertm.tui.apps.dashboard_compat import EnhancedDashboardApp  # type: ignore[possibly-missing-import]
from tracertm.tui.apps.dashboard_compat import (
    EnhancedDashboardApp as DashboardApp,  # type: ignore[possibly-missing-import]
)
from tracertm.tui.apps.graph import GraphApp  # type: ignore[possibly-missing-import]

__all__ = ["BrowserApp", "DashboardApp", "EnhancedDashboardApp", "GraphApp"]
