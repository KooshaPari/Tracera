"""Item list widget for TUI."""

try:
    from textual.widgets import DataTable

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    DataTable = object  # type: ignore[assignment,misc]


class ItemListWidget(DataTable):
    """Widget for displaying items in a table."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize."""
        if TEXTUAL_AVAILABLE:
            super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self._columns_added = False

    def on_mount(self) -> None:
        """Called when widget is mounted - setup columns here."""
        if not self._columns_added and TEXTUAL_AVAILABLE:
            self.add_columns("ID", "Title", "Type", "Status")
            self._columns_added = True
