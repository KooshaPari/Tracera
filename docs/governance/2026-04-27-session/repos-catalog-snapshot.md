# Phenotype-Org Repos Catalog Snapshot
**Date:** 2026-04-27 EOD
**Source:** observed during this session's mass lockfile-regen sweep

## Tier 1 — Active products (alerts at session start → end)
| Repo | Pre | Post | Method |
|---|---|---|---|
| HexaKit | 48 | 18 | lockfile + audit-fix-force (residuals manifest-bound) |
| QuadSGM | 37 | 0 | manifest-fix + uv lock --upgrade (CRIT cleared) |
| thegent | 49 | 10 | uv + npm + go (residuals manifest-bound) |
| PhenoLang | 36 | 3 | cargo update + uv lock + npm update |
| pheno | 22 | 19 | uv lock partial; cargo blocked by submodule URL |
| heliosCLI | 19 | 18 | npm audit fix --force (residuals uuid peerDep) |
| Tracera | 15 | 6 | cargo update + uv lock + go mod tidy |
| KDesktopVirt | 8 | 5 | cargo update (residuals manifest-bound) |
| AgilePlus | 4 | 4 | minor; lockfile clean |
| hwLedger | 7 | 7 | cargo no-op (rescan pending) |
| PhenoRuntime | 6 | 6 | no-diff |
| PhenoProject | 30 | 30 | npm peerDep override conflicts |

## Tier 2 — Maintained libs
| Repo | Alerts | Notes |
|---|---|---|
| byteport | 8 | lockfile clean; rescan pending |
| Civis | <5 | Cargo update merged (PR #258, #260) |
| Sidekick | 0 | merged PR #7 |
| Tasken | <5 | merged PR #8, #9 |
| HeliosLab | 3 | merged PR #61, #62, #63, #64, #65 |
| heliosBench | 0 | merged PR #131 |
| helios-router | 2 | merged PR #189 |
| Parpoura | 1 | merged PR #177 (4 cleared) |
| PolicyStack | 2 | merged PR #12 |
| PlatformKit | 2 | merged PR #19 |
| Dino | 5 | unmerged in batch (Dino R3 was no-diff) |
| Paginary | 3 | unchanged |
| DevHex | 3 | unchanged |
| phenotype-ops-mcp | 3 | no-diff |
| phenotype-auth-ts | 3 | no-diff |
| phenoDesign | 2 | no-diff |

## Pre-merge organization actions (this session)
- Bot-issue R6 sweep: 17 closed (8 agentapi-plusplus + 9 helios-cli)
- Stale branch cleanup: 32+ deleted (cliproxyapi 6, HexaKit 2, heliosCLI 5, AgilePlus 9, thegent 10)
- Total PRs: 18-20 lockfile-regen merged

## Repos NOT touched this session (Tier 3+)
~50 repos with 0 alerts or stale enough to skip. Next session can audit individually.

## Top 10 residuals (next-session priority)
1. PhenoProject 30 — npm peerDep walkthrough (manual review)
2. pheno 19 — submodule URL fix as separate small PR
3. HexaKit 18 — `cargo update --precise` per residual (cookbook avail)
4. heliosCLI 18 — uuid peerDep manifest edit
5. thegent 10 — manifest-level transitive bumps
6. byteport 8 — rescan verify
7. hwLedger 7 — rescan verify
8. Tracera 6 — rescan verify
9. PhenoRuntime 6 — manifest investigation
10. KDesktopVirt 5 — rustls-webpki + inventory parent bumps
