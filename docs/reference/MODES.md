# TraceRTM Modes (MCP, CLI, Hybrid)

TraceRTM supports three independent usage modes. None of them require the others.

## 1) MCP-only (agent-native)

Use MCP as the sole interface for agents (Claude/Codex/etc.).

- Entry: `scripts/mcp/tracertm_mcp_server.py` (FastMCP server)
- Storage: configured database (Postgres or SQLite)
- Config: per-user in `~/.tracertm/config.yaml` (or `TRACERTM_DATABASE_URL` env var)

Typical flow:
1. Start MCP server
2. Agent calls MCP tools (projects/items/links/traceability)
3. No CLI required

## 2) CLI-only (offline-first)

Use the local CLI and file watcher with no MCP running.

- Entry: `rtm` (Typer CLI)
- Storage: per-project `.trace/` + per-user `~/.tracertm/`
- Sync: optional (only if you configure API)

Typical flow:
1. `rtm init` creates `.trace/` in a repo
2. `rtm watch` indexes changes into local SQLite
3. Work entirely offline

## 3) Hybrid (MCP + CLI)

Run CLI for local workflows and MCP for agent workflows, sharing the same config.

- Shared config: `~/.tracertm/config.yaml`
- Shared DB: SQLite or Postgres
- Shared project state: `.trace/` for local project artifacts

Typical flow:
1. CLI manages local content
2. MCP agents query/update the same DB
3. Optional sync pushes/pulls to remote API

---

## Storage Contract (short)

- **Per-user (system)**: `~/.tracertm/`
  - `config.yaml`, `tracertm.db`, sync queue, conflict backups
- **Per-project (git)**: `.trace/`
  - committed markdown items + `.meta/links.yaml`
  - local-only `.meta/sync.yaml` should be gitignored

See `src/tracertm/storage/README.md` for the full offline-first storage model.

## Auth Notes

- MCP can run unauthenticated (local/dev) or with AuthKit (production).
- CLI uses device login (`rtm auth login`) to store an API token in `~/.tracertm/config.yaml`.
