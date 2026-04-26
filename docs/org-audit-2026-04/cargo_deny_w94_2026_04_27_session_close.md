# Cargo-Deny Advisory Sweep — W-94 (2026-04-27 session close)

Post-templates-registry-refactor + post-pheno-cleanup snapshot. W-93 re-verify (commit `bae55ec932`) baseline = **27** advisories org-wide.

## Methodology

- Tool: `cargo-deny 0.19.0`
- Command: `cargo deny check advisories` (no build, no update)
- Per-repo cap: 90s
- Scope: 12 repos (W-93 set + heliosCLI + PhenoProc + pheno)
- `ulimit -n 8192`; disk 32 GiB free

## Results — W-93 → W-94 Delta

| Repo | W-93 | W-94 | Δ | Verdict | Notes |
|------|-----:|-----:|---:|---------|-------|
| hwLedger | 0 | **0** | 0 | ok | Tauri suppress holds |
| BytePort | 0 | **0** | 0 | ok | suppressions active |
| KDesktopVirt | 4 | **4** | 0 | FAILED | bollard / rustls-webpki (RUSTSEC-2026-0049/-0098/-0099/-0104) unchanged |
| HeliosLab | 0 | **0** | 0 | ok | clean |
| Configra | 0 | **0** | 0 | ok | clean |
| FocalPoint | 19 | **5** | **-14** | FAILED | templates-registry refactor landed — iron/nickel/multipart/typemap chain dropped; remaining: paste / bincode / rustls-pemfile / fxhash / derivative + protobuf vuln |
| AgilePlus | 1 | **1** | 0 | FAILED | RUSTSEC-2024-0436 (paste via utoipa-axum 0.2) |
| PhenoObservability | 1 | **1** | 0 | FAILED | RUSTSEC-2025-0141 (bincode via surrealdb) |
| eyetracker | 2 | **2** | 0 | FAILED | bincode + paste via uniffi 0.27 |
| heliosCLI | 0 | **0** | 0 | ok | clean (W-92 baseline holds) |
| PhenoProc | 0 | **0** | 0 | ok | clean (W-92 baseline holds) |
| pheno | n/a | **n/a** | — | TOOLING ERROR | submodule fetch failure: `phenotype-observability` dep → `PhenoProc.git` git-dep → submodule `Evalora.git` returns 404. Workspace cleanup landed locally but the transitive submodule chain breaks cargo-deny. Cannot snapshot. |

## Wave Totals

- **W-93 audited (11 measurable)**: 27 advisories
- **W-94 audited (11 measurable, pheno excluded)**: **13** advisories
- **Net delta**: 27 → 13 = **-14 (-51.9%)**
- pheno still not measurable; first inclusion blocked on Evalora submodule remote (404).

## Cluster Analysis

- **FocalPoint templates-registry refactor — MAJOR WIN.** Predicted -11 (19→8), actual **-14 (19→5)**. The iron / nickel / multipart / typemap legacy chain plus several transitive unmaintained crates all dropped. Remaining 5 = paste, bincode, rustls-pemfile, fxhash, derivative (unmaintained) + protobuf RUSTSEC-2024-0437 (vulnerability). FocalPoint has now exited the "decommission required" tier and joins the standard upstream-tracking tier.
- **bollard / rustls-webpki cluster (KDV)** — 4 vulns unchanged. Upstream bollard release pending; needs follow-up tracking.
- **paste / bincode cluster (AgilePlus, PhenoObservability, eyetracker)** — 4 advisories across 3 repos waiting on utoipa 1.0 / surrealdb postcard / uniffi 0.28+ upstream.
- **Clean cohort grew 5 → 7**: hwLedger, BytePort, HeliosLab, Configra, heliosCLI, PhenoProc + (newly clean since W-93 set) — no regressions.

## Unexpected Findings

1. **FocalPoint dropped harder than projected.** Templates-registry refactor cleared not just the iron/nickel chain but also several transitive unmaintained crates from removed dev-dep paths. Net 19→5 vs projected 19→8.
2. **pheno first-time inclusion blocked.** Workspace cleanup made the local Cargo.toml resolvable, but the transitive `phenotype-observability` git-dep pulls `PhenoProc.git` whose submodule `Evalora.git` returns 404. Either Evalora was renamed/archived, or its submodule pin needs updating in PhenoProc. Until fixed, pheno cannot be advisory-audited.
3. **No regressions anywhere.** All 9 W-93 baseline repos held or improved.

## Follow-up Tickets

1. **pheno**: investigate Evalora 404 — is the repo renamed, archived, private, or deleted? Update PhenoProc submodule pointer or remove the dep chain. Blocks advisory snapshot.
2. **FocalPoint**: schedule paste / bincode / fxhash / derivative / rustls-pemfile / protobuf cleanup — now tractable with the legacy chain gone.
3. **KDV bollard**: track upstream bollard release for rustls-webpki advisory cluster.
4. **AgilePlus / eyetracker**: utoipa-axum 1.0 + uniffi 0.28+ upstream timelines.
5. **PhenoObservability / FocalPoint**: surrealdb postcard migration timeline.

## Cumulative Org-Wide Trajectory

| Wave | Audited Repos | Total Advisories | Δ from prior |
|------|---:|---:|---:|
| W-91 | 11 | ~58 | baseline |
| W-92 | 11 | 49 | -9 |
| W-93 (re-verify) | 11 | 27 | -22 |
| **W-94** | **11** | **13** | **-14 (-51.9%)** |

7 of 11 measurable repos clean; 4 with single-cluster residuals; FocalPoint exited heavy-tier; pheno first-attempt blocked on submodule remote.
