# Spec 009: AgilePlus to Tracera Governance Pipeline

| Field       | Value                                           |
| ----------- | ----------------------------------------------- |
| **Spec ID** | TRACERA-SPEC-009                                |
| **Title**   | AgilePlus Governance to Tracera Graph Ingestion |
| **Status**  | Implemented (contract v2026-08-30)              |
| **Date**    | 2026-08-30 (amended 2026-11-02)                 |

> **Amendment 2026-11-02 (issue #1164).** This spec is now a description of
> shipped behaviour, not a draft. The acceptor endpoint is
> `POST /api/v1/ingest/agileplus`. The former `/ingest/agileplus` registration
> actually ingested AgCord payloads and produced false-positive "AgilePlus
> accepted" claims; AgCord ingestion now lives at `POST /ingest/agcord`, and
> legacy `/ingest/agileplus` traffic is redirected (see §2.7). Sections
> describing phases, coverage scoring and memory distillation are retained as
> design intent and are explicitly marked as not implemented in §2.8.

---

## 1. Motivation

AgilePlus is the single authoritative governance source for all projects in the Tracera ecosystem (see ADR-GOV-001). This spec defines the `/ingest/agileplus` endpoint and the downstream graph-model enrichment pipeline that converts AgilePlus governance artifacts into first-class Tracera graph nodes and edges.

**Problems solved:**

1. Governance decisions made in AgilePlus are opaque once merged
2. No automated link between a spec change and the test that verifies it
3. Coverage metrics ignore governance context
4. Memory distillation from historical governance patterns is impossible without a unified graph

---

## 2. Endpoint Contract

### 2.1 Base URL

```
POST /api/v1/ingest/agileplus
```

`POST /ingest/agileplus` is **not** this endpoint. It is a legacy alias for the
AgCord ingester and answers `308 Permanent Redirect` to `/ingest/agcord` for AgCord
payloads, or `400 agileplus_wrong_path` for a SPEC-009 body.

### 2.2 Request Headers

| Header            | Required | Description                           |
| ----------------- | -------- | ------------------------------------- |
| Content-Type      | Yes      | application/json                      |
| X-AgilePlus-Token | Yes      | Bearer token for authentication       |
| X-Idempotency-Key | Yes      | UUID v4 for deduplication             |
| X-Ingestion-Phase | No       | polling (default), webhook, event_bus |

### 2.3 Request Body

```jsonc
{
  "source": "agileplus",
  "version": "2026-08-30",
  "entities": [
    {
      "type": "spec",
      "agileplus_id": "AP-SPEC-0042",
      "title": "Token Refresh Policy",
      "body": {
        /* full spec JSON from AgilePlus */
      },
      "metadata": {
        "created_at": "2026-08-30T10:00:00Z",
        "updated_at": "2026-08-30T14:30:00Z",
        "author": "governance-bot",
        "status": "approved",
        "version": 3,
      },
    },
  ],
  "trace_links": [
    {
      "source_id": "AP-SPEC-0042",
      "target_id": "AP-WI-1087",
      "relation": "specifies",
      "confidence": 1.0,
    },
  ],
  "coverage_enrichment": {
    "request": true,
    "include_transitive": true,
    "depth_limit": 4,
  },
  "memory_distillation": {
    "request": true,
    "pattern_window_days": 90,
    "min_support": 0.3,
  },
}
```

### 2.4 Response

```jsonc
{
  "status": "accepted",
  "ingestion_id": "ING-20260830-00142",
  "entities_processed": 12,
  "entities_accepted": 11,
  "entities_rejected": 1,
  "rejections": [
    { "agileplus_id": "AP-SPEC-0099", "reason": "duplicate version" },
  ],
  "trace_links_created": 8,
  "trace_links_updated": 3,
  "coverage_delta": {
    "nodes_added": 11,
    "edges_added": 8,
    "coverage_before": 0.72,
    "coverage_after": 0.78,
  },
  "distillation_result": {
    "patterns_extracted": 4,
    "memory_entries_created": 4,
  },
  "processing_time_ms": 342,
}
```

### 2.5 HTTP Status Codes

| Code | Meaning                          |
| ---- | -------------------------------- |
| 202  | Accepted - async processing      |
| 400  | Malformed request body           |
| 401  | Missing/invalid authentication   |
| 409  | Idempotency key already consumed |
| 422  | Entity validation failed         |
| 429  | Rate limit exceeded              |
| 500  | Internal server error            |

### 2.6 Rate Limits

- Polling ingestion: 60 requests/minute per token
- Webhook ingestion: 300 requests/minute (burst: 50)
- Event bus ingestion: 1000 events/minute (queue-backed)

> **Not implemented (2026-11-02).** No rate limiter is attached to the endpoint;
> the limits above remain design intent and a 429 is never emitted.

### 2.7 Implemented request handling

The endpoint is fail-closed at every step. Nothing is written unless the whole
request is acceptable.

| Condition                                                                        | Status | `error` code                                                                         |
| -------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| `TRACERA_AGILEPLUS_TOKEN` unset on the server                                    | 503    | `agileplus_ingest_not_configured`                                                    |
| Missing or wrong `X-AgilePlus-Token`                                             | 401    | `agileplus_unauthorized`                                                             |
| Body is not JSON                                                                 | 400    | `agileplus_malformed_body`                                                           |
| Missing `X-Idempotency-Key`, or not a UUID v4                                    | 400    | `agileplus_missing_idempotency_key`                                                  |
| Body does not match the envelope                                                 | 422    | `agileplus_invalid_envelope`                                                         |
| `source` is not `"agileplus"`                                                    | 422    | `agileplus_wrong_producer`                                                           |
| `version` is not in the accepted set                                             | 422    | `agileplus_unsupported_version`                                                      |
| `entities[]` empty or over 500 entries                                           | 422    | `agileplus_empty_entities` / `agileplus_too_many_entities`                           |
| Unknown entity `type`, bad `agileplus_id`/`title`                                | 422    | `agileplus_invalid_entity_type` / `agileplus_invalid_id` / `agileplus_missing_title` |
| `metadata.version` missing or `< 1`                                              | 422    | `agileplus_missing_revision`                                                         |
| Entity asserts `verified: true` / `product_verified: true`                       | 422    | `agileplus_unaccepted_claim`                                                         |
| `governance_decision` approved without `metadata.author` + `metadata.decided_at` | 422    | `agileplus_forged_approval`                                                          |
| Trace-link `confidence` outside `0.0..=1.0`                                      | 422    | `agileplus_invalid_confidence`                                                       |
| `X-Idempotency-Key` already consumed                                             | 409    | `agileplus_idempotency_key_consumed`                                                 |
| Entity revision does not advance the accepted one                                | 409    | `agileplus_stale_revision`                                                           |
| Store cannot persist provenance                                                  | 501    | `agileplus_provenance_unsupported`                                                   |
| Provenance persistence failed                                                    | 500    | `agileplus_store_error`                                                              |

Conflict responses on a consumed key carry `identical_replay` and
`conflicting_replay` booleans so a retry can be distinguished from a forgery.
Revisions are strictly increasing per `agileplus_id`: an equal revision is a
duplicate and a lower one is stale; both are 409.

Idempotency keys, body fingerprints and accepted revisions are persisted in
`agileplus_ingest_keys` and `agileplus_revisions`
(`migrations-sqlite/0011_agileplus_ingest.sql`,
`migrations-postgres/0011_agileplus_ingest.sql`), so they survive restart.

### 2.8 Implemented subset and ownership boundary

Implemented: typed envelope validation, token authentication, durable
idempotency and revision gating, entity→node mapping, and trace links whose
both endpoints are present in the request. Trace links referencing an entity
absent from the request are returned in `trace_links_unresolved` and are **not**
written.

Persisted nodes use the SWEE taxonomy; the SPEC-009 label is kept in node
metadata as `agileplus_entity`:

| SPEC-009 type         | `node_type`      | `external_id` prefix |
| --------------------- | ---------------- | -------------------- |
| `spec`                | `specification`  | `ap:`                |
| `work_item`           | `story`          | `ap:`                |
| `governance_decision` | `change_request` | `ap-gov:`            |
| `research_doc`        | `evidence`       | `ap-rd:`             |

Every persisted node carries `governance_owner: "agileplus"`,
`product_state_owner: "tracera"` and `capability_verified: false`. A
`work_item` whose status is `done` is stored as governance evidence only: it
never marks a Tracera product capability verified, and the response always
reports `product_capabilities_verified: 0`.

Not implemented (explicitly reported in the response `not_implemented` array):
`memory_distillation`, `coverage_score_recomputation`. `coverage_delta` reports
only the counts actually written.

---

## 3. Entity Mappings

### 3.1 Spec to SpecNode

| AgilePlus Field | Tracera Graph Property | Transform            |
| --------------- | ---------------------- | -------------------- |
| id              | external_id            | Prefix with ap:      |
| title           | name                   | Slugify + normalize  |
| body            | content                | Store as JSONB       |
| status          | status                 | Enum mapping         |
| version         | revision               | Integer              |
| author          | owned_by               | Resolve to AgentNode |
| created_at      | created_at             | ISO 8601             |
| updated_at      | updated_at             | ISO 8601             |

**Node label:** SpecNode
**Required properties:** external_id, name, status, revision

### 3.2 Work Item to WorkItemNode

| AgilePlus Field | Tracera Graph Property | Transform               |
| --------------- | ---------------------- | ----------------------- |
| id              | external_id            | Prefix with ap:         |
| title           | name                   | Pass through            |
| type            | work_item_type         | Enum: feature/bug/chore |
| priority        | priority               | Integer 1-5             |
| assignee        | assigned_to            | Resolve to AgentNode    |
| status          | status                 | Enum mapping            |
| estimate        | story_points           | Float                   |
| labels          | tags                   | Array of strings        |

**Node label:** WorkItemNode
**Required properties:** external_id, name, work_item_type, status

### 3.3 Governance Decision to GovernanceNode

| AgilePlus Field | Tracera Graph Property | Transform                  |
| --------------- | ---------------------- | -------------------------- |
| id              | external_id            | Prefix with ap-gov:        |
| title           | name                   | Pass through               |
| decision        | verdict                | Enum: approve/reject/defer |
| rationale       | reasoning              | Store as text              |
| deciders        | decided_by             | Array of AgentNodes        |
| effective_date  | effective_at           | ISO 8601                   |
| review_round    | review_cycle           | Integer                    |

**Node label:** GovernanceNode
**Required properties:** external_id, name, verdict, effective_at

### 3.4 Research Document to ResearchDocNode

| AgilePlus Field | Tracera Graph Property | Transform              |
| --------------- | ---------------------- | ---------------------- |
| id              | external_id            | Prefix with ap-rd:     |
| title           | name                   | Pass through           |
| abstract        | summary                | Truncate to 2000 chars |
| content         | body                   | Store as JSONB         |
| authors         | authored_by            | Array of AgentNodes    |
| citations       | references             | Array of URLs          |
| tags            | tags                   | Array of strings       |

**Node label:** ResearchDocNode
**Required properties:** external_id, name, summary

---

## 4. Trace Link Types

| #   | Relation   | Source Types    | Target Types | Description                          |
| --- | ---------- | --------------- | ------------ | ------------------------------------ |
| 1   | specifies  | SpecNode        | WorkItemNode | A spec governs a work item           |
| 2   | decides    | GovernanceNode  | SpecNode     | A governance decision affects a spec |
| 3   | implements | WorkItemNode    | CodeArtifact | A work item delivers code            |
| 4   | references | ResearchDocNode | SpecNode     | A research doc supports a spec       |
| 5   | validates  | TestNode        | SpecNode     | A test verifies a spec               |
| 6   | observes   | MetricNode      | WorkItemNode | A metric tracks a work item          |

### 4.1 Link Properties

```sql
CREATE TABLE trace_link (
    id              TEXT PRIMARY KEY,
    source_node_id  TEXT NOT NULL REFERENCES graph_node(id),
    target_node_id  TEXT NOT NULL REFERENCES graph_node(id),
    relation        TEXT NOT NULL,
    confidence      REAL NOT NULL DEFAULT 1.0 CHECK (confidence BETWEEN 0.0 AND 1.0),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    metadata        TEXT,
    UNIQUE(source_node_id, target_node_id, relation)
);
```

---

## 5. Three-Phase Ingestion Architecture

### 5.1 Phase 1 - Polling

> **Status 2026-11-02:** the synchronous accept path exists; the polling loop,
> `ingestion_state` delta-sync table, webhook HMAC verification and the Redis
> event-bus consumer are **not implemented**.

- Poll interval: configurable, default 5 minutes
- Delta sync: AgilePlus returns only entities modified since last_sync_token
- Backpressure: exponential backoff on 429, max 10 minutes
- State store: ingestion_state table holds last_sync_token per entity type

### 5.2 Phase 2 - Webhooks

- Delivery guarantee: at-least-once; idempotency key deduplicates
- Retry policy: 3 attempts with 1s, 5s, 30s delays
- Verification: HMAC-SHA256 signature in X-AgilePlus-Signature header
- Payload limit: 1 MB; larger payloads trigger polling fallback

### 5.3 Phase 3 - Event Bus

- Stream: agileplus:events in Redis
- Consumer group: tracera-ingestion
- Batch size: 50 events per poll
- Dead letter queue: agileplus:events:dlq for poison messages

---

## 6. Coverage Matrix Enrichment

### 6.1 Automatic Coverage Links

1. When a WorkItemNode is ingested, check for matching CodeArtifact nodes by name/label similarity
2. When a SpecNode is ingested, check for matching TestNode nodes by spec-reference annotation
3. When a GovernanceNode with verdict=approve is ingested, mark downstream specs as governance_verified

### 6.2 Coverage Score Computation

```
governance_coverage = (linked_nodes_with_governance) / (total_active_nodes)
trace_coverage = (nodes_with_valid_trace_links) / (total_active_nodes)
enriched_coverage = 0.6 * test_coverage + 0.4 * governance_coverage
```

---

## 7. Memory Distillation Pipeline

### 7.1 Distillation Stages

1. Aggregation - 90-day window of raw ingestion events
2. Pattern Mining - min_support threshold of 0.3
3. Abstraction - Generalize to MemoryNode
4. Storage - Write to graph as MemoryNode

### 7.2 Pattern Types

| Pattern                | Example                                         |
| ---------------------- | ----------------------------------------------- |
| approval_velocity      | Specs approved in < 2 days have fewer revisions |
| reviewer_bias          | Reviewer X approves 92% of Team A submissions   |
| spec_scope_correlation | Specs with >5 work items have 3x more reviews   |
| decision_deferral_rate | 15% deferred; avg deferral = 12 days            |

### 7.3 Triggers

- Scheduled: nightly batch at 02:00 UTC
- On-demand: POST /api/v1/distillation/run
- Post-ingestion: if >100 new events since last distillation

---

## 8. Error Handling

### 8.1 Retry Strategy

| Error Type         | Strategy                         |
| ------------------ | -------------------------------- |
| Validation error   | No retry; report to caller       |
| Duplicate/version  | No retry; idempotent skip        |
| Rate limit (429)   | Retry after Retry-After header   |
| Timeout (504)      | Retry up to 3 times, exponential |
| Server error (5xx) | Retry up to 2 times              |

---

## 9. Authentication

JWT claims: iss=agileplus.tracera.io, aud=ingest.tracera.io, exp=15min, scope=ingest:write

Per-entity scopes: ingest:specs, ingest:work-items, ingest:governance, ingest:research-docs

---

## 10. Performance Targets

| Metric                          | Target      |
| ------------------------------- | ----------- |
| Polling ingestion latency (p95) | < 500ms     |
| Webhook ingestion latency (p95) | < 200ms     |
| Event bus throughput            | > 500 msg/s |
| Coverage delta computation      | < 100ms     |
| Memory distillation (nightly)   | < 60s       |

---

## 11. Acceptance Criteria

| #     | Criterion                                                            |
| ----- | -------------------------------------------------------------------- |
| AC-01 | Endpoint accepts valid POST with all 4 entity types                  |
| AC-02 | Endpoint returns 401 for missing/invalid token                       |
| AC-03 | Endpoint returns 409 for duplicate idempotency key                   |
| AC-04 | Endpoint returns 429 when rate limit exceeded                        |
| AC-05 | Each entity type maps to correct graph node label                    |
| AC-06 | Spec mapping preserves all required properties                       |
| AC-07 | WorkItem mapping handles all work_item_types                         |
| AC-08 | Governance mapping enforces verdict enum                             |
| AC-09 | ResearchDoc mapping truncates summary at 2000 chars                  |
| AC-10 | All 6 trace link types create valid edges                            |
| AC-11 | Trace link conflict resolution prefers event_bus > webhook > polling |
| AC-12 | Coverage delta computed and returned in every response               |
| AC-13 | Memory distillation extracts patterns from 90-day window             |
| AC-14 | Memory distillation respects min_support of 0.3                      |
| AC-15 | Polling phase uses delta sync with last_sync_token                   |
| AC-16 | Webhook phase verifies HMAC-SHA256 signature                         |
| AC-17 | Event bus consumer processes batch of 50 events                      |
| AC-18 | Dead letter queue receives poison messages after 3 retries           |
| AC-19 | Idempotency key prevents duplicate entity creation                   |
| AC-20 | Partial success returns 202 with status: partial                     |
| AC-21 | Entity validation errors include field name and suggestion           |
| AC-22 | Authentication JWT is validated with correct issuer/audience         |
| AC-23 | Per-entity authorization scopes are enforced                         |
| AC-24 | Webhook payload limit of 1MB triggers polling fallback               |
| AC-25 | Performance: polling p95 < 500ms under 100 concurrent requests       |
| AC-26 | Performance: webhook p95 < 200ms under 500 concurrent requests       |

---

## 12. Migration Plan

| Phase | Duration | Description                                      |
| ----- | -------- | ------------------------------------------------ |
| 1     | 2 weeks  | Implement polling ingestion + unit tests         |
| 2     | 1 week   | Add webhook ingestion + signature verification   |
| 3     | 1 week   | Add event bus consumer + dead letter queue       |
| 4     | 2 weeks  | Coverage matrix enrichment + memory distillation |
| 5     | 1 week   | Load testing + performance tuning                |

---

## 13. Dependencies

| Dependency            | Version | Purpose                         |
| --------------------- | ------- | ------------------------------- |
| AgilePlus Gateway API | >= 2.0  | Source of governance entities   |
| Redis                 | >= 7.0  | Event bus and dead letter queue |
| PostgreSQL            | >= 15   | Graph node storage              |
| axum                  | >= 0.7  | HTTP framework                  |
| serde / serde_json    | >= 1.0  | Serialization                   |
| jsonwebtoken          | >= 9.0  | JWT validation                  |
| sha2 / hmac           | >= 0.10 | Webhook signature verification  |

---

_End of Spec 009_
