"""TUI applications."""

from tracertm.tui.apps.browser import BrowserApp
from tracertm.tui.apps.dashboard_v2 import EnhancedDashboardApp
from tracertm.tui.apps.graph import GraphApp

# Single dashboard implementation (enhanced with LocalStorageManager, sync, conflicts)
DashboardApp = EnhancedDashboardApp

__all__ = ["BrowserApp", "DashboardApp", "EnhancedDashboardApp", "GraphApp"]
