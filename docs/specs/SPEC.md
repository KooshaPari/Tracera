# Tracera API Endpoint Oracle Specification

## Status

Draft 2026-06-24 (Phase 0 migration oracle). Source inventory: `_tracera_feature_inventory.md`.

## Purpose

This specification formalizes the **24 main REST endpoints** surviving on `main` across **11 consolidated domain routers** in `src/tracertm/api/routers/`. It is the regression oracle for Py→Rust/Go and TS→Bun migration: every step MUST preserve these endpoints and their request/response contracts unless explicitly approved.

Verify by **capability** (method + path + schema), not by router filename.

## Router inventory

| Router module | Tag(s) | Endpoints |
|---|---|---|
| `auth.py` | auth | 1 |
| `code_trace.py` | analysis, code-trace | 1 |
| `comments.py` | comments | 3 |
| `evidence.py` | evidence | 3 |
| `impact.py` | impact | 2 |
| `impact_scoring.py` | impact | 1 |
| `ingest.py` | ingest | 2 |
| `org_intel.py` | org_intel | 3 |
| `sdlc_pm.py` | sdlc_pm | 4 |
| `traceability.py` | traceability | 4 |
| **Total** | **11 routers** | **24** |

Mount convention: `create_app()` in `src/tracertm/api/main.py` includes routers under `prefix="/api/v1"`. Routers `code_trace` and `comments` embed the full `/api/v1/...` prefix in their `APIRouter` definition.

---

## Functional Requirements

### FR-1 — Current authenticated user

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/auth/me` |
| **Capability** | Return the authenticated user's profile, JWT claims, and DB-backed account record (WorkOS AuthKit + `AccountRepository`). |
| **Request schema** | _(none — Bearer token in `Authorization` header)_ |
| **Response schema** | `MeResponse` |
| **Source router** | `auth.py` |

**Acceptance criterion:** Given a valid `Bearer` JWT with `sub`, when `GET /api/v1/auth/me` is called, then the response is `200` with JSON containing `user.id` equal to `sub`, a `claims` object, and `account` populated from DB or JWT fallback.

---

### FR-2 — UI code trace chain

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/analysis/code-trace/{component_id}` |
| **Capability** | Build a `UICodeTraceChain` by walking inbound/outbound trace links from a root item (UI → code → requirement → concept). |
| **Request schema** | Path: `component_id` (UUID); query: optional `project_id` |
| **Response schema** | `UICodeTraceChain` (inline `dict`: `id`, `name`, `description`, `levels[]`, `overallConfidence`, `lastUpdated`) |
| **Source router** | `code_trace.py` |

**Acceptance criterion:** Given a seeded item graph with at least one outbound link, when `GET /api/v1/analysis/code-trace/{component_id}` is called with a valid UUID, then the response is `200` with `levels` non-empty, each level having `type`, `confidence`, and `strategy`, and `overallConfidence` in `[0.0, 1.0]`.

---

### FR-3 — List item comments

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/items/{item_id}/comments` |
| **Capability** | List all comments for an item, oldest first. |
| **Request schema** | Path: `item_id` |
| **Response schema** | `list[CommentResponse]` |
| **Source router** | `comments.py` |

**Acceptance criterion:** Given the `item_comments` table exists and contains comments for `item_id`, when `GET /api/v1/items/{item_id}/comments` is called with a valid Bearer token, then the response is `200` with a JSON array ordered by `created_at` ascending.

---

### FR-4 — Create item comment

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/items/{item_id}/comments` |
| **Capability** | Create a new comment on an item attributed to the authenticated user. |
| **Request schema** | `CreateCommentBody` |
| **Response schema** | `CommentResponse` |
| **Source router** | `comments.py` |

**Acceptance criterion:** Given a valid Bearer token and migrated `item_comments` table, when `POST /api/v1/items/{item_id}/comments` is called with `{"content": "test"}`, then the response is `201` with `content` equal to `"test"` and `author_id` matching the token `sub`.

---

### FR-5 — Delete own comment

| Field | Value |
|---|---|
| **Method + path** | `DELETE /api/v1/items/{item_id}/comments/{comment_id}` |
| **Capability** | Delete a comment; only the author may delete (others receive 403). |
| **Request schema** | Path: `item_id`, `comment_id` |
| **Response schema** | _(empty — HTTP 204)_ |
| **Source router** | `comments.py` |

**Acceptance criterion:** Given a comment owned by the caller, when `DELETE /api/v1/items/{item_id}/comments/{comment_id}` is called, then the response is `204` and a subsequent `GET` list no longer includes that comment.

---

### FR-6 — Evidence pillar health

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/evidence/health` |
| **Capability** | Liveness probe for the evidence domain pillar. |
| **Request schema** | _(none)_ |
| **Response schema** | `{"pillar": "evidence", "status": "ok"}` |
| **Source router** | `evidence.py` |

**Acceptance criterion:** When `GET /api/v1/evidence/health` is called, then the response is `200` with `pillar` equal to `"evidence"` and `status` equal to `"ok"`.

---

### FR-7 — List evidence items

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/evidence` |
| **Capability** | List all stored evidence items linked to artifacts. |
| **Request schema** | _(none)_ |
| **Response schema** | `List[EvidenceResponse]` |
| **Source router** | `evidence.py` |

**Acceptance criterion:** Given at least one evidence item exists, when `GET /api/v1/evidence` is called, then the response is `200` with a JSON array where each element has `id`, `artifact_id`, `kind`, `url`, and `captured_at`.

---

### FR-8 — Create evidence item

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/evidence` |
| **Capability** | Register a new evidence artifact (URL, kind, capture timestamp) for traceability. |
| **Request schema** | `EvidenceCreate` |
| **Response schema** | `EvidenceResponse` |
| **Source router** | `evidence.py` |

**Acceptance criterion:** When `POST /api/v1/evidence` is called with a valid `EvidenceCreate` body, then the response is `201` with a server-assigned `id` and fields mirroring the request payload.

---

### FR-9 — Forward graph impact (Neo4j)

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/impact/forward/{artifact_id}` |
| **Capability** | Cypher-backed traversal of all downstream artifacts affected by changes to the source artifact. |
| **Request schema** | Path: `artifact_id` |
| **Response schema** | `ForwardImpactResponse` (inline `dict`: `artifact_id`, `direction`, `total`, `affected[]`) |
| **Source router** | `impact.py` |

**Acceptance criterion:** Given a Neo4j graph with outgoing trace links from `artifact_id`, when `GET /api/v1/impact/forward/{artifact_id}` is called with a valid Bearer token, then the response is `200` with `direction` equal to `"forward"` and `total` equal to `len(affected)`.

---

### FR-10 — Reverse graph impact (Neo4j)

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/impact/reverse/{artifact_id}` |
| **Capability** | Cypher-backed traversal of all upstream artifacts that affect the target artifact. |
| **Request schema** | Path: `artifact_id` |
| **Response schema** | `ReverseImpactResponse` (inline `dict`: `artifact_id`, `direction`, `total`, `upstream[]`) |
| **Source router** | `impact.py` |

**Acceptance criterion:** Given a Neo4j graph with incoming trace links to `artifact_id`, when `GET /api/v1/impact/reverse/{artifact_id}` is called with a valid Bearer token, then the response is `200` with `direction` equal to `"reverse"` and `total` equal to `len(upstream)`.

---

### FR-11 — Blast-radius risk scoring

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/impact/blast-radius` |
| **Capability** | Compute risk-weighted blast radius over a caller-supplied in-memory TraceLink graph (pure function, no DB). |
| **Request schema** | `BlastRadiusRequest` |
| **Response schema** | `BlastRadiusResult` |
| **Source router** | `impact_scoring.py` |

**Acceptance criterion:** When `POST /api/v1/impact/blast-radius` is called with a graph containing linked artifacts, then the response is `200` with `blast_radius_score` in `[0.0, 100.0]`, `risk_level` in `{"LOW","MEDIUM","HIGH","CRITICAL"}`, and `affected_artifacts` listing downstream IDs.

---

### FR-12 — GitHub issue bulk ingest

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/ingest/github` |
| **Capability** | Bulk-import GitHub issues into Requirements and TraceLinks via `GitHubImportService`. |
| **Request schema** | `GitHubIssueIngestRequest` |
| **Response schema** | `BulkIngestionResult` |
| **Source router** | `ingest.py` |

**Acceptance criterion:** When `POST /api/v1/ingest/github` is called with `{"repo": "org/repo", "issues": [<valid issue>]}` and a valid Bearer token, then the response is `200` with `total_processed`, `requirements_created`, `trace_links_created`, and `errors` fields present.

---

### FR-13 — Jira issue bulk ingest

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/ingest/jira` |
| **Capability** | Bulk-import Jira issues into Requirements and TraceLinks via `JiraImportService`. |
| **Request schema** | `JiraIssueIngestRequest` |
| **Response schema** | `BulkIngestionResult` |
| **Source router** | `ingest.py` |

**Acceptance criterion:** When `POST /api/v1/ingest/jira` is called with `{"issues": [<valid Jira issue>]}` and a valid Bearer token, then the response is `200` with `total_processed` ≥ 1 and integer counts for `requirements_created` and `trace_links_created`.

---

### FR-14 — Org-intel pillar health

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/org-intel/health` |
| **Capability** | Liveness probe for the organizational intelligence pillar. |
| **Request schema** | _(none)_ |
| **Response schema** | `{"pillar": "org_intel", "status": "ok"}` |
| **Source router** | `org_intel.py` |

**Acceptance criterion:** When `GET /api/v1/org-intel/health` is called, then the response is `200` with `pillar` equal to `"org_intel"` and `status` equal to `"ok"`.

---

### FR-15 — Organizational metrics

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/org-intel/metrics` |
| **Capability** | Return aggregate organizational traceability metrics (artifact count, coverage ratio, open gaps). |
| **Request schema** | _(none)_ |
| **Response schema** | `MetricsResponse` |
| **Source router** | `org_intel.py` |

**Acceptance criterion:** When `GET /api/v1/org-intel/metrics` is called, then the response is `200` with `total_artifacts` (int), `coverage_ratio` (float in `[0.0, 1.0]`), and `open_gaps` (int).

---

### FR-16 — List teams

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/org-intel/teams` |
| **Capability** | List organizational teams and their members. |
| **Request schema** | _(none)_ |
| **Response schema** | `List[TeamResponse]` |
| **Source router** | `org_intel.py` |

**Acceptance criterion:** When `GET /api/v1/org-intel/teams` is called, then the response is `200` with a non-empty JSON array where each element has `id`, `name`, `description`, and `members`.

---

### FR-17 — SDLC-PM pillar health

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/sdlc-pm/health` |
| **Capability** | Liveness probe for the SDLC program-management pillar. |
| **Request schema** | _(none)_ |
| **Response schema** | `{"pillar": "sdlc_pm", "status": "ok"}` |
| **Source router** | `sdlc_pm.py` |

**Acceptance criterion:** When `GET /api/v1/sdlc-pm/health` is called, then the response is `200` with `pillar` equal to `"sdlc_pm"` and `status` equal to `"ok"`.

---

### FR-18 — List sprints

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/sdlc-pm/sprints` |
| **Capability** | List all sprints in the SDLC program. |
| **Request schema** | _(none)_ |
| **Response schema** | `List[SprintResponse]` |
| **Source router** | `sdlc_pm.py` |

**Acceptance criterion:** When `GET /api/v1/sdlc-pm/sprints` is called, then the response is `200` with a JSON array where each sprint has `id`, `name`, `goal`, `start_date`, `end_date`, and `status`.

---

### FR-19 — List stories

| Field | Value |
|---|---|
| **Method + path** | `GET /api/v1/sdlc-pm/stories` |
| **Capability** | List all user stories across sprints. |
| **Request schema** | _(none)_ |
| **Response schema** | `List[StoryResponse]` |
| **Source router** | `sdlc_pm.py` |

**Acceptance criterion:** When `GET /api/v1/sdlc-pm/stories` is called, then the response is `200` with a JSON array where each story has `id`, `title`, `description`, and `status`.

---

### FR-20 — Create sprint

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/sdlc-pm/sprints` |
| **Capability** | Create a new sprint with name, goal, and date range. |
| **Request schema** | `SprintCreate` |
| **Response schema** | `SprintResponse` |
| **Source router** | `sdlc_pm.py` |

**Acceptance criterion:** When `POST /api/v1/sdlc-pm/sprints` is called with a valid `SprintCreate` body, then the response is `201` with a server-assigned `id` and `name` matching the request.

---

### FR-21 — Coverage matrix build

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/coverage-matrix` |
| **Capability** | Build a requirement-to-artifact coverage matrix from trace links with stale/conflict classification. |
| **Request schema** | `CoverageMatrixRequest` |
| **Response schema** | `CoverageMatrixResponse` |
| **Source router** | `traceability.py` |

**Acceptance criterion:** When `POST /api/v1/coverage-matrix` is called with at least one `TraceLinkInput`, then the response is `200` with `link_count` matching input size, `cells` non-empty, and each cell containing `coverage` in `{"covered","partial","missing","stale","conflict"}`.

---

### FR-22 — Spec-first governance gate

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/governance/spec-check` |
| **Capability** | Evaluate whether planned work is backed by approved specs, tests, and evidence traces. |
| **Request schema** | `GovernanceCheckRequest` |
| **Response schema** | `GovernanceReport` |
| **Source router** | `traceability.py` |

**Acceptance criterion:** When `POST /api/v1/governance/spec-check` is called with aligned `specs` and `traces`, then the response is `200` with `status` equal to `"pass"` and `violations` empty.

---

### FR-23 — In-memory impact analysis

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/impact` |
| **Capability** | Compute impacted artifacts from changed artifact IDs over a supplied trace-link graph (BFS with depth cap). |
| **Request schema** | `ImpactRequest` |
| **Response schema** | `ImpactResponse` |
| **Source router** | `traceability.py` |

**Acceptance criterion:** When `POST /api/v1/impact` is called with `changed_artifact_ids` and linked `TraceLinkInput` entries, then the response is `200` with `seeds` matching input IDs and `affected` containing at least the seed nodes at depth 0.

---

### FR-24 — Requirement-artifact confidence scoring

| Field | Value |
|---|---|
| **Method + path** | `POST /api/v1/confidence` |
| **Capability** | Score textual agreement between a requirement and an artifact using `JaccardScorer` (FR-TRC-019). |
| **Request schema** | `ConfidenceRequest` |
| **Response schema** | `ConfidenceResponse` |
| **Source router** | `traceability.py` |

**Acceptance criterion:** When `POST /api/v1/confidence` is called with `requirement_text` and `artifact_text`, then the response is `200` with `confidence` in `[0.0, 1.0]` and a non-empty `rationale` string.

---

## Non-Functional Requirements

### NFR-1 — API read latency

99% of successful `GET` requests to FR-1..FR-24 endpoints MUST complete within **500 ms** measured at the service boundary (`http.server.duration`).

**Acceptance criterion:** Under a 50-concurrent-user load test against a warm instance, p99 latency for GET endpoints is ≤ 500 ms over a 5-minute window.

---

### NFR-2 — API write latency

95% of successful `POST`/`DELETE` mutations (FR-4, FR-5, FR-8, FR-11..FR-13, FR-20..FR-24) MUST complete within **750 ms** (`tracera.operation.duration`).

**Acceptance criterion:** Under integration test harness with seeded fixtures, p95 write latency is ≤ 750 ms.

---

### NFR-3 — Authentication contract

All endpoints except pillar health probes (FR-6, FR-14, FR-17) and unauthenticated traceability pure-function endpoints (FR-21..FR-24) MUST reject requests without a valid `Authorization: Bearer <token>` header with **401**.

**Acceptance criterion:** Calling any auth-guarded endpoint without a Bearer token returns `401` with a JSON `detail` field; no handler body executes.

---

### NFR-4 — Request-ID observability

Every HTTP response MUST include `X-Request-Id` echoed from the inbound header or generated as UUID v4 via `RequestIdMiddleware`.

**Acceptance criterion:** A request without `X-Request-Id` receives a response containing a valid UUID in the `X-Request-Id` header; a provided value is echoed unchanged.

---

### NFR-5 — Error response shape

All `4xx` and `5xx` responses MUST return JSON `{"detail": ...}` per FastAPI convention; no HTML error pages on API routes.

**Acceptance criterion:** Triggering 404, 401, 422, and 500 on representative endpoints yields `Content-Type: application/json` with a `detail` key.

---

### NFR-6 — Rate limiting on code trace

`GET /api/v1/analysis/code-trace/{component_id}` (FR-2) MUST enforce per-user rate limits via `enforce_rate_limit`.

**Acceptance criterion:** Exceeding the configured request quota within the rate-limit window returns `429` with a JSON error body.

---

### NFR-7 — Endpoint registry completeness

The deployed API MUST expose exactly the **24 endpoints** enumerated in FR-1..FR-24; OpenAPI schema or router introspection MUST match this oracle set with zero undocumented drift.

**Acceptance criterion:** Automated inventory script diffs live route table against this spec; diff is empty unless an ADR-approved deprecation is recorded.

---

### NFR-8 — API availability

99.9% of non-health HTTP requests to FR endpoints MUST return a non-5xx response over a rolling 28-day window.

**Acceptance criterion:** SLO dashboard `http.server.request.count{status!~"5.."}` / total ≥ 0.999.

---

## Schema reference index

| Schema | Defined in |
|---|---|
| `MeResponse` | `auth.py` |
| `CommentResponse`, `CreateCommentBody` | `comments.py` |
| `EvidenceCreate`, `EvidenceResponse` | `evidence.py` |
| `BlastRadiusRequest`, `BlastRadiusResult` | `impact_scoring.py`, `blast_radius_service.py` |
| `GitHubIssueIngestRequest`, `JiraIssueIngestRequest`, `BulkIngestionResult` | `ingest.py`, `github_import_service.py` |
| `MetricsResponse`, `TeamResponse` | `org_intel.py` |
| `SprintCreate`, `SprintResponse`, `StoryResponse` | `sdlc_pm.py` |
| `CoverageMatrixRequest`, `CoverageMatrixResponse`, `ImpactRequest`, `ImpactResponse`, `GovernanceCheckRequest`, `ConfidenceRequest`, `ConfidenceResponse` | `traceability.py` |
| `GovernanceReport` | `governance.py` |

## Out of scope (review queue)

Per feature inventory, these capabilities are **absent** from main and require explicit user decision before restoration:

- `adrs` — ADR management endpoints
- `linear` — Linear integration
- `blockchain`, `chat`, `codex` — experimental cuts (likely deliberate)

## Acceptance test artifact

Executable Gherkin scenarios: [`acceptance/tracera_endpoints.feature`](./acceptance/tracera_endpoints.feature) — one scenario per FR, pending as migration oracle targets.
