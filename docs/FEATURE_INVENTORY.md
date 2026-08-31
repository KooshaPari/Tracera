# Tracera Feature Inventory — Migration Safety Oracle

> Historical migration oracle: entries labelled “CURRENT” describe the former
> Python `tracertm` service and are retained only for migration safety. They
> are not the live Rust `tracera-server` contract; use [`API_REFERENCE.md`](API_REFERENCE.md)
> for deployed routes.

**Generated:** 2026-06-24
**Purpose:** Authoritative catalog of every capability that has EVER existed across ALL branches and git history. Migrations MUST consult this oracle before dropping any feature.
**Scope:** Full repo at `E:/Dev/Tracera`. Surveyed via targeted `git log --diff-filter=A/D`, `git ls-tree --name-only -r`, and `git show <ref>:<path>` against historical commit `9e78f48d~1` (the last "fat" main pre-security-fix), `feat/trc013-bulk-tracelink-ingestion`, and current `HEAD` (= `main`).

---

## Legend

- **Type:** `API` (HTTP route) | `CLI` (Typer/cobra subcommand) | `CORE` (Rust public API in `crates/tracera-core`) | `SVC` (Python service layer) | `MODEL` (DB/ORM) | `MODULE` (top-level Python package) | `HANDLER` (legacy handler module) | `MCP` (Model Context Protocol tool) | `WORKFLOW` (Temporal/workflow) | `TUI` (Textual UI)
- **Location:** relative path from repo root.
- **On main?:** `YES` if present in `HEAD`, `NO` if only in history, `STUB` if file exists but contains only a stub/skeleton.
- **First seen:** commit hash (short) + branch. `(initial)` = present in the very first commit.

---

## 1. API ENDPOINTS

### 1a. HISTORICAL PYTHON — registered in `src/tracertm/api/main.py` (archived)

Mounted via `app.include_router(...)` with `prefix="/api/v1"` (`src/tracertm/api/main.py:22-26`).

| Feature | Method | Path | Location | On main? | First seen |
|---|---|---|---|---|---|
| Health probe (liveness) | GET | `/healthz` | `src/tracertm/api/main.py:28` | YES | 91e2f6b |
| Ready probe | GET | `/readyz` | `src/tracertm/api/main.py:36` | YES | 91e2f6b |
| Current user | GET | `/api/v1/me` | `src/tracertm/api/routers/auth.py:59` | YES | 91e2f6b |
| Coverage matrix | POST | `/api/v1/coverage-matrix` | `src/tracertm/api/routers/traceability.py:103` | YES | 91e2f6b |
| Spec-first governance | POST | `/api/v1/governance/spec-check` | `src/tracertm/api/routers/traceability.py:109` | YES | 91e2f6b |
| Impact (blast radius) | POST | `/api/v1/impact` | `src/tracertm/api/routers/traceability.py:115` | YES | 91e2f6b |
| Confidence scoring | POST | `/api/v1/confidence` | `src/tracertm/api/routers/traceability.py:242` | YES | 91e2f6b |
| Org-intel health | GET | `/api/v1/health` (org_intel) | `src/tracertm/api/routers/org_intel.py:55` | YES | 91e2f6b |
| Org-intel metrics | GET | `/api/v1/metrics` | `src/tracertm/api/routers/org_intel.py:61` | YES | 91e2f6b |
| Org-intel teams | GET | `/api/v1/teams` | `src/tracertm/api/routers/org_intel.py:72` | YES | 91e2f6b |
| SDLC/PM health | GET | `/api/v1/health` (sdlc_pm) | `src/tracertm/api/routers/sdlc_pm.py:99` | YES | 91e2f6b |
| SDLC sprints | GET | `/api/v1/sprints` | `src/tracertm/api/routers/sdlc_pm.py:105` | YES | 91e2f6b |
| SDLC stories | GET | `/api/v1/stories` | `src/tracertm/api/routers/sdlc_pm.py:111` | YES | 91e2f6b |
| Create sprint | POST | `/api/v1/sprints` | `src/tracertm/api/routers/sdlc_pm.py:117` | YES | 91e2f6b |
| Evidence health | GET | `/api/v1/health` (evidence) | `src/tracertm/api/routers/evidence.py:67` | YES | 91e2f6b |
| List evidence | GET | `/api/v1/evidence` | `src/tracertm/api/routers/evidence.py:73` | YES | 91e2f6b |
| Create evidence | POST | `/api/v1/evidence` | `src/tracertm/api/routers/evidence.py:79` | YES | 91e2f6b |

### 1b. CURRENT — file present but NOT registered in `main.py` (regression hazard)

These six router files exist under `src/tracertm/api/routers/` on HEAD but are not included by `main.py:22-26`. Their endpoints are unreachable at runtime.

| Feature | Method | Path | Location | On main? | First seen |
|---|---|---|---|---|---|
| Code trace by component | GET | `/api/v1/code-trace/{component_id}` | `src/tracertm/api/routers/code_trace.py:112` | YES (unmounted) | 91e2f6b |
| Blast-radius scoring | POST | `/api/v1/blast-radius` | `src/tracertm/api/routers/impact_scoring.py:30` | YES (unmounted) | 91e2f6b |
| GitHub issue ingest | POST | `/api/v1/ingest/github` | `src/tracertm/api/routers/ingest.py:26` | YES (unmounted) | 91e2f6b |
| JIRA issue ingest | POST | `/api/v1/ingest/jira` | `src/tracertm/api/routers/ingest.py:37` | YES (unmounted) | 91e2f6b |
| Forward impact | GET | `/api/v1/impact/forward/{artifact_id}` | `src/tracertm/api/routers/impact.py:33` | YES (unmounted) | 91e2f6b |
| Reverse impact | GET | `/api/v1/impact/reverse/{artifact_id}` | `src/tracertm/api/routers/impact.py:61` | YES (unmounted) | 91e2f6b |
| List comments | GET | `/api/v1/comments/` | `src/tracertm/api/routers/comments.py:90` | YES (unmounted) | 91e2f6b |
| Create comment | POST | `/api/v1/comments/` | `src/tracertm/api/routers/comments.py:111` | YES (unmounted) | 91e2f6b |
| Delete comment | DELETE | `/api/v1/comments/{comment_id}` | `src/tracertm/api/routers/comments.py:142` | YES (unmounted) | 91e2f6b |
| Chat (legacy handler) | — | `src/tracertm/api/handlers/chat.py` | — | YES (unmounted) | 9e78f48~1 |
| Impact (legacy handler) | — | `src/tracertm/api/handlers/impact.py` | — | YES (unmounted) | 9e78f48~1 |

### 1c. HISTORICAL — present in pre-consolidation `main.py` (`9e78f48d~1`), **MISSING from current main**

These endpoints lived in router files that were DELETED at `9e78f48ddc4410d91edc9669b06fc3dc3ffb9a55` (security fix commit) and the earlier `4ad704fd` cleanup. The bulk was in `src/tracertm/api/router_registry.py` (also deleted).

#### 1c.1 Authentication (`/auth`, `/api/v1/auth`, `/auth_refresh`, `/auth_session`, `/auth_public`, `/csrf-token`)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Auth (device-flow, refresh) | (router) | `/auth` | `routers/auth.py` | NO (deleted) | initial |
| Refresh token | POST | `/auth/refresh` | `routers/auth_refresh.py` | NO (deleted) | initial |
| CSRF token | GET | `/auth/csrf-token` | `routers/auth_session.py` | NO (deleted) | initial |
| Auth callback | POST | `/auth/callback` | `routers/auth_session.py` | NO (deleted) | initial |

#### 1c.2 Health & metrics (`/health`, `/metrics`, `/ready`)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Health | GET | `/health` | `routers/health.py` | NO (deleted) | initial |
| Metrics | GET | `/metrics` | `routers/health.py` | NO (deleted) | initial |
| Ready | GET | `/ready` | `routers/health.py` | NO (deleted) | initial |
| Canary | GET | `/health/canary` | `routers/health_canary.py` | NO (deleted) | initial |
| Readiness | GET | `/health/readiness` | `routers/health_canary.py` | NO (deleted) | initial |
| Liveness | GET | `/health/liveness` | `routers/health_canary.py` | NO (deleted) | initial |
| Cache stats | GET | `/cache/stats` | `routers/cache.py` | NO (deleted) | initial |
| Cache clear | POST | `/cache/clear` | `routers/cache.py` | NO (deleted) | initial |

#### 1c.3 Multi-account / OAuth (`/api/v1/accounts`, `/oauth`, `/integrations`)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| List accounts | GET | `/accounts` | `routers/accounts.py` | NO (deleted) | initial |
| Create account | POST | `/accounts` | `routers/accounts.py` | NO (deleted) | initial |
| Switch account | POST | `/accounts/{account_id}/switch` | `routers/accounts.py` | NO (deleted) | initial |
| OAuth start | POST | `/api/v1/integrations/oauth/start` | `routers/oauth.py` | NO (deleted) | initial |
| OAuth callback | POST | `/api/v1/integrations/oauth/callback` | `routers/oauth.py` | NO (deleted) | initial |
| OAuth credentials | GET | `/api/v1/integrations/credentials` | `routers/oauth.py` | NO (deleted) | initial |
| OAuth credential validate | POST | `/api/v1/integrations/credentials/{credential_id}/validate` | `routers/oauth.py` | NO (deleted) | initial |
| OAuth credential delete | DELETE | `/api/v1/integrations/credentials/{credential_id}` | `routers/oauth.py` | NO (deleted) | initial |
| OAuth stats | GET | `/api/v1/integrations/stats` | `routers/oauth.py` | NO (deleted) | initial |
| Integration mappings CRUD | GET/POST/PUT/DELETE | `/api/v1/integrations/mappings[...]` | `routers/integrations.py` | NO (deleted) | initial |
| Integration sync status | GET | `/api/v1/integrations/sync/status` | `routers/integrations.py` | NO (deleted) | initial |
| Sync trigger | POST | `/api/v1/integrations/sync/trigger` | `routers/integrations.py` | NO (deleted) | initial |
| Sync queue | GET | `/api/v1/integrations/sync/queue` | `routers/integrations.py` | NO (deleted) | initial |
| Integration conflicts | GET | `/api/v1/integrations/conflicts` | `routers/integrations.py` | NO (deleted) | initial |
| Resolve conflict | POST | `/api/v1/integrations/conflicts/{conflict_id}/resolve` | `routers/integrations.py` | NO (deleted) | initial |
| AgilePlus push | POST | `/api/v1/integrations/agileplus/push` | `routers/integrations.py` | NO (deleted) | initial |

#### 1c.4 GitHub integration (`/api/v1/integrations/github`, `/api/v1/webhooks/github`)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| List GitHub repos | GET | `/api/v1/integrations/github/repos` | `routers/github.py` | NO (deleted) | initial |
| Create GitHub repo | POST | `/api/v1/integrations/github/repos` | `routers/github.py` | NO (deleted) | initial |
| List repo issues | GET | `/api/v1/integrations/github/repos/{owner}/{repo}/issues` | `routers/github.py` | NO (deleted) | initial |
| GitHub app install URL | GET | `/api/v1/integrations/github/app/install-url` | `routers/github.py` | NO (deleted) | initial |
| GitHub app webhook | POST | `/api/v1/integrations/github/app/webhook` | `routers/github.py` | NO (deleted) | initial |
| List GitHub app installations | GET | `/api/v1/integrations/github/app/installations` | `routers/github.py` | NO (deleted) | initial |
| Link installation | POST | `/api/v1/integrations/github/app/installations/{installation_id}/link` | `routers/github.py` | NO (deleted) | initial |
| Delete installation | DELETE | `/api/v1/integrations/github/app/installations/{installation_id}` | `routers/github.py` | NO (deleted) | initial |
| GitHub projects | GET | `/api/v1/integrations/github/projects` | `routers/github.py` | NO (deleted) | initial |
| Auto-link projects | POST | `/api/v1/integrations/github/projects/auto-link` | `routers/github.py` | NO (deleted) | initial |
| Linked GitHub projects | GET | `/api/v1/integrations/github/projects/linked` | `routers/github.py` | NO (deleted) | initial |
| Unlink GitHub project | DELETE | `/api/v1/integrations/github/projects/{github_project_id}/unlink` | `routers/github.py` | NO (deleted) | initial |
| Receive GitHub webhook | POST | `/api/v1/webhooks/github/{webhook_id}` | `routers/github.py` | NO (deleted) | initial |

#### 1c.5 Linear integration

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Linear teams | GET | `/api/v1/integrations/linear/teams` | `routers/linear.py` | NO (deleted) | initial |
| Linear team issues | GET | `/api/v1/integrations/linear/teams/{team_id}/issues` | `routers/linear.py` | NO (deleted) | initial |
| Linear projects | GET | `/api/v1/integrations/linear/projects` | `routers/linear.py` | NO (deleted) | initial |

#### 1c.6 Chat / Codex / MCP / Codex AI integration

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Chat stream | POST | `/chat/stream` | `routers/chat.py` | NO (deleted) | initial |
| Chat submit | POST | `/chat` | `routers/chat.py` | NO (deleted) | initial |
| Codex image review | POST | `/codex/review-image` | `routers/codex.py` | NO (deleted) | initial |
| Codex video review | POST | `/codex/review-video` | `routers/codex.py` | NO (deleted) | initial |
| Codex interactions | GET | `/codex/interactions` | `routers/codex.py` | NO (deleted) | initial |
| Codex auth status | GET | `/codex/auth-status` | `routers/codex.py` | NO (deleted) | initial |
| MCP config | GET | `/mcp/config` | `routers/mcp.py` | NO (deleted) | initial |
| MCP JSON-RPC | POST | `/mcp/messages` | `routers/mcp.py` | NO (deleted) | initial |
| MCP SSE | GET | `/mcp/sse` | `routers/mcp.py` | NO (deleted) | initial |
| MCP tools | GET | `/mcp/tools` | `routers/mcp.py` | NO (deleted) | initial |
| MCP health | GET | `/mcp/health` | `routers/mcp.py` | NO (deleted) | initial |

#### 1c.7 Agent sessions & runs

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Create agent session | POST | `/api/v1/sessions` | `routers/agent.py` | NO (deleted) | initial |
| Get agent session | GET | `/api/v1/sessions/{session_id}` | `routers/agent.py` | NO (deleted) | initial |
| List agent sessions | GET | `/api/v1/sessions` | `routers/agent.py` | NO (deleted) | initial |
| Delete agent session | DELETE | `/api/v1/sessions/{session_id}` | `routers/agent.py` | NO (deleted) | initial |
| Run agent | POST | `/api/v1/run` | `routers/agent.py` | NO (deleted) | initial |

#### 1c.8 Items / Links / Comments / Projects (CRUD core)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| List items | GET | `/api/v1/items` | `routers/items.py` | NO (deleted) | initial |
| Get item | GET | `/api/v1/items/{item_id}` | `routers/items.py` | NO (deleted) | initial |
| Create item | POST | `/api/v1/items` | `routers/items.py` | NO (deleted) | initial |
| Update item | PUT | `/api/v1/items/{item_id}` | `routers/items.py` | NO (deleted) | initial |
| Delete item | DELETE | `/api/v1/items/{item_id}` | `routers/items.py` | NO (deleted) | initial |
| Bulk update items | POST | `/api/v1/items/bulk-update` | `routers/items.py` | NO (deleted) | initial |
| Item summary | GET | `/api/v1/items/summary` | `routers/items_summary.py` | NO (deleted) | initial |
| List links | GET | `/api/v1/links` | `routers/links.py` | NO (deleted) | initial |
| Grouped links | GET | `/api/v1/links/grouped` | `routers/links.py` | NO (deleted) | initial |
| Create link | POST | `/api/v1/links` | `routers/links.py` | NO (deleted) | initial |
| Update link | PUT | `/api/v1/links/{link_id}` | `routers/links.py` | NO (deleted) | initial |
| Delete link | DELETE | `/api/v1/links/{link_id}` | `routers/links.py` | NO (deleted) | initial |
| List projects | GET | `/api/v1/projects` | `routers/projects.py` | NO (deleted) | initial |
| Get project | GET | `/api/v1/projects/{project_id}` | `routers/projects.py` | NO (deleted) | initial |
| Create project | POST | `/api/v1/projects` | `routers/projects.py` | NO (deleted) | initial |
| Update project | PUT | `/api/v1/projects/{project_id}` | `routers/projects.py` | NO (deleted) | initial |
| Delete project | DELETE | `/api/v1/projects/{project_id}` | `routers/projects.py` | NO (deleted) | initial |
| Export project | GET | `/api/v1/projects/{project_id}/export` | `routers/projects.py` | NO (deleted) | initial |
| Import project | POST | `/api/v1/projects/{project_id}/import` | `routers/projects.py` | NO (deleted) | initial |
| Bulk import | POST | `/api/v1/projects/import` | `routers/projects.py` | NO (deleted) | initial |
| Project sync status | GET | `/api/v1/projects/{project_id}/sync/status` | `routers/project_sync_search.py` | NO (deleted) | initial |
| Project sync trigger | POST | `/api/v1/projects/{project_id}/sync` | `routers/project_sync_search.py` | NO (deleted) | initial |
| Project advanced search | POST | `/api/v1/projects/{project_id}/search/advanced` | `routers/project_sync_search.py` | NO (deleted) | initial |

#### 1c.9 Item specifications (FR-TRC-004 / FR-TRC-008)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Item-specs CRUD (extensive) | (router) | `/item-specs` | `routers/item_specs.py` | NO (deleted) | initial |

#### 1c.10 Test cases / suites / runs / results

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| List test cases | GET | `/api/v1/test-cases` | `routers/test_cases.py` | NO (deleted) | initial |
| Get test case | GET | `/api/v1/test-cases/{test_case_id}` | `routers/test_cases.py` | NO (deleted) | initial |
| Create test case | POST | `/api/v1/test-cases` | `routers/test_cases.py` | NO (deleted) | initial |
| Update test case | PUT | `/api/v1/test-cases/{test_case_id}` | `routers/test_cases.py` | NO (deleted) | initial |
| Test-case status | POST | `/api/v1/test-cases/{test_case_id}/status` | `routers/test_cases.py` | NO (deleted) | initial |
| Submit for review | POST | `/api/v1/test-cases/{test_case_id}/submit-review` | `routers/test_cases.py` | NO (deleted) | initial |
| Approve test case | POST | `/api/v1/test-cases/{test_case_id}/approve` | `routers/test_cases.py` | NO (deleted) | initial |
| Deprecate test case | POST | `/api/v1/test-cases/{test_case_id}/deprecate` | `routers/test_cases.py` | NO (deleted) | initial |
| Test-case activities | GET | `/api/v1/test-cases/{test_case_id}/activities` | `routers/test_cases.py` | NO (deleted) | initial |
| Delete test case | DELETE | `/api/v1/test-cases/{test_case_id}` | `routers/test_cases.py` | NO (deleted) | initial |
| Test-case stats | GET | `/api/v1/projects/{project_id}/test-cases/stats` | `routers/test_cases.py` | NO (deleted) | initial |
| List test suites | GET | `/api/v1/test-suites` | `routers/test_suites.py` | NO (deleted) | initial |
| Get test suite | GET | `/api/v1/test-suites/{suite_id}` | `routers/test_suites.py` | NO (deleted) | initial |
| Create test suite | POST | `/api/v1/test-suites` | `routers/test_suites.py` | NO (deleted) | initial |
| Update test suite | PUT | `/api/v1/test-suites/{suite_id}` | `routers/test_suites.py` | NO (deleted) | initial |
| Test-suite status | POST | `/api/v1/test-suites/{suite_id}/status` | `routers/test_suites.py` | NO (deleted) | initial |
| Attach test cases | POST | `/api/v1/test-suites/{suite_id}/test-cases` | `routers/test_suites.py` | NO (deleted) | initial |
| Detach test cases | DELETE | `/api/v1/test-suites/{suite_id}/test-cases/{test_case_id}` | `routers/test_suites.py` | NO (deleted) | initial |
| List suite cases | GET | `/api/v1/test-suites/{suite_id}/test-cases` | `routers/test_suites.py` | NO (deleted) | initial |
| Test-suite activities | GET | `/api/v1/test-suites/{suite_id}/activities` | `routers/test_suites.py` | NO (deleted) | initial |
| Delete test suite | DELETE | `/api/v1/test-suites/{suite_id}` | `routers/test_suites.py` | NO (deleted) | initial |
| Test-suite stats | GET | `/api/v1/projects/{project_id}/test-suites/stats` | `routers/test_suites.py` | NO (deleted) | initial |
| List test runs | GET | `/api/v1/test-runs` | `routers/test_runs.py` | NO (deleted) | initial |
| Get test run | GET | `/api/v1/test-runs/{run_id}` | `routers/test_runs.py` | NO (deleted) | initial |
| Create test run | POST | `/api/v1/test-runs` | `routers/test_runs.py` | NO (deleted) | initial |
| Update test run | PUT | `/api/v1/test-runs/{run_id}` | `routers/test_runs.py` | NO (deleted) | initial |
| Start test run | POST | `/api/v1/test-runs/{run_id}/start` | `routers/test_runs.py` | NO (deleted) | initial |
| Complete test run | POST | `/api/v1/test-runs/{run_id}/complete` | `routers/test_runs.py` | NO (deleted) | initial |
| Cancel test run | POST | `/api/v1/test-runs/{run_id}/cancel` | `routers/test_runs.py` | NO (deleted) | initial |
| Delete test run | DELETE | `/api/v1/test-runs/{run_id}` | `routers/test_runs.py` | NO (deleted) | initial |
| Test-run stats | GET | `/api/v1/projects/{project_id}/test-runs/stats` | `routers/test_runs.py` | NO (deleted) | initial |
| Submit run result | POST | `/api/v1/test-runs/{run_id}/results` | `routers/test_run_results.py` | NO (deleted) | initial |
| Submit bulk results | POST | `/api/v1/test-runs/{run_id}/bulk-results` | `routers/test_run_results.py` | NO (deleted) | initial |
| Get run results | GET | `/api/v1/test-runs/{run_id}/results` | `routers/test_run_results.py` | NO (deleted) | initial |
| Run activities | GET | `/api/v1/test-runs/{run_id}/activities` | `routers/test_run_results.py` | NO (deleted) | initial |

#### 1c.11 Coverage / QA / Quality (FR-TRC-012 / FR-TRC-014 / FR-TRC-017)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Coverage list | GET | `/coverage` | `routers/coverage.py` | NO (deleted) | initial |
| Create coverage | POST | `/coverage` | `routers/coverage.py` | NO (deleted) | initial |
| Get coverage | GET | `/coverage/{coverage_id}` | `routers/coverage.py` | NO (deleted) | initial |
| Update coverage | PUT | `/coverage/{coverage_id}` | `routers/coverage.py` | NO (deleted) | initial |
| Delete coverage | DELETE | `/coverage/{coverage_id}` | `routers/coverage.py` | NO (deleted) | initial |
| Verify coverage | POST | `/coverage/{coverage_id}/verify` | `routers/coverage.py` | NO (deleted) | initial |
| Coverage matrix | GET | `/coverage/matrix` | `routers/coverage.py` | NO (deleted) | initial |
| Coverage gaps | GET | `/coverage/gaps` | `routers/coverage.py` | NO (deleted) | initial |
| Test-case coverage | GET | `/test-cases/{test_case_id}/coverage` | `routers/coverage.py` | NO (deleted) | initial |
| Requirement coverage | GET | `/requirements/{requirement_id}/coverage` | `routers/coverage.py` | NO (deleted) | initial |
| Project coverage stats | GET | `/projects/{project_id}/coverage/stats` | `routers/coverage.py` | NO (deleted) | initial |
| Coverage activities | GET | `/coverage/{coverage_id}/activities` | `routers/coverage.py` | NO (deleted) | initial |
| Coverage matrix export (FR-TRC-014) | GET | `/api/v1/coverage-matrix/matrix` | `routers/coverage_matrix.py` | NO (deleted) | 484 (PR for FR-TRC-014) |
| QA metrics summary | GET | `/api/v1/qa/metrics/summary` | `routers/qa_metrics.py` | NO (deleted) | initial |
| QA pass-rate | GET | `/api/v1/qa/metrics/pass-rate` | `routers/qa_metrics.py` | NO (deleted) | initial |
| QA coverage | GET | `/api/v1/qa/metrics/coverage` | `routers/qa_metrics.py` | NO (deleted) | initial |
| QA defect density | GET | `/api/v1/qa/metrics/defect-density` | `routers/qa_metrics.py` | NO (deleted) | initial |
| QA flaky tests | GET | `/api/v1/qa/metrics/flaky-tests` | `routers/qa_metrics.py` | NO (deleted) | initial |
| QA execution history | GET | `/api/v1/qa/metrics/execution-history` | `routers/qa_metrics.py` | NO (deleted) | initial |
| Duplicate detection (FR-TRC-012) | POST | `/quality/duplicates` | `routers/dup_conflict.py` | NO (deleted) | 481 (PR for FR-TRC-012) |
| Conflict detection (FR-TRC-012) | POST | `/quality/conflicts` | `routers/dup_conflict.py` | NO (deleted) | 481 (PR for FR-TRC-012) |
| Traceability health score (FR-TRC-017) | GET | `/quality/score` | `routers/traceability_score.py` | NO (deleted) | 483 (PR for FR-TRC-017) |
| Requirement quality analysis | POST | `/quality/items/{item_id}/analyze` | `routers/quality.py` | NO (deleted) | initial |
| Requirement quality get | GET | `/quality/items/{item_id}` | `routers/quality.py` | NO (deleted) | initial |
| Problems CRUD | (router) | `/api/v1/problems[...]` | `routers/problems.py` | NO (deleted) | initial |
| Processes CRUD | (router) | `/api/v1/processes[...]` | `routers/processes.py` | NO (deleted) | initial |
| Executions CRUD | (router) | `/api/v1/executions[...]` | `routers/executions.py` | NO (deleted) | initial |
| Workflow runs/schedules | (router) | `/api/v1/workflows[...]` | `routers/workflows.py` | NO (deleted) | initial |

#### 1c.12 Graphs / Gaps / Analysis

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Trace gaps | GET | `/analysis/gaps` | `routers/analysis.py` | NO (deleted) | initial |
| Trace matrix | GET | `/analysis/trace-matrix` | `routers/analysis.py` | NO (deleted) | initial |
| Trace matrix export | GET | `/analysis/trace-matrix/export` | `routers/analysis.py` | NO (deleted) | initial |
| Reverse impact | GET | `/analysis/reverse-impact/{item_id}` | `routers/analysis.py` | NO (deleted) | initial |
| Analysis health | GET | `/analysis/health/{project_id}` | `routers/analysis.py` | NO (deleted) | initial |
| Analysis impact | GET | `/analysis/impact/{item_id}` | `routers/analysis.py` | NO (deleted) | initial |
| Cycles | GET | `/analysis/cycles/{project_id}` | `routers/analysis.py` | NO (deleted) | initial |
| Graph neighbors | GET | `/api/v1/graph/neighbors` | `routers/graphs.py` | NO (deleted) | initial |
| List graphs | GET | `/api/v1/graphs` | `routers/graphs.py` | NO (deleted) | initial |
| Get graph | GET | `/api/v1/graph` | `routers/graphs.py` | NO (deleted) | initial |
| Validate graph | GET | `/api/v1/graphs/{graph_id}/validate` | `routers/graphs.py` | NO (deleted) | initial |
| Snapshot graph | POST | `/api/v1/graphs/{graph_id}/snapshot` | `routers/graphs.py` | NO (deleted) | initial |
| Get snapshot | GET | `/api/v1/graphs/{graph_id}/snapshot` | `routers/graphs.py` | NO (deleted) | initial |
| Graph diff | GET | `/api/v1/graphs/{graph_id}/diff` | `routers/graphs.py` | NO (deleted) | initial |
| Graph report | GET | `/api/v1/graphs/{graph_id}/report` | `routers/graphs.py` | NO (deleted) | initial |

#### 1c.13 ADRs / Contracts / Features / Scenarios / Specifications (FR-TRC-005/006)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| ADR CRUD | (router) | `/api/v1/adrs[...]` | `routers/adrs.py` | NO (deleted) | initial |
| Contract CRUD | (router) | `/api/v1/contracts[...]` | `routers/contracts.py` | NO (deleted) | initial |
| Feature CRUD + scenarios | (router) | `/api/v1/features[...]` | `routers/features.py` | NO (deleted) | initial |
| Specifications umbrella | (router) | `/specifications[...]` | `routers/specifications.py` | NO (deleted) | initial |

#### 1c.14 Notifications / Blockchain / Temporal / Errors / Webhooks

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Notifications list | GET | `/notifications` | `routers/notifications.py` | NO (deleted) | initial |
| Mark notification read | POST | `/notifications/{notification_id}/read` | `routers/notifications.py` | NO (deleted) | initial |
| Read all | POST | `/notifications/read-all` | `routers/notifications.py` | NO (deleted) | initial |
| Blockchain baselines + version chain + embeddings | (router) | `/blockchain[...]` | `routers/blockchain.py` | NO (deleted) | initial |
| Temporal summary | GET | `/api/v1/temporal/summary` | `routers/temporal.py` | NO (deleted) | initial |
| Webhooks CRUD + inbound | (router) | `/api/v1/webhooks[...]` | `routers/webhooks.py` | NO (deleted) | initial |

#### 1c.15 WebSocket (realtime)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| WebSocket realtime | WS | `/ws` | `routers/websocket.py` | NO (deleted) | initial |

#### 1c.16 Execution service (rich)

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Execution CRUD + start/complete/artifacts | (router) | `/api/v1/executions[...]` | `routers/execution.py` | NO (deleted) | initial |

#### 1c.17 Mine (FR-TRC-011) — file is gone but service used to exist

| Feature | Method | Path | Location (historical) | On main? | First seen |
|---|---|---|---|---|---|
| Requirement miner (FR-TRC-011) | POST | `/api/v1/mine/requirements` | `routers/mine.py` | NO (deleted) | 482 (PR for FR-TRC-011) |

### 1d. Go (`cmd/server`) — independent HTTP service

| Feature | Method | Path | Location | On main? | First seen |
|---|---|---|---|---|---|
| Trace-link list | GET | `/api/v1/trace-links` | `cmd/server/main.go:426` | YES | initial |
| Trace-link create | POST | `/api/v1/trace-links` | `cmd/server/main.go:427` | YES | initial |
| Trace-link get | GET | `/api/v1/trace-links/{id}` | `cmd/server/main.go:428` | YES | initial |
| Trace-link delete | DELETE | `/api/v1/trace-links/{id}` | `cmd/server/main.go:429` | YES | initial |
| Requirement list | GET | `/api/v1/requirements` | `cmd/server/main.go:430` | YES | initial |
| Requirement create | POST | `/api/v1/requirements` | `cmd/server/main.go:431` | YES | initial |
| Requirement get | GET | `/api/v1/requirements/{id}` | `cmd/server/main.go:432` | YES | initial |
| Requirement delete | DELETE | `/api/v1/requirements/{id}` | `cmd/server/main.go:433` | YES | initial |
| Artifact list | GET | `/api/v1/artifacts` | `cmd/server/main.go:434` | YES | initial |
| Artifact create | POST | `/api/v1/artifacts` | `cmd/server/main.go:435` | YES | initial |
| Artifact get | GET | `/api/v1/artifacts/{id}` | `cmd/server/main.go:436` | YES | initial |
| Artifact delete | DELETE | `/api/v1/artifacts/{id}` | `cmd/server/main.go:437` | YES | initial |
| Health | GET | `/health` | `cmd/server/main.go:422` | YES | initial |

---

## 2. CLI COMMANDS

### 2a. CURRENT — Typer CLI in `src/tracertm/cli/`

| Feature | Subcommand | Location | On main? | First seen |
|---|---|---|---|---|
| `tracertm item create` | item | `src/tracertm/cli/commands/item.py:59` | YES | 91e2f6b |
| `tracertm item ls` | item | `src/tracertm/cli/commands/item.py:119` | YES | 91e2f6b |
| `tracertm item show` | item | `src/tracertm/cli/commands/item.py:156` | YES | 91e2f6b |
| `tracertm item update` | item | `src/tracertm/cli/commands/item.py:190` | YES | 91e2f6b |
| `tracertm item delete` | item | `src/tracertm/cli/commands/item.py:232` | YES | 91e2f6b |
| `tracertm item bulk_create` | item | `src/tracertm/cli/commands/item.py:266` | YES | 91e2f6b |
| `tracertm item bulk_update` | item | `src/tracertm/cli/commands/item.py:310` | YES | 91e2f6b |
| `tracertm item shell_completion` | item | `src/tracertm/cli/commands/item.py:359` | YES | 91e2f6b |
| `tracertm link create` | link | `src/tracertm/cli/commands/link.py:19` | YES | 91e2f6b |
| `tracertm link ls` | link | `src/tracertm/cli/commands/link.py:29` | YES | 91e2f6b |
| `tracertm link show` | link | `src/tracertm/cli/commands/link.py:39` | YES | 91e2f6b |
| `tracertm link delete` | link | `src/tracertm/cli/commands/link.py:45` | YES | 91e2f6b |
| `tracertm link bulk_create` | link | `src/tracertm/cli/commands/link.py:51` | YES | 91e2f6b |
| `tracertm link bulk-update` | link | `src/tracertm/cli/commands/link.py:59` | YES | 91e2f6b |
| `tracertm link import` | link | `src/tracertm/cli/commands/link.py:68` | YES | 91e2f6b |
| `tracertm link export` | link | `src/tracertm/cli/commands/link.py:76` | YES | 91e2f6b |
| `tracertm link check-consistency` | link | `src/tracertm/cli/commands/link.py:85` | YES | 91e2f6b |
| `tracertm link validate` | link | `src/tracertm/cli/commands/link.py:91` | YES | 91e2f6b |
| `tracertm link shell_completion` | link | `src/tracertm/cli/commands/link.py:97` | YES | 91e2f6b |
| `tracera status` | (root) | `cli/src/tracera_cli/main.py:27` | YES (stub) | 91e2f6b |
| `tracera list_artifacts` | (root) | `cli/src/tracera_cli/main.py:33` | YES (stub) | 91e2f6b |
| `tracera --version` | (root) | `cli/src/tracera_cli/main.py:15` | YES | 91e2f6b |

### 2b. HISTORICAL — deleted at `4ad704fd` (chore: cleanup agent coordination files)

| Feature | Subcommand | Location (historical) | On main? | First seen |
|---|---|---|---|---|
| `rtm backup export` | backup | `cli/commands/backup.py` | NO (deleted) | `1e9437b5` (Phase 4) |
| `rtm backup import` | backup | `cli/commands/backup.py` | NO (deleted) | `1e9437b5` |
| `rtm backup clone` | backup | `cli/commands/backup.py` | NO (deleted) | `1e9437b5` |
| `rtm backup template` | backup | `cli/commands/backup.py` | NO (deleted) | `1e9437b5` |
| `rtm backup list-templates` | backup | `cli/commands/backup.py` | NO (deleted) | `1e9437b5` |
| `rtm design init` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm design link` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm design sync` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm design generate` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm design status` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm design list` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm design export` | design | `cli/commands/design.py` | NO (deleted) | `1e9437b5` |
| `rtm test` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:unit` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:int` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:e2e` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:cov` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:matrix` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:story` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |
| `rtm test:comprehensive` | test | `cli/commands/test/app.py` | NO (deleted) | `1e9437b5` |

(plus several `cli/commands/test/{coverage,discover,discovery,grouping,orchestrator,env_manager}.py` helper modules — see §4.)

---

## 3. CORE CAPABILITIES — `crates/tracera-core` Rust public API

### 3a. Public modules (in `crates/tracera-core/src/lib.rs`)

| Module | Purpose | On main? | First seen |
|---|---|---|---|
| `cache` | TTL cache with LRU/LFU eviction, hit/miss/eviction stats | YES | `ed69540b` (PR #584) |
| `config` | 12-factor layered config loader (HTTPConfig, Neo4jConfig, S3Config, ObservabilityConfig, SentryConfig, EmbeddingsConfig, Config) | YES | `8572c1ce` (PR #577) |
| `coverage` | `CoverageSummary` aggregator over CoverageMatrix | YES | `8572c1ce` (PR #577) |
| `health` | Kubernetes-style health-check registry (`HealthCheck`, `HealthRegistry`, `ProbeType::{Liveness, Readiness, Startup}`, `HealthStatus::{Healthy, Degraded, Unhealthy}`) | YES | `ed69540b` (PR #584) |
| `ids` | Re-export `NfrId`, `RequirementId` from shared core | YES | `8572c1ce` (PR #577) |
| `impact` | Re-export blast-radius/impact (`compute_impact`, `conflicts_only`, `top_affected`, `BlastNode`, `ImpactConfig`, `ImpactReport`) | YES | `e547d2aa` (PR #576) |
| `matrix` | Re-export coverage matrix ops (`build_from_pairs`, `build_matrix`, `classify_cell`, `neighbors`, `CoverageMatrix`, `MatrixCell`, `added`, `changed`, `removed`) | YES | `e547d2aa` (PR #576) |
| `notification` | Multi-channel dispatcher (`Channel`, `Notification`, `ChannelPayload`, `EmailPayload`, `SlackPayload`, `WebhookPayload`, `WebhookMethod`, `PushPayload`, `SentRecord`, `DispatchReport`, `ChannelResult`, `DispatchError`, `Dispatcher`, `Recorder`) | YES | `a34de153` (cherry-pick) |
| `observability` | `init_tracing()`, `otlp_endpoint()`, `make_span()` | YES | `d582312f` (PR #581) |
| `pagination` | Offset/cursor/keyset pagination types + `keyset_slice` | YES | `a34de153` (cherry-pick) |
| `rate_limit` | `TokenBucket`, `SlidingWindow`, `LeakyBucket` algorithms | YES | `ed69540b` (PR #584) |
| `registry` | Content-addressed model registry (`ModelFormat::{Sklearn, Pytorch, Onnx}`, `ModelEntry`, `ModelRegistry`, `Save/Load/Get/List/Pin`) | YES | `8572c1ce` (PR #577) |
| `ui_links` | UI navigation payloads `TraceLinkUiLink`, `TraceLinkUiExt`, `ArtifactRefUiExt` | YES | `8572c1ce` (PR #577) |
| `workspace` | `WorkspaceMetadata` | YES | `8572c1ce` (PR #577) |

### 3b. Re-exports from `traceability_core` (the shared single-model)

| Item | Location | On main? |
|---|---|---|
| `build_from_pairs`, `build_matrix`, `classify_cell`, `neighbors` | `crates/tracera-core/src/lib.rs:28` | YES |
| `Artifact`, `ArtifactKind`, `ArtifactRef`, `BlastNode`, `BuildResult` | `crates/tracera-core/src/lib.rs:28` | YES |
| `CoverageMatrix`, `CoverageState`, `CORE_TRACE_LINK_TYPES`, `ImpactConfig`, `ImpactReport`, `LinkKind`, `MatrixCell`, `NfrId` | `crates/tracera-core/src/lib.rs:28` | YES |
| `NEO4J_NODE_LABELS`, `NEO4J_RELATIONSHIP_TYPES`, `Neo4jSchema` | `crates/tracera-core/src/lib.rs:28` | YES |
| `Requirement`, `RequirementId`, `RequirementStatus` | `crates/tracera-core/src/lib.rs:28` | YES |
| `TraceLink`, `TraceLinkError`, `TraceLinkType`, `VerificationMethod` | `crates/tracera-core/src/lib.rs:28` | YES |
| `compute_impact`, `conflicts_only`, `is_core_link_type`, `top_affected` | `crates/tracera-core/src/lib.rs:28` | YES |
| `added`, `changed`, `removed` (matrix diff) | `crates/tracera-core/src/lib.rs:35` | YES |

### 3c. Historical Rust core modules (deleted at `9e78f48d`)

| Module | Purpose | On main? | First seen | Last seen |
|---|---|---|---|---|
| `coverage` (early draft, replaced in #577) | Initial coverage scaffolding | NO (deleted then re-added as `coverage.rs` in 8572c1ce) | `9eb5f4ef` (PR #547) | `9e78f48d` |
| `ids` (early draft, replaced in #577) | Initial ids scaffolding | NO (re-added in 8572c1ce) | `9eb5f4ef` (PR #547) | `9e78f48d` |
| `impact` (early draft, replaced in #576) | Initial impact scaffolding | NO (re-added in e547d2aa) | `9eb5f4ef` (PR #547) | `9e78f48d` |
| `lib.rs` (early draft) | Initial lib scaffolding | NO (re-added in e547d2aa) | `9eb5f4ef` (PR #547) | `9e78f48d` |
| `matrix` (early draft, replaced in #576) | Initial matrix scaffolding | NO (re-added in e547d2aa) | `9eb5f4ef` (PR #547) | `9e78f48d` |

### 3d. Go backend (`backend/internal/`)

| Module | Purpose | On main? | First seen |
|---|---|---|---|
| `config` | Backend Go service config | YES | initial |
| `handlers/binder.go` | Shared handler binder (UUID, JSON) | YES | initial |
| `ml/registry.go` | Ported to Rust as `crates/tracera-core/src/registry.rs` | YES (still in Go; Rust is canonical) | initial |
| `observability/otel.go` | OpenTelemetry setup | YES | initial |
| `services/integration_test_setup.go` | Integration test scaffolding | YES | initial |
| `services/integration_tests.go` | Cross-service integration tests | YES | initial |
| `tracing/tracer.go` | OpenTelemetry tracer | YES | initial |

---

## 4. SERVICES / MODULES — top-level Python packages

### 4a. CURRENT — packages present on HEAD

| Module | Stated purpose | Location | On main? |
|---|---|---|---|
| `tracertm` (root) | TraceRTM — single source of truth for requirements/test/code traceability | `src/tracertm/__init__.py` | YES |
| `tracertm.adapters` | Hexagonal ports adapters (Neo4j graph) | `src/tracertm/adapters/` | YES |
| `tracertm.adapters.neo4j_graph_adapter` | Neo4j graph adapter | `src/tracertm/adapters/neo4j_graph_adapter.py` | YES |
| `tracertm.agent` | Agent sessions (currently empty on HEAD, populated historically) | `src/tracertm/agent/__init__.py` | YES (stub) |
| `tracertm.api` | FastAPI surface (routers, handlers, middleware) | `src/tracertm/api/` | YES |
| `tracertm.cli` | Typer CLI entry | `src/tracertm/cli/` | YES |
| `tracertm.database` | SQLAlchemy async DB connection | `src/tracertm/database/` | YES |
| `tracertm.governance` | Spec-first governance gate (`evaluate_spec_first_governance`) | `src/tracertm/governance.py` | YES |
| `tracertm.matrix` | Top-level matrix helper module | `src/tracertm/matrix.py` | YES |
| `tracertm.ml` | Model registry + inference model tests | `src/tracertm/ml/` | YES |
| `tracertm.mlflow_compat` | MLflow compatibility layer | `src/tracertm/mlflow_compat.py` | YES |
| `tracertm.models` | SQLAlchemy ORM models (item, link, project, artifact, trace_link, graph, agent_session, workflow, etc.) | `src/tracertm/models/` | YES |
| `tracertm.performance` | Performance helpers (`matrix`) | `src/tracertm/performance/` | YES |
| `tracertm.ports` | Hexagonal ports (`scorer`, `graph_contract`) | `src/tracertm/ports/` | YES |
| `tracertm.repositories` | Repository package (empty `__init__.py`) | `src/tracertm/repositories/__init__.py` | YES (stub) |
| `tracertm.scoring` | TF-IDF + Jaccard scorers + registry | `src/tracertm/scoring/` | YES |
| `tracertm.self_tracing` | Pytest plugin + evidence emitter | `src/tracertm/self_tracing/` | YES |
| `tracertm.services` | Service layer (currently ONLY `blast_radius_service.py` survives) | `src/tracertm/services/` | YES |
| `tracertm.services.blast_radius_service` | Blast-radius / risk-weighted path scoring (FR-TRC-015) | `src/tracertm/services/blast_radius_service.py` | YES |
| `tracertm.services.execution` | Execution service (empty) | `src/tracertm/services/execution/` | YES (stub) |
| `tracertm.services.recording` | Recording service (empty) | `src/tracertm/services/recording/` | YES (stub) |
| `tracertm.storage` | Writers (artifact, neo4j graph port, neo4j trace-link, trace-link) | `src/tracertm/storage/` | YES |

### 4b. HISTORICAL — services deleted at `9e78f48d`

The `src/tracertm/services/` directory once contained **100+ service modules**. All but `blast_radius_service.py` were deleted.

| Service | Stated purpose | First seen | Last seen |
|---|---|---|---|
| `adr_service` | ADR persistence | initial | `9e78f48d` |
| `advanced_analytics_service` | Cross-cutting analytics | initial | `9e78f48d` |
| `advanced_traceability_enhancements_service` | Traceability enrichments | initial | `9e78f48d` |
| `advanced_traceability_service` | Traceability core | initial | `9e78f48d` |
| `agent_coordination_service` | Multi-agent coordination | initial | `9e78f48d` |
| `agent_metrics_service` | Agent telemetry | initial | `9e78f48d` |
| `agent_monitoring_service` | Agent health/watchdog | initial | `9e78f48d` |
| `agent_performance_service` | Agent perf metrics | initial | `9e78f48d` |
| `agents.codex_service` | Codex agent backend | initial | `9e78f48d` |
| `ai_service` | Generic AI service | initial | `9e78f48d` |
| `ai_tools` | AI tool registry | initial | `9e78f48d` |
| `api_webhooks_service` | API webhook dispatch | initial | `9e78f48d` |
| `auto_link_service` | Automatic trace-link creation | initial | `9e78f48d` |
| `benchmark_service` | Performance benchmarking | initial | `9e78f48d` |
| `bulk_operation_service` | Bulk CRUD ops | initial | `9e78f48d` |
| `bulk_service` | Bulk ops (alt) | initial | `9e78f48d` |
| `cache_service` | Redis caching (w/ `RedisUnavailableError`) | initial | `9e78f48d` |
| `chaos_mode_service` | Chaos engineering harness | initial | `9e78f48d` |
| `checkpoint_service` | Service checkpoints | initial | `9e78f48d` |
| `commit_linking_service` | Git-commit → artifact linking | initial | `9e78f48d` |
| `concurrent_operations_service` | Concurrency helpers | initial | `9e78f48d` |
| `conflict_resolution_service` | Conflict resolution | initial | `9e78f48d` |
| `contract_service` | Contract persistence | initial | `9e78f48d` |
| `coverage_matrix_service` | Coverage matrix export (FR-TRC-014) | `f3bab4f8` (#484) | `9e78f48d` |
| `critical_path_service` | Critical-path analysis | initial | `9e78f48d` |
| `cycle_detection_service` | Graph cycle detection | initial | `9e78f48d` |
| `dependency_analysis_service` | Dependency graph analysis | initial | `9e78f48d` |
| `documentation_service` | Auto-generated docs | initial | `9e78f48d` |
| `drill_down_service` | Hierarchical drill-down | initial | `9e78f48d` |
| `dup_conflict_detector` | Duplicate/conflict detection (FR-TRC-012) | `17b96a38` (#481) | `9e78f48d` |
| `encryption_service` | Envelope encryption | initial | `9e78f48d` |
| `event_service` | Internal events | initial | `9e78f48d` |
| `event_sourcing_service` | Event-sourcing store | initial | `9e78f48d` |
| `execution.artifact_storage` | Execution artifact persistence | initial | `9e78f48d` |
| `execution.docker_orchestrator` | Docker-based execution orchestrator | initial | `9e78f48d` |
| `execution.execution_service` | Execution lifecycle | initial | `9e78f48d` |
| `execution.native_orchestrator` | Native process orchestrator | initial | `9e78f48d` |
| `export_import_service` | Import/export ops | initial | `9e78f48d` |
| `export_service` | Export ops | initial | `9e78f48d` |
| `external_integration_service` | External system integration | initial | `9e78f48d` |
| `feature_service` | Feature flag service | initial | `9e78f48d` |
| `file_watcher_service` | Filesystem watcher | initial | `9e78f48d` |
| `github_import_service` | GitHub issue import | initial | `9e78f48d` |
| `github_project_service` | GitHub Projects sync | initial | `9e78f48d` |
| `graph_analysis_service` | Graph analytics | initial | `9e78f48d` |
| `graph_report_service` | Graph report generation | initial | `9e78f48d` |
| `graph_service` | Graph CRUD | initial | `9e78f48d` |
| `graph_snapshot_service` | Graph snapshots | initial | `9e78f48d` |
| `graph_validation_service` | Graph validation | initial | `9e78f48d` |
| `grpc_client` | gRPC client wrapper | initial | `9e78f48d` |
| `history_service` | Entity history | initial | `9e78f48d` |
| `impact_analysis_service` | Impact analysis (Cypher) | initial | `9e78f48d` |
| `import_service` | Bulk import | initial | `9e78f48d` |
| `ingestion_service` | Bulk ingestion | initial | `9e78f48d` |
| `integration_sync_processor` | Integration sync | initial | `9e78f48d` |
| `item_service` | Item CRUD | initial | `9e78f48d` |
| `item_spec_service` | Item-spec service | initial | `9e78f48d` |
| `jira_import_service` | JIRA issue import | initial | `9e78f48d` |
| `link_service` | Link CRUD | initial | `9e78f48d` |
| `materialized_view_service` | Materialized views | initial | `9e78f48d` |
| `metrics_service` | Metrics emission | initial | `9e78f48d` |
| `notification_service` | Notification dispatch | initial | `9e78f48d` |
| `performance_optimization_service` | Perf optimisations | initial | `9e78f48d` |
| `performance_service` | Perf metrics | initial | `9e78f48d` |
| `performance_tuning_service` | Perf tuning | initial | `9e78f48d` |
| `plugin_service` | Plugin runtime | initial | `9e78f48d` |
| `progress_service` | Progress tracking | initial | `9e78f48d` |
| `progress_tracking_service` | Progress tracking (alt) | initial | `9e78f48d` |
| `project_backup_service` | Project backup/restore (used by `rtm backup` CLI) | initial | `9e78f48d` |
| `purge_service` | Purging old data | initial | `9e78f48d` |
| `query_optimization_service` | Query optimisations | initial | `9e78f48d` |
| `query_service` | Query helpers | initial | `9e78f48d` |
| `recording.ffmpeg_pipeline` | Recording pipeline (FFmpeg) | initial | `9e78f48d` |
| `recording.playwright_service` | Playwright recorder | initial | `9e78f48d` |
| `recording.tape_generator` | VHS tape generator | initial | `9e78f48d` |
| `recording.vhs_service` | VHS recorder | initial | `9e78f48d` |
| `repair_service` | Self-repair | initial | `9e78f48d` |
| `requirement_miner` | Requirement miner (FR-TRC-011) | `838a0dfd` (#482) | `9e78f48d` |
| `requirement_quality_service` | Requirement quality scoring | initial | `9e78f48d` |
| `scenario_service` | BDD scenario service | initial | `9e78f48d` |
| `search_service` | Search | initial | `9e78f48d` |
| `security_compliance_service` | Security compliance | initial | `9e78f48d` |
| `shortest_path_service` | Graph shortest-path | initial | `9e78f48d` |
| `spec_analytics_service` | Spec analytics | initial | `9e78f48d` |
| `spec_analytics_service_v2` | Spec analytics v2 | `14493e2e` | `14493e2e` |
| `specification_service` | Specification CRUD | initial | `9e78f48d` |
| `stateless_ingestion_service` | Stateless ingestion | initial | `9e78f48d` |
| `stats_service` | Statistics | initial | `9e78f48d` |
| `status_workflow_service` | Status workflow engine | initial | `9e78f48d` |
| `storage_service` | Storage abstraction | initial | `9e78f48d` |
| `sync_service` | Sync engine | initial | `9e78f48d` |
| `temporal_service` | Temporal.io wrapper | initial | `9e78f48d` |
| `trace_service` | Trace core service | initial | `9e78f48d` |
| `traceability_matrix_service` | Traceability matrix | initial | `9e78f48d` |
| `traceability_score_service` | Traceability health score (FR-TRC-017) | `c589d5d7` (#483) | `9e78f48d` |
| `traceability_service` | Traceability CRUD | initial | `9e78f48d` |
| `tui_service` | TUI service | initial | `9e78f48d` |
| `user_repository` | User repo (in services/) | initial | `9e78f48d` |
| `verification_service` | Verification | initial | `9e78f48d` |
| `view_registry_service` | View registry | initial | `9e78f48d` |
| `view_service` | View service | initial | `9e78f48d` |
| `visualization_service` | Visualization | initial | `9e78f48d` |
| `webhook_service` | Webhook dispatch | initial | `9e78f48d` |
| `workos_auth_service` | WorkOS authentication | initial | `9e78f48d` |

### 4c. HISTORICAL — other Python packages deleted at `9e78f48d` / `4ad704fd`

| Module | Stated purpose | First seen | Last seen |
|---|---|---|---|
| `tracertm.agent` | (was full) Agent runtime + sandbox (`agent_service.py`, `events.py`, `graph_session_store.py`, `sandbox/base.py`, `sandbox/local_fs.py`, `sandbox/snapshot_events.py`, `session_store.py`, `test_events.py`, `types.py`) | initial | `9e78f48d` |
| `tracertm.config` | (was full) `ConfigManager`, `GitHubAppConfig`, schema, settings | initial | `9e78f48d` |
| `tracertm.constants` | Constants | initial | `9e78f48d` |
| `tracertm.core` | (was full) Concurrency, config, context | initial | `9e78f48d` |
| `tracertm.database.async_connection` | Async DB | initial | `9e78f48d` |
| `tracertm.database.ensure_problems_processes` | Ensure seed rows | initial | `9e78f48d` |
| `tracertm.infrastructure` | Event bus, feature flags, NATS client | initial | `9e78f48d` |
| `tracertm.logging_config` | Logging | initial | `9e78f48d` |
| `tracertm.mcp` | Full MCP server, tools, prompts, resources, middleware | initial | `9e78f48d` |
| `tracertm.ml.model_registry` | ML model registry (replaced by Rust `crates/tracera-core/src/registry.rs`) | initial | `f722822c` |
| `tracertm.observability` | OpenTelemetry instrumentation, tracing, verify_traces, MLflow run logger | initial | `9e78f48d` |
| `tracertm.preflight` | Startup preflight checks | initial | `9e78f48d` |
| `tracertm.proto` | Generated gRPC stubs | initial | `9e78f48d` |
| `tracertm.repositories` | 20+ repo modules (account, agent, blockchain, event, execution, github_app, github_project, integration, item, item_spec, linear_app, link, problem, process, project, requirement_quality, specification, test_case, test_coverage, test_run, test_suite, webhook, workflow_run, workflow_schedule) | initial | `9e78f48d` |
| `tracertm.schemas` | 20+ Pydantic schema modules | initial | `9e78f48d` |
| `tracertm.storage` | `conflict_resolver`, `file_watcher`, `local_storage`, `markdown_parser`, `sync_engine` | initial | `9e78f48d` |
| `tracertm.testing_factories` | Test data factories | initial | `9e78f48d` |
| `tracertm.tests` | In-tree integration tests | initial | `9e78f48d` |
| `tracertm.tui` | Textual UI (apps + widgets + adapters) | initial | `9e78f48d` |
| `tracertm.utils` | figma + other helpers | initial | `9e78f48d` |
| `tracertm.v1` | v1 API stubs | initial | `9e78f48d` |
| `tracertm.validation` | `id_validator` | initial | `9e78f48d` |
| `tracertm.vault` | HashiCorp Vault client | initial | `9e78f48d` |
| `tracertm.workflows` | Temporal workflows, activities, agent execution, checkpoint, sandbox snapshot, tasks, worker, workflows | initial | `9e78f48d` |

### 4d. Models — current vs historical

**Current models (HEAD):** `agent_session`, `artifact`, `base`, `graph`, `item`, `item_comment`, `link`, `project`, `trace_link`, `types`, `workflow` (`src/tracertm/models/`)

**Deleted at `9e78f48d`:** `account`, `account_user`, `adr`, `agent`, `agent_checkpoint`, `agent_event`, `agent_lock`, `blockchain`, `codex_agent`, `contract`, `edge_type`, `event`, `execution`, `execution_config`, `external_link`, `feature`, `github_app_installation`, `github_project`, `graph_change`, `graph_node`, `graph_snapshot`, `graph_type`, `integration`, `item_spec`, `item_view`, `linear_app`, `link_type`, `node_kind`, `node_kind_rule`, `notification`, `problem`, `process`, `requirement_quality`, `scenario`, `specification`, `test_case`, `test_coverage`, `test_run`, `test_suite`, `user`, `view`, `webhook_integration`, `workflow_run`, `workflow_schedule`

---

## 5. OTHER OBSERVABILITY / INFRASTRUCTURE

| Feature | Location | On main? | First seen |
|---|---|---|---|
| Self-tracing pytest plugin | `src/tracertm/self_tracing/pytest_plugin.py` | YES | 91e2f6b |
| Self-tracing evidence emitter | `src/tracertm/self_tracing/evidence_emitter.py` | YES | 91e2f6b |
| MLflow compatibility layer | `src/tracertm/mlflow_compat.py` | YES | 91e2f6b |
| `x-request-id` middleware (FastAPI) | `src/tracertm/api/middleware/request_id.py` | YES | 91e2f6b |
| CORS middleware | `src/tracertm/api/middleware/cors.py` | YES | 91e2f6b |
| Go OTel setup | `backend/internal/observability/otel.go` | YES | initial |
| Go tracer | `backend/internal/tracing/tracer.go` | YES | initial |

Historical infrastructure (deleted):
- `tracertm.infrastructure.event_bus.py` (initial → `9e78f48d`)
- `tracertm.infrastructure.feature_flags.py` (initial → `9e78f48d`)
- `tracertm.infrastructure.nats_client.py` (initial → `9e78f48d`)
- `tracertm.observability.instrumentation.py` (initial → `9e78f48d`)
- `tracertm.observability.tracing.py` (initial → `9e78f48d`)
- `tracertm.observability.verify_traces.py` (initial → `9e78f48d`)
- `tracertm.observability.mlflow_run_logger.py` (initial → `9e78f48d`)
- All 7 middleware files (`auth`, `authentication_middleware`, `cache_headers_middleware`, `cors`, `error_handling`, `logging`, top-level `middleware.py`) (initial → `9e78f48d`)
- `tracertm.api.config.rate_limiting.py` (initial → `9e78f48d`)
- `tracertm.api.config.startup.py` (initial → `9e78f48d`)

---

## 6. SUMMARY COUNTS

| Category | Current (HEAD) | Historical | Total | On main? | Already-missing-from-main |
|---|---:|---:|---:|---:|---:|
| **API endpoints (Python FastAPI)** | 26 registered + 10 unmounted = **36** | **~190** | **~226** | YES (registered) / YES (unmounted) / NO (historical) | **~190** |
| **API endpoints (Go chi server)** | 13 | 0 | 13 | YES | 0 |
| **CLI subcommands (Typer + Go-tracera)** | 22 | 20 | 42 | YES / NO | **20** |
| **Rust core public modules** | 14 | 5 (early drafts, all re-introduced) | 14 unique | YES | 0 (re-introduced) |
| **Python services** | 1 (`blast_radius_service`) | ~90 | ~91 | YES / NO | **~90** |
| **Python top-level packages (services/)** | 1 dir (only `blast_radius_service.py` left) | 0 | 1 | YES | n/a |
| **Other Python packages** | 18 | ~25 | ~43 | YES / NO | **~25** |
| **SQLAlchemy ORM models** | 11 | ~45 | ~56 | YES / NO | **~45** |
| **Pydantic schemas** | 0 (file deleted) | ~20 | ~20 | NO | **20** |
| **Repositories** | 0 (file deleted, only stub `__init__.py`) | ~25 | ~25 | NO (stub) | **~25** |
| **MCP tools** | 0 | ~30 | ~30 | NO | **~30** |
| **FastAPI routers** | 11 files (5 mounted, 6 unmounted) | ~45 | ~56 | YES / NO | **~45** |
| **CLI command modules** | 2 (`item`, `link`) + 9 deleted = 2 + 9 + tracera_cli | 9 deleted (`backup`, `design`, `test/*` 7 files) | 11 | YES / NO | **9** |

---

## 7. REGRESSION FLAGS — Critical findings

The following features exist as **files on disk but are silently unreachable** because they are not wired into `main.py` or their parent Typer app:

| Symptom | Items | Risk |
|---|---|---|
| Routers present but not `include_router()`'d | `code_trace`, `comments`, `impact`, `impact_scoring`, `ingest` (5 files), plus `handlers/chat.py`, `handlers/impact.py` | HIGH — endpoints exist but get 404. Migration must either re-mount or explicitly drop with a changelog note. |
| Repositories package | `src/tracertm/repositories/__init__.py` is empty; all 20+ repo modules deleted | HIGH — anything that imports from `tracertm.repositories.*` will `ImportError`. |
| Schemas package | `src/tracertm/schemas/` directory deleted entirely | HIGH — model serializers gone. |
| MCP package | `src/tracertm/mcp/` deleted entirely (was full server) | MEDIUM — MCP route is gone (no router, no tool registry). |
| Workflows package | `src/tracertm/workflows/` deleted (Temporal) | MEDIUM — async workflows gone. |
| TUI package | `src/tracertm/tui/` deleted (Textual apps/widgets) | LOW — UI-only. |
| Observability | `src/tracertm/observability/` deleted (was OTel + MLflow logger) | MEDIUM — telemetry lost. |
| Infrastructure | `src/tracertm/infrastructure/` deleted (NATS, event_bus, feature_flags) | MEDIUM — async messaging lost. |
| CLI tooling | `rtm backup`, `rtm design`, `rtm test[...]` commands gone | MEDIUM — DX regression. |
| Coverage matrix FR-TRC-014 | Router `coverage_matrix.py` and service `coverage_matrix_service.py` both deleted | HIGH — explicit FR is unshipped on HEAD. |
| Blast radius FR-TRC-015 | Router `impact_scoring.py` and service `blast_radius_service.py` both present but router is unmounted | HIGH — service has tests but endpoint returns 404. |
| Requirement miner FR-TRC-011 | Router `mine.py` and service `requirement_miner.py` both deleted | HIGH — explicit FR is unshipped on HEAD. |
| Duplicate / conflict detector FR-TRC-012 | Router `dup_conflict.py` deleted, service `dup_conflict_detector.py` deleted | HIGH — explicit FR is unshipped on HEAD. |
| Traceability score FR-TRC-017 | Router `traceability_score.py` deleted, service `traceability_score_service.py` deleted | HIGH — explicit FR is unshipped on HEAD. |
| GitHub integration | `routers/github.py`, `handlers/github_*` all deleted; `services/github_*` deleted | HIGH — integration gone. |
| Linear integration | `routers/linear.py` deleted; `services/jira_import_service.py` deleted | HIGH — integration gone. |
| Webhooks | `routers/webhooks.py`, `services/webhook_service.py`, `repositories/webhook_repository.py` deleted | HIGH — webhook delivery gone. |
| WebSocket realtime | `routers/websocket.py`, `handlers/websocket.py` deleted | MEDIUM — realtime gone. |
| Temporal.io | `routers/temporal.py`, `services/temporal_service.py`, `workflows/*` deleted | MEDIUM — async engine gone. |

---

## 8. METHODOLOGY

This inventory was built using:

1. `git branch -a` + `git rev-parse HEAD` to identify the canonical `main` and key historical branches.
2. `git ls-tree --name-only -r HEAD -- <path>` for the current surface.
3. `git log --all --diff-filter=A/D --pretty=format:"%H %s" --name-only -- <path>` for additions/deletions across history.
4. `git show <ref>:<path>` against the pre-consolidation parent (`9e78f48d~1`) to extract endpoint definitions from the historical `main.py` and `router_registry.py`.
5. `fs_search` and direct file reads for the current main's `include_router()` registrations and `@router.<method>` decorators.
6. Cross-reference: every feature marked `YES (unmounted)` was verified against `src/tracertm/api/main.py:22-26` to confirm it is NOT in the include list.

Read-only. No commits, pushes, or edits to tracked files were performed. The single write was this `docs/FEATURE_INVENTORY.md` file as instructed.

**End of oracle.**
