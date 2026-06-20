# TracerTM - CLAUDE.md

## Overview

TracerTM is an agent-native, multi-view requirements traceability and project management system.

This checkout is primarily a Python `src/` package with supporting frontend and container tooling. The root package entry points are defined in `pyproject.toml`, including `rtm`, `tracertm`, `tracertm-mcp`, and `rtm-mcp`.

## Architecture

- `src/tracertm/`: main Python package
- `src/tracertm/api/`: FastAPI routes, middleware, and HTTP client glue
- `src/tracertm/services/`: business logic and orchestration
- `src/tracertm/repositories/`: data access layer
- `src/tracertm/storage/`: file and markdown handling
- `src/tracertm/mcp/`: MCP server implementation and tools
- `src/tracertm/agent/`: agent coordination, sessions, and sandbox helpers
- `src/tracertm/tui/`: Textual-based terminal UI
- `frontend/`: Bun-based React/TypeScript workspace
- `Taskfile.yml`: repo-wide build, test, lint, and cleanup orchestration
- `.devcontainer/Dockerfile`: development image with Go 1.23, Python 3.11, Node.js 20, Bun, uv, and helper tooling

Notes:

- The repo currently does not have a root `go.mod`; Go tasks in `Taskfile.yml` only act on detected nested modules.
- The package metadata in `pyproject.toml` requires Python `>=3.13`, even though the devcontainer installs Python 3.11.

## Build Commands

Use the task runner first when possible.

```bash
task build
```

Scoped builds:

```bash
task build:python   # uv build when pyproject.toml is present
task build:go       # build any detected Go modules
task build:bun      # bun build for the frontend workspace when available
```

Direct frontend build:

```bash
cd frontend
bun run build
```

## Test Commands

Repo-wide:

```bash
task test
```

Scoped test commands:

```bash
pytest
pytest -m unit
pytest -m integration
task test:python
task test:go
task test:bun
```

Common validation gates:

```bash
task quality
ruff check .
ruff format --check .
ty check src/
```

Frontend validation:

```bash
cd frontend
bun run lint
bun run typecheck
bun test
```

## Branch Discipline

- Use a dedicated branch for every change.
- Prefer `feature/<topic>` for new work and `fix/<topic>` for bug fixes.
- Keep the branch focused on one concern; avoid mixing unrelated edits.
- Do not commit directly to `main`.
- Open a pull request after the change is committed, and expect maintainer review plus CI quality gates.
- Keep commit messages concise and descriptive.
