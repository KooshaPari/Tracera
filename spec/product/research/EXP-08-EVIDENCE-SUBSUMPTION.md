# Tracera configuration/effectivity and evidence-reuse experiment

**Status:** design experiment specification; product tests deferred.

## Objective

Find the smallest safe applicability model that permits useful evidence reuse across product configurations without false green.

## Principle

Evidence reuse is a proof obligation.

```text
evidence applies to E
target requires T

reuse is allowed only if:
  E is proven to cover T
  AND candidate/criterion/verifier dependencies remain compatible
```

Missing applicability dimensions are Unknown, not wildcard.

## Typed dimensions for first experiment

Use only:
- platform: enum;
- browser_family: enum;
- browser_version: ordered semver-like integer;
- feature_flag: exact bool;
- api_schema: exact or explicit compatibility certificate;
- db_schema: exact or explicit compatibility certificate;
- dependency_version: exact/range with explicit compatibility rule;
- environment_class: enum;
- region: set;
- time interval.

Do not start with arbitrary Boolean expressions.

## Applicability predicates

V0 experiment supports:
- exact(value)
- one_of(set)
- range(min,max)
- interval(start,end)
- any() — only when the criterion explicitly declares the dimension irrelevant
- compatible_via(certificate_id)

An omitted dimension means Unknown.

## Safe examples

### Range subsumes target
Evidence:
`browser_family=chromium AND browser_version=[138,145]`

Target:
`chromium/141`

Expected: applicable.

### Explicit irrelevance
Criterion declares region irrelevant and evidence applicability contains `region=any()`.

Target:
EU.

Expected: applicable for region dimension.

### Certified compatibility
Evidence:
`api_schema=12`

Target:
`api_schema=13`

Certificate:
`schema-12-to-13-backward-compatible`, valid for the tested operation set.

Expected: applicable only for operations covered by the certificate.

## Unsafe/unknown examples

1. evidence has `feature_flag=false`; target=true → NOT_APPLICABLE.
2. evidence omits feature_flag; target=true → UNKNOWN, not applicable.
3. evidence chromium 138–145; target Firefox 142 → NOT_APPLICABLE.
4. evidence db_schema=18; target=19 with no certificate → UNKNOWN.
5. evidence expired valid-time interval → STALE/NOT_APPLICABLE according to criterion policy.
6. same configuration but different criterion revision → UNKNOWN until criterion compatibility is proven.
7. same criterion/configuration but different candidate artifact → no reuse unless artifact-equivalence/dependency rule proves the relevant behavior unchanged.
8. same source commit but changed external API/dependency → no automatic reuse.
9. same artifact but verifier version changed → historical evidence retained; comparison/reuse follows verifier compatibility policy.
10. omitted environment class → UNKNOWN.

## Subsumption relation

Return one of:
- PROVEN_APPLICABLE
- PROVEN_NOT_APPLICABLE
- UNKNOWN
- STALE

Never coerce UNKNOWN to true.

For conjunctive dimensions, all required dimensions must be PROVEN_APPLICABLE; any proven mismatch makes NOT_APPLICABLE; otherwise UNKNOWN/STALE propagates.

## Counterexample objective

The experiment must deliberately attempt to produce false green by:
- deleting each dimension guard;
- treating missing as wildcard;
- using source-commit equality as candidate equivalence;
- accepting a compatibility certificate outside its declared operation set;
- reusing evidence after criterion revision;
- reusing stale evidence.

Each mutation must be caught by the oracle suite.

## Cost objective

Overly strict matching can make Tracera economically useless. Measure:
- safe reuse rate;
- forced recheck rate;
- false reuse;
- unknown rate;
- human compatibility decisions required.

Compare:
A. exact-match-only;
B. typed subsumption;
C. typed subsumption + explicit compatibility certificates.

The goal is not maximum reuse. It is the best safe reuse/maintenance tradeoff.

## PLM import

PLM effectivity demonstrates conditional inclusion of structure relationships based on scoped variables and criteria. Tracera adapts that principle to software configurations rather than copying manufacturing-specific variables/processes.

## Gate

Do not add general-purpose effectivity syntax to the production schema until this experiment demonstrates that the restricted model cannot express ordinary software cases.
