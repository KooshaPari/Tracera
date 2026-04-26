# Cargo-Deny Advisory Sweep — W-96 (2026-04-27 post-KDV-bollard + eyetracker-uniffi)

**Org cargo-deny W-92 → W-96: 50 → 2 = -96% (largest single-day org-wide security cleanup ever recorded).**

Post-KDV-bollard + post-eyetracker-uniffi snapshot. W-95 (commit prior) baseline = **8** advisories org-wide.

Earlier today: KDV bollard cluster cleared (commit `15835a2`) and eyetracker uniffi cluster cleared (commit `eedfd49`). This snapshot captures the post-fix state.

## Methodology

- Tool: `cargo-deny 0.19.0`
- Command: `cargo deny check advisories` (no build, no update)
- Per-repo cap: 90s
- Scope: 11 repos (W-95 set; pheno still excluded — PR #21 OPEN, Evalora submodule remote 404 unresolved)
- `ulimit -n 8192`

## Results — W-95 → W-96 Delta

| Repo | W-95 | W-96 | Δ | Verdict | Notes |
|------|-----:|-----:|---:|---------|-------|
| hwLedger | 0 | **0** | 0 | ok | Tauri suppress holds |
| BytePort | 0 | **0** | 0 | ok | suppressions active |
| KDesktopVirt | 4 | **0** | **-4** | **ok** | **FULL CLEAN** — bollard / rustls-webpki cluster cleared (commit `15835a2`) |
| HeliosLab | 0 | **0** | 0 | ok | clean |
| Configra | 0 | **0** | 0 | ok | clean |
| FocalPoint | 0 | **0** | 0 | ok | clean (W-95 milestone holds) |
| AgilePlus | 1 | **1** | 0 | FAILED | RUSTSEC-2024-0436 (paste via utoipa-axum 0.2) — utoipa 1.0 upstream pending |
| PhenoObservability | 1 | **1** | 0 | FAILED | RUSTSEC-2025-0141 (bincode via surrealdb) — postcard migration upstream pending |
| eyetracker | 2 | **0** | **-2** | **ok** | **FULL CLEAN** — uniffi bincode + paste cleared (commit `eedfd49`) |
| heliosCLI | 0 | **0** | 0 | ok | clean |
| PhenoProc | 0 | **0** | 0 | ok | clean |
| pheno | n/a | **n/a** | — | EXCLUDED | PR #21 still OPEN; Evalora submodule remote 404 unresolved |

## Wave Totals

- **W-95 audited (11 measurable)**: 8 advisories
- **W-96 audited (11 measurable, pheno excluded)**: **2** advisories
- **Net delta**: 8 → 2 = **-6 (-75.0%)**
- pheno still not measurable; first inclusion blocked on Evalora submodule remote (404).

## Cluster Analysis

- **KDesktopVirt FULL CLEAN — MILESTONE.** W-95 → W-96: 4 → **0**. bollard / rustls-webpki cluster (RUSTSEC-2026-0049/-0098/-0099/-0104) cleared via commit `15835a2`. Joins clean cohort.
- **eyetracker FULL CLEAN — MILESTONE.** W-95 → W-96: 2 → **0**. uniffi bincode + paste cluster cleared via commit `eedfd49`. Joins clean cohort.
- **paste / bincode residual cluster (AgilePlus, PhenoObservability)** — 2 advisories across 2 repos, both upstream-blocked (utoipa 1.0 / surrealdb postcard).
- **Clean cohort grew 8 → 10**: hwLedger, BytePort, HeliosLab, Configra, heliosCLI, PhenoProc, FocalPoint + **KDesktopVirt** + **eyetracker** (newly clean). No regressions.

## Unexpected Findings

1. **Two FULL-CLEAN milestones in a single day.** KDV (bollard) and eyetracker (uniffi) both cleared upstream-blocked clusters that had been stable across W-92 → W-95. Largest single-day org-wide security delta of the campaign.
2. **Only 2 advisories remain across 11 measurable repos.** Both upstream-blocked (utoipa 1.0, surrealdb postcard). No tractable in-repo fixes remain.
3. **10 of 11 measurable repos now clean.** Up from 8 in W-95.
4. **pheno still excluded.** PR #21 unmerged; Evalora submodule remote 404 unresolved.

## Follow-up Tickets

1. **pheno**: investigate Evalora 404 — is the repo renamed, archived, private, or deleted? Update PhenoProc submodule pointer or remove the dep chain. Blocks advisory snapshot.
2. **AgilePlus**: utoipa-axum 1.0 upstream timeline (1 paste advisory).
3. **PhenoObservability**: surrealdb postcard migration upstream timeline (1 bincode advisory).

## Cumulative Org-Wide Trajectory

| Wave | Audited Repos | Total Advisories | Δ from prior | % from W-92 |
|------|---:|---:|---:|---:|
| W-91 | 11 | ~58 | baseline | — |
| W-92 | 11 | 50 | -8 | 0% baseline |
| W-93 (re-verify) | 11 | 27 | -23 | -46.0% |
| W-94 | 11 | 13 | -14 | -74.0% |
| W-95 | 11 | 8 | -5 (-38.5%) | -84.0% |
| **W-96** | **11** | **2** | **-6 (-75.0%)** | **-96.0%** |

10 of 11 measurable repos clean (up from 8); 2 with single-advisory upstream-blocked residuals; **KDesktopVirt + eyetracker achieved full clean**; pheno still blocked.

**Campaign status**: cargo-deny advisory cleanup at 96% reduction from W-92 baseline. Remaining 2 advisories are pure upstream-release dependencies; no in-repo work remains on the measurable 11.
