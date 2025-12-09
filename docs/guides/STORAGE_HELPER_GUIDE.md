# Storage Helper Guide

## Overview

The `storage_helper.py` module provides a centralized set of utilities for CLI commands to interact with TraceRTM's storage layer. It eliminates code duplication and ensures consistent patterns across all commands.

**Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/storage_helper.py`

## Core Features

### 1. Singleton Storage Manager
- **Function:** `get_storage_manager()`
- **Purpose:** Provides a single LocalStorageManager instance across the CLI session
- **Benefits:** Avoids multiple database connections, ensures consistent state

### 2. Project Context Management
- **Functions:** `get_current_project()`, `require_project()`
- **Purpose:** Manages project selection and validation
- **Benefits:** Consistent project context across commands

### 3. Sync Management
- **Functions:** `with_sync()`, `show_sync_status()`
- **Purpose:** Automatic synchronization and status display
- **Benefits:** Offline-first with transparent sync

### 4. Display Formatting
- **Functions:** `format_item_for_display()`, `format_link_for_display()`, etc.
- **Purpose:** Consistent Rich console output
- **Benefits:** Beautiful, uniform CLI output

### 5. Error Handling
- **Decorator:** `handle_storage_error()`
- **Purpose:** Consistent error messages and exit codes
- **Benefits:** Better user experience, easier debugging

---

## API Reference

### Storage Manager

#### `get_storage_manager() -> LocalStorageManager`

Get or create singleton LocalStorageManager instance.

**Returns:** Configured storage manager instance

**Example:**
```python
from tracertm.cli.storage_helper import get_storage_manager

storage = get_storage_manager()
project_storage = storage.get_project_storage("my-project")
```

**Notes:**
- Maintains a single instance per CLI process
- Reads storage directory from config if set
- Defaults to `~/.tracertm`

---

#### `reset_storage_manager() -> None`

Reset the singleton storage manager (primarily for testing).

**Example:**
```python
from tracertm.cli.storage_helper import reset_storage_manager

# In tests
def teardown():
    reset_storage_manager()
```

---

### Project Context

#### `get_current_project() -> tuple[str, str] | None`

Get the current project ID and name from configuration.

**Returns:** Tuple of (project_id, project_name) or None if no project is set

**Example:**
```python
from tracertm.cli.storage_helper import get_current_project

project = get_current_project()
if project:
    project_id, project_name = project
    print(f"Working on: {project_name}")
else:
    print("No project selected")
```

---

#### `@require_project()`

Decorator that ensures a project is selected before executing command.

**Raises:** `typer.Exit(code=1)` if no project is currently selected

**Example:**
```python
import typer
from tracertm.cli.storage_helper import require_project

app = typer.Typer()

@app.command()
@require_project()
def my_command():
    # This code only runs if a project is selected
    print("Project is selected!")
```

**Output (no project):**
```
✗ No project selected. Use 'rtm project switch <name>' or 'rtm project init <name>' first.
```

---

### Sync Management

#### `@with_sync(enabled: bool = True)`

Decorator that triggers sync after command execution (if enabled).

**Args:**
- `enabled`: Whether to perform sync (default: True)

**Example:**
```python
import typer
from tracertm.cli.storage_helper import with_sync, require_project

app = typer.Typer()

@app.command()
@require_project()
@with_sync(enabled=True)
def create_item(title: str):
    # Create item logic
    storage = get_storage_manager()
    # ... create item
    # Sync will happen automatically after this completes
```

**Behavior:**
- Checks `auto_sync` config setting
- Non-blocking - doesn't fail command if sync fails
- Shows warning if sync fails
- Queues changes for later sync

---

#### `show_sync_status() -> None`

Display current sync status with rich formatting.

**Shows:**
- Last sync time (human-readable)
- Pending changes count
- Sync errors
- Auto-sync setting

**Example:**
```python
from tracertm.cli.storage_helper import show_sync_status

@app.command("sync-status")
def sync_status_command():
    show_sync_status()
```

**Output:**
```
╭─── Sync Status ──────────────────────────╮
│ ✓ Last sync: 2 hours ago                │
│ ! 5 pending change(s)                    │
│ ✗ 1 sync error(s)                        │
│ Auto-sync: enabled                       │
╰──────────────────────────────────────────╯

Recent Errors:
  ✗ item 8f4a1b2c...: Connection timeout
```

---

### Display Formatting

#### `format_item_for_display(item: Item) -> Table`

Format an Item for Rich console display.

**Args:**
- `item`: Item instance to format

**Returns:** Rich Table with formatted item details

**Example:**
```python
from tracertm.cli.storage_helper import get_storage_manager, format_item_for_display
from rich.console import Console

storage = get_storage_manager()
console = Console()

item = storage.get_item("item-id")
if item:
    table = format_item_for_display(item)
    console.print(table)
```

**Output:**
```
ID              8f4a1b2c...
Title           User Authentication Feature
External ID     EPIC-001
Type            epic
View            FEATURE
Status          in_progress
Priority        high
Owner           alice@example.com
Created         2025-01-15 10:30
Updated         2025-01-20 14:45
Version         3
```

---

#### `format_link_for_display(link: Link, source_item: Item | None = None, target_item: Item | None = None) -> Table`

Format a Link for Rich console display.

**Args:**
- `link`: Link instance to format
- `source_item`: Optional source Item for additional context
- `target_item`: Optional target Item for additional context

**Returns:** Rich Table with formatted link details

**Example:**
```python
from tracertm.cli.storage_helper import get_storage_manager, format_link_for_display

storage = get_storage_manager()
link = storage.get_link("link-id")
source = storage.get_item(link.source_item_id)
target = storage.get_item(link.target_item_id)

table = format_link_for_display(link, source, target)
console.print(table)
```

**Output:**
```
Link ID         a3b5c7d9...
Type            implements
Source          User Auth Epic (8f4a1b2c...)
Target          Login Story (2e6f8a1c...)
Created         2025-01-15 11:00
Metadata        verified=true, priority=high
```

---

#### `format_items_table(items: list[Item], title: str = "Items", show_project: bool = False) -> Table`

Format a list of Items as a Rich table.

**Args:**
- `items`: List of Item instances
- `title`: Table title (default: "Items")
- `show_project`: Whether to show project column (default: False)

**Returns:** Rich Table with formatted items list

**Example:**
```python
from tracertm.cli.storage_helper import get_storage_manager, format_items_table

storage = get_storage_manager()
project_storage = storage.get_project_storage("my-project")
project = project_storage.get_project()

item_storage = project_storage.get_item_storage(project)
items = item_storage.list_items(item_type="epic")

table = format_items_table(items, title="Epics")
console.print(table)
```

**Output:**
```
                                    Epics
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ ID        ┃ Title             ┃ Type      ┃ Status    ┃ Priority┃ Updated        ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 8f4a1b2c..│ User Auth         │ epic      │ done      │ high    │ 2025-01-20 14:45│
│ 2e6f8a1c..│ Payment Gateway   │ epic      │ in_progre │ high    │ 2025-01-19 16:30│
│ 5d9c2b4f..│ Analytics         │ epic      │ todo      │ medium  │ 2025-01-18 09:15│
└───────────┴───────────────────┴───────────┴───────────┴─────────┴────────────────┘
```

---

#### `format_links_table(links: list[tuple[Link, Item | None, Item | None]], title: str = "Links") -> Table`

Format a list of Links with context as a Rich table.

**Args:**
- `links`: List of (Link, source_item, target_item) tuples
- `title`: Table title (default: "Links")

**Returns:** Rich Table with formatted links list

**Example:**
```python
from tracertm.cli.storage_helper import format_links_table

storage = get_storage_manager()
project_storage = storage.get_project_storage("my-project")
project = project_storage.get_project()
item_storage = project_storage.get_item_storage(project)

links = item_storage.list_links(source_id="item-id")
enriched = [
    (link, item_storage.get_item(link.source_item_id), item_storage.get_item(link.target_item_id))
    for link in links
]

table = format_links_table(enriched, title="Outgoing Links")
console.print(table)
```

**Output:**
```
                            Outgoing Links
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Source                   ┃ Type          ┃ Target              ┃ Created        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ User Auth Epic           │ implements    │ Login Story         │ 2025-01-15 11:00│
│ User Auth Epic           │ implements    │ Signup Story        │ 2025-01-15 11:05│
│ User Auth Epic           │ tests         │ Auth Test Suite     │ 2025-01-16 14:20│
└──────────────────────────┴───────────────┴─────────────────────┴────────────────┘
```

---

### Error Handling

#### `@handle_storage_error()`

Decorator to provide consistent error handling for storage operations.

**Example:**
```python
import typer
from tracertm.cli.storage_helper import handle_storage_error, get_storage_manager

app = typer.Typer()

@app.command()
@handle_storage_error
def my_command(item_id: str):
    storage = get_storage_manager()
    item = storage.get_item(item_id)
    # ... operate on item
    # Errors are caught and formatted consistently
```

**Handles:**
- `FileNotFoundError` - Missing files or directories
- `ValueError` - Invalid input values
- General exceptions with helpful hints

**Output (error):**
```
✗ File not found: /path/to/missing/file
Check that the project is properly initialized.
```

---

## Usage Patterns

### Pattern 1: Simple Command with Project Context

```python
import typer
from tracertm.cli.storage_helper import (
    require_project,
    get_storage_manager,
    handle_storage_error,
)
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
@require_project()
@handle_storage_error
def list_epics():
    """List all epics in the current project."""
    storage = get_storage_manager()
    project = get_current_project()
    project_id, project_name = project

    # Get epics
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    epics = item_storage.list_items(item_type="epic")

    # Display
    table = format_items_table(epics, title=f"Epics - {project_name}")
    console.print(table)
```

---

### Pattern 2: Create Command with Auto-Sync

```python
import typer
from tracertm.cli.storage_helper import (
    require_project,
    get_storage_manager,
    get_current_project,
    with_sync,
    handle_storage_error,
)
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
@require_project()
@handle_storage_error
@with_sync(enabled=True)  # Auto-sync after creation
def create_epic(
    title: str = typer.Argument(...),
    description: str | None = typer.Option(None, "--description", "-d"),
):
    """Create a new epic."""
    storage = get_storage_manager()
    project = get_current_project()
    project_id, project_name = project

    # Create epic
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    epic = item_storage.create_item(
        title=title,
        item_type="epic",
        description=description,
        status="todo",
        priority="medium",
    )

    console.print(f"[green]✓[/green] Epic created: {epic.title}")
    console.print(f"[dim]ID: {epic.id}[/dim]")

    # Sync happens automatically via @with_sync decorator
```

---

### Pattern 3: Show Command with Rich Formatting

```python
import typer
from tracertm.cli.storage_helper import (
    require_project,
    get_storage_manager,
    format_item_for_display,
    handle_storage_error,
)
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

@app.command()
@require_project()
@handle_storage_error
def show_item(item_id: str = typer.Argument(...)):
    """Show detailed item information."""
    storage = get_storage_manager()
    project = get_current_project()
    project_id, project_name = project

    # Get item
    project_storage = storage.get_project_storage(project_name)
    proj = project_storage.get_project()
    item_storage = project_storage.get_item_storage(proj)

    item = item_storage.get_item(item_id)
    if not item:
        console.print(f"[red]✗[/red] Item not found: {item_id}")
        raise typer.Exit(code=1)

    # Display with rich formatting
    table = format_item_for_display(item)
    console.print(Panel(table, title=item.title, border_style="blue"))

    # Show description if present
    if item.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(item.description)
```

---

### Pattern 4: Sync Status Check

```python
import typer
from tracertm.cli.storage_helper import show_sync_status

app = typer.Typer()

@app.command("sync-status")
def check_sync_status():
    """Check current synchronization status."""
    show_sync_status()
```

---

## Configuration

The storage helper reads these configuration values:

### `storage_dir`
**Type:** string (path)
**Default:** `~/.tracertm`
**Purpose:** Base directory for local storage

**Set via:**
```bash
rtm config set storage_dir /custom/path
```

---

### `auto_sync`
**Type:** boolean
**Default:** `false`
**Purpose:** Enable/disable automatic sync after commands

**Set via:**
```bash
rtm config set auto_sync true
```

---

### `api_endpoint`
**Type:** string (URL)
**Default:** None
**Purpose:** Remote API endpoint for sync

**Set via:**
```bash
rtm config set api_endpoint https://api.tracertm.com
```

---

### `current_project_id` / `current_project_name`
**Type:** string
**Set by:** `rtm project switch` or `rtm project init`
**Purpose:** Current project context

---

## Testing

The storage helper includes a `reset_storage_manager()` function for testing:

```python
import pytest
from tracertm.cli.storage_helper import reset_storage_manager

@pytest.fixture(autouse=True)
def reset_storage():
    """Reset storage manager between tests."""
    yield
    reset_storage_manager()

def test_my_command():
    # Test code here
    # Storage manager is reset after this test
    pass
```

---

## Benefits Summary

### Code Reduction
- **Before:** Each command duplicates storage setup (10-20 lines)
- **After:** Single function call (`get_storage_manager()`)
- **Savings:** ~80% less boilerplate per command

### Consistency
- Uniform error messages
- Consistent Rich output formatting
- Standard project validation
- Predictable sync behavior

### Maintainability
- Single source of truth for storage logic
- Easy to add global features (logging, metrics, etc.)
- Centralized configuration management

### Performance
- Singleton pattern avoids multiple database connections
- Efficient resource usage
- Fast command execution

---

## Migration Guide

### Old Pattern (Before)
```python
@app.command()
def my_command():
    config_manager = ConfigManager()
    storage_dir = config_manager.get("storage_dir")
    if storage_dir:
        storage = LocalStorageManager(base_dir=Path(storage_dir))
    else:
        storage = LocalStorageManager()

    project_id = config_manager.get("current_project_id")
    if not project_id:
        console.print("[red]No project selected[/red]")
        raise typer.Exit(code=1)

    # ... actual logic
```

### New Pattern (After)
```python
from tracertm.cli.storage_helper import require_project, get_storage_manager

@app.command()
@require_project()
def my_command():
    storage = get_storage_manager()
    # ... actual logic
```

**Lines saved:** 8-10 per command
**Readability:** Much improved
**Maintainability:** Centralized

---

## Troubleshooting

### Issue: "No project selected" error

**Cause:** No current project set in config

**Solution:**
```bash
rtm project switch <project-name>
# or
rtm project init <project-name>
```

---

### Issue: Storage manager returns old data

**Cause:** Singleton caching

**Solution:** This is by design. Storage manager persists for CLI session lifetime. For testing, use `reset_storage_manager()`.

---

### Issue: Sync doesn't trigger

**Cause:** `auto_sync` not enabled

**Solution:**
```bash
rtm config set auto_sync true
```

---

### Issue: Can't find storage directory

**Cause:** Custom storage dir not configured correctly

**Solution:**
```bash
rtm config set storage_dir ~/.tracertm
# or verify current setting
rtm config get storage_dir
```

---

## Future Enhancements

Potential additions to the storage helper:

1. **Batch Operations**
   ```python
   def batch_create_items(items: list[dict]) -> list[Item]:
       # Optimized batch creation with single transaction
   ```

2. **Search Helpers**
   ```python
   def search_items(query: str, filters: dict) -> list[Item]:
       # Unified search across all item types
   ```

3. **Export Helpers**
   ```python
   def export_to_markdown(items: list[Item]) -> str:
       # Generate markdown report
   ```

4. **Metrics Collection**
   ```python
   def track_command_usage(command_name: str):
       # Anonymous usage metrics
   ```

---

## Related Documentation

- **Architecture:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md`
- **Storage Module:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/storage/`
- **Config Manager:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/config/manager.py`
- **CLI Commands:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/`
