# EXP-12 executed checkpoint — suspect/invalidation propagation

**Date:** 2026-09-30  
**Experiment:** TRC-EXP-12-INVALIDATION-01  
**Scope:** synthetic reference model; not Tracera runtime proof.

## Result

- semantic checks: 6/6 passed;
- mutation controls: 4/4 detected.

## Confirmed seed semantics

1. Direct admitted dependency change makes current proof SUSPECT.
2. Unrelated criterion remains CURRENT_VALID.
3. Revoked compatibility certificate makes reuse that depended on it SUSPECT.
4. Traversal/evaluation budget exhaustion becomes UNKNOWN, not success.
5. Historical proof remains HISTORICAL_VALID for its original candidate/context.
6. New qualifying proof can be CURRENT_VALID without deleting old proof.

## Mutation controls

Detected broken variants that:
- ignored a changed dependency;
- ignored certificate revocation;
- treated budget exhaustion as success;
- deleted historical proof.

## Promoted rules

Physical relation/evidence existence is distinct from current semantic validity.

Invalidation is a change in current applicability, not retroactive deletion of what was observed.

A certificate revocation affects current reuse decisions justified by that certificate; it does not make the original historical observation disappear.

Bounded/partial invalidation traversal must surface uncertainty explicitly.

## Limits

- synthetic dependency graph;
- no real Tracera persistence/runtime;
- no typed transitive graph traversal;
- no certificate scope hierarchy;
- no real change-impact extractor.

Next: integrate these semantics into the repository/evidence contract after native assessment verification.
