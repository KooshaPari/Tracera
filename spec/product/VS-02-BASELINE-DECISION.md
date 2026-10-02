# Tracera Baseline Representation Decision

**Date:** 2026-09-30  
**Status:** accepted for VS-02 implementation.

## Candidates

### A — explicit baseline membership

Each accepted baseline explicitly references the exact entity revisions it contains.

### B — validity intervals

Each entity/assertion revision stores valid-from/valid-to baseline numbers and a baseline is reconstructed by interval predicates.

## Required vertical-slice queries

1. exact historical baseline snapshot;
2. compare baseline N to N+1;
3. retrieve one logical entity as it existed at baseline N;
4. prove evidence was evaluated against exact baseline;
5. preserve branches/future non-linear baseline ancestry;
6. import v0 baseline_revision values;
7. backend parity SQLite/Postgres;
8. no accidental historical mutation.

## Decision — explicit membership

Use explicit baseline membership for v1.

### Why

- exact snapshots are direct and auditable;
- parent baseline identity can support future non-linear histories;
- no temporal interval overlap bugs;
- no assumption that revision numbers form one global linear timeline;
- evidence binds directly to immutable BaselineId;
- import from v0 is straightforward;
- SQL semantics are nearly identical across SQLite/Postgres.

### Cost

Membership rows can be numerous for large baselines.

Mitigations:
- baseline creation can copy parent membership transactionally and apply delta;
- indexes make exact snapshot reads straightforward;
- later storage optimization/materialized inheritance can preserve the logical contract.

Do not prematurely optimize by weakening identity/history semantics.

## Delta representation

A baseline may also store a change/delta for efficient comparison, but delta is not the sole source of snapshot truth in VS-02.

## Acceptance invariants

- accepted baseline immutable;
- one entity revision per logical entity per baseline;
- membership belongs to same product;
- parent baseline belongs to same product;
- revision_number unique within product;
- observation references BaselineId, not only revision integer.
