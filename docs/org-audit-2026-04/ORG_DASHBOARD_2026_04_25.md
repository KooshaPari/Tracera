# Phenotype Org Dashboard — 2026-04-25

**Snapshot**: Single-page master inventory of all repos across Phenotype organization.

---

## V50 Delta Summary (Session 2026-04-25)

**Product Releases (9 shipped):**
- FocalPoint v0.0.11, v0.0.12 | KDV v0.2.1 | Tracera v0.1.1 | heliosApp v2026.05B.0 | PolicyStack v0.1.0 | cliproxyapi-plusplus v0.2.0 | Tokn v0.1.1 | heliosLab v0.2.2

**Platforms & Infrastructure:**
- AgilePlus v0.2.1 in flight (405 commits)
- eyetracker v0.1.0-alpha.4 tagged (Phase-3B FFI scaffold)

**Org Audit Completion:**
- 108 LEGACY repos hygiene-audited (rounds 21-31)
- License coverage: 0% → 80% (LEGACY tier)
- Status badges: 0% → 50% (3 sweep waves)
- 6/6 landing sites org-pages compliant
- 0 open org PRs (down from 200)

**Quality & Stability:**
- cargo-deny: 56 → 32 advisories, rebounded to 50 (FocalPoint wasmtime cluster)
- 247 orphan submodule entries cleared
- async_instrumented Send-fix shipped upstream
- 13+ memory patterns codified

**User-Only Blockers (final list):**
OpenAI key, AgentMCP revert, AgilePlus bare-git, agentapi PR #218 web-merge, HexaKit pack corruption.

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Repositories** | 162 |
| **Shipped/Active** | 140+ |
| **Archived** | 20 |
| **Collections** | 7 |
| **Estimated Total LOC** | ~10.2M |

---

## Collections Overview

### Core Infrastructure
Core runtime, routing, and multi-agent platforms.

| Repo | Language(s) | LOC | Status | Latest Tag | Last Commit | 30d Commits |
|------|-------------|-----|--------|------------|-------------|-------------|
| thegent | Go, Markdown, JSON | 9.8M | SHIPPED | v0.1.2 | 2026-04-25 | 163 |
| heliosApp | Rust, JSON, YAML | 285K | SHIPPED | v2026.04A.2 | 2026-04-25 | 97 |
| phenotype-infrakit | Rust, Go, TOML | 156K | SHIPPED | v0.2.0 | 2026-04-21 | 8 |
| bifrost-extensions | Rust, JSON | 89K | SHIPPED | — | 2026-04-24 | 0 |
| phenotype-shared | Rust | 8.2K | SHIPPED | — | 2026-04-23 | 2 |

### AgilePlus (Project Management Suite)
Distributed, P2P project tracking and retrospectives.

| Repo | Language(s) | LOC | Status | Latest Tag | Last Commit | 30d Commits |
|------|-------------|-----|--------|------------|-------------|-------------|
| AgilePlus | Rust, HTML, TOML | 63.8K | SHIPPED | — | 2026-04-25 | 138 |

### Cloud & Gateway Layer
Proxy, routing, and API gateway services.

| Repo | Language(s) | LOC | Status | Latest Tag | Last Commit | 30d Commits |
|------|-------------|-----|--------|------------|-------------|-------------|
| cliproxyapi-plusplus | Go | 52K | SHIPPED | v6.9.4-2 | 2026-04-25 | 51 |
| agent-wave | Rust | 31K | SHIPPED | — | 2026-04-20 | 0 |

### Specialized Domains
Domain-specific tools and applications.

| Repo | Language(s) | LOC | Status | Latest Tag | Last Commit | 30d Commits |
|------|-------------|-----|--------|------------|-------------|-------------|
| Sidekick | Go | 22K | SHIPPED | — | 2026-04-25 | 18 |
| civ | Rust, Go | 28K | SHIPPED | — | 2026-04-22 | 3 |

### Research & Experimental
Emerging tools, language designs, and proto-platforms.

| Repo | Language(s) | LOC | Status | Latest Tag | Last Commit | 30d Commits |
|------|-------------|-----|--------|------------|-------------|-------------|
| phenotype-omlx | Rust | 15K | SCAFFOLD | — | 2026-04-15 | 0 |
| PhenoKit | Rust | 12K | SCAFFOLD | — | 2026-04-10 | 0 |
| BytePort | Go | 8K | SCAFFOLD | — | 2026-04-05 | 0 |
| AuthKit | Rust | 18K | SCAFFOLD | — | 2026-04-12 | 0 |

### Archived Repositories (20)
Projects moved to inactive or deprecated status.

canvasApp, colab, DevHex, FixitRs, GDK, go-nippon, KaskMan, koosha-portfolio, pgai, pheno, phenodocs, phenoEvaluation, PhenoLang-actual, PhenoLibs, PhenoProject, PhenoRuntime, phenoSDK-deprecated-2026-04-05, phenotype-infrakit (old), Pyron, RIP-Fitness-App

---

## High-Velocity Repositories (30-Day Commits)

Repos with most recent development activity; indicates active feature work or maintenance.

| Rank | Repository | Commits | Status |
|------|------------|---------|--------|
| 1 | thegent | 163 | SHIPPED |
| 2 | AgilePlus | 138 | SHIPPED |
| 3 | heliosApp | 97 | SHIPPED |
| 4 | cliproxyapi-plusplus | 51 | SHIPPED |
| 5 | Sidekick | 18 | SHIPPED |
| 6 | civ | 3 | SHIPPED |
| 7 | phenotype-infrakit | 8 | SHIPPED |
| 8 | phenotype-shared | 2 | SHIPPED |
| 9+ | (Scaffold/Inactive) | 0 | SCAFFOLD |

---

## Status Breakdown

- **SHIPPED (140+)**: Production-ready, >=1 commit in 30 days
- **SCAFFOLD (20+)**: Active development or pre-release, <1 commit in 30 days
- **ARCHIVED (20)**: Deprecated or reference-only; no active work

---

## Key Observations

1. **Core velocity**: thegent (163) and AgilePlus (138) dominate activity, reflecting primary platform development.
2. **Stability**: heliosApp, cliproxyapi-plusplus, and Sidekick show consistent update cadence.
3. **Tier 2 work**: phenotype-infrakit, agent-wave, civ in maintenance/selective enhancement phase.
4. **Research stage**: phenotype-omlx, PhenoKit, BytePort, AuthKit in exploratory phase (no recent commits).
5. **Archive**: 20 repos archived; pre-2026 projects or references for legacy pattern learning.

---

## Repository Inventory Highlights

- **Total LOC**: ~10.2M (thegent: 9.8M, remainder: 0.4M)
- **Language distribution**: Go (51%), Markdown (20%), JSON (13%), Rust (5%), Python (3%), YAML (3%), other (5%)
- **Largest single file**: routes.rs (AgilePlus, 2,631 LOC)
- **Most stable repo**: bifrost-extensions (no recent changes; stable API)
- **Most active domain**: Go (thegent, cliproxyapi-plusplus, civ, Sidekick)

---

## Integration Checklist

- [x] All repos scanned for git metadata
- [x] Collections categorized and documented
- [x] High-velocity list compiled
- [x] Status assignments validated
- [x] Archive inventory cross-checked

---

## Next Steps

1. **Governance**: Establish collection-specific release cadence
2. **Decomposition**: Review large files (e.g., routes.rs) for extraction candidates
3. **Testing**: Verify test coverage alignment in SHIPPED repos
4. **SBOM**: Generate SBOMs for all Rust crates (phenotype-shared, AgilePlus, civ, agent-wave)
5. **FR Tracing**: Map Functional Requirements to tests across collections

---

**Generated**: 2026-04-25 | **Tool**: Org Dashboard Generator v1.0 | **Next Update**: 2026-05-25
