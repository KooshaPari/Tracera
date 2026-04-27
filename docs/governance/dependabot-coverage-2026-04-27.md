# Dependabot vs Renovate Coverage Audit — 2026-04-27

**Scope:** All non-archived, non-fork repos under `KooshaPari/` (read-only API audit; no PRs).
**Method:** GitHub GraphQL one-shot probe of `.github/dependabot.{yml,yaml}`, `renovate.json`, `.renovaterc.json`, `.github/renovate.json`, `.renovaterc` per repo. Activity tier enriched with `defaultBranchRef.history.totalCount`.
**Source:** `gh api 'users/KooshaPari/repos?per_page=100' --paginate` filtered `archived=false, fork=false`.

## Headline

| Metric | Count |
|---|---|
| Total non-archived non-fork repos | **71** |
| Dependabot-covered | **48** (67.6%) |
| Renovate-covered | **0** (0.0%) |
| Both | 0 |
| **Missing both** | **23** (32.4%) |

> Note: every audited repo has `pushed_at` within the past 24h (org-wide push session 2026-04-26), so the `<30d` heuristic floods tier-1 indiscriminately. Tiering below uses **default-branch commit count** as the activity proxy. Star count = 0 for every repo (private-style portfolio).

## Dependabot-covered (48)

```
AgilePlus, Apisync, Benchora, BytePort, Conft, DataKit, DevHex, Dino, GDK,
HexaKit, McpKit, Metron, PhenoCompose, PhenoHandbook, PhenoKits, PhenoLang,
PhenoMCP, PhenoObservability, PhenoProc, PhenoRuntime, PhenoSpecs, PhenoVCS,
PolicyStack, Stashly, Tasken, Tokn, Tracera, agileplus-landing,
argis-extensions, byteport-landing, heliosApp, heliosCLI, hwLedger,
hwledger-landing, pheno, phenoAI, phenoData, phenoDesign, phenoShared,
phenoUtils, phenoXdd, phenodocs, phenokits-landing, phenotype-infra,
phenotype-tooling, projects-landing, thegent, thegent-landing
```

## Renovate-covered (0)

None. Renovate is unused org-wide.

## Missing both (23)

Tiered by `defaultBranchRef.history.totalCount` (active push burst masks pushed_at-based tiering).

### Tier-1 — Active (commits > 15)

| Repo | Lang | Commits |
|---|---|---|
| FocalPoint | Rust | 306 |
| agent-devops-setups | Python | 42 |
| AuthKit | Rust | 26 |
| PhenoPlugins | HTML | 25 |
| Httpora | — | 23 |
| PhenoDevOps | — | 21 |
| Agentora | Rust | 20 |
| phenotype-auth-ts | TypeScript | 17 |
| PlayCua | Rust | 17 |

### Tier-2 — Emerging (commits 10–15)

| Repo | Lang | Commits |
|---|---|---|
| ObservabilityKit | Rust | 15 |
| PhenoAgent | Rust | 15 |
| PhenoProject | TypeScript | 15 |
| TestingKit | Python | 14 |
| ResilienceKit | Python | 13 |
| eyetracker | Kotlin | 11 |
| PlatformKit | Go | 10 |
| vibeproxy-monitoring-unified | — | 10 |

### Tier-3 — Nascent (commits < 10)

| Repo | Lang | Commits |
|---|---|---|
| phenotype-registry | — | 9 |
| AgentMCP | — | 8 |
| dinoforge-packs | Go | 8 |
| heliosBench | Python | 8 |
| phenotype-hub | — | 8 |
| nanovms | Go | 3 |

## Recommended Top-10 Bootstrap

Ordered by commit volume × language criticality (Rust/TS/Python/Go cores first, niche langs last):

1. **FocalPoint** (Rust, 306 commits) — highest-velocity uncovered repo; canonical disk-budget tooling
2. **agent-devops-setups** (Python, 42) — Python deps drift fast
3. **AuthKit** (Rust, 26) — security surface
4. **Httpora** (23) — runtime networking
5. **Agentora** (Rust, 20) — agent framework
6. **PhenoPlugins** (HTML/JS, 25) — JS supply chain
7. **PhenoDevOps** (21) — infra tooling
8. **phenotype-auth-ts** (TS, 17) — TS auth surface
9. **PlayCua** (Rust, 17) — agent CUA
10. **ObservabilityKit** (Rust, 15) — observability core

## Reuse note

48 existing `.github/dependabot.yml` configs are sources of truth — clone the most representative (e.g. `AgilePlus`, `FocalPoint` if it gets one, `thegent`) into the 23 gaps via centralized template rather than per-repo authoring. Renovate adoption (0/71) is not a gap — it is a deliberate single-tool stance. Do not introduce Renovate alongside Dependabot.

## Artifacts

- Raw probe (GraphQL): `/tmp/gql_resp.json`
- Enriched missing list: `/tmp/missing_enriched.json`
- Aggregated JSON: `/tmp/agg.json`
