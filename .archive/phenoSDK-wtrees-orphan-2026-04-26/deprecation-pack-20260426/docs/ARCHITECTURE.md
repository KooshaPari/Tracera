# PhenoSDK 2.0 Architecture

**Version**: 2.0.0
**Date**: 2025-10-13

---

## Overview

phenoSDK 2.0 is built on **hexagonal architecture** (ports and adapters pattern), providing clean separation of concerns and maximum flexibility.

### Core Principles

1. **Domain Independence** - Core domain has zero framework dependencies
2. **Protocol-Based** - All boundaries defined by protocols
3. **Dependency Injection** - All dependencies injected via DI container
4. **URI-Based Access** - Unified resource access via URIs
5. **Type Safety** - 100% type hints and protocol compliance

---

## Hexagonal Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│         (Your application code using phenoSDK)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Layer                             │
│  - InMemory* adapters (MCP, Resource, Tool, Session, etc.)  │
│  - BaseRegistry implementation                               │
│  - 7 resource scheme handlers                                │
│  - Observability implementations (pluggable)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Ports Layer                               │
│  - MCP ports (5 protocols)                                   │
│  - Observability ports (Logger, Tracer, Meter, etc.)        │
│  - Registry ports (5 protocols)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│  - Core types (MCP, Config, etc.)                           │
│  - Managers (McpManager, ConfigManager)                     │
│  - Business logic                                            │
│  - Zero framework dependencies                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Domain Layer

**Location**: `src/pheno/mcp/types.py`, `src/pheno/mcp/manager.py`, `src/pheno/config/core.py`

**Responsibilities**:
- Define core domain types
- Implement business logic
- Coordinate between ports
- No framework dependencies

**Examples**:
- `McpServer`, `McpSession`, `McpTool` - MCP domain types
- `McpManager` - Coordinates MCP operations
- `Config` - Configuration management

**Key Principle**: Domain depends on ports (protocols), not on adapters (implementations).

### Ports Layer

**Location**: `src/pheno/ports/`

**Responsibilities**:
- Define protocol interfaces
- Specify contracts for adapters
- Enable dependency inversion

**Examples**:
- `McpProvider` - MCP server connection protocol
- `ResourceProvider` - Resource access protocol
- `Logger`, `Tracer`, `Meter` - Observability protocols
- `Registry[T]` - Generic registry protocol

**Key Principle**: Ports are protocols (interfaces), not implementations.

### Adapter Layer

**Location**: `src/pheno/mcp/adapters/`, `src/pheno/adapters/`, `src/pheno/mcp/schemes/`

**Responsibilities**:
- Implement port protocols
- Handle external integrations
- Provide concrete functionality

**Examples**:
- `InMemoryMcpProvider` - In-memory MCP implementation
- `ConfigSchemeHandler` - config:// scheme handler
- `EnvSchemeHandler` - env:// scheme handler
- `BaseRegistry` - Generic registry implementation

**Key Principle**: Adapters implement ports and can be swapped without changing domain.

### Application Layer

**Location**: Your application code

**Responsibilities**:
- Use phenoSDK APIs
- Configure adapters
- Implement business logic

**Examples**:
```python
from pheno.mcp import setup_mcp

manager = setup_mcp(with_extended_schemes=True)
result = await manager.execute_tool("search", {"query": "hello"})
```

---

## Dependency Flow

```
Application
    ↓ uses
Domain (Manager, Types)
    ↓ depends on
Ports (Protocols)
    ↑ implemented by
Adapters (Implementations)
```

**Key**: Dependencies point inward. Domain never depends on adapters.

---

## Module Structure

```
src/pheno/
├── adapters/           # Adapter implementations
│   ├── container.py    # DI container
│   ├── base_registry.py # Base registry
│   └── registry.py     # Legacy registry
│
├── config/             # Configuration
│   └── core.py         # Config implementation
│
├── mcp/                # MCP (Model Context Protocol)
│   ├── types.py        # Domain types
│   ├── manager.py      # MCP manager
│   ├── setup.py        # Setup utilities
│   │
│   ├── adapters/       # MCP adapters
│   │   ├── provider.py
│   │   ├── resource_provider.py
│   │   ├── tool_registry.py
│   │   ├── session_manager.py
│   │   └── monitoring.py
│   │
│   └── schemes/        # Resource scheme handlers
│       ├── env_scheme.py
│       ├── file_scheme.py
│       ├── http_scheme.py
│       ├── logs_scheme.py
│       └── metrics_scheme.py
│
└── ports/              # Port protocols
    ├── mcp/            # MCP ports
    │   ├── provider.py
    │   ├── resource_provider.py
    │   ├── tool_registry.py
    │   ├── session_manager.py
    │   └── monitoring.py
    │
    ├── observability.py # Observability ports
    └── registry.py      # Registry ports
```

---

## Design Patterns

### 1. Dependency Injection

**Pattern**: Constructor injection with auto-wiring

**Example**:
```python
class UserService:
    def __init__(self, db: IDatabase):
        self.db = db

# Auto-wired by container
container.register(IDatabase, PostgresDatabase)
container.register(UserService, UserService)  # Auto-wires IDatabase!
```

### 2. Protocol-Based Design

**Pattern**: Define interfaces as protocols, implement in adapters

**Example**:
```python
# Port (protocol)
class Logger(Protocol):
    def info(self, message: str, **kwargs) -> None: ...

# Adapter (implementation)
class ConsoleLogger(Logger):
    def info(self, message: str, **kwargs) -> None:
        print(f"INFO: {message}", kwargs)

# Usage
logger: Logger = container.resolve(Logger)
logger.info("User logged in", user_id="123")
```

### 3. Registry Pattern

**Pattern**: Generic registry with search, categories, metadata

**Example**:
```python
class ToolRegistry(BaseRegistry[McpTool]):
    pass

registry = ToolRegistry()
registry.register("search", tool, category="data")
tools = registry.search("database")
data_tools = registry.list_by_category("data")
```

### 4. Resource Scheme Pattern

**Pattern**: URI-based resource access with pluggable handlers

**Example**:
```python
# Register scheme handler
manager.register_resource_scheme("db", DbSchemeHandler())

# Access via URI
user = await manager.get_resource("db://users/123")
```

### 5. Manager Pattern

**Pattern**: Facade that coordinates multiple ports

**Example**:
```python
class McpManager:
    def __init__(self, container):
        self.container = container

    async def execute_tool(self, name, params):
        # Coordinates: provider, registry, monitoring
        registry = self.container.resolve(ToolRegistry)
        provider = self.container.resolve(McpProvider)
        monitor = self.container.resolve(MonitoringProvider)

        tool = registry.get_tool(name)
        result = await provider.execute_tool(tool, params)
        await monitor.record_metric("tool_execution", ...)
        return result
```

---

## Key Concepts

### 1. Ports (Protocols)

Ports define **what** the system needs, not **how** it's implemented.

```python
from typing import Protocol

class ResourceProvider(Protocol):
    async def get_resource(self, uri: str) -> Any: ...
    async def list_resources(self, pattern: str) -> List[str]: ...
```

### 2. Adapters (Implementations)

Adapters provide **how** the ports are implemented.

```python
class InMemoryResourceProvider(ResourceProvider):
    async def get_resource(self, uri: str) -> Any:
        # Implementation
        pass
```

### 3. Dependency Inversion

Domain depends on ports (abstractions), not adapters (concretions).

```python
# Domain
class McpManager:
    def __init__(self, container):
        # Depends on protocol, not implementation
        self.provider: ResourceProvider = container.resolve(ResourceProvider)

# Application
container.register(ResourceProvider, InMemoryResourceProvider)
manager = McpManager(container)
```

### 4. URI-Based Access

All resources accessible via URIs with scheme handlers.

```python
# Scheme handlers implement ResourceSchemeHandler protocol
class EnvSchemeHandler(ResourceSchemeHandler):
    async def get_resource(self, uri: str) -> Any:
        _, var_name = uri.split("://", 1)
        return os.environ[var_name]

# Register and use
provider.register_scheme("env", EnvSchemeHandler())
value = await provider.get_resource("env://PATH")
```

---

## Extension Points

### 1. Custom Resource Schemes

Add new URI schemes for custom data sources:

```python
from pheno.ports.mcp import ResourceSchemeHandler

class DbSchemeHandler(ResourceSchemeHandler):
    async def get_resource(self, uri: str):
        # db://table/id
        table, id = uri.split("://")[1].split("/")
        return await self.db.fetch(table, id)

    async def list_resources(self, uri: str):
        table = uri.split("://")[1]
        return await self.db.list(table)

    def supports_scheme(self, scheme: str):
        return scheme == "db"

# Register
manager.register_resource_scheme("db", DbSchemeHandler())

# Use
user = await manager.get_resource("db://users/123")
```

### 2. Custom Observability

Implement observability protocols for your monitoring system:

```python
from pheno.ports.observability import Logger, Meter, Tracer

class DatadogLogger(Logger):
    def info(self, message: str, **kwargs):
        # Send to Datadog
        pass

class PrometheusMetrics(Meter):
    def create_counter(self, name: str):
        # Create Prometheus counter
        pass

# Register
container.register(Logger, DatadogLogger)
container.register(Meter, PrometheusMetrics)
```

### 3. Custom Registries

Create specialized registries for your domain:

```python
from pheno.adapters.base_registry import BaseRegistry

class PluginRegistry(BaseRegistry[Plugin]):
    def load_plugin(self, name: str):
        plugin = self.get(name)
        plugin.initialize()
        return plugin

registry = PluginRegistry()
registry.register("auth", auth_plugin, category="security")
plugin = registry.load_plugin("auth")
```

---

## Testing Strategy

### 1. Unit Tests

Test domain logic in isolation using mock ports:

```python
from unittest.mock import Mock

def test_execute_tool():
    # Mock ports
    provider = Mock(spec=McpProvider)
    registry = Mock(spec=ToolRegistry)

    # Test domain logic
    manager = McpManager(container)
    result = await manager.execute_tool("search", {"query": "test"})

    # Verify interactions
    registry.get_tool.assert_called_once_with("search")
    provider.execute_tool.assert_called_once()
```

### 2. Integration Tests

Test adapters with real implementations:

```python
def test_env_scheme():
    os.environ["TEST_VAR"] = "test_value"

    handler = EnvSchemeHandler()
    value = await handler.get_resource("env://TEST_VAR")

    assert value == "test_value"
```

### 3. End-to-End Tests

Test complete workflows:

```python
async def test_complete_workflow():
    manager = setup_mcp(with_extended_schemes=True)

    # Register tool
    manager.register_tool(tool, handler=search_handler)

    # Execute
    result = await manager.execute_tool("search", {"query": "hello"})

    # Verify
    assert result.success
    assert "hello" in str(result.output)
```

---

## Best Practices

### 1. Depend on Protocols

```python
# Good
def process_data(logger: Logger):
    logger.info("Processing...")

# Bad
def process_data(logger: ConsoleLogger):
    logger.info("Processing...")
```

### 2. Use Dependency Injection

```python
# Good
class UserService:
    def __init__(self, db: IDatabase):
        self.db = db

# Bad
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard-coded dependency
```

### 3. Register in DI Container

```python
# Good
container.register(IDatabase, PostgresDatabase)
service = container.resolve(UserService)

# Bad
db = PostgresDatabase()
service = UserService(db)
```

### 4. Use URI-Based Access

```python
# Good
config = await manager.get_resource("config://app/database")

# Bad
with open("config.yaml") as f:
    config = yaml.load(f)["app"]["database"]
```

---

## See Also

- [API Reference](API_REFERENCE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Examples](../examples/)
