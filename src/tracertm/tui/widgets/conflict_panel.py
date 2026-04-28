"""Conflict panel widget for TUI.

Displays and manages sync conflicts with resolution options.
"""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from tracertm.storage.conflict_resolver import Conflict, compare_versions

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

        class Container:  # type: ignore[no-redef]
            """Container."""

        class Vertical:  # type: ignore[no-redef]
            """Vertical."""

        class DataTable:  # type: ignore[no-redef]
            """DataTable."""

        class Label:  # type: ignore[no-redef]
            """Label."""

        class Static:  # type: ignore[no-redef]
            """Static."""

        class Button:  # type: ignore[no-redef]
            """Button."""

        class Binding:  # type: ignore[no-redef]
            """Binding."""

        class Message:  # type: ignore[no-redef]
            """Message."""

        class ComposeResult:  # type: ignore[no-redef]
            """ComposeResult."""


if TEXTUAL_AVAILABLE:

    class ConflictPanel(Container):
        """Panel for displaying and resolving sync conflicts.

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

        def __init__(self, conflicts: list[object] | None = None, *args: object, **kwargs: object) -> None:
            """Initialize conflict panel.

            Args:
                conflicts: List of Conflict objects
            """
            super().__init__(*args, **kwargs)  # type: ignore[arg-type]
            self.conflicts = conflicts or []
            self.selected_conflict = None

        def compose(self) -> ComposeResult:
            """Compose the conflict panel."""
            yield Static("⚠ Sync Conflicts Detected", id="conflict-title")

            with Vertical(id="conflict-list"):
                yield Label("Unresolved Conflicts:")
                table: Any = DataTable(id="conflicts-table")
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
                local_v = conflict.local_version.vector_clock.version  # type: ignore[attr-defined]
                remote_v = conflict.remote_version.vector_clock.version  # type: ignore[attr-defined]
                detected = conflict.detected_at.strftime("%Y-%m-%d %H:%M")  # type: ignore[attr-defined]

                table.add_row(
                    conflict.entity_type,  # type: ignore[attr-defined]
                    conflict.entity_id[:12] + "...",  # type: ignore[attr-defined]
                    f"v{local_v}",
                    f"v{remote_v}",
                    detected,
                )

        def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
            """Handle conflict selection."""
            if event.row_index < len(self.conflicts):  # type: ignore[attr-defined]
                idx = event.row_index  # type: ignore[attr-defined]
                self.selected_conflict = (
                    self.conflicts[idx] if isinstance(idx, int) and idx < len(self.conflicts) else None  # type: ignore[assignment]
                )
                self.show_conflict_detail(self.selected_conflict)  # type: ignore[arg-type]

        def show_conflict_detail(self, conflict: Conflict) -> None:
            """Show detailed view of a conflict.

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

            def __init__(self, conflict: Conflict, strategy: str) -> None:
                """Initialize."""
                super().__init__()
                self.conflict = conflict
                self.strategy = strategy

        class ConflictPanelClosed(Message):
            """Message sent when panel is closed."""

            def __init__(self) -> None:
                """Initialize."""
                super().__init__()


if not TEXTUAL_AVAILABLE:
    # Fallback when Textual is not available (stub for type checker)
    class ConflictPanel:  # type: ignore[no-redef]
        """Placeholder when Textual is not installed."""

        BINDINGS: ClassVar[list] = []
        conflicts: list
        selected_conflict: object | None

        def __init__(self, conflicts: list[object] | None = None, *_args: object, **_kwargs: object) -> None:
            """Initialize."""
            self.conflicts = conflicts or []
            self.selected_conflict = None

        def compose(self) -> Iterator[object]:
            """Compose."""
            return iter(())

        def on_mount(self) -> None:
            """On mount."""

        def refresh_conflict_list(self) -> None:
            """Refresh conflict list."""

        def on_data_table_row_selected(self, event: object) -> None:
            """On data table row selected."""

        def show_conflict_detail(self, conflict: object) -> None:
            """Show conflict detail."""

        def action_resolve_local(self) -> None:
            """Action resolve local."""

        def action_resolve_remote(self) -> None:
            """Action resolve remote."""

        def action_resolve_manual(self) -> None:
            """Action resolve manual."""

        def action_close(self) -> None:
            """Action close."""

        def on_button_pressed(self, event: object) -> None:
            """On button pressed."""

        def post_message(self, message: object) -> None:
            """Post message."""

        class ConflictResolved:
            def __init__(self, conflict: object, strategy: str) -> None:
                """Initialize."""

        class ConflictPanelClosed:
            def __init__(self) -> None:
                """Initialize."""
