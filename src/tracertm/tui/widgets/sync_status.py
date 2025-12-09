"""
Sync status widget for TUI.

Displays real-time sync status, pending changes, and conflict notifications.
"""

from datetime import datetime

try:
    from textual.app import ComposeResult
    from textual.containers import Horizontal
    from textual.reactive import reactive
    from textual.widgets import Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

    class Static:
        pass

    class Horizontal:
        pass

    def reactive(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


if TEXTUAL_AVAILABLE:

    class SyncStatusWidget(Static):
        """
        Widget displaying sync status with real-time updates.

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
            yield Horizontal(
                Static(id="connection-status", classes="status-line"),
                Static(id="sync-info", classes="status-line"),
                Static(id="conflict-info", classes="status-line"),
            )

        def on_mount(self) -> None:
            """Called when widget is mounted."""
            self.update_display()

        def watch_is_online(self, new_value: bool) -> None:
            """React to online status changes."""
            self.update_display()

        def watch_is_syncing(self, new_value: bool) -> None:
            """React to syncing status changes."""
            self.update_display()

        def watch_pending_changes(self, new_value: int) -> None:
            """React to pending changes count changes."""
            self.update_display()

        def watch_last_sync(self, new_value: datetime | None) -> None:
            """React to last sync timestamp changes."""
            self.update_display()

        def watch_conflicts_count(self, new_value: int) -> None:
            """React to conflicts count changes."""
            self.update_display()

        def watch_last_error(self, new_value: str | None) -> None:
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
            except Exception:
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
                    f"[bold]{self.pending_changes}[/] pending change"
                    + ("s" if self.pending_changes != 1 else "")
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
                    f"[bold yellow]⚠[/] {self.conflicts_count} conflict"
                    + ("s" if self.conflicts_count != 1 else "")
                )
                conflict_info.add_class("conflict")
            else:
                conflict_info.update("")
                conflict_info.remove_class("conflict")

        def _format_time_ago(self, dt: datetime) -> str:
            """
            Format datetime as relative time (e.g., '5 minutes ago').

            Args:
                dt: Datetime to format

            Returns:
                Formatted string
            """
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            delta = now - dt

            seconds = int(delta.total_seconds())

            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif seconds < 86400:
                hours = seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = seconds // 86400
                return f"{days} day{'s' if days != 1 else ''} ago"

        def set_online(self, online: bool) -> None:
            """
            Set online status.

            Args:
                online: True if online
            """
            self.is_online = online

        def set_syncing(self, syncing: bool) -> None:
            """
            Set syncing status.

            Args:
                syncing: True if syncing
            """
            self.is_syncing = syncing

        def set_pending_changes(self, count: int) -> None:
            """
            Set pending changes count.

            Args:
                count: Number of pending changes
            """
            self.pending_changes = count

        def set_last_sync(self, timestamp: datetime | None) -> None:
            """
            Set last sync timestamp.

            Args:
                timestamp: Last sync time
            """
            self.last_sync = timestamp

        def set_conflicts(self, count: int) -> None:
            """
            Set conflicts count.

            Args:
                count: Number of conflicts
            """
            self.conflicts_count = count

        def set_error(self, error: str | None) -> None:
            """
            Set error message.

            Args:
                error: Error message or None to clear
            """
            self.last_error = error


    class CompactSyncStatus(Static):
        """
        Compact single-line sync status widget for headers/footers.
        """

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


else:
    # Fallback when Textual is not available

    class SyncStatusWidget:
        """Placeholder when Textual is not installed."""

        pass

    class CompactSyncStatus:
        """Placeholder when Textual is not installed."""

        pass
