"""Sync status widget for TUI.

Displays real-time sync status, pending changes, and conflict notifications.
"""

from datetime import UTC, datetime
from typing import Any, TypeVar

# Time thresholds for relative time formatting
_SECONDS_PER_MINUTE = 60
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_DAY = 86400

T = TypeVar("T")

try:
    from textual.app import ComposeResult
    from textual.containers import Horizontal as TextualHorizontal
    from textual.css.query import QueryError
    from textual.reactive import reactive as textual_reactive
    from textual.widgets import Static as TextualStatic

    textual_available = True
    Static = TextualStatic
    Horizontal = TextualHorizontal
    reactive = textual_reactive
except ImportError:
    textual_available = False

    class QueryError(Exception):  # type: ignore[no-redef]
        """Placeholder when Textual is unavailable."""

    class Static:  # type: ignore[no-redef]
        """Static."""

        is_mounted: bool = False

        def query_one(self, _selector: str, _expect_type: type[Any]) -> object:
            """Query one."""
            msg = "Textual not available"
            raise RuntimeError(msg)

        def update(self, _content: str) -> None:
            """Update."""
            return

        def add_class(self, *_classes: str) -> None:
            """Add class."""
            return

        def remove_class(self, *_classes: str) -> None:
            """Remove class."""
            return

    class Horizontal:  # type: ignore[no-redef]
        """Horizontal."""

        def __init__(self, *_children: object, **_kwargs: object) -> None:
            """Initialize."""
            return

    class reactive[T]:  # type: ignore[no-redef]
        """reactive."""

        def __init__(self, default: T) -> None:
            """Initialize."""
            self.default = default


TEXTUAL_AVAILABLE = textual_available

if textual_available:

    class SyncStatusWidget(Static):
        """Widget displaying sync status with real-time updates.

        Shows:
        - Online/offline status
        - Pending changes count
        - Last sync timestamp
        - Sync in progress indicator
        - Conflict notifications
        """

        # Reactive attributes for automatic UI updates
        is_online: reactive[bool] = reactive(False)
        is_syncing: reactive[bool] = reactive(False)
        pending_changes: reactive[int] = reactive(0)
        last_sync: reactive[datetime | None] = reactive(None)
        conflicts_count: reactive[int] = reactive(0)
        last_error: reactive[str | None] = reactive(None)

        DEFAULT_CSS = """
        SyncStatusWidget {
            height: auto;
            padding: 0 1;
            background: $panel;
            border: solid $primary;
        }

        SyncStatusWidget .status-line {
            height: 1;
        }

        SyncStatusWidget .online {
            color: $success;
        }

        SyncStatusWidget .offline {
            color: $warning;
        }

        SyncStatusWidget .syncing {
            color: $accent;
        }

        SyncStatusWidget .error {
            color: $error;
        }

        SyncStatusWidget .conflict {
            color: $warning;
            text-style: bold;
        }
        """

        def compose(self) -> ComposeResult:
            """Compose the widget."""
            # Static/Horizontal are object when Textual is not installed; suppress for ty/pyright
            yield Horizontal(
                Static(id="connection-status", classes="status-line"),
                Static(id="sync-info", classes="status-line"),
                Static(id="conflict-info", classes="status-line"),
            )

        def on_mount(self) -> None:
            """Called when widget is mounted."""
            self.update_display()

        def watch_is_online(self, _new_value: bool) -> None:
            """React to online status changes."""
            self.update_display()

        def watch_is_syncing(self, _new_value: bool) -> None:
            """React to syncing status changes."""
            self.update_display()

        def watch_pending_changes(self, _new_value: int) -> None:
            """React to pending changes count changes."""
            self.update_display()

        def watch_last_sync(self, _new_value: datetime | None) -> None:
            """React to last sync timestamp changes."""
            self.update_display()

        def watch_conflicts_count(self, _new_value: int) -> None:
            """React to conflicts count changes."""
            self.update_display()

        def watch_last_error(self, _new_value: str | None) -> None:
            """React to error changes."""
            self.update_display()

        def update_display(self) -> None:
            """Update the display based on current state."""
            # Check if widget is mounted
            if not self.is_mounted:
                return

            try:
                # Connection status
                connection_status = self.query_one("#connection-status", Static)
            except QueryError:
                # Widget not yet composed
                return

            if self.is_syncing:
                connection_status.update("[bold cyan]⟳[/] Syncing...")
                connection_status.add_class("syncing")
                connection_status.remove_class("online", "offline", "error")
            elif self.last_error:
                connection_status.update(f"[bold red]✗[/] Error: {self.last_error}")
                connection_status.add_class("error")
                connection_status.remove_class("online", "offline", "syncing")
            elif self.is_online:
                connection_status.update("[bold green]●[/] Online")
                connection_status.add_class("online")
                connection_status.remove_class("offline", "syncing", "error")
            else:
                connection_status.update("[bold yellow]●[/] Offline")
                connection_status.add_class("offline")
                connection_status.remove_class("online", "syncing", "error")

            # Sync info
            sync_info = self.query_one("#sync-info", Static)
            if self.pending_changes > 0:
                sync_info.update(
                    f"[bold]{self.pending_changes}[/] pending change" + ("s" if self.pending_changes != 1 else ""),
                )
            elif self.last_sync:
                time_ago = self._format_time_ago(self.last_sync)
                sync_info.update(f"Last sync: {time_ago}")
            else:
                sync_info.update("Never synced")

            # Conflict info
            conflict_info = self.query_one("#conflict-info", Static)
            if self.conflicts_count > 0:
                conflict_info.update(
                    f"[bold yellow]⚠[/] {self.conflicts_count} conflict" + ("s" if self.conflicts_count != 1 else ""),
                )
                conflict_info.add_class("conflict")
            else:
                conflict_info.update("")
                conflict_info.remove_class("conflict")

        def _format_time_ago(self, dt: datetime) -> str:
            """Format datetime as relative time (e.g., '5 minutes ago').

            Args:
                dt: Datetime to format

            Returns:
                Formatted string
            """
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now(UTC)
            delta = now - dt

            seconds = int(delta.total_seconds())

            if seconds < _SECONDS_PER_MINUTE:
                return "just now"
            if seconds < _SECONDS_PER_HOUR:
                minutes = seconds // _SECONDS_PER_MINUTE
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            if seconds < _SECONDS_PER_DAY:
                hours = seconds // _SECONDS_PER_HOUR
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            days = seconds // _SECONDS_PER_DAY
            return f"{days} day{'s' if days != 1 else ''} ago"

        def set_online(self, online: bool) -> None:
            """Set online status.

            Args:
                online: True if online
            """
            self.is_online = online

        def set_syncing(self, syncing: bool) -> None:
            """Set syncing status.

            Args:
                syncing: True if syncing
            """
            self.is_syncing = syncing

        def set_pending_changes(self, count: int) -> None:
            """Set pending changes count.

            Args:
                count: Number of pending changes
            """
            self.pending_changes = count

        def set_last_sync(self, timestamp: datetime | None) -> None:
            """Set last sync timestamp.

            Args:
                timestamp: Last sync time
            """
            self.last_sync = timestamp

        def set_conflicts(self, count: int) -> None:
            """Set conflicts count.

            Args:
                count: Number of conflicts
            """
            self.conflicts_count = count

        def set_error(self, error: str | None) -> None:
            """Set error message.

            Args:
                error: Error message or None to clear
            """
            self.last_error = error

    class CompactSyncStatus(Static):
        """Compact single-line sync status widget for headers/footers."""

        is_online: reactive[bool] = reactive(False)
        is_syncing: reactive[bool] = reactive(False)
        pending_changes: reactive[int] = reactive(0)
        conflicts_count: reactive[int] = reactive(0)

        def render(self) -> str:
            """Render compact status line."""
            parts = []

            # Connection indicator
            if self.is_syncing:
                parts.append("[cyan]⟳[/]")
            elif self.is_online:
                parts.append("[green]●[/]")
            else:
                parts.append("[yellow]●[/]")

            # Pending changes
            if self.pending_changes > 0:
                parts.append(f"[bold]{self.pending_changes}[/] pending")

            # Conflicts
            if self.conflicts_count > 0:
                parts.append(f"[yellow]⚠{self.conflicts_count}[/]")

            return " | ".join(parts) if parts else "[dim]Offline[/]"

        def set_online(self, online: bool) -> None:
            """Set online status."""
            self.is_online = online

        def set_syncing(self, syncing: bool) -> None:
            """Set syncing status."""
            self.is_syncing = syncing

        def set_pending_changes(self, count: int) -> None:
            """Set pending changes count."""
            self.pending_changes = count

        def set_conflicts(self, count: int) -> None:
            """Set conflicts count."""
            self.conflicts_count = count
