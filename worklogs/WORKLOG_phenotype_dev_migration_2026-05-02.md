# phenotype.dev Domain Migration + Hygiene Audit — Cycle 2 (2026-05-02)

## phenotype.dev Migration (Canonical Repos)

### Committed & Pushed (Cycle 1 + Cycle 2)

| Repo | Files Fixed | Commit |
|------|-------------|--------|
| DataKit | SECURITY.md, pyproject.toml | 1d6269f |
| AuthKit | pyproject.toml (re-applied) | ddfd7ac |
| Httpora | pyproject.toml | 8e4afb0 |
| McpKit | pyproject.toml + 2 Cargo.toml | 583d743 |
| dispatch-mcp | pyproject.toml | db2d16494a |
| PhenoObservability | Cargo.toml | 5d55fb8 |
| ObservabilityKit | python/pyproject.toml | 933baae |
| libs/pheno_governance | pyproject.toml | f4154e13ba |
| libs/pheno_llm | pyproject.toml | 9bf2991a55 |
| PhenoProc | 16 pyproject.toml + SECURITY.md | 9cddec6 + 92525e5 |
| PhenoLang | pyproject.toml + SECURITY.md | cf9ed7e |
| phenotype-registry | README.md | 7c8e808 |
| Paginary | README.md + mkdocs.yml + library-research README | de5f900 + a4b2f20 |

### GitHub Homepage Fixes (via gh api)

| Repo | Action | Status |
|------|--------|--------|
| PhenoRuntime | cleared | ✓ |
| phenoShared | cleared | ✓ |
| phenotype-registry | cleared | ✓ |
| phenotype-infra | cleared | ✓ |
| PhenoMCP | cleared | ✓ |

### AuthKit-wtrees Worktrees (Committed & Pushed)

| Worktree | Commit |
|----------|--------|
| canonical-import-error-core | 050b1ef |
| cve-sweep-rsa-sqlx | 196c5a4 |
| feat/journey-impl | 030b396 |
| lockfile-retry | 28f1733 |
| phenotype-auth-fix | f83d913 |
| rand-workspace-dep | 8b19394 |
| rust-version-fix | 295d118 |
| trusted-publishing | 1d669ba |

### McpKit-wtrees (Committed & Pushed)
- sladge-badge: 971a6c7

## Hygiene Audit — Cycle 2

### Orphan Branch Cleanup (Deleted)
- DataKit: chore/ci-test-floor, chore/enable-dependabot
- AuthKit: refactor/rename-policy-engine, chore/add-reusable-workflows, chore/authkit-governance-docs-20260425, chore/enable-dependabot
- PhenoProc: chore/phenoproc-small-tail-20260426
- phenotype-journeys: chore/dead-code-phase1-phenotype-journeys
- PhenoSpecs: chore/enable-dependabot
- phenotype-bus: codex/license-apache-cleanup
- phenotype-tooling: codex/phenotype-tooling-docs-salvage, codex/pin-phenoshared-ci-2, fix-alert-sync-workflow-call
- phenotype-infra: bootstrap-governance, chore/iac-workspace-include-all-crates, feat/oci-lottery-daemon, feat/oci-lottery-invokes-post-acquire, feat/tailscale-governance, feat/tier3-path-microfrontends, chore/billing-blocked-rules-phenotype-dep-guard, chore/dependabot-cover-iac-cargo, feat/billing-rule-compensating-controls
- PhenoObservability: chore/add-reusable-workflows, chore/phenoobs-workspace-dedupe, fix/cargo-deny-private-deps
- ObservabilityKit: chore/rename-phenotype-health-runtime
- McpKit: chore/enable-dependabot

### phenotype-registry Hygiene (PR chain: chore/pin-github-actions-20260430)
- ✓ LICENSE (Apache 2.0)
- ✓ CODEOWNERS
- ✓ FUNDING.yml
- ✓ ISSUE_TEMPLATE (bug_report.yml + feature_request.yml)
- ✓ SECURITY.md (with phenotype.space security contact)
- ✓ PULL_REQUEST_TEMPLATE.md
- ✓ CONTRIBUTING.md
- ✓ CLAUDE.md (improved)
- ✓ .gitignore
- ✓ .editorconfig
- ✓ CITATION.cff

### Other Repos
- phenotype-infra: Apache 2.0 LICENSE (branch PR: chore/add-apache-license), FUNDING.yml, CITATION.cff, PR template
- phenotype-bus: .gitignore (pushed to main)
- PhenoHandbook: .gitignore (pushed to pin-actions-sha), CITATION.cff (pushed)
- phenotype-auth-ts: .editorconfig (pushed to main)
- phenotype-journeys: FUNDING.yml (pushed)
- PhenoSpecs: CODEOWNERS (pushed)

### Worktree Cleanup
- phenotype-tooling: pruned 2 temp worktrees (/private/tmp/phenotype-tooling-salvage.rleiVC, /private/tmp/phenotype-tooling-pin-ci)
- phenotype-infra: removed orphan worktree bootstrap-governance, pruned worktrees
- phenotype-infra-wtrees/bootstrap-governance: archived

## DEFERRED (No Replacement URL)

| Reference | Reason |
|-----------|--------|
| auth.phenotype.dev | AuthKit PRD/SPEC, PhenoHandbook, Paginary handbook |
| registry.phenotype.dev | archived spec docs |
| api.phenotype.dev | Paginary SOTA.md |
| sre.phenotype.dev | Paginary engineering SOTA |

## Infrastructure (Not Code)
- SSL 525 on: api.phenotype.space, dashboard.phenotype.space, registry.phenotype.space, auth.phenotype.space, pheno-mcp.phenotype.space, phenoshared.phenotype.space → Cloudflare cert setup needed

## Remaining Worktree Items (~206 markdown files)
- Mostly SPEC.md/PRD.md copies with auth.phenotype.dev design references
- Deferred until replacement URLs exist
