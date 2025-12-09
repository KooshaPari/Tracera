"""State display widget for TUI."""

try:
    from textual.widgets import DataTable, Static
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    class Static:
        pass
    class DataTable:
        pass

if TEXTUAL_AVAILABLE:
    class StateDisplayWidget(DataTable):
        """Widget for displaying project state."""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self._columns_added = False

        def on_mount(self) -> None:
            """Called when widget is mounted - setup columns here."""
            if not self._columns_added:
                self.add_columns("View", "Items", "Links")
                self._columns_added = True
else:
    class StateDisplayWidget:
        """Placeholder when Textual is not installed."""
        pass
