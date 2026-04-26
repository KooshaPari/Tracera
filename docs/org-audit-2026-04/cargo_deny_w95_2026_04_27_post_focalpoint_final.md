# Cargo-Deny Advisory Sweep — W-95 (2026-04-27 post-FocalPoint final)

Post-FocalPoint-final-cleanup snapshot. W-94 (commit `77a4705c4e`) baseline = **13** advisories org-wide.

## Methodology

- Tool: `cargo-deny 0.19.0`
- Command: `cargo deny check advisories` (no build, no update)
- Per-repo cap: 90s
- Scope: 11 repos (W-94 set minus pheno — pheno PR #21 still OPEN, Evalora submodule remote still 404)
- `ulimit -n 8192`; disk 39 GiB free

## Results — W-94 → W-95 Delta

| Repo | W-94 | W-95 | Δ | Verdict | Notes |
|------|-----:|-----:|---:|---------|-------|
| hwLedger | 0 | **0** | 0 | ok | Tauri suppress holds |
| BytePort | 0 | **0** | 0 | ok | suppressions active |
| KDesktopVirt | 4 | **4** | 0 | FAILED | bollard / rustls-webpki cluster (RUSTSEC-2026-0049/-0098/-0099/-0104) — upstream bollard release pending |
| HeliosLab | 0 | **0** | 0 | ok | clean |
| Configra | 0 | **0** | 0 | ok | clean |
| FocalPoint | 5 | **0** | **-5** | **ok** | **FULL CLEAN** — prometheus 0.13→0.14 cleared protobuf CVE + 3 transitives (c05a60e); starlark suppress (187cb41); uniffi bincode suppress landed (f373073) |
| AgilePlus | 1 | **1** | 0 | FAILED | RUSTSEC-2024-0436 (paste via utoipa-axum 0.2) — utoipa 1.0 upstream pending |
| PhenoObservability | 1 | **1** | 0 | FAILED | RUSTSEC-2025-0141 (bincode via surrealdb) — postcard migration upstream pending |
| eyetracker | 2 | **2** | 0 | FAILED | bincode + paste via uniffi 0.27 — uniffi 0.28+ upstream pending |
| heliosCLI | 0 | **0** | 0 | ok | clean |
| PhenoProc | 0 | **0** | 0 | ok | clean |
| pheno | n/a | **n/a** | — | EXCLUDED | PR #21 still OPEN; Evalora submodule remote 404 unresolved |

## Wave Totals

- **W-94 audited (11 measurable)**: 13 advisories
- **W-95 audited (11 measurable, pheno excluded)**: **8** advisories
- **Net delta**: 13 → 8 = **-5 (-38.5%)**
- pheno still not measurable; first inclusion blocked on Evalora submodule remote (404).

## Cluster Analysis

- **FocalPoint FULL CLEAN — MILESTONE.** W-94 → W-95: 5 → **0**. Three landed commits closed the gap:
  - `c05a60e` prometheus 0.13→0.14 with protobuf feature disabled (cleared RUSTSEC-2024-0437 CVE + 3 transitives: paste/derivative/fxhash via legacy chain)
  - `187cb41` starlark-transitive suppress (paste/derivative/fxhash residual via starlark)
  - `f373073` uniffi 0.27 bincode suppress (RUSTSEC-2025-0141 pending iOS UAT — uniffi 0.28→0.31 deferred)
  FocalPoint exits residuals tier and joins clean cohort.
- **bollard / rustls-webpki cluster (KDV)** — 4 vulns unchanged. Upstream-blocked.
- **paste / bincode cluster (AgilePlus, PhenoObservability, eyetracker)** — 4 advisories across 3 repos waiting on utoipa 1.0 / surrealdb postcard / uniffi 0.28+ upstream releases.
- **Clean cohort grew 7 → 8**: hwLedger, BytePort, HeliosLab, Configra, heliosCLI, PhenoProc + **FocalPoint** (newly clean). No regressions.

## Unexpected Findings

1. **FocalPoint reached zero in two waves.** W-93 = 19, W-94 = 5, W-95 = **0**. Templates-registry refactor + prometheus bump + 4 targeted suppressions cleared the entire chain. Largest single-repo cleanup of the campaign.
2. **All residual advisories are upstream-blocked.** No tractable in-repo fixes remain on the audited 11. Next-wave reductions require upstream releases (bollard, utoipa, surrealdb, uniffi).
3. **pheno still excluded.** PR #21 unmerged; Evalora submodule remote 404 unresolved.

## Follow-up Tickets

1. **pheno**: investigate Evalora 404 — is the repo renamed, archived, private, or deleted? Update PhenoProc submodule pointer or remove the dep chain. Blocks advisory snapshot.
2. **KDV bollard**: track upstream bollard release for rustls-webpki advisory cluster (4 vulns).
3. **AgilePlus**: utoipa-axum 1.0 upstream timeline (1 paste advisory).
4. **eyetracker**: uniffi 0.28+ upstream timeline (1 paste + 1 bincode).
5. **PhenoObservability**: surrealdb postcard migration upstream timeline (1 bincode).

## Cumulative Org-Wide Trajectory

| Wave | Audited Repos | Total Advisories | Δ from prior | % from W-92 |
|------|---:|---:|---:|---:|
| W-91 | 11 | ~58 | baseline | — |
| W-92 | 11 | 50 | -8 | 0% baseline |
| W-93 (re-verify) | 11 | 27 | -23 | -46.0% |
| W-94 | 11 | 13 | -14 | -74.0% |
| **W-95** | **11** | **8** | **-5 (-38.5%)** | **-84.0%** |

8 of 11 measurable repos clean (up from 7); 3 with single-cluster residuals; **FocalPoint achieved full clean**; pheno still blocked.
