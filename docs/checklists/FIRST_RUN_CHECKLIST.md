# First Run Checklist

Use this checklist when cloning the repo or setting up a new environment so the app runs without 500s or missing-table errors.

## 1. Prerequisites

- [ ] **Go** 1.21+
- [ ] **Node.js** 18+ (Bun recommended for frontend)
- [ ] **Python** 3.11+
- [ ] **PostgreSQL** 14+ running and reachable
- [ ] **Redis** (optional for cache)
- [ ] **NATS** (optional for real-time)
- [ ] **Go tooling** (for lint/format): **gofumpt** + **golangci-lint** (`make install-tools` or `go install mvdan.cc/gofumpt@latest` and `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest`). Run `make lint-go` / `make go-format` from repo root.
- [ ] **Python tooling** (optional): **bandit** + **pip-audit** for security (`uv pip install -e ".[dev,test]"` includes them). Run `make lint-python`, `make type-check`, `make security-scan`.
- [ ] **Frontend tooling**: **oxlint**, **oxfmt**, **stylelint**, **Vitest** (bun install in frontend). Run `make lint-frontend`, `make typecheck-frontend`, or `make quality-frontend`. See [OXC Implementation Checklist](OXC_IMPLEMENTATION_CHECKLIST.md) and [Python and TypeScript Tooling](../research/python-and-typescript-tooling.md).

## 2. Environment

- [ ] Copy env template and set required variables:
  ```bash
  cp .env.example .env
  # Edit .env: set DATABASE_URL (or TRACERTM_DATABASE_URL) to your PostgreSQL connection string
  ```
- [ ] **DATABASE_URL** (or **TRACERTM_DATABASE_URL**) must point to the database used by both Go and Python backends (e.g. `postgresql://user:pass@localhost:5432/tracertm`).

## 3. Dependencies

- [ ] **Frontend**
  ```bash
  cd frontend && bun install
  ```
- [ ] **Go backend**
  ```bash
  cd backend && go mod download
  ```
- [ ] **Python**
  ```bash
  uv pip install -e ".[dev,test]"
  # or: pip install -e ".[dev,test]"
  ```

## 4. Database migrations

- [ ] **Go backend** (if your setup uses SQL migrations in `backend/migrations/`):
  - Apply per your Go backend docs (e.g. `go run ./cmd/migrate` or SQL files).
- [ ] **Python backend (required for Test Cases, Links, Graphs, Test Runs)**
  ```bash
  ./scripts/shell/run_python_migrations.sh
  ```
  Or manually:
  ```bash
  export DATABASE_URL="postgresql://user:pass@localhost:5432/tracertm"
  uv run alembic upgrade head
  ```
  Without this step, project pages that use the Python API (test cases, links, graphs, test runs) will return **500** with `relation "test_cases" does not exist` (or similar). See [TROUBLESHOOTING — 500 relation does not exist](/docs/guides/TROUBLESHOOTING.md#500-relation--does-not-exist-undefinedtableerror).

## 5. Pre-commit (optional)

- [ ] Install hooks so lint/format run before commit:
  ```bash
  pre-commit install
  pre-commit run --all-files
  ```

## 6. Start services

- [ ] **Unified (recommended)**
  ```bash
  rtm dev install   # one-time
  rtm dev start
  ```
- [ ] **Or individual**
  - Terminal 1: `cd backend && go run ./cmd/...` (see backend README)
  - Terminal 2: `cd frontend && bun run dev`
  - Terminal 3: Python API if used (see Python docs)

## 7. Verify

- [ ] Open frontend at http://localhost:4000 (only dev URL; do not use port 5173).
- [ ] Log in (WorkOS AuthKit or your auth flow).
- [ ] Open a project → **Test Cases** (or **Links**, **Graphs**). Page should load without "500" or "relation does not exist". If you see those, re-run [step 4](#4-database-migrations) (Python migrations).

## Quick reference

| Step | Command / action |
|------|------------------|
| Env | `cp .env.example .env` and set `DATABASE_URL` |
| Frontend deps | `cd frontend && bun install` |
| Go deps | `cd backend && go mod download` |
| Python deps | `uv pip install -e ".[dev,test]"` |
| Python DB | `./scripts/shell/run_python_migrations.sh` |
| Start | `rtm dev start` |

See also: [TROUBLESHOOTING](/docs/guides/TROUBLESHOOTING.md), [DEVELOPMENT_WORKFLOW](/docs/guides/DEVELOPMENT_WORKFLOW.md), [END_TO_END_PLAN](/docs/reports/END_TO_END_PLAN.md).
