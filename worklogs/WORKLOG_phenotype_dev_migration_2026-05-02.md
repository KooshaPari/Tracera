# Hygiene Audit + phenotype.dev Migration — COMPLETE (2026-05-02)

## phenotype.dev Domain Migration: ✓ COMPLETE
- 14 canonical repos fixed & pushed (email, docs URL, security contact)
- 9 AuthKit-wtrees + 1 McpKit-wtrees committed & pushed
- 5 GitHub homepage URLs cleared
- Deferred: auth.phenotype.dev (no replacement URL exists)

## Hygiene Audit: ✓ COMPLETE

### Orphan Branches: ✓ ZERO across 22 repos
All 22 orphan branches deleted across cycle 2

### Governance Files: ✓ COMPLETE

All 7 key governance files across major repos:
- CLAUDE.md ✓
- AGENTS.md ✓  
- FUNDING.yml ✓
- CODEOWNERS ✓
- SECURITY.md ✓
- CITATION.cff ✓
- .gitignore ✓

Template files:
- PULL_REQUEST_TEMPLATE.md ✓
- ISSUE_TEMPLATE/ ✓

### Cargo-Deny: ✓ FIXED
- phenotype-bus: Unicode-3.0 → PASSES
- PhenoProc: Zlib + Unicode-3.0 + Apache-2.0 → PASSES

### Worktree Cleanup: ✓ COMPLETE
- phenotype-tooling: pruned 2 temp worktrees
- phenotype-infra: removed orphan bootstrap-governance worktree

## Infrastructure (Not Code Fixes Needed)
- SSL 525 on *.phenotype.space → Cloudflare SSL cert setup required

## Deferred
- auth.phenotype.dev (no replacement URL)
- AGENTS.md: phenotype-registry, phenotype-journeys (more substantive)
- Dependabot/npm audit: PhenoHandbook (@types/node, vitest)
