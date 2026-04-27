# CodeQL Coverage Audit — 2026-04-27

**Scope:** non-archived, non-fork public repos under `KooshaPari` org/user.
**Method:** GitHub API, read-only. For each repo: probe `.github/workflows/codeql*.y(a)ml`, latest `code-scanning/analyses?tool_name=CodeQL`, open `code-scanning/alerts?tool_name=CodeQL`.
**Total repos audited:** 71 (`/tmp/ko_repos.txt` minus 1 API artifact row).

## Categories

| Category | Count | Definition |
|---|---|---|
| WORKFLOW_RECENT | 29 | `codeql.yml` present AND latest CodeQL analysis < 30 days |
| DEFAULT_SETUP_RECENT | 5 | No workflow file but CodeQL analysis < 30 days (GitHub default setup) |
| WORKFLOW_STALE | 0 | — |
| DEFAULT_SETUP_STALE | 0 | — |
| NO_CODEQL | 37 | No workflow, no CodeQL analysis ever |

**Coverage:** 34/71 = **47.9%** of public non-archived repos have an active CodeQL signal (recent run, < 30 days). All active runs are within the last 3 days (2026-04-24 → 2026-04-26).

## WORKFLOW_RECENT (29)

AgilePlus, AuthKit, Benchora, BytePort, DataKit, DevHex, Dino, GDK, HexaKit, Httpora, hwLedger, McpKit, Metron, pheno, phenoAI, PhenoCompose, phenoData, phenodocs, PhenoKits, PhenoLang, PhenoProc, PhenoRuntime, phenoShared, PhenoSpecs, phenotype-auth-ts, phenotype-hub, Tokn, Tracera, vibeproxy-monitoring-unified

## DEFAULT_SETUP_RECENT (5)

GitHub-hosted "default setup" — no checked-in workflow but CodeQL analyses present:

heliosCLI, PhenoObservability, PhenoPlugins, ResilienceKit, thegent

## NO_CODEQL (37) — gap candidates

agent-devops-setups, AgentMCP, Agentora, agileplus-landing, Apisync, argis-extensions, byteport-landing, Conft, dinoforge-packs, eyetracker, FocalPoint, heliosApp, heliosBench, hwledger-landing, nanovms, ObservabilityKit, PhenoAgent, phenoDesign, PhenoDevOps, PhenoHandbook, phenokits-landing, PhenoMCP, PhenoProject, phenotype-infra, phenotype-registry, phenotype-tooling, phenoUtils, PhenoVCS, phenoXdd, PlatformKit, PlayCua, PolicyStack, projects-landing, Stashly, Tasken, TestingKit, thegent-landing

## Top 10 by open CodeQL alerts

| Rank | Repo | Open alerts |
|---|---|---|
| 1 | thegent | 100 |
| 2 | AgilePlus | 33 |
| 3 | PhenoProc | 25 |
| 4 | hwLedger | 8 |
| 5 | PhenoObservability | 5 |
| 5 | PhenoKits | 5 |
| 5 | McpKit | 5 |
| 5 | BytePort | 5 |
| 9 | phenoData | 4 |
| 10 | PhenoCompose | 3 |

(Note: alert query was capped at `per_page=100`, so `thegent` may be ≥100.)

## Findings

- **No "stale" CodeQL repos.** Every workflow-bearing repo has run CodeQL within the last 3 days, despite the GitHub Actions billing block. CodeQL analyses appear to be running (likely default-setup billing path differs from custom workflow billing, or runs predate billing exhaustion this cycle).
- **47.9% adoption.** Roughly half the surface area has an active CodeQL signal.
- **Adoption gaps cluster in 3 buckets:** (a) landing-page sites (`*-landing` ×6 — low value), (b) infra/tooling repos (`phenotype-infra`, `phenotype-registry`, `phenotype-tooling`, `agent-devops-setups`, `nanovms`), (c) substantive product repos missing CodeQL: **FocalPoint, heliosApp, PhenoMCP, PhenoVCS, PolicyStack, PlatformKit, PhenoAgent, PhenoDevOps, Conft, Tasken, Stashly, TestingKit, ObservabilityKit, phenoUtils, phenoXdd, AgentMCP, Agentora, eyetracker, Apisync, phenoDesign, Benchora-style code repos**. These should adopt either the standard `codeql.yml` or GitHub default setup.
- **Highest backlog:** `thegent` (≥100), `AgilePlus` (33), `PhenoProc` (25). Prioritize triage.

## Recommendations (no actions taken — read-only audit)

1. **Enable CodeQL default setup** on the 37 NO_CODEQL repos via `gh api repos/KooshaPari/<r>/code-scanning/default-setup -X PATCH -f state=configured`. Free tier covers public repos; default setup avoids custom-workflow billing concerns.
2. **Skip landing pages** (`*-landing`, `projects-landing`) and `phenotype-infra`/`phenotype-registry` if they're config-only.
3. **Triage top-3 alert backlogs** (thegent 100+, AgilePlus 33, PhenoProc 25) — separate effort tracked in `agileplus-codeql-triage-2026-04-27.md` (already exists for AgilePlus).
4. **Reconcile `WORKFLOW_RECENT` repos with codeql.yml** — confirm whether any are using paid runners; switch to `ubuntu-latest` if so per the billing constraint.

## Raw data

- `/tmp/ko_repos.txt` — repo list (72 lines incl. 1 stray)
- `/tmp/codeql_final.tsv` — repo, workflow, latest CodeQL ts, open alerts
- `/tmp/codeql_final_cat.tsv` — same with category column
