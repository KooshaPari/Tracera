"""
Item browser TUI application.

Interactive browser for viewing and navigating items.
"""


try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import DataTable, Footer, Header, Input, Static, Tree
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
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
    class Tree:
        pass
    class Static:
        pass
    class Input:
        pass
    class Binding:
        pass

from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item

if TEXTUAL_AVAILABLE:
    class BrowserApp(App):
        """Item browser TUI application."""

        CSS = """
        Screen {
            background: $surface;
        }

        #tree-panel {
            width: 30%;
            border-right: wide $primary;
        }

        #detail-panel {
            width: 70%;
        }

        Tree {
            height: 100%;
        }

        #item-details {
            height: 100%;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit", priority=True),
            Binding("r", "refresh", "Refresh"),
            Binding("f", "filter", "Filter"),
            Binding("?", "help", "Help"),
        ]

        def __init__(self) -> None:
            super().__init__()
            self.config_manager = ConfigManager()
            self.project_id: str | None = None
            self.current_view: str = "FEATURE"
            self.db: DatabaseConnection | None = None
            self.selected_item_id: str | None = None

        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header(show_clock=True)
            with Horizontal():
                with Vertical(id="tree-panel"):
                    yield Static("Item Hierarchy", id="tree-title")
                    yield Tree("Items", id="item-tree")
                    yield Static("Filter:", id="filter-label")
                    yield Input(placeholder="Search items...", id="filter-input")

                with Vertical(id="detail-panel"):
                    yield Static("Item Details", id="detail-title")
                    yield Static("", id="item-details")

            yield Footer()

        def on_mount(self) -> None:
            """Called when app starts."""
            self.setup_database()
            self.load_project()
            self.refresh_tree()

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

        def refresh_tree(self) -> None:
            """Refresh item tree."""
            if not self.db or not self.project_id:
                return

            item_tree = self.query_one("#item-tree", Tree)
            item_tree.clear()

            with Session(self.db.engine) as session:
                # Get root items (no parent)
                root_items = session.query(Item).filter(
                    Item.project_id == self.project_id,
                    Item.view == self.current_view,
                    Item.parent_id.is_(None),
                    Item.deleted_at.is_(None),
                ).order_by(Item.title).all()

                for item in root_items:
                    node = item_tree.root.add(item.title, data=item.id)
                    self._add_children(session, node, item.id)

        def _add_children(self, session: Session, parent_node: "Tree.Node", parent_id: str) -> None:
            """Recursively add children to tree."""
            children = session.query(Item).filter(
                Item.project_id == self.project_id,
                Item.parent_id == parent_id,
                Item.deleted_at.is_(None),
            ).order_by(Item.title).all()

            for child in children:
                child_node = parent_node.add(child.title, data=child.id)
                self._add_children(session, child_node, child.id)

        def on_tree_node_selected(self, event: "Tree.NodeSelected") -> None:
            """Handle item selection."""
            if event.node.data:
                self.selected_item_id = event.node.data
                self.show_item_details()

        def show_item_details(self) -> None:
            """Show details for selected item."""
            if not self.db or not self.selected_item_id:
                return

            with Session(self.db.engine) as session:
                item = session.query(Item).filter(Item.id == self.selected_item_id).first()
                if not item:
                    return

                details = f"""
[bold]Title:[/bold] {item.title}
[bold]View:[/bold] {item.view}
[bold]Type:[/bold] {item.item_type}
[bold]Status:[/bold] {item.status}
[bold]ID:[/bold] {item.id}

[bold]Description:[/bold]
{item.description or 'No description'}

[bold]Metadata:[/bold]
{item.item_metadata or '{}'}
                """.strip()

                item_details = self.query_one("#item-details", Static)
                item_details.update(details)

        def on_input_changed(self, event: "Input.Changed") -> None:
            """Handle filter input change."""
            # TODO: Implement filtering
            pass

        def action_refresh(self) -> None:
            """Refresh tree."""
            self.refresh_tree()

        def action_filter(self) -> None:
            """Focus filter input."""
            filter_input = self.query_one("#filter-input", Input)
            filter_input.focus()

        def action_help(self) -> None:
            """Show help."""
            self.notify("Press 'q' to quit, 'r' to refresh, 'f' to filter", timeout=3)

        def on_unmount(self) -> None:
            """Cleanup on exit."""
            if self.db:
                self.db.close()

else:
    class BrowserApp:
        """Placeholder when Textual is not installed."""

        def __init__(self) -> None:
            raise ImportError(
                "Textual is required for TUI. Install with: pip install textual"
            )
