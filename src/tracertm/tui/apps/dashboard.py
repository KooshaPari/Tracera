"""Dashboard TUI application with LocalStorageManager integration.

Provides interactive dashboard with:
- Local storage integration (SQLite + Markdown)
- Real-time sync status
- Conflict notifications
- Offline-first operation
"""

from typing import TYPE_CHECKING, Any, ClassVar

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Button, DataTable, Footer, Header, Input, Static, Tree

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

    if TYPE_CHECKING:
        from textual.app import App, ComposeResult
        from textual.binding import Binding
        from textual.containers import Container
        from textual.widgets import Button, DataTable, Footer, Header, Input, Static, Tree
    else:
        # Create dummy classes for runtime when textual unavailable
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

        class DataTable:  # type: ignore[no-redef]
            """DataTable."""

        class Static:  # type: ignore[no-redef]
            """Static."""

        class Tree:  # type: ignore[no-redef]
            """Tree."""

        class Binding:  # type: ignore[no-redef]
            """Binding."""

        class Button:  # type: ignore[no-redef]
            """Button."""

        class Input:  # type: ignore[no-redef]
            """Input."""


import logging
from pathlib import Path

from textual.containers import Horizontal, Vertical

from tracertm.config.manager import ConfigManager
from tracertm.storage.sync_engine import SyncStatus
from tracertm.tui.adapters.storage_adapter import StorageAdapter
from tracertm.tui.widgets.conflict_panel import ConflictPanel
from tracertm.tui.widgets.sync_status import SyncStatusWidget

if TEXTUAL_AVAILABLE:

    class DashboardApp(App):
        """Dashboard with LocalStorageManager integration.

        Features:
        - Offline-first local storage
        - Real-time sync status
        - Conflict notifications
        - Combined SQLite + Markdown view
        """

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

        #sync-status-panel {
            height: auto;
            border-bottom: solid $primary;
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

        .conflict-banner {
            background: $error;
            color: $text;
            text-style: bold;
            height: 3;
            content-align: center middle;
        }
        """

        BINDINGS: ClassVar[list[Binding]] = [  # type: ignore[assignment]
            Binding("q", "quit", "Quit", priority=True),
            Binding("v", "switch_view", "Switch View"),
            Binding("r", "refresh", "Refresh"),
            Binding("ctrl+s", "sync", "Sync", priority=True),
            Binding("s", "search", "Search"),
            Binding("c", "show_conflicts", "Conflicts"),
            Binding("?", "help", "Help"),
        ]

        def __init__(self, base_dir: Path | None = None) -> None:
            """Initialize dashboard.

            Args:
                base_dir: Base directory for local storage
            """
            super().__init__()
            self.config_manager = ConfigManager()
            self.project_name: str | None = None
            self.current_view: str = "epic"
            self.current_project_id: str | None = None
            self.items_data: list[dict[str, Any]] | None = None
            self.db: object | None = None

            # Initialize storage adapter
            self.storage_adapter = StorageAdapter(base_dir=base_dir)

            # Track sync state
            self._is_syncing = False
            self._sync_timer: object | None = None

        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header(show_clock=True)

            # Sync status bar
            with Container(id="sync-status-panel"):
                yield SyncStatusWidget(id="sync-status")

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
            self.load_project()
            self.setup_view_tree()
            self.setup_storage_callbacks()
            self.refresh_data()
            self.start_sync_status_updates()

        def load_project(self) -> None:
            """Load current project from config."""
            project_obj = self.config_manager.get("current_project")
            self.project_name = str(project_obj) if project_obj else None
            if not self.project_name:
                self.exit(message="No current project. Run 'rtm project init' first.")
                return

        def setup_view_tree(self) -> None:
            """Setup view tree widget."""
            view_tree = self.query_one("#view-tree", Tree)
            views = [
                "epic",
                "story",
                "test",
                "task",
            ]

            for view in views:
                node = view_tree.root.add(view.upper(), data=view)
                if view == self.current_view:
                    node.expand()

        def setup_storage_callbacks(self) -> None:
            """Setup reactive callbacks for storage events."""
            # Sync status updates
            self.storage_adapter.on_sync_status_change(self._on_sync_status_change)

            # Conflict notifications
            self.storage_adapter.on_conflict_detected(self._on_conflict_detected)

            # Item changes
            self.storage_adapter.on_item_change(self._on_item_change)

        def start_sync_status_updates(self) -> None:
            """Start periodic sync status updates."""
            self._sync_timer = self.set_interval(5.0, self.update_sync_status)

        def update_sync_status(self) -> None:
            """Update sync status display."""
            sync_widget = self.query_one("#sync-status", SyncStatusWidget)
            state = self.storage_adapter.get_sync_status()

            sync_widget.set_online(state.status != SyncStatus.ERROR)
            sync_widget.set_syncing(state.status == SyncStatus.SYNCING)
            sync_widget.set_pending_changes(state.pending_changes)
            sync_widget.set_last_sync(state.last_sync)
            sync_widget.set_conflicts(state.conflicts_count)
            sync_widget.set_error(state.last_error)

        def refresh_data(self) -> None:
            """Refresh all data displays."""
            if not self.project_name:
                return

            project = self.storage_adapter.get_project(self.project_name)
            if not project:
                # Create project if doesn't exist
                project = self.storage_adapter.create_project(self.project_name)

            self.refresh_stats(project)
            self.refresh_items(project)

        def refresh_stats(self, project: object) -> None:
            """Refresh statistics display."""
            stats = self.storage_adapter.get_project_stats(project)  # type: ignore[arg-type]

            # Update stats table
            stats_table = self.query_one("#stats-table", DataTable)
            stats_table.clear()
            stats_table.add_columns("Type", "Count", "Status Distribution")

            # Items by type
            for item_type, count in stats["items_by_type"].items():
                stats_table.add_row(item_type.upper(), str(count), "")

            # Add separator
            stats_table.add_row("---", "---", "---")

            # Total
            stats_table.add_row("TOTAL", str(stats["total_items"]), f"{stats['total_links']} links")

            # Update state summary
            state_summary = self.query_one("#state-summary", Static)
            summary_lines = [
                f"Total Items: {stats['total_items']}",
                f"Total Links: {stats['total_links']}",
                "",
                "Status:",
            ]
            for status, count in stats["items_by_status"].items():
                summary_lines.append(f"  {status}: {count}")

            state_summary.update("\n".join(summary_lines))

        def refresh_items(self, project: object) -> None:
            """Refresh items table."""
            items = self.storage_adapter.list_items(project, item_type=self.current_view)  # type: ignore[arg-type]

            items_table = self.query_one("#items-table", DataTable)
            items_table.clear()
            items_table.add_columns("ID", "Title", "Status", "Priority", "Source")

            for item in items:
                # Check if item has markdown file
                has_markdown = "content_hash" in (item.item_metadata or {})
                source = "SQLite+MD" if has_markdown else "SQLite"

                items_table.add_row(
                    str(item.id)[:8] + "...",
                    item.title[:40],
                    item.status,
                    item.priority,
                    source,
                )

        def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
            """Handle view tree selection."""
            if event.node.data:
                self.current_view = event.node.data
                self.refresh_items(self.storage_adapter.get_project(self.project_name))  # type: ignore[arg-type]
                items_title = self.query_one("#items-title", Static)
                items_title.update(f"Items - {self.current_view.upper()}")

        def action_switch_view(self) -> None:
            """Switch to different view."""
            views = ["epic", "story", "test", "task"]
            current_idx = views.index(self.current_view) if self.current_view in views else 0
            next_idx = (current_idx + 1) % len(views)
            self.current_view = views[next_idx]
            self.refresh_data()
            items_title = self.query_one("#items-title", Static)
            items_title.update(f"Items - {self.current_view.upper()}")

        def action_refresh(self) -> None:
            """Refresh all data."""
            self.refresh_data()
            self.notify("Data refreshed", severity="information")

        async def action_sync(self) -> None:
            """Trigger sync operation."""
            if self._is_syncing:
                self.notify("Sync already in progress", severity="warning")
                return

            self._is_syncing = True
            self.notify("Starting sync...", severity="information")

            try:
                result = await self.storage_adapter.trigger_sync()

                if result["success"]:
                    self.notify(
                        f"Sync complete: {result['entities_synced']} entities synced",
                        severity="information",
                        timeout=5,
                    )
                    self.refresh_data()
                else:
                    error_msg = result.get("error", "Unknown error")
                    self.notify(f"Sync failed: {error_msg}", severity="error")

            except (ConnectionError, OSError, RuntimeError, TimeoutError, ValueError) as error:
                self.notify(f"Sync error: {error}", severity="error")
            finally:
                self._is_syncing = False

        def action_search(self) -> None:
            """Open search dialog."""
            try:

                class SearchDialog(Container):
                    """Search dialog for items."""

                    def __init__(self, dashboard: "DashboardApp") -> None:
                        super().__init__()
                        self.dashboard = dashboard
                        self.border_title = "Search Items"

                    def compose(self) -> ComposeResult:
                        with Horizontal():
                            yield Input(placeholder="Enter search query...", id="search_input")
                            yield Button("Search", id="search_btn")
                            yield Button("Cancel", id="cancel_btn")

                    def on_button_pressed(self, event: Button.Pressed) -> None:
                        if event.button.id == "search_btn":
                            search_input = self.query_one("#search_input", Input)
                            query = search_input.value
                            if query:
                                self.dashboard.perform_search(query)
                            self.remove()
                        elif event.button.id == "cancel_btn":
                            self.remove()

                # Create and show search dialog
                search_dialog = SearchDialog(self)
                self.mount(search_dialog)

                # Focus on input field
                self.query_one("#search_input", Input).focus()
                self.notify("Search dialog opened", timeout=2)

            except ImportError:
                self.notify("Search UI not available", severity="warning")

        def perform_search(self, query: str) -> None:
            """Perform search on items.

            Args:
                query: Search query string (searches name, type, status)
            """
            try:
                # For now, fall back to simple filtering
                if self.items_data is not None:
                    query_lower = query.lower()
                    matched = [
                        item
                        for item in self.items_data
                        if query_lower in item.get("title", "").lower() or query_lower in item.get("type", "").lower()
                    ]
                    self.notify(f"Found {len(matched)} items matching '{query}'", timeout=2)
                else:
                    self.notify("Search complete", timeout=2)

            except (AttributeError, TypeError, ValueError) as error:
                self.notify(f"Search error: {error!s}", severity="error")

        def action_show_conflicts(self) -> None:
            """Show conflicts panel."""
            conflicts = self.storage_adapter.get_unresolved_conflicts()

            if not conflicts:
                self.notify("No unresolved conflicts", severity="information")
                return

            # Show conflict panel as modal
            self.push_screen(ConflictPanel(conflicts=conflicts))  # type: ignore[arg-type,call-overload]

        def action_help(self) -> None:
            """Show help."""
            help_text = (
                "Keyboard Shortcuts:\n"
                "  q: Quit\n"
                "  v: Switch view\n"
                "  r: Refresh\n"
                "  Ctrl+S: Sync\n"
                "  s: Search\n"
                "  c: Show conflicts\n"
                "  ?: This help"
            )
            self.notify(help_text, timeout=10)

        # Callback handlers

        def _on_sync_status_change(self, state: object) -> None:
            """Handle sync status changes."""
            # Use call_from_thread for thread-safe updates
            try:
                self.call_from_thread(self.update_sync_status)

                # Show notification for important status changes
                if state.status == SyncStatus.SUCCESS:  # type: ignore[attr-defined]
                    self.call_from_thread(
                        self.notify,
                        f"Sync completed: {state.synced_entities} entities",  # type: ignore[attr-defined]
                        severity="information",
                    )
                elif state.status == SyncStatus.ERROR:  # type: ignore[attr-defined]
                    self.call_from_thread(
                        self.notify,
                        f"Sync error: {state.last_error}",  # type: ignore[attr-defined]
                        severity="error",
                    )
                elif state.status == SyncStatus.CONFLICT:  # type: ignore[attr-defined]
                    self.call_from_thread(
                        self.notify,
                        f"Conflicts detected: {state.conflicts_count}",  # type: ignore[attr-defined]
                        severity="warning",
                    )
            except (AttributeError, RuntimeError, TypeError, ValueError) as error:
                logging.getLogger(__name__).debug("App not running, ignoring sync status callback: %s", error)

        def _on_conflict_detected(self, conflict: object) -> None:
            """Handle conflict detection."""
            try:
                self.call_from_thread(
                    self.notify,
                    f"Conflict detected: {conflict.entity_type} {conflict.entity_id[:12]}",  # type: ignore[attr-defined]
                    severity="warning",
                )
                self.call_from_thread(self.update_sync_status)
            except (AttributeError, RuntimeError, TypeError, ValueError) as error:
                logging.getLogger(__name__).debug("App not running, ignoring conflict callback: %s", error)

        def _on_item_change(self, _item_id: str) -> None:
            """Handle item changes."""
            # Refresh items list after change
            try:
                self.call_from_thread(self.refresh_data)
            except RuntimeError as error:
                logging.getLogger(__name__).debug("App not running, ignoring item change callback: %s", error)

        def on_unmount(self) -> None:
            """Cleanup on exit."""
            if self._sync_timer:
                self._sync_timer.stop()  # type: ignore[attr-defined]


if not TEXTUAL_AVAILABLE:
    # Fallback when Textual is not available
    class DashboardApp:  # type: ignore[no-redef]
        """Placeholder when Textual is not installed."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            """Initialize."""
            msg = "Textual is required for TUI. Install with: pip install textual"
            raise ImportError(msg)
