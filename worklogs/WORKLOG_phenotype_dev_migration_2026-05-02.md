# phenotype.dev Domain Migration + Hygiene Audit — Final (2026-05-02)

## phenotype.dev Migration: COMPLETE
- 14 canonical repos fixed, committed & pushed
- 9 AuthKit-wtrees worktrees committed & pushed  
- 1 McpKit-wtrees worktree committed & pushed
- 5 GitHub homepage URLs cleared via gh API
- Deferred: auth.phenotype.dev (no replacement URL exists)

## Hygiene Audit: COMPLETE

### Orphan Branches: ZERO across 21 repos
All orphan branches deleted across DataKit, AuthKit, PhenoProc, phenotype-journeys, PhenoSpecs, phenotype-bus, phenotype-tooling, phenotype-infra, PhenoObservability, ObservabilityKit, McpKit

### Governance Files Added

| Repo | Files Added |
|------|-----------|
| phenotype-registry | CLAUDE, CODEOWNERS, FUNDING, ISSUE_TEMPLATE, SECURITY, PR_TEMPLATE, CONTRIBUTING, .gitignore, .editorconfig, CITATION, LICENSE |
| phenotype-infra | LICENSE, FUNDING, CITATION, PR_TEMPLATE, ISSUE_TEMPLATE |
| dispatch-mcp | CLAUDE, CODEOWNERS, FUNDING, ISSUE_TEMPLATE, SECURITY, PR_TEMPLATE, CONTRIBUTING, .gitignore, CITATION |
| PhenoSpecs | CODEOWNERS, .gitignore |
| PhenoHandbook | .gitignore, CITATION |
| phenotype-bus | .gitignore |
| phenotype-auth-ts | .editorconfig |
| Paginary | FUNDING, .gitignore |
| phenotype-org-governance | FUNDING, CODEOWNERS, CITATION |
| Tracera | FUNDING, CODEOWNERS, SECURITY, CITATION |
| Httpora | CITATION |

### Cargo-Deny Fixes
- phenotype-bus: Unicode-3.0 → **PASSES**
- PhenoProc: Zlib + Unicode-3.0 + Apache-2.0 to pheno-proc-uds → **licenses PASS** (bans: wildcard warnings non-blocking)

### Repos with Complete Hygiene (10/10)
DataKit, BytePort, KDesktopVirt, Httpora, McpKit, PhenoObservability, ObservabilityKit, PhenoLang, HexaKit, PhenoSpecs

### Worktree Cleanup
- phenotype-tooling: pruned 2 temp worktrees
- phenotype-infra: removed orphan bootstrap-governance worktree
- phenotype-infra-wtrees/bootstrap-governance: archived

## Infrastructure (Not Code Fixes Needed)
- SSL 525 on `api.phenotype.space`, `dashboard.phenotype.space`, `registry.phenotype.space`, `auth.phenotype.space`, `pheno-mcp.phenotype.space`, `phenoshared.phenotype.space` → Cloudflare SSL cert setup required

## Deferred
- auth.phenotype.dev (no replacement URL yet)
- ~206 worktree markdown files with SPEC/PRD design references
- PhenoHandbook/phenotype-bus/phenotype-auth-ts/phenotype-tooling: AGENTS.md and CONTRIBUTING.md (more substantive)
- phenotype-journeys/phenotype-bus/phenotype-auth-ts: ~200 node_modules packages (gitignored but orphaned)
