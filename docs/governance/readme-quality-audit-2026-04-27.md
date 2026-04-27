# README Quality Re-Audit — 2026-04-27

**Scope:** All non-archived, non-fork repos under `KooshaPari/*` (n=91).
**Method:** GitHub Contents API only (read-only). Per `feedback_readme_verify_then_write` — DO NOT auto-rewrite without verifying paths/commands/imports against actual repo contents.

## Scoring Rubric

- **CRITICAL:** README <500 bytes OR none of `## Install` / `## Usage` / `## Quick Start` / `## Getting Started` present.
- **WARN:** Has Install/Usage but no Quick-Start/Getting-Started entry path.
- **FORK-flagged:** Contains upstream markers (OpenAI Codex, Codex CLI, claude-code, "fork of", "forked from", "upstream:") AND first `#` heading does not contain the actual repo name (identity collision risk).

## Summary Counts

| Category | Count |
|----------|-------|
| OK | 61 |
| CRITICAL | 17 |
| WARN | 12 |
| FORK-flagged | 1 |
| **Total audited** | **91** |

## Top-5 Most Urgent (smallest, no entry path)

| Rank | Repo | Bytes | First Heading | Notes |
|------|------|-------|---------------|-------|
| 1 | `phenoResearchEngine` | 221 | `# phenotype-research-engine` | Stub. Identity-collision risk (heading != repo name). |
| 2 | `phenotype-auth-ts` | 572 | `# phenotype-auth-ts` | Near-empty; auth library — high consequence for missing usage. |
| 3 | `thegent-workspace` | 613 | `# TheGent Workspace` | Workspace landing should at least list members + entry. |
| 4 | `Parpoura` | 743 | `# parpour` | Stub + identity-collision (heading "parpour" != repo "Parpoura"). |
| 5 | `AgentMCP` | 1482 | `# AgentMCP` | Verified resolved earlier in session — re-check whether quick-start was actually added. |

## CRITICAL (17)

| Repo | Bytes | First Heading | Likely Cause |
|------|-------|---------------|--------------|
| AgentMCP | 1482 | # AgentMCP | No install/usage/QS/GS section |
| agileplus-landing | 1568 | # agileplus-landing | Landing page (intentional minimal? verify) |
| AuthKit | 1929 | # AuthKit | No entry path |
| byteport-landing | 6231 | # byteport-landing | Landing — verify intent |
| FocalPoint | 9338 | # FocalPoint | Has prose but no `## Install`/`## Usage` headings |
| hwledger-landing | 6231 | # hwledger-landing | Landing — verify intent |
| Parpoura | 743 | # parpour | Stub + identity collision |
| phenokits-landing | 6251 | # phenokits-landing | Landing — verify intent |
| PhenoMCP | 4442 | # PhenoMCP | No entry path. Recent PR #11 was flagged for fiction (`feedback_readme_verify_then_write`). Verify current state. |
| phenoResearchEngine | 221 | # phenotype-research-engine | Stub + identity collision |
| phenotype-auth-ts | 572 | # phenotype-auth-ts | Stub |
| phenotype-org-audits | 5971 | # phenotype-org-audits | Has prose, no entry path; may be intentional (audit repo) |
| phenotype-registry | 7850 | # Phenotype Registry System - Master Index | Index doc, may be intentional |
| projects-landing | 3229 | # projects-landing | Landing — verify intent |
| TestingKit | 4063 | # TestingKit | No entry path |
| thegent-landing | 5848 | # thegent-landing | Landing — verify intent |
| thegent-workspace | 613 | # TheGent Workspace | Stub |

**Note:** 6 of 17 CRITICAL are `*-landing` repos. These are likely intentional minimal microsites; treat as "verify intent, then either rewrite or whitelist" rather than auto-rewrite.

## WARN (12) — has some content, missing quick entry path

| Repo | Bytes | First Heading |
|------|-------|---------------|
| agent-devops-setups | 6317 | # Agent DevOps Setups |
| agent-user-status | 10028 | # Agent User Status |
| cheap-llm-mcp | 6875 | # cheap-llm-mcp |
| DevHex | 7203 | # DevHex |
| Eidolon | 7948 | # Eidolon |
| heliosBench | 2101 | # Helios Benchmark Harness |
| heliosCLI | 10484 | # heliosCLI |
| phenoData | 2287 | # PhenoData — Data Layer Workspace |
| phenotype-bus | 6609 | # phenotype-bus |
| phenotype-tooling | 4047 | # phenotype-tooling |
| PolicyStack | 14104 | # Policy scope stack for multi-harness AgentOps |
| thegent-dispatch | 1412 | # thegent-dispatch |

## FORK-flagged (1)

| Repo | Bytes | First Heading | Notes |
|------|-------|---------------|-------|
| PlayCua | 15273 | # bare-cua | First heading is "bare-cua" (upstream name). Per `feedback_fork_aware_readme`, this is **ADD-only** territory — preserve upstream README, prefix with `# PlayCua` preamble that documents the fork relationship. Do NOT rewrite. |

## Recommended Forward Plan (no auto-execution)

1. **Verify intent on `*-landing` repos** (6 critical): If intentional minimal microsite, add to a whitelist file and exclude from future audits. Otherwise, rewrite.
2. **Stub repos with identity collisions** (`phenoResearchEngine`, `Parpoura`): Decide canonical name first (rename repo or fix README heading), then write minimal install/usage from verified source paths.
3. **`PhenoMCP` re-verification:** PR #11 was flagged for fictional content. Diff current README against actual `pyproject.toml` / `Cargo.toml` / entrypoint before any further edit.
4. **`PlayCua` fork preamble:** Add `# PlayCua` block above existing `# bare-cua` content; never overwrite upstream body.
5. **WARN tier (12 repos):** Add `## Quick Start` or `## Getting Started` only after reading the actual entry point file for each — no template-fill from prompt.

## Provenance

- Generated: 2026-04-27
- Source: `gh repo list KooshaPari --no-archived --source` + `gh api repos/<r>/contents/README.md`
- Classifier: `/tmp/readme_audit/_categorized.tsv` (91 rows)
- Read-only audit; zero writes to any repo.
