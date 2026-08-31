# ADR-GOV-002: AgilePlus → Tracera Graph Ingestion Architecture

| Field        | Value                                      |
|--------------|--------------------------------------------|
| **Status**   | Accepted                                   |
| **Date**     | 2026-08-30                                 |
| **Deciders** | Tracera Core Team                          |
| **Supersedes** | ADR-DEP-001 (Phenodag Queue Absorption)  |

## Context

AgilePlus operates a multi-layer project coordination platform that manages requirements,
stories, test plans, and deployment pipelines across distributed teams.  Tracera owns the
canonical traceability graph — the directed acyclic graph of artifact nodes linked by
semantic relationships such as *satisfies*, *verifies*, and *depends_on*.

Today the only ingestion path is a synchronous HTTP poll (`ingest_live`) that pulls
GitHub and Jira issues, normalises them into `NormalisedIssue`, and writes them through
the `Store::create_story` / `Store::create_trace_link` trait interface.  This approach
has three structural limitations:

1. **Latency** — the polling loop runs at a fixed cadence (default 60 s).  Events that
   occur between polls are invisible until the next tick, which is unacceptable for
   real-time CI/CD trace-link updates and deployment-state propagation.
2. **Completeness** — the current pipeline only ingests issue-level entities.  AgilePlus
   also produces *test runs*, *deployment artifacts*, and *sprint-level metadata* that
   have no representation in the Tracera graph today.
3. **Coupling** — the `phenodag-queue` feature flag (ADR-DEP-001) established that
   separate queue systems are an operational burden.  A single, unified ingestion
   architecture across all upstream producers (AgilePlus, Phenodag, Helios benchmarks,
   future MCP tools) is required.

Given the growing volume of AgilePlus graph data and the need for sub-second freshness,
the cost of a single-mode ingestion pipeline now outweighs its simplicity.

## Decision

We will introduce a **three-phase ingestion architecture** — polling, webhooks, and an
event bus — to move AgilePlus graph data into Tracera with bounded latency, idempotent
writes, and a clear migration path from the existing polling-only model.

### Phase 1: Polling (existing, retained)

The current `fetch_github_issues` / `fetch_jira_issues` / `ingest_live` path is retained
as a **catch-up backfill** mechanism.  It continues to run on a configurable cron
(`TRACERA_POLL_INTERVAL_SECS`, default 300) and is responsible for:

- Reconciling any events missed during webhook or event-bus outages.
- Backfilling historical data after initial deployment.
- Serving environments (air-gapped, CI runners) where outbound webhook delivery is
  not possible.

Polling uses the `NormalisedIssue` → `persist_issues` path unchanged.  Each poll
writes an *ingestion checkpoint* (`last_poll_at` per source) to avoid redundant
re-processing.

### Phase 2: Webhooks (near-real-time, source-initiated)

AgilePlus will register webhook subscriptions for four entity types (see *Entity Mapping
Table* below).  Tracera exposes a new `/api/v1/ingest/webhook` endpoint that:

1. Validates the HMAC-SHA256 signature using a per-source shared secret stored in
   `TRACERA_WEBHOOK_SECRET_{SOURCE}`.
2. Normalises the payload into the existing `NormalisedIssue` abstraction or, for new
   entity types, into a richer `GraphEvent` envelope.
3. Writes the event into a **durable staging table** (`ingest_events`) before touching
   the graph, enabling replay on failure.
4. Returns `202 Accepted` with the event ID within 200 ms (SLA).

Webhooks provide **at-least-once delivery**.  Idempotency is enforced via the
`idempotency_key` field derived from `(source, external_id, updated_at)` — see
*Idempotency Strategy*.

### Phase 3: Event Bus (async, fan-out)

For high-volume or cross-system scenarios (e.g. deployment pipelines that produce
hundreds of events per minute), we introduce an optional **event bus** backed by the
existing Phenodag queue infrastructure (already feature-flagged as `phenodag-queue`).

The bus accepts `GraphEvent` messages on the `tracera.ingest` topic and fans them out
to:

- The **graph writer** — applies node upserts and edge creates to the `Store`.
- The **distillation worker** — runs the memory distillation pipeline (see below).
- The **downstream notifier** — pushes change notifications to subscribed MCP tools
  and edge workers.

The event bus is **not required** for basic operation.  Deployments that do not set
`TRACERA_EVENT_BUS_URL` will route all traffic through Phases 1 and 2.

### Phase Ordering

```
AgilePlus ──webhook──▶ Tracera /ingest/webhook ──▶ staging ──▶ Store
                     (Phase 2)                  (idempotent)

AgilePlus ──event-bus──▶ tracera.ingest topic ──▶ graph writer ──▶ Store
                       (Phase 3)                (async)

GitHub/Jira ──poll──▶ Tracera /ingest/live ──▶ NormalisedIssue ──▶ Store
                    (Phase 1, catch-up)
```

## Entity Mapping Table

The four AgilePlus entity types and their Tracera graph representation:

| AgilePlus Entity     | Tracera Node Type | ID Convention          | Key Fields Mapped                          | Confidence |
|----------------------|-------------------|------------------------|--------------------------------------------|------------|
| **Requirement**      | `Story`           | `story-{source}-{id}`  | title, description, status, priority       | 1.0        |
| **Test Run**         | `EvidenceItem`    | `ev-tr-{source}-{id}`  | kind=`test_run`, url, metadata.{outcome,duration_ms} | 1.0 |
| **Deployment Artifact** | `EvidenceItem` | `ev-deploy-{source}-{id}` | kind=`deployment`, url, metadata.{env,version} | 1.0 |
| **Sprint**           | `Sprint`          | `sprint-{source}-{id}` | name, goal, start_date, end_date, status   | 1.0        |

*Requirement* maps directly to the existing `Story` record.  *Test Run* and
*Deployment Artifact* are represented as `EvidenceItem` records linked to their parent
story via `kind` differentiation, consistent with the existing `{source}_issue` pattern
in `ingest.rs:535`.  *Sprint* maps to the existing `Sprint` domain type in
`store.rs:94-103`.

## Trace Link Semantics

Six trace-link relationship types are supported across the AgilePlus → Tracera graph.
The first three are already present in the codebase; the last three are new.

| Relationship     | Direction (Source → Target)          | Semantics                                      | Confidence Range | Status     |
|------------------|--------------------------------------|------------------------------------------------|------------------|------------|
| `satisfies`      | Story → Requirement                  | A story fulfills a requirement                 | 0.7 – 1.0       | Existing   |
| `verifies`       | EvidenceItem(Test) → Story           | A test run validates a story's implementation  | 0.8 – 1.0       | Existing   |
| `depends_on`     | Story → Story                        | One story blocks or depends on another         | 0.6 – 1.0       | Existing   |
| `deploys`        | EvidenceItem(Deploy) → Story         | A deployment artifact delivers a story         | 1.0              | **New**    |
| `refines`        | Story → Story                        | A story is a refinement / decomposed child      | 0.9              | **New**    |
| `originates_from`| Story → EvidenceItem                 | A story was auto-generated from evidence       | 0.7 – 0.9       | **New**    |

Link creation follows the same pattern as the existing `create_trace_link` path in
`ingest.rs:548-555`.  The `source` field records which upstream system produced the link
(`"agileplus"`, `"github"`, `"jira"`, or `"manual"`).

## Idempotency Strategy

Every inbound event carries an **idempotency key** computed as:

```
idempotency_key = SHA-256(source || ":" || external_id || ":" || updated_at)
```

The key is stored in the `ingest_events` staging table with a unique constraint.
On write:

1. If the key **does not exist** → insert the event and proceed to graph mutation.
2. If the key **already exists** and the payload hash matches → return `200 OK`
   (idempotent replay, no graph mutation).
3. If the key **already exists** and the payload hash differs → return
   `409 Conflict` (stale event, caller must re-fetch).

The staging table retains rows for **30 days** to support catch-up polling and
debugging, then a background compaction job removes expired rows.

## Delta Sync Approach

Full-graph reconciliation is expensive.  The delta sync protocol ensures only changed
entities are processed after the initial backfill.

### Watermark Tracking

Each source maintains a **sync watermark** — the `updated_at` timestamp of the most
recently ingested event.  Watermarks are persisted in a `sync_state` table keyed by
`(source, entity_type)`.

| Column       | Type                     | Description                                |
|--------------|--------------------------|--------------------------------------------|
| `source`     | `TEXT PRIMARY KEY`       | Upstream system identifier                 |
| `entity_type`| `TEXT PRIMARY KEY`       | One of: requirement, test_run, deploy, sprint |
| `watermark`  | `TIMESTAMPTZ`           | Last successfully ingested `updated_at`    |
| `cursor`     | `TEXT`                   | Opaque cursor for paginated APIs           |

### Polling Delta

The Phase 1 poll fetches only entities where `updated_at > watermark`.  This is
supported by:

- GitHub: `?since={watermark}` query parameter on the issues endpoint.
- Jira: `jql=updated >= "{watermark}"` filter clause.
- AgilePlus: `changed_since={watermark_unix}` parameter.

### Webhook Delta

Webhooks inherently deliver deltas.  The `updated_at` field in the webhook payload
is compared against the stored watermark.  Events older than the watermark are
dropped (they were already processed by a prior poll or webhook).

### Conflict Resolution

When two events for the same entity arrive concurrently (e.g. from webhook and
event bus), the **last-writer-wins** policy applies based on `updated_at`.  The
idempotency key prevents duplicate graph mutations for the same logical update.

## Memory Distillation Pipeline

The distillation pipeline compresses high-frequency, low-signal ingestion events
into durable, queryable graph summaries.  It runs as an async worker consuming
from the event bus topic `tracera.ingest.distill`.

### Pipeline Stages

1. **Buffer** — Accumulates events in a 60-second tumbling window per entity.
   Multiple updates to the same entity within the window are collapsed into a
   single upsert (last-writer-wins).

2. **Classify** — Each collapsed event is classified into one of three tiers:
   - *Hot* (confidence ≥ 0.9): Applied immediately to the graph.  Includes
     verified test runs and confirmed deployments.
   - *Warm* (0.5 ≤ confidence < 0.9): Queued for batch write within 5 minutes.
     Includes auto-extracted requirement references.
   - *Cold* (confidence < 0.5): Stored in a sidecar table for human review
     before graph promotion.

3. **Compact** — Periodically (every 15 minutes), the distillation worker merges
   adjacent trace-link chains.  For example, if Story A → satisfies → REQ-1 and
   REQ-1 → refined_by → Story B, a transitive `refines` edge A → B is emitted
   with `confidence = min(confidence_A, confidence_B) * 0.9`.

4. **Evict** — EvidenceItem records older than 90 days with zero inbound trace
   links are archived to cold storage.  This prevents unbounded graph growth while
   retaining full auditability through the archive.

### Backpressure

If the staging table exceeds 100,000 unprocessed events, the distillation worker
emits a `tracera.ingest.backpressure` metric and the webhook endpoint shifts to
**synchronous mode** (processing events inline before returning 202).

## Consequences

### Positive

- **Sub-second freshness** for webhook-delivered events, vs. 60-second polling cadence.
- **Unified ingestion surface** across AgilePlus, GitHub, Jira, and future sources
  (MCP tools, Helios benchmarks), replacing the fragmented per-source polling in
  `ingest.rs:587-619`.
- **Idempotent writes** prevent duplicate graph mutations from at-least-once delivery,
  eliminating the race conditions present in the current concurrent poll model.
- **Tiered processing** via the distillation pipeline avoids flooding the graph with
  low-confidence auto-extracted links while still capturing high-confidence data
  immediately.
- **Backward compatible** — the Phase 1 poll path is unchanged; Phase 2 and Phase 3
  are additive.

### Negative

- **Operational complexity** — three ingestion modes require monitoring, alerting, and
  runbook documentation for each.  Mitigated by sharing the `ingest_events` staging
  table across all three phases.
- **Schema migration** — the `ingest_events` and `sync_state` tables require new
  DDL migrations (PR 1 of the 7-PR plan below).
- **Webhook secret management** — per-source HMAC secrets must be rotated and stored
  securely, adding a secrets-management requirement to deployment.
- **Distillation latency** — warm-tier events may be delayed up to 5 minutes, which
  is acceptable for non-critical trace links but must be documented for downstream
  consumers.

## Alternatives Considered

* **Webhooks only (no polling, no bus)**: Rejected because air-gapped environments and
  CI runners cannot receive inbound webhooks.  Polling is required as a fallback.

* **Event bus only (no webhooks)**: Rejected because the bus adds infrastructure
  (broker, topic partitioning, consumer groups) that is overkill for small deployments
  and single-repo setups.  Webhooks provide a zero-infrastructure option for simple
  cases.

* **Direct write (no staging table)**: Rejected because at-least-once delivery without
  idempotent staging risks duplicate graph mutations under retry, which corrupts the
  trace-link confidence model.

* **CRDT-based merge**: Considered for concurrent-write resolution but rejected as
  over-engineered.  Last-writer-wins on `updated_at` is sufficient for the current
  entity cardinality (< 100K entities) and avoids introducing a CRDT runtime dependency.

## Migration Plan (7 PRs)

The migration is delivered as a sequence of seven pull requests, each independently
reviewable and deployable.

### PR 1: Schema Foundation — `ingest_events` and `sync_state` tables

Adds the `ingest_events` staging table (event ID, idempotency key, payload hash,
source, entity type, created_at, expires_at) and the `sync_state` watermark table.
Includes DDL migrations for both SQLite and Postgres backends.  No behavioral changes
to existing ingest paths.

### PR 2: Idempotency Layer — dedup filter in `persist_issues`

Wraps the existing `persist_issues` function with an idempotency check.  Before each
`Store::create_story` / `Store::create_trace_link` call, the idempotency key is
computed and checked against `ingest_events`.  Duplicate events are short-circuited
with a log warning.  Existing poll behavior is unchanged.

### PR 3: Webhook Endpoint — `/api/v1/ingest/webhook`

Implements the HMAC-SHA256–validated webhook endpoint.  Accepts `GraphEvent` payloads
for all four entity types, normalises them, writes to the staging table, and invokes
the idempotent graph-mutation path from PR 2.  Includes rate limiting (1000 req/min
per source) and request body validation matching the existing `MAX_REQUEST_BODY_BYTES`
guard (`main.rs:48`).

### PR 4: Delta Sync — watermark tracking and filtered polling

Adds watermark read/write logic to `sync_state`.  Modifies `fetch_github_issues` and
`fetch_jira_issues` to accept an optional `since` parameter and pass it as a query
filter.  Updates `ingest_live` to read the stored watermark and apply it.  Polling
now processes only changed entities after the initial backfill completes.

### PR 5: AgilePlus Adapter — new source connector

Implements `fetch_agileplus_entities` following the same `NormalisedIssue` pattern
as the existing GitHub/Jira adapters.  Maps the four entity types (Requirement,
Test Run, Deployment Artifact, Sprint) into the Tracera domain model.  Adds
`AGILEPLUS_API_URL` and `AGILEPLUS_API_TOKEN` environment variable configuration.
Registers the adapter in the `ingest_live` orchestrator.

### PR 6: Event Bus Integration — `phenodag-queue` enablement

Activates the existing `phenodag-queue` feature flag in production.  Implements
the `tracera.ingest` topic consumer that reads `GraphEvent` messages, writes them
to the staging table, and triggers graph mutation via the idempotent path.  Adds
the distillation worker (buffer → classify → compact → evict) as a background
tokio task.  Retains the feature flag as a deployment-time opt-in.

### PR 7: Migration Cutover — default source switchover and documentation

Switches the default ingestion mode from polling-only to "all available phases"
(auto-detect based on configured environment variables).  Adds operational
documentation: monitoring dashboards for `ingest_events` depth, webhook delivery
latency, and distillation backlog metrics.  Updates `adr_index.md` and the
governance README to reference this ADR.

## References

- `crates/tracera-server/src/ingest.rs` — existing ingest pipeline (769 lines)
- `crates/tracera-server/src/store.rs` — `Store` trait and domain types
- `crates/tracera-server/src/main.rs` — `MAX_COVERAGE_LINKS` and request guards
- `crates/tracera-server/Cargo.toml` — `phenodag-queue` feature flag
- `docs/governance/ADR-DEP-001-phenodag-absorption.md` — Phenodag queue absorption rationale
