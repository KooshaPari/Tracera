# LEGACY Badge Hygiene — FINAL Ledger (Round 35)

**Date**: 2026-04-26
**Scope**: Final sweep of LEGACY-tier repos lacking shields.io badges in first 30 README lines.
**Predecessor**: Rounds 21-31 (audit) + Rounds 32-34 (badge application, ~78.5% coverage entering R35).

## Round-35 Applied (6 repos)

| Repo | Language | Commit | Notes |
|------|----------|--------|-------|
| argis-extensions | Go | 0d7f950 | "Bifrost Extensions" upstream wrapper |
| byteport-landing | TS | 12cbf47 | Tier-2 org-pages landing |
| cheap-llm-mcp | Python | aa9849b | Haiku-replacement MCP server |
| hwledger-landing | TS | 67c23a9 | Tier-2 org-pages landing |
| phenokits-landing | TS | 8f73475 | Tier-2 org-pages landing |
| phenotype-bus | Rust | f5b01d5 | Async pub/sub event bus |

Per-repo standard 3-badge header (License + CI + Language). Local commits only; no push.

## Coverage Delta

- **Pre-R35**: ~78.5% of 108 LEGACY repos badged (~85 repos)
- **R35 added**: 6 repos
- **Post-R35**: ~84.3% (~91/108 repos badged)

Estimated remaining un-badged: ~17 repos.

## Skip Categories (Remaining Tail)

| Category | Repos | Rationale |
|----------|-------|-----------|
| Nested-workspace ghosts | PhenoContracts, PhenoEvents, PhenoKit, PhenoSchema | 1-3 line placeholder READMEs (per `nested_workspaces.md` 274f946e68); not worth badging |
| 404 / reconciliation in flight | phenoSDK | Separate phenoSDK reconciliation excluded by directive |
| Critical metadata gaps | crates, configs, credentials | Per R31 ledger: 0/4 hygiene; need full README before badges meaningful |
| Archived / status=archived | dinoforge-packs | README declares "Status: archived" |
| Dirty worktrees (active branches) | atoms.tech, bare-cua, DataKit, KlipDot, localbase3, netweave-final2, org-github, phench, phenotype-auth-ts, phenotype-journeys, AgentMCP | Non-main branches or large dirty trees; skip per provenance discipline |
| Doc-only / no-language | phenotype-hub | No Cargo.toml/package.json/pyproject; cannot pick canonical language badge |
| Already touched recently (<R34) | PhenoMCP (48bc21a), foqos-private, Configra, Civis, BytePort, cloud, eyetracker, DevHex, GDK, cliproxyapi-plusplus | Per R31 ledger and memory; some still showing badges=✗ in R31 audit but pending re-verify |

## Certification

**Status**: TAIL-DEFERRED at ~84.3% (below 90% threshold).

**Named blockers preventing 90%+ this round**:
1. **Critical metadata tier (3 repos)**: crates/configs/credentials need README authorship before badges, not badge-only.
2. **Nested-workspace ghosts (4 repos)**: should be deleted or expanded per nested_workspaces governance, not band-aid badged.
3. **Dirty-tree repos (~11 repos)**: feature branches mid-flight; touching READMEs would cross provenance lines (MODE 1 vs MODE 2 mixing per dirty-tree commit discipline).
4. **phenoSDK**: explicitly excluded by directive.

**Path to 90%+**:
- Resolve nested-workspace ghosts (delete 4 dirs) → mechanical denominator drop pulls coverage to ~88%.
- Author proper READMEs for crates/configs/credentials → +3 to numerator → ~91%.
- Once dirty-tree branches merge, sweep remaining ~11 → 95%+ feasible.

## Decision

R35 closes systematic LEGACY badge sweeps. Further coverage gains depend on **content authorship** (READMEs, decisions on ghost dirs) rather than mechanical badge insertion. No R36 recommended without first resolving the nested-workspace and critical-metadata blockers.

— Round-35, 2026-04-26
