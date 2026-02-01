# TracerTM End-to-End Plan

**Version:** 1.0  
**Date:** January 31, 2026  
**Scope:** From current state to a complete, production-ready system across frontend, backends, database, auth, tooling, and deployment.

---

## 1. Executive Summary

| Layer | Current state | End state |
|-------|----------------|-----------|
| **Frontend** | Many project views are a generic item registry; Test Cases / Test Runs / QA etc. are domain-optimized. Dashboard and routing work. | Key views (Features, API, Domain, Code, Database) domain-optimized; consistent UX, no dead 500s. |
| **Go backend** | APIs for items, links, projects, agents, graphs; auth (WorkOS) and protected routes. | Stable; migrations documented; no missing tables for Go-owned data. |
| **Python backend** | APIs for test_cases, links, graphs, test_runs, specs; Alembic migrations exist. | Migrations applied by default; no UndefinedTableError; asyncpg URL handled. |
| **Database** | Go uses SQL migrations (backend/internal/db); Python uses Alembic. Two DBs or shared PG possible. | Single source of truth for “run migrations”; Python migrations script in path; docs clear. |
| **Auth** | WorkOS AuthKit; 401 on /auth/me without token fixed (no unnecessary calls). | Login → dashboard → project views without spurious 401s; session refresh clear. |
| **Tooling** | Ruff, mypy, basedpyright (Python); golangci-lint (Go); Biome + TypeScript (frontend); pre-commit. | All green in CI; one-command lint/format/typecheck per repo. |
| **Docs & runbooks** | README, DEVELOPMENT_WORKFLOW, TROUBLESHOOTING, PROJECT_VIEWS_ARCHITECTURE. | End-to-end plan + “first run” checklist; 500/relation errors documented. |
| **Deploy** | Docker, K8s configs, staging/prod flows. | Deploy path documented; health checks and migrations in pipeline. |

**Phases:** 0 Foundation → 1 Data & APIs → 2 Domain Views → 3 UX & Polish → 4 Scale & Release.

---

## 2. Current State (Detailed)

### 2.1 Frontend

- **Project dashboard** (`/projects/:id`): ProjectDetailView — charts, stats, links. ✅
- **Generic views** (feature, api, domain, code, test, database, wireframe, architecture, infrastructure, dataflow, dependency, security, performance, monitoring, journey, configuration): All use `ItemsTableView` with a `view` prop (same table, different type). ✅ By design.
- **Domain-optimized views** (test-cases, test-runs, test-suites, coverage, qa-dashboard, problem, process, webhooks, graph, integrations, traceability, impact-analysis, workflows): Custom components. ✅
- **Auth:** WorkOS; validateSession/getCurrentUser only when token present (fix applied). ✅
- **API client:** Routes to Go vs Python by path; Bearer token and CSRF. ✅

### 2.2 Go Backend

- **Stack:** Echo, PostgreSQL (sqlc), Redis, NATS, optional Neo4j.
- **Auth:** AuthAdapterMiddleware; protected routes: GET /api/v1/auth/me, GET /api/v1/auth/user.
- **Lint:** golangci-lint in CI and pre-commit; `.golangci.yml` in backend. ✅

### 2.3 Python Backend

- **Stack:** FastAPI, SQLAlchemy (async), PostgreSQL (asyncpg), Alembic.
- **Tables:** test_cases, links, graphs, test_runs, specifications, etc. via Alembic.
- **Issue:** If Alembic has not been run, 500 UndefinedTableError (e.g. `relation "test_cases" does not exist`).
- **Fix in place:** `scripts/run_python_migrations.sh`; TROUBLESHOOTING doc; env.py converts asyncpg URL to psycopg2 for Alembic. ✅

### 2.4 Database

- **Go:** Migrations in `backend/migrations/` (e.g. SQL); applied separately from Python.
- **Python:** Alembic in `alembic/versions/`; requires `DATABASE_URL` or `TRACERTM_DATABASE_URL` and `uv run alembic upgrade head` (or script).

### 2.5 Tooling

- **Python:** Ruff, mypy, basedpyright, pre-commit, CI (quality.yml, ci.yml). ✅
- **Go:** golangci-lint, pre-commit gofmt + golangci-lint. ✅
- **Frontend:** Biome, TypeScript, oxlint; CI frontend-checks job. ✅

---

## 3. Gaps and Risks

| Gap | Impact | Mitigation |
|-----|--------|------------|
| Python DB not migrated | 500 on test-cases, links, graphs, test-runs. | Run `./scripts/run_python_migrations.sh`; document in first-run checklist. |
| Many views are generic table | UX feels “same” everywhere; no domain-specific workflows for Feature/API/Domain. | Phase 2: add domain views for priority types. |
| Two migration systems (Go SQL + Python Alembic) | Confusion on “which DB” and “run what when”. | Document in one place; consider single “migrate all” script later. |
| Stale or missing runbooks | New devs hit 500s or auth issues. | TROUBLESHOOTING + END_TO_END_PLAN + first-run checklist. |

---

## 4. End State Vision

- **User:** Can sign in, open a project, use Features / Test Cases / API / Domain etc. without 500s; key views feel domain-appropriate (not only a generic table).
- **Dev:** One-command setup (deps + DB migrations); clear docs for first run, troubleshooting, and deployment.
- **CI/CD:** Lint/format/typecheck and tests pass; deploy path runs migrations and health checks.

---

## 5. Phased Plan

### Phase 0: Foundation (Do First)

**Goal:** Environment and data layer reliable; no avoidable 500s or auth noise.

| # | Task | Owner | Deps | Complexity |
|---|------|-------|------|------------|
| 0.1 | Document “first run” checklist: install deps, set DATABASE_URL, run Go migrations (if any), run `./scripts/run_python_migrations.sh`, start services. | Docs | — | 1 |
| 0.2 | Ensure Python backend (or startup script) documents “run Alembic before first use” and link from README. | Docs | — | 1 |
| 0.3 | Verify auth flow E2E: login → dashboard → project → test-cases (no 401 on /auth/me when token present). | QA | 0.1 | 2 |
| 0.4 | Optional: Add a preflight or health endpoint that checks for Python tables (e.g. test_cases exists) and returns 503 with message “run Python migrations” if missing. | Backend-Py | — | 3 |

**Exit criteria:** New clone can follow checklist and open project + Test Cases without 500; auth flow works.

---

### Phase 1: Data & APIs (Stability)

**Goal:** All project pages that hit Python backend return 200 or handled errors (no UndefinedTableError).

| # | Task | Owner | Deps | Complexity |
|---|------|-------|------|------------|
| 1.1 | Run Python migrations in every relevant environment (dev, CI, staging) and document in deployment runbook. | DevOps / Docs | 0.1 | 2 |
| 1.2 | Align frontend API routing with backend: ensure /api/v1/test-cases, /api/v1/links, /api/v1/projects/:id/graphs etc. point to Python where implemented. | Frontend | — | 2 |
| 1.3 | Add minimal error boundaries or toasts for “Failed to load test cases” (and similar) with retry or link to troubleshooting. | Frontend | — | 2 |
| 1.4 | Optional: Shared “migrate all” script that runs Go migrations then Alembic (order and env documented). | Scripts | 0.1 | 3 |

**Exit criteria:** Test Cases, Links, Graphs, Test Runs pages load or show clear error (no raw 500 stack).

---

### Phase 2: Domain-Optimized Views (Product)

**Goal:** Prioritized project views are real domain UIs, not only the generic item registry.

| # | Task | Owner | Deps | Complexity |
|---|------|-------|------|------------|
| 2.1 | **Feature view:** Replace ItemsTableView for `feature` with a dedicated FeatureView (e.g. epic/feature hierarchy, status, create from template). Reuse existing route; switch in `projects.$projectId.views.$viewType.tsx`. | Frontend | 1.x | 5 |
| 2.2 | **API view:** Domain view for API contracts (list endpoints, method, path, summary). | Frontend | 1.x | 4 |
| 2.3 | **Domain view:** Domain model or concept view (entities, relationships). | Frontend | 1.x | 5 |
| 2.4 | **Code view:** Code/component view (file or module-level traceability). | Frontend | 1.x | 4 |
| 2.5 | **Database view:** Schema/table-level view. | Frontend | 1.x | 4 |
| 2.6 | Update sidebar/navigation labels if any view name changes. | Frontend | 2.1–2.5 | 1 |
| 2.7 | Document new components in PROJECT_VIEWS_ARCHITECTURE.md. | Docs | 2.1–2.5 | 1 |

**Exit criteria:** Features, API, Domain (and optionally Code, Database) have dedicated UIs; architecture doc updated.

**Priority:** 2.1 (Features) and 2.2 (API) first; then 2.3–2.5 by product priority.

---

### Phase 3: UX & Polish

**Goal:** Consistent loading, empty states, and error handling across project views.

| # | Task | Owner | Deps | Complexity |
|---|------|-------|------|------------|
| 3.1 | Standardize loading skeletons for list/table views (reuse or extend existing ChunkLoadingSkeleton). | Frontend | — | 2 |
| 3.2 | Standardize empty states: “No test cases yet”, “No features”, with primary CTA (e.g. “Create first test case”). | Frontend | — | 2 |
| 3.3 | Ensure 401/403 trigger redirect to login or clear message (already partially done; verify all key routes). | Frontend | — | 2 |
| 3.4 | Optional: Replace “Item Registry” label where it still appears with view-specific title (e.g. “Features”, “API Endpoints”) for views still using ItemsTableView. | Frontend | — | 1 |

**Exit criteria:** No blank content without loading or empty state; auth errors handled consistently.

---

### Phase 4: Scale & Release

**Goal:** Production-ready deployment and observability.

| # | Task | Owner | Deps | Complexity |
|---|------|-------|------|------------|
| 4.1 | Deployment runbook: build order, env vars, migration order (Go then Python or as-is), health checks. | DevOps / Docs | 1.1 | 3 |
| 4.2 | CI: Ensure migration step for Python (e.g. in CI or in Docker build) so staging/prod never start with missing tables. | DevOps | 1.1 | 3 |
| 4.3 | Health endpoints: Go /health, Python /health; gateway or K8s probe them. | Backend | — | 2 |
| 4.4 | Optional: Centralized error tracking (e.g. Sentry) for frontend and backends. | DevOps | — | 4 |
| 4.5 | Version and changelog: tag release, update CHANGELOG from plan phases. | Docs | All | 1 |

**Exit criteria:** One documented path to deploy with migrations and health checks; optional monitoring in place.

---

## 6. Dependencies (Summary)

```
Phase 0 (Foundation)
  ├── 0.1 First-run checklist
  ├── 0.2 Alembic doc in README
  ├── 0.3 Auth E2E verify
  └── 0.4 Optional preflight for Python tables

Phase 1 (Data & APIs) — depends on 0.1, 0.2
  ├── 1.1 Migrations in envs
  ├── 1.2 API routing alignment
  ├── 1.3 Error boundaries / toasts
  └── 1.4 Optional “migrate all” script

Phase 2 (Domain views) — depends on 1.x
  ├── 2.1 Feature view
  ├── 2.2 API view
  ├── 2.3 Domain view
  ├── 2.4 Code view
  ├── 2.5 Database view
  ├── 2.6 Sidebar/nav
  └── 2.7 Architecture doc

Phase 3 (UX & polish) — can run parallel to 2
  ├── 3.1 Loading skeletons
  ├── 3.2 Empty states
  ├── 3.3 Auth error handling
  └── 3.4 View-specific titles

Phase 4 (Scale & release) — depends on 1.1, 4.1
  ├── 4.1 Deployment runbook
  ├── 4.2 CI migration step
  ├── 4.3 Health checks
  ├── 4.4 Optional monitoring
  └── 4.5 Changelog / version
```

---

## 7. Success Criteria

| Phase | Success |
|-------|--------|
| 0 | New developer follows checklist and sees project + Test Cases without 500; login works. |
| 1 | Test Cases, Links, Graphs, Test Runs load or show clear error; no UndefinedTableError in normal use. |
| 2 | At least Features and API (and optionally Domain/Code/Database) have dedicated domain views. |
| 3 | Every project view has loading and empty state; auth errors redirect or message. |
| 4 | Deploy runbook exists; CI or deploy runs migrations; health checks used. |

---

## 8. File and Doc References

| Topic | Location |
|-------|----------|
| Project views (generic vs domain) | `docs/reference/PROJECT_VIEWS_ARCHITECTURE.md` |
| Python migrations | `scripts/run_python_migrations.sh`, `alembic/env.py`, `alembic/versions/` |
| 500 relation does not exist | `docs/guides/TROUBLESHOOTING.md` (§ 500 relation … does not exist) |
| Auth (no 401 on /auth/me) | Frontend: `api/client.ts`, `stores/authStore.ts`, `api/auth.ts`, `AuthKitSync.tsx` |
| Go lint | `backend/.golangci.yml`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml` |
| View switch (route) | `frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx` |
| Generic table | `frontend/apps/web/src/views/ItemsTableView.tsx` |

---

## 9. Next Steps

1. **Immediate:** Run Phase 0 (foundation) — first-run checklist and Alembic doc.
2. **Short-term:** Phase 1 — ensure Python migrations run everywhere; fix any remaining 500s.
3. **Product:** Phase 2 — prioritize Feature and API domain views; then Domain, Code, Database.
4. **Polish:** Phase 3 in parallel or after 2.1–2.2.
5. **Release:** Phase 4 when moving to staging/production.

This plan is the single end-to-end reference; update it as phases complete or scope changes.
