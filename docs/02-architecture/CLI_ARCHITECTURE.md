# TraceRTM CLI Architecture

**Version**: 1.0  
**Last Updated**: 2025-01-27

---

## 📖 Overview

TraceRTM CLI is built on **Typer** (FastAPI's CLI framework) with **Rich** for beautiful terminal output. The architecture follows a modular command group pattern, making it easy to extend and maintain.

---

## 🏗️ Architecture Layers

### Layer 1: Entry Point

**File**: `src/tracertm/cli/app.py`

The main entry point that:
- Initializes the Typer app
- Registers all command groups
- Handles global options (--version, --debug)
- Sets up Rich console

```python
app = typer.Typer(
    name="rtm",
    help="TraceRTM - Agent-native, multi-view requirements traceability system",
    add_completion=True,
    rich_markup_mode="rich",
)
```

### Layer 2: Command Groups

**Location**: `src/tracertm/cli/commands/`

Each command group is a separate Typer app:

- `config.py` - Configuration management
- `project.py` - Project management
- `item.py` - Item CRUD operations
- `link.py` - Link management
- `view.py` - View switching
- `db.py` - Database operations
- `backup.py` - Backup/restore
- `state.py` - Project state dashboard
- `search.py` - Cross-view search
- `drill.py` - Drill-down navigation
- `ingest.py` - Stateless ingestion (MD/MDX/YAML)
- `export.py` - Data export
- `history.py` - Item history
- `benchmark.py` - Performance benchmarking
- `droid.py` - Droid agent integration
- `cursor.py` - Cursor agent integration

### Layer 3: Services

**Location**: `src/tracertm/services/`

Business logic is separated into services:

- `item_service.py` - Item operations
- `link_service.py` - Link operations
- `view_registry_service.py` - View management
- `stateless_ingestion_service.py` - File ingestion
- `chaos_mode_service.py` - Chaos mode operations
- `benchmark_service.py` - Performance benchmarking

### Layer 4: Data Layer

**Location**: `src/tracertm/`

- `models/` - SQLAlchemy models
- `repositories/` - Data access layer
- `database/` - Database connection management
- `config/` - Configuration management

---

## 🔧 Command Structure

### Standard Command Pattern

```python
import typer
from rich.console import Console

app = typer.Typer(help="Command group description")
console = Console()

@app.command()
def command_name(
    arg: str = typer.Argument(..., help="Argument description"),
    option: str = typer.Option(None, "--option", "-o", help="Option description"),
) -> None:
    """
    Command description.
    
    Example:
        rtm command-name arg --option value
    """
    try:
        # 1. Load configuration
        config_manager = ConfigManager()
        
        # 2. Connect to database
        db = DatabaseConnection(database_url)
        db.connect()
        
        # 3. Execute business logic
        with Session(db.engine) as session:
            # ... operations ...
            session.commit()
        
        # 4. Display results
        console.print("[green]✓[/green] Success message")
        
    except TraceRTMError as e:
        e.display()
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(code=1)
```

### Error Handling Pattern

**File**: `src/tracertm/cli/errors.py`

Custom exceptions with Rich display:

```python
class TraceRTMError(Exception):
    def display(self) -> None:
        console.print(f"[red]✗[/red] {self.message}")
        if self.suggestion:
            console.print(f"[yellow]💡[/yellow] {self.suggestion}")
```

---

## 🎨 Rich Integration

### Tables

```python
from rich.table import Table

table = Table(title="Items")
table.add_column("ID", style="cyan")
table.add_column("Title", style="green")
table.add_column("Status", style="yellow")

for item in items:
    table.add_row(str(item.id), item.title, item.status)

console.print(table)
```

### Progress Bars

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console,
) as progress:
    task = progress.add_task("Processing...", total=None)
    # ... work ...
```

### Trees

```python
from rich.tree import Tree

tree = Tree("Root")
child = tree.add("Child")
console.print(tree)
```

### Panels

```python
from rich.panel import Panel

panel = Panel("Content", title="Title", border_style="green")
console.print(panel)
```

---

## 🔌 Extension Points

### Adding a New Command Group

1. **Create command file**: `src/tracertm/cli/commands/new_group.py`

```python
import typer
from rich.console import Console

app = typer.Typer(help="New command group")
console = Console()

@app.command()
def command() -> None:
    """Command description."""
    console.print("Hello from new command!")
```

2. **Register in app.py**:

```python
from tracertm.cli.commands import new_group

app.add_typer(new_group.app, name="new-group", help="New command group")
```

3. **Add to `__init__.py`**: `src/tracertm/cli/commands/__init__.py`

```python
from . import new_group
```

### Adding a New Command to Existing Group

Simply add a new `@app.command()` function to the existing command file.

---

## 📊 Data Flow

### Command Execution Flow

```
User Input
    ↓
Typer CLI (app.py)
    ↓
Command Group (commands/*.py)
    ↓
Service Layer (services/*.py)
    ↓
Repository Layer (repositories/*.py)
    ↓
Database (SQLAlchemy)
    ↓
Response
    ↓
Rich Display (Console)
```

### Example: Item Creation Flow

```
rtm item create "Title" --view FEATURE
    ↓
item.py::create_item()
    ↓
ConfigManager.get("current_project_id")
    ↓
DatabaseConnection.connect()
    ↓
ItemService.create_item()
    ↓
ItemRepository.create()
    ↓
Session.commit()
    ↓
Rich table display
```

---

## 🧪 Testing Architecture

### Test Structure

```
tests/
├── unit/
│   └── cli/
│       ├── test_item_commands.py
│       ├── test_project_commands.py
│       └── ...
├── integration/
│   └── test_cli_workflows.py
└── e2e/
    └── test_cli_journeys.py
```

### Testing Pattern

```python
from typer.testing import CliRunner
from unittest.mock import patch

runner = CliRunner()

@patch("tracertm.cli.commands.item.ConfigManager")
def test_command(mock_config):
    result = runner.invoke(app, ["command", "args"])
    assert result.exit_code == 0
```

---

## 🔐 Configuration Management

### ConfigManager

**File**: `src/tracertm/config/manager.py`

- Loads config from `~/.tracertm/config.json`
- Manages current project ID
- Stores database URL
- Provides typed access to config values

### Config Structure

```json
{
  "database_url": "sqlite:///tracertm.db",
  "current_project_id": "proj-123",
  "default_view": "FEATURE"
}
```

---

## 🗄️ Database Connection

### DatabaseConnection

**File**: `src/tracertm/database/connection.py`

- Manages SQLAlchemy engine
- Handles connection pooling
- Provides health checks
- Supports SQLite and PostgreSQL

### Connection Pattern

```python
db = DatabaseConnection(database_url)
db.connect()

with Session(db.engine) as session:
    # ... operations ...
    session.commit()

db.close()
```

---

## 🎯 Command Registration

### Registration Order

Commands are registered in `app.py` in logical groups:

1. **Core**: config, project, db
2. **Data**: item, link, view
3. **Operations**: backup, ingest, export
4. **Navigation**: state, search, drill
5. **Advanced**: benchmark, history
6. **Agents**: droid, cursor

### Command Naming

- Use kebab-case for command names: `bulk-update`
- Use snake_case for function names: `bulk_update_items`
- Use descriptive help text

---

## 🚀 Performance Considerations

### Async Operations

Some commands use async for better performance:

- `benchmark.py` - Uses async SQLAlchemy
- `ingest.py` - Can process large files asynchronously

### Caching

- View registry is cached
- Config is loaded once per command
- Database connections are pooled

### Optimization

- Limit query results with `--limit`
- Use indexes on frequently queried fields
- Batch operations for bulk updates

---

## 🔍 Debugging

### Debug Mode

Enable with `--debug` flag:

```bash
rtm --debug item list
```

This enables:
- Full stack traces
- SQL query logging
- Detailed error messages

### Logging

Logging is configured in `app.py`:

```python
if debug:
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Related Documentation

- **CLI User Guide**: `docs/04-guides/CLI_USER_GUIDE.md`
- **CLI API Reference**: `docs/06-api-reference/CLI_API_REFERENCE.md`
- **CLI Tutorial**: `docs/01-getting-started/CLI_TUTORIAL.md`
- **CLI Examples**: `docs/04-guides/CLI_EXAMPLES.md`

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
