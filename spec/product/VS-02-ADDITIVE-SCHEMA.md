# Tracera Product Persistence v1 — Additive Schema Design

**Date:** 2026-09-30  
**Status:** proposed schema for VS-02/03; preserves v0 product_nodes/product_edges.

## Goals

Fix v0 limitations without rewriting historical schema:
- product-scoped local identity vs global row identity;
- immutable baseline history;
- entity revision history;
- relation/assertion history;
- append-only observations;
- explicit applicability/invalidation;
- SQLite/Postgres parity.

## Tables

### product_baselines_v1

```sql
baseline_id TEXT PRIMARY KEY,
product_id TEXT NOT NULL,
revision_number INTEGER NOT NULL,
parent_baseline_id TEXT NULL,
accepted_at TIMESTAMP/TEXT NOT NULL,
metadata JSON/JSONB/TEXT NOT NULL DEFAULT '{}',
UNIQUE(product_id, revision_number)
```

`baseline_id` is immutable opaque identity. Revision number is human/order compatibility, not the only identity.

### product_entities_v1

Stable cross-baseline logical entity identity.

```sql
entity_id TEXT PRIMARY KEY,
product_id TEXT NOT NULL,
local_id TEXT NOT NULL,
entity_kind TEXT NOT NULL,
created_at ...,
UNIQUE(product_id, local_id)
```

This permits Product A/search and Product B/search.

### product_entity_revisions_v1

Immutable content revision.

```sql
entity_revision_id TEXT PRIMARY KEY,
entity_id TEXT NOT NULL REFERENCES product_entities_v1(entity_id),
content_revision INTEGER NOT NULL,
title TEXT NOT NULL,
description TEXT NOT NULL DEFAULT '',
status TEXT NOT NULL,
metadata ...,
created_at ...,
UNIQUE(entity_id, content_revision)
```

### baseline_entity_membership_v1

Which exact revision participates in an accepted baseline.

```sql
baseline_id TEXT NOT NULL,
entity_revision_id TEXT NOT NULL,
PRIMARY KEY(baseline_id, entity_revision_id)
```

Application validation must prevent two revisions of the same entity in one accepted baseline.

### product_assertions_v1

Immutable relation/assertion revision rather than timeless mutable edge.

Candidate fields:
- assertion_id;
- product_id;
- source_entity_revision_id;
- predicate;
- target_entity_revision_id nullable;
- target_value JSON nullable;
- authority;
- applicability JSON;
- semantic_status;
- provenance JSON;
- created_at.

A later assertion supersedes/invalidates through explicit relation/event rather than overwriting historical assertion bytes.

### product_observations_v1

Append-only evidence observation:
- observation_id;
- product_id;
- baseline_id;
- subject_entity_id/revision optional;
- capability/local subject;
- candidate_ref;
- configuration JSON;
- result;
- collector/verifier id;
- verifier_version;
- recorded_at;
- raw_evidence_ref;
- metadata.

### evidence_reuse_decisions_v1

Needed for safe certificate/invalidation fanout:
- reuse_decision_id;
- observation_id;
- target_baseline_id;
- target_candidate_ref;
- criterion_ref;
- applicability_state;
- compatibility_certificate_ref nullable;
- decided_at;
- policy_version;
- reason/provenance.

### invalidation_events_v1

Append-only:
- invalidation_id;
- trigger_kind;
- trigger_ref;
- target_kind;
- target_ref;
- prior_state;
- new_state;
- reason;
- occurred_at.

This is not the only possible graph representation; it makes semantic changes auditable.

## Baseline acceptance transaction

Accepting baseline N should transactionally:
1. verify unique product revision number;
2. verify parent exists/belongs to same product;
3. verify each membership points to one entity revision;
4. reject duplicate logical entity revisions in same baseline;
5. insert baseline;
6. insert membership;
7. append acceptance event/provenance.

No mutation of baseline N after acceptance.

## v0 projection/import

Existing `product_nodes` remains queryable.

Migration helper can project each v0 row into:
- product_entities_v1 entity keyed by product + v0 id;
- one entity revision representing current v0 row;
- synthetic/imported baseline identity derived from product + baseline_revision;
- membership.

Record provenance:
`source_schema = product_nodes_v0`, original row id and migration version.

Do not delete v0 rows.

Existing `product_edges` can be imported as assertions with v0 provenance and authority reflecting their original source, not automatically accepted as mature truth.

## SQLite/Postgres representation

Use semantically equivalent types:
- SQLite JSON stored as validated TEXT where JSON1 behavior is sufficient;
- Postgres JSONB;
- timestamps RFC3339 TEXT vs TIMESTAMPTZ;
- same uniqueness and FK semantics.

Repository contract must normalize backend representation.

## Scope control

VS-02 does not need every mature ontology field.

Do not add:
- arbitrary graph-expression language;
- full certificate authority infrastructure;
- all lifecycle projections;
- every external source type.

The schema must merely avoid making those future semantics impossible.

## Contract tests

Same fixture against SQLite and Postgres:
1. create products A/B;
2. both use local_id `search`;
3. accept A baseline 1 and B baseline 7;
4. revise A/search into baseline 2;
5. prove baseline 1 still returns old revision;
6. append contradictory A/B observations;
7. restart;
8. prove exact identity/history;
9. create reuse decision then invalidate it;
10. prove original observation remains historically queryable.

## Open design questions before migration code

- whether entity revision membership should use validity intervals instead of explicit membership;
- whether assertion membership belongs directly to baseline;
- exact candidate-ref structure;
- whether invalidation state is materialized on reuse decision for fast reads in addition to event history;
- product root entity representation vs separate products table.

Choose using vertical-slice query workload, not aesthetic normalization alone.
