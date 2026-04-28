"""
Dashboard Layouts - Reusable dashboard patterns.

Ported from zen-mcp-server patterns for general use.
"""

from textual.app import ComposeResult
from textual.containers import Container, Grid, ScrollableContainer, Vertical
from textual.widgets import Static


class ThreeSectionDashboard(Container):
    """Three-section dashboard layout (header/main/footer).

    Common pattern for monitoring dashboards with:
    - Fixed header (status banner, title)
    - Scrollable main content
    - Fixed footer (controls, help)

    Example:
        class MyDashboard(App):
            def compose(self) -> ComposeResult:
                with ThreeSectionDashboard():
                    yield StatusBanner(...)  # Goes to header
                    yield ProcessTable(...)  # Goes to main
                    yield ControlPanel(...)  # Goes to footer
    """

    DEFAULT_CSS = """
    ThreeSectionDashboard {
        layout: vertical;
        height: 100%;
    }

    ThreeSectionDashboard > .dashboard-header {
        height: auto;
        dock: top;
    }

    ThreeSectionDashboard > .dashboard-main {
        height: 1fr;
    }

    ThreeSectionDashboard > .dashboard-footer {
        height: auto;
        dock: bottom;
    }
    """

    def __init__(self, header_height: int = 3, footer_height: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.header_height = header_height
        self.footer_height = footer_height

    def compose(self) -> ComposeResult:
        """
        Compose three-section layout.
        """
        with Vertical(classes="dashboard-header"):
            yield Static(id="header-content")

        with ScrollableContainer(classes="dashboard-main"):
            yield Static(id="main-content")

        with Vertical(classes="dashboard-footer"):
            yield Static(id="footer-content")


class GridDashboard(Container):
    """Grid-based dashboard layout.

    Flexible grid for status cards, metrics panels, etc.

    Example:
        with GridDashboard(columns=3):
            yield StatusCard("Server 1")
            yield StatusCard("Server 2")
            yield StatusCard("Server 3")
            yield MetricsPanel("Metrics")
    """

    DEFAULT_CSS = """
    GridDashboard {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
    }

    GridDashboard.two-column {
        grid-size: 2;
    }

    GridDashboard.four-column {
        grid-size: 4;
    }
    """

    def __init__(self, columns: int = 3, gutter: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.columns = columns
        self.gutter = gutter

        # Set class based on columns
        if columns == 2:
            self.add_class("two-column")
        elif columns == 4:
            self.add_class("four-column")


class SidebarDashboard(Container):
    """Dashboard with sidebar layout.

    Common pattern for:
    - Left sidebar: navigation, controls
    - Right main area: content, logs

    Example:
        with SidebarDashboard(sidebar_width=40):
            # Sidebar content
            yield ControlPanel()
            # Main content
            yield LogViewer()
    """

    DEFAULT_CSS = """
    SidebarDashboard {
        layout: horizontal;
        height: 100%;
    }

    SidebarDashboard > .sidebar {
        width: 40;
        border-right: solid $primary;
        background: $panel;
    }

    SidebarDashboard > .main-area {
        width: 1fr;
        background: $surface;
    }
    """

    def __init__(self, sidebar_width: int = 40, **kwargs):
        super().__init__(**kwargs)
        self.sidebar_width = sidebar_width

    def compose(self) -> ComposeResult:
        """
        Compose sidebar layout.
        """
        with Vertical(classes="sidebar"):
            yield Static(id="sidebar-content")

        with Vertical(classes="main-area"):
            yield Static(id="main-content")


class MonitoringDashboard(Container):
    """Complete monitoring dashboard layout.

    Combines multiple patterns:
    - Header with status banner
    - Grid of status cards
    - Metrics panel
    - Log viewer
    - Footer with controls

    Example:
        class MyMonitor(App):
            def compose(self) -> ComposeResult:
                with MonitoringDashboard():
                    yield StatusBanner(...)
                    yield StatusCard(...)
                    yield MetricsPanel(...)
                    yield LogViewer(...)
    """

    DEFAULT_CSS = """
    MonitoringDashboard {
        layout: vertical;
        height: 100%;
    }

    MonitoringDashboard > .banner {
        height: 3;
        dock: top;
    }

    MonitoringDashboard > .status-grid {
        height: auto;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
    }

    MonitoringDashboard > .metrics {
        height: 10;
        padding: 0 1;
    }

    MonitoringDashboard > .logs {
        height: 1fr;
        padding: 0 1 1 1;
    }

    MonitoringDashboard > .controls {
        height: 3;
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        """
        Compose monitoring dashboard.
        """
        # Banner
        with Container(classes="banner"):
            yield Static(id="banner-content")

        # Status cards grid
        with Grid(classes="status-grid"):
            yield Static(id="status-cards")

        # Metrics
        with Container(classes="metrics"):
            yield Static(id="metrics-content")

        # Logs
        with ScrollableContainer(classes="logs"):
            yield Static(id="logs-content")

        # Controls
        with Container(classes="controls"):
            yield Static(id="controls-content")


class TabbedDashboard(Container):
    """Tabbed dashboard layout.

    Multiple views in tabs:
    - Overview
    - Processes
    - Metrics
    - Logs

    Example:
        with TabbedDashboard(tabs=["Overview", "Processes", "Logs"]):
            yield OverviewPanel()
            yield ProcessTable()
            yield LogViewer()
    """

    DEFAULT_CSS = """
    TabbedDashboard {
        layout: vertical;
        height: 100%;
    }

    TabbedDashboard > TabbedContent {
        height: 1fr;
    }
    """

    def __init__(self, tabs: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.tabs = tabs or ["Main"]

    def compose(self) -> ComposeResult:
        """
        Compose tabbed layout.
        """
        from textual.widgets import TabbedContent, TabPane

        with TabbedContent():
            for tab_name in self.tabs:
                with TabPane(tab_name):
                    yield Static(id=f"tab-{tab_name.lower()}")


class SplitDashboard(Container):
    """Split dashboard layout (top/bottom or left/right).

    Example:
        with SplitDashboard(direction="horizontal", ratio=0.6):
            yield ProcessTable()  # 60% width
            yield LogViewer()     # 40% width
    """

    DEFAULT_CSS = """
    SplitDashboard.horizontal {
        layout: horizontal;
        height: 100%;
    }

    SplitDashboard.vertical {
        layout: vertical;
        height: 100%;
    }

    SplitDashboard > .split-primary {
        width: 60%;
        height: 60%;
    }

    SplitDashboard > .split-secondary {
        width: 40%;
        height: 40%;
    }
    """

    def __init__(
        self,
        direction: str = "horizontal",
        ratio: float = 0.6,
        **kwargs,  # or "vertical"  # Primary section ratio
    ):
        super().__init__(**kwargs)
        self.direction = direction
        self.ratio = ratio
        self.add_class(direction)

    def compose(self) -> ComposeResult:
        """
        Compose split layout.
        """
        with Container(classes="split-primary"):
            yield Static(id="primary-content")

        with Container(classes="split-secondary"):
            yield Static(id="secondary-content")
