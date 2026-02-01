# Temporal Implementation Plan

Implementation plan for full Temporal integration: inventory, config model, schedules, workers, API alignment, health, observability, and Hatchet cleanup.

---

## 1. Inventory and mapping

### 1.1 Current workflow endpoints (Python API)

| Endpoint | Method | Purpose | Temporal equivalent |
|---------|--------|---------|----------------------|
| `/api/v1/workflows/trigger` | POST | Trigger workflow by name + input | `Client.start_workflow()`; map `workflow_name` → workflow type |
| `/api/v1/workflows/graph-snapshot` | POST | Graph snapshot | `GraphSnapshotWorkflow` |
| `/api/v1/workflows/graph-validate` | POST | Graph validation | `GraphValidationWorkflow` |
| `/api/v1/workflows/graph-export` | POST | Graph export | `GraphExportWorkflow` |
| `/api/v1/workflows/graph-diff` | POST | Graph diff | `GraphDiffWorkflow` |
| `/api/v1/workflows/integrations-sync` | POST | Integration sync | `IntegrationSyncWorkflow` |
| `/api/v1/workflows/integrations-retry` | POST | Integration retry | `IntegrationRetryWorkflow` |
| `/api/v1/projects/{id}/workflows/runs` | GET | List runs (DB) | Keep; add optional sync from Temporal handles for status |
| `/api/v1/projects/{id}/workflows/schedules/bootstrap` | POST | Bootstrap schedules | Temporal Schedule API create; persist in DB |
| `/api/v1/projects/{id}/workflows/schedules` | GET | List schedules | Temporal Schedule list + DB metadata |
| `/api/v1/projects/{id}/workflows/schedules/{cron_id}` | DELETE | Delete schedule | Temporal Schedule delete + DB |

**Payload mapping (Hatchet-era → Temporal):**

- **Trigger:** `workflow_name` (e.g. `graph.snapshot`) + `input` (e.g. `project_id`, `graph_id`) → `Client.start_workflow(WorkflowType, id=..., task_queue=..., args=[...])`. Workflow ID: deterministic from `project_id` + workflow type + optional idempotency key.
- **Run status:** Today from DB (`workflow_runs` + `external_run_id`). Add optional fetch from Temporal handle by `workflow_id`/`run_id` for live status (RUNNING, COMPLETED, FAILED).

### 1.2 Python Temporal service and worker

- **Service:** `src/tracertm/services/temporal_service.py` — `TemporalService`, `TemporalSettings` (host, namespace, timeout, task_queue, ui_url). `start_workflow()`, `health_check()`. No schedule APIs yet.
- **Worker:** `src/tracertm/workflows/worker.py` — single task queue `tracertm-tasks`; workflows: IndexingWorkflow, AnalysisWorkflow, GraphSnapshotWorkflow, GraphValidationWorkflow, GraphExportWorkflow, GraphDiffWorkflow, IntegrationSyncWorkflow, IntegrationRetryWorkflow; activities from `activities.py`.
- **Workflows:** `src/tracertm/workflows/workflows.py` — each workflow uses `execute_activity` with timeouts and `RetryPolicy` (e.g. max 3 attempts, backoff). No schedule usage; no workflow-level idempotency key in trigger.

### 1.3 Go delegation client

- **Client:** `backend/internal/clients/workflow_client.go` — `WorkflowClient` delegates to Python: `POST /api/v1/workflows/trigger`, `GET /api/v1/workflows/runs/:runID`. No direct Temporal SDK in Go; all workflow execution via Python API.
- **Handler:** `backend/internal/handlers/workflow_handler.go` — TriggerWorkflow, GetWorkflowRun, CancelWorkflowRun (delegate to Python).
- **Note:** Go `TemporalService` / `TemporalHandler` are **version/branch domain** (VersionBranch, Version, MergeRequest), not Temporal.io. No change to that naming; only workflow orchestration is Temporal.io (in Python).

### 1.4 Hatchet-era → Temporal mapping

| Hatchet (legacy) | Temporal equivalent |
|------------------|----------------------|
| HatchetService.trigger_workflow(name, input) | TemporalService.start_workflow(workflow_type, workflow_id=?, task_queue=?, **args) |
| Hatchet run ID | Temporal WorkflowRun (workflow_id + run_id) |
| Hatchet task / worker | Temporal Worker + Activities on task queue |
| No schedules in Hatchet (or ad‑hoc) | Temporal Schedule API (create/list/delete) |
| HATCHET_API_URL, HATCHET_CLIENT_TOKEN | TEMPORAL_HOST, TEMPORAL_NAMESPACE (no token for dev server) |

---

## 2. Temporal configuration model and validation

### 2.1 Configuration model (env)

- **Required:** `TEMPORAL_HOST` (e.g. `127.0.0.1:7233`), `TEMPORAL_NAMESPACE` (e.g. `default`).
- **Optional:** `TEMPORAL_TASK_QUEUE` (default `tracertm-tasks`), `TEMPORAL_UI_URL`, `TEMPORAL_TIMEOUT`, TLS: `TEMPORAL_TLS`, `TEMPORAL_TLS_CERT`, `TEMPORAL_TLS_KEY` (for production).
- **Strict validation:** On startup (Python and Go), validate presence and format of required vars; validate host:port and namespace non-empty. Fail fast with clear error if invalid.

### 2.2 Preflight for server/namespace reachability

- **Python:** Already have `temporal-host` (TCP) and `temporal-namespace` (env) in preflight. Keep required; add optional **namespace reachability** check: connect client and verify namespace (e.g. describe namespace or simple RPC) so unreachable namespace fails preflight with clear message.
- **Go:** Already have `temporal-host` in preflight with poll/retry. Ensure same: TCP reachability first; optionally document “namespace check” if Go ever talks to Temporal directly.

---

## 3. Temporal schedule support

- **Implement in Python** using Temporal Schedule API:
  - **Create:** `Client.create_schedule()` — cron or interval, workflow type, args, policy (overlap, pause). Return schedule ID.
  - **List:** `Client.list_schedules()` (namespace or filter); map to project via schedule ID naming or search attributes (e.g. `project_id`).
  - **Delete:** `Client.get_schedule_handle(schedule_id).delete()`.
- **Persist schedule metadata in DB:** New table (e.g. `workflow_schedules`): `id`, `project_id`, `schedule_id` (Temporal), `workflow_type`, `cron_spec`/`interval`, `payload`, `created_at`, `created_by`. Use for UI filtering and audit; source of truth for “what schedules exist” is DB; Temporal is execution source of truth.
- **API:** Implement real logic in `/api/v1/projects/{id}/workflows/schedules/bootstrap` (create default schedules + DB rows), GET schedules (list from Temporal + join DB or list from DB and verify with Temporal), DELETE (Temporal delete + DB delete).

---

## 4. Workers, task queues, idempotency, retries, timeouts

- **Task queues:** Keep single queue `tracertm-tasks` for now; document. If needed later, add per-workflow-type queues (e.g. `graph-tasks`, `integration-tasks`) and wire in worker and client.
- **Per-workflow:** In `temporal_service.start_workflow()` and/or in workflow definitions:
  - **Idempotency:** Use deterministic `workflow_id` (e.g. `{workflow_type}-{project_id}-{input_hash}` or `{workflow_type}-{project_id}-{graph_id}`) so duplicate triggers are same workflow; document policy.
  - **Retry policy:** Already in workflows (e.g. `RetryPolicy(maximum_attempts=3, ...)`). Centralize in a small helper per workflow type if desired (e.g. `graph_retry_policy()`, `integration_retry_policy()`).
  - **Timeouts:** Already `start_to_close_timeout` per activity. Add workflow execution timeout where appropriate (`workflow.run` timeout).
- **Worker:** Ensure all workflow types and activities are registered; add any new workflows/schedules activities when schedule execution is implemented.

---

## 5. API and frontend alignment

- **Schedule management:** Expose create/list/delete in Python; Go can proxy to Python or frontend calls Python. Response types: schedule id, workflow type, cron/interval, status (active/paused), created_at; align with DB and Temporal.
- **Workflow run status:** Keep `GET /api/v1/projects/{id}/workflows/runs` (DB list). Add optional “refresh from Temporal” for a run (by `external_run_id` = Temporal workflow_id or run_id): call Temporal describe and update DB row + return. Frontend types: run id, workflow_name, status, started_at, completed_at, result/error; align with existing `WorkflowRun` and Temporal status enum.
- **Frontend:** Ensure types (schedule list item, workflow run item) match API; use Temporal statuses (RUNNING, COMPLETED, FAILED, etc.) in UI where applicable.

---

## 6. Health checks

- **Temporal service:** Python: already `TemporalService.health_check()` (connect + namespace). Expose in `/health` or `/api/v1/health` (e.g. `temporal: { status, host, namespace }`). Go: if Go has no direct Temporal client, health can report “workflow backend” by calling Python health or a small Python endpoint that returns Temporal status.
- **Worker heartbeat:** Worker process can expose a simple HTTP or file-based “last heartbeat” (e.g. worker writes timestamp every N seconds); health endpoint reads it. Alternatively, Temporal “worker health” is implicit (task queue polling); document that “no workflow progress” may indicate worker down.
- **Task queue:** Optional: list open workflows or poll task queue to ensure worker is processing; keep simple (e.g. “Temporal reachable + namespace OK” is enough for preflight; worker liveness separate).
- **Surface in Go/Python health:** Both backends’ health responses should include a `temporal` (or `workflows`) section: `{ status, namespace, task_queue, worker_last_seen? }`. Required: clear failure if Temporal is unreachable (per project stance).

---

## 7. Observability

- **Structured logs:** Include `workflow_id`, `run_id`, `workflow_type`, `project_id` in log records for workflow trigger, completion, and failure.
- **Trace correlation:** Use a shared trace ID (e.g. from request header) when triggering workflows and in activities; add to Temporal workflow/activity context so logs and traces link.
- **Metrics:** Emit (e.g. Prometheus): workflow_started_total, workflow_completed_total, workflow_failed_total, workflow_retries_total, activity_latency_seconds by workflow_type/activity. Optionally schedule_* counters.
- **Dashboards:** Grafana (or equivalent) for workflow counts, failures, retries, latency; optionally worker task queue depth.

---

## 8. Tests and local dev

- **Tests:** Unit tests for TemporalService (start_workflow, health_check) with mocked Temporal client; integration tests that start Temporal dev server, run worker, trigger workflow, assert DB and status. Same for schedule create/list/delete if implemented.
- **Local dev scripts:** Use existing `./scripts/start-services.sh temporal` (Temporal dev server + optional namespace). Add optional script or doc: create namespace if not `default`, create task queue if needed. Migration notes: “Start Temporal before Python/Go; set TEMPORAL_HOST=127.0.0.1:7233.”
- **Hatchet cleanup:** Remove or update remaining Hatchet references in docs and tests: replace Hatchet with Temporal in setup guides, health examples, and any test fixtures or docs that still mention Hatchet. Archive Hatchet service/worker files if still present; remove `hatchet-sdk` from dependencies. Track in a short “Hatchet removal checklist” (docs or CHANGELOG).

---

## 9. Implementation order (suggested)

1. **Config + preflight** — Strict validation and namespace reachability preflight (Python + Go).
2. **Schedule API** — Implement create/list/delete in Python with DB persistence; wire bootstrap and list/delete endpoints.
3. **Idempotency + retries/timeouts** — Deterministic workflow_id, centralize retry/timeout per workflow type.
4. **Health** — Temporal + optional worker heartbeat in Python/Go health endpoints.
5. **API alignment** — Run status refresh from Temporal; frontend types.
6. **Observability** — Logs, trace ID, metrics, dashboard.
7. **Tests + scripts** — Integration tests, local dev doc, Hatchet removal.

---

## References

- Python: `src/tracertm/services/temporal_service.py`, `src/tracertm/workflows/worker.py`, `src/tracertm/workflows/workflows.py`, `src/tracertm/api/main.py` (workflow routes), `src/tracertm/models/workflow_run.py`, `src/tracertm/repositories/workflow_run_repository.py`.
- Go: `backend/internal/clients/workflow_client.go`, `backend/internal/handlers/workflow_handler.go`, `backend/internal/preflight/preflight.go`.
- Docs: `docs/guides/TEMPORAL_SETUP.md`, `docs/reports/HATCHET_REFERENCES_AUDIT.md`, `docs/guides/HATCHET_TO_TEMPORAL_MIGRATION.md`.
