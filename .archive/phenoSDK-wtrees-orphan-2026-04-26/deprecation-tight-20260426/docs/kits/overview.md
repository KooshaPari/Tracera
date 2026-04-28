# Kits Overview

> Complete overview of all Pheno-SDK kits with use cases and selection guide

---

## Kit Categories

### 🏗️ Core Patterns (3 kits)
Foundation patterns for clean architecture

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [adapter-kit](../../adapter-kit/) | DI, Factory, Repository patterns | Always - foundational patterns |
| [config-kit](../../config-kit/) | Configuration management | Always - app configuration |
| [domain-kit](../../domain-kit/) | Domain-driven design | Complex business domains |

### 💾 Data Layer (3 kits)
Data persistence and retrieval

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [db-kit](../../db-kit/) | Universal database abstraction | Database operations |
| [storage-kit](../../storage-kit/) | Multi-provider file storage | File uploads/downloads |
| [vector-kit](../../vector-kit/) | Embeddings & semantic search | AI/ML, search features |

### 📊 Observability (2 kits)
Monitoring and debugging

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [observability-kit](../../observability-kit/) | Logging, metrics, tracing | Always - production apps |
| [resource-management-kit](../../resource-management-kit/) | Resource monitoring | Performance tracking |

### 🚀 Deployment (3 kits)
Application deployment and infrastructure

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [deploy-kit](../../deploy-kit/) | Universal deployment toolkit | Deploying to any platform |
| [multi-cloud-deploy-kit](../../multi-cloud-deploy-kit/) | Multi-cloud orchestration | Cloud deployments |
| [build-analyzer-kit](../../build-analyzer-kit/) | Build analysis | Optimizing builds |

### 🏗️ Service Infrastructure (2 kits)
Core service management and routing

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [service-infra](../../service-infra/) | Service orchestration and management | Multi-service applications |
| [proxy-gateway](../../proxy-gateway/) | Health-aware reverse proxy | API routing and load balancing |

### 🖥️ User Interface (2 kits)
CLI and terminal interfaces

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [tui-kit](../../tui-kit/) | Terminal UI components | Monitoring dashboards |
| [cli-builder-kit](../../cli-builder-kit/) | CLI framework | Command-line tools |

### 🌐 Communication (3 kits)
Real-time and asynchronous communication

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [stream-kit](../../stream-kit/) | WebSocket/SSE streaming | Real-time updates |
| [event-kit](../../event-kit/) | Event bus, webhooks | Event-driven architecture |
| [api-gateway-kit](../../api-gateway-kit/) | API gateway patterns | API management |

### 🔄 Orchestration (3 kits)
Workflow and process management

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [workflow-kit](../../workflow-kit/) | Saga pattern, workflows | Distributed transactions |
| [orchestrator-kit](../../orchestrator-kit/) | Multi-agent orchestration | Coordinating agents |
| [process-monitor-sdk](../../process-monitor-sdk/) | Process monitoring | Process tracking |

### 🤖 MCP Integration (3 kits)
Model Context Protocol support

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [mcp-sdk-kit](../../mcp-sdk-kit/) | MCP utilities | Building MCP servers |
| [mcp-infra-sdk](../../mcp-infra-sdk/) | MCP infrastructure | MCP infrastructure |
| [auth-adapters](../../authkit-client/) | Authentication adapters | Auth integration |

### 🛠️ Utilities (3 kits)
General-purpose utilities

| Kit | Purpose | When to Use |
|-----|---------|-------------|
| [filewatch-kit](../../filewatch-kit/) | File system watching | Hot reload, file monitoring |
| [pydevkit](../../pydevkit/) | Development utilities | Correlation IDs, utilities |
| [mcp-QA](../../mcp-QA/) | Quality assurance | Testing MCP servers |

---

## Use Case Matrix

### Building a REST API

**Required:**
- `adapter-kit` - Dependency injection
- `config-kit` - Configuration
- `observability-kit` - Logging & metrics

**Optional:**
- `db-kit` - Database operations
- `storage-kit` - File uploads
- `event-kit` - Event handling

### Building an MCP Server

**Required:**
- `mcp-sdk-kit` - MCP utilities
- `observability-kit` - Monitoring
- `workflow-kit` - Workflow management

**Optional:**
- `vector-kit` - Semantic search
- `db-kit` - Data persistence
- `mcp-QA` - Testing

### Building a CLI Tool

**Required:**
- `cli-builder-kit` - CLI framework
- `config-kit` - Configuration

**Optional:**
- `tui-kit` - Rich UI
- `filewatch-kit` - File monitoring
- `observability-kit` - Logging

### Building a Monitoring Dashboard

**Required:**
- `tui-kit` - Terminal UI
- `observability-kit` - Metrics collection

**Optional:**
- `stream-kit` - Real-time updates
- `resource-management-kit` - Resource tracking

### Building Microservices

**Required:**
- `adapter-kit` - Architecture patterns
- `observability-kit` - Distributed tracing
- `event-kit` - Inter-service communication
- `service-infra` - Service orchestration
- `proxy-gateway` - API routing

**Optional:**
- `stream-kit` - Real-time messaging
- `workflow-kit` - Saga pattern
- `auth-adapters` - Authentication

---

## Selection Guide

### Start Here (Every App)

1. **config-kit** - Configuration management
2. **observability-kit** - Logging, metrics, tracing
3. **adapter-kit** - Clean architecture patterns

### Add as Needed

**For Data:**
- `db-kit` - Database operations
- `storage-kit` - File storage
- `vector-kit` - Semantic search

**For Communication:**
- `stream-kit` - Real-time updates
- `event-kit` - Events & webhooks

**For Complex Workflows:**
- `workflow-kit` - Saga pattern
- `orchestrator-kit` - Agent coordination

**For Deployment:**
- `deploy-kit` - Platform deployment

**For User Interface:**
- `tui-kit` - Terminal dashboards
- `cli-builder-kit` - CLI tools

---

## Quick Start by Kit

### adapter-kit
```python
from adapter_kit import Container, Repository

container = Container()
container.register(IDatabase, PostgresDatabase, singleton=True)
db = container.resolve(IDatabase)
```

### db-kit
```python
from db_kit import Database

db = Database.supabase()
users = await db.query("users", filters={"active": True})
```

### observability-kit
```python
from observability import StructuredLogger, MetricsCollector

logger = StructuredLogger("my-app")
metrics = MetricsCollector()
```

### auth-adapters
```python
from pheno.auth import AuthManager
from pheno.adapters.auth.providers import AuthKitProvider

auth = AuthManager()
auth.register_provider("authkit", AuthKitProvider)
result = await auth.authenticate("authkit", credentials)
```

### service-infra
```python
from pheno.infra import ServiceManager, ServiceConfig

manager = ServiceManager()
manager.register_service(ServiceConfig(
    name="api",
    command=["python", "api.py"],
    preferred_port=8000
))
await manager.start_all()
```

### proxy-gateway
```python
from pheno.infra.proxy_gateway import ProxyServer

proxy = ProxyServer(proxy_port=9100, fallback_port=9000)
proxy.add_upstream("/api", port=8000)
await proxy.start()
```

### stream-kit
```python
from stream_kit import StreamingManager

manager = StreamingManager()
await manager.broadcast("channel", {"data": "value"})
```

### workflow-kit
```python
from workflow_kit import Saga

saga = Saga("process")
saga.add_step("action", do_work, compensation=undo)
```

---

## Dependencies Between Kits

```
config-kit (no deps)
    ↑
adapter-kit (no deps)
    ↑
db-kit
    ↑
mcp-sdk-kit ← observability-kit ← workflow-kit
```

Most kits are independent, but some commonly work together:
- `db-kit` uses `config-kit` for configuration
- `mcp-sdk-kit` integrates with `observability-kit`
- All kits can use `adapter-kit` patterns

---

## Performance Characteristics

| Kit | Overhead | Notes |
|-----|----------|-------|
| adapter-kit | None | Pure Python patterns |
| db-kit | Low | Query caching, connection pooling |
| observability-kit | ~0.1ms/operation | Minimal overhead |
| stream-kit | <1ms latency | WebSocket: fastest, SSE: ~2ms |
| storage-kit | Depends on provider | S3: network latency |
| vector-kit | Depends on provider | In-memory: fast, API: slow |

---

## Next Steps

1. **Read individual kit docs** - Each kit has comprehensive README
2. **Check examples** - Real code in each kit's `examples/` directory
3. **Try tutorials** - [docs/tutorials/](../tutorials/) for complete guides
4. **Join community** - GitHub Discussions for questions

---

For detailed API documentation, see [llms.txt](../../llms.txt).

<!-- DOCS_KITS_OVERVIEW_FINGERPRINT: d4f1a91589769fa0bc92c016b9abcd054c1fc380794a1490fc34bf49fb598a67 -->
