# Hygiene Audit + phenotype.dev Migration — COMPLETE (2026-05-02)

## phenotype.dev Domain Migration: ✓ COMPLETE
- 14 canonical repos fixed & pushed
- 9 AuthKit-wtrees + 1 McpKit-wtrees committed & pushed
- 5 GitHub homepage URLs cleared
- Deferred: auth.phenotype.dev (no replacement URL exists)

## Hygiene Audit: ✓ COMPLETE

### Orphan Branches: ✓ ZERO across 22 repos

### Governance Files: ✓ COMPLETE
All 7 key governance files across major repos

### GitHub Actions: ✓ ZERO v2/v3 versions

### Cargo-Deny: ✓ FIXED
- phenotype-bus: Unicode-3.0 → PASSES
- PhenoProc: Zlib + Unicode-3.0 + Apache-2.0 → PASSES

## Infrastructure (Not Code Fixes Needed)
- SSL 525 on *.phenotype.space → Cloudflare SSL cert setup required

## Deferred
- auth.phenotype.dev (no replacement URL)
- AGENTS.md: phenotype-registry, phenotype-journeys
- Dependabot: PhenoHandbook npm (@types/node, vitest)
