# TracerTM Agent Handbook

## Kilo Gastown Integration

This repository is a **rig** in Kilo Gastown.

- **Rig ID**: `9614f3ef-45c8-4bdc-bdf2-906899b5f052`
- **Town**: `78a8d430-a206-4a25-96c0-5cd9f5caf984`
- **Worktree Branch**: `convoy/methodology-trace/a8883763/head`

### Work Delegation

Use `gt_sling` and `gt_sling_batch` for delegating work to other agents in the rig:

```bash
gt_sling <bead_id> <agent_id>  # Delegate single bead
gt_sling_batch <bead_ids> <agent_id>  # Delegate multiple beads
```

---

## Project Overview

**TracerTM** is an agent-native, multi-view requirements traceability and project management system.

### Stack

| Layer | Technology |
|-------|------------|
| Backend API | Go |
| Python Services | FastAPI, SQLAlchemy, Pydantic |
| Frontend | React 19, TypeScript, TanStack Router, Zustand |
| Relational DB | PostgreSQL 17+ |
| Graph DB | Neo4j 5.0+ |
| Cache | Redis 7+ |
| Messaging | NATS 2.9+ |
| Workflow Engine | Temporal |
| Observability | Prometheus, Loki, Jaeger |

### Architecture

```
frontend/          # React/TypeScript SPA
backend/           # Go API server (separate repo)
src/tracertm/      # Python services & CLI
├── api/           # FastAPI routes
├── services/      # Business logic
├── repositories/  # Data access
├── storage/       # File/markdown handling
├── mcp/           # MCP server tools
├── agent/         # Agent coordination
└── tui/           # Textual TUI
```

---

## Development Commands

### Python (Primary)

```bash
# Install dependencies
task install        # or: uv sync

# Run tests
pytest              # or: task test
pytest -m unit      # unit tests only
pytest -m integration  # integration tests

# Lint & format
ruff check . && ruff format .
ty check src/       # type checking

# Quality gates (full)
task quality

# Database migrations
task db:migrate
task db-rollback
```

### Frontend

```bash
cd frontend

bun run dev         # Start dev server
bun run build       # Production build
bun run lint        # ESLint
bun run typecheck   # TypeScript check
bun test            # Vitest tests
```

### Go Backend

```bash
go test ./...
go build ./...
golangci-lint run
```

### All Services (TUI Dashboard)

```bash
task dev:tui        # Start all services with interactive TUI
task dev            # Standard dev mode
```

---

## Key Files

| Path | Purpose |
|------|---------|
| `pyproject.toml` | Python package config, pytest/ruff settings |
| `Taskfile.yml` | Task automation |
| `Makefile` | Naming convention checks |
| `frontend/package.json` | Frontend dependencies |
| `src/tracertm/` | Main Python source |
| `tests/` | Test suite |

---

## Quality Gates

Before committing, ensure:

1. `pytest` - All tests pass
2. `ruff check .` - No lint errors
3. `ruff format --check .` - Code properly formatted
4. `ty check src/` - Type annotations valid

---

## Environment Setup

```bash
# Prerequisites
go 1.21+, python 3.13+, node/bun
postgresql 17+, redis 7+, neo4j 5.0+, nats 2.9+
task (taskfile.dev), process-compose

# First run
task install
task db:migrate
task dev:tui
```

Access services at `http://localhost:4000` (Gateway), `http://localhost:3000` (Grafana), `http://localhost:16686` (Jaeger).
