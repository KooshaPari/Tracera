# MCP Integration Map - Meta-Protocol Strategy

**Status**: Analysis Complete
**Date**: 2025-10-13
**Objective**: Map all MCP integration points and define consolidation strategy for MCP as meta-protocol

---

## Executive Summary

MCP (Model Context Protocol) is currently fragmented across **5 major components** in the phenoSDK ecosystem. This document maps all integration points and proposes a consolidation strategy to make MCP the **meta-protocol** that unifies all phenoSDK capabilities.

---

## 1. Current MCP Components

### 1.1 mcp-sdk-kit (Resource & Monitoring Layer)

**Location**: `mcp-sdk-kit/mcp_sdk/`

#### Core Modules

##### Resources (`mcp_sdk/resources/`)
```python
# Registry
ResourceRegistry - Central registry for MCP resources

# Template Engine
ResourceTemplate - Template definition with parameters
ResourceParameter - Parameter specification
ResourceAnnotation - Metadata annotations
ResourceContext - Execution context
ResourceTemplateEngine - Template rendering engine

# Scheme Handlers
ResourceSchemeHandler - Base handler protocol
ResourceSchemeRegistry - Scheme registration
```

##### Resource Schemes (`mcp_sdk/resources/schemes.py`)
```python
# Built-in schemes
ZenResourceScheme       # zen://     - Core server resources
SystemResourceScheme    # system://  - System information
ConfigResourceScheme    # config://  - Configuration access
LogsResourceScheme      # logs://    - Structured logs
MetricsResourceScheme   # metrics:// - Performance metrics
ToolsResourceScheme     # tools://   - Tool metadata
PromptsResourceScheme   # prompts:// - Prompt templates
FilesResourceScheme     # files://   - File system access
StaticResourceScheme    # static://  - Static content
```

##### Project Graph (`mcp_sdk/resources/project_graph.py`)
```python
# Node Types
NodeType - Enum for graph node types
NodeStatus - Node status tracking
GraphNode - Base graph node
WBSNode - Work Breakdown Structure node

# Project Management
ProjectGraph - Project dependency graph
Team - Team structure
TeamMember - Team member details
Deliverable - Project deliverable
AcceptanceCriterion - Acceptance criteria
QualityGate - Quality gate definition

# Requirements
UserStory - User story specification
RequirementSpec - Requirement specification
UseCase - Use case definition
TestCase - Test case definition

# Analysis
CriticalPathAnalysis - Critical path computation
CommunicationMessage - Team communication
```

##### Monitoring (`mcp_sdk/workflow.py`, `mcp_sdk/metrics.py`, `mcp_sdk/performance.py`)
```python
# Workflow Monitoring
WorkflowMonitoringIntegration - FastAPI integration
monitor_workflow_execution - Decorator for workflow tracking
configure_monitoring_from_env - Environment-based config
initialize_workflow_monitoring - Setup helper
integrate_with_server - Server integration

# Metrics
AgentMetricsCollector - Agent execution metrics
get_metrics_collector - Singleton accessor
MetricType - Metric type enum

# Performance
PerformanceOptimizer - Runtime optimization
get_performance_optimizer - Singleton accessor
```

**Purpose**: Provides MCP resource templates, project management structures, and monitoring capabilities

**Dependencies**:
- FastAPI (for workflow integration)
- Pydantic (for data models)
- Prometheus (optional, for metrics)

---

### 1.2 mcp-infra-sdk (Infrastructure Layer)

**Location**: `mcp-infra-sdk/mcp_infra/`

#### Core Capabilities
```python
# Production Infrastructure
create_production_app - Create production-ready MCP app
ProductionConfig - Production configuration

# Components (composes existing pheno-SDK)
# - tui-kit: Terminal UI components
# - process-monitor-sdk: Process management
# - Launchers: MCP server launchers
# - TUIs: Production TUI interfaces
# - Logging: Enhanced log viewing
# - Configuration: Environment loading
```

**Purpose**: Production infrastructure for MCP servers - launchers, TUIs, monitoring

**Key Features**:
- Production-ready Textual TUIs
- Process management with health checking
- Port allocation and tunnel management
- Configuration utilities
- Enhanced logging (filtering, tailing, buffering)

**Dependencies**:
- tui-kit
- process-monitor-sdk
- Textual (for TUI)

---

### 1.3 src/pheno/mcp (Domain Layer)

**Location**: `src/pheno/mcp/`

#### Domain Types (`types.py`)
```python
# Core MCP Abstractions
McpTool - MCP tool abstraction
McpServer - MCP server connection
ToolExecution - Tool execution context
McpSession - MCP communication session
ToolResult - Tool execution result
```

#### Manager (`mcp_manager.py`)
```python
McpManager - Central MCP management
```

**Purpose**: Domain-level MCP abstractions following hexagonal architecture

**Architecture**:
- Domain concepts in `pheno.mcp`
- Ports in `pheno.ports.mcp` (to be created)
- Adapters in mcp-sdk-kit, mcp-infra-sdk

**Current Status**: Minimal domain layer, needs port definitions

---

### 1.4 mcp-QA (Testing & Adapters Layer)

**Location**: `pheno/mcp/qa/`

#### Core Adapters (`pheno/mcp/qa/core/adapter.py`)
```python
MCPAdapter - Enhanced FastMCP client adapter
EnhancedMCPAdapter - Rich logging adapter
create_adapter - Factory function

# Features
# - Beautiful color-coded output
# - Emoji indicators
# - Structured logging with context
# - Performance metrics
# - Error highlighting
# - Configurable verbosity
```

#### Adapter Protocols (`pheno/mcp/qa/adapters/`)
```python
# Protocol definitions
create_oauth_adapter - OAuth adapter factory
create_resource_adapter - Resource monitor factory
MCPClientAdapter - Client wrapper adapter
```

**Purpose**: Testing utilities and adapters for MCP with rich logging and QA features

**Key Features**:
- Enhanced MCP client with rich output
- OAuth integration
- Resource monitoring
- Pytest plugins
- Credential management
- Retry logic with Cloudflare 530 handling

---

### 1.5 KInfra MCP Extensions

**Location**: `KInfra/libraries/python/kinfra/infrastructure/mcp_extensions/`

#### MCP Manager (`mcp_manager.py`)
```python
# Environment Detection
detect_mcp_environment - Auto-detect MCP environment
get_mcp_endpoint - Get MCP endpoint URL
get_mcp_config - Get MCP configuration
set_mcp_environment - Set MCP environment

# Integration
# - Cloudflare tunnel integration
# - Environment-based configuration
# - Multi-environment support
```

**Purpose**: KInfra-specific MCP integration for infrastructure management

**Key Features**:
- MCP environment detection
- Endpoint configuration
- Tunnel management integration
- Multi-environment support

---

## 2. MCP as Meta-Protocol Strategy

### 2.1 Vision

**MCP should be the universal protocol that:**
1. Exposes all phenoSDK capabilities as MCP resources
2. Provides unified tool interface for all kits
3. Enables cross-kit composition via MCP sessions
4. Supports monitoring and observability through MCP
5. Allows external systems to interact with phenoSDK via MCP

### 2.2 Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Meta-Protocol                        │
│                    (pheno.mcp unified API)                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Resources  │      │  Monitoring  │     │Infrastructure│
│ (mcp-sdk-kit)│      │(mcp-sdk-kit) │     │(mcp-infra)   │
└──────────────┘      └──────────────┘     └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │ Ports Layer  │    │ Domain Layer │
            │(pheno.ports) │    │  (pheno.*)   │
            └──────────────┘    └──────────────┘
```

### 2.3 Hexagonal Architecture Mapping

#### Domain Layer (`pheno.mcp`)
```python
# Core domain types
McpTool, McpServer, McpSession, ToolExecution, ToolResult

# Domain services
McpManager - Orchestrates MCP operations

# Resource abstractions
Resource, ResourceTemplate, ResourceContext

# Monitoring abstractions
WorkflowMonitor, MetricsCollector
```

#### Ports Layer (`pheno.ports.mcp` - TO BE CREATED)
```python
# Provider protocols
class McpProvider(Protocol):
    """MCP implementation provider"""
    async def connect(self, server: McpServer) -> McpSession: ...
    async def execute_tool(self, tool: McpTool, params: dict) -> ToolResult: ...

class ToolRegistry(Protocol):
    """Tool registration and discovery"""
    def register_tool(self, tool: McpTool) -> None: ...
    def get_tool(self, name: str) -> McpTool: ...
    def list_tools(self) -> list[McpTool]: ...

class SessionManager(Protocol):
    """Session lifecycle management"""
    async def create_session(self, server: McpServer) -> McpSession: ...
    async def close_session(self, session: McpSession) -> None: ...

class ResourceProvider(Protocol):
    """Resource access and management"""
    async def get_resource(self, uri: str) -> Any: ...
    def register_scheme(self, scheme: str, handler: ResourceSchemeHandler) -> None: ...

class MonitoringProvider(Protocol):
    """Workflow and metrics monitoring"""
    async def track_workflow(self, workflow_id: str, metadata: dict) -> None: ...
    async def record_metric(self, name: str, value: float, tags: dict) -> None: ...
```

#### Adapter Layer (Existing kits implement ports)
```python
# mcp-sdk-kit implements:
# - ResourceProvider (via ResourceRegistry, schemes)
# - MonitoringProvider (via WorkflowMonitoringIntegration)
# - ToolRegistry (via resource templates)

# mcp-infra-sdk implements:
# - McpProvider (via production infrastructure)
# - SessionManager (via launcher and process management)

# mcp-QA implements:
# - McpProvider (via enhanced adapters)
# - Testing utilities
```

---

## 3. Consolidation Roadmap

### Phase 1: Define Ports (Week 1)

**Create `src/pheno/ports/mcp/`**
```
src/pheno/ports/mcp/
├── __init__.py
├── provider.py          # McpProvider protocol
├── tool_registry.py     # ToolRegistry protocol
├── session_manager.py   # SessionManager protocol
├── resource_provider.py # ResourceProvider protocol
└── monitoring.py        # MonitoringProvider protocol
```

**Tasks**:
- [ ] Define all MCP port protocols
- [ ] Document protocol contracts
- [ ] Add type hints and docstrings
- [ ] Create protocol tests

### Phase 2: Expand Domain Layer (Week 2)

**Expand `src/pheno/mcp/`**
```
src/pheno/mcp/
├── __init__.py
├── types.py            # Existing domain types
├── mcp_manager.py      # Existing manager
├── resources.py        # Resource abstractions (new)
├── monitoring.py       # Monitoring abstractions (new)
└── tools.py            # Tool abstractions (new)
```

**Tasks**:
- [ ] Move resource abstractions from mcp-sdk-kit to domain
- [ ] Move monitoring abstractions from mcp-sdk-kit to domain
- [ ] Keep implementations in mcp-sdk-kit as adapters
- [ ] Update imports and dependencies

### Phase 3: Implement Adapters (Week 3)

**Update mcp-sdk-kit to implement ports**
```python
# mcp-sdk-kit/mcp_sdk/adapters/
from pheno.ports.mcp import ResourceProvider, MonitoringProvider

class McpResourceAdapter(ResourceProvider):
    """Implements ResourceProvider using mcp-sdk-kit"""
    # Existing ResourceRegistry, schemes implementation

class McpMonitoringAdapter(MonitoringProvider):
    """Implements MonitoringProvider using mcp-sdk-kit"""
    # Existing WorkflowMonitoringIntegration implementation
```

**Tasks**:
- [ ] Create adapter implementations in mcp-sdk-kit
- [ ] Create adapter implementations in mcp-infra-sdk
- [ ] Update mcp-QA to use ports
- [ ] Add adapter tests

### Phase 4: Unified API Surface (Week 4)

**Create unified `pheno.mcp` API**
```python
# Single import for all MCP functionality
from pheno.mcp import (
    # Domain types
    McpTool, McpServer, McpSession, ToolExecution, ToolResult,

    # Manager
    McpManager,

    # Resources (auto-wired from mcp-sdk-kit adapter)
    ResourceRegistry, ResourceTemplate, get_resource,

    # Monitoring (auto-wired from mcp-sdk-kit adapter)
    WorkflowMonitor, track_workflow, record_metric,

    # Infrastructure (auto-wired from mcp-infra-sdk adapter)
    create_production_app, ProductionConfig,

    # Schemes
    register_scheme, get_scheme_handler,
)
```

**Tasks**:
- [ ] Create unified API in `pheno.mcp.__init__.py`
- [ ] Auto-wire adapters using DI container
- [ ] Add comprehensive examples
- [ ] Update all documentation

---

## 4. MCP Resource Scheme Strategy

### 4.1 Extend Schemes to Cover All Kits

**Proposed Additional Schemes**:
```python
# Data Access
db://          # Database resources (db-kit)
storage://     # Storage resources (storage-kit)
vector://      # Vector store resources (vector-kit)

# Communication
stream://      # Stream resources (stream-kit)
event://       # Event resources (event-kit)

# Workflow
workflow://    # Workflow resources (workflow-kit)
orchestrator:// # Orchestration resources (orchestrator-kit)

# Deployment
deploy://      # Deployment resources (deploy-kit)
cloud://       # Cloud provider resources (multi-cloud-deploy-kit)

# UI
tui://         # TUI resources (tui-kit)
cli://         # CLI resources (cli-builder-kit)

# Development
test://        # Test resources (pheno.testing)
qa://          # QA resources (mcp-QA)
```

### 4.2 Scheme Handler Pattern

```python
from pheno.ports.mcp import ResourceSchemeHandler

class DbSchemeHandler(ResourceSchemeHandler):
    """Handle db:// resources"""

    async def get_resource(self, uri: str) -> Any:
        # Parse db://table/id
        # Use db-kit to fetch resource
        pass

    async def list_resources(self, uri: str) -> list[str]:
        # List available database resources
        pass
```

---

## 5. Integration Examples

### 5.1 Unified MCP Access

```python
from pheno.mcp import McpManager, get_resource

# Initialize MCP manager
manager = McpManager()

# Access resources via schemes
config = await get_resource("config://app/database")
logs = await get_resource("logs://app/errors?limit=100")
metrics = await get_resource("metrics://app/requests")

# Database access via MCP
users = await get_resource("db://users?active=true")

# Storage access via MCP
file = await get_resource("storage://s3/bucket/file.txt")

# Vector search via MCP
results = await get_resource("vector://embeddings/search?q=machine+learning")
```

### 5.2 Cross-Kit Composition

```python
from pheno.mcp import McpManager, track_workflow

manager = McpManager()

# Workflow that composes multiple kits via MCP
@track_workflow("data_pipeline")
async def data_pipeline():
    # Fetch from database
    data = await get_resource("db://raw_data")

    # Store in cloud storage
    await manager.execute_tool("storage.upload", {
        "uri": "storage://s3/processed/data.json",
        "content": data
    })

    # Generate embeddings
    embeddings = await manager.execute_tool("vector.embed", {
        "text": data["content"]
    })

    # Store embeddings
    await get_resource("vector://store/add", method="POST", data=embeddings)
```

---

## 6. Benefits of MCP as Meta-Protocol

### 6.1 Unified Interface
- Single protocol for all phenoSDK capabilities
- Consistent resource access patterns
- Standard tool execution interface

### 6.2 Discoverability
- All capabilities exposed via MCP resources
- Self-documenting through resource templates
- Tool metadata available via `tools://` scheme

### 6.3 Composability
- Cross-kit workflows via MCP sessions
- Resource chaining through URIs
- Event-driven composition via MCP events

### 6.4 Observability
- All operations tracked through MCP monitoring
- Unified metrics collection
- Workflow visualization via project graph

### 6.5 External Integration
- External systems can use phenoSDK via MCP
- Language-agnostic protocol
- Standard MCP clients work out of the box

---

## 7. Next Steps

### Immediate (This Week)
1. [ ] Review and approve MCP integration map
2. [ ] Define `pheno.ports.mcp` protocols
3. [ ] Create MCP consolidation branch

### Short Term (Weeks 1-2)
1. [ ] Implement all MCP ports
2. [ ] Expand `pheno.mcp` domain layer
3. [ ] Update mcp-sdk-kit as adapter

### Medium Term (Weeks 3-4)
1. [ ] Create unified MCP API
2. [ ] Add scheme handlers for all kits
3. [ ] Comprehensive MCP documentation
4. [ ] MCP integration examples

---

**End of MCP Integration Map**
