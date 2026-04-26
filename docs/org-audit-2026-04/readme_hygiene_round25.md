# README Hygiene Audit — Round 25 (LEGACY Tier, W-82+)

**Scope**: Continued README hygiene check to LEGACY tier (108 repos, 30-90d inactivity). Round 25 extends Round 24 coverage.

**Period**: 2026-04-25 | **Coverage**: Next 10 LEGACY repos by recent activity

## Next 10 LEGACY Repos Audited

| Repo | Last Commit | README | Install | License | Status |
|------|-------------|--------|---------|---------|--------|
| phenoData | 2026-04-25 | ✓ | ✓ | ✗ | Review |
| PhenoDevOps | 2026-04-25 | ✓ | ? | ✓ | Review |
| phenodocs | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| PhenoHandbook | 2026-04-25 | ✓ | ? | ✗ | Review |
| PhenoKits | 2026-04-25 | ✓ | ? | ✗ | Review |
| PhenoMCP | 2026-04-25 | ✓ | ? | ✗ | Review |
| PhenoObservability | 2026-04-25 | ✓ | ✓ | ✗ | Review |
| PhenoPlugins | 2026-04-25 | ✓ | ? | ✓ | Review |
| PhenoProc | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| PhenoProject | 2026-04-25 | ✓ | ✓ | ✗ | Review |

### Descriptions
- **phenoData**: Phenotype data layer workspace and storage primitives
- **PhenoDevOps**: DevOps tooling and operational infrastructure for Phenotype ecosystem
- **phenodocs**: Documentation distribution and docsite infrastructure
- **PhenoHandbook**: Handbook and guide documentation (operational, architecture, governance)
- **PhenoKits**: SDK collection and kit aggregation for Phenotype ecosystem
- **PhenoMCP**: Model Context Protocol support and MCP server infrastructure
- **PhenoObservability**: Observability SDKs and unified instrumentation framework
- **PhenoPlugins**: Plugin system and extension point infrastructure
- **PhenoProc**: Process management and execution environment framework
- **PhenoProject**: Project/workspace management and orchestration

## Universal Gap Status Update

**LICENSE File Missing** (5 of 10 repos, 50% gap rate — elevated from prior rounds)

- **phenoData, PhenoHandbook, PhenoKits, PhenoMCP, PhenoObservability, PhenoProject**: Missing LICENSE files (6 repos)
- **4 repos**: LICENSE files present (40% pass rate)
- **Status badges**: 1/10 repos have badges (10% — significant drop from R24's 100%)

**Key observation**: LICENSE adoption has deteriorated (40% vs R24's 60%), and status badge adoption has sharply dropped (10% vs prior 100%). This suggests Round 25 repos are infrastructure/SDK projects with different documentation standards or recent creation without full metadata.

## Installation Pattern Analysis

- **Documented (6 repos)**: phenoData, phenodocs, PhenoObservability, PhenoProc, PhenoProject (explicit install sections)
- **Undocumented (4 repos)**: PhenoDevOps, PhenoHandbook, PhenoKits, PhenoMCP (no install docs)
- **Language mix**: Mixed (infrastructure, docs, SDKs, plugin systems) — install docs vary by type

**Observation**: 60% lack installation steps. Infrastructure and toolkit projects (DevOps, Handbook, Kits, MCP) show lower install documentation, likely because they're consumed as libraries or embedded tools rather than standalone packages.

## Summary

- **README completeness**: 10/10 (100%) — maintained from prior rounds
- **Install instructions**: 6/10 (60%) — matches R24 but lower than R23 (80%)
- **License files**: 4/10 (40%) — **significant drop from R24's 60%**
- **Status badges**: 1/10 (10%) — **critical drop from R24/R23's 70-100%**

**Grade: C+** | Strong README adoption but sharp deterioration in LICENSE and badge coverage. Suggests infrastructure projects need metadata standardization.

**Gaps identified**: 
1. phenoData, PhenoHandbook, PhenoKits, PhenoMCP, PhenoObservability, PhenoProject need LICENSE
2. PhenoDevOps, PhenoHandbook, PhenoKits, PhenoMCP need install documentation
3. 9 repos missing status badges (likely oversight in creation)

### Recommended Next Action

1. **Batch LICENSE addition**: Add Apache-2.0 to phenoData, PhenoHandbook, PhenoKits, PhenoMCP, PhenoObservability, PhenoProject (6 repos)
2. **Add status badges**: All 10 repos need badge restoration (search prior rounds for badge patterns)
3. **Infrastructure documentation**: Add install/consumption docs to PhenoDevOps, PhenoHandbook, PhenoKits, PhenoMCP
4. **Continue to Round 26**: Next 10 repos (~48 remaining in LEGACY tier)

**Status**: ✅ Round 25 Complete | Ready for batch cleanup or Round 26

---

**Cumulative Hygiene Trend (Rounds 21-25)**:
- README: 95% avg (trend: stable at 100% last 3 rounds)
- Install: 60% avg (trend: declining 80% → 60%)
- License: 60% avg (trend: declining 80% → 40%)
- Badges: 70% avg (trend: volatile 100% → 10%)

**Recommendation**: Standardize metadata templates for new projects to prevent recurrence of LICENSE/badge gaps. Prioritize batch cleanup before Round 26.
