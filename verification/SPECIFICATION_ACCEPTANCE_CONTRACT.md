# Tracera Specification Acceptance Contract

**Status:** canonical non-runtime acceptance contract  
**Date:** 2026-10-01

This contract grades the **specification system itself**. It does not grade product implementation.

## Required objects

A specification baseline is eligible for acceptance only when it contains:
1. a canonical mature-contract manifest;
2. stable atomic requirement identities;
3. source/provenance bindings;
4. mature-domain coverage disposition;
5. semantic stage projections;
6. actor-to-outcome journeys;
7. requirement↔journey bindings;
8. concrete verification-case definitions;
9. trace expectations;
10. explicit unresolved decisions/blockers;
11. supersession/history metadata.

## Atomic requirement quality

Each requirement must state:
- one normative obligation;
- subject/actor;
- observable behavior or invariant;
- applicability/effectivity;
- failure semantics where material;
- provenance;
- stage applicability;
- verification intent.

A requirement fails specification acceptance if it is:
- generic filler produced from a template dimension;
- a compound bundle whose independent failure modes cannot be graded;
- implementation-only detail with no product obligation;
- an aspiration with no observable consequence;
- a duplicate under different wording;
- stage membership assigned by position/count;
- supported only by another generated requirement.

## Oracle readiness

A requirement is **oracle-ready** only when at least one verification case defines:
- exact requirement revision;
- preconditions;
- fixture/input;
- action/stimulus;
- expected observable;
- negative/counterexample;
- isolation/reset assumptions;
- evidence/receipt expected from execution;
- allowed explicit non-pass states.

Reserved test IDs or prose such as "verify this works" are not oracle readiness.

## Mandatory adversarial families

Where applicable, the verification catalogue must include:
- empty denominator / zero applicable checks;
- wrong product/baseline/candidate/configuration;
- stale evidence;
- conflicting evidence;
- missing collector;
- unauthorized mutation;
- invalid type/relation;
- partial/progressive graph data;
- budget exhaustion/continuation;
- dependency uncertainty;
- certificate/reuse revocation;
- historical evidence retained while current applicability changes;
- work Done without product proof;
- product proof without work-state authority;
- transport disagreement;
- migration/restart/history preservation;
- optional dependency unavailable;
- superseded requirement/evidence;
- duplicate/replayed ingestion;
- concurrent/conflicting change proposal.

## Journey acceptance

A journey is specification-ready only when it defines:
- actor;
- preconditions;
- exact starting state;
- ordered/branching actions;
- expected intermediate invariants;
- terminal outcome;
- failure/recovery path;
- bound requirements;
- oracle cases;
- stage applicability.

A journey cannot be closed by file/route presence.

## Stage acceptance

A stage projection is valid only when:
- membership is justified by required outcomes/dependencies;
- all required journeys are named;
- all required requirements are transitively bound;
- excluded mature obligations remain represented in the mature contract;
- empty projection is NotAssessable, never achieved;
- no fixed percentage/count determines membership.

## Trace completeness

Trace completeness is graded separately from behavior.

Required link classes:
```text
source → requirement
requirement ↔ journey
requirement → verification case
requirement → intended implementation surface (when known)
verification case → evidence contract
stage → journey/requirement projection
decision → affected requirement/domain
historical capability → disposition/current requirement
```

Missing implementation/evidence links before implementation exists are explicit `UNREALIZED`, not specification failure if the specification link expectation is defined.

## Acceptance statuses

- **AcceptedSpec** — all mandatory specification checks satisfied.
- **UnsatisfiedSpec** — concrete specification defect exists.
- **InconclusiveSpec** — conflicting authority/source prevents resolution.
- **IncompleteSpec** — required semantic decomposition/oracle work remains.
- **NotApplicable** — check is explicitly inapplicable with rationale.

There is no vacuous success.

## Final gate

A mature Tracera specification cannot be called final while any mature-domain row is PARTIAL/UNDERDECOMPOSED, any mandatory journey lacks oracle bindings, or the canonical contract manifest remains invalidated.
