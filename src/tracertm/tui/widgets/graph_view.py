"""Graph view widget for TUI."""

try:
    from textual.widgets import Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Static = object  # type: ignore[assignment,misc]


class GraphViewWidget(Static):
    """Widget for displaying graph visualization."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize."""
        if TEXTUAL_AVAILABLE:
            super().__init__("Graph View", *args, **kwargs)  # type: ignore[arg-type]
