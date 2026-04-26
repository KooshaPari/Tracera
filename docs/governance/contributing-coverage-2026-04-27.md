# CONTRIBUTING.md Coverage Audit — 2026-04-27

**Method:** GitHub Contents API only (`repos/KooshaPari/<repo>/contents/CONTRIBUTING.md`, fallback `.github/CONTRIBUTING.md`).
**Scope:** 71 non-archived, non-fork repos owned by `KooshaPari`.

## Summary

| Category | Count | % | Threshold (bytes) |
|----------|------:|--:|-------------------|
| MISSING  | 32    | 45.1% | 404 / not present |
| STUB     | 13    | 18.3% | < 300 |
| SHORT    | 14    | 19.7% | 300 – 999 |
| GOOD     | 12    | 16.9% | >= 1000 |

Combined "needs work" (MISSING + STUB): **45 / 71 (63.4%)**.

## MISSING (32)

AgentMCP, Agentora, agileplus-landing, AuthKit, Benchora, byteport-landing, DevHex, dinoforge-packs, eyetracker, heliosBench, hwledger-landing, ObservabilityKit, PhenoAgent, PhenoDevOps, phenodocs, PhenoHandbook, phenokits-landing, PhenoMCP, PhenoObservability, PhenoPlugins, PhenoProject, PhenoSpecs, phenotype-auth-ts, phenotype-hub, phenotype-registry, PlatformKit, PlayCua, projects-landing, ResilienceKit, TestingKit, thegent-landing, vibeproxy-monitoring-unified.

## STUB (<300 bytes, 13)

| Repo | Bytes |
|------|------:|
| Apisync | 184 |
| argis-extensions | 184 |
| Httpora | 184 |
| PolicyStack | 184 |
| Stashly | 184 |
| Tasken | 184 |
| Tokn | 184 |
| agent-devops-setups | 288 |
| AgilePlus | 288 |
| heliosApp | 288 |
| HexaKit | 288 |
| pheno | 288 |
| PhenoLang | 288 |

The repeated 184/288 sizes strongly suggest two boilerplate templates copy-pasted across these repos.

## SHORT (300–999 bytes, 14)

heliosCLI (400), Conft (461), phenotype-tooling (664), Metron (773), phenoAI (774), phenoData (776), phenoUtils (777), hwLedger (810), PhenoProc (812), phenoDesign (839), DataKit (870), phenotype-infra (876), McpKit (956), BytePort (959).

## GOOD (>=1000 bytes, 12)

PhenoKits (1095), GDK (1141), phenoShared (1189), PhenoVCS (1227), phenoXdd (1227), PhenoRuntime (1231), thegent (1291), nanovms (1431), PhenoCompose (1431), Tracera (2123), FocalPoint (8093), Dino (22469).

## Top-10 MISSING (priority for templating)

Prioritized by ecosystem centrality:

1. AuthKit
2. ObservabilityKit
3. PlatformKit
4. ResilienceKit
5. TestingKit
6. PhenoMCP
7. PhenoObservability
8. PhenoPlugins
9. PhenoAgent
10. PhenoDevOps

(landing/docs sub-repos and `phenotype-hub`/`phenotype-registry` follow as a second wave.)

## Recommendation

Roll out a single canonical CONTRIBUTING.md template (>=1000 bytes, with PR/issue process, AgilePlus-spec mandate, quality-gate expectations) to all 45 MISSING+STUB repos. The 184/288-byte clustering indicates current stubs are placeholder boilerplate, not authored content.
