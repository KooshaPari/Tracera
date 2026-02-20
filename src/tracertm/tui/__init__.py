"""Textual TUI (Terminal User Interface) for TraceRTM."""

from tracertm.tui.apps.browser import BrowserApp
from tracertm.tui.apps.dashboard_compat import EnhancedDashboardApp
from tracertm.tui.apps.dashboard_compat import (
    EnhancedDashboardApp as DashboardApp,
)
from tracertm.tui.apps.graph import GraphApp

__all__ = ["BrowserApp", "DashboardApp", "EnhancedDashboardApp", "GraphApp"]
