# Tracera forward work breakdown

Status: canonical recovery WBS as of 2026-10-04.

## Release target

Next meaningful release: remotely usable, zero-paid-service private/operator
cloud alpha.

Target topology:

```
Vercel Hobby frontend
 -> owned product domain
 -> tailnet-aware API naming
 -> Tailscale organizational network
 -> stable service identity where practical
 -> one host-level Caddy
 -> owner's desktop
 -> tracera-server
 -> persistent product state
```

Cloudflare Tunnel is optional public ingress later.

### Current engineering ETA

Assuming focused execution and no newly discovered major browser regression:

- private/operator remote backend alpha: 1–2 focused working days;
- useful authenticated cloud alpha closing HJ-PRE-001..003: 3–5 days;
- broader recovered-product alpha closing HJ-PRE-001..008: 7–12 days.

## P0 — clean authoritative backend candidate

1. Clear branch-owned Rust formatting/Clippy failures.
2. Clear branch-owned Python/Ruff failures without laundering historical debt.
3. Preserve already-green native Rust/product persistence tests.
4. Run the product application/router suite on the exact release candidate.
5. Keep SQLite and Postgres semantic differences explicit.

Exit: one concrete commit with native product persistence/application evidence
and no branch-owned compile/lint blocker.

## P1 — finish ProductApplication mutation vertical

Implement backend-neutral application operations for:

- baseline acceptance;
- observation ingestion;
- evidence-reuse admission;
- dependency-change invalidation;
- compatibility-certificate revocation.

Do not add these to the giant legacy Store and do not couple handlers to
SqliteStore/PgStore.

## P2 — bounded invalidation HTTP

Expose the mature invalidation result without collapsing uncertainty:

```
affected
continuation
complete
persisted_event_count
```

Required adversarial behavior:

- budget exhaustion -> complete=false;
- continuation survives;
- replay is idempotent;
- conflicting immutable replay fails;
- partial persistence rolls back;
- original observation history survives;
- certificate revocation invalidates reuse, not observation;
- cross-product target attempts fail.

## P3 — Postgres contract parity

Execute one shared semantic contract suite against SQLite and Postgres:

- product-scoped IDs;
- immutable baselines;
- parent/membership scope;
- observation scope;
- reuse scope;
- invalidation replay;
- batch rollback;
- certificate revocation;
- bounded continuation;
- historical preservation.

SQL-text similarity is not execution parity.

## P4 — current user journey recovery

After the backend mutation spine is credible, stop expanding backend
architecture and recover the product.

Required order:

1. HJ-PRE-001 product open/select;
2. HJ-PRE-002 product inventory;
3. HJ-PRE-003 canonical complete unified graph;
4. HJ-PRE-004 perspectives;
5. HJ-PRE-005 traceability matrix;
6. HJ-PRE-006 item detail;
7. HJ-PRE-007 relationship mutation;
8. HJ-PRE-008 typed projections.

For each distinguish route existence, rendering, data correctness, interaction
correctness and journey closure.

The first cloud alpha only needs the journeys it claims to ship, but those
journeys must be correct.

## P5 — deployed private/operator alpha

Network doctrine:
`docs/architecture/NETWORK_DEPLOYMENT_DOCTRINE.md`

Required:

- Vercel frontend build;
- owned product hostname;
- tailnet service/API resolution;
- one host-level Caddy;
- desktop backend;
- no browser bearer secret;
- HJ-PRE-001..003 against real remote state;
- restart persistence;
- backup/restore;
- no fallback/stub response represented as product truth.

## P6 — historical executable archaeology

Run isolated historical anchors without rewriting them:

- 0e8b0bdd — strongest pre-performance/LKG candidate;
- 27262fa4 — progressive-loading semantic transition;
- 4a897659 — immediate edge-render repair;
- d5296270 — mega-transaction/scope-collapse pivot.

For each capture build/startup, routes, graph nodes/edges, matrix, item detail,
PageDecomposition, console/network failures and screenshots where useful.

Derive executable:
- LKG-A;
- PERF-START;
- FIRST-BAD;
- STABILITY-LOSS.

## P7 — current versus LKG differential harness

For identical fixtures classify each surface/journey as:

- PARITY;
- INTENTIONAL_SUPERSESSION;
- REGRESSION;
- NEW_CAPABILITY;
- UNKNOWN.

Do not claim product recovery from source-file presence.

## P8 — graph performance only after correctness

Build a canonical complete graph fixture/oracle first.

Benchmark ladder:
1K, 5K, 10K, 25K, 50K, 100K nodes with multiple edge densities.

Evaluate independently:
- data loading;
- rendering;
- viewport culling;
- virtualization;
- layout;
- workers;
- server slicing;
- caching;
- WebGL/WebGPU where justified.

Hard distinction:
not loaded != nonexistent; not rendered != absent; culled != absent.

## P9 — dogfood Tracera on Tracera

Represent the Tracera mature contract, implementation and evidence in Tracera
and ask the product to assess its own candidate. This is a product validation
milestone, not merely a demo.

## P10 — AgilePlus federation

After both independent kernels are trusted:

```
AgilePlus AcceptedWork
 -> Tracera Observation
 -> applicability policy
 -> CurrentValid / Suspect / Stale / Invalid / Unknown
```

Then mutate a dependency and prove applicability changes without rewriting
AgilePlus history or deleting the original Tracera observation.

## Completion discipline

Future status reports separate:

- mature semantic coverage;
- implementation realization;
- native evidence;
- journey closure;
- deployment readiness;
- operational readiness;
- historical parity;
- external validation;
- uncertainty/regressions.

Every report includes time-to-next-deployed/installable release.
