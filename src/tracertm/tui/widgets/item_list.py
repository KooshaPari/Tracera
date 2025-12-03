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
            self.add_columns("ID", "Title", "Type", "Status")
else:
    class ItemListWidget:
        """Placeholder when Textual is not installed."""
        pass
