"""
Main dashboard TUI application.

Provides interactive dashboard with project state, view switching, and item browsing.
"""


try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import DataTable, Footer, Header, Static, Tree
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    # Create dummy classes for type checking
    class App:
        pass
    class ComposeResult:
        pass
    class Container:
        pass
    class Header:
        pass
    class Footer:
        pass
    class DataTable:
        pass
    class Static:
        pass
    class Tree:
        pass
    class Binding:
        pass

from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.link import Link

if TEXTUAL_AVAILABLE:
    class DashboardApp(App):
        """Main dashboard TUI application."""

        CSS = """
        Screen {
            background: $surface;
        }

        #sidebar {
            width: 25%;
            border-right: wide $primary;
        }

        #main {
            width: 75%;
        }

        #state-panel {
            height: 30%;
            border-bottom: wide $primary;
        }

        #items-panel {
            height: 70%;
        }

        DataTable {
            height: 100%;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit", priority=True),
            Binding("v", "switch_view", "Switch View"),
            Binding("r", "refresh", "Refresh"),
            Binding("s", "search", "Search"),
            Binding("?", "help", "Help"),
        ]

        def __init__(self) -> None:
            super().__init__()
            self.config_manager = ConfigManager()
            self.project_id: str | None = None
            self.current_view: str = "FEATURE"
            self.db: DatabaseConnection | None = None

        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header(show_clock=True)
            with Horizontal():
                with Vertical(id="sidebar"):
                    yield Static("Views", id="views-title")
                    yield Tree("Views", id="view-tree")
                    yield Static("Project State", id="state-title")
                    yield Static("", id="state-summary")

                with Vertical(id="main"):
                    with Container(id="state-panel"):
                        yield Static("Project Statistics", id="stats-title")
                        yield DataTable(id="stats-table")
                    with Container(id="items-panel"):
                        yield Static(f"Items - {self.current_view}", id="items-title")
                        yield DataTable(id="items-table")

            yield Footer()

        def on_mount(self) -> None:
            """Called when app starts."""
            self.setup_database()
            self.load_project()
            self.setup_view_tree()
            self.refresh_data()

        def setup_database(self) -> None:
            """Setup database connection."""
            database_url = self.config_manager.get("database_url")
            if not database_url:
                self.exit(message="No database configured. Run 'rtm config init' first.")
                return

            self.db = DatabaseConnection(database_url)
            self.db.connect()

        def load_project(self) -> None:
            """Load current project."""
            self.project_id = self.config_manager.get("current_project_id")
            if not self.project_id:
                self.exit(message="No current project. Run 'rtm project init' first.")
                return

        def setup_view_tree(self) -> None:
            """Setup view tree widget."""
            view_tree = self.query_one("#view-tree", Tree)
            views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]

            for view in views:
                node = view_tree.root.add(view, data=view)
                if view == self.current_view:
                    node.expand()

        def refresh_data(self) -> None:
            """Refresh all data displays."""
            if not self.db or not self.project_id:
                return

            self.refresh_stats()
            self.refresh_items()

        def refresh_stats(self) -> None:
            """Refresh statistics display."""
            if not self.db or not self.project_id:
                return

            with Session(self.db.engine) as session:
                # Get item counts by view
                view_counts = {}
                for view in ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]:
                    count = session.query(Item).filter(
                        Item.project_id == self.project_id,
                        Item.view == view,
                        Item.deleted_at.is_(None),
                    ).count()
                    view_counts[view] = count

                # Get link count
                link_count = session.query(Link).filter(
                    Link.project_id == self.project_id
                ).count()

                # Update stats table
                stats_table = self.query_one("#stats-table", DataTable)
                stats_table.clear()
                stats_table.add_columns("View", "Items", "Links")

                for view, count in view_counts.items():
                    links_for_view = session.query(Link).join(
                        Item, Link.source_item_id == Item.id
                    ).filter(
                        Item.view == view,
                        Item.project_id == self.project_id,
                    ).count()
                    stats_table.add_row(view, str(count), str(links_for_view))

                stats_table.add_row("TOTAL", str(sum(view_counts.values())), str(link_count))

                # Update state summary
                state_summary = self.query_one("#state-summary", Static)
                total_items = sum(view_counts.values())
                state_summary.update(f"Total Items: {total_items}\nTotal Links: {link_count}")

        def refresh_items(self) -> None:
            """Refresh items table."""
            if not self.db or not self.project_id:
                return

            with Session(self.db.engine) as session:
                items = session.query(Item).filter(
                    Item.project_id == self.project_id,
                    Item.view == self.current_view,
                    Item.deleted_at.is_(None),
                ).limit(100).all()

                items_table = self.query_one("#items-table", DataTable)
                items_table.clear()
                items_table.add_columns("ID", "Title", "Type", "Status")

                for item in items:
                    items_table.add_row(
                        str(item.id)[:8],
                        item.title[:50],
                        item.item_type,
                        item.status,
                    )

        def on_tree_node_selected(self, event: "Tree.NodeSelected") -> None:
            """Handle view tree selection."""
            if event.node.data:
                self.current_view = event.node.data
                self.refresh_items()
                items_title = self.query_one("#items-title", Static)
                items_title.update(f"Items - {self.current_view}")

        def action_switch_view(self) -> None:
            """Switch to different view."""
            # Cycle through views
            views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
            current_idx = views.index(self.current_view) if self.current_view in views else 0
            next_idx = (current_idx + 1) % len(views)
            self.current_view = views[next_idx]
            self.refresh_items()
            items_title = self.query_one("#items-title", Static)
            items_title.update(f"Items - {self.current_view}")

        def action_refresh(self) -> None:
            """Refresh all data."""
            self.refresh_data()

        def action_search(self) -> None:
            """Open search dialog."""
            # TODO: Implement search dialog
            self.notify("Search not yet implemented", severity="warning")

        def action_help(self) -> None:
            """Show help."""
            self.notify("Press 'q' to quit, 'v' to switch view, 'r' to refresh", timeout=3)

        def on_unmount(self) -> None:
            """Cleanup on exit."""
            if self.db:
                self.db.close()

else:
    # Fallback when Textual is not available
    class DashboardApp:
        """Placeholder when Textual is not installed."""

        def __init__(self) -> None:
            raise ImportError(
                "Textual is required for TUI. Install with: pip install textual"
            )
