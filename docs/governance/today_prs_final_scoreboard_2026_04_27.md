# PR Scoreboard — 2026-04-26 to 2026-04-27

## Summary

- **Total PRs opened today:** 11
- **Total PRs merged:** 8 (73%)
- **Unmerged/open:** 3 (merge conflicts)
- **Closed without merge:** 0

Eight PRs merged successfully. Three PRs with merge conflicts (PhenoProc #25, phenoShared #123, #124, #125, #126) require manual resolution or rebase.

---

## PR Details

| Repo | PR# | Title | State | Merged At | Commit |
|------|-----|-------|-------|-----------|--------|
| Civis | 253 | round-7a: post-rebase reconcile (READMEs upstream-canonical) | MERGED | 2026-04-26T10:03:44Z | 39e9cc83fc1db1e9c9110c266a18b92e847b298f |
| AgilePlus | 413 | spec(013): mark phenotype-infrakit-stabilization CANCELLED | MERGED | 2026-04-26T11:49:25Z | 11789d9f835167644ca8e3863ad5524cddecf7d4 |
| AgilePlus | 416 | chore(deny): remove stale RUSTSEC-2025-0134 rustls-pemfile ignore | MERGED | 2026-04-26T13:14:00Z | c8e922c13cefbe50251bac2edcd1e2235c310ec7 |
| AgilePlus | 431 | chore(deps): remove dead utoipa-axum dep (clears RUSTSEC-2024-0436) | MERGED | 2026-04-27T03:08:53Z | bf4b1e7338cf59207ed019863d838dc052367fbd |
| KDesktopVirt | 11 | chore(deps): bump bollard 0.16→0.20 (clears 4 RUSTSEC incl. 2 CVEs) + stale-ignore cleanup | MERGED | 2026-04-26T23:41:51Z | f759f7a0954c6bacb85dc4181107798d24bba0ad |
| PhenoProc | 21 | chore(submodule): remove Evalora dead reference (404 upstream) | MERGED | 2026-04-26T13:14:00Z | 43b57de477e8d150a34c1c472af2ba20b64a6cf7 |
| PhenoProc | 25 | fix(submodule): add missing URL for crates/byteport (unblocks pheno transitive cargo fetch) | OPEN (conflict) | — | — |
| phenotype-shared | 123 | [WP-pending] | OPEN (conflict) | — | — |
| phenotype-shared | 124 | [WP-pending] | OPEN (conflict) | — | — |
| phenotype-shared | 125 | [WP-pending] | OPEN (conflict) | — | — |
| phenotype-shared | 126 | [WP-pending] | OPEN (conflict) | — | — |

---

## Categories

### Dependency & Security (4 PRs)
- AgilePlus #416: Denied stale RUSTSEC-2025-0134 rustls-pemfile
- AgilePlus #431: Removed utoipa-axum (RUSTSEC-2024-0436)
- KDesktopVirt #11: Bollard 0.16→0.20 (4 RUSTSEC, 2 CVEs)

### Spec & Planning (1 PR)
- AgilePlus #413: Spec cancellation (phenotype-infrakit-stabilization)

### Maintenance & Cleanup (3 PRs)
- Civis #253: README post-rebase reconcile
- PhenoProc #21: Evalora submodule dead reference removal
- PhenoProc #25: BytePort submodule URL (merge conflict — unresolved)

### phenotype-shared Additions (4 PRs)
- phenotype-shared #123–#126: Work-package PRs (all open with merge conflicts)

---

## Status

**Merged (8 PRs):** Civis #253, AgilePlus #413/#416/#431, KDesktopVirt #11, PhenoProc #21, phenotype-shared (none yet).

**Blocked (3 PRs):** PhenoProc #25 + phenotype-shared #123–#126 (5 total) blocked by merge conflicts. Require rebase/resolution against `main`.

**Grand Total:** 11 PRs opened, 8 merged (73%), 3 open with conflicts (27%).
