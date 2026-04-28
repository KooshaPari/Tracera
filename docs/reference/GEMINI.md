# Gemini Agent Governance

This document mirrors the core coordination rules found in `CLAUDE.md` and `AGENTS.md`.

## Shared Actor Coordination (CRITICAL)

Assume many isolated/uncommunicating actors (other agents or the user) are working in the same workspace.

### 1. Command Debouncing & Locking
- High-impact commands (e.g., `make lint`, `make test`, `make quality`) are wrapped in a locking mechanism (`scripts/shell/smart-command.sh`).
- **Check Before Run**: Before executing a heavy command, check for existing locks in `.process-compose/locks/`.
- **Wait or Skip**: If a command is already running, wait for it to finish or skip your redundant call and use its results if possible.

### 2. Process-Compose Awareness
- **Hot Reload Enabled**: All core services (Go backend, Python backend, Frontend) are running under `process-compose` with hot-reload enabled.
- **DO NOT Start Services Individually**: Avoid running scripts like `scripts/shell/start-go-backend.sh` directly.
- **Service Interaction**:
    - Use `make dev-status` to check service health.
    - Use `make dev-restart SERVICE=<name>` to restart a specific service if it hangs.
    - Use `make dev-logs-follow SERVICE=<name>` to debug.

### 3. Consolidated Commands
- **Prevent Naming Explosion**: Do not create new specific test or lint targets in the `Makefile` for every sub-task.
- **Prefer Unified Targets**: Use `make test`, `make lint`, or `make quality`. These are optimized to share resources and provide consolidated feedback.

## Quality Enforcement
- **Opinionated Styling**: Follow the project's strict linting and formatting rules.
- **No Silencing**: Do not use `nolint` or `ignore` comments. Fix the root cause.
- **Native Over Docker**: Prefer native tools and services. Use Docker only if explicitly requested.

## Documentation Organization
- **No Root Markdown**: Do not create `.md` files in the project root.
- **Proper Subdirectories**: Place all new documentation in `docs/` (e.g., `docs/guides/`, `docs/reports/`, `docs/reference/`).
