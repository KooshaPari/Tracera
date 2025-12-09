"""View switcher widget for TUI."""

try:
    from textual.widgets import Tree
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    class Tree:
        pass

if TEXTUAL_AVAILABLE:
    class ViewSwitcherWidget(Tree):
        """Widget for switching between views."""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__("Views", *args, **kwargs)

        def on_mount(self) -> None:
            """Called when widget is mounted - setup views here."""
            self.setup_views()

        def setup_views(self) -> None:
            """Setup view tree."""
            views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
            for view in views:
                self.root.add(view, data=view)
else:
    class ViewSwitcherWidget:
        """Placeholder when Textual is not installed."""
        pass
