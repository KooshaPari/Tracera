---
audience: [developers, agents]
status: active
---

# Testing Strategy

## Recovery Validation

- `git status --short --branch`
- verify no root case-collision dirt after governance cleanup
- verify `backend/`, `src/tracertm/`, `frontend/`, and `config/` are present

## Infrastructure Validation

- process-compose config validation: passed with 25 configured processes
- preflight checks for PostgreSQL, NATS, Neo4j, Temporal, Alloy, Loki, Prometheus, Grafana
- explicit failure output for missing required dependencies
- Alloy readiness: `curl -fsS http://127.0.0.1:12345/-/ready`
- Alloy metrics: `curl -fsS http://127.0.0.1:12345/metrics`
- OTLP path: app -> Alloy `127.0.0.1:4319` -> Tempo/shared tracing storage
- Verified locally with official Grafana Alloy `v1.15.1` installed at
  `$HOME/.local/bin/grafana-alloy`; the wrapper reached `/-/ready` and opened
  `127.0.0.1:4319`.
- `bash -n scripts/shell/alloy-if-not-running.sh scripts/shell/check-loki-installation.sh
  scripts/shell/verify-apm-integration.sh`
- `scripts/shell/check-loki-installation.sh`
- `bash -n scripts/shell/verify-apm-integration.sh`
- repo search for `jaeger-if-not-running` and `readiness-jaeger` returned only the wrapper files
  themselves plus archived report docs
- Dragonfly default smoke: `bash scripts/shell/redis-if-not-running.sh`
- Redis fallback smoke: `REDIS_COMPAT_PROVIDER=redis bash scripts/shell/redis-if-not-running.sh`
- QA/test router extraction validation:
  - `python -m py_compile src/tracertm/api/main.py src/tracertm/api/routers/test_cases.py
    src/tracertm/api/routers/test_suites.py src/tracertm/api/routers/test_runs.py
    src/tracertm/api/routers/test_run_results.py src/tracertm/api/routers/coverage.py
    src/tracertm/api/routers/qa_metrics.py`
  - route-table check on the extracted routers confirmed the expected
    `/api/v1/test-cases`, `/api/v1/test-suites`, `/api/v1/test-runs`,
    `/api/v1/test-runs/{run_id}/results`, `/api/v1/coverage/matrix`, and
    `/api/v1/qa/metrics/summary` paths
  - full `main.py` import remains blocked by an unrelated syntax error in
    `src/tracertm/api/routers/webhooks.py`, so the route-table validation was
    performed against the extracted router modules directly
- Problem router extraction validation:
  - `python -m py_compile src/tracertm/api/main.py src/tracertm/api/routers/problems.py`
  - route-table check confirmed the expected problem paths and methods:
    `/api/v1/problems`, `/api/v1/problems/{problem_id}`, `/api/v1/problems/{problem_id}/activities`,
    `/api/v1/problems/{problem_id}/close`, `/api/v1/problems/{problem_id}/permanent-fix`,
    `/api/v1/problems/{problem_id}/rca`, `/api/v1/problems/{problem_id}/status`,
    `/api/v1/problems/{problem_id}/workaround`, and `/api/v1/projects/{project_id}/problems/stats`
  - `git diff --check` passed after the extraction

## Backend Validation

- Focused Go: `go test ./internal/nats ./internal/services` passed
- Go: `go test ./...`
- Go: `go build ./...`
- Python: `ruff check .`
- Python: `ty check src/`
- Python: targeted tests around traceability, workflows, NATS, storage, and preflight

## Frontend Validation

- `bun run build`
- TypeScript check
- graph smoke tests
- Sigma/WebGL performance tests for 10k nodes
- performance-mode smoke for 50k nodes

## Demo Validation

Each long-form guide should have a runnable script or checklist that proves:

- seed data was created
- trace graph renders
- requirement version changes are visible
- audit/history entries exist
- agent/session checkpoint flow works
- screenshots or recordings are generated where useful

## Auth Validation

For the public auth split, validate the mounted route table after wiring
`auth_public.py` so there is exactly one route source per path:

- `/api/v1/auth/me`
- `/api/v1/auth/logout`
- `/api/v1/auth/signup`
- `/api/v1/auth/login`
- `/api/v1/auth/device/code`
- `/api/v1/auth/device/token`
- `/api/v1/auth/device/complete`
