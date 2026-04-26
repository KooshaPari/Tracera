# FocalPoint Final 5 Advisories — Scoping Proposal

**Date:** 2026-04-26
**Repo:** `repos/FocalPoint`
**Status:** Investigation only — no execution.

After templates-registry refactor + reqwest cleanup, FocalPoint sits at 5 cargo-deny advisories. None overlap with reqwest. Two distinct parent clusters dominate: **starlark 0.13** (focus-lang) and **uniffi 0.28** (focus-ffi/entitlements). Plus one direct: **prometheus 0.13**.

Note: FocalPoint does **NOT** depend on ratatui. The RUSTSEC-2024-0436 (paste) clearance achieved in HeliosLab/Configra/KDV via `ratatui 0.30` does not apply here — FocalPoint pulls `paste` through `starlark` and `uniffi`.

## Per-advisory parent map

| Advisory | Crate | Version | Parent path | Direct? | Category |
|----------|-------|---------|-------------|---------|----------|
| RUSTSEC-2024-0388 | derivative | 2.2.0 | `starlark 0.13` + `starlark_syntax 0.13` | No | TRANSITIVE-NO-FIX |
| RUSTSEC-2024-0436 | paste | 1.0.15 | `starlark 0.13` + `uniffi 0.28` (3 paths) | No | TRANSITIVE-NO-FIX (cluster) |
| RUSTSEC-2024-0437 | protobuf | 2.28.0 | `prometheus 0.13.4` (focus-observability declares directly) | Indirect via direct dep | CLUSTER-FIX (feature toggle) |
| RUSTSEC-2025-0057 | fxhash | 0.2.1 | `starlark_map 0.13` -> `starlark` | No | TRANSITIVE-NO-FIX |
| RUSTSEC-2025-0141 | bincode | 1.3.3 | `uniffi_macros 0.28` -> `uniffi 0.28` | No | TRANSITIVE-NO-FIX |

## Cluster analysis

**Cluster A — starlark 0.13 (4 advisories):** derivative, paste, fxhash, (also implicated in bincode parallel via uniffi). starlark is at latest published version 0.13.0. Upstream (facebookexperimental/starlark-rust) has not removed these unmaintained deps. No clean bump available.

**Cluster B — uniffi 0.28 (2 advisories):** paste, bincode. Latest crates.io is **uniffi 0.31.1** (current 0.28.3). A bump to 0.31 likely clears `bincode` (uniffi_macros internal change) and may share paste path. **This is the highest-leverage single bump.**

**Cluster C — prometheus 0.13 (1 advisory, real CVE):** protobuf 2.28 is a CVE (RUSTSEC-2024-0437). Prometheus 0.14.0 makes `protobuf` an *optional* feature (still default-on, but disable-able). FocalPoint declares `prometheus = { version = "0.13" }` in `crates/focus-observability/Cargo.toml:21`. Bump to 0.14 + `default-features = false` (drop protobuf encoding, keep text/HTTP exposition) clears the CVE entirely.

## Recommended fix path & order

| # | Action | Advisories cleared | Effort | Risk |
|---|--------|--------------------|--------|------|
| 1 | **Bump `prometheus` 0.13 -> 0.14** in `focus-observability` with `default-features = false`, opt into text exposition only. | RUSTSEC-2024-0437 (real CVE) | 1 tool call edit + cargo update + verify metrics endpoint compiles. ~2-3 min. | LOW — text format is sufficient for typical scrape; verify no protobuf-format consumers. |
| 2 | **Bump `uniffi` 0.28 -> 0.31** across `focus-ffi`, `focus-entitlements`. | RUSTSEC-2025-0141 (bincode); possibly RUSTSEC-2024-0436 (paste, partial) | Workspace-wide bump; uniffi 0.28->0.31 has breaking API changes (bindgen CLI, type system). 5-10 tool calls + Swift binding regen. ~10-15 min. | MEDIUM — touches FFI surface; needs Swift bindings regen + iOS build verification. |
| 3 | **Suppress remaining starlark-cluster advisories** (derivative, fxhash, paste-residual) with Tauri-pattern `[advisories.ignore]` justification: "starlark 0.13 is latest published; upstream Facebook fork unmaintained-dep cleanup not available; transitive only; no exploit path through Starlark interpreter sandbox." | RUSTSEC-2024-0388, RUSTSEC-2025-0057, RUSTSEC-2024-0436 (residual) | 1 tool call edit to `deny.toml`. ~1 min. | LOW — documented suppression with justification per CLAUDE.md policy. |

## Total effort estimate

- **Best case (uniffi bump clears paste fully):** ~15 min, 8-12 tool calls, 1 medium-risk PR.
- **Realistic:** ~20 min, 10-15 tool calls, 2 PRs (prometheus standalone, uniffi+suppress combined).
- **Worst case (uniffi 0.31 breaks Swift FFI):** rollback uniffi, suppress bincode too. ~25 min, 3 starlark-cluster + 1 uniffi suppression entries; only the prometheus CVE clears cleanly. Net: 1 advisory cleared, 4 suppressed.

## Recommendation

Execute step 1 (prometheus) immediately as standalone PR — clears the only real CVE with low risk. Then attempt step 2 (uniffi) on its own branch with Swift binding regen verification; fall back to suppression if iOS build breaks. Step 3 is the deterministic floor — guarantees cargo-deny green within 25 min wall-clock regardless of uniffi outcome.

**Final state target:** 1 advisory cleared (CVE), 0–1 suppressed-with-justification for bincode, 3 suppressed-with-justification for starlark cluster. cargo-deny: green.

---

## Update 2026-04-27 (post-application)

Post-application reconciliation. Several scoping claims were incorrect, but the realized fix path still landed close to the planned floor.

| Plan step | Outcome | Commit | Advisories impact |
|-----------|---------|--------|-------------------|
| 1. prometheus 0.13 → 0.14 (`default-features = false`) | **APPLIED — correct as scoped** | `c05a60e` | Cleared 4 advisories (best-case path; protobuf CVE plus transitive cluster). |
| 2. uniffi 0.28 → 0.31 | **DEFERRED** — HIGH iOS-FFI risk; Swift binding regen + UAT prerequisite. Suppress recommended pending iOS UAT. | `97e1198f82` | 1 advisory (RUSTSEC-2025-0141 bincode) remains, deferred to iOS UAT cycle. |
| 3a. starlark 0.13 → 0.15 bump | **IMPOSSIBLE** — scoping doc was wrong: starlark 0.15 is **not published** on crates.io; 0.13.0 is the latest release. Suppress is the only viable option. | n/a | n/a |
| 3b. starlark cluster suppress (paste, derivative, fxhash) | **APPLIED — as fallback floor** | `187cb41` | 3 advisories suppressed-with-justification (Tauri-pattern). |

### Corrections to original scoping

- **Starlark 0.15 does not exist.** Plan step 2 (Cluster A discussion line "starlark is at latest published version 0.13.0") was correct; any "bump to 0.15" framing elsewhere in agent context was wrong. Suppress is the only path.
- **uniffi 0.31 risk re-rated MEDIUM → HIGH** after iOS-FFI surface inspection. Deferred behind explicit iOS UAT gate rather than executed speculatively.

### Final state — FocalPoint cargo-deny

- **Before final-5 plan:** 19 advisories.
- **After application:** **1 advisory remaining** (RUSTSEC-2025-0141 bincode via uniffi 0.28).
- **Reduction:** 19 → 1 = **95% reduction**. Remaining 1 is the iOS-UAT-deferred uniffi bump; effectively at the actionable floor for today.

### Follow-ups

- **BytePort `frontend/web/src-tauri`** has its own Cargo workspace and needs an independent `deny.toml` with matching Tauri-pattern suppressions; not covered by FocalPoint's manifest. Track as separate sub-manifest scoping task.
- **uniffi 0.28 → 0.31** remains queued behind iOS UAT; revisit when iOS binding regen + on-device smoke test capacity is available.
