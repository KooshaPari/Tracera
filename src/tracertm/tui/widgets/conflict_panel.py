"""
Conflict panel widget for TUI.

Displays and manages sync conflicts with resolution options.
"""

from typing import TYPE_CHECKING, ClassVar

try:
    from textual.app import ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Vertical
    from textual.message import Message
    from textual.widgets import Button, DataTable, Label, Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

    if TYPE_CHECKING:
        from textual.app import ComposeResult
        from textual.binding import Binding
        from textual.containers import Container, Vertical
        from textual.message import Message
        from textual.widgets import Button, DataTable, Label, Static
    else:

        class Container:
            pass

        class Vertical:
            pass

        class DataTable:
            pass

        class Label:
            pass

        class Static:
            pass

        class Button:
            pass

        class Binding:
            pass

        class Message:
            pass

        class ComposeResult:
            pass


if TEXTUAL_AVAILABLE:

    class ConflictPanel(Container):
        """
        Panel for displaying and resolving sync conflicts.

        Shows:
        - List of unresolved conflicts
        - Conflict details (local vs remote)
        - Resolution actions
        """

        BINDINGS: ClassVar[list] = [
            Binding("l", "resolve_local", "Use Local"),
            Binding("r", "resolve_remote", "Use Remote"),
            Binding("m", "resolve_manual", "Merge Manually"),
            Binding("escape", "close", "Close"),
        ]

        DEFAULT_CSS = """
        ConflictPanel {
            height: 100%;
            border: thick $error;
            background: $panel;
        }

        ConflictPanel #conflict-title {
            dock: top;
            height: 3;
            background: $error;
            content-align: center middle;
            text-style: bold;
        }

        ConflictPanel #conflict-list {
            height: 50%;
            border-bottom: solid $primary;
        }

        ConflictPanel #conflict-detail {
            height: 50%;
            padding: 1;
        }

        ConflictPanel .conflict-row {
            height: auto;
            margin: 1;
        }

        ConflictPanel .local-version {
            color: $accent;
        }

        ConflictPanel .remote-version {
            color: $warning;
        }

        ConflictPanel .actions {
            dock: bottom;
            height: 3;
            background: $surface;
        }
        """

        def __init__(self, conflicts: list | None = None, *args, **kwargs):
            """
            Initialize conflict panel.

            Args:
                conflicts: List of Conflict objects
            """
            super().__init__(*args, **kwargs)
            self.conflicts = conflicts or []
            self.selected_conflict = None

        def compose(self) -> ComposeResult:
            """Compose the conflict panel."""
            yield Static("⚠ Sync Conflicts Detected", id="conflict-title")

            with Vertical(id="conflict-list"):
                yield Label("Unresolved Conflicts:")
                table = DataTable(id="conflicts-table")
                table.add_columns("Type", "ID", "Local", "Remote", "Detected")
                yield table

            with Vertical(id="conflict-detail"):
                yield Label("Conflict Details:", id="detail-title")
                yield Static("Select a conflict to view details", id="detail-content")

            with Container(classes="actions"):
                yield Button("Use Local [L]", id="btn-local", variant="primary")
                yield Button("Use Remote [R]", id="btn-remote", variant="warning")
                yield Button("Merge Manually [M]", id="btn-manual", variant="success")
                yield Button("Close [ESC]", id="btn-close", variant="default")

        def on_mount(self) -> None:
            """Called when widget is mounted."""
            self.refresh_conflict_list()

        def refresh_conflict_list(self) -> None:
            """Refresh the conflict list display."""
            table = self.query_one("#conflicts-table", DataTable)
            table.clear()

            for conflict in self.conflicts:
                local_v = conflict.local_version.vector_clock.version
                remote_v = conflict.remote_version.vector_clock.version
                detected = conflict.detected_at.strftime("%Y-%m-%d %H:%M")

                table.add_row(
                    conflict.entity_type,
                    conflict.entity_id[:12] + "...",
                    f"v{local_v}",
                    f"v{remote_v}",
                    detected,
                )

        def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
            """Handle conflict selection."""
            if event.row_index < len(self.conflicts):
                self.selected_conflict = self.conflicts[event.row_index]
                self.show_conflict_detail(self.selected_conflict)

        def show_conflict_detail(self, conflict) -> None:
            """
            Show detailed view of a conflict.

            Args:
                conflict: Conflict object to display
            """
            detail_content = self.query_one("#detail-content", Static)

            local = conflict.local_version
            remote = conflict.remote_version

            # Build detail text
            lines = [
                f"[bold]Entity:[/] {conflict.entity_type} - {conflict.entity_id}",
                "",
                "[bold cyan]Local Version:[/]",
                f"  Version: {local.vector_clock.version}",
                f"  Timestamp: {local.vector_clock.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                f"  Client: {local.vector_clock.client_id}",
                "",
                "[bold yellow]Remote Version:[/]",
                f"  Version: {remote.vector_clock.version}",
                f"  Timestamp: {remote.vector_clock.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                f"  Client: {remote.vector_clock.client_id}",
                "",
                "[bold]Data Differences:[/]",
            ]

            # Compare data
            from tracertm.storage.conflict_resolver import compare_versions

            differences = compare_versions(local, remote)

            if differences["modified"]:
                lines.append(f"  Modified fields: {', '.join(differences['modified'])}")
            if differences["added"]:
                lines.append(f"  Added in remote: {', '.join(differences['added'])}")
            if differences["removed"]:
                lines.append(f"  Removed in remote: {', '.join(differences['removed'])}")

            detail_content.update("\n".join(lines))

        def action_resolve_local(self) -> None:
            """Resolve conflict using local version."""
            if self.selected_conflict:
                self.post_message(self.ConflictResolved(conflict=self.selected_conflict, strategy="local"))

        def action_resolve_remote(self) -> None:
            """Resolve conflict using remote version."""
            if self.selected_conflict:
                self.post_message(self.ConflictResolved(conflict=self.selected_conflict, strategy="remote"))

        def action_resolve_manual(self) -> None:
            """Resolve conflict manually."""
            if self.selected_conflict:
                self.post_message(self.ConflictResolved(conflict=self.selected_conflict, strategy="manual"))

        def action_close(self) -> None:
            """Close the conflict panel."""
            self.post_message(self.ConflictPanelClosed())

        def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            if event.button.id == "btn-local":
                self.action_resolve_local()
            elif event.button.id == "btn-remote":
                self.action_resolve_remote()
            elif event.button.id == "btn-manual":
                self.action_resolve_manual()
            elif event.button.id == "btn-close":
                self.action_close()

        # Custom messages for parent app
        class ConflictResolved(Message):
            """Message sent when conflict is resolved."""

            def __init__(self, conflict, strategy: str):
                super().__init__()
                self.conflict = conflict
                self.strategy = strategy

        class ConflictPanelClosed(Message):
            """Message sent when panel is closed."""

            def __init__(self):
                super().__init__()


if not TEXTUAL_AVAILABLE:
    # Fallback when Textual is not available (stub for type checker)
    class ConflictPanel:  # type: ignore[no-redef]
        """Placeholder when Textual is not installed."""

        BINDINGS: ClassVar[list] = []
        conflicts: list
        selected_conflict: object | None

        def __init__(self, conflicts: list | None = None, *args: object, **kwargs: object) -> None:
            self.conflicts = conflicts or []
            self.selected_conflict = None

        def compose(self):  # type: ignore[no-untyped-def]
            return iter(())

        def on_mount(self) -> None:
            pass

        def refresh_conflict_list(self) -> None:
            pass

        def on_data_table_row_selected(self, event: object) -> None:
            pass

        def show_conflict_detail(self, conflict: object) -> None:
            pass

        def action_resolve_local(self) -> None:
            pass

        def action_resolve_remote(self) -> None:
            pass

        def action_resolve_manual(self) -> None:
            pass

        def action_close(self) -> None:
            pass

        def on_button_pressed(self, event: object) -> None:
            pass

        def post_message(self, message: object) -> None:
            pass

        class ConflictResolved:
            def __init__(self, conflict: object, strategy: str) -> None: ...

        class ConflictPanelClosed:
            def __init__(self) -> None: ...
