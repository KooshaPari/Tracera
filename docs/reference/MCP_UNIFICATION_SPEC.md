# MCP Unification + Auth Spec (TraceRTM)

## Goals
- One MCP server instance for all tools (core + specs + quality).
- Parameterized tool surface for LLM-friendly usage (atoms-style).
- Auth via WorkOS AuthKit with optional dev API keys.
- CLI device login flow for headless auth.
- MCP and CLI fully independent (either can run alone).

## Scope
- Merge `scripts/mcp/tracertm_mcp_server.py` with `src/tracertm/mcp/*`.
- Add parameterized tools alongside legacy tools for compatibility.
- Add AuthKit + dev API key auth on MCP server.
- Add CLI `auth` command group (device flow).

## Tool Surface (Parameterized)
- `project_manage(action, payload)`
- `item_manage(action, payload)`
- `link_manage(action, payload)`
- `trace_analyze(kind, payload)`
- `graph_analyze(kind, payload)`
- `spec_manage(kind, action, payload)`
- `quality_analyze(payload)`
- `config_manage(action, payload)`
- `sync_manage(action, payload)`
- `export_manage(action, payload)`
- `import_manage(action, payload)`
- `ingest_manage(action, payload)`
- `backup_manage(action, payload)`
- `watch_manage(action, payload)`
- `db_manage(action, payload)`
- `agents_manage(action, payload)`
- `progress_manage(action, payload)`
- `saved_queries_manage(action, payload)`
- `test_manage(action, payload)`
- `tui_manage(action, payload)`
- `benchmark_manage(action, payload)`
- `chaos_manage(action, payload)`
- `design_manage(action, payload)`

## Auth Modes
- Frontend pass-through: Bearer token from AuthKit session.
- OAuth (PKCE) for agent clients.
- CLI device flow (AuthKit device authorization).
- Dev API keys via static bearer tokens (dev-only).

## WBS
1. Consolidation
   - Export single `mcp` instance
   - Register spec + param tools
2. Parameterized Tools
   - Implement action/dispatch layer
   - Preserve legacy tools
3. Auth Integration
   - AuthKit provider
   - Static token support
   - Composite verifier
4. CLI Auth
   - `rtm auth login/status/logout`
   - Store token in config
5. API + Frontend MCP Config
   - `/api/v1/mcp/config` endpoint
   - Frontend MCP client helper (Bearer pass-through)
6. Docs + Validation
   - Capability matrix
   - Auth setup docs
   - MCP-only test

## DAG

```
Consolidation ──┬──> Parameterized Tools ──┬──> Capability Matrix
                │                         └──> Validation
                └──> Auth Integration ─────┬──> CLI Auth
                                           └──> Validation
```
