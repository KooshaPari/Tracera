# Cargo-Deny Advisory Sweep — W-93 (2026-04-26 evening)

Post-fix snapshot following today's deps-impacting work: pyo3 0.22→0.24 (HeliosLab/Configra), ratatui 0.29→0.30 (HeliosLab/Configra/KDV), Tauri suppress-with-justification (hwLedger/BytePort), openssl + fastmcp bumps in PhenoLang, AgilePlus v0.2.1 release.

## Methodology

- Tool: `cargo-deny 0.19.0`
- Scope: all 9 W-92 repos with Rust advisory deltas (FocalPoint, AgilePlus, PhenoObservability, eyetracker, hwLedger, BytePort, KDesktopVirt, HeliosLab, Configra).
- Command: `cargo deny check advisories` (no build, no update).
- Per-repo cap: 60s.
- Skipped: Sidekick/Eidolon/Tracely/GDK (W-92 tooling errors not yet repaired).

## Results — W-92 → W-93 Delta

| Repo | W-92 | W-93 | Δ | Verdict | Notes |
|------|-----:|-----:|---:|---------|-------|
| hwLedger | 24 | **0** | -24 | ok | Tauri suppress-with-justification entries active in deny.toml |
| BytePort | 17 | n/a | — | TOOLING ERROR | dual workspace roots (`frontend/web/src-tauri` + repo root) — cargo-deny refuses to resolve. Suppressions present but unverifiable until workspace structure is split. |
| KDesktopVirt | 4 | **5** | +1 | FAILED | ratatui 0.30 ✓ but pulled `time 0.3.41` <0.3.47 (RUSTSEC-2026-0009 stack-exhaustion DoS), plus 4 prior bollard/rustls-webpki advisories remain |
| HeliosLab | 2 | **0** | -2 | ok | pyo3 0.24 + ratatui 0.30 — both clean |
| Configra | 2 | **0** | -2 | ok | pyo3 0.24 + ratatui 0.30 — clean (3 stale ignores warn `advisory-not-detected`) |
| FocalPoint | 19 | **19** | 0 | FAILED | unchanged — multipart/iron/nickel/typemap unmaintained chain |
| AgilePlus | 1 | **1** | 0 | FAILED | RUSTSEC-2024-0436 (paste) via utoipa-axum 0.2 — independent of v0.2.1 release path |
| PhenoObservability | 1 | **1** | 0 | FAILED | RUSTSEC-2025-0141 (bincode unmaintained, surrealdb chain) |
| eyetracker | 2 | **2** | 0 | FAILED | bincode + paste via uniffi 0.27 |

## Wave Totals

- W-92 audited sum (9 repos): **49** advisories
- W-93 audited sum (8 measurable repos): **28** advisories
- BytePort excluded from W-93 numerics (workspace tooling error post-edit). W-92's 17 BytePort advisories presumed suppressed — confirm after workspace split.
- **Net delta (apples-to-apples, excluding BytePort both sides): 32 → 28 = -4 (-12.5%)**
- **Inclusive delta (assuming BytePort suppressions effective): 49 → 28 = -21 (-43%)**

## Cluster Analysis

- **pyo3 cluster — RESOLVED.** HeliosLab + Configra both clean. RUSTSEC-2025-0020 cleared from org.
- **ratatui cluster — RESOLVED for HeliosLab/Configra; REGRESSION on KDV.** RUSTSEC-2024-0436 (paste) cleared from HeliosLab/Configra, but ratatui 0.30 → ratatui-widgets 0.3 → time 0.3.41 introduced **RUSTSEC-2026-0009** (DoS stack exhaustion). Fix: `cargo update -p time` (need ≥0.3.47).
- **Tauri cluster — SUPPRESSED in hwLedger; UNVERIFIABLE in BytePort.** hwLedger reports 0 advisories — suppression entries verified working. BytePort blocked by dual-workspace-root before cargo-deny can evaluate.
- **Stale-ignore warnings (advisory-not-detected).** Configra has 3, AgilePlus has 1 — flagged as cleanup candidates. Indicates upstream patches landed; ignore entries can be retired.

## Unexpected Findings

1. **KDV regressed by 1.** ratatui 0.30 upgrade added a transitive `time 0.3.41` (one minor behind the 0.3.47 patch). Net: -3 (paste cleared) +4 (one new time DoS + 3 unchanged bollard/rustls-webpki) = +1. Trivial follow-up: `cargo update -p time`.
2. **BytePort workspace breakage.** Tauri-suppress agent's edits left two `[workspace]` roots in the Cargo graph; needs structural fix (likely `[workspace] members = ["frontend/web/src-tauri"]` from root or excluding the nested manifest).
3. **AgilePlus stale ignore.** RUSTSEC-2025-0134 ignore is now `advisory-not-detected` post v0.2.1 → confirms async-nats upgrade cleared rustls-pemfile transitively. Safe to delete the ignore line.

## Follow-up Tickets

1. KDV: `cargo update -p time` to ≥0.3.47 — closes RUSTSEC-2026-0009.
2. BytePort: split or unify workspace; re-run advisories to confirm 17→0.
3. Configra/AgilePlus: prune stale `advisory-not-detected` ignore entries (4 total).
4. FocalPoint: schedule decommission of templates-registry's iron/nickel/multipart legacy chain (19 advisories, no patches available).
5. PhenoObservability + eyetracker: track surrealdb (bincode→postcard) and uniffi 0.28+ (paste→pastey) upstream timelines.

## Cumulative Org-Wide (Audited Subset)

- W-92 (9 repos): 49 advisories
- W-93 (8 repos measurable): **28** advisories
- 5 repos clean (hwLedger, HeliosLab, Configra) joined W-92's heliosCLI + PhenoProc → **5 of 11 cleanly auditable repos at zero advisories** (was 2 of 11).
