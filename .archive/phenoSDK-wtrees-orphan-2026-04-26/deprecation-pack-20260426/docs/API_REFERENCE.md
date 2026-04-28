# PhenoSDK 2.0 API Reference

**Version**: 2.0.0
**Date**: 2025-10-13

---

## Table of Contents

1. [Dependency Injection](#dependency-injection)
2. [Configuration](#configuration)
3. [MCP (Model Context Protocol)](#mcp-model-context-protocol)
4. [Resource Schemes](#resource-schemes)
5. [Registry Pattern](#registry-pattern)
6. [Observability](#observability)

---

## Dependency Injection

### Container

**Module**: `pheno.adapters.container`

#### Container Class

```python
from pheno.adapters.container import Container, Lifecycle

container = Container()
```

**Methods**:

- `register(interface, implementation, lifecycle=Lifecycle.TRANSIENT)` - Register a service
- `resolve(interface)` - Resolve a service instance
- `has_service(interface)` - Check if service is registered
- `clear()` - Clear all registrations

**Lifecycles**:

- `Lifecycle.TRANSIENT` - New instance each time
- `Lifecycle.SINGLETON` - Single instance (default for most services)
- `Lifecycle.SCOPED` - Instance per scope (not yet implemented)

**Example**:

```python
from pheno.adapters.container import Container, Lifecycle

container = Container()

# Register with auto-wiring
container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)
container.register(UserService, UserService)  # Auto-wires IDatabase!

# Resolve
service = container.resolve(UserService)
```

#### Global Container

```python
from pheno.adapters.container import get_container, set_container

# Get global container
container = get_container()

# Set custom global container
set_container(my_container)
```

---

## Configuration

### Config

**Module**: `pheno.config`

#### Config Class

```python
from pheno.config import Config

config = Config.load(
    env_prefix="APP_",
    config_file="config.yaml",
    defaults={"debug": False}
)
```

**Methods**:

- `load(env_prefix, config_file, defaults)` - Load configuration
- `get(key, default=None)` - Get configuration value
- `set(key, value)` - Set configuration value
- `to_dict()` - Convert to dictionary

**Example**:

```python
from pheno.config import Config

# Load from multiple sources (env > file > defaults)
config = Config.load(
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

# Access values
debug = config.get("debug")
db_host = config.get("database.host")

# Set values
config.set("debug", True)
```

#### Built-in Config Classes

```python
from pheno.config import AppConfig, DatabaseConfig, RedisConfig

# Application config
app_config = AppConfig.load(env_prefix="APP_")

# Database config
db_config = DatabaseConfig.load(env_prefix="DB_")

# Redis config
redis_config = RedisConfig.load(env_prefix="REDIS_")
```

---

## MCP (Model Context Protocol)

### Setup

**Module**: `pheno.mcp`

#### setup_mcp()

```python
from pheno.mcp import setup_mcp

manager = setup_mcp(
    container=None,  # Optional DI container
    with_monitoring=True,  # Enable monitoring
    with_default_schemes=True,  # config://, memory://
    with_extended_schemes=False  # env://, file://, http://, logs://, metrics://
)
```

#### setup_mcp_with_config()

```python
from pheno.mcp import setup_mcp_with_config

config = {
    "app": {"name": "myapp", "debug": True},
    "database": {"host": "localhost", "port": 5432}
}

manager = setup_mcp_with_config(config)

# Access via config:// scheme
db_config = await manager.get_resource("config://database")
```

### McpManager

**Module**: `pheno.mcp`

#### Connection Management

```python
from pheno.mcp import McpManager, McpServer

manager = McpManager()

# Connect to server
server = McpServer(url="http://localhost:8000", name="my-server")
session = await manager.connect(server)

# Disconnect
await manager.disconnect(session)
```

#### Tool Management

```python
from pheno.mcp import McpTool

# Register tool
def search_handler(query: str) -> dict:
    return {"results": [f"Found: {query}"]}

tool = McpTool(
    name="search",
    description="Search documentation",
    parameters={"query": {"type": "string", "required": True}}
)

manager.register_tool(tool, handler=search_handler)

# Execute tool
result = await manager.execute_tool("search", {"query": "hello"})
print(result.output)  # {"results": ["Found: hello"]}

# List tools
tools = manager.list_tools()
```

#### Resource Access

```python
# Get resource
config = await manager.get_resource("config://app/database")

# List resources
uris = await manager.list_resources("config://app/*")

# Register custom scheme
manager.register_resource_scheme("db", DbSchemeHandler())
```

### Domain Types

**Module**: `pheno.mcp.types`

#### McpServer

```python
from pheno.mcp import McpServer

server = McpServer(
    url="http://localhost:8000",
    name="my-server",
    auth_token="secret",
    timeout=30,
    metadata={"env": "prod"}
)
```

#### McpSession

```python
from pheno.mcp import McpSession, SessionStatus

session = McpSession(
    session_id="session-123",
    server=server,
    status=SessionStatus.CONNECTED
)

# Check if active
if session.is_active():
    print("Session is active")
```

#### McpTool

```python
from pheno.mcp import McpTool

tool = McpTool(
    name="search",
    description="Search documentation",
    parameters={"query": {"type": "string"}},
    category="search",
    tags=["docs", "search"],
    version="1.0.0"
)
```

#### ToolResult

```python
from pheno.mcp import ToolResult

result = ToolResult(
    output={"results": [...]},
    success=True,
    metadata={"execution_time": 1.23}
)

if result.is_success():
    print(result.output)
```

---

## Resource Schemes

### Available Schemes

| Scheme | Purpose | Module |
|--------|---------|--------|
| `config://` | Configuration access | `pheno.mcp.adapters.resource_provider` |
| `memory://` | In-memory storage | `pheno.mcp.adapters.resource_provider` |
| `env://` | Environment variables | `pheno.mcp.schemes.env_scheme` |
| `file://` | File system | `pheno.mcp.schemes.file_scheme` |
| `http://` | HTTP resources | `pheno.mcp.schemes.http_scheme` |
| `logs://` | Application logs | `pheno.mcp.schemes.logs_scheme` |
| `metrics://` | Metrics | `pheno.mcp.schemes.metrics_scheme` |

### config://

```python
# Access configuration
app_name = await manager.get_resource("config://app/name")
db_config = await manager.get_resource("config://database")

# List config keys
keys = await manager.list_resources("config://app/*")
```

### memory://

```python
# Store value
from pheno.ports.mcp import ResourceProvider
provider = manager.container.resolve(ResourceProvider)
handler = provider.get_scheme_handler("memory")
await handler.set("memory://cache/user-123", {"name": "Alice"})

# Retrieve value
user = await manager.get_resource("memory://cache/user-123")

# List keys
keys = await manager.list_resources("memory://cache/*")
```

### env://

```python
# Get environment variable
path = await manager.get_resource("env://PATH")

# List variables with prefix
app_vars = await manager.list_resources("env://APP_*")
```

### file://

```python
# Read JSON file (auto-parsed)
config = await manager.get_resource("file://./config.json")

# Read YAML file (auto-parsed)
data = await manager.get_resource("file://./data.yaml")

# Read text file
content = await manager.get_resource("file://./README.md")

# List files
json_files = await manager.list_resources("file://*.json")
```

### http://

```python
# Fetch JSON API
users = await manager.get_resource("https://api.example.com/users")

# With custom headers
from pheno.mcp.schemes import HttpSchemeHandler
handler = HttpSchemeHandler(headers={"Authorization": "Bearer token"})
manager.register_resource_scheme("https", handler)
```

### logs://

```python
# Get logs handler
from pheno.ports.mcp import ResourceProvider
provider = manager.container.resolve(ResourceProvider)
handler = provider.get_scheme_handler("logs")

# Add logs
handler.add_log("INFO", "User logged in", user_id="123")
handler.add_log("ERROR", "Database error", error=str(e))

# Query logs
all_logs = await manager.get_resource("logs://app/all")
errors = await manager.get_resource("logs://app/errors")
recent = await manager.get_resource("logs://app/all?limit=50")
since = await manager.get_resource("logs://app/all?since=2024-01-01")
```

### metrics://

```python
# Get metrics handler
from pheno.ports.mcp import ResourceProvider
provider = manager.container.resolve(ResourceProvider)
handler = provider.get_scheme_handler("metrics")

# Record metrics
handler.record_counter("http_requests_total", 1, status="200")
handler.record_gauge("memory_usage_bytes", 1024000)
handler.record_histogram("response_time_seconds", 0.123)

# Query metrics
all_metrics = await manager.get_resource("metrics://all")
counters = await manager.get_resource("metrics://counters/http_requests_total")
gauges = await manager.get_resource("metrics://gauges/memory_usage_bytes")
```

---

## Registry Pattern

### BaseRegistry

**Module**: `pheno.adapters.base_registry`

```python
from pheno.adapters.base_registry import BaseRegistry

class MyRegistry(BaseRegistry[MyType]):
    pass

registry = MyRegistry()
```

**Methods**:

- `register(name, item, **metadata)` - Register item
- `unregister(name)` - Unregister item
- `get(name)` - Get item by name
- `has(name)` - Check if item exists
- `list(**filters)` - List all items
- `list_names()` - List item names
- `clear()` - Clear all items
- `count()` - Get item count

**Search Methods**:

- `search(query)` - Search items
- `filter(**criteria)` - Filter by criteria

**Category Methods**:

- `list_by_category(category)` - List items in category
- `list_categories()` - List all categories
- `get_category(name)` - Get item category

**Metadata Methods**:

- `set_metadata(name, metadata)` - Set metadata
- `get_metadata(name)` - Get metadata
- `update_metadata(name, updates)` - Update metadata

**Observable Methods**:

- `on_register(callback)` - Register callback
- `on_unregister(callback)` - Unregister callback

**Example**:

```python
from pheno.adapters.base_registry import BaseRegistry
from pheno.mcp.types import McpTool

class ToolRegistry(BaseRegistry[McpTool]):
    pass

registry = ToolRegistry()

# Register with metadata
registry.register(
    "search",
    search_tool,
    category="data",
    version="1.0"
)

# Search
tools = registry.search("database")

# Filter
data_tools = registry.filter(category="data")

# Callbacks
registry.on_register(lambda name, tool: print(f"Registered: {name}"))
```

---

## Observability

### Ports

**Module**: `pheno.ports.observability`

All observability functionality is defined via protocols. Implementations can be plugged in via DI container.

#### Logger

```python
from pheno.ports.observability import Logger

logger: Logger = container.resolve(Logger)

logger.debug("Debug message", request_id="abc123")
logger.info("User logged in", user_id="123")
logger.warning("Rate limit approaching", current=95)
logger.error("Database error", error=str(e))
logger.critical("System shutdown", reason="out of memory")
```

#### Tracer

```python
from pheno.ports.observability import Tracer

tracer: Tracer = container.resolve(Tracer)

span = tracer.start_span("process_request", user_id="123")
span.set_attribute("method", "POST")
span.add_event("cache_miss", key="user:123")
span.end()
```

#### Meter

```python
from pheno.ports.observability import Meter

meter: Meter = container.resolve(Meter)

counter = meter.create_counter("http_requests_total")
counter.add(1, endpoint="/api/users", status="200")

gauge = meter.create_gauge("memory_usage_bytes")
gauge.set(1024000)

histogram = meter.create_histogram("response_time_seconds")
histogram.record(0.123, method="GET")
```

#### HealthChecker

```python
from pheno.ports.observability import HealthChecker

health: HealthChecker = container.resolve(HealthChecker)

# Add health check
health.add_check(database_health_check)

# Check health
status = health.check_all()
# {"status": "healthy", "checks": {...}}
```

---

## Quick Start

### Basic Setup

```python
from pheno.mcp import setup_mcp, McpServer, McpTool

# Setup MCP
manager = setup_mcp(with_extended_schemes=True)

# Connect to server
server = McpServer(url="http://localhost:8000")
session = await manager.connect(server)

# Register tool
def search(query: str) -> dict:
    return {"results": [f"Found: {query}"]}

tool = McpTool(name="search", description="Search docs")
manager.register_tool(tool, handler=search)

# Execute tool
result = await manager.execute_tool("search", {"query": "hello"})

# Access resources
config = await manager.get_resource("config://app/database")
env_var = await manager.get_resource("env://PATH")
```

### With Configuration

```python
from pheno.config import AppConfig
from pheno.mcp import setup_mcp_with_config

# Load config
config = AppConfig.load(env_prefix="APP_", config_file="config.yaml")

# Setup MCP with config
manager = setup_mcp_with_config(config.to_dict())

# Access via config:// scheme
db_host = await manager.get_resource("config://database/host")
```

### With DI Container

```python
from pheno.adapters.container import Container, Lifecycle
from pheno.mcp import setup_mcp

# Create container
container = Container()

# Register services
container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)

# Setup MCP with container
manager = setup_mcp(container=container)

# Services are available
db = container.resolve(IDatabase)
```

---

## See Also

- [Migration Guide](MIGRATION_GUIDE.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Examples](../examples/)
- [GitHub Repository](https://github.com/KooshaPari/phenoSDK)
