# CLI/TUI Integration Guide for Conflict Resolution

This guide shows how to integrate the conflict resolver into TraceRTM's CLI and TUI interfaces.

## CLI Commands

### 1. List Conflicts

```python
# src/tracertm/cli/commands/conflicts.py

import click
from rich.console import Console
from rich.table import Table

from tracertm.database.connection import get_session
from tracertm.storage import ConflictResolver, ConflictStatus

console = Console()


@click.group()
def conflicts():
    """Manage sync conflicts."""
    pass


@conflicts.command("list")
@click.option("--type", type=click.Choice(["item", "project", "link"]), help="Filter by entity type")
@click.option("--status", type=click.Choice(["unresolved", "resolved"]), default="unresolved")
def list_conflicts(type, status):
    """List conflicts."""
    session = next(get_session())
    resolver = ConflictResolver(session)

    if status == "unresolved":
        conflicts_list = resolver.list_unresolved(entity_type=type)
    else:
        # Would need additional query method for resolved conflicts
        conflicts_list = []

    if not conflicts_list:
        console.print("[green]No conflicts found![/green]")
        return

    # Display table
    table = Table(title=f"Conflicts ({status})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Entity ID", style="green")
    table.add_column("Local v", style="blue")
    table.add_column("Remote v", style="blue")
    table.add_column("Detected", style="yellow")

    for conflict in conflicts_list:
        table.add_row(
            conflict.id[:20] + "...",
            conflict.entity_type,
            conflict.entity_id[:20] + "...",
            str(conflict.local_version.vector_clock.version),
            str(conflict.remote_version.vector_clock.version),
            conflict.detected_at.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)
```

### 2. Show Conflict Details

```python
@conflicts.command("show")
@click.argument("conflict_id")
def show_conflict(conflict_id):
    """Show detailed conflict information."""
    from tracertm.storage import format_conflict_summary, compare_versions

    session = next(get_session())
    resolver = ConflictResolver(session)

    conflict = resolver.get_conflict(conflict_id)

    if not conflict:
        console.print(f"[red]Conflict {conflict_id} not found[/red]")
        return

    # Print summary
    console.print(format_conflict_summary(conflict))
    console.print()

    # Print versions
    console.print("[cyan]Local Version:[/cyan]")
    console.print_json(data=conflict.local_version.data)
    console.print()

    console.print("[magenta]Remote Version:[/magenta]")
    console.print_json(data=conflict.remote_version.data)
    console.print()

    # Print diff
    diff = compare_versions(conflict.local_version, conflict.remote_version)

    if diff["added"]:
        console.print(f"[green]Added fields:[/green] {', '.join(diff['added'])}")
    if diff["removed"]:
        console.print(f"[red]Removed fields:[/red] {', '.join(diff['removed'])}")
    if diff["modified"]:
        console.print(f"[yellow]Modified fields:[/yellow] {', '.join(diff['modified'])}")

    # Print backup path
    if conflict.backup_path:
        console.print(f"\n[blue]Backup:[/blue] {conflict.backup_path}")
```

### 3. Resolve Conflicts

```python
@conflicts.command("resolve")
@click.argument("conflict_id")
@click.option(
    "--strategy",
    type=click.Choice(["auto", "local", "remote", "manual"]),
    default="auto",
    help="Resolution strategy",
)
def resolve_conflict(conflict_id, strategy):
    """Resolve a specific conflict."""
    from tracertm.storage import ConflictStrategy

    session = next(get_session())
    resolver = ConflictResolver(session)

    conflict = resolver.get_conflict(conflict_id)

    if not conflict:
        console.print(f"[red]Conflict {conflict_id} not found[/red]")
        return

    if conflict.status != ConflictStatus.UNRESOLVED:
        console.print(f"[yellow]Conflict already {conflict.status.value}[/yellow]")
        return

    # Map strategy
    strategy_map = {
        "auto": ConflictStrategy.LAST_WRITE_WINS,
        "local": ConflictStrategy.LOCAL_WINS,
        "remote": ConflictStrategy.REMOTE_WINS,
        "manual": ConflictStrategy.MANUAL,
    }

    if strategy == "manual":
        # Interactive manual resolution
        resolve_manual_interactive(resolver, conflict)
    else:
        # Automatic resolution
        result = resolver.resolve(conflict, strategy_map[strategy])

        console.print(
            f"[green]✓ Resolved conflict {conflict_id}[/green]\n"
            f"Strategy: {result.strategy_used.value}\n"
            f"Winner: {'local' if result.version == conflict.local_version else 'remote'}\n"
            f"Version: {result.version.vector_clock.version}"
        )


def resolve_manual_interactive(resolver, conflict):
    """Interactive manual resolution."""
    from tracertm.storage import compare_versions

    console.print("\n[bold]Manual Conflict Resolution[/bold]\n")

    # Show versions
    console.print("[cyan]Local Version:[/cyan]")
    console.print_json(data=conflict.local_version.data)
    console.print()

    console.print("[magenta]Remote Version:[/magenta]")
    console.print_json(data=conflict.remote_version.data)
    console.print()

    # Show diff
    diff = compare_versions(conflict.local_version, conflict.remote_version)
    console.print("[yellow]Differences:[/yellow]")
    console.print(f"  Added: {diff['added']}")
    console.print(f"  Removed: {diff['removed']}")
    console.print(f"  Modified: {diff['modified']}")
    console.print()

    # Get resolution choice
    choice = click.prompt(
        "Choose resolution",
        type=click.Choice(["local", "remote", "merge"]),
        default="merge",
    )

    if choice == "local":
        from tracertm.storage import ConflictStrategy
        result = resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)
        console.print(f"[green]✓ Using local version[/green]")

    elif choice == "remote":
        from tracertm.storage import ConflictStrategy
        result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)
        console.print(f"[green]✓ Using remote version[/green]")

    else:
        # Interactive merge
        merged_data = dict(conflict.local_version.data)

        console.print("\n[bold]Merging fields:[/bold]")
        for field in diff["modified"]:
            local_val = conflict.local_version.data.get(field)
            remote_val = conflict.remote_version.data.get(field)

            console.print(f"\n[yellow]{field}:[/yellow]")
            console.print(f"  Local:  {local_val}")
            console.print(f"  Remote: {remote_val}")

            choice = click.prompt(
                "  Choose",
                type=click.Choice(["local", "remote", "custom"]),
                default="local",
            )

            if choice == "local":
                merged_data[field] = local_val
            elif choice == "remote":
                merged_data[field] = remote_val
            else:
                custom_val = click.prompt("  Enter value")
                merged_data[field] = custom_val

        # Apply merged resolution
        result = resolver.resolve_manual(conflict, merged_data)
        console.print(f"\n[green]✓ Merged resolution complete[/green]")
```

### 4. Conflict Statistics

```python
@conflicts.command("stats")
def show_stats():
    """Show conflict statistics."""
    session = next(get_session())
    resolver = ConflictResolver(session)

    stats = resolver.get_conflict_stats()

    console.print("\n[bold]Conflict Statistics[/bold]\n")
    console.print(f"Total conflicts: {stats['total']}")
    console.print()

    # By status
    console.print("[cyan]By Status:[/cyan]")
    for status, count in stats["by_status"].items():
        console.print(f"  {status}: {count}")
    console.print()

    # By entity type
    console.print("[magenta]By Entity Type:[/magenta]")
    for entity_type, count in stats["by_entity_type"].items():
        console.print(f"  {entity_type}: {count}")
```

### 5. Batch Resolution

```python
@conflicts.command("resolve-all")
@click.option(
    "--strategy",
    type=click.Choice(["auto", "local", "remote"]),
    default="auto",
    help="Resolution strategy",
)
@click.option("--type", type=click.Choice(["item", "project", "link"]), help="Filter by entity type")
@click.confirmation_option(prompt="Resolve all conflicts?")
def resolve_all(strategy, type):
    """Resolve all unresolved conflicts."""
    from tracertm.storage import ConflictStrategy

    session = next(get_session())
    resolver = ConflictResolver(session)

    conflicts_list = resolver.list_unresolved(entity_type=type)

    if not conflicts_list:
        console.print("[green]No conflicts to resolve![/green]")
        return

    strategy_map = {
        "auto": ConflictStrategy.LAST_WRITE_WINS,
        "local": ConflictStrategy.LOCAL_WINS,
        "remote": ConflictStrategy.REMOTE_WINS,
    }

    resolved_count = 0
    failed_count = 0

    with console.status("[bold green]Resolving conflicts...") as status:
        for conflict in conflicts_list:
            try:
                result = resolver.resolve(conflict, strategy_map[strategy])
                resolved_count += 1
                console.print(f"[green]✓[/green] {conflict.id[:30]}...")
            except Exception as e:
                failed_count += 1
                console.print(f"[red]✗[/red] {conflict.id[:30]}: {e}")

    console.print(
        f"\n[bold]Summary:[/bold]\n"
        f"  Resolved: {resolved_count}\n"
        f"  Failed: {failed_count}"
    )
```

## TUI Integration (Textual)

### Conflict View Widget

```python
# src/tracertm/tui/widgets/conflicts.py

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from tracertm.storage import ConflictResolver


class ConflictsView(Container):
    """Widget for displaying and resolving conflicts."""

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.resolver = ConflictResolver(session)

    def compose(self) -> ComposeResult:
        yield Static("Sync Conflicts", id="conflicts-title")
        yield DataTable(id="conflicts-table")
        yield Horizontal(
            Button("Refresh", id="refresh-btn"),
            Button("Resolve Selected", id="resolve-btn"),
            Button("Resolve All", id="resolve-all-btn"),
            id="conflicts-buttons",
        )

    def on_mount(self) -> None:
        """Setup table when mounted."""
        table = self.query_one("#conflicts-table", DataTable)
        table.add_columns("ID", "Type", "Entity", "Local v", "Remote v", "Detected")
        self.refresh_conflicts()

    def refresh_conflicts(self) -> None:
        """Refresh conflict list."""
        table = self.query_one("#conflicts-table", DataTable)
        table.clear()

        conflicts = self.resolver.list_unresolved()

        for conflict in conflicts:
            table.add_row(
                conflict.id[:20],
                conflict.entity_type,
                conflict.entity_id[:20],
                str(conflict.local_version.vector_clock.version),
                str(conflict.remote_version.vector_clock.version),
                conflict.detected_at.strftime("%Y-%m-%d %H:%M"),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "refresh-btn":
            self.refresh_conflicts()

        elif event.button.id == "resolve-btn":
            table = self.query_one("#conflicts-table", DataTable)
            row = table.cursor_row
            if row >= 0:
                # Get conflict ID from selected row
                conflict_id = table.get_row_at(row)[0]
                self.resolve_conflict(conflict_id)

        elif event.button.id == "resolve-all-btn":
            self.resolve_all_conflicts()

    def resolve_conflict(self, conflict_id: str) -> None:
        """Resolve a specific conflict."""
        from tracertm.storage import ConflictStrategy

        conflict = self.resolver.get_conflict(conflict_id)
        if conflict:
            result = self.resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)
            self.refresh_conflicts()
            self.notify(f"Resolved: {conflict_id[:20]}")

    def resolve_all_conflicts(self) -> None:
        """Resolve all conflicts."""
        from tracertm.storage import ConflictStrategy

        conflicts = self.resolver.list_unresolved()
        for conflict in conflicts:
            self.resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)

        self.refresh_conflicts()
        self.notify(f"Resolved {len(conflicts)} conflicts")
```

## Integration with Sync Command

```python
# src/tracertm/cli/commands/sync.py

@click.command()
@click.option("--strategy", type=click.Choice(["auto", "local", "remote"]), default="auto")
@click.option("--resolve/--no-resolve", default=True, help="Auto-resolve conflicts")
def sync(strategy, resolve):
    """Sync local changes with remote."""
    from tracertm.storage import ConflictResolver, ConflictStrategy, SyncEngine

    session = next(get_session())
    resolver = ConflictResolver(session)
    sync_engine = SyncEngine(session, resolver)

    console.print("[bold]Starting sync...[/bold]\n")

    # Perform sync
    result = sync_engine.sync()

    # Handle conflicts
    if result.get("conflicts"):
        conflicts_count = len(result["conflicts"])
        console.print(f"\n[yellow]Found {conflicts_count} conflicts[/yellow]\n")

        if resolve:
            strategy_map = {
                "auto": ConflictStrategy.LAST_WRITE_WINS,
                "local": ConflictStrategy.LOCAL_WINS,
                "remote": ConflictStrategy.REMOTE_WINS,
            }

            for conflict_id in result["conflicts"]:
                conflict = resolver.get_conflict(conflict_id)
                resolved = resolver.resolve(conflict, strategy_map[strategy])
                console.print(f"[green]✓[/green] Resolved {conflict_id[:30]}")

            console.print(f"\n[green]All conflicts resolved using {strategy} strategy[/green]")
        else:
            console.print("[yellow]Use 'tracertm conflicts list' to review conflicts[/yellow]")
            console.print("[yellow]Use 'tracertm conflicts resolve <id>' to resolve manually[/yellow]")

    console.print(f"\n[green]Sync complete![/green]")
    console.print(f"  Pushed: {result.get('pushed', 0)}")
    console.print(f"  Pulled: {result.get('pulled', 0)}")
    console.print(f"  Conflicts: {len(result.get('conflicts', []))}")
```

## Configuration

Add conflict resolution settings to `~/.tracertm/config.yaml`:

```yaml
sync:
  # Conflict resolution strategy
  conflict_strategy: last_write_wins  # auto, local, remote, manual

  # Auto-resolve conflicts during sync
  auto_resolve: true

  # Backup directory
  backup_dir: ~/.tracertm/conflicts

  # Backup retention
  backup_retention_days: 30

  # Conflict notification
  notify_on_conflict: true
```

## Best Practices

1. **Default to Auto-Resolve**: Use `LAST_WRITE_WINS` for most workflows
2. **Notify Users**: Alert users when conflicts are detected
3. **Provide Details**: Show clear diff when conflicts occur
4. **Backup Everything**: Always create backups before resolution
5. **Track Statistics**: Monitor conflict rate to identify issues
6. **Enable Manual Review**: Provide option to review before resolution
7. **Clear Feedback**: Show what was resolved and how

## Example CLI Session

```bash
# Sync and auto-resolve conflicts
$ tracertm sync --strategy auto
Starting sync...

Found 2 conflicts

✓ Resolved conflict_item-123_1705329600
✓ Resolved conflict_item-456_1705329601

Sync complete!
  Pushed: 5
  Pulled: 3
  Conflicts: 2 (resolved)

# List conflicts
$ tracertm conflicts list
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ ID                   ┃ Type   ┃ Entity ID            ┃ Local v ┃ Remote v ┃ Detected        ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ conflict_item-789... │ item   │ item-789...          │ 4       │ 4        │ 2024-01-15 14:30│
└──────────────────────┴────────┴──────────────────────┴─────────┴──────────┴─────────────────┘

# Show conflict details
$ tracertm conflicts show conflict_item-789_1705329600
Conflict: item 'item-789'
  Local:  v4 @ 2024-01-15 14:30
  Remote: v4 @ 2024-01-15 14:35
  Status: unresolved
  Detected: 2024-01-15 14:35:00

Local Version:
{
  "title": "Feature Implementation",
  "status": "in_progress",
  "priority": "high"
}

Remote Version:
{
  "title": "Feature Implementation",
  "status": "done",
  "owner": "user-456"
}

Added fields: owner
Modified fields: status

Backup: /Users/user/.tracertm/conflicts/item/item-789_20240115_143500

# Resolve manually
$ tracertm conflicts resolve conflict_item-789_1705329600 --strategy manual
Manual Conflict Resolution

...interactive merge session...

✓ Merged resolution complete

# Get statistics
$ tracertm conflicts stats

Conflict Statistics

Total conflicts: 15

By Status:
  unresolved: 3
  resolved_auto: 10
  resolved_manual: 2

By Entity Type:
  item: 12
  project: 2
  link: 1
```
