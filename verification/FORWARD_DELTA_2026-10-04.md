# Forward delta — 2026-10-04 product mutation/invalidation

This file records implemented deltas that supersede earlier WBS wording.

## Completed since the prior WBS

The ProductApplication mutation surface now includes product/path-scoped:

- baseline acceptance;
- observation append;
- evidence reuse decision append;
- immutable dependency-edge append;
- bounded dependency-change invalidation execution.

The HTTP product surface mounts these writes behind existing bearer + CSRF
protection.

## Dependency authority

Dependency invalidation no longer needs or permits an HTTP caller to supply the
authoritative graph.

A new product-scoped immutable dependency ledger exists on both SQLite and
Postgres with:

- stable dependency_edge_id;
- product_id;
- dependency_ref;
- dependent_ref;
- typed authority string;
- revision;
- active flag;
- recorded_at;
- exact replay idempotency;
- conflicting immutable-ID rejection;
- unknown-product rejection.

ProductApplication loads persisted edges for the requested product/revision,
maps their authority, executes bounded traversal and persists the invalidation
batch atomically.

## Bounded HTTP truth

The dependency invalidation response exposes:

- affected;
- continuation;
- complete;
- persisted_event_count.

A mounted-route witness asserts that budget exhaustion remains
`complete=false`, continuation remains visible, and only the visited frontier
is persisted.

## Deployment security fix

CORS and CSRF now share one trusted-browser-origin policy. Previously CORS
allowed deployed Vercel/product origins while CSRF accepted only
`http://127.0.0.1:18000`, which would have made every production browser POST
fail with 403.

## Remaining mutation work

- certificate-revocation mutation route;
- observation/reuse/baseline/dependency replay semantics at application/HTTP
  where not already inherited from persistence;
- dependency supersession/deactivation semantics rather than rewriting history;
- Postgres native execution parity for the dependency ledger and mutation path.

## Immediate native gate

Run current migrations, Rust tests, mounted product routes and Clippy on one
concrete candidate. Preserve SQLite/Postgres differences as explicit evidence
until both execute the same contract suite.
