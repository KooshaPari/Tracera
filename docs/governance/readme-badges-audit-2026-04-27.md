# README Badge Audit — 2026-04-27

**Scope:** Top-30 most-recently-pushed non-archived non-fork repos under `KooshaPari/`.
**Method:** GitHub Contents API → base64 decode README.md → regex-grep 4 badge categories.

## Categories

| Category | Pattern |
|---|---|
| License | `shields.io/badge/[Ll]icense`, `shields.io/github/license`, `License-(MIT|Apache|BSD)` |
| Build/CI | `actions/workflows/<name>.yml/badge.svg`, `shields.io/github/actions/workflow/status` |
| Release/version | `shields.io/crates/v`, `shields.io/npm/v`, `shields.io/pypi/v`, `shields.io/github/v/release`, `crates.io/crates/...`, `badge.fury.io` |
| Docs | `docs.rs/<crate>/badge`, `readthedocs.io/.../badge`, `shields.io/badge/docs` |

Scoring: **OK** ≥3 categories · **PARTIAL** 1–2 · **NONE** 0.

## Results — Top-30

| Repo | Score | Lic | CI | Ver | Doc |
|---|---|---|---|---|---|
| DevHex | PARTIAL (2) | 1 | 1 | 0 | 0 |
| Httpora | PARTIAL (2) | 1 | 1 | 0 | 0 |
| PhenoAgent | PARTIAL (2) | 1 | 1 | 0 | 0 |
| PhenoCompose | PARTIAL (2) | 1 | 1 | 0 | 0 |
| PhenoDevOps | PARTIAL (2) | 1 | 1 | 0 | 0 |
| PhenoMCP | PARTIAL (2) | 1 | 1 | 0 | 0 |
| PhenoPlugins | PARTIAL (2) | 1 | 1 | 0 | 0 |
| PhenoProc | PARTIAL (2) | 1 | 1 | 0 | 0 |
| Agentora | NONE | 0 | 0 | 0 | 0 |
| phenotype-auth-ts | NONE | 0 | 0 | 0 | 0 |
| PlayCua | NONE | 0 | 0 | 0 | 0 |
| AuthKit | NONE | 0 | 0 | 0 | 0 |
| AgilePlus | NONE | 0 | 0 | 0 | 0 |
| FocalPoint | NONE | 0 | 0 | 0 | 0 |
| heliosCLI | NONE | 0 | 0 | 0 | 0 |
| phenoXdd | NONE | 0 | 0 | 0 | 0 |
| phenotype-infra | NONE | 0 | 0 | 0 | 0 |
| phenotype-tooling | NONE | 0 | 0 | 0 | 0 |
| AgentMCP | NONE | 0 | 0 | 0 | 0 |
| PlatformKit | NONE | 0 | 0 | 0 | 0 |
| ResilienceKit | NONE | 0 | 0 | 0 | 0 |
| PhenoKits | NONE | 0 | 0 | 0 | 0 |
| hwLedger | NONE | 0 | 0 | 0 | 0 |
| McpKit | NONE | 0 | 0 | 0 | 0 |
| ObservabilityKit | NONE | 0 | 0 | 0 | 0 |
| TestingKit | NONE | 0 | 0 | 0 | 0 |
| Benchora | NONE | 0 | 0 | 0 | 0 |
| nanovms | NONE | 0 | 0 | 0 | 0 |
| agent-devops-setups | NONE | 0 | 0 | 0 | 0 |
| GDK | NONE | 0 | 0 | 0 | 0 |

## Summary

- **OK (≥3):** **0 / 30** (0%)
- **PARTIAL (1–2):** **8 / 30** (27%) — all sit at exactly 2 (License + CI)
- **NONE:** **22 / 30** (73%)
- **Zero repos** carry a release/version badge or a docs badge.

## Top-10 Most-Naked READMEs (NONE)

1. Agentora
2. phenotype-auth-ts
3. PlayCua
4. AuthKit
5. AgilePlus
6. FocalPoint
7. heliosCLI
8. phenoXdd
9. phenotype-infra
10. phenotype-tooling

## Recommendations

1. **Canonical badge block wave** — author a stack-aware `.tpl` (Rust/TS/Python/Go) producing License + CI + Release + Docs badges; PR sweep to all 30 repos.
2. **PARTIAL repos (8) — promote to OK:** add release badge (`shields.io/github/v/release` works without a published package) + docs badge (`docs.rs` for Rust libs, `pages` URL otherwise). Cheap edit, ~2 lines per README.
3. **NONE repos (22):** prioritize user-facing tools first — AgilePlus, FocalPoint, heliosCLI, AuthKit, PlayCua — these are the most repo-card-visible. Infra repos (phenotype-infra, phenotype-tooling, agent-devops-setups) lower priority.
4. **Release-badge gap (0/30) is the biggest signal-loss** — even unreleased repos benefit from `shields.io/github/v/release?include_prereleases` showing "no releases yet" honestly.

## Source

- Script: ad-hoc Bash + `gh api /repos/.../contents/README.md`
- Raw scores: `/tmp/badge-audit/scores.tsv` (ephemeral; regenerate from this doc's regexes)
- Generated: 2026-04-27
