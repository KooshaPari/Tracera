# Tracera Pass 07 — Runtime Reachability and Verticalization Findings

**Date:** 2026-09-29  
**Status:** source-backed implementation finding; NOT product acceptance.  
**Inspected revision:** `cc4cba87e049932e837df65a5cec04baeb363815`

## Purpose

Pass 06 established candidate architecture semantics and a research-only oracle. Pass 07 asks a different question:

> Which Tracera product-model primitives are actually connected into a usable runtime/product journey today?

Repository search is used as a static reachability signal. Absence from search is not proof that dynamic/reflection-generated wiring cannot exist; findings are therefore phrased narrowly.

## F-07-01 — product query layer is not mounted

Search for `query_intents(`, `build_product_view(`, `ProductQuery` and `InvalidationIndex` finds definitions/re-exports and unit tests, but no server handler/router consumer.

### Consequence

The earlier `query_intents` defects are currently best classified as **latent domain-contract defects**, not demonstrated production isolation vulnerabilities:
- `ProductQuery.product_id` is declared but not applied by `query_intents`;
- invalid kind/status values parse to `None`, removing that filter;
- baseline filtering is `>=`, not an exact snapshot selector.

Before mounting this helper, the contract must decide:
- invalid discriminator → explicit error vs empty result;
- exact baseline snapshot vs historical lower-bound query;
- whether product scoping is mandatory in the helper or guaranteed by a typed/pre-scoped repository boundary.

## F-07-02 — assessment product scoping is internally inconsistent

`assess_product(product_id, observations)` initially builds a map from observations matching the requested product, but then:
- calls `assess_capability(cap_id, observations)` with the **entire input observation slice**;
- derives result baseline from the entire input slice;
- reports `observation_count = observations.len()`.

Additionally, the grouping key is `obs.product_id`, while `Observation` has a separate optional `capability_id`.

`assess_with_intents` filters observations where `o.product_id == intent.id`, again conflating product and capability identities.

### Required adversarial witness

At minimum:
1. product A and product B;
2. overlapping capability labels/IDs;
3. A has current passing proof;
4. B has current failing proof and a higher baseline;
5. assess A;
6. prove B cannot affect A status, baseline, count, findings, or explanation.

A second case must bind one product to two distinct capabilities through `capability_id` and prove they remain separate.

## F-07-03 — explicit Unknown/Stale can false-green

`assess_capability` explicitly branches on Failed, Passed and Inconclusive. If observations are timestamp-fresh but their explicit result is `Unknown` or `Stale`, the function can fall through to the final Satisfied branch because no failure/inconclusive condition matched.

This is stronger than a design concern: the enum explicitly supports these states, but the assessment state machine does not exhaustively handle them.

### Required invariant

No `ObservationResult` variant other than an admissible Passed result may contribute to Satisfied without an explicit rule proving why.

Prefer exhaustive matching over a fallthrough comment such as "All relevant observations passed."

## F-07-04 — determinism is time-parameterized, not input-only

Assessment documentation says identical inputs produce identical output, but freshness reads `Utc::now()` internally and result metadata also records current time.

Correct contract should distinguish:
- deterministic **decision** for a frozen evaluation time/configuration;
- nondeterministic metadata timestamp;
- expected state transition as evidence crosses a freshness boundary.

Evaluation time should be injectable/bound in a grader identity when reproducibility matters.

## F-07-05 — product persistence schema exists without an observed domain repository

SQLite and PostgreSQL migrations create `product_nodes`, `product_edges`, and the SWEE→product FK. Static search finds these tables referenced in design/migrations/traversal comments, but no observed store CRUD/handler path for them.

`ObservationStore` is an in-memory store inside the product module.

### Consequence

The product model currently has useful domain primitives + schema, but the inspected source does not establish a persisted end-to-end product-model path.

## F-07-06 — page decomposition UI recovers original Featuregraph intent but is detached

`PageDecompositionView` models:
```
Site → Page → Layout → Section → Component → Element
```
with search, selection, depth/view modes, and code/design callbacks.

Static search finds the component and its test file, but no live consumer/route.

The test suite demonstrates useful component behavior, but multiple tests merely assert that the component/title/buttons render and do not actually verify the named action (for example some expand/collapse/view-mode/statistics/accessibility cases).

### Consequence

Do not delete this surface as dead code without forensic review: it is a concrete implementation of the original Featuregraph UI decomposition. But do not count it as a usable product journey until it is mounted to canonical persisted state and its meaningful interactions are verified.

## Architectural conclusion

The shortest low-rewrite path is **verticalization**, not another horizontal subsystem:

```
accepted Product + Baseline
  → persisted product graph
  → exact scoped observation
  → assessment/dissatisfaction
  → bounded product query
  → mounted machine interface
  → mounted human projection
  → proposed delta
  → external/durable work reference
  → new evidence
  → reassessment
```

Reuse current primitives where semantically sound. Fix/invalidate them where adversarial witnesses fail.

## Next bounded implementation/verification design

1. Define exact identity types: ProductId, ProductEntityId/CapabilityId, Baseline/Configuration, ObservationId.
2. Specify repository interfaces for persisted product nodes/relations/observations independent of SQLite/Postgres.
3. Specify exhaustive assessment truth table, including Unknown/Stale/Inconclusive and frozen evaluation time.
4. Define the two-product/two-capability adversarial fixture.
5. Trace actual router/API/MCP and UI data paths and select one minimal mounted vertical slice.
6. Define evidence required for restart persistence and worker-neutral reassessment.
7. Only then decide whether existing product primitives are repaired, wrapped, migrated, or retired.

This pass does not authorize mass test generation. It does define concrete future test/oracle cases required before the product layer can be graded green.
