# TracerTM Unified Architecture

**Version:** 2.0.0
**Date:** January 31, 2026
**Status:** Production Ready

## Table of Contents

1. [Overview](#overview)
2. [3-Tier Architecture](#3-tier-architecture)
3. [Service Communication Matrix](#service-communication-matrix)
4. [Port Assignments](#port-assignments)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Technology Stack](#technology-stack)
7. [Auto-Reload Mechanisms](#auto-reload-mechanisms)
8. [Infrastructure Components](#infrastructure-components)

---

## Overview

TracerTM is a modern, agent-native requirements traceability management system built on a **unified 3-tier architecture** with **polyglot microservices**, **real-time sync**, and **AI-powered analysis**.

###Key Architectural Principles

- **Polyglot Microservices**: Go for performance-critical operations, Python for AI/ML and flexible scripting
- **Unified API Gateway**: Single entry point with intelligent routing (Caddy)
- **Real-time Everything**: WebSocket + NATS for instant updates
- **Hot Reload Development**: All services support live code reloading
- **Process Orchestration**: Overmind manages all services with tmux multiplexing
- **Temporal Workflows**: Durable execution for long-running operations

---

## 3-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION TIER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐ │
│  │   Web Application    │  │   Desktop (Electron) │  │   Python CLI/TUI │ │
│  │  React + TanStack    │  │    Tauri/Electron    │  │  Typer + Textual │ │
│  │   Port: 5173         │  │   Bundled Runtime    │  │   Terminal-based │ │
│  └──────────┬───────────┘  └──────────┬───────────┘  └─────────┬────────┘ │
│             │                          │                        │          │
│             └──────────────────────────┴────────────────────────┘          │
│                                        │                                    │
└────────────────────────────────────────┼────────────────────────────────────┘
                                         │
                                    ┌────▼────┐
                                    │  Caddy  │ API Gateway & TLS Termination
                                    │Port: 80 │ Intelligent Request Routing
                                    └────┬────┘
                                         │
┌────────────────────────────────────────┼────────────────────────────────────┐
│                             APPLICATION TIER                                 │
├────────────────────────────────────────┴────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────┐      ┌─────────────────────────────────┐  │
│  │     Go Backend (Gin)        │◄────►│  Python Backend (FastAPI)       │  │
│  │      Port: 8080             │ gRPC │       Port: 8000                │  │
│  ├─────────────────────────────┤      ├─────────────────────────────────┤  │
│  │ • Projects Management       │      │ • Specifications                │  │
│  │ • Items (Req/Feature/Task)  │      │ • Executions & Test Results     │  │
│  │ • Links (Traceability)      │      │ • MCP (Model Context Protocol)  │  │
│  │ • Graph Analysis            │      │ • Quality Metrics               │  │
│  │ • Search (pgvector)         │      │ • Authentication (WorkOS)       │  │
│  │ • Real-time (WebSocket)     │      │ • Notifications                 │  │
│  │ • AI Agent Coordination     │      │ • AI/ML Services                │  │
│  │ • Temporal Client           │      │ • gRPC Client                   │  │
│  │ • Hot Reload (Air)          │      │ • Hot Reload (uvicorn)          │  │
│  └─────────────┬───────────────┘      └─────────────┬───────────────────┘  │
│                │                                     │                       │
│                └──────────────┬──────────────────────┘                       │
│                               │                                              │
│                    ┌──────────▼──────────┐                                  │
│                    │  Temporal Server    │  Workflow Orchestration          │
│                    │    Port: 7233       │  Durable Execution               │
│                    └──────────┬──────────┘                                  │
│                               │                                              │
└───────────────────────────────┼──────────────────────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────────────────┐
│                              DATA TIER                                       │
├───────────────────────────────┴──────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌──────────┐ │
│  │   PostgreSQL   │  │   Neo4j Graph  │  │  Redis Cache   │  │   NATS   │ │
│  │  Port: 5432    │  │  Port: 7687    │  │  Port: 6379    │  │Port: 4222│ │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤  ├──────────┤ │
│  │ • Relational   │  │ • Graph DB     │  │ • Session      │  │ • Events │ │
│  │   Data         │  │ • Traceability │  │   Storage      │  │ • PubSub │ │
│  │ • pgvector     │  │   Queries      │  │ • Query Cache  │  │ • Queue  │ │
│  │   (embeddings) │  │ • Impact       │  │ • Rate Limit   │  │ • Stream │ │
│  │ • Full-text    │  │   Analysis     │  │ • Distributed  │  │ • Durable│ │
│  │   Search       │  │ • Cycles       │  │   Locks        │  │   Msgs   │ │
│  └────────────────┘  └────────────────┘  └────────────────┘  └──────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         OBSERVABILITY & MONITORING                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌──────────┐ │
│  │  Prometheus    │  │    Grafana     │  │  Exporters     │  │  Logs    │ │
│  │  Port: 9090    │  │  Port: 3000    │  │  Various Ports │  │  Files   │ │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤  ├──────────┤ │
│  │ • Metrics      │  │ • Dashboards   │  │ • Nginx: 9113  │  │ • Caddy  │ │
│  │   Collection   │  │ • Alerts       │  │ • Postgres:    │  │ • Nginx  │ │
│  │ • Time-series  │  │ • Visualization│  │   9187         │  │ • App    │ │
│  │   Database     │  │ • Analytics    │  │ • Redis: 9121  │  │   Logs   │ │
│  └────────────────┘  └────────────────┘  └────────────────┘  └──────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Service Communication Matrix

This matrix shows which services communicate with each other and via which protocol.

### Legend
- ✅ = Direct Communication
- gRPC = gRPC Protocol
- HTTP = REST API
- WS = WebSocket
- NATS = Message Queue
- DB = Database Connection

```
┌─────────────────┬─────┬────┬────┬──────┬──────┬──────┬──────┬────────┬────────┐
│ From \ To       │ Go  │ Py │ Web│ Caddy│ PG   │ Redis│ NATS │ Temporal│ Neo4j │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Web App         │     │    │    │ HTTP │      │      │      │        │        │
│ (Frontend)      │     │    │    │  WS  │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Caddy Gateway   │ HTTP│HTTP│HTTP│      │      │      │      │        │        │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Go Backend      │     │gRPC│ WS │      │  DB  │  ✅  │ NATS │   ✅   │   DB   │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Python Backend  │gRPC │    │    │      │  DB  │  ✅  │ NATS │   ✅   │        │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ PostgreSQL      │     │    │    │      │      │      │      │        │        │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Redis           │     │    │    │      │      │      │      │        │        │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ NATS            │     │    │    │      │      │      │      │        │        │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Temporal        │  ✅ │ ✅ │    │      │      │      │      │        │        │
│                 │     │    │    │      │      │      │      │        │        │
├─────────────────┼─────┼────┼────┼──────┼──────┼──────┼──────┼────────┼────────┤
│ Neo4j           │     │    │    │      │      │      │      │        │        │
│                 │     │    │    │      │      │      │      │        │        │
└─────────────────┴─────┴────┴────┴──────┴──────┴──────┴──────┴────────┴────────┘
```

### Communication Patterns

#### 1. Client → Backend (API Requests)
```
Web/Desktop → Caddy → Go/Python Backend
```

#### 2. Real-time Updates (WebSocket)
```
Web → Caddy → Go Backend → NATS → All Connected Clients
```

#### 3. Inter-Service Communication (gRPC)
```
Go Backend ←─gRPC─→ Python Backend
   │                     │
   ├─ GraphService ─────►│  (Go provides, Python consumes)
   │◄─ AIService ────────┤  (Python provides, Go consumes)
```

#### 4. Event-Driven (NATS)
```
Any Service → NATS → Subscribed Services
```

#### 5. Workflow Orchestration (Temporal)
```
Go/Python → Temporal Server → Workflow Execution → Go/Python Workers
```

---

## Port Assignments

### Development Ports (Local)

| Service | Port | Protocol | Purpose | URL |
|---------|------|----------|---------|-----|
| **Frontend** |
| Vite Dev Server | 5173 | HTTP | Web UI development | http://localhost:5173 |
| Storybook | 6006 | HTTP | Component development | http://localhost:6006 |
| **API Gateway** |
| Caddy | 80 | HTTP | Unified API gateway | http://localhost |
| Caddy Admin | 2019 | HTTP | Runtime configuration | http://localhost:2019 |
| **Application Services** |
| Go Backend | 8080 | HTTP/WS | Go API + WebSocket | http://localhost:8080 |
| Python Backend | 8000 | HTTP | Python/FastAPI API | http://localhost:4000 |
| Temporal Server | 7233 | gRPC | Workflow orchestration | localhost:7233 |
| Temporal UI | 8233 | HTTP | Workflow visualization | http://localhost:8233 |
| **Databases** |
| PostgreSQL | 5432 | TCP | Primary database | postgresql://localhost:5432 |
| Redis | 6379 | TCP | Cache & sessions | redis://localhost:6379 |
| Neo4j | 7687 | Bolt | Graph database | bolt://localhost:7687 |
| Neo4j HTTP | 7474 | HTTP | Neo4j browser | http://localhost:7474 |
| **Messaging** |
| NATS Client | 4222 | TCP | Message broker | nats://localhost:4222 |
| NATS Cluster | 6222 | TCP | Cluster communication | - |
| NATS Monitor | 8222 | HTTP | Monitoring/metrics | http://localhost:8222 |
| **Observability** |
| Prometheus | 9090 | HTTP | Metrics collection | http://localhost:9090 |
| Grafana | 3000 | HTTP | Dashboards | http://localhost:3000 |
| **Exporters** |
| Nginx Exporter | 9113 | HTTP | Nginx metrics | http://localhost:9113 |
| Postgres Exporter | 9187 | HTTP | PostgreSQL metrics | http://localhost:9187 |
| Redis Exporter | 9121 | HTTP | Redis metrics | http://localhost:9121 |

### Production Ports (Docker/K8s)

| Service | Port | Load Balanced | Public |
|---------|------|---------------|--------|
| Nginx Gateway | 80, 443 | ✅ | ✅ |
| Go Backend | 8080 | ✅ | ❌ |
| Python Backend | 8000 | ✅ | ❌ |
| PostgreSQL | 5432 | ❌ | ❌ |
| Redis | 6379 | ✅ | ❌ |
| NATS | 4222 | ✅ | ❌ |

---

## Data Flow Diagrams

### 1. User Request Flow (Read Operations)

```
┌──────┐
│ User │
└──┬───┘
   │
   ▼
┌────────────┐
│ Web Client │
└──┬─────────┘
   │ HTTP GET /api/v1/projects
   ▼
┌─────────────┐
│   Caddy     │ Route based on URL path
└──┬──────────┘
   │ Proxy to localhost:8080
   ▼
┌─────────────┐
│ Go Backend  │
└──┬──────────┘
   │ 1. Check Redis cache
   ▼
┌─────────────┐
│    Redis    │ Cache hit? Return cached data
└──┬──────────┘
   │ Cache miss
   ▼
┌─────────────┐
│ PostgreSQL  │ Query database
└──┬──────────┘
   │ Return results
   ▼
┌─────────────┐
│ Go Backend  │ 1. Store in Redis cache
└──┬──────────┘  2. Return to client
   │
   ▼
┌────────────┐
│ Web Client │ Display data
└────────────┘
```

### 2. Real-time Update Flow (WebSocket)

```
┌──────────┐                    ┌──────────┐
│  User A  │                    │  User B  │
└────┬─────┘                    └────┬─────┘
     │                               │
     │ WebSocket Connection          │
     ▼                               ▼
┌─────────────────────────────────────────┐
│            Caddy Gateway                │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│          Go Backend (WebSocket)         │
└───────────────┬─────────────────────────┘
                │
                │ Subscribe to topics
                ▼
┌─────────────────────────────────────────┐
│               NATS                      │
└───────────────┬─────────────────────────┘
                │
  ┌─────────────┼─────────────┐
  │             │             │
  ▼             ▼             ▼
┌────┐      ┌────┐       ┌────┐
│Sub1│      │Sub2│       │Sub3│
└────┘      └────┘       └────┘
  │             │             │
  │ Item Updated Event        │
  └─────────────┼─────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│          Go Backend (WebSocket)         │
└───────────────┬─────────────────────────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
┌──────────┐      ┌──────────┐
│  User A  │      │  User B  │
└──────────┘      └──────────┘
Both receive update in real-time
```

### 3. Cross-Service Operation (gRPC)

```
┌────────────┐
│ Web Client │
└──┬─────────┘
   │ POST /api/v1/specifications
   ▼
┌─────────────┐
│   Caddy     │ Route to Python
└──┬──────────┘
   │
   ▼
┌──────────────────┐
│ Python Backend   │
└──┬───────────────┘
   │ 1. Process specification
   │ 2. Need graph analysis
   ▼
┌──────────────────┐
│ gRPC Client      │ Call Go's GraphService.AnalyzeImpact()
└──┬───────────────┘
   │ gRPC over HTTP/2
   ▼
┌──────────────────┐
│   Go Backend     │
│  (gRPC Server)   │
└──┬───────────────┘
   │ 1. Query Neo4j for graph
   ▼
┌──────────────────┐
│      Neo4j       │ Cypher query for impact analysis
└──┬───────────────┘
   │ Return affected nodes
   ▼
┌──────────────────┐
│   Go Backend     │ Process and return results
└──┬───────────────┘
   │ gRPC response
   ▼
┌──────────────────┐
│ Python Backend   │ 1. Receive impact data
└──┬───────────────┘  2. Complete specification processing
   │                  3. Store in PostgreSQL
   ▼
┌──────────────────┐
│   PostgreSQL     │
└──┬───────────────┘
   │ Success
   ▼
┌──────────────────┐
│ Python Backend   │ Return response to client
└──┬───────────────┘
   │
   ▼
┌────────────┐
│ Web Client │
└────────────┘
```

---

## Technology Stack

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React 18 | 18.x | UI framework |
| **Router** | TanStack Router | 1.x | Type-safe routing |
| **State Management** | Zustand | 5.x | Global state |
| **API Client** | TanStack Query | 5.x | Server state + caching |
| **UI Components** | shadcn/ui | - | Accessible components |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |
| **Build Tool** | Vite | 6.x | Fast dev server + bundler |
| **Package Manager** | Bun | 1.x | Fast package manager |
| **Graph Visualization** | React Flow | 11.x | Interactive graphs |
| **Testing** | Vitest + Playwright | Latest | Unit + E2E tests |

### Backend - Go

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Go | 1.22+ | Systems programming |
| **Web Framework** | Gin | 1.x | HTTP router |
| **ORM** | GORM | 1.x | Database abstraction |
| **Database Driver** | pgx | 5.x | PostgreSQL driver |
| **gRPC** | grpc-go | 1.x | Inter-service RPC |
| **WebSocket** | gorilla/websocket | 1.x | Real-time connections |
| **NATS Client** | nats.go | 1.x | Message queue client |
| **Hot Reload** | Air | 1.x | Development auto-reload |
| **API Docs** | Swaggo | 1.x | OpenAPI generation |

### Backend - Python

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.12+ | AI/ML & flexibility |
| **Web Framework** | FastAPI | 0.115+ | Modern async API |
| **ORM** | SQLAlchemy | 2.x | Database abstraction |
| **Async Driver** | asyncpg | 0.31+ | PostgreSQL async driver |
| **gRPC** | grpcio | 1.x | Inter-service RPC |
| **NATS Client** | nats-py | 2.x | Message queue client |
| **Temporal** | temporalio | 1.x | Workflow orchestration |
| **AI/ML** | Anthropic SDK | 0.77+ | Claude AI integration |
| **Hot Reload** | uvicorn --reload | - | Development auto-reload |
| **CLI** | Typer | 0.21+ | Command-line interface |

### Infrastructure

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Gateway** | Caddy | 2.x | Reverse proxy + TLS |
| **Process Manager** | Overmind | 2.x | Development orchestration |
| **Workflow Engine** | Temporal | 1.x | Durable execution |
| **Database** | PostgreSQL | 15+ | Relational data + pgvector |
| **Graph Database** | Neo4j | 5.x | Graph relationships |
| **Cache** | Redis | 7.x | In-memory cache |
| **Message Queue** | NATS | 2.x | Pub/sub + streaming |
| **Container** | Docker | 27.x | Containerization |
| **Orchestration** | Docker Compose | 2.x | Multi-container apps |
| **Monitoring** | Prometheus + Grafana | Latest | Metrics + dashboards |

---

## Auto-Reload Mechanisms

All services support hot reload in development for instant feedback.

### Frontend (Vite)

**Technology:** Vite HMR (Hot Module Replacement)

```bash
# Procfile entry
frontend: cd frontend/apps/web && bun run dev --host 0.0.0.0
```

**Features:**
- Instant updates for .tsx/.ts files
- Preserves application state
- Sub-100ms reload times
- WebSocket-based update protocol

### Go Backend (Air)

**Technology:** Air - Live reload for Go apps

```bash
# Procfile entry
go: cd backend && air -c .air.toml
```

**Configuration:** `backend/.air.toml`

```toml
[build]
  cmd = "go build -o ./tmp/main ."
  bin = "./tmp/main"
  delay = 1000
  exclude_dir = ["assets", "tmp", "vendor", "frontend"]
  include_ext = ["go", "tpl", "tmpl", "html"]
  exclude_regex = ["_test.go"]
```

**How it works:**
1. Air watches file system for changes
2. Detects `.go` file modification
3. Stops current process
4. Recompiles binary
5. Starts new process
6. Typically completes in 1-3 seconds

### Python Backend (Uvicorn)

**Technology:** Uvicorn with `--reload` flag

```bash
# Procfile entry
python: uvicorn src.tracertm.api.main:app --reload --host 0.0.0.0 --port 8000
```

**How it works:**
1. Uvicorn uses watchfiles library
2. Monitors Python files in project
3. Detects changes
4. Gracefully shuts down workers
5. Reloads application
6. Starts new workers

### Caddy (Auto-reload Config)

**Technology:** Caddy `--watch` flag

```bash
# Procfile entry
caddy: caddy run --config Caddyfile --watch
```

**How it works:**
1. Caddy monitors Caddyfile
2. Detects configuration change
3. Validates new configuration
4. Hot-swaps routing rules
5. Preserves active connections

---

## Infrastructure Components

### 1. Overmind Process Manager

**Purpose:** Unified orchestration of all development services

**Usage:**
```bash
# Start all services
overmind start

# Start specific services
overmind start go python frontend

# Restart a service
overmind restart go

# Connect to a service
overmind connect go

# Stop all services
overmind kill
```

**Procfile Structure:**
```bash
temporal: temporal server start-dev --db-filename .temporal/dev.db
caddy: caddy run --config Caddyfile --watch
go: cd backend && air -c .air.toml
python: uvicorn src.tracertm.api.main:app --reload --host 0.0.0.0 --port 8000
frontend: cd frontend/apps/web && bun run dev --host 0.0.0.0
temporal_worker: python -m tracertm.workflows.worker
```

### 2. Caddy API Gateway

**Purpose:** Unified entry point with intelligent routing

**Routing Strategy:**

| URL Pattern | Backend | Service | Purpose |
|-------------|---------|---------|---------|
| `/api/v1/projects/*` | Go (8080) | Projects API | Project management |
| `/api/v1/items/*` | Go (8080) | Items API | Requirements/tasks |
| `/api/v1/links/*` | Go (8080) | Links API | Traceability |
| `/api/v1/graph/*` | Go (8080) | Graph API | Analysis |
| `/api/v1/search/*` | Go (8080) | Search API | Full-text search |
| `/api/v1/ws` | Go (8080) | WebSocket | Real-time updates |
| `/api/v1/specifications/*` | Python (8000) | Specs API | Specifications |
| `/api/v1/executions/*` | Python (8000) | Exec API | Test execution |
| `/api/v1/mcp/*` | Python (8000) | MCP API | Model Context Protocol |
| `/api/v1/quality/*` | Python (8000) | Quality API | Quality metrics |
| `/api/v1/auth/*` | Python (8000) | Auth API | Authentication |
| `/*` | Frontend (5173) | UI | Web application |

### 3. gRPC Inter-Service Communication

**Protocol Buffers:** `/proto/tracertm/v1/tracertm.proto`

**Services:**

#### GraphService (Go → Python)
```protobuf
service GraphService {
  rpc AnalyzeImpact(ImpactRequest) returns (ImpactResponse);
  rpc FindCycles(CycleRequest) returns (CycleResponse);
  rpc CalculatePath(PathRequest) returns (PathResponse);
  rpc StreamGraphUpdates(GraphStreamRequest) returns (stream GraphUpdate);
}
```

### 4. NATS Message Broker

**Purpose:** Event-driven architecture + real-time sync

**Subjects:**
```
tracertm.items.created
tracertm.items.updated
tracertm.items.deleted
tracertm.links.created
tracertm.links.deleted
tracertm.specifications.created
tracertm.executions.completed
tracertm.websocket.broadcast
```

### 5. Temporal Workflows

**Purpose:** Durable execution for long-running operations

**Example Workflows:**
- Test suite execution
- Bulk import/export operations
- AI-powered analysis tasks
- Scheduled report generation

---

## Next Steps

- See [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) for daily developer workflow
- See [RTM_DEV_QUICK_REFERENCE.md](../reference/RTM_DEV_QUICK_REFERENCE.md) for command cheat sheet
- See [UNIFIED_INFRASTRUCTURE_IMPLEMENTATION.md](../reports/UNIFIED_INFRASTRUCTURE_IMPLEMENTATION.md) for implementation details
- See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment

---

**Document Version:** 2.0.0
**Last Updated:** January 31, 2026
**Maintained By:** TracerTM Architecture Team
