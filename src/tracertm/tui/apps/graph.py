"""Graph visualization TUI application.

Visualizes item relationships and links as a graph.
"""

from typing import TYPE_CHECKING, ClassVar

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import DataTable, Footer, Header, Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

    if TYPE_CHECKING:
        from textual.app import App, ComposeResult
        from textual.binding import Binding
        from textual.containers import Container
        from textual.widgets import DataTable, Footer, Header, Static
    else:

        class App:  # type: ignore[no-redef]
            """App."""

        class ComposeResult:  # type: ignore[no-redef]
            """ComposeResult."""

        class Container:  # type: ignore[no-redef]
            """Container."""

        class Header:  # type: ignore[no-redef]
            """Header."""

        class Footer:  # type: ignore[no-redef]
            """Footer."""

        class Static:  # type: ignore[no-redef]
            """Static."""

        class DataTable:  # type: ignore[no-redef]
            """DataTable."""

        class Binding:  # type: ignore[no-redef]
            """Binding."""


from sqlalchemy.orm import Session
from textual.containers import Horizontal, Vertical

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.link import Link

if TEXTUAL_AVAILABLE:

    class GraphApp(App):
        """Graph visualization TUI application."""

        CSS = """
        Screen {
            background: $surface;
        }

        #graph-panel {
            width: 75%;
            border-right: wide $primary;
        }

        #info-panel {
            width: 25%;
        }

        #graph-canvas {
            height: 100%;
            border: wide $primary;
        }
        """

        BINDINGS: ClassVar[list] = [
            Binding("q", "quit", "Quit", priority=True),
            Binding("r", "refresh", "Refresh"),
            Binding("+", "zoom_in", "Zoom In"),
            Binding("-", "zoom_out", "Zoom Out"),
            Binding("?", "help", "Help"),
        ]

        def __init__(self) -> None:
            """Initialize."""
            super().__init__()
            self.config_manager = ConfigManager()
            self.project_id: str | None = None
            self.db: DatabaseConnection | None = None
            self.nodes: dict[str, tuple[int, int]] = {}  # item_id -> (x, y)
            self.links: list[tuple[str, str]] = []  # (source_id, target_id)
            self.zoom: float = 1.0

        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header(show_clock=True)
            with Horizontal():
                with Vertical(id="graph-panel"):
                    yield Static("Relationship Graph", id="graph-title")
                    yield Static("", id="graph-canvas")

                with Vertical(id="info-panel"):
                    yield Static("Graph Info", id="info-title")
                    yield DataTable(id="link-table")
                    yield Static("", id="graph-stats")

            yield Footer()

        def on_mount(self) -> None:
            """Called when app starts."""
            self.setup_database()
            self.load_project()
            self.load_graph_data()
            self.render_graph()

        def setup_database(self) -> None:
            """Setup database connection."""
            database_url_obj = self.config_manager.get("database_url")
            database_url = str(database_url_obj) if database_url_obj else None
            if not database_url:
                self.exit(message="No database configured. Run 'rtm config init' first.")
                return

            self.db = DatabaseConnection(str(database_url)) if database_url else DatabaseConnection("")
            self.db.connect()

        def load_project(self) -> None:
            """Load current project."""
            self.project_id = self.config_manager.get("current_project_id")  # type: ignore[assignment]
            if not self.project_id:
                self.exit(message="No current project. Run 'rtm project init' first.")
                return

        def load_graph_data(self) -> None:
            """Load graph data (items and links)."""
            if not self.db or not self.project_id:
                return

            with Session(self.db.engine) as session:
                # Get items
                items = (
                    session
                    .query(Item)
                    .filter(
                        Item.project_id == self.project_id,
                        Item.deleted_at.is_(None),
                    )
                    .limit(50)
                    .all()
                )  # Limit for performance

                # Simple layout: grid
                cols = int(len(items) ** 0.5) + 1
                for i, item in enumerate(items):
                    x = (i % cols) * 20
                    y = (i // cols) * 5
                    self.nodes[item.id] = (x, y)  # type: ignore[index]

                # Get links
                links = session.query(Link).filter(Link.project_id == self.project_id).limit(100).all()

                self.links = [
                    (link.source_item_id, link.target_item_id)  # type: ignore[misc]
                    for link in links
                    if link.source_item_id in self.nodes and link.target_item_id in self.nodes
                ]

        def render_graph(self) -> None:
            """Render graph visualization."""
            canvas = self.query_one("#graph-canvas", Static)

            # Simple ASCII graph representation
            lines = ["Relationship Graph\n"]
            lines.append(f"Nodes: {len(self.nodes)}, Links: {len(self.links)}\n\n")

            # Show link table
            link_table = self.query_one("#link-table", DataTable)
            link_table.clear()
            link_table.add_columns("Source", "Target", "Type")

            with Session(self.db.engine) as session:  # type: ignore[union-attr]
                for source_id, target_id in self.links[:20]:  # Limit display
                    source = session.query(Item).filter(Item.id == source_id).first()
                    target = session.query(Item).filter(Item.id == target_id).first()
                    if source and target:
                        link = (
                            session
                            .query(Link)
                            .filter(Link.source_item_id == source_id, Link.target_item_id == target_id)
                            .first()
                        )
                        link_type = link.link_type if link else "unknown"
                        link_table.add_row(
                            source.title[:30],
                            target.title[:30],
                            link_type,
                        )

            # Update stats
            stats = self.query_one("#graph-stats", Static)
            stats.update(f"Nodes: {len(self.nodes)}\nLinks: {len(self.links)}\nZoom: {self.zoom:.1f}x")

            # Simple graph visualization
            graph_text = "Graph Visualization\n"
            graph_text += "=" * 50 + "\n"
            graph_text += "Use +/- to zoom, 'r' to refresh\n"
            graph_text += f"Showing {len(self.nodes)} items and {len(self.links)} links\n"
            canvas.update(graph_text)

        def action_refresh(self) -> None:
            """Refresh graph data."""
            self.load_graph_data()
            self.render_graph()

        def action_zoom_in(self) -> None:
            """Zoom in."""
            self.zoom = min(self.zoom * 1.2, 5.0)
            self.render_graph()

        def action_zoom_out(self) -> None:
            """Zoom out."""
            self.zoom = max(self.zoom / 1.2, 0.5)
            self.render_graph()

        def action_help(self) -> None:
            """Show help."""
            self.notify("Press 'q' to quit, 'r' to refresh, '+/-' to zoom", timeout=3)

        def on_unmount(self) -> None:
            """Cleanup on exit."""
            if self.db:
                self.db.close()


if not TEXTUAL_AVAILABLE:

    class GraphApp:  # type: ignore[no-redef]
        """Placeholder when Textual is not installed."""

        project_id: str | None
        db: DatabaseConnection | None
        nodes: dict[str, tuple[int, int]]
        links: list[tuple[str, str]]
        zoom: float
        config_manager: object
        BINDINGS: ClassVar[list]

        def __init__(self) -> None:
            """Initialize."""
            msg = "Textual is required for TUI. Install with: pip install textual"
            raise ImportError(msg)

        def setup_database(self) -> None:
            """Setup database."""

        def load_graph_data(self) -> None:
            """Load graph data."""

        def render_graph(self) -> None:
            """Render graph."""

        def on_unmount(self) -> None:
            """On unmount."""

        def action_zoom_in(self) -> None:
            """Action zoom in."""

        def action_zoom_out(self) -> None:
            """Action zoom out."""

        def action_refresh(self) -> None:
            """Action refresh."""

        def action_help(self) -> None:
            """Action help."""

        def query_one(self, _selector: str, _widget_type: type | None = None) -> object:
            """Query one."""

        def notify(self, message: str, *args: object, **kwargs: object) -> None:
            """Notify."""

        def exit(self, *args: object, **kwargs: object) -> None:
            """Exit."""
