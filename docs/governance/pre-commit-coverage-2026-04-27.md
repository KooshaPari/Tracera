# Pre-commit Hook Coverage Audit — KooshaPari Org

**Date:** 2026-04-27
**Method:** API-only via `gh api`. Probed `.pre-commit-config.yaml` on default branch.
**Scope:** 82 non-archived repos.

## Summary

| Status | Count | % |
|--------|------:|--:|
| Missing | 50 | 61.0% |
| Stub (<200 bytes) | 6 | 7.3% |
| Standard (>=200 bytes) | 26 | 31.7% |

## By Language (Missing)

| Language | Missing |
|----------|--------:|
| Rust | 16 |
| Go | 8 |
| TypeScript | 6 |
| Python | 6 |
| Astro | 6 |
| none | 5 |
| Kotlin/HTML/C | 3 |

## By Language (Standard — for comparison)

Rust 10, Python 3, Go 3, TypeScript 2, JS 2, none 2, Swift/HTML/CSS/C# 1 each.

## Stub Repos (need expansion)

| Repo | Language | Size |
|------|----------|-----:|
| Apisync | Rust | 43 |
| Tokn | Rust | 43 |
| PolicyStack | Python | 20 |
| Stashly | Rust | 20 |
| Tasken | Rust | 20 |
| thegent | Python | 20 |

## Top 10 Missing (priority: Rust/Go/TS/Python core libs)

1. FocalPoint (Rust)
2. Metron (Rust)
3. ObservabilityKit (Rust)
4. PhenoAgent (Rust)
5. PhenoMCP (Rust)
6. PhenoObservability (Rust)
7. PhenoRuntime (Rust)
8. hwLedger (Rust)
9. AuthKit (Rust)
10. McpKit (Go)

## Full Missing Inventory

Rust (16): Agentora, AuthKit, FocalPoint, hwLedger, Metron, ObservabilityKit, PhenoAgent, phenoAI, phenoData, PhenoMCP, PhenoObservability, phenotype-infra, phenoUtils, PhenoRuntime, PhenoVCS, PlayCua

Go (8): DevHex, dinoforge-packs, MCPForge, McpKit, nanovms, PhenoCompose, phenotype-ops-mcp, PlatformKit

TypeScript (6): Conft, PhenoHandbook, PhenoProject, PhenoSpecs, phenotype-auth-ts, Planify

Python (6): DataKit, heliosBench, PhenoKits, phenotype-omlx, ResilienceKit, TestingKit

Astro (6, landing pages): agileplus/byteport/hwledger/phenokits/projects/thegent-landing

Other (8): AgentMCP, DINOForge-UnityDoorstop, eyetracker, PhenoDevOps, PhenoPlugins, phenotype-hub, phenotype-registry, phenoXdd

## Recommendations

- Extend stubs (6 repos, all <50 bytes) — likely empty/placeholder.
- Roll out a Rust template covering 16 missing core repos (gitleaks/trufflehog + clippy + rustfmt + trailing-whitespace).
- Go template for 8 missing (golangci-lint + gofumpt).
- Python/TS templates already piloted in standard repos — clone configs.
