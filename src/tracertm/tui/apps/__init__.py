"""TUI applications."""

from tracertm.tui.apps.browser import BrowserApp  # type: ignore[possibly-missing-import]
from tracertm.tui.apps.dashboard import DashboardApp  # type: ignore[possibly-missing-import]
from tracertm.tui.apps.graph import GraphApp  # type: ignore[possibly-missing-import]

__all__ = ["BrowserApp", "DashboardApp", "GraphApp"]
