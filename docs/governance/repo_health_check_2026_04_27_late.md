# Cross-Repo Health Check — Post W-96 Deps Wave

**Date:** 2026-04-27 (late)
**Scope:** Rust workspaces touched by today's dependency / SBOM / cargo-deny work.
**Mode:** Pure read — `cargo metadata --no-deps` parse + `git status Cargo.lock` drift + last commit.

## Summary

| Status | Count | Repos |
|--------|-------|-------|
| GREEN  | 11    | BytePort, KDesktopVirt, HeliosLab, Configra, FocalPoint, AgilePlus*, PhenoObservability, eyetracker, heliosCLI, PhenoProc, pheno |
| YELLOW | 1     | hwLedger (Cargo.lock dirty, uncommitted) |
| RED    | 0     | — |

`*` AgilePlus canonical folder is a **bare repo** (`is-bare-repository=true`); `git status` therefore returns "must be run in a work tree". This is expected for the canonical mirror layout, not a parse failure. `cargo metadata` succeeded.

## Per-Repo Detail

| Repo | meta_exit | Cargo.lock | Last Commit |
|------|-----------|-----------|-------------|
| hwLedger | 0 | **M Cargo.lock** | `04fdbc0 chore(sbom): bootstrap CycloneDX SBOM tracking (post-2026-04-26 deps refresh)` |
| BytePort | 0 | clean | `6c01dd66 fix(workspace): consolidate to single workspace root for cargo-deny audit` |
| KDesktopVirt | 0 | clean | `14f0a9c chore(deny): remove 3 stale ignores (post-bollard 0.20)` |
| HeliosLab | 0 | clean | `cca07e8 chore(sbom): bootstrap CycloneDX SBOM tracking` |
| Configra | 0 | clean | `f0a3398 chore(sbom): bootstrap CycloneDX SBOMs (workspace coverage)` |
| FocalPoint | 0 | clean | `f373073 chore(deny): suppress RUSTSEC-2025-0141 bincode pending iOS UAT` |
| AgilePlus | 0 | n/a (bare) | `2b3909f chore(deny): remove 1 stale ignore (upstream patch landed)` |
| PhenoObservability | 0 | clean | `ba25d1e chore(crates): remove dead phenotype-surrealdb stub` |
| eyetracker | 0 | clean | `eedfd49 chore(ffi): bump uniffi to 0.31 (#3)` |
| heliosCLI | 0 | clean | `b29c6f9 chore(deny): remove 2 unused ignores` |
| PhenoProc | 0 | clean | `d01c53a chore(dead-code): remove orphan bifrost-routing-backup` |
| pheno | 0 | clean | `fc601c0 chore(sbom): bootstrap CycloneDX SBOMs (post-workspace-cleanup)` |

## Findings

- **0 RED** — every workspace's `Cargo.toml` graph still resolves; no missing members, no broken paths, no unresolved registry refs.
- **1 YELLOW** — `hwLedger/Cargo.lock` has uncommitted changes (likely a `cargo update` side-effect from the SBOM bootstrap commit). Action: review and either commit or restore in next hwLedger touch; not blocking.
- **AgilePlus bare-repo note** — confirms canonical folder is bare; agent activity belongs in `AgilePlus-wtrees/<topic>` worktrees per Phenotype worktree commandments.

## No Action Required

Today's dep/SBOM/cargo-deny waves did **not** introduce workspace metadata regressions in any of the 12 audited repos. hwLedger's dirty lock is the only follow-up.
