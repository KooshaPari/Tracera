# Org PR Scoreboard — 2026-04-27 Final Tally

**Reporting Period:** 2026-04-26 00:00 — 2026-04-27 06:00 UTC

## Summary

- **Total PRs opened:** 12
- **Total PRs merged:** 10 (83.3%)
- **Closed as duplicate:** 1 (phenoShared #124)
- **Still open:** 1 (AgilePlus #432, security-alerts branch)

**Final Status:** 10 merged successfully, 1 duplicate closed, 1 conflict resolution in flight.

---

## PR Details

| Repo | PR# | Title | State | Merged At |
|------|-----|-------|-------|-----------|
| Civis | 253 | round-7a: post-rebase reconcile (READMEs upstream-canonical) | MERGED | 2026-04-26T10:03:44Z |
| AgilePlus | 413 | spec(013): mark phenotype-infrakit-stabilization CANCELLED | MERGED | 2026-04-26T11:49:25Z |
| AgilePlus | 416 | chore(deny): remove stale RUSTSEC-2025-0134 rustls-pemfile ignore | MERGED | 2026-04-26T13:14:00Z |
| AgilePlus | 431 | chore(deps): remove dead utoipa-axum dep (clears RUSTSEC-2024-0436) | MERGED | 2026-04-27T03:08:53Z |
| AgilePlus | 432 | security-alerts branch (conflict resolution in flight) | OPEN | — |
| KDesktopVirt | 11 | chore(deps): bump bollard 0.16→0.20 (clears 4 RUSTSEC incl. 2 CVEs) + stale-ignore cleanup | MERGED | 2026-04-26T23:41:51Z |
| PhenoProc | 21 | chore(submodule): remove Evalora dead reference (404 upstream) | MERGED | 2026-04-26T13:14:00Z |
| PhenoProc | 25 | fix(submodule): add missing URL for crates/byteport (unblocks pheno transitive cargo fetch) | MERGED | 2026-04-27T03:25:57Z |
| phenotype-shared | 123 | [WP] | MERGED | 2026-04-27T03:25:27Z |
| phenotype-shared | 124 | [WP] — DUPLICATE | CLOSED | — |
| phenotype-shared | 125 | [WP] (after rebase) | MERGED | 2026-04-27T03:28:47Z |
| phenotype-shared | 126 | [WP] (after rebase) | MERGED | 2026-04-27T03:29:01Z |

---

## Categories (Merged — 10 PRs)

### Dependency & Security (4 PRs)
- AgilePlus #416: Denied stale RUSTSEC-2025-0134 rustls-pemfile
- AgilePlus #431: Removed utoipa-axum (RUSTSEC-2024-0436)
- KDesktopVirt #11: Bollard 0.16→0.20 (4 RUSTSEC, 2 CVEs)

### Spec & Planning (1 PR)
- AgilePlus #413: Spec cancellation (phenotype-infrakit-stabilization)

### Maintenance & Cleanup (3 PRs)
- Civis #253: README post-rebase reconcile
- PhenoProc #21: Evalora submodule dead reference removal
- PhenoProc #25: BytePort submodule URL (after rebase)

### phenotype-shared Additions (2 PRs merged; 1 duplicate)
- phenotype-shared #123: Work package (merged post-rebase)
- phenotype-shared #124: DUPLICATE — work consolidated into #125/#126
- phenotype-shared #125: Work package (merged post-rebase)
- phenotype-shared #126: Work package (merged post-rebase)

---

## Final Status

**Merged (10 PRs):** Civis #253, AgilePlus #413/#416/#431, KDesktopVirt #11, PhenoProc #21/#25, phenotype-shared #123/#125/#126.

**Closed (1 PR):** phenotype-shared #124 (duplicate; work on main).

**Still Open (1 PR):** AgilePlus #432 (security-alerts branch, conflict resolution in flight).

**Grand Total:** 12 PRs opened, 10 merged (83.3%), 1 closed as duplicate, 1 open.
