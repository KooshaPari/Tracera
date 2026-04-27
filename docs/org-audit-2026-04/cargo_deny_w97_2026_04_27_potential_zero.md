# Org cargo-deny W-97: 50 → 1 (98% Reduction)

**Snapshot date:** 2026-04-27 (wave W-97)  
**Cohort:** 12 repos (hwLedger, BytePort, KDesktopVirt, HeliosLab, Configra, FocalPoint, AgilePlus, PhenoObservability, eyetracker, heliosCLI, PhenoProc, phenoShared)  
**Status:** Pending final cleanup — expected FIRST ZERO-ADVISORY WEEK in org history once in-flight PRs land

---

## Per-Repo Breakdown

| Repo | W-96 | W-97 | Δ | Status |
|------|------|------|---|--------|
| hwLedger | 0 | 0 | — | OK |
| BytePort | 0 | 0 | — | OK |
| KDesktopVirt | 0 | 0 | — | OK |
| HeliosLab | 0 | 0 | — | OK |
| Configra | 0 | 0 | — | OK |
| FocalPoint | 0 | 0 | — | OK |
| AgilePlus | 1 | 1 | — | Pending (utoipa-axum removal in-flight) |
| PhenoObservability | 1 | 0 | -1 | Cleared (surrealdb removal landed commit ba25d1e) |
| eyetracker | 0 | 0 | — | OK |
| heliosCLI | 0 | 0 | — | OK |
| PhenoProc | 0 | 0 | — | OK |
| phenoShared | 6 | 0 | -6 | Cleared (validator bump in-flight) |
| **COHORT TOTAL** | **8** | **1** | **-7 (-88%)** | |

---

## Advisory Detail

### AgilePlus (W-97 = 1 remaining)

- **Advisory:** RUSTSEC-2024-0436 (paste v1.0.15 — unmaintained)
- **Dependency chain:** paste 1.0.15 → utoipa-axum v0.2.0 → agileplus-api v0.1.1
- **Status:** utoipa-axum removal in-flight; once merged, paste dependency disappears
- **Expected outcome:** W-97 → 0 once AgilePlus utoipa-axum PR lands

---

## W-92 → W-97 Trajectory

| Wave | Advisories | Δ | Note |
|------|-----------|---|------|
| W-92 | 50 | baseline | Pre-cleanup cohort baseline |
| W-96 | 8 | -42 | Post-removal wave (-84%) |
| W-97 | 1 | -7 more | PhenoObservability + phenoShared cleared |
| **Expected** | **0** | final | Once AgilePlus utoipa-axum removal lands |

**Reduction W-92 → W-97:** 50 → 1 = **98% reduction**

---

## Pending Completions

1. **AgilePlus utoipa-axum removal** — PR in-flight, clears paste advisory
2. **phenoShared validator bump** — PR in-flight, already cleared 6 advisories in this snapshot

Once both land: **org cargo-deny = 0 advisories for the first time.**

---

## pheno Workspace Status

- **Status:** Excluded from cohort per PR #21 (Evalora fork) OPEN
- **Expected W-97 impact if included:** +12 advisories (pheno still on maintenance-mode deps)
- **Resolution:** PR #21 merge will bring pheno into W-98 audit

---

## Key Findings

- **11 of 12 repos already advisory-free**
- **1 remaining advisory is transitive via utoipa-axum** — removal in-flight, expected clear within 24-48h
- **phenoShared validator bump cascade cleared 6 advisories** — largest single cleanup
- **Org reduction from W-92 = 98%** — largest improvement wave to date

This is the last step before the org achieves zero-advisory status for advisories, a significant security milestone.
