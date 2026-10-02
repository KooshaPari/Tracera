# EXP-08 executable checkpoint — applicability semantics

**Date:** 2026-09-29  
**Status:** research checkpoint; NOT Tracera runtime proof.

A minimal executable reference check was run against the restricted effectivity semantics in `EXP-08-EVIDENCE-SUBSUMPTION.md`.

## Cases exercised

| Case | Expected | Result |
|---|---|---|
| Chromium version range covers target | PROVEN_APPLICABLE | pass |
| Feature-flag value differs | PROVEN_NOT_APPLICABLE | pass |
| Required dimension omitted | UNKNOWN | pass |
| Compatibility certificate required but absent | UNKNOWN | pass |
| Declared compatibility certificate available | PROVEN_APPLICABLE | pass |
| Evidence explicitly stale | STALE | pass |

## Interpretation

The four-state relation is coherent for these seed cases:
- `PROVEN_APPLICABLE`
- `PROVEN_NOT_APPLICABLE`
- `UNKNOWN`
- `STALE`

This does **not** establish:
- safe candidate-artifact equivalence;
- criterion-version compatibility;
- dependency transitivity;
- certificate authority/admission;
- operation-scoped certificates;
- compound/disjunctive applicability;
- realistic safe-reuse economics;
- Tracera implementation compliance.

## Next experiment

Construct a realistic software configuration matrix and compare:
A. exact-match-only;
B. typed subsumption;
C. typed subsumption + explicit compatibility certificates.

Measure:
- true safe reuse;
- false reuse;
- forced rechecks;
- unknowns;
- compatibility decisions/certificates required.

Do not generalize the effectivity language before that experiment.
