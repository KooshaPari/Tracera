# Tracera VP Stages and Product-Shape Grading

Stages are projections over the canonical mature contract, not independent backlogs.

## Stage semantics

Each FR can be `required`, `recommended`, `optional`, `excluded`, or `not_applicable` for a stage, with independent criticality.

A stage is achieved only when:
1. every essential required blocker is verified;
2. declared required feature completion rules close;
3. declared critical journeys close;
4. no failed/unknown/stale/inconclusive result is silently converted to pass.

Percent completion is descriptive, not sufficient for stage acceptance.

## CVP

The Current Viable Product is the smallest **real, encapsulated Tracera** that demonstrates the product's canonical loop through mature-shaped boundaries:

```text
accepted product/intent
 -> persistent graph
 -> trace/evidence binding
 -> deterministic assessment
 -> dissatisfaction finding
 -> bounded human/agent navigation
 -> resolution reference
 -> re-verification
 -> truthful product-state update
```

A CVP may use narrow adapters and local persistence, but SHOULD NOT require a rewrite of the product model, identity, evidence, assessment or grading semantics to reach MVP.

## MVP

MVP expands the same spine into a practically reusable product: broader feature closure, multiple real products/components, durable restart/recovery, agent and human surfaces, external-work references, stronger history/impact reasoning, and repeatable grading.

## GA

GA requires broad accepted behavior, supported runtime/deployment, security/governance, recovery, compatibility, release proof, and appropriate supported integrations. Optional integrations do not become core merely because code exists.

## Mature

Mature is the currently accepted full contract projection. It is expected to evolve through explicit baseline amendments.

## "30% done" rule

Never report only a raw percentage. A status projection MUST include:

```text
Mature contract completeness
Highest achieved stage
CVP/MVP/GA readiness
Structural shape
Core features closed / total
Critical journeys closed / total
Implementation survivability
Mature-contract compatibility
Transition burden
Unknown / stale / inconclusive / failed blockers
```

## Shape derivation

- **scaffold** — boundaries/files/types exist but little usable behavior closes.
- **primitive_system** — substantial primitives work but product journeys do not close.
- **product_husk** — broad visible surface with shallow, stubbed, disconnected or unverified behavior.
- **vertical_slice** — at least one narrow real end-to-end product journey closes.
- **narrow_functional_product** — multiple coherent core journeys close but mature breadth is limited.
- **broad_product** — broad core feature and journey closure.

Shape and stage are independent.

## Transition health

For each stage transition report:
- additive FRs;
- progressive enrichments;
- new adapters;
- expected replacements;
- breaking interfaces;
- schema resets;
- data migrations;
- discarded core implementations.

A stage that is usable but creates high rewrite burden is not architecturally equivalent to one that grows additively.
