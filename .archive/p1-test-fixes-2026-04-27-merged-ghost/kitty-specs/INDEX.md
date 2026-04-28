# AgilePlus Specification Index

Last Audit: 2026-04-25

## Status Overview

| Status | Count | Specs |
|--------|-------|-------|
| IN_PROGRESS | 19 | Active development / partial completion |
| DEFERRED | 15 | Future work, planned but not started |
| DONE | 3 | Completed and merged |
| OBSOLETE | 0 | Archived / superseded |

**Total Specs:** 37 | **UNKNOWN:** 0

---

## Core Platform (AgilePlus-001 to 003)

| Spec ID | Directory | Status | Created | Notes |
|---------|-----------|--------|---------|-------|
| AgilePlus-001 | `001-spec-driven-development-engine` | IN_PROGRESS | 2026-02-27 | Core 7-command CLI, MCP server, agent dispatch |
| AgilePlus-002 | `002-org-wide-release-governance-dx-automation` | IN_PROGRESS | 2026-03-01 | Release governance, SemVer, git-cliff, npm/PyPI/crates adapters |
| AgilePlus-003 | `003-agileplus-platform-completion` | DONE | 2026-03-10 | Infrastructure, sync, dashboard, multi-device. All 21 WPs merged. |

---

## Foundational Architecture (AgilePlus-004 to 022)

| Spec ID | Directory | Status | Created | Notes |
|---------|-----------|--------|---------|-------|
| AgilePlus-004 | `004-modules-and-cycles` | DEFERRED | 2026-03-15 | Module system, cycle detection |
| AgilePlus-008 | `008-temporal-deployment-workflow-migration` | DEFERRED | 2026-03-20 | Temporal integration for async workflows |
| AgilePlus-012 | `012-github-portfolio-triage` | DEFERRED | 2026-03-22 | GitHub Portfolio integration |
| AgilePlus-013 | `013-phenotype-infrakit-stabilization` | IN_PROGRESS | 2026-03-25 | Stabilize infrakit monorepo |
| AgilePlus-014 | `014-observability-stack-completion` | IN_PROGRESS | 2026-03-26 | Observability: Prometheus, Jaeger, metrics |
| AgilePlus-015 | `015-plugin-system-completion` | DEFERRED | 2026-03-27 | Plugin architecture completion |
| AgilePlus-016 | `016-agent-framework-expansion` | IN_PROGRESS | 2026-03-28 | Agent dispatch framework expansion |
| AgilePlus-017 | `017-cli-tools-consolidation` | DEFERRED | 2026-03-29 | CLI tooling consolidation |
| AgilePlus-018 | `018-template-repo-cleanup` | DEFERRED | 2026-03-30 | Template repository cleanup |
| AgilePlus-019 | `019-private-repo-catalog` | DEFERRED | 2026-04-01 | Private repository cataloging |
| AgilePlus-020 | `020-portfolio-and-web-apps` | DEFERRED | 2026-04-02 | Portfolio and web applications |
| AgilePlus-021 | `021-polyrepo-ecosystem-stabilization` | DEFERRED | 2026-04-03 | Polyrepo ecosystem stabilization |
| AgilePlus-022 | `022-batch13-repo-remediation` | DEFERRED | 2026-04-04 | Batch 13 repository remediation |

---

## Ecosystem Work (eco-001 to eco-012)

| Spec ID | Directory | Status | Created | Notes |
|---------|-----------|--------|---------|-------|
| AgilePlus-001 | `eco-001-worktree-remediation` | IN_PROGRESS | 2026-03-31 | Worktree cleanup and consolidation |
| AgilePlus-002 | `eco-002-branch-consolidation` | IN_PROGRESS | 2026-04-01 | Branch consolidation across repos |
| AgilePlus-003 | `eco-003-circular-dep-resolution` | IN_PROGRESS | 2026-04-02 | Resolve circular dependencies |
| AgilePlus-004 | `eco-004-hexagonal-migration` | IN_PROGRESS | 2026-04-03 | Hexagonal architecture migration |
| AgilePlus-005 | `eco-005-xdd-quality` | IN_PROGRESS | 2026-04-04 | XDD quality gates |
| AgilePlus-006 | `eco-006-governance-sync` | IN_PROGRESS | 2026-04-05 | Governance synchronization |
| AgilePlus-012 | `eco-012-orgops-capital-ledger` | DEFERRED | 2026-04-06 | OrgOps capital ledger |

---

## PhenoSDK Decomposition (phenosdk-*)

| Spec ID | Directory | Status | Notes |
|---------|-----------|--------|-------|
| AgilePlus-SDK-phenosdk-decompose-core | `phenosdk-decompose-core` | IN_PROGRESS | Core SDK decomposition |
| AgilePlus-SDK-phenosdk-decompose-llm | `phenosdk-decompose-llm` | IN_PROGRESS | LLM adapter extraction |
| AgilePlus-SDK-phenosdk-decompose-mcp | `phenosdk-decompose-mcp` | IN_PROGRESS | MCP protocol implementation |
| AgilePlus-SDK-phenosdk-fix-notimplemented | `phenosdk-fix-notimplemented` | DEFERRED | NotImplemented error cleanup |
| AgilePlus-SDK-phenosdk-sanitize-atoms | `phenosdk-sanitize-atoms` | DEFERRED | Atom sanitization |
| AgilePlus-SDK-phenosdk-wave-a-contracts | `phenosdk-wave-a-contracts` | IN_PROGRESS | Wave A contract definitions |

---

## Portfolio & Audit Work

| Spec ID | Directory | Status | Notes |
|---------|-----------|--------|-------|
| AgilePlus-portfolio-audit-kooshapari-2026 | `portfolio-audit-kooshapari-2026` | IN_PROGRESS | Portfolio audit and update |
| AgilePlus-kooshapari-stale-repo-triage | `kooshapari-stale-repo-triage` | IN_PROGRESS | Stale repo triage and archival |

---

## Infrastructure Work

| Spec ID | Directory | Status | Notes |
|---------|-----------|--------|-------|
| AgilePlus-oci-lottery-daemon | `oci-lottery-daemon` | DEFERRED | OCI lottery daemon |
| AgilePlus-oci-post-acquire-hooks | `oci-post-acquire-hooks` | DEFERRED | Post-acquire webhook handlers |
| AgilePlus-snyk-phase-1-deploy | `snyk-phase-1-deploy` | IN_PROGRESS | Snyk security scanning deployment |

---

## Consolidation & Templates

| Spec ID | Directory | Status | Notes |
|---------|-----------|--------|-------|
| AgilePlus-feature-specification-template-platform-completion | `feature-specification-template-platform-completion` | DONE | Spec template platform |
| AgilePlus-codeprojects-archive-manifest | `codeprojects-archive-manifest` | DONE | Archived projects manifest |
| AgilePlus-thegent-dotfiles-consolidation | `thegent-dotfiles-consolidation` | IN_PROGRESS | Thegent dotfiles consolidation |

---

## Legend

- **IN_PROGRESS**: Active development, partial completion, or planning phase. Has open work packages or recent commits.
- **DEFERRED**: Planned but not started. Defined in spec and plan, awaiting resources or blocked dependencies.
- **DONE**: Completed and merged to main. All work packages merged. Verified in git history.
- **OBSOLETE**: Archived or superseded. No longer relevant to active projects.

## Preamble Standard

All specs now include a YAML frontmatter preamble:

```yaml
---
spec_id: AgilePlus-NNN
status: <DONE | IN_PROGRESS | DEFERRED | OBSOLETE>
last_audit: 2026-04-25
---
```

This enables automated spec tracking, kanban board synchronization, and governance audits.
