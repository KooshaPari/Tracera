---
repo: "Tracera"
aliases: ["tracera-server", "tracera-edge"]
status: "active"
last_verified: "2026-09-20"
owner: "kooshapari"
build_deploy_status: "in_progress — see Long-term paths below"
---

# CVP — Tracera

## Identity

Tracera is a **trace-link matrix and observability ledger** for agentic and
LLM workflows. It captures structured trace-links across runs, distills
short-term and long-term memory from session history, and serves an audit
ledger the user (or another agent) can replay. The thing it does that
generic observability does not is **cross-run reasoning**: "if I change
this spec, what breaks across the last 30 agent runs that touched it?"

If you swapped Tracera for a generic log aggregator or APM tool, the user
loses the cross-run dependency view and the memory distillation. Those two
capabilities _are_ Tracera.

## Closest Viable Product

The Tracera CVP is **one user, one machine, one durable workspace, where
the user can**:

1. Capture a session trace (input → tool calls → output) into the local
   store.
2. See the trace-link graph: which sessions depended on which specs,
   prompts, or prior sessions.
3. Cross-reference a node ("if I delete this spec, what breaks?") and get
   a real answer derived from the local trace-link graph.
4. Distill the last N sessions into a stable long-term memory entry the
   next session can load as context.
5. Run it all locally on a single user's machine with no third-party API
   dependency, then optionally publish the workspace to a shared URL
   behind Cloudflare Access. (Cloudflare Edge Worker + Tunnel are used
   only as infrastructure for fleet discovery and public sharing — they
   are not application APIs.)

Everything else (multi-tenant auth, billing, graph analytics, OnCall
integrations, ML inference pipelines, etc.) is post-CVP.

## In CVP (must ship in this slice)

- **Local-first Rust server** (`crates/tracera-server/`). 93 routes already
  implemented; the CVP requires a working subset.
  - Health, ready, metrics endpoints (live).
  - `POST /api/v1/trace` and trace-link graph traversal.
  - `POST /api/v1/impact` / `confidence` / `blast-radius`.
  - Session ingest (manual paste or local agent).
  - Memory distillation API surface (`/api/v1/memory/...`).
- **Local SQLite store** for trace-links + memory (`crates/tracera-server/src/sqlite_store/`).
  No external DB dependency for CVP.
- **Web frontend** (`frontend/apps/web/`) talking to the local Rust server
  via the configured `VITE_API_URL` (default `http://127.0.0.1:18000`).
- **Cloudflare Edge Worker** (`crates/tracera-edge/`). The CVP uses the edge
  worker for:
  - Fleet enrollment handshake (`/fleet/enroll`).
  - Liveness proxy for the local Rust server through Cloudflare Tunnel.
- **Fleet layer** (`crates/tracera-server/src/sidecar/` or `bin/fleet-sidecar`).
  One enrolled local node is enough for CVP. Multi-node orchestration is
  post-CVP.
- **Electrobun desktop viewer** (`crates/tracera-tauri/` + `desktop/`).
  Bundles the local server + UI as a single downloadable artifact for
  users who don't want to run the Rust server manually. **In-scope**
  for the CVP release — desktop is the primary install surface for
  non-developer users.

## Post-CVP (defer until CVP is live)

These are explicitly out of the CVP slice:

- Multi-tenant WorkOS auth (single-user local is enough).
- Cloud D1/R2 for persistence (SQLite is enough).
- ML inference pipelines (`crates/tracera-ml/`, Neo4j adapter, RAG).
- Multi-node fleet orchestration (`crates/tracera-cli/`, `tracera-go-cli/`).
- GitHub/Jira/AgilePlus ingestion (`crates/tracera-server/src/ingest/`).
  These become the next CVP after this one ships.
- The phenodag queue absorption surface (gated behind the `phenodag-queue`
  feature flag).
- Custom-domain Tracera hosting on pheno.studio (the CVP can publish via
  Cloudflare Tunnel, but branded multi-tenant hosting is post-CVP).

## Anti-CVPs

Things that look like they belong in the Tracera CVP but don't, and where
they actually live:

| Looks like Tracera CVP     | Actually lives in        | Why                                                                                 |
| -------------------------- | ------------------------ | ----------------------------------------------------------------------------------- |
| Cross-team sprint planning | `AgilePlus`              | Tracera observes _what was done_; it does not plan _what to do_.                    |
| Code-search over source    | `HeliosLab`              | Tracera indexes traces, not source files.                                           |
| Generic agent runtime      | `agentmcp` / `AgentMCP`  | Tracera is a _trace store_, not a runtime.                                          |
| Audit log streaming        | `PhenotypeApps`          | Tracera's audit is per-workspace, not per-org.                                      |
| MCP server host            | `tracera-mcp` (post-CVP) | The CVP exposes tools via local IPC; the MCP server is a remote interface post-CVP. |

## Build-deploy status

As of 2026-09-20:

- **Frontend**: live on Vercel.
  (`Deploy Tracera to Vercel` workflow → `tracera-j9n7ramax-koosha-paridehpours-projects.vercel.app` — that workflow's CI checks are green.)
- **API tier**: Vercel same-origin catch-all router (`api/[...path].ts`)
  serving 41 stub endpoints. Acts as the proxy target until the live
  Rust-backed path comes online.
- **Rust server**: code complete (83 .rs files, 93 routes), builds locally.
  Not currently deployed; runs on `homelab-koosh` for development.
- **Fleet layer**: enrollment + reporting live; one node enrolled.
- **Cloudflare edge**: Worker deployed at `tracera-edge-dev.kooshapari.workers.dev`.

The CVP "ship" state is reached when the Rust server is reachable through
`https://tracera.pheno.studio/api` via Cloudflare Tunnel, the Vercel
catch-all proxies to it, and the live data path returns real (not stubbed)
data. That work is the next blocker.

## Long-term paths (executed 2026-09-20)

To not block on the slow CI loop, the following foundational work was done
in parallel:

1. **CVP, intent, boundary docs** in `phenotype-registry`. The placeholders
   in `docs/intent/Tracera.md` and `docs/boundary/Tracera.md` are now
   filled with the actual Tracera scope.
2. **Proxy-or-stub mode** in `api/[...path].ts`. When `TRACERA_BACKEND_URL`
   env is set on Vercel, the catch-all forwards the request to the live
   Rust server. Otherwise returns stubs. Same-origin frontend keeps working
   in either mode.
3. **Repo-root debt cleanup**. Tracked debug files removed; `.gitignore`
   expanded.
4. **`.env.production` route-count comment** corrected (501 → 41, the
   consolidated catch-all number).

These moves do not require the build-deploy to land and shrink the
critical path when it does.

## Open Questions

- **Memory distillation model**: which distillation strategy is canonical
  for the CVP? `crates/tracera-server/src/memory/distillation/` has
  pattern-based and graph-input strategies. CVP probably ships with
  pattern-based only.
- **Cloudflare Tunnel auth**: Access policy for the public tunnel URL.
  Bypass for self? Auth required for shared workspaces? Decide before
  the first non-developer test.

## Change Log

| Date       | Change                                              | Worklog   |
| ---------- | --------------------------------------------------- | --------- |
| 2026-09-20 | Initial CVP, status = active (build-deploy pending) | this file |
