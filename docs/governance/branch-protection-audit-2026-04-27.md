# Branch Protection Audit — 2026-04-27

Audit of branch protection on default branch (`main`) across **non-archived, non-fork** KooshaPari repos.

**Method:** `gh api repos/<r>/branches/<default>/protection` (404 → check `/rulesets` for ruleset coverage).

## Summary

| Status | Count | Share |
|---|---|---|
| **UNPROTECTED** | 62 | 87.3% |
| **RULESET** | 8 | 11.3% |
| **CLASSIC** | 1 | 1.4% |
| **Total** | 71 | 100% |

## CLASSIC Branch Protection (1)

Repos using legacy branch protection API:

| Repo | Branch | enforce_admins | required_reviews | restrictions | Notes |
|---|---|---|---|---|---|
| heliosApp | main | false | none | none | Protection record exists but all fields empty/unset (effectively unprotected — only blocks force-push and deletion) |

## RULESET Coverage (8)

Repos using repository rulesets (modern API):

| Repo | Rulesets | Names |
|---|---|---|
| agent-devops-setups | 1 | Main Governance Baseline |
| AgilePlus | 1 | Main Governance Baseline |
| BytePort | 1 | Main |
| heliosBench | 2 | Main, Mainm (typo — likely orphan duplicate) |
| heliosCLI | 1 | Main |
| phenoShared | 1 | Main Governance Baseline |
| thegent | 1 | Main |
| Tracera | 1 | Main |

All rulesets: `enforcement=active`, `target=branch`, `conditions=null` (applies to default-branch context).

## UNPROTECTED Repos (62)

No branch protection AND no repository rulesets:

- AgentMCP
- Agentora
- agileplus-landing
- Apisync
- argis-extensions
- AuthKit
- Benchora
- byteport-landing
- Conft
- DataKit
- DevHex
- Dino
- dinoforge-packs
- eyetracker
- FocalPoint
- GDK
- HexaKit
- Httpora
- hwLedger
- hwledger-landing
- McpKit
- Metron
- nanovms
- ObservabilityKit
- pheno
- PhenoAgent
- phenoAI
- PhenoCompose
- phenoData
- phenoDesign
- PhenoDevOps
- phenodocs
- PhenoHandbook
- PhenoKits
- phenokits-landing
- PhenoLang
- PhenoMCP
- PhenoObservability
- PhenoPlugins
- PhenoProc
- PhenoProject
- PhenoRuntime
- PhenoSpecs
- phenotype-auth-ts
- phenotype-hub
- phenotype-infra
- phenotype-registry
- phenotype-tooling
- phenoUtils
- PhenoVCS
- phenoXdd
- PlatformKit
- PlayCua
- PolicyStack
- projects-landing
- ResilienceKit
- Stashly
- Tasken
- TestingKit
- thegent-landing
- Tokn
- vibeproxy-monitoring-unified

## High-Priority Unprotected (active core repos)

Top candidates for ruleset rollout — high-activity core/infra repos:

1. **thegent-landing** — public-facing landing for thegent
2. **PhenoMCP** — MCP integration core
3. **PhenoRuntime** — runtime substrate
4. **PhenoLang** — language tooling
5. **FocalPoint** — disk-pruner/tooling, governance-critical
6. **PhenoObservability** / **PhenoPlugins** / **phenotype-hub** / **phenotype-infra** — infra & observability
7. **heliosApp** (CLASSIC but effectively empty — migrate to ruleset)

## Recommendations

1. **Migrate `heliosApp` from CLASSIC to RULESET** to match the rest of the helios family pattern; current classic config has no enforcements and is effectively no-op.
2. **Apply "Main Governance Baseline" ruleset to all Pheno* core repos** (PhenoMCP, PhenoRuntime, PhenoLang, PhenoObservability, PhenoPlugins, PhenoVCS, PhenoProject, PhenoAgent, PhenoCompose, PhenoProc, PhenoKits, PhenoSpecs, PhenoDevOps, PhenoHandbook). 14 repos.
3. **Apply "Main" ruleset to phenotype-* infra repos** (phenotype-hub, phenotype-infra, phenotype-registry, phenotype-tooling, phenotype-auth-ts, phenoUtils, phenoXdd). 7 repos.
4. **Clean up `heliosBench` ruleset** — drop typo'd "Mainm" duplicate.
5. **Landing pages** (agileplus-landing, byteport-landing, hwledger-landing, phenokits-landing, projects-landing, thegent-landing): low-risk; either apply minimal ruleset or accept as unprotected static-site hosts.
6. **Verify post-billing-block restoration:** memory entry `reference_billing_blocked_rules.md` notes 5 rulesets dropped 2026-04-25; this audit confirms only 8 rulesets remain across 71 repos. Restore script is in phenotype-infra/iac per memory.

## Raw Data

Snapshot TSV: `.audit-tmp/final3.tsv` (`name	branch	status	rulesets	admins	reviews	restr	stars`).

_Generated 2026-04-27 via `gh api` read-only probe; 71 non-archived non-fork repos surveyed._
