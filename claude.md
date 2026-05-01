# CLAUDE.md — Tracera

## Project Overview

**Name**: Tracera
**Purpose**: Agent-native, multi-view requirements traceability and project management system
**Language**: Python 3.13+ (FastAPI backend) + TypeScript/React 19 (frontend)
**Status**: Active — recovering from partial clone state
**Remote**: `Tracera/` partial clone (blobless, no `.py` sources); `Tracera-recovered/` has real sources

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.13+, FastAPI, SQLAlchemy 2.0 (async), Pydantic 2 |
| gRPC | grpcio, protoc |
| Workflow | Temporal, NATS |
| Graph DB | Neo4j |
| Cache | Redis |
| Observability | OpenTelemetry, Prometheus, Structlog |
| Auth | WorkOS |
| MCP | fastmcp 3.0+ |
| Frontend | React 19, TypeScript, TanStack Router, Zustand, Radix UI |
| Package manager | uv (Python), bun (frontend) |

## Project Structure

```
src/tracertm/       # Python package (main source)
├── api/             # FastAPI routes
├── services/        # Business logic
├── repositories/    # Data access
├── storage/         # File/markdown handling
├── mcp/             # MCP server tools
├── agent/           # Agent coordination
├── tui/             # Textual TUI
├── grpc/            # gRPC service
├── workflows/       # Temporal workflows
└── observability/   # Tracing/metrics

frontend/            # React monorepo (turbo)
backend/             # Go API stub
tests/               # pytest suite (unit/integration/e2e)
alembic/             # DB migrations
scripts/             # Dev & seed scripts
```

## Development

### Python setup
```bash
uv sync
pytest                    # run tests
pytest -m unit            # unit only
pytest -m integration     # integration only
ruff check . && ruff format .
ty check src/
```

### Frontend
```bash
bun install
bun run dev
```

### Quality gates
```bash
poe quality   # full: ruff + ty + tach + bandit + pip-audit + pytest
poe test      # pytest
poe lint      # ruff check --fix
```

## Quality Gates

- All tests must pass (`pytest`)
- All lints must pass (`ruff check`, `ty check`)
- No suppressions without inline justification
- Max function: 40 lines, max complexity: 10
- No placeholder TODOs in committed code

## Governance References

- **Parent governance**: `/Users/kooshapari/CodeProjects/Phenotype/repos/CLAUDE.md`
- **Global governance**: `/Users/kooshapari/.claude/CLAUDE.md`
- **Local agents**: See `AGENTS.md`
