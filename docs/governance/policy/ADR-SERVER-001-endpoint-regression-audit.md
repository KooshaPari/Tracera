# ADR-SERVER-001: Endpoint regression inventory and tiered recovery plan (Python → Rust migration)

- **Status**: Accepted
- **Date**: 2026-08-21
- **Authors**: KooshaPari (audit performed against `HEAD` of `Tracera`, branch `feat/install-scripts`, SHA `8a22353ed`)
- **Supersedes**: none
- **Related**:
  - [`docs/FEATURE_INVENTORY.md`](../../../docs/FEATURE_INVENTORY.md) — migration safety oracle
  - [`endpoint_traceability_map.md`](endpoint_traceability_map.md) — current governance slice
  - [`coverage_matrix_self_application.md`](coverage_matrix_self_application.md) — control coverage map
  - [Python original (commit `2ece64691f`)](https://github.com/KooshaPari/Tracera/commit/2ece64691f40c11fd6a08f8480ce3b35a8c7395b) — `/src/tracertm/api/routers/`
  - Recovery PRs: `#661`, `#660`, `#677`, `#709`, `#713`, `#717`, `#737`, `#799`

## Context and problem statement

The Tracera service was ported from a Python FastAPI implementation to a native
Rust `axum` implementation in late June 2026 (PR `#677`, commit `30d85f252`,
"feat(server): native tracera-server axum crate, 20 endpoints (rebased)"). The
port shipped with an explicit "20 endpoints" cut from a Python surface of
~100+ endpoints across 22 routers (`src/tracertm/api/routers/`).

Subsequent recovery commits (`#709`, `#713`, `#717`, `#737`, `#799`) restored
Postgres persistence, the ITIL problem-management domain, the GitHub/Jira
ingest pipeline, the project-summary read API, and trace-link persistence. The
current route table contains **26 mounted routes** (24 business + 2
operational probes), per `endpoint_traceability_map.md`.

Meanwhile, the TypeScript SDK in `frontend/apps/web/src/api/{endpoints,schema}.ts`
and the native MCP server in `crates/tracertm-mcp/src/main.rs` were authored
against the *original* Python surface and the `services/traceraClient.js` TS
SDK cut. As a result, those consumers issue HTTP calls that return `404`
against the live Rust server. This ADR enumerates every such call, tiers it
into `must-restore`, `useful`, and `can-defer`, and prescribes a recovery
sequence that prioritises runtime-critical regressions.

## Decision drivers

1. **Runtime correctness**: an MCP tool or web page that calls a non-mounted
   route fails on every invocation. These are blocking bugs and must be
   restored first.
2. **Author surface**: callers live in two repos internal to the same
   monorepo (`frontend/apps/web` and `crates/tracertm-mcp`). Endpoint drift
   between server and consumers is the regression vector.
3. **Oracle compliance**: the FEATURE_INVENTORY explicitly marks 80+ endpoints
   as "NO (deleted)". Restoring them in random order risks re-adding surfaces
   that the new Rust contracts intentionally superseded (e.g. Prometheus
   `/metrics`, Python MCP server, device-flow auth).
4. **Cost**: each restoration costs a migration on the persistence layer
   (`Store` trait), a route handler, schema definitions, and tests. Tiering
   gates the cost so that the cheap, blocking fixes ship first.

## What is currently mounted (26 routes)

Source: `crates/tracera-server/src/main.rs:677-705` (`build_router_with_auth`).

| # | Method | Path | Module |
|---|---|---|---|
| 1 | GET | `/healthz` | `health::healthz` |
| 2 | GET | `/health` | `health::health` |
| 3 | GET | `/readyz` | `health::readyz` |
| 4 | GET | `/ready` | `health::ready` |
| 5 | POST | `/api/v1/coverage-matrix` | `coverage_matrix` |
| 6 | POST | `/api/v1/impact` | `impact` |
| 7 | POST | `/api/v1/confidence` | `confidence` |
| 8 | POST | `/api/v1/blast-radius` | `blast_radius` |
| 9 | POST | `/api/v1/governance/spec-check` | `spec_check` |
| 10 | POST | `/api/v1/trace/forward/{artifact_id}` | `trace_forward` |
| 11 | POST | `/api/v1/trace/reverse/{artifact_id}` | `trace_reverse` |
| 12 | GET | `/api/v1/trace/{artifact_id}/links` | `list_persisted_trace_links` |
| 13 | GET | `/evidence` | `list_evidence` |
| 14 | POST | `/evidence` | `create_evidence` |
| 15 | GET | `/evidence/health` | `health::health` |
| 16 | POST | `/ingest/github` | `ingest_github` |
| 17 | POST | `/ingest/jira` | `ingest_jira` |
| 18 | GET | `/sdlc-pm/health` | `health::health` |
| 19 | GET | `/sdlc-pm/sprints` | `list_sprints` |
| 20 | POST | `/sdlc-pm/sprints` | `create_sprint` |
| 21 | GET | `/sdlc-pm/stories` | `list_stories` |
| 22 | GET | `/api/v1/projects` | `list_projects` |
| 23 | GET | `/api/v1/projects/{project_id}` | `get_project` |
| 24 | GET | `/problems` | `list_problems` |
| 25 | POST | `/problems` | `create_problem` |
| 26 | GET | `/problems/health` | `health::health` |
| 27 | GET | `/org-intel/health` | `health::health` |
| 28 | GET | `/org-intel/teams` | `list_teams` |
| 29 | GET | `/org-intel/metrics` | `org_metrics` |

(Documented in `endpoint_traceability_map.md` lines 13-38 with five
extras added since that audit: trace-link listing, project read, project
list, problem list/create, problem health.)

## Refactor timeline

| Commit | PR | Action | Endpoints affected |
|---|---|---|---|
| `2ece64691f` | (initial) | Python FastAPI mounted: ~100+ endpoints across 22 routers | All Python routers registered |
| `4a78d6a1a` | — | "chore(cleanup): remove archived agileplus specs, claude commands, dispatch-mcp, mcp-tool-chest, Tracertm-rs" | `.claude/`, `.github/`, `.agileplus/`, `frontend/apps/web/` (full UI removed) |
| `531fad438` | #661 | "fix: wire missing Tracera routers (endpoint parity vs oracle)" | Restored some routers that had been unmounted |
| `d27044dc8` | #660 | "fix: restore account_repository to repair FastAPI import regression" | Restored `account_repository.py` |
| `30d85f252` | #677 | "feat(server): native tracera-server axum crate, 20 endpoints (rebased)" | **Ported**: coverage-matrix, impact, confidence, blast-radius, spec-check, trace forward/reverse, evidence (list/create), ingest github/jira, sprints (list/create), stories (list), teams (list), org-intel/metrics. **Dropped**: ~80 |
| `363bab441` | #709 | "feat(server): restore Postgres persistence (evidence/sprints/stories/teams) — dropped in Python→Rust migration" | Switched in-memory state → Postgres-backed `Store` trait; route surface unchanged |
| `a313c7912` | #713 | "feat(server): Store trait + SQLite on-device tier alongside Postgres" | Backend-tier migration; routes unchanged |
| `f70988865` | #717 | "feat(ingest): implement real GitHub/Jira issue ingest via Store trait" | `/ingest/github` and `/ingest/jira` now persist via `Store` |
| `5fae0d1c0` | #737 | "recover: restore ITIL Problem-management domain model (Rust port from Python original at 2ece64691f)" | **Restored**: `GET /problems`, `POST /problems`, `GET /problems/health`, plus `Problem` model and migrations `0007_create_problems.sql` |
| `d8f7e57a3` | #741 | "feat(web): add services/traceraClient.js, restructure yarn workspaces" | TS SDK cut against the Python surface; **mismatch with live Rust server begins here** |
| `aaf7aef23` | #799 | "fix(selfhost): wire protected API to Postgres" | Restored bearer-auth enforcement for the self-hosted deploy; routes unchanged |
| `bc67028d7` | #879 | "fix(server): migrate :project_id to {project_id} for Axum 0.8" | Cosmetic path-parameter syntax; no API loss |
| `52108664b` | #880 | "fix(server): migrate last :artifact_id in trace links route for Axum 0.8" | Cosmetic |
| `078ed097f` | #878 | "fix(server): migrate :param to {param} for Axum 0.8" | Cosmetic |

## Tiered regression inventory

### Tier 1 — `must-restore` (broken consumer + simple fix)

These endpoints are **invoked at runtime** by a live consumer but return
`404` against the live Rust server. Each call produces a real bug.

| # | Method | Path | Original (Python) | Consumed by | Evidence |
|---|---|---|---|---|---|
| 1.1 | POST | `/api/v1/stories` | `src/tracertm/api/routers/sdlc_pm.py` (POST `/api/v1/stories`) | `tracertm-mcp` tool `create_issue` | `crates/tracertm-mcp/src/main.rs:95` issues `POST /api/v1/stories` with `{id, title, description, status, story_points}`. Server has `GET /sdlc-pm/stories` only — **path and method both wrong**. |
| 1.2 | POST | `/api/v1/trace` | n/a (ad-hoc route, see `Store::create_trace_link`) | `tracertm-mcp` tool `trace_link` | `crates/tracertm-mcp/src/main.rs:107` issues `POST /api/v1/trace` with `{id, source_id, target_id, relationship, confidence, source}`. Server has only `POST /api/v1/trace/{forward,reverse}/{id}` and `GET /api/v1/trace/{id}/links`. |
| 1.3 | GET | `/api/v1/stories` | `src/tracertm/api/routers/sdlc_pm.py` (GET `/api/v1/stories`) | `tracertm-mcp` tool `list_issues` | `crates/tracertm-mcp/src/main.rs:135` issues `GET /api/v1/stories`. Server mounts `GET /sdlc-pm/stories` — path mismatch. |
| 1.4 | POST | `/api/v1/projects` | `routers/projects.py` (deleted) | Frontend `projectsApi.create` | `frontend/apps/web/src/api/endpoints.ts:61` issues `POST /api/v1/projects`. Server has `GET /api/v1/projects` only — read-only. |
| 1.5 | PUT | `/api/v1/projects/{id}` | `routers/projects.py` (deleted) | Frontend `projectsApi.update` | `frontend/apps/web/src/api/endpoints.ts:69`. Not mounted. |
| 1.6 | DELETE | `/api/v1/projects/{id}` | `routers/projects.py` (deleted) | Frontend `projectsApi.delete` | `frontend/apps/web/src/api/endpoints.ts:78`. Not mounted. |

**Rationale for tier-1:**

- 1.1–1.3 are exercised every time the MCP server runs a `create_issue`,
  `trace_link`, or `list_issues` call — three of the five advertised MCP
  tools. They are silently broken on first use.
- 1.4–1.6 are exercised by the web frontend's create/edit/delete project
  buttons; the backend would 404 on every save. Currently the UI is
  decoupled from the server (the web app ships its own state), but the
  contract violation is observable in the OpenAPI client codegen.

**Recommended fix:**

1. Add `POST /api/v1/stories` (alias of `POST /sdlc-pm/sprints`-style write)
   that delegates to `Store::create_story`. Mirror the existing
   `create_sprint` handler shape (`crates/tracera-server/src/main.rs:1054-1084`).
2. Add `GET /api/v1/stories` that delegates to `Store::list_stories` and
   keep `/sdlc-pm/stories` as a legacy alias.
3. Add `POST /api/v1/trace` that delegates to `Store::create_trace_link`
   (the trait method already exists at `crates/tracera-server/src/store.rs:240`).
4. Add the three project mutators behind the existing `GET /api/v1/projects`
   handler. Persist via a new `Store::create_project`/`update_project`/
   `delete_project` triplet on the trait (current implementation derives
   `ProjectSummary` from problem rows; mutators require a new
   `projects` table or a JSON metadata column on `problems`).

### Tier 2 — `useful` (frontend references exist but no current runtime caller)

These endpoints are typed in `frontend/apps/web/src/api/{endpoints,schema}.ts`
and would be needed the moment the frontend is re-coupled to the live
server. They are not broken today (the web app talks to its own bundled
state) but they represent the contract the SDK was built against.

| Domain | Endpoints |
|---|---|
| Items CRUD | `GET/POST/PUT/DELETE /api/v1/items`, `GET /api/v1/items/{id}`, `POST /api/v1/items/bulk-update`, `GET /api/v1/items/summary`, `GET /api/v1/items/{item_id}/pivot-targets`, `POST /api/v1/items/{item_id}/pivot` |
| Links CRUD | `GET/POST/PUT/DELETE /api/v1/links`, `GET /api/v1/links/{id}`, `GET /api/v1/links/grouped`, `GET /api/v1/projects/{projectId}/links` |
| Graph traversal | `GET /api/v1/graph/{ancestors,descendants,impact,dependencies,traverse}/{id}`, `GET /api/v1/graph/{path,paths,full,cycles,topo-sort,orphans}`, plus 8 `/api/v1/graph/analysis/*` routes (`centrality`, `coverage`, `cycles`, `dependencies`, `dependents`, `impact`, `metrics`, `shortest-path`, `cache/invalidate`) |
| Search | `POST /api/v1/search`, `GET /api/v1/search`, `GET /api/v1/search/suggest`, `POST /api/v1/search/{index/{id},batch-index,reindex}`, `GET /api/v1/search/{stats,health}`, `DELETE /api/v1/search/index/{id}` |
| Projects | `GET /api/v1/projects/{project_id}/export`, `POST /api/v1/projects/{project_id}/import`, `POST /api/v1/import`, `POST /api/v1/projects/{projectId}/versions/compare` + 2 sibling routes |
| Auth (current) | `POST /api/v1/auth/{login,logout,refresh,verify}`, `GET /api/v1/auth/me`, `GET /api/v1/csrf-token` |
| Equivalences | 17 routes under `/api/v1/equivalences` and `/api/v1/projects/{projectId}/equivalences` (canonical concepts, projections, detection, confirm/reject, batch ops) |
| Journeys | 16 routes under `/api/v1/journeys` and `/api/v1/projects/{projectId}/journeys` (CRUD + steps + detection + visualization) |
| Component library | `/api/v1/libraries`, `/api/v1/libraries/{id}`, `/api/v1/components`, `/api/v1/components/{id}`, `/api/v1/tokens`, `/api/v1/libraries/{id}/{components,tokens}`, `/api/v1/components/{id}/usage` |
| Codex / Docs / AI | `/api/v1/projects/{project_id}/codex/{auth-status,interactions,review-image,review-video}`, `/api/v1/docs/{,search,/{id}}`, `/api/v1/ai/{analyze,stream-chat}`, `/api/v1/spec-analytics/{analyze,batch-analyze,ears-patterns,validate-iso29148}` |
| Executions | `/api/v1/projects/{project_id}/executions{,/{id},{id}/start,{id}/complete,{id}/artifacts}` + `/api/v1/projects/{project_id}/execution-config` |
| Settings / Mutations / Events | `GET/PUT /api/v1/settings`, `GET/POST /api/v1/mutations`, `GET/POST /api/v1/events{,/{id}}` |
| Storage / Distributed ops | 7 `/storage/*` routes, 7 `/distributed-operations/*` routes |

**Rationale for tier-2:** these are the next obvious restore surface if/when
the frontend re-couples. They should be restored in priority order: **items
+ links** first (they underpin every project tab), **graph** second
(centrality/cycles/impact drive the visualisations), **search** third
(global search bar), then **auth** (gates everything else once tokens are
required), then the rest as feature work.

**Recommended sequencing:** open one PR per domain family. Each PR must (a)
extend `Store` if persistence is needed, (b) add migration if a new table
is required, (c) re-generate `frontend/apps/web/src/api/schema.ts` so the
SDK contract matches, (d) add at least one round-trip test in
`crates/tracera-server/src/main.rs` (`mod tests`).

### Tier 3 — `can-defer` (deleted on purpose; superseded or unreachable)

These endpoints are documented in `docs/FEATURE_INVENTORY.md` as
"NO (deleted)" and should **not** be restored unless an explicit user
request re-introduces them.

| Endpoint class | Reason to defer |
|---|---|
| `/metrics` (Prometheus) | Operations team migrated to OTLP via the `vibeproxy-monitoring-unified` sidecar; `/metrics` was deleted to drop the `prometheus_client` Python dep |
| `/health/canary`, `/health/readiness`, `/health/liveness`, `/cache/stats`, `/cache/clear` | Superseded by `/healthz`+`/readyz`; canary degraded by design |
| `/auth/{device/code,device/token,device/complete,refresh,revoke,logout,logout-expired}`, `/api/v1/auth/me`, `/auth/me`, `/csrf-token` | The Python device-flow auth was replaced by a single bearer-token check in `auth::require_bearer` (`crates/tracera-server/src/auth.rs:15-43`). Re-introducing the device flow is a separate auth-architecture ADR. |
| `/api/v1/integrations/{github,oauth,mappings,sync,conflicts,...}` and `/api/v1/webhooks/github/{webhook_id}` | Live GitHub ingest is via `/ingest/github` (`crates/tracera-server/src/main.rs:1385-1435`); the integrations layer was collapsed when `account_repository.py` was dropped (PR #660) |
| `/chat/{stream}`, `/chat`, `/api/v1/ai/{analyze,stream-chat}` | AI chat was relocated to the `tracertm-mcp` native crate (`a108d0826`, "feat(mcp): wire 5 MCP tools into tracertm-mcp crate (#897)") and to the `heliosApp` AI runtime |
| `/codex/{review-image,review-video,interactions,auth-status}` | Codex review is now a frontend-only local artefact; the backend `/codex` route was deleted in `4a78d6a1a` |
| `/mcp/{messages,sse,tools,health,config}` | Python MCP server was deleted; the `tracertm-mcp` Rust crate supersedes it |
| `/api/v1/sessions{,/{session_id}}`, `POST /api/v1/run` (agent) | Agent sandbox model was not ported; `tracertm-mcp` provides the agent surface instead |
| `/adrs` (entire CRUD), `/api/v1/adrs/*` | ADR records are now stored as Markdown in `docs/governance/policy/`, not in the DB. The frontend `ADRCard` reads from the docs folder (`frontend/apps/web/src/components/specifications/adr/ADRCard.tsx`). |
| `/contracts/*`, `/features/*`, `/scenarios/*`, `/item-specs/*` (specifications router) | Consolidated under `/api/v1/spec-analytics/*` in the Rust port; the legacy routers were deleted wholesale in `4a78d6a1a` |
| `/notifications/*` | Notifications were replaced by `tower_http` header propagation; the in-DB queue is unused |
| `/errors` | Errors are surfaced via standard HTTP status codes plus structured `ErrorResponse` bodies |
| `/execution/*` | Execution records were merged into the ingest pipeline (Helios benchmark envelopes → `evidence` + `stories`) |
| `/equivalences/*`, `/concepts/*`, `/api/v1/items/{id}/pivot*` (full equivalence subsystem) | Partial implementation; restored in tier-2 only if the equivalence-detection feature is re-prioritised |
| `/projects/{projectId}/versions/compare*` | Version diff is now a frontend-side computation; the backend route was deleted |
| `/api/v1/distributed-operations/*` | Multi-agent coordination was scoped down to `tracertm-mcp` after `168ef2e9f` |

**Rationale for tier-3:** these endpoints were removed intentionally. The
recovery commits restored the surface that the *current* Rust server's own
contracts and `tracertm-mcp` need. Re-adding the deleted Python surface
would re-grow the binary, re-add dependencies (FastAPI/SQLAlchemy-less
constraints), and undo the consolidation that the `feat/install-scripts`
branch is now building installers on top of.

## Recovery plan

### Phase 1 — Tier-1 must-restore (1 PR, ~200 LoC)

Open `feat/restore-tier-1-mcp` against `main`:

1. Add `POST /api/v1/stories` and `GET /api/v1/stories` in
   `crates/tracera-server/src/main.rs`; delegate to existing
   `Store::list_stories` / `Store::create_story` (`store.rs:214,222`).
2. Add `POST /api/v1/trace` that calls `Store::create_trace_link`
   (`store.rs:240`).
3. Extend `Store` with `create_project` / `update_project` /
   `delete_project`. Add a new migration `0009_create_projects.sql` so
   the project row is no longer derived from `problems`. Implement
   the three methods on both `PgStore` and `SqliteStore`.
4. Add `POST /api/v1/projects`, `PUT /api/v1/projects/{id}`,
   `DELETE /api/v1/projects/{id}`.
5. Update `endpoint_traceability_map.md` to mark all six tier-1 routes
   `✅`.
6. Add round-trip tests in the existing `mod tests` (`main.rs:1607`).
7. Re-run `openapi-typescript` to regenerate `schema.ts` (the codegen
   script lives in `frontend/apps/web/scripts/`).

### Phase 2 — Tier-2 useful (4-6 PRs)

Group by domain family per the table above. Each PR must (a) extend
`Store` only if persistence is needed, (b) include migrations, (c)
include tests, (d) update `endpoint_traceability_map.md`.

### Phase 3 — Tier-3 can-defer

Add a `docs/governance/policy/deleted_endpoints.md` registry that
links each tier-3 endpoint to the commit and PR that deleted it, and
states the superseding surface. This freezes the de-scope decision
so future audits don't re-litigate it.

## Consequences

### Positive

- MCP `create_issue`, `trace_link`, and `list_issues` start working on
  first call (currently 100% failure rate).
- Web frontend `projectsApi.{create,update,delete}` start working when
  the SDK is re-coupled.
- The `endpoint_traceability_map.md` 26-route governance slice grows
  to ~31 routes after phase 1, restoring the deleted-endpoints audit
  signal.
- `FEATURE_INVENTORY.md` oracle remains the source of truth for the
  deleted-Python surface.

### Negative

- Phase 1 introduces a real `projects` table; the current
  "derive-from-problems" optimisation in `Store::list_projects` must
  be reworked.
- Re-introducing `/api/v1/items`, `/api/v1/links`, etc. (phase 2)
  will require deciding what to do with the empty in-memory `Mutex`
  fallbacks that several handlers still expose.
- The Tier-3 registry must be reviewed on every release to prevent
  silent resurrection of deleted routers.

### Neutral

- The MCP server at `crates/tracertm-mcp/src/main.rs` continues to be
  the authoritative runtime contract for the 5 native tools; once
  phase 1 lands, the consumer/server pair aligns.

## Compliance and verification

- **CI gate**: add a route-mount audit to
  `crates/tracera-server/src/main.rs` `mod tests` that loads
  `build_router_with_auth` with a stub `AuthToken` and asserts each
  path in this ADR's tier-1 table resolves to a mounted route. Fail
  the build if any of them 404s.
- **MCP smoke test**: extend `crates/tracertm-mcp/src/main.rs` to
  exercise `tools/list` + each `tools/call` against a fixture
  server in CI. Reuse the `testdata/observability-ledger-consumer-v1.json`
  envelope pattern.
- **Schema drift**: regenerate `frontend/apps/web/src/api/schema.ts`
  on every server-side route change; the codegen script already
  exists in `frontend/apps/web/scripts/`.

## References

- `crates/tracera-server/src/main.rs:677-705` — current route table.
- `crates/tracera-server/src/store.rs:188-338` — current `Store`
  trait contract.
- `crates/tracertm-mcp/src/main.rs:86-141` — MCP tool definitions and
  HTTP calls.
- `frontend/apps/web/src/api/endpoints.ts:30-541` — web SDK consumer
  surface.
- `frontend/apps/web/src/api/schema.ts:7-3102` — auto-generated OpenAPI
  schema (full Python-era surface).
- `docs/FEATURE_INVENTORY.md:1-731` — historical migration oracle.
- `docs/governance/policy/endpoint_traceability_map.md:13-38` —
  current governance slice.
- `docs/governance/policy/coverage_matrix_self_application.md:20-24`
  — current self-assessment showing "Missing" on auth, "Missing" on
  ingest/comments endpoints (this ADR closes those gaps for tier-1).
- Python original: commit `2ece64691f`, file list at
  `src/tracertm/api/routers/` (22 routers, ~100+ endpoints).