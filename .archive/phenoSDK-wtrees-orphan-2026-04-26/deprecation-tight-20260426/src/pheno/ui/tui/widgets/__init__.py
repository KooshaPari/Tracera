"""
TUI-Kit Widgets - Reusable Textual widgets for terminal UIs.

Comprehensive widget library ported from zen-mcp-server patterns.

Enhanced Widgets (v0.3.0):
- ServerStatusWidget: Protocol-based MCP server monitoring with ClientAdapter
- ResourceStatusWidget: Comprehensive resource monitoring with threshold alerts

Note: Import protocols from tui_kit.protocols for type hints and implementations:
    from tui_kit.protocols import ClientAdapter, ResourceProvider
"""

from pheno.ui.tui.banner import (
    Banner,
    BrandedPanel,
    StatusBanner,
    WelcomeScreen,
    generate_ascii_banner,
)
from pheno.ui.tui.form_widget import FieldType, FormField, FormWidget
from pheno.ui.tui.log_viewer import LogEntry, LogLevel, LogViewer
from pheno.ui.tui.metrics_table import MetricRow, MetricsTable
from pheno.ui.tui.progress_widget import ProgressWidget, TaskProgress

# Protocol-based resource monitoring (v0.4.0)
from pheno.ui.tui.resource_status import (
    DatabaseProvider,
    ResourceMetric,
    ResourceMonitor,
)
from pheno.ui.tui.resource_status import (
    ResourceStatusWidget as ResourceStatusWidgetEnhanced,
)
from pheno.ui.tui.resource_status import TaskMetrics as ResourceTaskMetrics
from pheno.ui.tui.results_display import (
    DataTableDisplay,
    ProgressTracker,
    ResultsDisplay,
)
from pheno.ui.tui.status_dashboard import (
    OAuthStatusWidget,
    ResourceStatusWidget,
    StatusDashboard,
    StatusDashboardApp,
    StatusWidget,
    create_status_dashboard,
    run_status_dashboard_app,
)

# New widgets from zen patterns
from pheno.ui.tui.status_panel import MetricsPanel, StatusCard, StatusPanel
from pheno.ui.tui.tree_view import TreeNode, TreeView

# Enhanced widgets extracted from mcp-QA with protocol support
from pheno.ui.tui.widgets.server_status import ServerStatusWidget

__all__ = [
    # Branding & Banners
    "Banner",
    "BrandedPanel",
    "DataTableDisplay",
    "DatabaseProvider",
    "FieldType",
    "FormField",
    "FormWidget",
    "LogEntry",
    "LogLevel",
    # Core widgets
    "LogViewer",
    "MetricRow",
    "MetricsPanel",
    "MetricsTable",
    "OAuthStatusWidget",
    "ProgressTracker",
    "ProgressWidget",
    "ResourceMetric",
    "ResourceMonitor",
    # Protocol-based resource monitoring (v0.4.0)
    "ResourceStatusEnhanced",
    "ResourceStatusWidget",
    "ResourceStatusWidgetEnhanced",
    "ResourceTaskMetrics",
    # Results & Display
    "ResultsDisplay",
    # Enhanced widgets with protocol support (v0.3.0)
    "ServerStatusWidget",
    "StatusBanner",
    "StatusCard",
    "StatusDashboard",
    "StatusDashboardApp",
    # Status & Metrics
    "StatusPanel",
    # Status dashboard
    "StatusWidget",
    "TaskProgress",
    "TreeNode",
    "TreeView",
    "WelcomeScreen",
    "create_status_dashboard",
    "generate_ascii_banner",
    "run_status_dashboard_app",
]

# Note: ClientAdapter should be imported from tui_kit.protocols for protocol-based resource monitoring
