# EXP-11 — Dependency-footprint soundness and invalidation

**Status:** architecture experiment specification.

## Problem

Criterion-specific dependency footprints make evidence reuse economically attractive, but a missing dependency is dangerous:

```text
real dependency changes
  + footprint omits it
  → old evidence appears reusable
  → false green
```

Therefore footprint derivation is itself a verification problem.

## Sources of footprint edges

Classify every dependency edge by provenance:

1. deterministic:
   - compiler/indexer reference;
   - build graph;
   - package/lock resolution;
   - schema/API reference;
   - deployment/config declaration;
   - test instrumentation/coverage where semantically appropriate;
2. declared:
   - criterion/test metadata;
   - architecture/spec contract;
3. inferred:
   - static/LLM/graph inference;
4. compatibility assertion:
   - explicit proof that a changed dependency is irrelevant/compatible.

Confidence is not authority.

## Conservative admission rule

A criterion footprint may be used to **exclude** a changed dimension from re-verification only when irrelevance is established by deterministic/accepted evidence.

An inferred absence of a dependency is not proof of independence.

Inferred edges may expand the footprint conservatively. They must not remove a deterministic/accepted dependency without an explicit superseding decision/proof.

## Change invalidation

When a dependency changes:

- direct criteria depending on it become suspect;
- evidence tied to those criteria remains historically valid but not current proof;
- transitive dependents become suspect according to typed dependency rules;
- compatibility certificates may discharge only their declared edge/criterion/operation scope;
- revalidation restores current applicability.

## Required adversarial cases

1. criterion depends on lockfile; footprint omits lock → mutation must be detected.
2. API client generated from schema; schema changes while source caller does not → invalidation propagates through generated artifact.
3. feature flag read dynamically; static source graph misses runtime configuration dependency → declared/runtime evidence must preserve dependency.
4. criterion depends only on GET endpoint; unrelated POST implementation changes → no forced recheck if independence is proven.
5. inferred dependency edge is false positive → may cause extra recheck, not false green.
6. inferred dependency edge is false negative → cannot authorize reuse by itself.
7. dependency removed from accepted architecture but stale deterministic index still reports it → provenance/revision prevents permanent phantom invalidation.
8. compatibility certificate revoked → all reuse decisions depending on it become suspect.
9. transitive chain A→B→criterion; B's compatibility to B' does not imply A compatibility unless scope covers it.
10. test coverage touched file X but semantic criterion also depends on environment/config Y → coverage alone cannot define full footprint.

## Metrics

- unsafe reuse / false green;
- unnecessary invalidations;
- unknown rate;
- footprint precision/recall against curated ground truth;
- revalidation fanout;
- human adjudications;
- inference cost.

## Gate

No product-level evidence reuse based on dependency footprints until:
- deterministic/accepted edge precedence is defined;
- inferred absence cannot prove independence;
- certificate revocation invalidation is implemented;
- false-negative mutation controls exist;
- footprint provenance is revision-bound.
