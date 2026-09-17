# TEST_COVERAGE_MAP — Tracera 100% User-Story/Path Traceability

> Generated: 2026-09-12 · Source: `crates/tracera-server/src/main.rs` route table (206 routes) + `frontend/apps/web/e2e` (53 specs) + `frontend/apps/web/src` (247 vitest) + `audit/SCORECARD-FULL-2026-08-30.md`

## 1. Counts

| Layer | Count | Evidence |
|-------|-------|----------|
| API routes (`/.route("/api/v1/...")`) | 206 | `agents/sandbox/routes.txt:1-206` |
| Playwright e2e specs | 53 | `frontend/apps/web/e2e/*.spec.ts` |
| Vitest unit specs (src) | 247 | `frontend/apps/web/src/**/*.test.{ts,tsx}` |
| Rust integration (tracera-server) | 110+ | `cargo test --workspace --lib` (prior: 110 passed) |

## 2. Route Domains (206 routes)

| Domain | Routes | Example |
|--------|--------|---------|
| Auth/WorkOS/CSRF | 6 | `/api/v1/auth/login`, `/me`, `/verify`, `/csrf-token`, `/auth/workos/*` |
| AI/Agent | 7 | `/ai/analyze`, `/ai/stream-chat`, `/agents/*`, `/distributed/tasks/*` |
| Graph/SWEE | 30 | `/graph/nodes`, `/edges`, `/neighbors/{id}`, `/ancestors/{id}`, `/analysis/*`, `/full` |
| SDLC-PM | 32 | `/projects`, `/sprints`, `/stories`, `/teams`, `/trace_links`, `/problems` |
| Evidence/Docs/Codex/Specs | 18 | `/evidence`, `/docs`, `/codex/*`, `/spec-check` |
| Execution/Journeys | 15 | `/executions`, `/journeys/*`, `/imports`, `/mutations` |
| Trust/Equivalences | 8 | `/equivalences/*`, `/components/*` |
| Meta/Health | 8 | `/health`, `/readyz`, `/metrics`, `/version`, `/graph/cache/invalidate` |
| **Total** | **206** | |

## 3. E2E Coverage (Playwright, 53 specs)

Heuristic: filename keyword vs route first-segment. 38/53 specs map 1:1; 15 are cross-cutting (a11y, perf, visual, critical-path, bulk-ops).

| Spec file | Domain covered | Paths exercised |
|-----------|----------------|-----------------|
| `auth*.spec.ts` (3) | Auth | login/logout/me/refresh/verify + WorkOS authorize/callback |
| `dashboard*.spec.ts` (5) | Dashboard | summary/items/metrics + live-data (seeded prod) |
| `graph*.spec.ts` (4) | Graph/SWEE | nodes/edges/neighbors/ancestors/descendants/full/traverse/topo-sort/cycles/communities |
| `agents.spec.ts` | AI/Agent | distributed/agents/tasks/queues/locks |
| `equivalence.spec.ts` | Trust | equivalences/*, confirm/reject/batch |
| `import-export.spec.ts` | Execution | imports/mutations/items/bulk-update |
| `component-library.spec.ts` | Components | libraries/components/tokens |
| `critical-path.spec.ts` | E2E journey | projects→sprints→stories→trace_links (happy path) |
| `bulk-operations.spec.ts` | SDLC-PM | items/bulk-update, stories bulk |
| `dimension-filters.spec.ts` | SDLC-PM | sprints/stories filtered by team/project |
| `edge-cases.spec.ts` | Negative | 401/403/404/422 on all domains |
| `accessibility.*`, `*.visual.*`, `*.perf.*` (6) | Cross-cutting | a11y, visual, perf on dashboard/graph |
| `example*.spec.ts` (4) | Template | baseline |
| `dashboard-live-data.spec.ts` | Live prod | dashboard summary against seeded Postgres (10 nodes, 6 edges) |

**Gap (heuristic, filename-only):** `ai/*`, `codex/*`, `docs/*`, `journeys/*`, `executions/*`, `events/*` have no dedicated spec filename match — covered via `graph`/`import-export` mocks. Recommend 6 new specs (see §6).

## 4. Vitest Coverage (247 specs, `src/`)

| Layer | Dir pattern | Count (est) | What it tests |
|-------|-------------|-------------|---------------|
| api-client | `src/api/**/*.test.ts` | ~38 | `client-core`, `auth-api`, `graph-api`, `projects-api`, `sprints-api`, CSRF header injection, retry, 401 refresh |
| mcp | `src/mcp/**/*.test.ts` | ~12 | `tracera-mcp` tool wrappers (read/write/navigate/propose), rmcp transport mock |
| db/store | `src/lib/preflight.test.ts`, `src/stores/*.test.ts` | ~18 | preflight probe, authStore, dashboardStore, graphStore (seeded data → summary) |
| ui/lib | `src/lib/**/*.test.ts` | ~45 | route-guards, ndjson, gpu-compute, websocket, csrf, deployment-origin |
| ui/components | `src/components/**/*.test.tsx` | ~134 | 134 component unit tests (metric cards, filters, graph viz) |

All 247 run via `vitest --coverage` (v8). Current: `cargo test --workspace --lib` 110 passed covers Rust store/migrate layer.

## 5. Rust / DB / MCP / API Integration (cargo)

| Suite | File | Coverage |
|-------|------|----------|
| `tracera-server` lib | `crates/tracera-server/src/**/*` | store trait, migrations (postgres/sqlite), `pg_store.rs:1-800`, `sqlite_store.rs`, cache.rs, r2.rs, neo4j.rs — `cargo test` 110 passed (`audit/SCORECARD-FULL-2026-08-30.md:1`) |
| `tracera-mcp` | `crates/tracera-mcp/src/**/*.rs` | rmcp 3.2 tool_router (list_nodes/get_node/neighbors/create_node/create_edge/propose), DemoStore (Store trait impl), stdio transport |
| `tracera-workos` | `crates/tracera-workos/src/**/*.rs` | authKit hosted login, `from_env` mock path, HMAC webhook verify |
| `tracera-atlas` | `crates/tracera-atlas/src/**/*.rs` | engine/observability (RecordingSink), delegation |

## 6. Gaps to 100% — 6 new specs + 1 gate (required)

| # | Missing story | New spec | Layer |
|---|---------------|----------|-------|
| 1 | AI analyze/classify/infer/stream-chat/suggest | `ai.spec.ts` | e2e (mock anthropic) + vitest `src/api/ai.test.ts` |
| 2 | Codex entries/search + docs/search | `codex-docs.spec.ts` | e2e + vitest `src/api/codex.test.ts` |
| 3 | Journeys/steps/events/visualize + executions/logs/rerun | `journeys-executions.spec.ts` | e2e + Rust `tests/journeys.rs` |
| 4 | Events stream (NDJSON) + graph full/topo-sort/orphans | `events-graph-full.spec.ts` | e2e + vitest `src/lib/ndjson.test.ts` (already exists, expand) |
| 5 | Distributed queues/locks claim/fail + equivalences batch | `distributed.spec.ts` | e2e + Rust `tests/distributed.rs` |
| 6 | Admin users/audit + uploads/artifacts download | `admin-artifacts.spec.ts` | e2e + vitest `src/api/artifacts.test.ts` |

After these 6, heuristic uncovered → 0. True 100% = every route hit by at least one of: e2e happy + e2e error (401/422) + vitest unit + Rust integration.

## 7. Coverage Gate (CI)

Add `.github/workflows/ci-coverage-gate.yml:1-40`:
```yaml
name: ci-coverage-gate
on: [push, pull_request]
jobs:
  vitest:
    runs-on: ubuntu-latest
    steps: [checkout, bun install, bun run test:coverage -- --reporter=json]
    # fail if lines <95 or branches <90
  cargo:
    runs-on: ubuntu-latest
    steps: [checkout, cargo llvm-cov --workspace --lcov --output-path lcov.info]
    # fail if <95
```

## 8. Traceability Matrix (story → spec → code)

| User Story | API route(s) | E2E spec | Vitest | Rust |
|------------|--------------|----------|--------|------|
| As user I log in via WorkOS | `POST /auth/workos/authorize`, `GET /api/v1/auth/me` | `auth*.spec.ts` | `src/api/auth-api.test.ts` | `tracera-workos` |
| As user I view dashboard with seeded data | `GET /api/v1/dashboard/summary` | `dashboard-live-data.spec.ts:1` | `src/stores/dashboardStore.test.ts` | `pg_store.rs:dashboard` |
| As user I CRUD SWEE graph | `POST/GET /graph/nodes`, `/edges`, `/neighbors/{id}` | `graph.spec.ts` | `src/api/graph-api.test.ts` | `swee.rs:1`, `store.rs:1` |
| As agent I call MCP tools | `mcp-server stdio: list_nodes, create_node…` | `agents.spec.ts` | `src/mcp/*.test.ts` | `tracera-mcp/src/tools.rs:1` |
| As user I manage sprints/stories | `/sprints`, `/stories`, `/trace_links` | `critical-path.spec.ts`, `dimension-filters.spec.ts` | `src/api/sprints.test.ts` | `sqlite_store.rs` |

Extend per §6 for remaining 6 domains.

---
*Heuristic gap count is filename-only and over-counts; true coverage via `vitest --coverage` + `cargo llvm-cov` is the gate. This map is the source of truth for closing to 100%.*
