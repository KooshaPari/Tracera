# Evidence Contract Design

## 1. Goal
Define one canonical backend source of truth for:
- requirement coverage status
- verification status (pending/in-progress/passed/failed)
- verification evidence
- gap rationale and ownership

This contract is shared across the coverage matrix pipeline, specification generation, and UI dashboards so every surface reads from the same data shape and semantics.

## 2. Single source of truth
All evidence and status data must be stored in the backend database table `requirement_evidence_contract` (or equivalent persisted domain model) and exposed through a single API contract:

- **Canonical record**: one row per `(requirement_id, spec_item_id)` pair.
- **Canonical keyset**: `(project_id, requirement_id, spec_item_id, phase)`
- **Single status enum** for all systems:
  - `not_assessed`
  - `in_progress`
  - `verified`
  - `blocked`
  - `not_applicable`
- **Single verification mode enum**:
  - `automated`, `manual`, `not_needed`
- **Single gap taxonomy**: `not_implemented`, `insufficient_evidence`, `flaky`, `blocked_by_dependency`, `deferred`, `other`

### 2.1 Canonical schema
Use a strict contract schema versioned at `1`. Recommended columns:

- `project_id`
- `requirement_id`
- `spec_item_id`
- `phase`
- `status`
- `verification_mode`
- `verification_artifacts` (JSON list of artifact references)
- `evidence` (JSON map)
- `gap_reason` (nullable)
- `owner`
- `updated_at`
- `updated_by`
- `source_run_id`
- `schema_version` (default `1`)
- `traceability_confidence` (0.0-1.0)

### 2.2 Ingestion and authority
- Upstream ingestion services should always write through one internal service: `evidence_contract_writer`.
- Direct DB writes outside this service are forbidden by policy.
- Every write must include `schema_version`, `source_run_id`, and actor identity.

## 3. Contract APIs
The backend must expose one read and one write contract used by all clients:

### 3.1 Read API
`GET /api/v1/evidence-contract` with filters:
- `project_id`
- `spec_id` / `requirement_id`
- `status`
- `phase`
- `spec_version`

Response payload: list of contract records with embedded `requirement` metadata (title, owner, tags) when requested.

### 3.2 Write API
`POST /api/v1/evidence-contract/updates` for upserts.
- Upserts are idempotent on `(project_id, requirement_id, spec_item_id, phase)`.
- Reject unknown enum values.
- Reject records with stale `source_run_id` unless explicitly overriding.

## 4. How dashboards must consume it
Both matrix and spec dashboards must be strict consumers of this contract (no local inference):

### 4.1 Matrix dashboard
- Uses one query call to build rows by requirement and column.
- Computes each cell as: latest canonical contract status + evidence summary + gap reason.
- Must show gap count from `status='blocked' OR status='not_assessed'` by spec and by phase.
- Must display evidence links from `verification_artifacts` directly.

### 4.2 Spec dashboard
- Uses the same query endpoint and groups by `spec_item_id`.
- Renders:
  - Coverage badge from status rollups
  - Verification maturity from `traceability_confidence`
  - Open gaps by taxonomic reason
- Must not invent additional status states; must map exactly from canonical enums.

## 5. Data consistency rules
1. A `status != verified` must include either evidence (if `in_progress`) or gap_reason (`not_assessed/blocked`).
2. `verified` requires evidence artifact references or at minimum deterministic acceptance note when `verification_mode=not_needed`.
3. Duplicate rows for same keyset are rejected.
4. Status transitions follow allowed transitions:
   - `not_assessed -> in_progress -> verified`
   - `not_assessed -> blocked`
   - `in_progress -> blocked`
   - `blocked -> in_progress`
   - `verified -> in_progress` (revalidation)

## 6. Backward compatibility
For consumers expecting older field names, keep compatibility views/adapters only in API layer, never in the stored model.

## 7. Dashboards update contract
Matrix and spec dashboards must call this service via same query path and cache for no more than 30s with an ETag/If-None-Match strategy.

## 8. Audit and gap reporting
All writes must emit changelog events with:
- commit style hash of the source spec run
- actor
- previous status
- next status
- gap_reason changes

This enables reproducible matrix snapshots and governance reports.

## 9. Open questions
- Should `traceability_confidence` be computed at ingestion or stored as an evidence-quality input?
- Which actor identity should be treated as canonical for non-human automation runs?
