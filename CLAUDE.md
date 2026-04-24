# TracerTM - CLAUDE.md

## Project Overview

**TracerTM** is an agent-native, multi-view requirements traceability and project management system. It enables tracking of requirements across the software development lifecycle with tight integration into Kilo Gastown for multi-agent orchestration.

- **Rig ID**: `9614f3ef-45c8-4bdc-bdf2-906899b5f052`
- **Town**: `78a8d430-a206-4a25-96c0-5cd9f5caf984`
- **Branch**: `convoy/methodology-trace/a8883763/head`

## Stack

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
| Observability | Prometheus, Loki, Grafana Alloy, Tempo |

## Architecture

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

## Code Conventions

### Python (Primary)

- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`
- **Type checking**: `ty check src/`
- **Testing**: `pytest` (unit: `pytest -m unit`, integration: `pytest -m integration`)
- **Quality gates**: `task quality`

### Frontend

- Use `bun` instead of `npm` for all package management
- Commands: `bun run dev`, `bun run build`, `bun run lint`, `bun test`

### Key Files

| Path | Purpose |
|------|---------|
| `pyproject.toml` | Python package config, pytest/ruff settings |
| `Taskfile.yml` | Task automation |
| `Makefile` | Naming convention checks |
| `frontend/package.json` | Frontend dependencies |
| `src/tracertm/` | Main Python source |
| `tests/` | Test suite |

### Code Quality Non-Negotiables

- Zero new lint suppressions without inline justification
- All new code must pass: `ruff check`, `ty check`, tests
- Max function: 40 lines. Max cognitive complexity: 15
- No placeholder TODOs in committed code
- Hook-backed enforcement for complexity and imports

### Library Preferences

| Need | Use | NOT |
|------|-----|-----|
| Retry/resilience | tenacity | Custom retry loops |
| HTTP client | httpx | Custom wrappers |
| Logging | loguru + structlog | print() or logging.getLogger |
| Config | pydantic-settings | Manual env parsing |
| CLI | typer | argparse |
| Validation | pydantic | Manual if/else |
| Database ORM | SQLAlchemy (async) | Raw SQL strings |
| API framework | FastAPI + uvicorn | Flask / custom ASGI |
| MCP tools | fastmcp | Custom MCP protocol handling |
| Workflow orchestration | temporalio | Custom job queues |

## Agent Behavior Rules

### Work Delegation

Use `gt_sling` and `gt_sling_batch` for delegating work to other agents:

```bash
gt_sling <bead_id> <agent_id>  # Delegate single bead
gt_sling_batch <bead_ids> <agent_id>  # Delegate multiple beads
```

### Context Management

**Manager Pattern**: Operate as a strategic manager, not a worker. Delegate to subagents.

**Keep in Main Context**:
- User intent and requirements
- Strategic decisions and trade-offs
- Summaries of completed work
- Critical architectural knowledge

**Delegate to Subagents**:
- File exploration (>3 files)
- Pattern searches across codebase
- Multi-file implementations
- Long command sequences
- Test execution

### Development Commands

```bash
# Install dependencies
task install        # or: uv sync

# Run tests
pytest              # or: task test

# Lint & format
ruff check . && ruff format .

# Type checking
ty check src/

# Quality gates (full)
task quality

# Database migrations
task db:migrate
task db-rollback

# All Services (TUI Dashboard)
task dev:tui        # Start all services with interactive TUI
task dev            # Standard dev mode
```

### Dev Environment Rules

- **The user runs `make dev-tui`** in their own terminal as the primary observation dashboard
- **Never** run `make dev`, `make dev-tui`, or `make dev-down` — those are user-only commands
- **Hot reload** handles code changes — do not restart services just because you edited code
- **Config/env changes** require restart of affected service only

### CLI Commands for Introspection

| Action | Command |
|--------|---------|
| Check all service health | `make dev-status` |
| Restart one service | `make dev-restart SERVICE=go-backend` |
| Tail logs (all) | `make dev-logs` |
| Tail logs (one service) | `make dev-logs SERVICE=python-backend` |

### Quality Gates (Pre-Commit)

1. `pytest` - All tests pass
2. `ruff check .` - No lint errors
3. `ruff format --check .` - Code properly formatted
4. `ty check src/` - Type annotations valid

### Worktree Discipline

- Feature work goes in `.worktrees/<topic>/`
- Legacy `PROJECT-wtrees/` and `repo-wtrees/` roots are for migration only
- Canonical repository remains on `main` for final integration

### Governance

- Worktree discipline, reuse protocol, git delivery, stability, CI, child-agent delegation
- Source: `KooshaPari/thegent` -> `templates/claude/governance-blocks/`
- Reference the source instead of duplicating blocks

### Child Agent Usage

- Use child agents liberally for discovery-heavy, migration-heavy, and high-context work
- Delegate broad scans, decomposition, and implementation waves to subagents
- Keep the parent lane focused on deterministic integration and finalization
- Preserve explicit handoffs and cross-agent context in session notes and audits

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

Access services at `http://localhost:4000` (Gateway) and `http://localhost:3000` (Grafana/Tempo).
