# Reuse / Invalidation Persistence v1

**Date:** 2026-09-30  
**Implementation:** SQLite 011 / Postgres 0012.

## Purpose

Persist the *decision to reuse evidence* separately from the original observation, and persist invalidation as append-only events.

## Why separate reuse decisions

Observation:
> verifier V observed result R for candidate/configuration C.

ReuseDecision:
> policy P admitted that observation as proof for target T.

Those are different facts.

A later policy/certificate/dependency change can invalidate the second without rewriting the first.

## Revocation flow

```text
Observation O
   ↓
ReuseDecision R
   ← Certificate C

C revoked
   ↓
InvalidationEvent
 target = R
 state = SUSPECT/INVALID_FOR_TARGET

Observation O remains unchanged.
```

## Current limitation

The v1 ledger records state transitions but does not yet enforce a single materialized current-state row. Current applicability may be derived from latest admitted decision + invalidation events during the first vertical slice.

If query load justifies it, add a materialized projection later while retaining event history.

## Next

- add Rust records/port methods;
- SQLite/Postgres adapters;
- revocation fixture;
- bounded propagation engine;
- prove invalidation cannot delete historical observations.
