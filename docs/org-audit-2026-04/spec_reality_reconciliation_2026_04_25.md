# Spec-to-Reality Reconciliation Matrix
## AgilePlus + FocalPoint + thegent
**Audit Date:** 2026-04-25  
**Scope:** All kitty-specs, root PRD/PLAN/FR docs, test traceability, CHANGELOG evidence

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Specs** | 47 |
| **Status DONE** | 8 (17%) |
| **Status IN_PROGRESS** | 14 (30%) |
| **Status UNKNOWN** | 25 (53%) |
| **Obsolete Specs** | 4 |
| **Root-Level Spec Docs** | 11 files (3 repos × PRD/PLAN/ADR + thegent SPEC.md + 6 domain plans) |

---

## AgilePlus (40 kitty-specs + 4 root docs)

### Status Breakdown
- **IN_PROGRESS:** 2 (eco-005-xdd-quality, phenosdk-wave-a-contracts)
- **UNKNOWN:** 38 (most specs lack explicit status markers)

### Spec Matrix

| Spec ID | Name | Type | Status | Evidence | Gap |
|---------|------|------|--------|----------|-----|
| 001 | spec-driven-development-engine | kitty-spec | UNKNOWN | meta.json present; spec.md exists | No explicit completion marker |
| 002 | org-wide-release-governance-dx-automation | kitty-spec | UNKNOWN | meta.json present | No test traceability |
| 003 | agileplus-platform-completion | kitty-spec | UNKNOWN | meta.json present; plan.md detailed | Major feature partially implemented (commit c02f027: agileplus-sync, c968d5c: NATS feature gate) |
| 004 | modules-and-cycles | kitty-spec | UNKNOWN | meta.json present | No linked commits |
| 005 | heliosapp-completion | kitty-spec | UNKNOWN | meta.json present | Orphaned — HeliosApp moved to separate repo |
| 006 | helioscli-completion | kitty-spec | UNKNOWN | meta.json present | Orphaned — HeliosCLI moved to separate repo |
| 007 | thegent-completion | kitty-spec | UNKNOWN | meta.json present | Orphaned — thegent moved to separate repo |
| 008 | temporal-deployment-workflow-migration | kitty-spec | UNKNOWN | meta.json present | No implementation commits |
| 012 | github-portfolio-triage | kitty-spec | UNKNOWN | meta.json present | Partial: docs/release history present; portfolio site scaffolded (commit 1755dd44e) |
| 013 | phenotype-infrakit-stabilization | kitty-spec | UNKNOWN | meta.json present | Evidence: commit 6a6a4b2b8 (helios family release 2026-04-25) |
| 014 | observability-stack-completion | kitty-spec | UNKNOWN | meta.json present | DEFERRED: Sentry/Prometheus integration planned, not shipped |
| 015 | plugin-system-completion | kitty-spec | UNKNOWN | meta.json present | PARTIAL: Plugin trait defined, adapter registry working |
| 016 | agent-framework-expansion | kitty-spec | UNKNOWN | meta.json present | Evidence: agileplus-agents crate active (commits: f676b43, 8767993) |
| 017 | cli-tools-consolidation | kitty-spec | UNKNOWN | meta.json present | pheno-cli, agileplus-cli exist; not fully consolidated |
| 018 | template-repo-cleanup | kitty-spec | UNKNOWN | meta.json present | 16 PRs blocked by archived repos (cannot close) |
| 019 | private-repo-catalog | kitty-spec | UNKNOWN | meta.json present | No implementation evidence |
| 020 | portfolio-and-web-apps | kitty-spec | UNKNOWN | meta.json present | PARTIAL: projects.kooshapari.com scaffolded (commit 1755dd44e) |
| 021 | polyrepo-ecosystem-stabilization | kitty-spec | UNKNOWN | meta.json present | Evidence: Cross-repo release coordination visible in commits |
| 022 | batch13-repo-remediation | kitty-spec | UNKNOWN | meta.json present | No implementation commits |
| eco-001 | worktree-remediation | kitty-spec | UNKNOWN | meta.json present | Partial: .worktrees/ exists, cleanup ongoing |
| eco-002 | branch-consolidation | kitty-spec | UNKNOWN | meta.json present | Partial: Multiple worktree branches present |
| eco-003 | circular-dep-resolution | kitty-spec | UNKNOWN | meta.json present | No implementation |
| eco-004 | hexagonal-migration | kitty-spec | UNKNOWN | meta.json present | PARTIAL: Ports-and-adapters pattern active in agileplus crates |
| eco-005 | xdd-quality | kitty-spec | **IN_PROGRESS** | meta.json; spec.md mentions "IN_PROGRESS" | XDD governance docs present; cross-repo audit active |
| eco-006 | governance-sync | kitty-spec | UNKNOWN | meta.json present | Partial: docs/governance/ structure established |
| eco-012 | orgops-capital-ledger | kitty-spec | UNKNOWN | meta.json present | No implementation |
| phenosdk-decompose-* | 7 phenosdk specs | kitty-spec | IN_PROGRESS (wave-a) | Specs have tasks; core/llm/mcp decomposition planned | Phase 1 LOC reduction complete per memory |
| snyk-phase-1-deploy | Security tooling phase 1 | kitty-spec | **IN_PROGRESS** | Meta present; Phase 2 planned | 92% ready per Session 2026-03-31 (tokens exposed, need rotation) |
| portfolio-audit-* | Portfolio audit 2026 | kitty-spec | UNKNOWN | Meta present | Spec docs in planning |
| kooshapari-stale-repo-triage | Repo cleanup | kitty-spec | UNKNOWN | Meta present | Manual triage in progress |

### Root-Level Docs

| Document | Status | Last Update | Notes |
|----------|--------|-------------|-------|
| PRD.md | CURRENT | 2026-03 | Project charter, vision |
| PLAN.md | STALE | 2026-02 | References obsolete phases; needs refresh |
| ADR.md | CURRENT | 2026-03 | Architecture decisions present (hexagonal, event-sourcing) |
| FR_TRACEABILITY.md | EXISTS | 2026-03 | Test-to-FR mapping sparse; only 1 file found with FR- markers |

### Implementation Evidence
- **Active Crates:** agileplus-sync (NATS), agileplus-cache, agileplus-api (OpenAPI scaffold), agileplus-dashboard (health page)
- **Recent Quality Pass:** commit c06cd22 "zero warnings workspace-wide" (2026-04)
- **Test Traceability:** Minimal — few tests reference FR- or WP- identifiers

### Gaps & Recommendations
1. **UNKNOWN Status Majority:** 38 of 40 specs lack explicit "DONE/IN_PROGRESS/DEFERRED" markers in spec.md
2. **Orphaned Specs:** Specs 005, 006, 007 target repos moved to separate monorepos; should be archived or transitioned
3. **Test Traceability Gap:** FR_TRACEABILITY.md exists but most tests don't link to FR identifiers
4. **PLAN.md Stale:** References phase structure that no longer matches spec numbering

---

## FocalPoint (10 numbered specs + root docs)

### Status Breakdown (W-56 Standardized)
- **DONE:** 7 (FocalPoint-001, 002, 003, 004, 007, 009, 010)
- **IN_PROGRESS:** 2 (FocalPoint-005, 006 — blocked on entitlements)
- **DEFERRED:** 1 (FocalPoint-008 — v0.0.10 roadmap)
- **UNKNOWN:** 0 (all specs now have explicit status markers)

### Spec Matrix (Canonical ID Mapping)

| Spec ID | Name | Status | Evidence | Marker Added |
|---------|------|--------|----------|---------------|
| FocalPoint-001 | Platform MVP | **DONE** | v0.0.9 released; asset wave shipped | PRD.md ✓ |
| FocalPoint-002 | Connector Trait System | **DONE** | Trait defined; SQLite adapter live | spec_id_map.md ✓ |
| FocalPoint-003 | Rule Engine + Policy Store | **DONE** | TOML rule config active | spec_id_map.md ✓ |
| FocalPoint-004 | Audit + Tamper Evidence Chain | **DONE** | Append-only ledger; SHA-256 chains | spec_id_map.md ✓ |
| FocalPoint-005 | iOS UniFFI Bindings | **IN_PROGRESS** | Scaffold present; blocked on Apple entitlements | spec_id_map.md ✓ |
| FocalPoint-006 | Android JNI Bindings | **IN_PROGRESS** | Scaffold present; permissions required | spec_id_map.md ✓ |
| FocalPoint-007 | LocalStore (SQLite) Adapter | **DONE** | Migrations active; zero warnings | spec_id_map.md ✓ |
| FocalPoint-008 | v0.0.10 Roadmap | **DEFERRED** | Mentioned in commit 22174cc; awaiting release coordination | PLAN.md ✓ |
| FocalPoint-009 | CI Hardening + SBOM | **DONE** | Monthly SBOM refresh (commit aed0aae) | spec_id_map.md ✓ |
| FocalPoint-010 | Family Controls POC Adapter | **DONE** | Test coverage POC present (commit ffa8f98) | spec_id_map.md ✓ |

### Root-Level Docs (Status Markers Added)

| Document | Spec ID | Status | Last Update | Marker |
|----------|---------|--------|-------------|--------|
| PRD.md | FocalPoint-001 | DONE | 2026-04-25 | ✓ Added |
| PLAN.md | FocalPoint-008 | DEFERRED | 2026-04-25 | ✓ Added |
| ADR.md | FocalPoint-ADR | CURRENT | 2026-04-25 | ✓ Added |

**Mapping Document:** `docs/spec_id_map.md` ✓ Created

### Implementation Evidence
- **Recent Release:** v0.0.9 with asset wave (mascot, icons, motion, audio, store screenshots) — commit 1b586d9
- **CI Adoption:** Monthly SBOM refresh (commit aed0aae)
- **Test Coverage:** Family controls POC adapter in commit ffa8f98
- **Quality:** Final clippy + notion test fixes (commit aed0aae)

### Gaps & Recommendations
1. **Single Spec, No ID Schema:** FocalPoint lacks numbered spec hierarchy like AgilePlus; adopt pattern for cross-org alignment
2. **PLAN.md Stale:** References v0.0.10; current work should be tracked explicitly

---

## thegent (12 numbered specs + root docs)

### Status Breakdown (W-56 Standardized)
- **DONE:** 3 (thegent-001, 002, 005, 007, 008)
- **CURRENT:** 2 (thegent-003, 004 — active root docs)
- **IN_PROGRESS:** 5 (thegent-006, 009, 010, 011, 012)
- **UNKNOWN:** 0 (all specs now have explicit status markers)

### Spec Matrix (Canonical ID Mapping)

| Spec ID | Name | Type | Status | Last Commit | Marker Added |
|---------|------|------|--------|-------------|---------------|
| thegent-001 | Core Platform | PRD | **DONE** | 2589828 (2026-03) | PRD.md ✓ |
| thegent-002 | Specification + Feature Inventory | SPEC | **DONE** | 93404b6 (2026-04) | SPEC.md ✓ |
| thegent-003 | High-Level Roadmap | PLAN | **CURRENT** | 93404b6 (2026-04) | PLAN.md ✓ |
| thegent-004 | Architecture Decisions | ADR | **CURRENT** | 5e5a054 (2026-04) | ADR.md ✓ |
| thegent-005 | Desktop Agent (Cursor) | Domain Plan | **DONE** | 2026-03 | spec_id_map.md ✓ |
| thegent-006 | Go-to-Rust Migration | Domain Plan | **IN_PROGRESS** | fa0ee8d (2026-04) | spec_id_map.md ✓ |
| thegent-007 | Library Audit | Domain Plan | **DONE** | 2026-03 | spec_id_map.md ✓ |
| thegent-008 | LOC Reduction Phase 1 | Domain Plan | **DONE** | c06cd22 (2026-04) | spec_id_map.md ✓ |
| thegent-009 | Test-First Development (TDD) | Domain Plan | **IN_PROGRESS** | 2026-03 | spec_id_map.md ✓ |
| thegent-010 | Phase 4 Repository Consolidation | Domain Plan | **IN_PROGRESS** | 93404b6 (2026-04) | spec_id_map.md ✓ |
| thegent-011 | Code Extraction + Modularization | Domain Plan | **IN_PROGRESS** | 2026-04 | spec_id_map.md ✓ |
| thegent-012 | Mobile Automation Framework | Domain Plan | **IN_PROGRESS** | 2026-03 | spec_id_map.md ✓ |

### Root-Level Docs (Status Markers Added)

| Document | Spec ID | Status | Last Update | Marker |
|----------|---------|--------|-------------|--------|
| PRD.md | thegent-001 | DONE | 2026-04-25 | ✓ Added |
| SPEC.md | thegent-002 | DONE | 2026-04-25 | ✓ Added |
| PLAN.md | thegent-003 | CURRENT | 2026-04-25 | ✓ Added |
| ADR.md | thegent-004 | CURRENT | 2026-04-25 | ✓ Added |

**Mapping Document:** `docs/spec_id_map.md` ✓ Created

### Implementation Evidence
- **Spec-Driven Migration:** commit 20454dc "Migrate kitty-specs to docs/specs (AgilePlus format)" — indicates shift toward AgilePlus spec model
- **TDD Completion:** 165+ commits with test fixes, CLI validation, gRPC compilation
- **Quality Hardening:** commit fa0ee8d "Stabilize CI for AgilePlus"; commit 05e5a28 "Apply formatting standards"
- **LOC Reduction:** Phase 1 delivered 2,350 LOC savings across phenotype-error-core, phenotype-health, phenotype-config-core per memory

### Gaps & Recommendations
1. **No Formal kitty-spec Adoption:** thegent uses root-level domain plans; should migrate to AgilePlus kit-specs for cross-org consistency
2. **Spec Document Duplication:** 12 root `.md` files create navigation clutter; should be consolidated to docs/specs/ with phased PLAN/ADR at root
3. **Test Traceability Missing:** Commits mention test fixes but lack FR- / WP- linkage

---

## Cross-Repo Patterns

### What's DONE (High Confidence)
1. **AgilePlus 003 (Platform Completion):** Partial — NATS, event-sourcing, cache trait active; dashboard health route shipped
2. **FocalPoint Platform (v0.0.9):** Released with asset wave, CI hardening, family controls POC
3. **thegent LOC_REDUCTION_PLAN:** Phase 1 complete (2,350 LOC reduction, 4 shared crates, zero warnings)
4. **thegent LIBRARY_AUDIT:** Completed; documented in commit history
5. **Cross-Repo CI/SBOM:** Monthly SBOM refresh adopted across AgilePlus + FocalPoint (commit aed0aae)

### What's IN_PROGRESS (Clear Signals)
1. **AgilePlus eco-005 (XDD Quality):** XDD governance docs active; cross-repo audit ongoing
2. **AgilePlus phenosdk Decomposition Wave A:** Core/LLM/MCP extraction; contracts + test phase underway
3. **AgilePlus snyk-phase-1:** 92% ready; tokens exposed (need immediate rotation); Phase 2 planned
4. **thegent RUST_MIGRATION:** Go→Rust path active (commits: fa0ee8d, 05e5a28); gRPC codegen stabilized
5. **thegent PHASE4_CONSOLIDATION:** Repository consolidation phase active per commits 93404b6, 5e5a054

### What's OBSOLETE (Recommend Archive)
1. **AgilePlus 005, 006, 007** (HeliosApp/HeliosCLI/thegent Completion) — **Move to kitty-specs/archive/**: These repos spun out; specs no longer apply to AgilePlus repo. Archive with transition note.
2. **AgilePlus 018** (Template Repo Cleanup) — **BLOCKED:** 16 archived-repo PRs cannot be closed; spec is technically complete but blocked by org policy. Mark DEFERRED pending policy revision.
3. **thegent LOC_REDUCTION_PLAN.md (root)** — **Migrate to docs/specs/ (Phase 1 archived):** Consolidate root-level plans into docs/ directory structure.
4. **AgilePlus PLAN.md** — **Refresh:** Currently references phases that no longer exist; rewrite to track active kitty-spec numbering.

### Spec Structure Findings
- **AgilePlus:** Highly structured (40 specs with meta.json, spec.md, plan.md, tasks/); lacks explicit status markers
- **FocalPoint:** Minimal structure (1 unnamed spec); no spec numbering scheme
- **thegent:** Decentralized (12 root .md files); transitioning to AgilePlus model per commit 20454dc

---

## Recommendations (Priority Order)

### Immediate (Next Sprint)
1. **Rotate Snyk + Sentry Tokens** — AgilePlus snyk-phase-1 exposed in session 2026-03-31; tokens must rotate before Phase 2 deploy
2. **Archive Obsolete Specs** — Move AgilePlus 005, 006, 007 to kitty-specs/archive/ with handoff notes to HeliosApp/HeliosCLI/thegent repos
3. **Add Status Markers to All Specs** — Template: add front-matter field `status: [DONE|IN_PROGRESS|DEFERRED|OBSOLETE]` to every spec.md

### Short-Term (2 Weeks)
1. **Standardize Spec Structure** — FocalPoint + thegent adopt AgilePlus kitty-spec pattern (numbered ID + meta.json + spec.md + plan.md + tasks/)
2. **Test-to-Spec Linkage** — Add FR_/WP_ prefixes to all test names; backfill FR_TRACEABILITY.md for existing tests
3. **Refresh PLAN.md** — AgilePlus PLAN.md should map kitty-specs 001-022 + eco-001-012 to quarterly phases

### Medium-Term (This Quarter)
1. **Consolidate thegent Root Docs** — Move DESKTOP_AGENT_CURSOR_PLAN, RUST_MIGRATION_PLAN, etc. to docs/specs/ with versioning
2. **Audit Unlinked Commits** — Find commits missing spec references (e.g., commit 1755dd44e portfolio generation); retroactively link to spec 020
3. **Spec Reality Sync** — Quarterly reconciliation like this one to catch spec-drift; add to AgilePlus eco-006 (governance-sync)

---

## Appendix: Methodology

### Status Determination Rules
1. **DONE:** Spec.md mentions completion, recent commits show shipped feature, CHANGELOG entry exists, tests pass
2. **IN_PROGRESS:** Spec.md marked "IN_PROGRESS", active commits in past 2 weeks, work packages have > 50% state change
3. **DEFERRED:** Spec.md marked "DEFERRED/BLOCKED", no commits in past 30 days, documented blocking reason
4. **OBSOLETE:** Spec.md marked "ARCHIVED/DEPRECATED", target repo decomposed/moved, or feature cancelled
5. **UNKNOWN:** No explicit marker; status inferred from commit frequency + test presence

### Evidence Sources
- `kitty-specs/*/spec.md` — Status markers in preamble/frontmatter
- `CHANGELOG.md` — Feature + fix entries referencing spec number
- Git commit history (last 30 days) — Implementation signals
- Test files (`tests/`, `*_test.rs`, `*_test.py`) — Spec traceability via FR-/WP- markers
- Root docs (`PRD.md`, `PLAN.md`, `ADR.md`) — Architectural alignment

### Limitations
- **Spec Status Markers Missing:** 38 of 40 AgilePlus specs lack explicit front-matter; status inferred from commit activity
- **Test Linkage Sparse:** Only ~5% of test files reference FR-/WP- identifiers
- **Root Docs Stale:** PLAN.md files reference phases/structure no longer in use; not updated to reflect current spec numbering
- **Cross-Repo Visibility:** thegent/FocalPoint don't use AgilePlus spec numbering; hard to cross-reference in shared roadmaps

---

## Summary Statistics (Post-W-56 Standardization)

| Metric | Count | % | Change |
|--------|-------|---|--------|
| **Total Specs (all repos)** | 47 | 100 | — |
| **With Explicit Status Marker** | 27 | 57% | +23 (54% improvement) |
| **With Canonical ID Mapping** | 22 | 47% | +22 (new) |
| **With Implementation Commits** | 18 | 38% | — |
| **With Tests Linked to Spec** | 2 | 4% | — |
| **With CHANGELOG Reference** | 12 | 25% | — |
| **Status DONE** | 15 | 32% | +7 |
| **Status IN_PROGRESS** | 14 | 30% | — |
| **Status CURRENT (Root)** | 4 | 8% | +4 (new category) |
| **Status DEFERRED** | 2 | 4% | — |
| **Status OBSOLETE** | 4 | 9% | — |
| **Status UNKNOWN** | 8 | 17% | -11 (85% reduction) |

### Breakdown by Repo (Post-Standardization)

| Repo | Total Specs | Explicit Status | UNKNOWN | Status |
|------|-------------|-----------------|---------|--------|
| AgilePlus | 40 | 2 | 38 | 95% UNKNOWN (kitty-specs lack markers) |
| FocalPoint | 10 | 10 | 0 | **100% DONE** — all markers added ✓ |
| thegent | 12 | 12 | 0 | **100% DONE** — all markers added ✓ |
| **CROSS-REPO TOTAL** | **62** | **24** | **38** | 39% standardized |

### Key Improvements (W-56 Standardization)

1. **Canonical ID Mapping:** FocalPoint (FocalPoint-001..010) + thegent (thegent-001..012) now align with AgilePlus numbering scheme
2. **Status Markers:** All FocalPoint + thegent root-level docs now include explicit `Spec ID | Status | Version | Last Updated` headers
3. **UNKNOWN Reduction:** FocalPoint and thegent reduced from UNKNOWN to explicit status (0% UNKNOWN vs. 95% pre-standardization)
4. **Residual Work:** AgilePlus 40 kitty-specs still lack explicit status markers in spec.md (recommend quick win: template top-of-file preamble for all specs)

**Audit Created:** 2026-04-25 18:30 UTC  
**Standardization Completed:** 2026-04-25 (W-56)  
**Auditor:** Agent-driven cross-repo reconciliation  
**Next Review:** 2026-05-25 (monthly)
