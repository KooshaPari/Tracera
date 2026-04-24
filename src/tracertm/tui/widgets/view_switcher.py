"""View switcher widget for TUI."""

try:
    from textual.widgets import Tree

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Tree = object  # type: ignore[assignment,misc]


class ViewSwitcherWidget(Tree):
    """Widget for switching between views."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize."""
        if TEXTUAL_AVAILABLE:
            super().__init__("Views", *args, **kwargs)  # type: ignore[arg-type]

    def on_mount(self) -> None:
        """Called when widget is mounted - setup views here."""
        if TEXTUAL_AVAILABLE:
            self.setup_views()

    def setup_views(self) -> None:
        """Setup view tree."""
        views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
        for view in views:
            if TEXTUAL_AVAILABLE:
                self.root.add(view, data=view)
