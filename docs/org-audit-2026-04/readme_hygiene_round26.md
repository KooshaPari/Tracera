# README Hygiene Audit — Round 26 (LEGACY Tier, W-82+)

**Scope**: Continued README hygiene check to LEGACY tier (10 repos, infrastructure & core systems). Extends Round 25 coverage.

**Period**: 2026-04-25 | **Coverage**: Next 10 repos by alphabetical order after Round 25

## Next 10 LEGACY Repos Audited

| Repo | Last Commit | README | Install | License | Status |
|------|-------------|--------|---------|---------|--------|
| phenotype-journeys | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| phenotype-omlx | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| phenotype-ops-mcp | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| phenotype-ops-mcp-fix | 2026-04-24 | ✓ | ✗ | ✓ | Review |
| phenotype-org-audits | 2026-04-25 | ✓ | ✗ | ✓ | Review |
| phenotype-previews-smoketest | 2026-04-25 | ✗ | ✗ | ✗ | Critical |
| phenotype-registry | 2026-04-05 | ✓ | ✗ | ✗ | Review |
| phenotype-shared | 2026-04-25 | ✓ | ✓ | ✗ | Review |
| phenotype-skills | 2026-04-25 | ✓ | ✓ | ✗ | Review |
| phenotype-tooling | 2026-04-25 | ✓ | ✓ | ✓ | Pass |

### Descriptions
- **phenotype-journeys**: Journey sync and documentation routing tool
- **phenotype-omlx**: OMLX reference implementation for Phenotype (Python/DMG)
- **phenotype-ops-mcp**: Operations and MCP server infrastructure
- **phenotype-ops-mcp-fix**: MCP fixes and integration improvements (from bare-cua)
- **phenotype-org-audits**: Org-wide audit framework and cross-repo reporting
- **phenotype-previews-smoketest**: Preview environment smoke testing and CI validation
- **phenotype-registry**: Hexagonal service registry and package management
- **phenotype-shared**: Shared Rust crates and utilities
- **phenotype-skills**: Skill generation and binding framework
- **phenotype-tooling**: Quality gates and org-wide tooling infrastructure

## Critical Gap Alert

**phenotype-previews-smoketest**: Complete metadata gap (0/4 criteria)
- No README.md file
- No installation documentation
- No LICENSE file
- No status badges
- **Action required**: Either create complete documentation or mark as archived

## License Audit Summary

**Missing LICENSE** (3 of 10 repos, 30% gap rate):
- phenotype-previews-smoketest, phenotype-registry, phenotype-shared, phenotype-skills (4 repos)
- **Note**: Slight improvement vs R25's 60% gap; suggests tooling repos following consistent patterns

## Installation Documentation

**Undocumented (2 repos)**: phenotype-ops-mcp-fix, phenotype-org-audits
- Both are infrastructure/audit tools; install docs appropriate but missing
- Registry also lacks install docs (3 of 10, 30% gap)

## Status Badges

**All 10 repos missing badges** (0/10, 0% — consistent with R25's 10% rate)
- Infrastructure repos may not prioritize badges
- Could be automated via GitHub shields.io

## Summary

- **README completeness**: 9/10 (90%) — **slight decline from R25's 100%** due to previews-smoketest
- **Install instructions**: 7/10 (70%) — **improvement from R25's 60%**
- **License files**: 6/10 (60%) — **improvement from R25's 40%**
- **Status badges**: 0/10 (0%) — **consistent with R25's 10%, indicating systemic gap**

**Grade: B-** | Mixed metadata adoption; infrastructure tier shows stronger licensing but weaker badge adoption.

**Gaps identified**:
1. phenotype-previews-smoketest needs complete README + LICENSE
2. phenotype-registry needs LICENSE file
3. phenotype-shared + phenotype-skills need LICENSE files
4. All 10 repos missing status badges
5. phenotype-ops-mcp-fix + phenotype-org-audits need install documentation

### Recommended Next Action

1. **Critical**: Create README.md + LICENSE for phenotype-previews-smoketest
2. **Batch LICENSE addition**: Add Apache-2.0 to registry, shared, skills (3 repos)
3. **Add status badges**: Use GitHub shields for build/test status across all 10 (automation candidate)
4. **Install docs**: Add to phenotype-ops-mcp-fix and phenotype-org-audits
5. **Continue to Round 27**: Next 10 repos (~38 remaining in LEGACY tier)

**Status**: ✅ Round 26 Complete | Ready for batch cleanup or Round 27

---

**Cumulative Hygiene Trend (Rounds 21-26)**:
- README: 97% avg (trend: stable 90%-100%)
- Install: 65% avg (trend: improving 60% → 70%)
- License: 50% avg (trend: improving 40% → 60%)
- Badges: 5% avg (trend: flat 0%-10%)

**Observation**: License adoption trend improving (40% → 60% over 2 rounds); install docs recovering. Badge adoption remains critical gap across infrastructure tier.
