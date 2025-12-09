# Storage Helper - Quick Reference

**Module:** `tracertm.cli.storage_helper`

## Essential Imports

```python
from tracertm.cli.storage_helper import (
    get_storage_manager,      # Get singleton storage
    get_current_project,      # Get current project
    require_project,          # Decorator: ensure project
    with_sync,                # Decorator: auto-sync
    handle_storage_error,     # Decorator: error handling
    show_sync_status,         # Display sync status
    format_item_for_display,  # Format single item
    format_items_table,       # Format item list
    format_link_for_display,  # Format single link
    format_links_table,       # Format link list
)
```

---

## Common Patterns

### 1. List Command (Read-Only)

```python
@app.command()
@require_project()
@handle_storage_error
def list_items(item_type: str = "epic"):
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    # Get items
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)
    items = item_storage.list_items(item_type=item_type)

    # Display
    table = format_items_table(items, title=f"{item_type}s")
    console.print(table)
```

---

### 2. Show Command (Single Item)

```python
@app.command()
@require_project()
@handle_storage_error
def show_item(item_id: str):
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    # Get item
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)
    item = item_storage.get_item(item_id)

    if not item:
        console.print(f"[red]✗[/red] Item not found")
        raise typer.Exit(code=1)

    # Display
    from rich.panel import Panel
    table = format_item_for_display(item)
    console.print(Panel(table, title=item.title))
```

---

### 3. Create Command (Write with Sync)

```python
@app.command()
@require_project()
@handle_storage_error
@with_sync(enabled=True)  # Auto-sync after
def create_item(
    title: str,
    item_type: str = "epic",
    description: str | None = None,
):
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    # Create item
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    item = item_storage.create_item(
        title=title,
        item_type=item_type,
        description=description,
        status="todo",
        priority="medium",
    )

    console.print(f"[green]✓[/green] Created: {item.title}")
    # Sync happens automatically
```

---

### 4. Update Command (Write with Sync)

```python
@app.command()
@require_project()
@handle_storage_error
@with_sync(enabled=True)
def update_item(
    item_id: str,
    title: str | None = None,
    status: str | None = None,
):
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    # Update item
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    item = item_storage.update_item(
        item_id=item_id,
        title=title,
        status=status,
    )

    console.print(f"[green]✓[/green] Updated: {item.title}")
```

---

### 5. Sync Status Command

```python
@app.command("sync-status")
def check_sync():
    show_sync_status()
```

---

## Decorator Combinations

### Safe Read (No Sync)
```python
@app.command()
@require_project()
@handle_storage_error
def read_only_command():
    # ...
```

### Safe Write (With Sync)
```python
@app.command()
@require_project()
@handle_storage_error
@with_sync(enabled=True)
def write_command():
    # ...
```

### Global Command (No Project Required)
```python
@app.command()
@handle_storage_error
def global_command():
    # No @require_project - works without project
    # ...
```

---

## Error Handling

All decorators handle errors automatically:

- `@require_project()` → "No project selected" message
- `@handle_storage_error()` → Formatted error with hints
- `@with_sync()` → Warning if sync fails (doesn't fail command)

**Manual error handling only needed for specific business logic:**

```python
@app.command()
@require_project()
@handle_storage_error
def my_command(item_id: str):
    storage = get_storage_manager()
    item = storage.get_item(item_id)

    if not item:
        console.print(f"[red]✗[/red] Item not found: {item_id}")
        raise typer.Exit(code=1)  # Business logic error

    # ... process item
```

---

## Display Helpers

### Single Item (Detailed)
```python
table = format_item_for_display(item)
console.print(Panel(table, title=item.title))
```

### Multiple Items (Table)
```python
table = format_items_table(
    items,
    title="Epics",
    show_project=False,  # Optional
)
console.print(table)
```

### Single Link (Detailed)
```python
table = format_link_for_display(link, source_item, target_item)
console.print(table)
```

### Multiple Links (Table)
```python
# Enrich links with items
enriched = [
    (link, storage.get_item(link.source_item_id), storage.get_item(link.target_item_id))
    for link in links
]
table = format_links_table(enriched, title="Links")
console.print(table)
```

---

## Configuration

Check config values:
```python
from tracertm.config.manager import ConfigManager

config = ConfigManager()
auto_sync = config.get("auto_sync")
storage_dir = config.get("storage_dir")
api_endpoint = config.get("api_endpoint")
```

Set config values:
```bash
rtm config set auto_sync true
rtm config set storage_dir ~/.tracertm
rtm config set api_endpoint https://api.example.com
```

---

## Testing

Reset singleton between tests:
```python
from tracertm.cli.storage_helper import reset_storage_manager

@pytest.fixture(autouse=True)
def reset_storage():
    yield
    reset_storage_manager()
```

Mock storage manager:
```python
from unittest.mock import patch, MagicMock

@patch('tracertm.cli.storage_helper.get_storage_manager')
def test_command(mock_storage):
    mock_storage.return_value = MagicMock()
    # Test logic
```

---

## Common Gotchas

### 1. Decorator Order Matters
```python
# ✓ Correct order (inside to outside)
@app.command()
@require_project()      # Check first
@handle_storage_error   # Then wrap in error handling
@with_sync()            # Finally add sync
def my_command():
    pass

# ✗ Wrong order
@app.command()
@with_sync()            # Don't put sync first
@require_project()
def my_command():
    pass
```

### 2. Project Context in Global Commands
```python
# If command works with OR without project:
project = get_current_project()
if project:
    project_id, project_name = project
    # Project-specific logic
else:
    # Global logic
```

### 3. Item Display Truncation
```python
# Tables truncate long titles automatically
# For full titles, use Panel or show command
```

### 4. Sync Failures Don't Fail Commands
```python
# @with_sync() warns but doesn't fail
# Command completes, changes saved locally
# Sync retried later or manually via 'rtm sync'
```

---

## Performance Tips

1. **Use singleton storage** (get_storage_manager()) - don't create multiple instances
2. **Limit results** before formatting tables
3. **Batch operations** when possible
4. **Use @with_sync(enabled=False)** for batch imports to avoid per-item sync

```python
# Good: Batch with single sync
@with_sync(enabled=True)
def import_items(items: list):
    storage = get_storage_manager()
    for item_data in items:
        storage.create_item(**item_data)
    # Sync once at end

# Bad: Sync per item
def import_items_slow(items: list):
    for item_data in items:
        @with_sync(enabled=True)  # Syncs for each!
        def create():
            storage.create_item(**item_data)
```

---

## Full Example

Complete command with all features:

```python
import typer
from rich.console import Console
from rich.panel import Panel

from tracertm.cli.storage_helper import (
    format_item_for_display,
    format_items_table,
    get_current_project,
    get_storage_manager,
    handle_storage_error,
    require_project,
    with_sync,
)

app = typer.Typer(help="My commands")
console = Console()


@app.command("list")
@require_project()
@handle_storage_error
def list_epics(limit: int = 10):
    """List epics in current project."""
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    items = item_storage.list_items(item_type="epic")
    items = items[:limit]  # Limit results

    if items:
        table = format_items_table(items, title=f"Epics - {project_name}")
        console.print(table)
    else:
        console.print("[yellow]No epics found[/yellow]")


@app.command("show")
@require_project()
@handle_storage_error
def show_epic(item_id: str):
    """Show epic details."""
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    item = item_storage.get_item(item_id)
    if not item:
        console.print(f"[red]✗[/red] Epic not found: {item_id}")
        raise typer.Exit(code=1)

    table = format_item_for_display(item)
    console.print(Panel(table, title=item.title, border_style="blue"))


@app.command("create")
@require_project()
@handle_storage_error
@with_sync(enabled=True)
def create_epic(
    title: str = typer.Argument(...),
    description: str | None = typer.Option(None, "--description", "-d"),
    priority: str = typer.Option("medium", "--priority", "-p"),
):
    """Create new epic."""
    storage = get_storage_manager()
    project_id, project_name = get_current_project()

    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    item = item_storage.create_item(
        title=title,
        item_type="epic",
        description=description,
        status="todo",
        priority=priority,
    )

    console.print(f"[green]✓[/green] Epic created: {item.title}")
    console.print(f"[dim]ID: {item.id}[/dim]")


if __name__ == "__main__":
    app()
```

---

## See Also

- **Full Documentation:** `STORAGE_HELPER_GUIDE.md`
- **Implementation Summary:** `STORAGE_HELPER_SUMMARY.md`
- **Working Examples:** `src/tracertm/cli/commands/example_with_helper.py`
- **Source Code:** `src/tracertm/cli/storage_helper.py`
