# Governance Documentation Index

This directory contains governance policies, audit reports, investigation findings, and decision records for the Phenotype organization.

---

## 2026-04-26 Session: Cross-Repo Audit & User-Story Verification

**Summary:** Comprehensive audit session covering archive state validation, consumer dependencies, phantom submodule detection, and 25+ user-story walkthroughs across Kit repos and major systems.

### User-Story & Code Walkthroughs (25 docs)

Detailed verification and README accuracy checks for Kit-pattern repos, MCP projects, and miscellaneous systems:

- [Kit-Pattern Repos Re-Verification](./userstory-kits-reverify-2026-04-26.md) — ResilienceKit, ObservabilityKit, SecurityKit phantom gitlinks & README audit
- [Kit-Pattern Repos Batch 2](./userstory-kits-reverify-batch2-2026-04-26.md) — ArchitectureKit, DataKit, PerformanceKit walkthroughs
- [MCP Code & Requirements Reverify](./userstory-mcp-reverify-2026-04-26.md) — claude-ai-cheap-llm MCP, thegent-dispatch code structure
- [Tier 1 Repos Reverify](./userstory-tier1-reverify-2026-04-26.md) — AgilePlus, phenotype-infrakit, heliosCLI, Portalis
- [Tier 2 Repos Reverify](./userstory-tier2-reverify-2026-04-26.md) — thegent, PhenoKits, policy-stack, other secondary systems
- [Misc Batch 4 (First-Run Verification)](./userstory-misc-batch4-firstrun-2026-04-26.md) — Batch 4 assorted repos
- [Misc Batch 6 (First-Run Verification)](./userstory-misc-batch6-firstrun-2026-04-26.md) — Batch 6 assorted repos
- [Misc Batch 7 (First-Run Verification)](./userstory-misc-batch7-firstrun-2026-04-26.md) — Batch 7 assorted repos
- [Misc Batch 8 (First-Run Verification)](./userstory-misc-batch8-firstrun-2026-04-26.md) — Batch 8 assorted repos
- [Misc Batch 9 (First-Run Verification)](./userstory-misc-batch9-firstrun-2026-04-26.md) — Batch 9 assorted repos
- [Misc Batch 10 (First-Run Verification)](./userstory-misc-batch10-firstrun-2026-04-26.md) — Batch 10 assorted repos

### Audits & State Verification (5 docs)

Cross-repo dependency, archive status, and configuration audits:

- [Archive State Verification — Canonical Repos](./archive-state-canonical-2026-04-26.md) — GitHub archive status, last-push dates, descriptions for 16+ repos
- [Archive Successors: Settly & Authvault](./archive-successors-settly-authvault-2026-04-26.md) — Feature migration paths from archived repos
- [phenoShared Consumer Audit](./phenoshared-consumer-audit-2026-04-26.md) — All 12 workspace members consuming phenotype-shared crates
- [phenoShared Consumer Audit (Deep)](./phenoshared-consumer-audit-DEEP-2026-04-26.md) — Detailed per-crate and per-consumer breakdown
- [Session PR Queue Status](./session-pr-queue-status-2026-04-26.md) — 50+ PRs across Phenotype org, merge status & blockers

### Investigation Reports (5 docs)

Deep dives into specific issues, missing references, and installation failures:

- [PhenoSchema 404 Reference Sweep](./phenoschema-404-reference-sweep-2026-04-26.md) — 100+ cross-project references to deleted PhenoSchema repo; impact analysis
- [AgilePlus Install Broken Investigation](./agileplus-install-broken-investigation-2026-04-26.md) — Root cause analysis: Node module resolution failure, workaround guidance
- [Org Bot Issue Bulk-Close Candidates](./org-bot-issue-bulkclose-candidates-2026-04-26.md) — Archived-repo PRs, stale issues, suggested triage
- [CIVIS Issue Triage Plan](./civis-issue-triage-plan-2026-04-26.md) — Pre-session backlog sweep, priority triage
- [Org Pre-Session PR Backlog](./org-pre-session-pr-backlog-2026-04-26.md) — 40+ unmerged PRs, blockers, and merge order recommendations

---

## Recurring Governance Documents

Reference these for ongoing policy and architectural decisions:

### Active Policies
- `scripting_policy.md` — Language hierarchy: Rust default, Go/Zig/Mojo with justification, Python/TS only in existing runtimes, Bash ≤5 lines + justification
- `disk_budget_policy.md` — Rust target/ management, pre-dispatch disk checks (≥30Gi), target-pruner automation
- `org-pages-default-pattern.md` — New projects auto-get portfolio entry + `<project>.kooshapari.com` + path-based microfrontends
- `qc-enforcement.md` — Zero suppressions without inline justification, opinionated linting/formatting, quality gate mandates

### Architecture & Design
- `project_decomposition_governance.md` — Guidance for extracting shared packages, monorepo vs. polyrepo decisions
- `plugin_architecture_governance.md` — Plugin systems, Extism/WASM contracts, registry patterns
- `path_governance.md` — (Needs update to current workspace paths)

### Multi-Session Coordination
- `multi_session_coordination.md` — Argis↔Helios coordination via `.argis-helios-bus/`, disk space management, concurrent agent limits
- `long_push_pattern.md` — Long-running git operations, `nohup git push & disown` pattern, `git ls-remote` verification

---

## Quick Navigation

**Looking for:**
- **Archive status** → `archive-state-canonical-2026-04-26.md`
- **Deleted repo references** → `phenoschema-404-reference-sweep-2026-04-26.md`
- **PR blockers & merge order** → `org-pre-session-pr-backlog-2026-04-26.md`
- **Code walkthroughs** → `userstory-*-2026-04-26.md` (21 docs across multiple categories)
- **Scripting standards** → `scripting_policy.md`
- **Disk/resource management** → `disk_budget_policy.md`

---

## Document Metadata

**Total Governance Docs (2026-04-26 session):** 21 new docs

**Categories:**
- User-story walkthroughs: 11
- Audits: 5
- Investigation reports: 5

**Archive Date:** 2026-04-26  
**Next Review:** Ongoing; add new investigations to this index when created
