# Unmaintained-Crate Cluster Audit — 2026-04-27

**Advisories:** RUSTSEC-2024-0436 (paste), RUSTSEC-2024-0388 (derivative), RUSTSEC-2025-0057 (fxhash)
**Method:** Cargo.lock scan + parent-dep inspection (no cargo tree, pure lockfile reads). Vendored `codex-rs` subtrees skipped.
**Scope (12 repos):** hwLedger, BytePort, KDesktopVirt, HeliosLab, Configra, FocalPoint, AgilePlus, PhenoObservability, eyetracker, heliosCLI, PhenoProc, pheno.

## Org Matrix

| Repo | paste | derivative | fxhash | Parent dep(s) |
|---|---|---|---|---|
| hwLedger | — | — | 0.2.1 | selectors |
| BytePort (root) | — | — | 0.2.1 | selectors |
| BytePort (tauri) | — | — | 0.2.1 | selectors |
| KDesktopVirt | 1.0.15 | 2.2.0 | 0.2.1 | gstreamer + option-operations / kube-runtime / display-info + screenshots |
| HeliosLab | — | — | — | (cleared via ratatui 0.29→0.30, today) |
| Configra | — | — | — | (cleared today) |
| FocalPoint (root) | 1.0.15 | 2.2.0 | 0.2.1 | starlark + uniffi / starlark + starlark_syntax / starlark_map |
| FocalPoint (fuzz) | 1.0.15 | 2.2.0 | 0.2.1 | same |
| FocalPoint (rule-library tests) | 1.0.15 | 2.2.0 | 0.2.1 | same |
| AgilePlus | 1.0.15 | — | — | utoipa-axum |
| PhenoObservability | — | — | — | clean |
| eyetracker | 1.0.15 | — | — | uniffi_bindgen + uniffi_core |
| heliosCLI | — | — | — | clean |
| PhenoProc/Evalora | 1.0.15 | — | — | simba |
| PhenoProc/byteport-tauri | — | — | 0.2.1 | selectors |
| pheno | — | — | — | clean |

## Cluster Patterns

1. **selectors → fxhash** (hwLedger, BytePort×2, PhenoProc/byteport-tauri). The `selectors` crate (servo CSS selectors, used transitively by html5ever / scraper / kuchiki) still pins fxhash 0.2.1. Single upstream cluster — 4 lockfiles.
2. **starlark → paste + derivative + fxhash** (FocalPoint×3). Triple-hit cluster. starlark-rs 0.13 ecosystem still pulls all three. starlark 0.14 (in flight upstream) drops `derivative`; full purge needs 0.15+.
3. **uniffi → paste** (FocalPoint, eyetracker). uniffi 0.28 still uses paste in `uniffi_bindgen`/`uniffi_core`. Cleared by uniffi 0.29+ migration.
4. **gstreamer / kube / display-info / screenshots / option-operations → paste+deriv+fxhash** (KDesktopVirt only). Heterogeneous; KDV is the worst single-repo case (3 advisories × 4 distinct parent lineages).
5. **utoipa-axum → paste** (AgilePlus). Cleared by utoipa 5.x → 6.x (paste-free) once released.
6. **simba → paste** (PhenoProc/Evalora). simba 0.9 still has it; nalgebra-stack issue.

## Top 5 Leverage Targets

| Rank | Upgrade | Repos cleared | Advisories cleared |
|---|---|---|---|
| 1 | `selectors` (whichever scraper/html5ever consumer is pinning it — likely scraper 0.20→0.22) | hwLedger, BytePort root, BytePort tauri, PhenoProc/byteport-tauri (4) | fxhash ×4 |
| 2 | `starlark` 0.13→0.15 | FocalPoint root + fuzz + rule-library (3) | paste+derivative+fxhash ×3 = 9 |
| 3 | `uniffi` 0.28→0.29 | FocalPoint, eyetracker (2; FocalPoint paste already covered by #2) | paste ×1 net (eyetracker) |
| 4 | `utoipa-axum` (next major) | AgilePlus (1) | paste ×1 |
| 5 | KDV multi-bump (`gstreamer` 0.23+, `kube` 0.99+, `display-info` 0.5+, drop `screenshots` for `xcap`) | KDesktopVirt (1) | paste+deriv+fxhash ×1 = 3 |

## Expected Delta

- **#1 selectors-cluster bump:** clears 4 of 6 fxhash exposures org-wide (~67% of fxhash advisory surface).
- **#2 starlark bump:** clears all 3 derivative exposures and 3 of 6 fxhash; biggest single-repo win.
- **Combined #1+#2:** clears 100% of derivative org-wide; 5/6 fxhash; 3/6 paste (FocalPoint trio).
- **+#3+#4:** clears remaining paste in eyetracker + AgilePlus; leaves only KDV + simba (PhenoProc/Evalora).
- **Final residual after top-4:** KDV (3 advisories, heterogeneous parents) + PhenoProc/Evalora (paste via simba). KDV warrants its own dedicated bump cycle.

## Notes

- `pheno`, `heliosCLI`, `PhenoObservability`, `HeliosLab` (post ratatui 0.30), `Configra` (post ratatui 0.30): **clean baseline**.
- KDV has no Cargo.lock under `KDV` path; canonical name is `KDesktopVirt`.
- All findings are lockfile-only; no cargo invocations were run (disk/FD-safe).

— audit only, no bumps performed
