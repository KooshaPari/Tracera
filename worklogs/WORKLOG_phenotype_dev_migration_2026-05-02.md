# phenotype.dev Domain Migration + Hygiene Audit — Cycle 3 (2026-05-02)

## phenotype.dev Migration (Completed)
- 14 canonical repos fixed, committed & pushed
- 9 AuthKit-wtrees worktrees committed & pushed
- 1 McpKit-wtrees worktree committed & pushed
- 5 GitHub homepage URLs cleared
- Deferred: auth.phenotype.dev (no replacement URL)

## Hygiene Audit — Cycle 3

### Orphan Branch Cleanup
- 22 orphan branches deleted across 10 repos (cycle 2)
- All repos: ZERO orphan branches remaining

### Full Hygiene Sweep Results

#### Repos with Complete Hygiene (10/10)
- DataKit, BytePort, KDesktopVirt, Httpora, McpKit, PhenoObservability, ObservabilityKit, PhenoLang, HexaKit, PhenoSpecs

#### Repos with 9/10
- PhenoProc: Missing CITATION.cff
- phenotype-infra: Missing CITATION.cff (branch PR: chore/add-apache-license)
- phenotype-journeys: Complete

#### Repos with 8/10
- PhenoHandbook: Missing AGENTS.md, CONTRIBUTING.md
- phenotype-bus: Missing AGENTS.md, CONTRIBUTING.md
- phenotype-tooling: Missing AGENTS.md, CONTRIBUTING.md
- phenotype-auth-ts: Missing AGENTS.md, CONTRIBUTING.md

#### New Repos (bootstrap complete)
- phenotype-registry: CLAUDE, CODEOWNERS, FUNDING, ISSUE_TEMPLATE, SECURITY, PR_TEMPLATE, CONTRIBUTING, .gitignore, .editorconfig, CITATION, LICENSE
- dispatch-mcp: CLAUDE, CODEOWNERS, FUNDING, ISSUE_TEMPLATE, SECURITY, PR_TEMPLATE, CONTRIBUTING, .gitignore, CITATION
- phenotype-org-governance: FUNDING, CODEOWNERS, CITATION

#### Tracera
- FUNDING.yml, CODEOWNERS, SECURITY.md, CITATION.cff

#### Paginary
- FUNDING.yml, .gitignore

## Cargo-Deny Fixes
- phenotype-bus: added Unicode-3.0 → **PASSES**
- PhenoProc: added Zlib/Unicode-3.0 + Apache-2.0 to pheno-proc-uds → **licenses PASS** (bans: wildcard warnings non-blocking)

## Worktree Cleanup
- phenotype-tooling: pruned 2 temp worktrees
- phenotype-infra: removed orphan bootstrap-governance worktree
- phenotype-infra-wtrees/bootstrap-governance: archived

## Infrastructure (Not Code)
- SSL 525 on `*.phenotype.space` → Cloudflare cert setup needed

## Deferred
- auth.phenotype.dev (no replacement URL)
- ~206 worktree markdown files (SPEC/PRD copies with auth.phenotype.dev refs)
