# VS-02 Schema Gap — Product Scope and Baseline History

**Date:** 2026-09-30  
**Status:** blocking schema finding before SQLite implementation.

## Existing schema

SQLite `009_product_model.sql` and Postgres `0010_product_model.sql` are intentionally parallel.

Current `product_nodes`:
- `id TEXT PRIMARY KEY`;
- `product_id TEXT NOT NULL`;
- `intent_kind`;
- title/description/status;
- `baseline_revision INTEGER`.

Current `product_edges` references `product_nodes(id)`.

## Gap 1 — scoped logical IDs contradict global primary key

Rust `AcceptedIntent.id` documents the ID as **scoped to the product**.

SQL makes `id` globally unique.

Therefore this valid mature case cannot be represented directly:

```text
Product A / capability "search"
Product B / capability "search"
```

without inventing globally prefixed IDs in the persistence adapter, which would make an undocumented storage encoding part of identity semantics.

### Required correction

Separate:
- stable globally unique row/entity identity;
- product-scoped logical/local identity.

Candidate additive fields/table design:
- `entity_id` globally stable opaque identity;
- `product_id`;
- `local_id`;
- unique(`product_id`, `local_id`, revision/effectivity scope as appropriate).

Do not silently redefine `AcceptedIntent.id` globally.

## Gap 2 — baseline is a mutable scalar, not a historical object

`baseline_revision` on `product_nodes` does not by itself represent immutable accepted baselines.

Questions it cannot answer cleanly:
- which exact set of entities constituted baseline 3?
- what was the parent of baseline 3?
- when was it accepted?
- can the same logical entity have different accepted content in baselines 2 and 3?
- what exact baseline did an observation evaluate if rows were later updated?

### Required correction

Add a first-class baseline table/identity and baseline membership/revision semantics.

Minimal candidate:
- `product_baselines(product_id, baseline_id, revision_number, parent_baseline_id, accepted_at, metadata)`;
- entity revision table or immutable entity rows;
- membership/validity relation from baseline to entity revision.

The exact normalized shape should be chosen to minimize duplication while preserving immutable historical reads.

## Gap 3 — edge identity/history

Current edge uniqueness:
`UNIQUE(source_id, target_id, edge_type)`.

This assumes one timeless edge between globally unique node IDs.

Mature requirements need:
- relation revision/provenance;
- authority;
- applicability;
- semantic status/suspect state;
- historical validity.

Do not mutate an old edge into a new baseline's meaning.

## Gap 4 — observation persistence is not represented here

The product graph migration includes an `observation_covers_capability` edge type, but observations are Rust values and evidence/storage concepts elsewhere.

A graph edge is not sufficient evidence identity.

VS-02 must establish an append-only observation/evidence persistence path bound to product + baseline + subject.

## Reuse decision

**Reuse the existing migration as historical/product-graph v0. Do not drop it.**

Add an additive v1 persistence migration that:
- preserves existing tables;
- introduces explicit baseline history;
- resolves global-vs-local identity;
- supports append-only observations;
- allows semantic invalidation without history deletion.

Provide a projection/import path from old `product_nodes/product_edges` into the new port.

## Backend parity

SQLite and Postgres currently mirror each other closely. Preserve that property in the additive migration and test both through the same repository contract.

## Gate

Do not implement VS-02 CRUD directly on `product_nodes` as if the schema already satisfies the mature contract. That would bake the discovered identity/history contradiction into the repository API.
