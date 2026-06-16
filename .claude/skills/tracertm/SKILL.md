---
name: tracertm-ops
description: Use this skill for TraceRTM project ops, local service checks, task routing, and development stack diagnostics. Covers Python/Go/frontend/service health, seed/migration flow, and MCP startup for this repo.
---

# Tracera operations skill

## When to invoke
- Use when a task involves environment setup, local runbooks, or cross-service checks in Tracera.
- Use for debugging `rtm`, `tracertm`, MCP connectivity, service health, or task automation failures.
- Use before major workflow changes to ensure Postgres/Redis/Neo4j/NATS/Temporal/MinIO prerequisites are known.

## Repo facts
- **Repo:** `E:/Dev/Tracera`
- **Python package:** `tracertm` (entry points `rtm`, `tracertm`, `tracertm-mcp`)
- **Core CLI file:** `scripts/dev` (Typer app)
- **Task orchestrator:** `Taskfile.yml` + `Taskfile.gateway.yml`
- **MCP reference:** `docs/reference/MCP.md`, `scripts/mcp/claude_desktop_config.json`
- **Service ports (default):** gateway `4000`, python backend `8000`, go backend `8080`, PostgreSQL `5432`, Redis `6379`, Neo4j `7687`, NATS `4222`, MinIO/S3 `9000`.

## First actions
1. Verify branch/task context and current services using `tracertm-doctor` before editing.
2. For infra, run `scripts/dev health` and then `tracertm status` in Task/TUI workflows.
3. Use `tracertm-quality` to align with repo quality expectations.

## Useful command families

### Environment bring-up
- `.env`: create/update via docs, avoid hardcoded credentials in code.
- `scripts/dev init`: scaffold local `.env` and perform health check.
- `task db:migrate`, `task db:rollback`, and migration review when schema changes are in scope.

### Service health
- `scripts/dev health`: checks PostgreSQL/Redis/Neo4j/NATS/Temporal + backend/gateway
- `scripts/dev status`: local process checks and running stack context
- `scripts/dev logs`: tail component logs or `-s` filtered logs

### Execution and quality
- `task install`: install/update dependencies
- `task test` / `pytest` for Python suite
- `task lint`: lint + formatting checks
- `task quality`: repo-wide quality gate

### MCP operations
- `rtm-mcp` or `tracertm-mcp` to start STDIO MCP server
- `rtm mcp tools`, `rtm mcp resources` for visibility of available capabilities
- HTTP endpoint expectations: `http://localhost:4000/mcp` when gateway/API is running

### Frontend/Backend split
- `bun run dev` / `bun run build` / `bun run lint` / `bun run typecheck` from `frontend/`
- `go test ./...` and `go build ./...` in `backend/`

## Common triage patterns
- If startup fails after schema changes: run `task db:migrate`, then restart affected services.
- For MCP auth failures: verify `TRACERTM_MCP_AUTH_MODE` and token strategy from `.env`/shell env, keep secrets outside tracked files.
- For import/type failures in one layer, keep fixes scoped to `src/tracertm/<layer>` and rerun `task quality` only in that area.

## Guardrails
- Do not copy domain or game-specific workflows from unrelated projects.
- Keep `.claude` as process scaffolding only: commands, MCP config, and project-specific agent skills.
- Keep secrets in `.env`; never include tokens or API keys in repo files.
