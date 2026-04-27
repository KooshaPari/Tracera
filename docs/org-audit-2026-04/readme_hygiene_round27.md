# README Hygiene Audit — Round 27 (LEGACY Tier, W-82+)

**Scope**: Continued README hygiene check to LEGACY tier (10 repos, diverse domains). Extends Round 26 coverage.

**Period**: 2026-04-25 | **Coverage**: Next 10 repos by recent activity

## Next 10 LEGACY Repos Audited

| Repo | Last Commit | README | Install | License | Badges | Status |
|------|-------------|--------|---------|---------|--------|--------|
| Tokn | 2026-04-25 | ✓ | ✓ | ✓ | ✓ | Pass |
| Sidekick | 2026-04-25 | ✓ | ✓ | ✓ | ✗ | Review |
| PolicyStack | 2026-04-25 | ✓ | ✗ | ✓ | ✗ | Review |
| Metron | 2026-04-25 | ✓ | ✓ | ✓ | ✗ | Review |
| HeliosLab | 2026-04-25 | ✓ | ✓ | ✓ | ✗ | Review |
| FocalPoint | 2026-04-25 | ✓ | ✓ | ✓ | ✗ | Review |
| Eidolon | 2026-04-25 | ✓ | ✗ | ✓ | ✗ | Review |
| Dino | 2026-04-25 | ✓ | ✓ | ✓ | ✓ | Pass |
| DataKit | 2026-04-25 | ✓ | ✓ | ✓ | ✗ | Review |
| Conft | 2026-04-25 | ✓ | ✓ | ✓ | ✗ | Review |

### Descriptions
- **Tokn**: Token management and credential handling framework
- **Sidekick**: Multi-agent coordination and dispatch system
- **PolicyStack**: Policy engine and authorization framework
- **Metron**: Metrics aggregation and observability hub
- **HeliosLab**: Experimental Helios ecosystem testing environment
- **FocalPoint**: Agent focus/priority management and task routing
- **Eidolon**: Language model inference and routing service
- **Dino**: Foundational agent framework and skill system
- **DataKit**: Data processing and transformation toolkit
- **Conft**: Configuration management and validation framework

## Key Findings

**Strong baseline**: All 10 repos have README.md and LICENSE files — **100% on core metadata**.

**Install documentation gap**: 2 repos missing (PolicyStack, Eidolon) — **80% pass rate**, consistent with prior rounds.

**Status badges critical gap**: Only 2 repos have badges (Tokn, Dino) — **20% pass rate, significant drop from R26's 0% baseline** but still well below target.

## License Audit Summary

**All 10 repos have LICENSE** — **100% pass rate** (improvement from R26's 60%, R25's 40%). Suggests batch license addition in prior cleanup drove strong adoption.

## Installation Documentation

**Documented (8 repos)**: Tokn, Sidekick, Metron, HeliosLab, FocalPoint, Dino, DataKit, Conft
**Undocumented (2 repos)**: PolicyStack (large governance framework, likely complex install), Eidolon (inference service, may assume Docker/container knowledge)

## Status Badges

**Present (2 repos)**: Tokn, Dino
**Missing (8 repos)**: All except Tokn & Dino

Observation: Tokn has build badge (GitHub Actions); Dino has release badge. Others lack any CI/CD visibility badges despite active development. Opportunity for automated badge injection.

## Summary

- **README completeness**: 10/10 (100%) — **maintained from R26**
- **Install instructions**: 8/10 (80%) — **improvement from R26's 70%**
- **License files**: 10/10 (100%) — **significant improvement from R26's 60%**
- **Status badges**: 2/10 (20%) — **minor improvement from R26's 0%**

**Grade: A-** | Strongest round yet on core metadata (README + LICENSE). Install docs solid. Badges remain the primary systemic gap.

**Gaps identified**:
1. PolicyStack needs install/quickstart documentation
2. Eidolon needs inference/docker setup docs
3. 8 repos missing status badges (automation candidate for build/release badges)

### Recommended Next Action

1. **Add install docs**: PolicyStack and Eidolon (2 repos, ~30 min)
2. **Add shields badges**: Build status to 8 repos (automation via GitHub Actions → shields.io URLs)
3. **Continue to Round 28**: ~38 LEGACY repos remain
4. **Optional batch cleanup**: Batch install docs + badge automation across Rounds 25-27 (9 missing install, 22 missing badges)

**Status**: ✅ Round 27 Complete | **Cumulative coverage: Rounds 21-27 = 70 repos audited** | Ready for Round 28 or batch cleanup

---

**Cumulative Hygiene Trend (Rounds 21-27)**:
- README: 99% avg (trend: stable 100% last 4 rounds)
- Install: 71% avg (trend: improving 60% → 80%)
- License: 73% avg (trend: improving 40% → 100%)
- Badges: 13% avg (trend: improving 0% → 20%)

**Recommendation**: Establish automated badge injection for repos with GitHub Actions CI. Standardize install doc templates for governance/framework projects (PolicyStack, Eidolon). Consider Round 28 focus on infrastructure/experimental tier (remaining ~38 repos).
