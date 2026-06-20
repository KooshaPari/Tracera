# 06 -- Implementation Guide

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [05-ARCHITECTURE](./05-ARCHITECTURE.md) | [07-TEST](./07-TEST-STRATEGY.md)

---

## Project Structure

### Python Backend (`src/tracertm/`)

```
src/tracertm/
  api/                    # FastAPI routers
    main.py               # FastAPI app factory
    routers/              # Endpoint definitions
    middleware/           # Auth, CORS, timing
  cli/                    # Typer CLI (6+ command modules)
    app.py                # Main CLI app factory
    commands/             # Command modules (backup, design, dev, graph, impact, test)
    __main__.py           # CLI entry point
    performance.py        # Perf profiling CLI
    ui/                   # TUI components
  tui/                    # Textual TUI (future expansion)
  services/               # Business logic (92 service modules)
    item_service.py
    link_service.py
    search_service.py
    auto_link_service.py
    traceability_matrix_service.py
    impact_analysis_service.py
    agent_coordination_service.py
    ...
  repositories/           # Data access layer (42+ modules)
    item_repository.py
    link_repository.py
    event_repository.py
    ...
  models/                 # SQLAlchemy ORM (53 model modules, 6800+ LOC)
    item.py
    link.py
    project.py
    agent.py
    ...
  mcp/                    # FastMCP server (20 tool modules)
    core.py               # FastMCP server instance
    server.py             # MCP server setup
    tools/                # Tool implementations (20 modules)
      items.py            # Item CRUD tools
      links.py            # Link management tools
      projects.py         # Project tools
      graph.py            # Graph analysis tools
      traceability.py     # Traceability tools
      core_tools.py       # Core utilities
      ...
    resources/            # Resource handlers
    auth.py               # MCP auth provider
    metrics.py            # Prometheus metrics
  workflows/              # Temporal workflows
  agent/                  # AI agent coordination
  clients/                # External service clients
  grpc/                   # gRPC service implementations
  infrastructure/         # Cache, queue, circuit breaker
  observability/          # OTel, Prometheus, logging
  storage/                # Local/S3 file storage
  validation/             # Data validation
  vault/                  # HashiCorp Vault
  schemas/                # Pydantic schemas/DTOs (23+ modules)
  config/                 # Configuration management (8 modules)
  database/               # Database utilities
  core/                   # Core utilities
  utils/                  # General utilities
  v1/                     # API v1 support
  constants.py            # Global constants
  preflight.py            # Startup checks (16KB+ preflight logic)
```

### Go Backend (`backend/`)

```
backend/
  cmd/api/               # API entry point
    main.go              # Primary entry
  internal/              # 57 internal packages
    handlers/            # HTTP handlers (40+ handler modules)
      project_handler.go
      item_handler.go
      link_handler.go
      agent_handler.go
      search_handler.go
      graph_handler.go
      websocket_handler.go
      agent_coordination_handlers.go
      auth_handler.go
      ai_handler.go
      ...
    services/            # Domain services (20+ modules)
    repository/          # GORM repositories
    auth/                # WorkOS SSO, JWT, RBAC
    graph/               # Neo4j integration
    realtime/            # Real-time hub (formerly websocket)
    websocket/           # WebSocket support
    temporal/            # Workflow workers
    agents/              # Agent coordination
    cache/               # Redis + in-memory
    nats/                # NATS event bus
    events/              # Event definitions
    storage/             # S3/MinIO
    codeindex/           # AST parsing (10K+ LOC)
    docindex/            # Documentation indexing
    docservice/          # Document service
    equivalence/         # Equivalence engine (16K+ LOC)
    embeddings/          # Embedding service
    middleware/          # CORS, auth, logging, tracing
    models/              # GORM models (7 model modules)
    validation/          # Input validation
    health/              # Health checks
    metrics/             # Prometheus metrics
    resilience/          # Retry, circuit breaker
    ratelimit/           # Sliding window rate limiter
    pagination/          # Pagination utilities
    traceability/        # Traceability service
    journey/             # User journey tracking
    grpc/                # gRPC service implementations
    database/            # Database setup
    db/                  # DB query builders
    config/              # Config management
    integration/         # Integration tests
    testutil/            # Testing utilities
    ...
```

### Frontend (`frontend/`)

```
frontend/
  apps/
    web/                 # Main SPA (React 19 + Vite)
      src/
        api/             # API client modules (45+ modules)
          client.ts      # Core API client
          items.ts       # Item CRUD client
          links.ts       # Link management client
          projects.ts    # Project client
          graph.ts       # Graph client
          mcp-client.ts  # MCP client
          auth.ts        # Auth client
          ...
        components/      # React components (shadcn/ui + custom)
        routes/          # TanStack Router pages
        stores/          # Zustand state stores
        hooks/           # React hooks (queries, mutations)
        lib/             # Utilities and helpers
        context/         # React context providers
        pages/           # Page components
        router.tsx       # Router configuration
        main.tsx         # Entry point
    docs/                # Fumadocs documentation site
    storybook/           # Component showcase
    desktop/             # Tauri desktop wrapper
  packages/              # Shared packages (monorepo support)
```

---

## Code Conventions

### Python Conventions

- **Line length**: 120 (ruff configured)
- **Type annotations**: Required on all functions (`ty` type checker enforced)
- **Imports**: isort via ruff, absolute imports preferred
- **Models**: SQLAlchemy 2.0 declarative with `Mapped[]` type annotations
- **Schemas**: Pydantic v2 with `model_validator` decorators
- **Async**: `async def` for all API handlers; services may be sync
- **Naming**: snake_case for functions/vars, PascalCase for classes
- **Entry points**: `rtm` (CLI), `rtm-mcp` (MCP server)
- **Logging**: loguru for structured logging
- **Decorators**: FastAPI route decorators in api/routers/; @mcp.tool/@mcp.resource in MCP tools

### Go Conventions

- **Formatting**: gofumpt (stricter than gofmt)
- **Linting**: golangci-lint (.golangci-backend.yml) with 20+ linters enabled
  - Includes: errcheck, govet, revive, gosec, gocyclo, gocognit, dupl, goconst, etc.
  - Run: `cd backend && golangci-lint run`
- **Error handling**: Always check errors, wrap with `fmt.Errorf("context: %w", err)`
- **Models**: GORM structs with `gorm:"..."` tags and `json:"..."` tags
- **Handlers**: Echo context receiver, typed request/response structs
- **Naming**: camelCase for vars/fields, PascalCase for exported funcs/types
- **Testing**: testify for assertions, testcontainers for integration tests
- **Logging**: log/slog (standard library structured logging)

### TypeScript Conventions

- **Framework**: React 19 with React Compiler
- **Routing**: TanStack Router (file-based, type-safe)
- **State**: Zustand stores (no Redux)
- **Server state**: TanStack Query v5
- **Components**: shadcn/ui + Radix UI primitives
- **Styling**: Tailwind CSS
- **Linting**: OxLint (Biome migration in progress)

---

## Implementation Patterns

### Pattern 1: Python Service Layer

Every domain operation goes through a service:

```python
# src/tracertm/services/item_service.py
class ItemService:
    def __init__(self, repo: ItemRepository, event_repo: EventRepository):
        self.repo = repo
        self.event_repo = event_repo

    async def create_item(self, project_id: str, data: ItemCreateSchema) -> Item:
        item = Item(**data.model_dump(), project_id=project_id)
        await self.repo.create(item)
        await self.event_repo.emit("item.created", item.id)
        return item
```

### Pattern 2: Go Handler + Service

```go
// backend/internal/handlers/item_handler.go
func (h *ItemHandler) CreateItem(c echo.Context) error {
    var req CreateItemRequest
    if err := c.Bind(&req); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, err.Error())
    }
    item, err := h.service.CreateItem(c.Request().Context(), req)
    if err != nil {
        return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
    }
    return c.JSON(http.StatusCreated, item)
}
```

### Pattern 3: MCP Tool Registration

FastMCP (not raw MCP library) with shared `mcp` instance from `core.py`:

```python
# src/tracertm/mcp/tools/items.py
from tracertm.mcp.core import mcp

@mcp.tool(description="Create a new traceability item in a project")
async def create_item(
    project_id: str,
    title: str,
    item_type: str = "requirement",
    description: str = "",
) -> dict:
    """Create a new traceability item."""
    # Tool implementation uses get_session() from base_async.py
    session = await get_mcp_session()
    item = Item(
        project_id=project_id,
        title=title,
        item_type=item_type,
        description=description
    )
    session.add(item)
    await session.commit()
    return {"id": item.id, "title": item.title, "status": item.status}
```

**Key patterns:**
- Decorator: `@mcp.tool(description="...")` on async function
- Import: `from tracertm.mcp.core import mcp` (singleton instance)
- Tools split across 20 modules for faster loading
- Return dicts, not Pydantic models (MCP constraint)

### Pattern 4: CLI Command

```python
# src/tracertm/cli/commands/item.py
import typer
from rich.console import Console
from tracertm.cli.ui.components import console

app = typer.Typer()

@app.command()
def create(
    title: str,
    project: str = typer.Option(None, "--project", "-p", help="Project ID"),
    item_type: str = typer.Option("requirement", "--type", "-t", help="Item type"),
) -> None:
    """Create a new traceability item."""
    try:
        svc = get_item_service()
        item = svc.create_item_sync(project, title, item_type)
        console.print(f"[green]✓ Created item {item.id}[/green]")
    except Exception as e:
        console.print(error_panel(f"Failed to create item: {e}"))
        raise typer.Exit(1)

# Register in src/tracertm/cli/app.py
# app.add_typer(item_app, name="item", help="Item management")
```

**Key patterns:**
- Import: `from tracertm.cli.app import app` (singleton)
- Commands registered in `app.py` main CLI factory
- Use `rich.console.Console` for formatted output
- Return type hint: `-> None`
- Error handling with rich panels

### Pattern 5: Event Emission (NATS)

```python
# All state changes emit events
await event_repo.emit("item.created", {
    "item_id": item.id,
    "project_id": project_id,
    "type": item.type,
    "timestamp": datetime.utcnow().isoformat(),
})
```

### Pattern 6: Graph Query (Hybrid)

```python
# Simple query: PostgreSQL CTE
items = await repo.get_descendants(item_id, max_depth=5)

# Complex analysis: NetworkX
import networkx as nx
G = nx.DiGraph()
# ... build graph from DB ...
cycles = list(nx.simple_cycles(G))
critical_path = nx.dag_longest_path(G)
```

```go
// Performance-critical: Go custom algorithm
func (s *GraphService) FindShortestPath(ctx context.Context, from, to string) ([]string, error) {
    // BFS with early termination
    // ...
}
```

---

## Key Integration Points

### Python <-> Go Communication

```
Python FastAPI --> gRPC --> Go Echo
                           |
                           +--> Graph algorithms
                           +--> Bulk import processing
                           +--> Token bridge (cost optimization)
```

Protobuf definitions: `proto/` directory
gRPC services: `src/tracertm/grpc/` and `backend/internal/grpc/`

### Database Migrations

```bash
# Python (Alembic)
alembic upgrade head
alembic revision --autogenerate -m "Add new table"

# Go (Atlas or raw SQL)
# Schema in backend/schema.sql
```

### Running the Dev Stack

The project uses **native services** (no Docker required for dev) managed via **process-compose**.

```bash
# Start all services
make dev

# Check service status
process-compose status

# Individual services (with hot reload)
process-compose up python-api    # FastAPI on :8000
process-compose up go-api        # Echo API on :3000
process-compose up frontend      # Vite dev server on :5173

# Stop services
process-compose down

# View logs
process-compose logs -f python-api
```

**Prerequisites:**
- PostgreSQL (local)
- Redis (local)
- NATS (local)
- Go 1.23+
- Python 3.12+
- Node.js 20+ / Bun

**Environment Setup:**
- Copy `.env.example` to `.env` (if needed)
- Database auto-migrates on startup (Alembic)
- Preflight checks in `src/tracertm/preflight.py` validate dependencies

---

## File Modification Guide

### Adding a New API Endpoint

**Python:**
1. Add schema in `src/tracertm/schemas/`
2. Add service method in `src/tracertm/services/`
3. Add router in `src/tracertm/api/routers/`
4. Register router in `src/tracertm/api/main.py`
5. Add tests in `tests/api/`

**Go:**
1. Add request/response types in `backend/internal/models/`
2. Add service method in `backend/internal/services/`
3. Add handler in `backend/internal/handlers/`
4. Register route in `backend/internal/server/routes.go`
5. Add tests in `backend/internal/handlers/*_test.go`

### Adding a New MCP Tool

1. Create tool function in `src/tracertm/mcp/tools/` (one of 20 domain modules)
   - Example: `src/tracertm/mcp/tools/items.py`
2. Use `@mcp.tool(description="...")` decorator (imports `mcp` from `core.py`)
3. Function signature must match FastMCP expectations:
   - Async function with clear parameters
   - Return dict (not Pydantic models)
   - Use TypedDict for complex parameter types
4. Tool module auto-loads from `src/tracertm/mcp/tools/_load.py`
5. Add tests in `tests/mcp/` (for critical tools)

### Adding a New CLI Command

1. Create command module in `src/tracertm/cli/commands/`
   - Example: `src/tracertm/cli/commands/item.py`
2. Use Typer decorator: `@app.command()`
   - Import `Console` from `rich`
   - Use `typer.Option()` for flags
3. Register in `src/tracertm/cli/app.py`:
   - `app.add_typer(item_app, name="item", help="...")`
4. Entry point: `rtm` CLI via `src/tracertm/cli/__main__.py`
5. Add tests in `tests/cli/`

### Adding a New Frontend View

1. Create route in `frontend/apps/web/src/routes/` (TanStack Router)
   - File-based routing: `routes/items.tsx` -> `/items`
2. Create components in `frontend/apps/web/src/components/`
   - Use shadcn/ui + Radix UI primitives
   - Prop types via TypeScript interfaces
3. Add Zustand store if needed in `frontend/apps/web/src/stores/`
   - Client state only (not server state)
4. Add TanStack Query hooks in `frontend/apps/web/src/hooks/`
   - Server state via hooks (`useQuery`, `useMutation`)
   - API client in `src/api/`
5. Add to Storybook in `frontend/apps/storybook/`
   - Component showcase and test harness
6. Add tests:
   - Unit: Vitest for components, hooks, utilities
   - E2E: Playwright for critical user workflows

---

## Quality Checklist

### Before Submitting Code

**Python:**
- [ ] `ruff check src/tracertm/` passes (0 violations)
  - Command: `ruff check src/tracertm/ --fix` (auto-fix most)
- [ ] `ty check src/tracertm/` passes (0 type errors)
  - Type checker enforces function annotations
- [ ] All new functions have type annotations
  - Parameter types and return types required
- [ ] No bare suppressions (ruff/ty comments require justification)

**Go:**
- [ ] `go fmt ./...` passes (or `gofumpt -w .`)
- [ ] `cd backend && golangci-lint run` passes
  - Runs 20+ linters (errcheck, gosec, gocyclo, dupl, etc.)
- [ ] Error handling: all errors checked/wrapped
- [ ] GORM models: all fields have `gorm:""` and `json:""` tags

**Frontend:**
- [ ] `bunx oxlint` passes (TypeScript linter)
- [ ] React components have proper prop types
- [ ] TanStack Query hooks used for server state
- [ ] Zustand stores for client state only

**Integration:**
- [ ] **Tests**: All relevant tests pass
  - Unit: services, utilities
  - Integration: API endpoints, database operations
  - E2E: critical user workflows
- [ ] **Coverage**: New code has tests (target: 80-90%)
  - Services: 100% coverage (business logic)
  - Handlers: 80%+ coverage (error paths)
  - Utilities: 90%+ coverage

**Features:**
- [ ] **API**: Endpoints documented (OpenAPI auto-gen)
  - FastAPI routes auto-documented from docstrings
- [ ] **Events**: State changes emit NATS events
  - Use `EventRepository.emit()` for all mutations
- [ ] **MCP**: New features have MCP tool equivalents
  - Tools in `src/tracertm/mcp/tools/`
  - Register with `@mcp.tool()` decorator
- [ ] **CLI**: Complex features have CLI commands
  - Commands in `src/tracertm/cli/commands/`
  - Register in `app.py`

**Code Quality:**
- [ ] No dead imports (ruff F401)
- [ ] No unused variables (ruff F841)
- [ ] No placeholder TODOs (comment should explain next step)
- [ ] Max function length: 40 lines (guidelines, not hard limit)
- [ ] Max cyclomatic complexity: 10 per function
