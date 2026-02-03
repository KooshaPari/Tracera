"""Graph view widget for TUI."""

from typing import Any

try:
    from textual.widgets import Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Static = object


class GraphViewWidget(Static):
    """Widget for displaying graph visualization."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if TEXTUAL_AVAILABLE:
            super().__init__("Graph View", *args, **kwargs)
