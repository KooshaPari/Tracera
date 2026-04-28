# Getting Started with PhenoSDK 2.0

**Version**: 2.0.0
**Date**: 2025-10-13

---

## Installation

```bash
pip install pheno-sdk
```

Or install from source:

```bash
git clone https://github.com/KooshaPari/phenoSDK.git
cd phenoSDK
pip install -e .
```

---

## Quick Start

### 1. Basic MCP Setup

```python
from pheno.mcp import setup_mcp, McpServer, McpTool

# Setup MCP with all features
manager = setup_mcp(
    with_monitoring=True,
    with_extended_schemes=True
)

# Connect to MCP server
server = McpServer(url="http://localhost:8000", name="my-server")
session = await manager.connect(server)

# Register a tool
def search_docs(query: str) -> dict:
    """Search documentation."""
    return {"results": [f"Found: {query}"]}

tool = McpTool(
    name="search",
    description="Search documentation",
    parameters={"query": {"type": "string", "required": True}}
)

manager.register_tool(tool, handler=search_docs)

# Execute tool
result = await manager.execute_tool("search", {"query": "hello world"})
print(result.output)
# {"results": ["Found: hello world"]}
```

### 2. Configuration

```python
from pheno.config import AppConfig

# Load configuration from multiple sources
config = AppConfig.load(
    env_prefix="APP_",
    config_file="config.yaml",
    defaults={
        "debug": False,
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }
)

# Access configuration
if config.debug:
    print(f"Running in debug mode")

db_host = config.get("database.host")
db_port = config.get("database.port")
```

### 3. Resource Access

```python
from pheno.mcp import setup_mcp

manager = setup_mcp(with_extended_schemes=True)

# Environment variables
path = await manager.get_resource("env://PATH")
app_name = await manager.get_resource("env://APP_NAME")

# Configuration files
config = await manager.get_resource("file://./config.json")
data = await manager.get_resource("file://./data.yaml")

# HTTP APIs
users = await manager.get_resource("https://api.example.com/users")

# Application logs
errors = await manager.get_resource("logs://app/errors?limit=100")
recent_logs = await manager.get_resource("logs://app/all?limit=50")

# Metrics
all_metrics = await manager.get_resource("metrics://all")
counters = await manager.get_resource("metrics://counters/http_requests_total")
```

---

## Common Use Cases

### CLI Utilities

The unified `pheno` CLI ships with several infrastructure helpers:

- `./pheno schema check` – compare the local Supabase schema snapshot with the live database (requires Supabase credentials in the environment).
- `./pheno schema update` – refresh the local snapshot after applying migrations.
- `./pheno deploy --target vercel` – run deployment readiness checks (ensures `vercel.json`, build scripts, and git status are in good shape).
- `./pheno embeddings --entity-types document requirement` – backfill embeddings through the progressive embedding service (requires Supabase + Vertex AI).

Run `./pheno schema --help`, `./pheno deploy --help`, or `./pheno embeddings --help` for detailed usage.

### Use Case 1: Building an MCP Tool

```python
from pheno.mcp import setup_mcp, McpTool
import asyncio

async def main():
    # Setup
    manager = setup_mcp(with_monitoring=True)

    # Define tool handler
    async def analyze_data(data: list, operation: str) -> dict:
        """Analyze data with specified operation."""
        if operation == "sum":
            result = sum(data)
        elif operation == "avg":
            result = sum(data) / len(data)
        elif operation == "max":
            result = max(data)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return {
            "operation": operation,
            "result": result,
            "count": len(data)
        }

    # Register tool
    tool = McpTool(
        name="analyze",
        description="Analyze numerical data",
        parameters={
            "data": {"type": "array", "required": True},
            "operation": {"type": "string", "required": True}
        },
        category="analytics"
    )

    manager.register_tool(tool, handler=analyze_data)

    # Execute
    result = await manager.execute_tool(
        "analyze",
        {"data": [1, 2, 3, 4, 5], "operation": "avg"}
    )

    print(result.output)
    # {"operation": "avg", "result": 3.0, "count": 5}

if __name__ == "__main__":
    asyncio.run(main())
```

### Use Case 2: Configuration Management

```python
from pheno.config import Config
from pheno.mcp import setup_mcp_with_config

# Load configuration
config = Config.load(
    env_prefix="APP_",
    config_file="config.yaml",
    defaults={
        "app": {
            "name": "MyApp",
            "debug": False
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "mydb"
        },
        "redis": {
            "host": "localhost",
            "port": 6379
        }
    }
)

# Setup MCP with config
manager = setup_mcp_with_config(config.to_dict())

# Access config via URI
async def get_db_config():
    db_config = await manager.get_resource("config://database")
    print(f"Connecting to {db_config['host']}:{db_config['port']}")
    return db_config

# Use in application
db_config = asyncio.run(get_db_config())
```

### Use Case 3: Logging and Metrics

```python
from pheno.mcp import setup_mcp
from pheno.ports.mcp import ResourceProvider

async def main():
    manager = setup_mcp(with_extended_schemes=True)

    # Get handlers
    provider = manager.container.resolve(ResourceProvider)
    logs_handler = provider.get_scheme_handler("logs")
    metrics_handler = provider.get_scheme_handler("metrics")

    # Add logs
    logs_handler.add_log("INFO", "Application started", version="2.0")
    logs_handler.add_log("INFO", "User logged in", user_id="123")
    logs_handler.add_log("ERROR", "Database connection failed", error="timeout")

    # Record metrics
    metrics_handler.record_counter("http_requests_total", 1, status="200", method="GET")
    metrics_handler.record_counter("http_requests_total", 1, status="404", method="GET")
    metrics_handler.record_gauge("active_connections", 42)
    metrics_handler.record_histogram("request_duration_seconds", 0.123, endpoint="/api/users")

    # Query logs
    all_logs = await manager.get_resource("logs://app/all")
    errors = await manager.get_resource("logs://app/errors")

    print(f"Total logs: {len(all_logs)}")
    print(f"Errors: {len(errors)}")

    # Query metrics
    all_metrics = await manager.get_resource("metrics://all")
    print(f"Counters: {len(all_metrics['counters'])}")
    print(f"Gauges: {len(all_metrics['gauges'])}")
    print(f"Histograms: {len(all_metrics['histograms'])}")

asyncio.run(main())
```

### Use Case 4: Custom Registry

```python
from pheno.adapters.base_registry import BaseRegistry
from dataclasses import dataclass

@dataclass
class Plugin:
    name: str
    version: str
    enabled: bool = True

class PluginRegistry(BaseRegistry[Plugin]):
    def enable_plugin(self, name: str):
        """Enable a plugin."""
        plugin = self.get(name)
        plugin.enabled = True
        self.update_metadata(name, {"enabled": True})

    def disable_plugin(self, name: str):
        """Disable a plugin."""
        plugin = self.get(name)
        plugin.enabled = False
        self.update_metadata(name, {"enabled": False})

    def list_enabled(self):
        """List enabled plugins."""
        return [p for p in self.list() if p.enabled]

# Usage
registry = PluginRegistry()

# Register plugins
registry.register(
    "auth",
    Plugin(name="auth", version="1.0"),
    category="security",
    author="alice"
)

registry.register(
    "cache",
    Plugin(name="cache", version="2.0"),
    category="performance",
    author="bob"
)

# Use registry features
security_plugins = registry.list_by_category("security")
enabled_plugins = registry.list_enabled()
plugins = registry.search("cache")

# Callbacks
registry.on_register(lambda name, plugin: print(f"Registered: {name} v{plugin.version}"))
```

### Use Case 5: Dependency Injection

```python
from pheno.adapters.container import Container, Lifecycle
from typing import Protocol

# Define interfaces
class IDatabase(Protocol):
    def query(self, sql: str) -> list: ...

class ICache(Protocol):
    def get(self, key: str) -> any: ...
    def set(self, key: str, value: any) -> None: ...

# Implementations
class PostgresDatabase:
    def query(self, sql: str) -> list:
        # Implementation
        return []

class RedisCache:
    def get(self, key: str) -> any:
        # Implementation
        return None

    def set(self, key: str, value: any) -> None:
        # Implementation
        pass

# Service with dependencies
class UserService:
    def __init__(self, db: IDatabase, cache: ICache):
        self.db = db
        self.cache = cache

    def get_user(self, user_id: str):
        # Try cache first
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return cached

        # Query database
        users = self.db.query(f"SELECT * FROM users WHERE id = '{user_id}'")
        if users:
            user = users[0]
            self.cache.set(f"user:{user_id}", user)
            return user

        return None

# Setup DI container
container = Container()
container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)
container.register(ICache, RedisCache, Lifecycle.SINGLETON)
container.register(UserService, UserService)  # Auto-wires dependencies!

# Use
service = container.resolve(UserService)
user = service.get_user("123")
```

---

## Next Steps

### Learn More

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Architecture Guide](ARCHITECTURE.md) - Understand the architecture
- [Migration Guide](MIGRATION_GUIDE.md) - Migrate from 1.x to 2.0

### Examples

Check out the [examples/](../examples/) directory for more examples:

- `examples/basic_mcp.py` - Basic MCP usage
- `examples/resource_schemes.py` - Using resource schemes
- `examples/custom_registry.py` - Creating custom registries
- `examples/dependency_injection.py` - DI patterns
- `examples/observability.py` - Logging and metrics

### Community

- **GitHub**: [github.com/KooshaPari/phenoSDK](https://github.com/KooshaPari/phenoSDK)
- **Issues**: [Report bugs or request features](https://github.com/KooshaPari/phenoSDK/issues)
- **Discussions**: [Ask questions](https://github.com/KooshaPari/phenoSDK/discussions)

---

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'pheno'`

**Solution**: Make sure phenoSDK is installed:
```bash
pip install pheno-sdk
```

**Issue**: `RuntimeError: McpProvider not registered`

**Solution**: Call `setup_mcp()` before using the manager:
```python
from pheno.mcp import setup_mcp
manager = setup_mcp()
```

**Issue**: `ValueError: Unsupported scheme: env://`

**Solution**: Enable extended schemes:
```python
manager = setup_mcp(with_extended_schemes=True)
```

**Issue**: `KeyError: Item not found: my_tool`

**Solution**: Register the tool before executing:
```python
manager.register_tool(tool, handler=my_handler)
```

---

## Tips and Best Practices

### 1. Use Setup Functions

```python
# Good - uses setup function
manager = setup_mcp(with_extended_schemes=True)

# Bad - manual setup
from pheno.adapters.container import Container
from pheno.ports.mcp import McpProvider
# ... lots of manual registration
```

### 2. Enable Monitoring

```python
# Good - automatic monitoring
manager = setup_mcp(with_monitoring=True)
result = await manager.execute_tool("search", {"query": "hello"})
# Automatically tracked in metrics

# Bad - no monitoring
manager = setup_mcp(with_monitoring=False)
# No automatic tracking
```

### 3. Use URI-Based Access

```python
# Good - URI-based
config = await manager.get_resource("file://./config.json")

# Bad - direct file access
import json
with open("config.json") as f:
    config = json.load(f)
```

### 4. Leverage Auto-Wiring

```python
# Good - auto-wiring
container.register(UserService, UserService)

# Bad - manual wiring
container.register(UserService, lambda: UserService(db, cache))
```

---

## See Also

- [API Reference](API_REFERENCE.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Examples](../examples/)
