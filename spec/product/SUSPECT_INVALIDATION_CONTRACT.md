# Tracera Suspect / Invalidation Semantic Contract

**Status:** proposed architecture contract derived from EXP-08..11.  
**Date:** 2026-09-30.

## Core distinction

Historical truth and current applicability are separate.

An observation/assertion can remain true about its original candidate/configuration while no longer proving the current target.

Never implement invalidation by deleting history.

## Semantic states

- `CURRENT_VALID` — admitted proof/assertion applies to current target.
- `SUSPECT` — a dependency changed and applicability has not been re-established.
- `STALE` — freshness/effectivity policy expired.
- `INVALID_FOR_TARGET` — proven mismatch with target.
- `UNKNOWN` — insufficient information to establish applicability.
- `SUPERSEDED` — replaced as current accepted meaning, retained historically.
- `HISTORICAL_VALID` — valid for its original context, not current proof.

These are semantic applicability states, not necessarily one persisted enum for every object.

## Trigger classes

- entity/revision change;
- accepted baseline or criterion revision;
- candidate artifact/dependency change;
- configuration/effectivity change;
- dependency-footprint change;
- verifier identity/version/authority change;
- compatibility-certificate expiry/revocation;
- source-system correction;
- accepted ProductChange.

## Dependency rule

A current reuse decision is justified by explicit dependency/applicability edges.

If a dependency changes:
1. locate criteria/reuse decisions whose admitted footprint includes it;
2. mark current applicability SUSPECT unless explicit compatibility discharges the change;
3. propagate through typed dependent edges under a budget;
4. preserve old proof as HISTORICAL_VALID for original context;
5. create new current proof/reuse decision after revalidation.

Missing/inferred absence cannot suppress invalidation.

## Compatibility-certificate revocation

Revocation affects reuse decisions justified by the certificate.

Maintain explicit edges:

```text
Certificate
  → justifies
ReuseDecision
  → applies
Evidence
  → target
Candidate/Configuration/Criterion
```

Revoking the certificate:
- marks dependent reuse decisions SUSPECT/INVALID_FOR_TARGET;
- propagates to assessments using those decisions;
- does not delete the certificate;
- does not delete the original observation;
- does not rewrite the historical assessment that was valid under the then-admitted policy.

## Traversal budget

Invalidation traversal must be bounded.

Budget exhaustion returns PARTIAL/UNKNOWN with a continuation/frontier.

It must never mean "no more affected nodes."

## Revalidation

Revalidation appends new proof.

It may restore CURRENT_VALID.

It must not mutate the old evidence into a new candidate/configuration identity.

## Negative controls

1. unrelated dependency change does not invalidate;
2. direct admitted dependency change does;
3. inferred false positive may over-invalidate;
4. inferred/missing false negative cannot authorize reuse;
5. certificate scope applies only to declared criterion/operation/configuration;
6. certificate revocation invalidates dependent reuse decisions;
7. expiry leaves historical evidence queryable;
8. physical relation remains while semantic status becomes suspect;
9. new proof restores current validity without deleting old proof;
10. traversal budget exhaustion cannot produce complete/green.

## MACE interpretation

Invalidation can reduce current verified position or increase uncertainty while preserving historical achievement.

A progress chart must distinguish:
- regression in product behavior;
- loss of evidence applicability;
- grader/scope change;
- historical best.

Do not flatten these into one decreasing percentage.

## Persistence implication

The vertical slice needs durable identity for:
- dependency/assertion;
- evidence;
- applicability/reuse decision;
- invalidation event/reason;
- certificate where used;
- assessment/evaluation.

This does not require the entire mature ontology before VS-01, but the repository contract must not make historical preservation impossible.
