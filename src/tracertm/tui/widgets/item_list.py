"""Item list widget for TUI."""

try:
    from textual.widgets import DataTable
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    class DataTable:
        pass

if TEXTUAL_AVAILABLE:
    class ItemListWidget(DataTable):
        """Widget for displaying items in a table."""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self._columns_added = False

        def on_mount(self) -> None:
            """Called when widget is mounted - setup columns here."""
            if not self._columns_added:
                self.add_columns("ID", "Title", "Type", "Status")
                self._columns_added = True
else:
    class ItemListWidget:
        """Placeholder when Textual is not installed."""
        pass
