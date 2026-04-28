# Dependabot Residuals Tracker — 2026-04-27 EOD

## Top residuals (manifest-bound)
| Repo | Open alerts | Ecosystem | Notes |
|---|---|---|---|
| PhenoProject | 30 | npm | peerDep override conflicts; needs manual override edits |
| pheno | 19 | rust+npm | Cargo blocked on submodule URL config; partial Python clear |
| HexaKit | 18 | rust+pip | rust transitives at semver pin; need cargo update --precise |
| heliosCLI | 18 | npm+rust | npm peer-dep on uuid; rust lockfile partial |
| hwLedger | 7 | rust+pip | minor; cargo update was no-op |
| PhenoRuntime | 6 | mixed | minor |
| KDesktopVirt | 5 | rust | residual after PR #14 merged 8→5 |
| Dino | 5 | mixed | clone failed in batch; retry needed |
| AgilePlus | 4 | mixed | minor; rescan async |
| phenotype-ops-mcp | 3 | mixed | minor |
| PhenoLang | 3 | residual after PR #28 (-33) | minor |
| Paginary | 3 | mixed | minor |
| HeliosLab | 3 | mixed | minor after PR #61, #63, #64 |
| DevHex | 3 | mixed | minor |
| PolicyStack | 2 | mixed | minor after PR #12 |
| PlatformKit | 2 | mixed | minor after PR #19 |
| phenoDesign | 2 | npm | minor |
| helios-router | 2 | mixed | minor after PR #189 |
| Parpoura | 1 | mixed | minor after PR #177 |
| **TOTAL** | **127** | | down from 207 (-80, -39%) |

## Cleared this session
- QuadSGM 37→0 (incl 2 CRIT: fastmcp SSRF, authlib JWS bypass)
- thegent 49→10 (-39)
- HexaKit 48→18 then audit-fix 18→18 (npm cleared, rust residual)
- PhenoLang 36→3 (-33)
- KDesktopVirt 8→5 (-3)
- Tracera 15→6 (-9)
- byteport 8→8 (lockfile applied; rescan pending — predict drop)
- pheno 22→19 (-3, partial Python clear)
- + many minor-residuals (1-2 each)

## Recommended next-session actions
1. PhenoProject npm overrides walkthrough (manual review of 30)
2. HexaKit `cargo tree --invert <vulnerable>` per residual to identify parent bumps
3. heliosCLI uuid peerDep resolution
4. pheno submodule URL config fix (separate small PR) — superseded by 2026-04-28 live check: `gh api repos/KooshaPari/pheno/dependabot/alerts` returned no open alerts, `.gitmodules` URLs are HTTPS remotes, and local submodule URL config has no drift.
5. Verify CRIT count == 0 across org — completed 2026-04-28; live sweep found no open critical Dependabot alerts. Repos with Dependabot alerts disabled during the sweep: Planify, DINOForge-UnityDoorstop, vibeproxy, portage.

## 2026-04-28 Follow-up
- Closed `KooshaPari/Tracera#390` as stale/conflict-no-deep-rebase. Evidence: `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY`, 87 changed files, broad workflow/archive/data/CLI-stub changes, and checked-in `__pycache__` artifacts.
