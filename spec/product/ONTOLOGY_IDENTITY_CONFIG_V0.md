# Tracera ontology / identity / configuration v0

**Status:** PROPOSED, falsifiable architecture contract — not accepted schema.  
**Date:** 2026-09-29.  
**Inputs:** current Tracera product/SWEE types, Featuregraph archaeology, PLM/ALM/MBSE research, Passes 01–07.

## Design rule

Do not force every concept into one `NodeKind`. Separate stable product meaning, version/configuration, assertions/relations, realization, observations/evidence, work references, and projections.

## Identity layers

### ProductFamilyId
Optional stable family identity spanning related products/editions.

### ProductId
Stable identity of a product independent of repository name, release, deployment, or worker.

### EntityId
Stable identity of a conceptual product entity across revisions: capability, interaction, interface, requirement, component, etc.

### RevisionId
Immutable revision of an entity's definition. Revision identity is not artifact version and not baseline number.

### ConfigurationId
Identity of a resolved or explicitly named compatible selection of entity revisions, options and contextual values.

### BaselineId
Frozen accepted contract/configuration snapshot for a declared purpose. A baseline references configuration/revision membership; it is not merely a monotonically increasing integer.

### ArtifactId
Identity of a concrete immutable or version-addressable realization: source revision, build artifact, package, image, schema, document revision, test binary, etc.

### DeploymentId
Identity of a realized artifact/configuration in an environment at a point/interval.

### ObservationId
Identity of an append-only measurement/finding/result.

### ChangeId
Identity of a durable proposed product change/graph delta.

### DevelopmentId / AttemptId
External AgilePlus/work-system identities. Tracera references them; it does not use them as product identity.

## Product entity roles

A product entity has a stable ID and typed role. Candidate role families:

- intent: claim, requirement, obligation, constraint, target;
- experience: surface, page/screen, region, interaction, state, journey;
- functional: capability, feature, sub-feature;
- architecture: system, service, component, module, interface, API/event/data contract;
- implementation reference: source unit/symbol/package;
- supply chain: dependency/component;
- verification: criterion, oracle, test/check;
- lifecycle: release/channel/configuration/deployment;
- risk/security: threat, risk, control, mitigation;
- documentation/decision: spec, ADR, rationale;
- external reference.

Do not finalize these enums until projection/use-case review is complete.

## Projection / viewpoint

A `Projection` is a purpose-specific view over shared canonical entities and assertions, not a duplicate product tree.

Examples:
- experience/UI;
- functional;
- journey;
- architecture;
- API/interface;
- implementation;
- supply chain;
- verification;
- lifecycle/release/deployment;
- runtime;
- security/risk;
- documentation/intent.

One entity may appear in several projections. Projection membership/order/layout is separate from semantic identity.

## Assertion / relation

Replace the assumption that every graph edge is a timeless fact.

Candidate assertion fields:

```text
AssertionId
source EntityRef
predicate
target EntityRef/value
projection memberships
authority
provenance
confidence?              # only when meaningful
applicability/effectivity
valid/effective interval?
recorded_at
baseline/configuration context?
status = candidate | accepted | rejected | suspect | superseded
validator/version?
last_validated_at?
```

### Authority is not confidence

Candidate authority classes:
- accepted product decision/fact;
- deterministic authoritative-source fact;
- verified observation-derived fact;
- imported assertion;
- human/agent proposal;
- inferred candidate;
- historical/superseded fact.

A 0.99-confidence inference remains an inference.

## Applicability / effectivity

Inspired by PLM effectivity, but generalized for software.

An applicability scope declares dimensions relevant to a relation/entity/criterion/evidence item. Candidate dimensions:
- product/edition/variant;
- entity/release/version range;
- platform/OS/architecture/device;
- environment;
- tenant/customer class;
- region/regulatory regime;
- feature flags/evaluation context;
- rollout cohort;
- dependency/API/schema versions;
- valid/effective time.

Expressions must be typed, bounded and explainable. Avoid arbitrary executable code as the canonical expression language.

### Unknown is not wildcard

If a target configuration requires a dimension and evidence omits it, reuse is not automatically safe. It is Unknown unless an explicit rule proves irrelevance/subsumption.

## Configuration

A configuration is a resolved product context:

```text
Configuration
  product
  selected entity revisions/options
  environment/platform dimensions
  feature/effectivity values
  external dependency/API versions
  provenance/resolution rule
```

Configurations may be named or derived. Resolution must explain included/excluded assertions.

## Baseline

A baseline freezes accepted product meaning for a purpose:

```text
Baseline
  id
  product
  accepted_at
  parent baseline(s)
  configuration or membership snapshot
  accepted claim/entity revisions
  acceptance authority/decision
```

Current `BaselineRevision(u64)` can remain as a compatibility/order field during migration, but is insufficient as the mature identity.

## Product state is multi-axis

Do not encode one mutable "product status."

Keep distinguishable:
- accepted/intended;
- designed;
- implemented;
- built;
- released;
- deployed;
- observed.

Dissatisfaction can be a typed discrepancy between these axes.

## Evidence

An evidence observation binds at minimum:
- product;
- subject/entity/criterion;
- accepted baseline/contract;
- candidate artifact or deployment where applicable;
- target configuration/applicability;
- verifier identity/version/authority;
- observation time;
- result/value;
- provenance/raw artifact;
- evaluation/run identity.

Existing `Observation` lacks several of these and must not be considered mature merely because it has product + baseline.

## Suspect / invalidation

When an assertion endpoint, criterion, configuration dependency, verifier, or candidate changes:
1. preserve prior assertion/evidence against its original context;
2. determine dependent assertions/evidence whose applicability may no longer hold;
3. mark them suspect/stale/unknown as appropriate;
4. schedule/recommend revalidation;
5. restore accepted validity only through explicit compatible rule or new proof.

Physical edge existence does not imply semantic validity.

## ProductChange / GraphDelta

A graph edit is normally a proposal:

```text
ProductChange
  id
  base baseline/configuration
  motivation/finding
  proposed assertions/entities added/modified/retired
  impact set
  evidence invalidation set
  authorization
  external development/work references
  realization artifacts
  verification obligations
  reconciliation state
  resulting baseline/configuration if accepted
```

Proposal, realization, verification and acceptance are separate events.

## Current-type migration mapping

| Current | v0 interpretation |
|---|---|
| `ProductId` | retain concept; strengthen validation/alias semantics |
| `BaselineRevision(u64)` | compatibility/order field under richer BaselineId |
| `AcceptedIntent.id: String` | migrate toward stable EntityId + RevisionId |
| `AcceptedIntent.baseline` | baseline membership/reference |
| `Observation.product_id` | retain |
| `Observation.baseline` | richer baseline/config binding required |
| `Observation.capability_id: Option<String>` | replace with typed subject/entity reference |
| `ObservationSource.collector/version` | becomes verifier/producer identity but requires authority/admission |
| SWEE `NodeKind` | engineering-evidence projection; not whole product ontology |
| SWEE `EdgeKind` | engineering relation vocabulary; wrap/map into assertion semantics rather than extending indefinitely |

## Falsification cases before acceptance

1. same capability name in two products;
2. same entity across two revisions;
3. two product variants sharing most entities;
4. feature flag changes applicability;
5. evidence omits a required applicability dimension;
6. dependency/API version changes but implementation source does not;
7. baseline changes while artifact stays identical;
8. artifact changes while accepted contract stays identical;
9. canary and stable deployments coexist;
10. old evidence remains historically true but invalid for current target;
11. inferred edge has higher confidence than an accepted contradictory decision;
12. worker/development identity changes without product identity change;
13. one entity appears in UI, functional and verification projections;
14. relation becomes suspect without being deleted;
15. graph delta partially realizes and is abandoned.

If v0 cannot represent these without identity conflation or destructive history, revise it before schema migration.
