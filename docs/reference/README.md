# Auto-Generated Python API Clients

This directory contains Python API clients auto-generated from OpenAPI specifications.

## Directories

- `python_api_client/` - Client for Python FastAPI backend
- `go_api_client/` - Client for Go Echo backend

## Generation

```bash
# From project root
bun run generate:client

# Or with full pipeline
bun run generate:all
```

## Usage Examples

### Basic Usage

```python
from tracertm.generated import PythonAPIClient

# Create client
client = PythonAPIClient(base_url="http://localhost:4000")

# Make type-safe API calls
async with client as api:
    # Get item
    response = await api.items.get_item(item_id="123")
    print(response.parsed)

    # Create item
    new_item = await api.items.create_item(
        body={"title": "New Item", "description": "Test"}
    )
    print(new_item.parsed)
```

### Synchronous Client

```python
from tracertm.generated.python_api_client import Client
from tracertm.generated.python_api_client.api.items import get_item

# Create client
client = Client(base_url="http://localhost:4000")

# Make requests
item = get_item.sync(client=client, id="123")
print(item)
```

### Error Handling

```python
from tracertm.generated import PythonAPIClient
from tracertm.generated.python_api_client.errors import UnexpectedStatus

async with PythonAPIClient(base_url="http://localhost:4000") as client:
    try:
        response = await client.items.get_item(item_id="123")
        print(response.parsed)
    except UnexpectedStatus as e:
        print(f"Error {e.status_code}: {e.content}")
```

### CLI Integration

```python
# src/tracertm/cli/commands/items.py
import asyncio
import typer
from tracertm.generated import PythonAPIClient
from tracertm.config.manager import ConfigManager

app = typer.Typer()
config = ConfigManager()

@app.command()
def get(item_id: str):
    """Get an item by ID."""
    async def _get():
        async with PythonAPIClient(base_url=config.api_url) as client:
            response = await client.items.get_item(item_id=item_id)
            return response.parsed

    item = asyncio.run(_get())
    typer.echo(f"Item: {item.title}")

@app.command()
def list():
    """List all items."""
    async def _list():
        async with PythonAPIClient(base_url=config.api_url) as client:
            response = await client.items.list_items()
            return response.parsed

    items = asyncio.run(_list())
    for item in items:
        typer.echo(f"- {item.id}: {item.title}")
```

### Configuration

```python
from tracertm.generated import PythonAPIClient

# Custom configuration
client = PythonAPIClient(
    base_url="http://localhost:4000",
    timeout=30.0,
    verify_ssl=True,
    follow_redirects=True,
)

# Custom headers
client = PythonAPIClient(
    base_url="http://localhost:4000",
    headers={"Authorization": "Bearer token123"}
)
```

## Structure

Each generated client contains:

```
python_api_client/
├── __init__.py           # Client exports
├── client.py             # Main client class
├── errors.py             # Error types
├── types.py              # Type definitions
├── api/                  # API endpoint modules
│   ├── items/
│   ├── projects/
│   └── ...
└── models/               # Request/response models
    ├── item.py
    ├── project.py
    └── ...
```

## Notes

- These clients are auto-generated - **do not edit manually**
- Regenerate after any API changes
- Fully type-hinted with mypy support
- Async by default, sync methods available
- See [API Contract Generation Guide](../../../../docs/guides/API_CONTRACT_GENERATION.md) for details

## Dependencies

The generated clients require:
- `httpx` - HTTP client
- `attrs` - Data classes
- `python-dateutil` - Date parsing

These are included in the `full` extras of the main package.
