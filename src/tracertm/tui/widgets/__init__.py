"""TUI widgets."""

from tracertm.tui.widgets.conflict_panel import ConflictPanel
from tracertm.tui.widgets.graph_view import GraphViewWidget
from tracertm.tui.widgets.item_list import ItemListWidget
from tracertm.tui.widgets.state_display import StateDisplayWidget
from tracertm.tui.widgets.sync_status import (
    CompactSyncStatus,
    SyncStatusWidget,
)
from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget

try:
    from tracertm.tui.widgets.action_plan_panel import ActionPlanPanel
    from tracertm.tui.widgets.agent_process_list import AgentProcessList
    from tracertm.tui.widgets.live_log_view import LiveLogView
    from tracertm.tui.widgets.step_status_table import StepStatusTable
except ImportError:
    ActionPlanPanel = None
    AgentProcessList = None
    LiveLogView = None
    StepStatusTable = None

__all__ = [
    "ActionPlanPanel",
    "AgentProcessList",
    "CompactSyncStatus",
    "ConflictPanel",
    "GraphViewWidget",
    "ItemListWidget",
    "LiveLogView",
    "StateDisplayWidget",
    "StepStatusTable",
    "SyncStatusWidget",
    "ViewSwitcherWidget",
]
