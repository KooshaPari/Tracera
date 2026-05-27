# Tooling Reference

This document is the quick reference for local development in TraceRTM.

TraceRTM is a Python-first monorepo with a small amount of frontend and Go support:

- Python lives under `src/tracertm/` and is the primary application surface.
- The frontend is a Bun-managed workspace under `frontend/`.
- Infrastructure is driven by `docker-compose.yml` and `docker-compose.prod.yml`.
- Shared developer commands are exposed through `Taskfile.yml` and the root `package.json` scripts.

---

## 1. Overview

The default dev stack is a local multi-service environment for the Python API, Go API, and supporting infrastructure:

- `python-backend` for the FastAPI-based Python service.
- `go-backend` for the Go service.
- `nginx` as the local gateway.
- `postgres` for relational storage.
- `dragonfly` as the Redis-compatible cache.
- `nats` for messaging.
- `prometheus` and `grafana` for monitoring.
- Exporters for nginx, postgres, and cache metrics.

The repo also contains a production-like compose stack in `docker-compose.prod.yml` that adds:

- `neo4j`
- `minio`

That file is closer to the full deployment surface, while `docker-compose.yml` is the standard local development stack.

---

## 2. CLI Commands

The repository exposes the most common workflows through `package.json` scripts, which mostly forward to `make` targets.

Note: the checked-in makefiles are split. The root [`Makefile`](../Makefile) currently only defines `lint-naming`, and [`Makefile.gateway`](../Makefile.gateway) carries the gateway-specific operational targets such as `test`, `config-test`, and `config-reload`. The `package.json` script names are still useful as the intended command surface, but some of them forward to make targets that are not defined in the root makefile in this checkout. In particular, there is no root `make quality` target in the current tree.

### Root `package.json`

| Command | Purpose |
|---|---|
| `bun run dev` | Start the full dev stack |
| `bun run dev:tui` | Start the interactive TUI-based dev mode |
| `bun run dev:down` | Stop the dev stack |
| `bun run dev:logs` | Tail dev logs |
| `bun run dev:status` | Show dev stack status |
| `bun run quality` | Run the quality gate |
| `bun run check` | Run repo checks |
| `bun run lint` | Run frontend linting |
| `bun run lint:all` | Run repo-wide linting |
| `bun run type-check` | Run repo-wide type checking |
| `bun run format` | Run formatting |
| `bun run test` | Run repo-wide tests |
| `bun run test:frontend` | Run frontend tests |
| `bun run test:python` | Run Python tests |
| `bun run test:go` | Run Go tests |
| `bun run test:integration` | Run integration tests |
| `bun run db:migrate` | Apply database migrations |
| `bun run db:rollback` | Roll back the last migration |
| `bun run db:reset` | Reset the database |
| `bun run db:shell` | Open a database shell |

### `Makefile`

The checked-in root `Makefile` currently only defines the naming check:

| Command | Purpose |
|---|---|
| `make lint-naming` | Run naming-consistency checks for Python, Go, and frontend code |

### `Makefile.gateway`

The gateway makefile is separate from the root build/test surface:

| Command | Purpose |
|---|---|
| `make test` | Run the gateway test suite |
| `make config-test` | Validate nginx configuration |
| `make config-reload` | Reload nginx configuration |
| `make cache-clear` | Clear the nginx cache and restart the gateway |
| `make db-backup` | Run the gateway backup flow |

### `Taskfile.yml`

The bulk of the repo-wide automation lives in `Taskfile.yml`:

| Task | Purpose |
|---|---|
| `task build` | Build detected Python, Go, and Bun workspaces |
| `task build:python` | Build the Python package with `uv build` |
| `task build:go` | Build Go modules |
| `task build:bun` | Build the Bun workspace when present |
| `task test` | Run all detected test suites |
| `task test:python` | Run Python tests with `uv run pytest` |
| `task test:go` | Run Go tests |
| `task test:bun` | Run Bun workspace tests |
| `task lint` | Run lint and format checks across Python, Go, and Bun |
| `task lint:python` | Run Ruff lint and format checks |
| `task lint:go` | Run `gofmt` verification and `go vet` |
| `task lint:bun` | Run Bun lint and type checks |
| `task clean` | Remove common build and test artifacts |

### Practical command shortcuts

Use these when you want the shortest path to a specific workflow:

```bash
bun run dev
bun run test:python
bun run test:frontend
bun run quality
task lint
task test
```

---

## 3. Docker Compose

### Default dev stack: `docker-compose.yml`

This is the normal local stack.

| Service | Role |
|---|---|
| `nginx` | Local API gateway |
| `nginx-exporter` | Nginx metrics exporter |
| `go-backend` | Go backend service |
| `python-backend` | Python backend service |
| `postgres` | PostgreSQL database |
| `postgres-exporter` | PostgreSQL metrics exporter |
| `dragonfly` | Redis-compatible cache |
| `redis-exporter` | Cache metrics exporter |
| `nats` | Message broker |
| `prometheus` | Metrics collection |
| `grafana` | Dashboards and observability |

### Production-like stack: `docker-compose.prod.yml`

This file extends the stack with the broader infra surfaces used by the repo:

| Service | Role |
|---|---|
| `postgres` | PostgreSQL 17 data store |
| `dragonfly` | Redis-compatible cache |
| `nats` | Messaging |
| `go-backend` | Go backend |
| `python-backend` | Python backend |
| `nginx` | Gateway |
| `neo4j` | Graph database |
| `minio` | Object storage |
| `grafana` | Dashboards |

### Notes

- The compose files use `dragonfly` rather than a native `redis` container for the cache layer.
- If you are looking for the graph and object-storage dependencies mentioned in higher-level planning docs, they are present in `docker-compose.prod.yml`, not in the default dev compose file.

---

## 4. MCP Server

TraceRTM does have an MCP package under `src/tracertm/mcp/`, but it is designed to run as part of the backend, not as a standalone process.

Key points:

- `src/tracertm/mcp/__main__.py` exits with an error if invoked directly.
- The API mounts the MCP router under `/api/v1/mcp`.
- `src/tracertm/mcp/server.py` is the main MCP server entrypoint referenced by the repo docs.
- `docs/reference/MCP_TOOL_REFERENCE.md` is the detailed tool catalog and protocol reference.

Operationally, the rule is:

```bash
# Do not run MCP by itself
python -m tracertm.mcp

# Run the backend/API instead, then use the mounted MCP endpoint
```

If you are extending MCP tooling, work inside `src/tracertm/mcp/` and validate through the backend that mounts it.

---

## 5. Dev Workflow

The fastest iteration loop in this repo is:

1. Make the change in the relevant surface:
   - Python application code in `src/tracertm/`
   - Frontend code in `frontend/`
   - Compose or infra changes in the root compose files
2. Run the narrowest useful check first:
   - `bun run test:python`
   - `bun run test:frontend`
   - `task lint:python`
   - `task lint:bun`
3. Expand to the declared repo-level gate only after the local check passes:
   - `bun run quality`
   - `task test`
   - `task lint`
4. If you touched runtime wiring, restart the affected service rather than the whole stack when possible.
5. Use the logs/status commands to confirm the service actually picked up the change:
   - `bun run dev:status`
   - `bun run dev:logs`

For MCP work specifically, keep changes inside the package and validate through the backend route that exposes the MCP server.

---

## 6. Testing

### Python

```bash
pytest
pytest -m unit
pytest -m integration
```

The repo also wires Python tests through:

```bash
bun run test:python
task test:python
task test
```

### Frontend

```bash
bun test
bun run test:frontend
```

### Cross-stack

```bash
task test
bun run test
```

### Recommended order

When you are iterating locally:

1. Run the nearest unit test target.
2. Run the package-level test target.
3. Finish with the repo-level test or quality gate before handing off.
