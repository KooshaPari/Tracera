"""TUI widgets."""

from tracertm.tui.widgets.conflict_panel import ConflictPanel
from tracertm.tui.widgets.graph_view import GraphViewWidget
from tracertm.tui.widgets.item_list import ItemListWidget
from tracertm.tui.widgets.state_display import StateDisplayWidget
from tracertm.tui.widgets.sync_status import CompactSyncStatus, SyncStatusWidget
from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget

__all__ = [
    "CompactSyncStatus",
    "ConflictPanel",
    "GraphViewWidget",
    "ItemListWidget",
    "StateDisplayWidget",
    "SyncStatusWidget",
    "ViewSwitcherWidget",
]
