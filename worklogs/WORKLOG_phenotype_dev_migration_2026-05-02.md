# phenotype.dev Domain Migration - Worklog Update 2026-05-02

## Status: IN PROGRESS - Major work done, remaining deferred

## Canonical Repo Fixes (Committed)

| Repo | Files Fixed | Commit |
|------|-------------|--------|
| DataKit | SECURITY.md, pyproject.toml | 1d6269f |
| AuthKit | pyproject.toml (re-applied) | ddfd7ac re-commit |
| BytePort | SECURITY.md | 8d950d27 |
| KDesktopVirt | SECURITY.md | 8b76aea |
| Httpora | pyproject.toml | 8e4afb0 |
| McpKit | pyproject.toml + 2 Cargo.toml (re-applied) | 583d743 re-commit |
| dispatch-mcp | pyproject.toml | db2d16494a |
| PhenoObservability | Cargo.toml | 5d55fb8 |
| ObservabilityKit | python/pyproject.toml | 933baae |
| libs/pheno_governance | pyproject.toml | f4154e13ba |
| libs/pheno_llm | pyproject.toml | 9bf2991a55 |
| PhenoProc | 16 pyproject.toml + SECURITY.md | 9cddec6 + 92525e5 |
| PhenoLang | pyproject.toml + SECURITY.md | cf9ed7e |
| phenotype-registry | README.md | 7c8e808 |
| Paginary | README.md + mkdocs.yml | de5f900 |

## GitHub Homepage Fixes (via gh api -X PATCH)

- PhenoRuntime: cleared
- phenoShared: cleared
- phenotype-registry: cleared
- phenotype-infra: cleared
- PhenoMCP: cleared (via -F flag)

## DEFERRED (No Replacement URL Exists)

| Reference | Files | Reason |
|-----------|-------|--------|
| auth.phenotype.dev | AuthKit/docs/PRD.md, SPEC.md; PhenoHandbook, Paginary handbook |
| registry.phenotype.dev | .archive/pheno/PRD.md, SPEC.md, SOTA.md |
| auth.phenotype.dev issuer | Paginary SOTA.md, oauth-pkce.md |
| api.phenotype.dev | Paginary SOTA.md |
| sre.phenotype.dev | Paginary engineering SOTA |

## Deferred Categories (Cosmetic, Not Broken)

- Backstage catalog-info.yaml annotations (phenotype.dev/registry-type)
- JSON schema $id fields
- Author email addresses in archived/locked files
- SPEC.md/PRD.md design documents referencing hypothetical URLs

## Worktrees Remaining

- ~206 markdown files across worktrees with phenotype.dev references (mostly SPEC.md, PRD.md, worklog copies)
- ~9 AuthKit-wtrees pyproject.toml files fixed but may need commit
- McpKit-wtrees sladge-badge pyproject.toml fixed

## GitHub Homepage Fixes Needed

- PhenoMCP: verified cleared

## Infrastructure (Not Code)

- SSL 525 on: api.phenotype.space, dashboard.phenotype.space, registry.phenotype.space, auth.phenotype.space, pheno-mcp.phenotype.space, phenoshared.phenotype.space → Cloudflare cert setup needed

## Next Steps

1. Commit AuthKit-wtrees and McpKit-wtrees pyproject.toml fixes
2. Fix remaining Paginary markdown files with clear URL refs
3. Sweep worktree SPEC.md files for URL references (defer if auth/registry)
4. Push all canonical commits to origin
