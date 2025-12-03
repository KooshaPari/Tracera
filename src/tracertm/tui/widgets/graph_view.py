"""Graph view widget for TUI."""

try:
    from textual.widgets import Static
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    class Static:
        pass

if TEXTUAL_AVAILABLE:
    class GraphViewWidget(Static):
        """Widget for displaying graph visualization."""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__("Graph View", *args, **kwargs)
else:
    class GraphViewWidget:
        """Placeholder when Textual is not installed."""
        pass
