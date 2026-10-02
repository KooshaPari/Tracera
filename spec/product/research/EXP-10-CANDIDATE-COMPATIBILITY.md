# EXP-10 — Compatibility certificates and candidate equivalence

**Status:** architecture experiment specification; not production policy.

## Problem

EXP-08/09 showed typed applicability can avoid large amounts of needless re-verification, but the strongest reuse model depended on assumed-valid compatibility certificates.

That assumption is unsafe.

Separately, a product candidate is not identified by source commit alone.

## Candidate identity

For verification purposes, a candidate may depend on:
- source revision(s);
- generated source/assets;
- dependency lock/resolution;
- compiler/build toolchain;
- build configuration;
- schema/migration revision;
- feature/configuration values;
- immutable artifact digest(s);
- external API/service contract versions where the criterion depends on them.

A criterion declares its **dependency footprint**: which candidate dimensions can affect the behavior it measures.

Two candidates may reuse evidence only if every dependency in that criterion's footprint is either:
1. identical;
2. explicitly irrelevant for that criterion; or
3. covered by an admitted compatibility certificate.

"Same Git commit" is never sufficient by itself unless the criterion's dependency footprint proves all other dimensions irrelevant.

## CompatibilityCertificate

Candidate fields:

```text
CertificateId
issuer / authority
issued_at
validity interval
source domain/value
target domain/value
covered criterion IDs/revisions
covered operation/surface set
configuration constraints
direction
transitive = false by default
evidence/provenance supporting certificate
revocation state
supersedes?
```

### Default rules

- compatibility is directional;
- transitivity is OFF unless explicitly proven;
- a certificate applies only to declared criterion revisions and operations;
- omitted scope is not wildcard;
- expired/revoked certificate cannot authorize new reuse;
- certificate evidence remains historically queryable;
- a certificate cannot certify itself;
- worker assertion alone is not certificate authority;
- criterion revision invalidates reuse unless compatibility to the new criterion is explicit.

## Adversarial cases

1. API 12→13 certificate covers GET /users; reuse for POST /payments must fail.
2. API 12→13 and 13→14 exist; 12→14 must remain UNKNOWN unless composition is explicitly authorized/proven.
3. DB 18→19 certificate is directional; evidence from 19 cannot automatically validate 18.
4. certificate expired after historical evidence was recorded; history remains valid, new reuse fails.
5. certificate revoked; new reuse fails and dependents become suspect.
6. criterion v1 certificate cannot validate criterion v2.
7. same source commit, dependency lock changed; dependency-sensitive criterion must recheck.
8. same source commit, build toolchain changed; binary/runtime-sensitive criterion must recheck.
9. same source and lock, feature flag changed; flag-sensitive criterion must recheck.
10. different artifact digest but changed files are outside criterion dependency footprint; reuse may be allowed only through explicit dependency/impact proof.
11. certificate issuer is unadmitted; reuse fails.
12. certificate scope omits environment; environment-sensitive criterion remains UNKNOWN.

## Comparison models

A. source-commit equality;
B. full candidate equality;
C. criterion dependency-footprint equality;
D. footprint equality + admitted scoped certificates.

Measure:
- false reuse;
- safe reuse;
- forced rechecks;
- unknowns;
- certificate count/maintenance;
- invalidation fanout.

## Gate

Do not promote compatibility certificates into the accepted ontology until mutation controls demonstrate that operation scope, direction, criterion revision, authority, expiration/revocation and non-transitivity are independently enforced.
