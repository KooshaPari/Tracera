# Phase 2: Document Migration - File Mapping Plan

**Status**: In Progress  
**Date**: November 21, 2024  
**Total Files to Migrate**: 252 (169 root + 83 docs/)

---

## Overview

This document maps each of the 252 documentation files to their new location in the organized docs/ structure.

---

## Root Files (169) - Detailed Mapping

### Category A: Getting Started & Entry Points (5 files)
**Destination**: `docs/01-getting-started/`

| File | Action |
|------|--------|
| README.md | Copy to 01-getting-started/ (keep original in root) |
| START_HERE.md | Move to 01-getting-started/ |
| START_HERE_REFACTOR_INDEX.md | Move to 01-getting-started/refactor-guide.md |
| QUICK_START_AGENTS.md | Move to 01-getting-started/ |
| CONTRIBUTING.md | Move to 01-getting-started/ |

### Category B: Architecture & Design (18 files)
**Destination**: `docs/02-architecture/`

| File | Action | Note |
|------|--------|------|
| COMPREHENSIVE_ARCHITECTURE_DESIGN.md | Move | Core architecture |
| ATOMIC_TRACE_ARCHITECTURE.md | Move | Atomic design |
| INTERNAL_VIEW_ARCHITECTURES.md | Move | View patterns |
| NATS_TECHNICAL_ARCHITECTURE.md | Move | Messaging system |
| OPTIMAL_INFRASTRUCTURE_ARCHITECTURE.md | Move | Infrastructure |
| ROOT_ORCHESTRATOR_DESIGN.md | Move | Orchestration |
| TRACE_SSOT_ARCHITECTURE_DEEP_DIVE.md | Move | SSOT patterns |
| REQUIREMENTS_TRACEABILITY_ARCHITECTURE.md | Move | RTM architecture |
| REQUIREMENTS_TRACEABILITY_MASTER.md | Move | RTM master |
| ATOMIC_EXAMPLES.md | Move | Examples |
| ATOMIC_IMPLEMENTATION_ROADMAP.md | Move | Roadmap |
| ATOMIC_COMPLETE_SUMMARY.md | Move | Summary |
| COMPLETE_VIEW_TAXONOMY.md | Move | View taxonomy |
| SPEC_TDD_ARCHITECTURE_RESEARCH.md | Move | TDD research |
| ATOMS_TECH_ANALYSIS.md | Move | Technical analysis |

### Category C: Planning & Implementation (18 files)
**Destination**: `docs/03-planning/`

| File | Action |
|------|--------|
| IMPLEMENTATION_PLAN.md | Move |
| MASTER_PLAN_WBS_DAGS.md | Move |
| AGILE_WATERFALL_HYBRID_PLAN.md | Move |
| MASTER_INDEX.md | Archive (merge with docs/INDEX.md) |
| MASTER_INDEX_ALL_PLANS.md | Archive (merge with docs/INDEX.md) |
| MODERNIZATION_CHECKLIST.md | Move |
| MODERNIZATION_INDEX.md | Move |
| MODERNIZATION_SUMMARY.md | Move |
| MODERNIZATION_VERIFICATION_REPORT.txt | Move |
| MODERN_PYTHON_INFRA.md | Move |
| SETUP_MODERN_INFRA.md | Move |
| QUICK_REFERENCE_MODERN_INFRA.md | Move to 08-reference/ |
| TEAM_ONBOARDING_GUIDE.md | Move to 04-guides/ |
| DEVELOPER_GUIDE.md | Move to 04-guides/ |
| DEPLOYMENT_GUIDE.md | Move to 04-guides/ |
| PRODUCTION_DEPLOYMENT_GUIDE.md | Move to 04-guides/ |

### Category D: Guides & How-To (12 files)
**Destination**: `docs/04-guides/`

| File | Action |
|------|--------|
| MIGRATION_PLAN_PHASE1.md | Move as migration-guide.md |
| MIGRATION_CODE_EXAMPLES.md | Move |
| MIGRATION_EXECUTION_GUIDE.md | Move |
| MIGRATION_COMPLETE_ALL_PHASES.md | Archive to 07-reports/phase-3/ |
| REFACTOR_COMPLETE_SUMMARY.md | Archive to 07-reports/phase-3/ |
| REFACTOR_DELIVERY_CHECKLIST.md | Move |
| POST_REFACTOR_CHECKLIST.md | Move |
| MONITOR_IMPLEMENTATION_GUIDE.md | Move |
| CLI_MONITOR_DELIVERY.md | Move |

### Category E: Research - Ecosystem & Dependencies (12 files)
**Destination**: `docs/05-research/`

| File | Action |
|------|--------|
| COMPREHENSIVE_DEPENDENCY_ANALYSIS.md | Move |
| DEPENDENCY_COMPARISON_MATRIX.md | Move |
| DEPENDENCY_MIGRATION_GUIDE.md | Move |
| DEPENDENCY_RESEARCH_INDEX.md | Move |
| ENHANCED_DEPENDENCIES_GUIDE.md | Move |
| COMPREHENSIVE_PYTHON_TOOLS_DEEP_RESEARCH.md | Move |
| TRACE_PACKAGES_TOOLS_ECOSYSTEM.md | Move |
| TRACE_ADVANCED_TOOLING_INTEGRATIONS.md | Move |
| ADVANCED_PYTHON_TOOLS_RESEARCH.md | Move |
| ULTRA_STRICT_PYTHON_RESEARCH.md | Move |
| ULTRA_DEEP_RESEARCH_ALL_PACKAGES.md | Move |
| COMPREHENSIVE_PACKAGE_MATRIX_1000_PLUS.md | Move |

### Category F: Research - Community & Academic (6 files)
**Destination**: `docs/05-research/`

| File | Action |
|------|--------|
| COMMUNITY_STRATEGIES_GITHUB_REDDIT_ARXIV.md | Move |
| GITHUB_TRENDS_ANALYSIS.md | Move |
| ACADEMIC_RESEARCH_FINDINGS.md | Move |
| TRACE_COMPREHENSIVE_RESEARCH_SUMMARY.md | Move |
| TRACE_ARXIV_ACADEMIC_RESEARCH.md | Move |
| TRACE_DEEP_RESEARCH_BLOGS_REDDIT_GITHUB.md | Move |

### Category G: Research - Indexes (8 files)
**Destination**: `docs/05-research/` (merge into README)

Action: Archive (consolidate into 05-research/README.md)
- COMPREHENSIVE_RESEARCH_MASTER_INDEX.md
- MASTER_RESEARCH_INDEX.md
- TRACE_RESEARCH_INDEX.md
- RESEARCH_DOCUMENTATION_INDEX.md
- RESEARCH_MASTER_INDEX.md
- RESEARCH_STATUS_FINAL.md
- COMPREHENSIVE_RESEARCH_COMPLETE.md
- RESEARCH_COMPLETE_FINAL.txt
- RESEARCH_COMPLETE.txt

### Category H: RTM & Requirements Traceability (13 files)
**Destination**: `docs/05-research/rtm-deep-dives/`

| File | Action |
|------|--------|
| REQUIREMENTS_TRACEABILITY_BEST_PRACTICES.md | Move |
| REQUIREMENTS_TRACEABILITY_COMPARISON.md | Move |
| REQUIREMENTS_TRACEABILITY_GETTING_STARTED.md | Move |
| REQUIREMENTS_TRACEABILITY_INDEX.md | Move |
| REQUIREMENTS_TRACEABILITY_MVP.md | Move |
| REQUIREMENTS_TRACEABILITY_RESEARCH.md | Move |
| REQUIREMENTS_TRACEABILITY_ROADMAP.md | Move |
| REQUIREMENTS_TRACEABILITY_SPEC.md | Move |
| REQUIREMENTS_TRACEABILITY_SUMMARY.md | Move |
| REQUIREMENTS_TRACEABILITY_USECASES.md | Move |
| REQUIREMENTS_TRACEABILITY_VISUAL_GUIDE.md | Move |

### Category I: RTM/Trace Deep Dives (18 files)
**Destination**: `docs/05-research/rtm-deep-dives/` and `docs/05-research/trace-research/`

**RTM Deep Dives**:
- RTM_CHAOS_ENGINEERING_SCOPE_MANAGEMENT.md
- RTM_COMPLETE_VIEW_SUMMARY.md
- RTM_CRUD_EXAMPLES_WALKTHROUGH.md
- RTM_DEEP_DIVE_ADVANCED_ARCHITECTURES.md
- RTM_DEEP_DIVE_AI_ML_INTEGRATION.md
- RTM_DEEP_DIVE_FORMAL_METHODS.md
- RTM_DEEP_DIVE_GRAPH_DATABASES.md
- RTM_DEEP_DIVE_MULTI_LANGUAGE_IMPLEMENTATION.md
- RTM_DEEP_DIVE_REGULATORY_COMPLIANCE.md
- RTM_EXPANDED_RESEARCH_SUMMARY.md
- RTM_EXTENDED_VIEWS_AND_LINKS.md
- RTM_FEATURE_GRAPH_ARCHITECTURE.md
- RTM_FINAL_ARCHITECTURE_SUMMARY.md
- RTM_FINAL_COMPREHENSIVE_SUMMARY.md
- RTM_INTELLIGENT_CRUD_SCAFFOLDING.md
- RTM_INTELLIGENT_CRUD_SUMMARY.md
- RTM_MULTI_VIEW_CLI_EXAMPLES.md
- RTM_PROJECT_STATE_VISUALIZATION.md

Action: Move all to `docs/05-research/rtm-deep-dives/`

### Category J: Trace Research (10 files)
**Destination**: `docs/05-research/trace-research/`

| File | Action |
|------|--------|
| TRACE_FEATURES_ALGORITHMS_DEEP_DIVE.md | Move |
| TRACE_CONSISTENCY_SYNCHRONIZATION_PATTERNS.md | Move |
| TRACE_ATTACHED_LAYERS_MULTIVIEW.md | Move |
| TRACE_PM_TOOLING_RESEARCH.md | Move |
| TRACE_PM_TOOLING_SUMMARY.md | Move |

### Category K: Status Reports & Summaries (35 files)
**Destination**: `docs/07-reports/` (organized by phase)

See detailed mapping below by phase and final-validation.

### Category L: Miscellaneous & Obsolete (8 files)
**Destination**: `docs/07-reports/archive/`

Action: Archive (review and potentially consolidate)
- ACTUAL_REALITY_REPORT.md
- BACKGROUND_CHECKS_SUMMARY.md
- CRITICAL_FINDINGS.md
- CHANGELOG.md
- assignment.md
- FINAL_HONEST_REALITY.md
- HONEST_VALIDATION_REPORT.md
- LESSONS_LEARNED.md → Move to 08-reference/ if valuable

### Category M: Code Consolidation & Analysis (5 files)
**Destination**: `docs/05-research/`

| File | Action |
|------|--------|
| CODE_CONSOLIDATION_ANALYSIS.md | Move |
| CODE_REVIEW_VALIDATION.md | Move |
| TECH_STACK_VALIDATION.md | Move |
| KIMAKI_CONSOLIDATION_ANALYSIS.md | Move |
| USAGE_CONSOLIDATION_ANALYSIS.md | Move |

### Category N: Category Analysis & Comparisons (10 files)
**Destination**: `docs/05-research/`

| File | Action |
|------|--------|
| COMPREHENSIVE_30_CATEGORY_ANALYSIS.md | Move |
| COMPREHENSIVE_CODEBASE_ANALYSIS.md | Move |
| CROSS_PROJECT_DEPENDENCY_ANALYSIS.md | Move |
| MEGA_COMPREHENSIVE_100_CATEGORY_ANALYSIS.md | Move |
| MEGA_RESEARCH_FINAL_SUMMARY.md | Move |
| ULTRA_COMPREHENSIVE_50_CATEGORY_ANALYSIS.md | Move |
| ULTRA_DEEP_RESEARCH_MASTER_INDEX.md | Move |
| ULTRA_RESEARCH_MASTER_INDEX.md | Move |
| KIMAKI_QUICK_REFERENCE.md | Move to 08-reference/ |
| QUICK_REFERENCE.md | Move to 08-reference/ |

### Category O: API & Workflows (2 files)
**Destination**: `docs/06-api-reference/`

| File | Action |
|------|--------|
| README_STDIO_MCP_SERVER.md | Move as mcp-server-guide.md |
| STDIO_MCP_SERVER_SETUP_COMPLETE.md | Move |

---

## Docs/ Files (83) - Quick Mapping

### Planning & Product Documents (10 files)
**Destination**: `docs/03-planning/`
- PRD.md, PRD-ENHANCED.md, PRD_VALIDATION_REPORT.md
- epic-*.md (all 4 files)
- product-brief-TraceRTM-*.md
- PHASE_2_PLAN.md, PHASE_2_PROGRESS.md

### Phase Completions (15 files)
**Destination**: `docs/07-reports/phase-*/` (organized by phase)
- PHASE-*-COMPLETION-REPORT.md (each to appropriate phase)
- PHASE_2_PLAN.md, PHASE_2_PROGRESS.md
- sprint-*.md files (to appropriate sprint section)

### Implementation & Testing (30 files)
**Destination**: `docs/04-guides/` and `docs/02-architecture/`
- architecture.md → docs/02-architecture/
- Test design files → docs/04-guides/testing/
- TEST-*.md files → docs/04-guides/testing/
- Implementation readiness reports → docs/03-planning/

### Research & Analysis (15 files)
**Destination**: `docs/05-research/`
- RESEARCH-SUMMARY.md
- COMPREHENSIVE_RESEARCH_SUMMARY.md
- CRAPH-*.md files
- CRUN_DEEP_DIVE.md
- FIGMA_AS_CODE_RESEARCH.md
- BACKEND_INTEGRATED_SERVICES_RESEARCH.md
- ADDITIONAL_INTEGRATIONS_RESEARCH.md

### Final Reports & Completion (10 files)
**Destination**: `docs/07-reports/final-validation/`
- FINAL-*.md files
- COMPLETE*.md files
- COVERAGE_CLOSURE_REPORT.md
- validation-*.md files

### Other (3 files)
- INDEX.md → Archive (merge with docs/INDEX.md)
- bmm-workflow-status.yaml → Archive or move to 04-guides/
- ux-*.html, ux-*.md → Archive or move to 04-guides/design/

---

## Migration Strategy

### Phase 1: Getting Started & Reference (Fast)
1. Move 01-getting-started files (5 files)
2. Move 08-reference files (10 files)
3. Total: ~15 files, ~30 minutes

### Phase 2: Architecture & Planning (Medium)
1. Move 02-architecture files (15 files)
2. Move 03-planning files (18 files)
3. Total: ~33 files, ~45 minutes

### Phase 3: Guides & Research (Large)
1. Move 04-guides files (12 files)
2. Move 05-research files (60+ files including RTM/Trace)
3. Total: ~72 files, ~90 minutes

### Phase 4: API & Reports (Remaining)
1. Move 06-api-reference files (2 files)
2. Move 07-reports files (35+ files organized by phase)
3. Total: ~37 files, ~45 minutes

### Phase 5: Docs Reorganization & Cleanup
1. Reorganize 83 existing docs/ files
2. Archive obsolete files
3. Update internal links
4. Total: ~120 minutes

---

## Success Criteria

- [ ] All 169 root files moved
- [ ] All 83 docs/ files reorganized
- [ ] All internal links updated
- [ ] No broken file references
- [ ] Archive directory contains obsolete files
- [ ] Each section has functioning README
- [ ] Master INDEX.md is complete
- [ ] Ready for Phase 3 (consolidation)

---

**Total Migration Time**: 4-5 hours
**Current Status**: Planning phase complete, ready for file movement
**Next Step**: Begin Phase 1 of migration

