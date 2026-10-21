# Tracera gap inventory

Read-only static audit against the `origin/main` source snapshot at `9a4360e812eeee81ee7c0367b12a967cf7764440`. No app code was changed and no tests were run. The live application is behind Cloudflare Access; this inventory does not claim an authenticated live-service verification. The Specifications summary payload and CIVIS item count are operator-provided observations, not re-probed here.

## Baseline selection

The default baseline set for this inventory is:

1. `docs/sessions/20260726-frontend-convergence/02_PARITY_MATRIX.md`
2. `docs/sessions/20260722-rich-dashboard-recovery/07_FRONTEND_CONVERGENCE_MATRIX.md`
3. `docs/04-guides/mcp-cli-api-matrix.md`

The first is an acceptance-gate checklist, the second is a frontend convergence candidate matrix, and the third identifies itself as historical/retired Python MCP/CLI documentation. They are not a current page-by-page attestation of actual project data. If a hand-built Koosha matrix CSV is supplied, switch the baseline input to that CSV and keep the three documents as provenance; do not edit the inventory schema. Each later refresh should record the selected baseline file(s), revision/date, and per-view expected artifact in `evidence`.

## Acceptance rule

A view named `X` must render artifact `X` for the selected project, with all required records and fields. A route or component existing does not establish data parity. A valid empty result must be distinguishable from a failed request, a stub response, or a partial/stale artifact. Unverified items remain `Unknown` rather than being treated as passing or failing.

## Issues

### [Instinct] GAP-001 Specifications summary route is an unused stub

`GET /api/v1/projects/{id}/specifications/summary` is reported as returning `{"items":[],"data":[],"results":[],"total":0,"count":0,"stub":true}`. Its declared `SpecificationSummary` contract includes ADR, contract, feature, health score, and health detail rollups. Static caller tracing found that `useSpecificationSummary` does not feed the active Specifications Dashboard: `useSpecificationsDashboardViewModel` loads dashboard data through its own queries. The route remains an API contract gap, but its response does not explain the active dashboard state. Implement the declared aggregate if the route is retained, or remove the unused route and hook; track dashboard completeness through the active queries.

Evidence: `frontend/apps/web/src/hooks/use-specifications/summary-hooks.ts:6-19`; `frontend/apps/web/src/views/specifications-dashboard/useSpecificationsDashboardViewModel.ts:81-87`; `frontend/apps/web/src/views/SpecificationsDashboardView.tsx:5,30`; operator-reported response and 26-ADR count, not independently re-probed.

### [Instinct] GAP-002 System status fabricates healthy service state

`fetchSystemStatus()` calls `/api/v1/health`, but initializes status to healthy, uptime to 99.9, and queued jobs to zero. On errors or absent response data it returns those same synthetic values. This can present an outage or missing endpoint as healthy.

Evidence: `frontend/apps/web/src/api/system.ts:1,52-91`.

### [Instinct] GAP-003 Events list converts failures to an empty list

The events list wrapper returns `[]` when the response is invalid or the request fails. A user cannot distinguish “no events” from “events unavailable.”

Evidence: `frontend/apps/web/src/api/events.ts:1,38-47`.

### [Instinct] GAP-004 Event detail drops request failures as undefined

`fetchEvent` resolves `undefined` on failures, which can be interpreted as an absent optional event instead of an API error or not-found response.

Evidence: `frontend/apps/web/src/api/events.ts:51-61`.

### [Instinct] GAP-005 Traceability Matrix item and link queries hit registered 501 routes

The active `TraceabilityMatrixView` calls `useItems({projectId})` and `useLinks({projectId})`. Those hooks request the flat collection routes `/api/v1/items?project_id=...` and `/api/v1/links?project_id=...`; both are registered to the generic HTTP 501 handler. The project-scoped list/create path `/api/v1/projects/{project_id}/items` in `queries-items.ts` is a separate query path, not used by this view; its unregistered status remains recorded in GAP-010. The zero-valued fallback in `api/matrix.ts` belongs to `fetchMatrix`, which has no production callers and does not drive this view.

Evidence: `frontend/apps/web/src/views/TraceabilityMatrixView.tsx:73-78`; `frontend/apps/web/src/hooks/useItems.ts:61-70,231`; `frontend/apps/web/src/hooks/useLinks.ts:26-52,113`; `crates/tracera-server/src/router.rs:175-188`; `frontend/apps/web/src/api/matrix.ts:56-90`; a non-test search found no `fetchMatrix` callers under `frontend/apps/web/src`; remaining call sites are the API declaration/export and tests in `frontend/apps/web/src/__tests__/api/matrix.test.ts`.

### [Instinct] GAP-006 Matrix export fabricates an empty artifact

The export fallback returns `{}` after a failed request. The caller can treat that as a completed export despite having no matrix artifact.

Evidence: `frontend/apps/web/src/api/matrix.ts:76-85`.

### [Instinct] GAP-007 Reports template list is hard-coded

The Reports API module is marked as a stub and returns a static in-code template list. The UI does not establish that those templates are available from the service or backed by complete source artifacts.

Evidence: `frontend/apps/web/src/api/reports.ts:2,23,48`.

### [Instinct] GAP-008 Report generation returns synthetic data

`generateReport` returns a fabricated ID/time and empty `data` object. It does not establish that a report artifact was generated from project data.

Evidence: `frontend/apps/web/src/api/reports.ts:50-63`.

### [Instinct] GAP-009 Multiple frontend API modules still identify as stubs

The web API modules `system.ts`, `search.ts`, `matrix.ts`, `events.ts`, and `reports.ts` contain explicit stub comments. The concrete false-success and empty-fallback behaviors found in these modules are recorded in GAP-002 through GAP-008. Search's exact response behavior and every caller-to-handler pairing were not fully resolved in this static pass and remain open evidence work.

Evidence: `frontend/apps/web/src/api/system.ts:1`; `search.ts:5`; `matrix.ts:3`; `events.ts:1`; `reports.ts:2`.

### [Instinct] GAP-010 Item and link routes return generic 501 responses

The flat Axum router registers these item/link paths with `any(not_implemented)`: `/api/v1/items`, `/api/v1/items/summary`, `/api/v1/items/bulk-update`, `/api/v1/items/{id}`, `/api/v1/items/{item_id}/pivot-targets`, `/api/v1/items/{item_id}/pivot`, `/api/v1/links`, `/api/v1/links/{id}`, `/api/v1/links/grouped`, and `/api/v1/projects/{project_id}/links`. These handlers return HTTP 501 and `{"error":"not_implemented","message":"ADR-SERVER-001"}`. Separately, the frontend uses `GET` and `POST /api/v1/projects/{project_id}/items`, but that project-scoped collection is not registered and falls through instead of returning 501. The active item and traceability views cannot establish persisted, complete project item/link artifacts.

Evidence: `crates/tracera-server/src/router.rs:25,175-188`; `frontend/apps/web/src/api/queries-items.ts:50-132`; `frontend/apps/web/src/views/TraceabilityMatrixView.tsx:73-76`.

### [Instinct] GAP-011 Graph routes return generic 501 responses

The server routes `/api/v1/graph/ancestors/{id}`, `/descendants/{id}`, `/impact/{id}`, `/dependencies/{id}`, `/traverse/{id}`, `/path`, `/paths`, `/full`, `/cycles`, `/topo-sort`, `/orphans`, `/analysis/centrality`, `/analysis/coverage`, `/analysis/cycles`, `/analysis/dependencies`, `/analysis/dependents`, `/analysis/impact`, `/analysis/metrics`, `/analysis/shortest-path`, and `/cache/invalidate` to the generic 501 handler. Dedicated graph and project views exist, but a route declaration or view file is not evidence of a complete graph artifact. Exact caller mapping remains to be completed for each graph operation.

Evidence: `crates/tracera-server/src/router.rs:25,190-209`; view inventory under `frontend/apps/web/src/routes/` and `frontend/apps/web/src/pages/projects/views/`.

### [Instinct] GAP-012 Search endpoints return generic 501 responses

`/api/v1/search`, `/api/v1/search/suggest`, `/api/v1/search/index/{id}`, `/api/v1/search/batch-index`, `/api/v1/search/reindex`, `/api/v1/search/stats`, and `/api/v1/search/health` use the generic 501 handler. The Search API wrapper is also explicitly marked as a stub. Confirm each visible search page operation maps to a working implementation and distinguishes no matches from a failed search.

Evidence: `crates/tracera-server/src/router.rs:25,211-217`; `frontend/apps/web/src/api/search.ts:5`.

### [Instinct] GAP-013 Project import/export endpoints return generic 501 responses

`/api/v1/projects/{project_id}/export`, `/api/v1/projects/{project_id}/import`, and `/api/v1/import` use the generic 501 handler. The frontend exposes project equivalence import/export flows. Implement validated artifact transfer and do not signal success for absent or partial data.

Evidence: `crates/tracera-server/src/router.rs:25,219-225`; `frontend/apps/web/src/components/equivalence/ImportWizard.tsx:98-115`; `ExportWizard.tsx:92-96`.

### [Instinct] GAP-014 Authentication route handlers are unimplemented

`/api/v1/auth/login`, `/logout`, `/refresh`, and `/verify` use the generic 501 handler in this router. Authentication can be supplied by a different deployment layer, so live-client behavior and exact route callers are not established by this source finding. Reconcile the deployed auth provider and every frontend call before representing these as supported routes.

Evidence: `crates/tracera-server/src/router.rs:25,227-230`.

### [Instinct] GAP-015 Equivalence route handlers are unimplemented

`/api/v1/equivalences`, `/api/v1/equivalences/{id}`, `/confirm`, `/reject`, and `/batch` are wired to the generic 501 handler. Import/export components call project-scoped equivalence validation/import/export endpoints; reconcile those exact project paths with the mounted router and ensure equivalence artifacts are persisted and complete.

Evidence: `crates/tracera-server/src/router.rs:25,235-239`; `frontend/apps/web/src/components/equivalence/ImportWizard.tsx:98-115`; `ExportWizard.tsx:92-96`.

### [Instinct] GAP-016 Journey routes return generic 501 responses

Journey list/detail/steps/detect/visualize and related paths are routed to the generic 501 handler. The frontend journey query and mutation modules call journey list/detail/steps and create/update/delete operations. Those views cannot meet the artifact rule while the used handlers remain unimplemented.

Evidence: `crates/tracera-server/src/router.rs:25,269-276`; `frontend/apps/web/src/api/journeys-queries.ts:23-70`; `journeys-mutations.ts:32-237`.

### [Instinct] GAP-017 Current parity baseline is not a current per-view actual-data matrix

The 20260726 matrix lists convergence acceptance gates and pending status, the 20260722 matrix compares the frontend shell with a candidate frontend implementation and notes missing Rust routes/typed adapters, and `mcp-cli-api-matrix.md` identifies itself as historical/retired and describes the earlier Python stack. These sources do not attest every current project view/sidebar page against live, complete artifacts. Keep the baseline source replaceable: when Koosha's hand-built matrix CSV is supplied, select it as the active baseline input, retain this source set as provenance, and preserve the same CSV columns.

Current frontend route and view inventory includes dashboard, graph, item list/detail, project list, search, settings, agents/admin/auth; project ADRs, contracts, features, compliance, specifications, agents, equivalence, scenario activity, settings, and temporal; and generic project views API, architecture, code, configuration, coverage, dataflow, database, dependency, domain, feature, infrastructure, integrations, journey, monitoring, performance, problem, process, QA dashboard, security, test cases/runs/suites, test, webhooks, and wireframe. This is source route coverage only. The actual artifact and data completeness for every entry remains `Unknown` unless supported by a specific row in the CSV.

Evidence: all three baseline paths listed in Baseline selection; route declarations under `frontend/apps/web/src/routes/`; dedicated views under `frontend/apps/web/src/pages/projects/views/`.

### [Instinct] GAP-018 CIVIS project reports zero items loaded

The task context reports CIVIS has zero items loaded. The service is behind Cloudflare Access and no authenticated live read was made during this static audit, so the count and cause are not independently verified here. Determine whether the source project is truly empty or whether ingestion, project scoping, permissions, or pagination/filtering prevented items from loading.

Evidence: operator-reported task context; live access not independently exercised.

### [Instinct] GAP-019 Artifact completeness is not established across all views

Apply the invariant: a view named `X` renders artifact `X`, with complete required records and fields. Mark unavailable, stale, partial, and truly empty data distinctly. The route inventory establishes that screens exist; it does not prove they render the complete named artifact. Per-view caller/API/response verification remains open where the CSV says `Unknown`.

Evidence: frontend route/view inventory; the three baselines above; specific false-success examples GAP-001 through GAP-008.

## Sidebar and project-view completeness ledger

Every sidebar destination below exists as a navigation entry. Apart from separately documented findings above, the API/artifact identity and record completeness for each destination were not independently proven in this static pass, so the corresponding `VIEW-*` CSV row is `Unknown`. These rows are coverage records, not claims that route presence proves parity.

| Sidebar label                   | Destination                                          |
| ------------------------------- | ---------------------------------------------------- |
| Dashboard                       | `/`                                                  |
| Projects                        | `/projects`                                          |
| Items                           | `/items`                                             |
| Agents                          | `/agents`                                            |
| Overview                        | `/projects/{activeId}`                               |
| Feature Layer / Features        | `/projects/{activeId}/views/feature`                 |
| Source Map / Code View          | `/projects/{activeId}/views/code`                    |
| Validation                      | `/projects/{activeId}/views/test`                    |
| Workflow Runs                   | `/projects/{activeId}/views/workflows`               |
| Project Settings / Settings     | `/projects/{activeId}/settings`                      |
| Specifications Dashboard        | `/projects/{activeId}/specifications`                |
| Scenario Activity               | `/projects/{activeId}/scenario-activity`             |
| ADRs                            | `/projects/{activeId}/specifications?tab=adrs`       |
| Contracts                       | `/projects/{activeId}/specifications?tab=contracts`  |
| Compliance                      | `/projects/{activeId}/specifications?tab=compliance` |
| Domain Model                    | `/projects/{activeId}/views/domain`                  |
| Problem Analysis / Bug Tracking | `/projects/{activeId}/views/problem`                 |
| Wireframes                      | `/projects/{activeId}/views/wireframe`               |
| Architecture                    | `/projects/{activeId}/views/architecture`            |
| API Documentation               | `/projects/{activeId}/views/api`                     |
| Database Schema                 | `/projects/{activeId}/views/database`                |
| Data Flow                       | `/projects/{activeId}/views/dataflow`                |
| Test Cases                      | `/projects/{activeId}/views/test-cases`              |
| Test Suites                     | `/projects/{activeId}/views/test-suites`             |
| Test Runs                       | `/projects/{activeId}/views/test-runs`               |
| QA Dashboard                    | `/projects/{activeId}/views/qa-dashboard`            |
| Coverage Report                 | `/projects/{activeId}/views/coverage`                |
| Journey Map                     | `/projects/{activeId}/views/journey`                 |
| Process Flow                    | `/projects/{activeId}/views/process`                 |
| Timeline                        | `/projects/{activeId}/views/monitoring`              |
| Reports / Performance           | `/projects/{activeId}/views/performance`             |
| Impact Analysis                 | `/projects/{activeId}/views/impact-analysis`         |
| Traceability Matrix             | `/projects/{activeId}/views/traceability`            |
| Dependency Graph                | `/projects/{activeId}/views/dependency`              |
| Performance Metrics             | `/projects/{activeId}/views/performance`             |
| Security Analysis               | `/projects/{activeId}/views/security`                |
| Monitoring Dashboard            | `/projects/{activeId}/views/monitoring`              |
| Integrations                    | `/projects/{activeId}/views/integrations`            |
| Webhooks                        | `/projects/{activeId}/views/webhooks`                |
| System Settings                 | `/settings`                                          |

Additional project routes found in `frontend/apps/web/src/routes/` include ADR/contract/feature detail and scenario routes; compliance; specifications; agents; equivalence; scenario activity; project settings; temporal; and generic project views for API, architecture, code, configuration, coverage, dataflow, database, dependency, domain, feature, infrastructure, integrations, journey, monitoring, performance, problem, process, QA dashboard, security, test cases, test runs, test suites, test, webhooks, and wireframe, including generic `$viewType` and `$viewType.$itemId`. Their individual response completeness remains `Unknown`; see GAP-017/GAP-019. Sidebar source: `frontend/apps/web/src/components/layout/sidebar-nav.ts:66-392`.

## Backend 501 route ledger

The route strings below are registered directly in the flat Axum router at `crates/tracera-server/src/router.rs:175-334`. They are recorded as written; no implicit `/api/v1` prefix is added within these registrations. Every listed stub route uses `any(not_implemented)` and returns HTTP 501. The project-scoped item collection is called by the frontend but is not registered, so it falls through rather than returning this 501 payload. This ledger does not establish that every route is called by the frontend.

- Items (registered 501): `/api/v1/items`, `/api/v1/items/summary`, `/api/v1/items/bulk-update`, `/api/v1/items/{id}`, `/api/v1/items/{item_id}/pivot-targets`, `/api/v1/items/{item_id}/pivot`.
- Items (frontend-required, unregistered): `GET` and `POST /api/v1/projects/{project_id}/items` (list and create).
- Links (registered 501): `/api/v1/links`, `/api/v1/links/{id}`, `/api/v1/links/grouped`, `/api/v1/projects/{project_id}/links`.
- Graph (registered 501): `/api/v1/graph/ancestors/{id}`, `/api/v1/graph/descendants/{id}`, `/api/v1/graph/impact/{id}`, `/api/v1/graph/dependencies/{id}`, `/api/v1/graph/traverse/{id}`, `/api/v1/graph/path`, `/api/v1/graph/paths`, `/api/v1/graph/full`, `/api/v1/graph/cycles`, `/api/v1/graph/topo-sort`, `/api/v1/graph/orphans`, `/api/v1/graph/analysis/centrality`, `/api/v1/graph/analysis/coverage`, `/api/v1/graph/analysis/cycles`, `/api/v1/graph/analysis/dependencies`, `/api/v1/graph/analysis/dependents`, `/api/v1/graph/analysis/impact`, `/api/v1/graph/analysis/metrics`, `/api/v1/graph/analysis/shortest-path`, `/api/v1/graph/cache/invalidate`.
- Search (registered 501): `/api/v1/search`, `/api/v1/search/suggest`, `/api/v1/search/index/{id}`, `/api/v1/search/batch-index`, `/api/v1/search/reindex`, `/api/v1/search/stats`, `/api/v1/search/health`.
- Import/export and versions (registered 501): `/api/v1/projects/{project_id}/export`, `/api/v1/projects/{project_id}/import`, `/api/v1/projects/{project_id}/versions/compare`, `/api/v1/import`.
- Auth (registered 501): `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/refresh`, `/api/v1/auth/verify`. `/api/v1/auth/me` is handled separately and is not a stub.
- Equivalences (registered 501): `/api/v1/equivalences`, `/api/v1/equivalences/{id}`, `/api/v1/equivalences/confirm`, `/api/v1/equivalences/reject`, `/api/v1/equivalences/batch`, `/api/v1/projects/{project_id}/equivalences`, `/api/v1/projects/{project_id}/equivalences/{id}`, `/api/v1/projects/{project_id}/equivalences/canonical`, `/api/v1/projects/{project_id}/equivalences/projections`, `/api/v1/projects/{project_id}/equivalences/detect`, `/api/v1/projects/{project_id}/equivalences/batch`, `/api/v1/projects/{project_id}/equivalences/stats`.
- Journeys (registered 501): `/api/v1/journeys`, `/api/v1/journeys/{id}`, `/api/v1/journeys/{id}/steps`, `/api/v1/journeys/{id}/steps/{step_id}`, `/api/v1/journeys/{id}/detect`, `/api/v1/journeys/{id}/visualize`, `/api/v1/projects/{project_id}/journeys`, `/api/v1/projects/{project_id}/journeys/{id}`, `/api/v1/projects/{project_id}/journeys/{id}/steps`, `/api/v1/projects/{project_id}/journeys/{id}/steps/{step_id}`, `/api/v1/projects/{project_id}/journeys/{id}/detect`, `/api/v1/projects/{project_id}/journeys/{id}/visualize`.
- Libraries/components/tokens (registered 501): `/api/v1/libraries`, `/api/v1/libraries/{id}`, `/api/v1/libraries/{id}/components`, `/api/v1/libraries/{id}/tokens`, `/api/v1/components`, `/api/v1/components/{id}`, `/api/v1/components/{id}/usage`, `/api/v1/tokens`.
- Codex/docs/AI (registered 501): `/api/v1/projects/{project_id}/codex/auth-status`, `/api/v1/projects/{project_id}/codex/sessions`, `/api/v1/projects/{project_id}/codex/sessions/{session_id}`, `/api/v1/projects/{project_id}/docs/generate`, `/api/v1/projects/{project_id}/ai/summarize`, `/api/v1/projects/{project_id}/ai/classify`.

## 2026-10-17 append-only census follow-up

The original static inventory above retains its historical source identity. The [current evidence tree](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/STATUS.md) separately collects current intent/interface/backend/Desk evidence; old rows are not silently reclassified or accepted as closed.

### [Instinct] GAP-020 Desk CLI cannot qualify a stack without matching layout assets

The installed `C:\Users\koosh\.cargo\bin\tracera.exe` identifies as 0.1.0 in the operator's [dated Desk report](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/evidence/desk-status-2026-10-17.md). Current source resolves an ancestor `docker-compose.bundle.yml` or `docker-compose.local.yml`; explicit `--root` / `TRACERA_ROOT` requires `<root>/tracera-bundle/docker-compose.bundle.yml` or `<root>/docker-compose.local.yml`. A standalone executable in cargo-bin does not establish those assets. Record the actual failure and matching package/worktree before choosing a runtime. Source: `048f44d2c38925f4c7c9968dfeaeda1a97f4d970:crates/tracera-cli/src/bundle.rs:47-142`; `commands.rs:145-170`.

Follow the [Desk forward path](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/DESK-FORWARD-PATH.md): discover matching assets, select an already available Compose-capable runtime, then preflight disk/ports/CPU and data ownership. No service, WSL, Docker, installation, or cleanup action is part of this docs change.

### [Instinct] GAP-021 Reconcile Desk runtime identities before acceptance

A Compose management CLI and a manually launched SQLite API are different candidates. The report's absent native Tracera process/service does not prove a later or differently named API is down. Preserve each exact binary hash/version, PID/listeners, config/root, database, and readiness receipt. No requirement for a Windows service is inferred. The actual one-GPU/vLLM occupancy, C: headroom, and Fedora/docker-desktop states constrain placement; they are not automatic feature failures. Evidence: the [dated operator report](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/evidence/desk-status-2026-10-17.md) and [separate forward plan](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/DESK-FORWARD-PATH.md). Startup qualification requires a separately authorized owned action; this work only records the plan.

Fresh GAP-020 evidence: [actual Desk CLI/bundle reconciliation](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/evidence/backend/desk-reconciliation.json) confirms status fails before Compose because cargo-bin ancestor discovery cannot see sibling `C:\Users\koosh\Tracera\docker-compose.local.yml`. `--root` is advertised but not executed because status can write env files.

Fresh GAP-021 evidence: [runtime receipt](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/evidence/backend/live-runtime.json) preserves manual PID20208and early200readiness separately from later timeouts. [UI witness](../state/tracera-state-forward-20261017-q1/observations/20261017T231000Z-census/evidence/live-view-report.json) records five direct empty-response paths and missing8091listener, with54dynamic paths NOT_RUNand deployed SHAUNKNOWN. CIVIS genuine0items at22:33Zis qualified only for that response; other project manifests remain incomplete.

## D-04 operator follow-up (2026-10-18T06:53Z report receipt)

GAP-020 additionally requires the exact root-qualified status/up sequence and prerequisites documented in [D-04 preflight](D04-ROOT-PREFLIGHT.md). This extends the existing launch/layout issue rather than duplicating it. Historical GAP-020/021 records remain unchanged.

### [Instinct] GAP-022 Qualify the selected Desk Compose backend before launch

Docker selected with docker-desktop reported Stopped is an unqualified launch prerequisite, not independent proof of every endpoint being down. Fedora Podman on port 7777 does not automatically satisfy native `podman compose` or `wsl+docker`. Source supports Podman but compatibility of that endpoint remains UNKNOWN. See [source identities, evidence limits, and positive/negative closure oracles](D04-ROOT-PREFLIGHT.md). First perform read-only root/config/backend identification and preserve configuration; no backend switch or startup was executed.

### [Instinct] GAP-023 Preserve env configuration during root-qualified status

Source `cmd_status` runs env preparation before Compose. `ensure_env_file` preserves a file containing a nonempty exact `POSTGRES_PASSWORD=` line but regenerates the whole file otherwise, including read failure. Existing real compose-side env files are retained by the link helper; different symlink targets can be replaced. This is source-qualified conditional overwrite risk; actual Desk overwrite is UNKNOWN. See [source proof and isolated positive/negative closure oracles](D04-ROOT-PREFLIGHT.md). Secure byte/metadata preservation and a read-only preflight precede any status/up call. Runtime validation NOT_RUN.
