# Tracera Mature Product Model

**Contract:** `TRC-MATURE-V1`  
**Canonical product:** Tracera (`PRD-TRACERA`)  
**Source snapshot:** `17eef2379d4a673e1c8cc71ed7663fae9e94309b`

## Product identity

Tracera is the persistent canonical product/system model for describing accepted product intent, connecting that intent to implementation and evidence, traversing the resulting graph with bounded semantics, detecting dissatisfaction, and presenting truthful product state to humans and agents.

Trace/session observability, memory, SWEE, ingestion, analytics, and external integrations are subordinate capabilities. They do not redefine Tracera as a generic APM, work tracker, agent runtime, or source-code search engine.

**AgilePlus owns work execution. Tracera owns product identity, accepted intent, product relations, evidence interpretation, assessment, dissatisfaction, and product-state projection.**

## Hierarchy

```text
Product
  -> Pillar / Domain
    -> Core/Supporting/Enabling Feature
      -> Feature
        -> Atomic FR
          -> Acceptance Criterion
            -> Verification Case / Oracle
              -> Implementation / Test / Evidence
```

Parent nodes aggregate descendants and never earn duplicate completion credit.

## Product roles

- `core`: fundamentally defines the product.
- `supporting`: makes core behavior practical.
- `enabling`: technical prerequisite.
- `differentiator`: material advantage beyond minimum viability.
- `enhancement`: improves an existing capability.
- `convenience`: useful polish.
- `operational`: run/support/deploy behavior.
- `auxiliary`: valuable but does not expand canonical functional completion.
- `experimental`: hypothesis, not accepted core scope.

## Structural shape

A raw completion percentage is insufficient. Derive independently:

- mature-contract completeness;
- VP-stage readiness;
- feature closure;
- journey closure;
- structural shape;
- implementation survivability;
- mature-contract compatibility;
- transition burden.

Supported structural-shape vocabulary:

`scaffold | primitive_system | product_husk | vertical_slice | narrow_functional_product | broad_product`

Shape is not a maturity stage. A low-percentage vertical slice may be more usable than a higher-percentage husk.

## Stub-first growth invariant

> **Stub the breadth; mature the spine.**

Early stages SHOULD expose mature-shaped boundaries and implement the smallest real closed journey through them. Prefer additive/enriching evolution. Replacement-only implementations are allowed only when replacement and migration cost are explicitly bounded and trivial.

Growth dispositions:

`permanent_spine | progressive | stub | adapter | replaceable | prototype_only | retiring`

## Working baseline

`spec/product/mature-contract.v1.json` currently contains:

- 25 pillars;
- 200 features;
- 1,000 atomic FR records;
- stage projections for CVP, MVP, GA and Mature;
- verification intent and positive/negative oracle descriptions;
- future test identities.

The number 1,000 is not a quota and is not itself evidence of completeness. Future reconciliation may split, merge, add or retire requirements through explicit baseline amendments.

## Existing-source reconciliation

Older repository and registry documents describe Tracera as trace/session observability and memory infrastructure. Those capabilities remain represented, but the controlling product definition is the canonical product/system graph and dissatisfaction model. Historical documents remain useful evidence and migration oracles; they are not allowed to silently shrink the accepted product horizon.

## Explicit non-ownership

Tracera does not become:
- the canonical work-execution state machine (AgilePlus);
- an agent runtime;
- a generic source-code search product;
- a generic cross-org analytics dashboard;
- a duplicate Git store.

External systems may be represented, observed and linked without Tracera taking ownership of their native facts.
