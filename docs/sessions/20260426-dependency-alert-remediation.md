# Dependency Alert Remediation Session - 2026-04-26

## Goal

Reduce live Tracera dependency alerts without letting the task become a broad
repo cleanup.

## SIZE-DEP: Keep Dependency Remediation Finishable

- **Cap:** one runtime/test dependency surface per PR unless alerts share the
  same lockfile.
- **Current size:** GitPython `uv.lock` hotfix is merged; CI Python compatibility
  is the next bounded task because the hotfix PR exposed workflow pins below the
  repository's `requires-python = ">=3.13"` contract.
- **Stop rule:** keep each PR to one dependency/runtime surface and leave broader
  CI, Go, frontend, and archive cleanup as explicit follow-up lanes.
- **Spillover:** create separate WBS items for Python lower-bound cleanup, Go
  Docker module investigation, frontend package bumps, and archive manifest
  quarantine.

## SIZE-CI-PYTHON-313: Python CI Compatibility

- **Scope:** PR-triggered Python workflow setup and local Python type-tool
  version alignment.
- **Reason:** `CI/CD Pipeline / Python Tests (3.12)` failed because workflows
  installed the project on Python 3.12 while `pyproject.toml` requires Python
  3.13 or newer.
- **Included:** `.github/workflows/ci.yml`, `quality.yml`, `tests.yml`,
  `pre-commit.yml`, `test-pyramid.yml`, `contracts.yml`, `chaos-tests.yml`,
  `architecture.yml`, `dependabot-auto-merge.yml`, `test-validation.yml`,
  `test.yml`, `ci-cd.yml`, and `[tool.ty.environment]`.
- **Excluded:** Go toolchain/race failures, old action-version upgrades,
  shellcheck cleanups, `requirements.txt` workflow migration, contract
  `scripts/.venv` repair, and archive dependency manifests.

## SIZE-CI-GO-TOOLCHAIN: Deferred Go CI Lane

- **Scope:** active Tracera Go workflow pins and toolchain ownership.
- **Current evidence:** the Go failure used Go 1.23 wrappers while logs resolved
  a Go 1.25.7 target, then failed golangci-lint/covdata/race-test steps.
- **Action:** align PR-triggered Go workflow setup to the backend `go 1.25.7`
  module contract, remove `GOTOOLCHAIN: local` overrides from Go test wrappers,
  and move the strict golangci-lint action to the current Go-1.25-capable line.
- **Included:** `ci.yml`, `go-tests.yml`, `test.yml`, `test-validation.yml`,
  `test-pyramid.yml`, `benchmarks.yml`, and `performance-regression.yml`.
- **Excluded:** Go race-test code failures, coverage artifact semantics, stale
  non-PR docs/schema/contract helper pins, and broader workflow action upgrades.

## Alert Buckets

| Bucket | Scope | Action |
|---|---|---|
| GitPython | `uv.lock` | Patch in this lane. |
| Other Python | `pyproject.toml`, `uv.lock` | Separate Python dependency cleanup lane. |
| Python CI | `.github/workflows/*.yml`, `pyproject.toml` | Align PR-triggered Python setup to 3.13. |
| Go Docker module | `backend/**/go.mod` | Defer until a published fixed module tag or replacement module path is confirmed. |
| Go CI toolchain | reusable workflow / Go wrappers | Separate toolchain lane. |
| Frontend npm | `frontend/**` | Separate frontend dependency lane. |
| Archived npm snapshots | `ARCHIVE/CONFIG/default/**/package.json` | Separate archive quarantine task. |

## SIZE-CI-PERF-REPORT-ARTIFACTS: Performance Report Guard

- **Scope:** `performance-regression.yml` report fan-in behavior only.
- **Reason:** after the Go toolchain fix, `Generate Performance Report` failed
  while downloading `smoke-test-results` even though the producing smoke job had
  failed before uploading that artifact.
- **Action:** run the report fan-in only when at least one performance producer
  succeeded, download artifacts only from successful producers, and only post the
  PR smoke summary comment when the smoke summary file exists.
- **Excluded:** fixing the underlying smoke/load runtime failures, k6 scenario
  behavior, backend startup, and report rendering semantics.

## SIZE-CI-PERF-PGVECTOR: Performance Database Image

- **Scope:** `performance-regression.yml` Postgres service images only.
- **Reason:** `Smoke Test - Quick Performance Check` failed during migrations
  because the hosted `postgres:17` image does not include the `vector` extension
  required by `backend/schema.sql`.
- **Action:** use `pgvector/pgvector:pg17` for smoke and load performance
  database services, matching the repository's existing pgvector test-compose
  pattern while preserving PostgreSQL 17.
- **Excluded:** backend migration redesign, making pgvector optional, k6 scenario
  behavior, and unrelated smoke/load runtime failures after migrations succeed.

## SIZE-CI-ALEMBIC-VERSION-WIDTH: Migration Revision Width

- **Scope:** Alembic revision table compatibility for existing long revision IDs.
- **Reason:** after the pgvector image fix, performance smoke migrations reached
  revision `030_enhance_item_specs_blockchain` and failed because Alembic's
  default `alembic_version.version_num VARCHAR(32)` cannot store that 35-character
  revision ID.
- **Action:** widen `alembic_version.version_num` to `VARCHAR(128)` at the start
  of revision 030 before Alembic updates the version table to that revision, and
  include `alembic/**` in the performance workflow path filters so migration
  changes exercise the smoke path.
- **Excluded:** renaming historical revision IDs, rebuilding the migration graph,
  and fixing downstream migration/runtime failures after revision 030.

## SIZE-CI-PERF-BACKEND-ENTRYPOINT: Performance Backend Build Target

- **Scope:** `performance-regression.yml` Go build target only.
- **Reason:** after migrations completed, smoke failed at
  `go build -o api ./cmd/api` because `backend/cmd/api` does not exist.
- **Action:** build the backend module root with `go build -o api .`, matching
  `backend/Taskfile.yml` and `backend/Dockerfile`.
- **Excluded:** startup dependency services, preflight policy, k6 auth/data
  behavior, and stale README command examples.

## SIZE-CI-PERF-RUNTIME-SERVICES: Performance Backend Startup Dependencies

- **Scope:** `performance-regression.yml` smoke/load backend startup services
  and CI-only preflight environment.
- **Reason:** after the backend entrypoint fix, smoke built the Go backend and
  then failed during startup preflight because CI only provided Postgres and
  Redis while the backend requires NATS, Neo4j, S3 endpoint/env, Temporal
  host/env, WorkOS env, and disabled tracing when no collector is present.
- **Action:** add NATS and Neo4j service containers, provide CI-safe WorkOS/S3/
  Temporal environment values, disable tracing, and use lightweight local TCP
  listeners for S3 and Temporal because current startup only preflights those
  endpoints and does not initialize real S3 or Temporal clients. Bind those
  placeholders through `127.0.0.1` and wait for them before launching the API so
  Go preflight does not race Python startup or resolve `localhost` to IPv6; keep
  Temporal in URL form (`tcp://127.0.0.1:7233`) so Go URL parsing accepts it.
- **Excluded:** changing backend preflight policy, adding real MinIO/Temporal
  stacks, auth-seeding k6 scenarios, frontend performance, and broader runtime
  compose consolidation.

## SIZE-CI-NOTIFICATIONS-RLS-MIGRATION: Notification Startup Schema Ownership

- **Scope:** Go backend notification startup schema checks and the Alembic
  notification expiration column.
- **Reason:** after the runtime service lane, performance smoke reached backend
  infrastructure initialization and failed because GORM tried to alter
  `notifications.user_id` from Alembic's `VARCHAR(255)` to `TEXT` while RLS
  policies depended on that column.
- **Action:** stop broad GORM `AutoMigrate` against an existing Alembic-owned
  `notifications` table, align Go notification GORM tags with Alembic types,
  add only the missing `expires_at` column/index additively, and add Alembic
  revision `060_add_notification_expiration` as the canonical schema owner for
  that column.
- **Excluded:** dropping/recreating RLS policies, changing notification policy
  semantics, broad GORM/Alembic ownership redesign, and k6 auth/data seeding.

## SIZE-CI-AGENT-TASKS-ALEMBIC: Agent Task Persistence Table

- **Scope:** Alembic ownership for the Go agent task queue persistence table.
- **Reason:** after the notification schema fix, performance smoke reached the
  infrastructure health loop and failed because `VerifyTaskBackendPersistence`
  inserts into `agent_tasks`, but the CI pre-start Alembic migration path did
  not create that table.
- **Action:** add Alembic revision `061_add_agent_tasks` mirroring the existing
  backend raw SQL migration for `agent_tasks` and its indexes so CI databases
  created by Alembic match the Go runtime's durable task queue expectations.
- **Excluded:** fixing older internal DB migration warnings, changing health
  check semantics, redesigning the task queue, and k6 scenario behavior.

## SIZE-CI-K6-CSRF-SMOKE: Performance k6 Auth Harness Drift

- **Scope:** k6 performance helper auth/session setup and smoke scenario
  project fixture creation.
- **Reason:** after the agent task table fix, performance smoke reached a live
  backend, `/health` returned OK, and k6 failed because the helper still called
  removed/stale auth endpoints (`/api/v1/auth/csrf`, `/api/v1/auth/login`).
  The backend now exposes `/api/v1/csrf-token`, returns `{ "token": ... }`,
  and removed password login in favor of AuthKit.
- **Action:** add CI `csrf-only` k6 auth mode that prepares CSRF headers/cookie
  without reintroducing password login, set required CI auth/CSRF environment
  values in the performance workflow, guard smoke iterations when session
  preparation fails, and create a real smoke project before item creation so
  item CRUD uses a valid UUID project ID.
- **Excluded:** re-adding password auth, mocking WorkOS in production code,
  changing protected route policy, and broad load/stress data-model cleanup.

## Validation Targets

```bash
uv lock --locked
uv run python -m compileall -q src
actionlint -shellcheck= -ignore 'the runner of ".*" action is too old' \
  -ignore 'input "webhook_url" is not defined' \
  -ignore '"needs" section should not be empty' .github/workflows/<changed>.yml
git diff --check
```
