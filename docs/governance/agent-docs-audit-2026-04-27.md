# Agent Instruction Docs Audit — KooshaPari org

**Date:** 2026-04-27  
**Method:** GitHub REST API contents probe (read-only)  
**Scope:** 71 non-archived non-fork repos owned by KooshaPari  

## Distribution

| Category | Count | % |
|----------|-------|---|
| BOTH (CLAUDE.md + AGENTS.md) | 46 | 64% |
| CLAUDE_ONLY | 4 | 5% |
| AGENTS_ONLY | 9 | 12% |
| NONE | 12 | 16% |

## NONE — repos lacking any agent doc

Sorted by recent push activity. `*-landing` are static marketing pages (acceptable).

| Repo | Last Push | Notes |
|------|-----------|-------|
| AgentMCP | recent | ACTIVE code repo — needs CLAUDE.md |
| TestingKit | recent | ACTIVE code repo — needs CLAUDE.md |
| eyetracker | recent | ACTIVE code repo — needs CLAUDE.md |
| heliosBench | recent | ACTIVE code repo — needs CLAUDE.md |
| phenotype-registry | recent | ACTIVE infra — needs CLAUDE.md |
| Conft | recent | ACTIVE code repo — needs CLAUDE.md |
| byteport-landing | recent | landing site (low priority) |
| agileplus-landing | recent | landing site (low priority) |
| hwledger-landing | recent | landing site (low priority) |
| phenokits-landing | recent | landing site (low priority) |
| projects-landing | recent | landing site (low priority) |
| thegent-landing | recent | landing site (low priority) |

## CLAUDE_ONLY (4)

- AgilePlus
- phenotype-auth-ts
- phenotype-tooling
- phenoXdd

## AGENTS_ONLY (9)

- Agentora
- Benchora
- hwLedger
- McpKit
- phenoData
- PhenoMCP
- PhenoProc
- PhenoSpecs
- PlatformKit

## BOTH (46)

- AuthKit
- BytePort
- Apisync
- argis-extensions
- agent-devops-setups
- DataKit
- DevHex
- dinoforge-packs
- FocalPoint
- Dino
- heliosApp
- GDK
- heliosCLI
- Httpora
- HexaKit
- Metron
- pheno
- nanovms
- PhenoAgent
- ObservabilityKit
- phenoAI
- PhenoCompose
- phenoDesign
- PhenoDevOps
- phenodocs
- PhenoKits
- PhenoObservability
- PhenoLang
- PhenoPlugins
- PhenoHandbook
- PhenoProject
- PhenoRuntime
- phenoShared
- phenotype-infra
- phenotype-hub
- PhenoVCS
- phenoUtils
- PlayCua
- ResilienceKit
- PolicyStack
- Stashly
- thegent
- Tasken
- vibeproxy-monitoring-unified
- Tokn
- Tracera

## Stub Detection

Probed first 50 bytes of every present file. **No stubs detected** — all CLAUDE.md/AGENTS.md files exceed 100 bytes (no 1-byte placeholder drift).

## Top-5 active code repos with NONE

1. **AgentMCP** — pushed 2026-04-26 22:06Z (active code, no docs)

2. **TestingKit** — pushed 2026-04-26 21:59Z (active code, no docs)

3. **eyetracker** — pushed 2026-04-26 21:50Z (active code, no docs)

4. **heliosBench** — pushed 2026-04-26 21:50Z (active code, no docs)

5. **Conft** — pushed 2026-04-26 16:45Z (active code, no docs)


## Constraints

Read-only audit. No PRs opened. Source: `gh api repos/KooshaPari/{repo}/contents/{path}`.

