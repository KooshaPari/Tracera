# VS-01 — Product Persistence Port Contract

**Status:** proposed implementation contract.  
**Date:** 2026-09-30.

## Decision

Do not immediately enlarge the existing broad `Store` trait with the entire mature product ontology.

Introduce a narrow product persistence port first, implemented by SQLite/Postgres adapters and consumed by product application services.

After the vertical slice proves the boundary, decide whether to:
- merge the port into `Store`;
- retain it as a focused sub-port composed by the application;
- split the legacy Store into capability-specific ports.

This minimizes blast radius and avoids forcing every existing Store test/mock to implement speculative mature semantics.

## Slice types

These are intentionally narrower than the mature ontology.

### PersistedProduct
- product_id: stable ProductId
- display_name
- created_at

### PersistedBaseline
- product_id
- baseline revision/order compatibility field
- baseline_id/string stable identity if introduced in migration
- accepted_at
- parent reference optional
- configuration metadata JSON for v1 compatibility

### PersistedProductEntity
- product_id
- entity_id
- entity_kind
- title
- revision
- status
- metadata

### PersistedAssertion
- assertion_id
- product_id
- source_entity_id
- predicate
- target_entity_id/value
- status
- authority
- applicability metadata
- created_at

### PersistedObservation
Reuse/upgrade current Observation semantics, but persistence must retain:
- product;
- capability/subject;
- baseline;
- result;
- collector/verifier;
- recorded_at;
- raw/provenance reference.

Candidate/configuration enrichment can be additive once identity migration is decided.

## Required port operations

- create/get product;
- append/get baseline;
- put/get/list entities scoped by product+baseline;
- put/get/list assertions scoped by product+baseline;
- append/list observations scoped by product + subject + baseline;
- transaction boundary for accepting a new baseline/change;
- exact historical reads.

No unbounded "list everything" method is required for the slice.

## Invariants

1. product scope is explicit in every product-owned read/write;
2. historical baseline data is immutable or append/supersede;
3. observations are append-only;
4. same local entity/capability label in two products cannot collide;
5. backend adapters return equivalent semantic results;
6. restart preserves exact IDs and history;
7. product persistence does not depend on UI renderer state;
8. work/AttemptId is not used as product identity;
9. bounded queries expose limits/continuation;
10. invalidation changes applicability state, not historical bytes.

## Backend parity fixture

Two products A/B:
- same local capability name `search`;
- different baseline revisions;
- different assertion/evidence;
- restart database;
- query A exactly;
- prove B cannot affect rows/count/baseline/assessment input.

Run same contract against SQLite and Postgres.

## Migration rule

Current migrations already contain product node/edge tables. Inspect them before adding new schema.

Prefer additive migration/reuse if their columns can faithfully support this slice.

Do not rename/drop historical tables merely to make the new ontology aesthetically clean.

If old tables are semantically incompatible:
- document mismatch;
- add new schema;
- provide explicit migration/projection;
- retain historical provenance.

## Exit gate

VS-01 is accepted only when the port is narrow enough to implement now and rich enough that VS-02/03/04 do not require replacing its identity/history semantics.
