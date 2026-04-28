"""
Public entry point for the TUI toolkit.
"""

__version__ = "0.3.0"  # Bumped for protocol-based architecture and enhanced widgets

from pheno.ui.tui.widgets.unified_progress import (
    CategoryStats,
    Task,
    TaskMetrics,
    TaskPriority,
    TaskStatus,
    UnifiedProgressWidget,
)

from .apps import (
    create_log_viewer_app,
    create_progress_app,
    create_status_app,
    create_tui_app,
)

# Core modules
from .core.stream_capture import (
    CapturedLine,
)
from .core.stream_capture import LogLevel as CaptureLogLevel
from .core.stream_capture import (
    OutputFormatter,
    StreamCapture,
    capture_output,
)

# Factories
from .factories import (
    WidgetFactory,
    WidgetTemplate,
    create_widget,
    get_widget_factory,
)

# Layouts
from .layouts import (
    GridCell,
    GridLayout,
    SplitDirection,
    SplitLayout,
    Tab,
    TabbedLayout,
)

# Protocols (new in 0.3.0)
from .protocols import (
    ClientAdapter,
    MetricsProvider,
    OAuthCacheProvider,
    ResourceProvider,
    TunnelProvider,
)

# Themes
from .themes import (
    ColorScheme,
    DarkTheme,
    LightTheme,
    Theme,
    ThemeManager,
    get_theme_manager,
)

# Utils
from .utils import (
    BoxDrawing,
    ColorUtils,
    KeyboardShortcuts,
    darken,
    draw_border,
    draw_box,
    get_shortcut,
    get_shortcuts,
    hex_to_rgb,
    lighten,
    register_shortcut,
    rgb_to_hex,
)

# Widgets
from .widgets import (
    FieldType,
    FormField,
    FormWidget,
    LogEntry,
    LogLevel,
    LogViewer,
    MetricRow,
    MetricsTable,
    OAuthStatusWidget,
    ProgressWidget,
    ResourceMetric,
    ResourceStatusWidget,
    ResourceStatusWidgetEnhanced,
    ServerStatusWidget,
    StatusDashboard,
    StatusDashboardApp,
    StatusWidget,
    TaskProgress,
    TreeNode,
    TreeView,
    TunnelStatusWidget,
    create_status_dashboard,
    run_status_dashboard_app,
)

    log_viewer = LogViewer(
        max_entries=max_entries,
        auto_scroll=auto_scroll,
        show_stats=show_stats
    )

    return create_tui_app(
        title=title,
        layout="vertical",
        widgets=[log_viewer],
        bindings=[
            ("q", "quit", "Quit"),
            ("c", "clear", "Clear Logs"),
            ("f", "filter", "Filter"),
            ("s", "save", "Save Logs")
        ],
        **kwargs
    )


# Common panel/widget factories
def create_metrics_panel(title: str = "Metrics", **kwargs) -> 'MetricsTable':
    """Create a configured metrics panel.

    Args:
        title: Panel title
        **kwargs: Additional MetricsTable kwargs

    Returns:
        Configured MetricsTable widget

    Example:
        ```python
        from pheno.ui.tui import create_metrics_panel

        metrics = create_metrics_panel("System Metrics")
        metrics.add_metric("cpu_usage", 0, unit="%", warning_threshold=70, critical_threshold=90)
        metrics.add_metric("memory_usage", 0, unit="MB")
        ```
    """
    defaults = {
        "auto_refresh": True,
        "show_sparklines": True,
        "show_trends": True
    }
    defaults.update(kwargs)

    return MetricsTable(**defaults)


def create_progress_panel(title: str = "Progress", **kwargs) -> 'ProgressWidget':
    """Create a configured progress panel.

    Args:
        title: Panel title
        **kwargs: Additional ProgressWidget kwargs

    Returns:
        Configured ProgressWidget

    Example:
        ```python
        from pheno.ui.tui import create_progress_panel

        progress = create_progress_panel("Test Progress")
        progress.add_task("test_1", "Running test 1", total=100)
        ```
    """
    defaults = {
        "show_individual": True,
        "show_summary": True,
        "compact": False
    }
    defaults.update(kwargs)

    return ProgressWidget(**defaults)


def create_log_panel(title: str = "Logs", **kwargs) -> 'LogViewer':
    """Create a configured log panel.

    Args:
        title: Panel title
        **kwargs: Additional LogViewer kwargs

    Returns:
        Configured LogViewer widget

    Example:
        ```python
        from pheno.ui.tui import create_log_panel, LogLevel

        logs = create_log_panel("Application Logs")
        logs.add_log("Started", LogLevel.INFO, "System")
        ```
    """
    defaults = {
        "max_entries": 1000,
        "auto_scroll": True,
        "show_stats": True
    }
    defaults.update(kwargs)

    return LogViewer(**defaults)


__all__ = [
    # Version
    "__version__",
    # Convenience Functions (new)
    "create_tui_app",
    "create_status_app",
    "create_progress_app",
    "create_log_viewer_app",
    "create_metrics_panel",
    "create_progress_panel",
    "create_log_panel",
    # Core - Stream Capture (new in 0.2.0)
    "StreamCapture",
    "CapturedLine",
    "CaptureLogLevel",
    "OutputFormatter",
    "capture_output",
    # Protocols (new in 0.3.0)
    "ClientAdapter",
    "TunnelProvider",
    "ResourceProvider",
    "MetricsProvider",
    "OAuthCacheProvider",
    # Unified Progress (new in 0.2.0)
    "UnifiedProgressWidget",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskMetrics",
    "CategoryStats",
    # Widgets - Status Dashboard
    "StatusWidget",
    "OAuthStatusWidget",
    "ServerStatusWidget",
    "ResourceStatusWidget",
    "StatusDashboard",
    "StatusDashboardApp",
    "create_status_dashboard",
    "run_status_dashboard_app",
    # Widgets - Enhanced (new in 0.3.0)
    "TunnelStatusWidget",
    "ResourceStatusWidgetEnhanced",
    "ResourceMetric",
    # Widgets - Core
    "LogViewer",
    "LogEntry",
    "LogLevel",
    "ProgressWidget",
    "TaskProgress",
    "MetricsTable",
    "MetricRow",
    "TreeView",
    "TreeNode",
    "FormWidget",
    "FormField",
    "FieldType",
    # Layouts
    "SplitLayout",
    "SplitDirection",
    "TabbedLayout",
    "Tab",
    "GridLayout",
    "GridCell",
    # Themes
    "ThemeManager",
    "Theme",
    "ColorScheme",
    "DarkTheme",
    "LightTheme",
    "get_theme_manager",
    # Factories
    "WidgetFactory",
    "WidgetTemplate",
    "create_widget",
    "get_widget_factory",
    # Utils
    "ColorUtils",
    "rgb_to_hex",
    "hex_to_rgb",
    "darken",
    "lighten",
    "BoxDrawing",
    "draw_box",
    "draw_border",
    "KeyboardShortcuts",
    "register_shortcut",
    "get_shortcut",
    "get_shortcuts",
]
