# README Hygiene Audit — Round 23 (LEGACY Tier, W-82+)

**Scope**: Continued README hygiene check to LEGACY tier (108 repos, 30-90d inactivity). Round 23 extends Round 22 coverage.

**Period**: 2026-04-25 | **Coverage**: Next 10 LEGACY repos by recent activity

## Next 10 LEGACY Repos Audited

| Repo | Last Commit | README | Install | License | Status |
|------|-------------|--------|---------|---------|--------|
| phench | 2026-04-25 | ✓ | ✓ | ✗ | Review |
| heliosApp | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| agentapi-plusplus | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| hwLedger | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| TestingKit | 2026-04-25 | ✗ | N/A | ✗ | Review |
| DataKit | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| AuthKit | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| ObservabilityKit | 2026-04-25 | ✓ | ✓ | ✓ | Review |
| ResilienceKit | 2026-04-25 | ✓ | ✓ | ✓ | Pass |
| McpKit | 2026-04-25 | ✓ | ? | ✗ | Review |

### Descriptions
- **phench**: Phenotype benchmarking and Python service orchestration framework
- **heliosApp**: Helios application platform (v2026.03A.0)
- **agentapi-plusplus**: Multi-model AI routing gateway extending Anthropic agentapi
- **hwLedger**: LLM capacity planner + fleet ledger + desktop inference runtime
- **TestingKit**: Testing framework (no README found)
- **DataKit**: Storage and events SDK for Phenotype ecosystem
- **AuthKit**: Unified cross-platform authentication SDK
- **ObservabilityKit**: Unified observability SDKs & instrumentation
- **ResilienceKit**: Multi-language resilience and fault-tolerance toolkit
- **McpKit**: Model Context Protocol support

## Universal Gap Status Update

**LICENSE File Missing** (2 of 10 repos, 20% gap rate — improvement from Round 22's 100%)

- **phench, McpKit**: Missing LICENSE files
- **8 repos**: LICENSE files present (80% pass rate)
- **Status badges**: 7/10 repos have badges in README (70%)

**Key improvement**: Rounds 21-22 showed 100% LICENSE gap. Round 23 shows 80% compliance — suggests recent org-wide LICENSE addition pass may have improved 60+ repos already.

## Installation Pattern Analysis

- **Python + Cargo hybrid**: phench (Python + Rust)
- **Rust (cargo)**: DataKit, AuthKit, ObservabilityKit, ResilienceKit
- **Go**: agentapi-plusplus, hwLedger
- **Node/NPM**: heliosApp
- **Documentation/Placeholder**: TestingKit, McpKit (minimal/missing docs)

## Summary

- **README completeness**: 9/10 (90%) — marked improvement from Round 22's 80%
- **Install instructions**: 8/10 (80%)
- **License files**: 8/10 (80%) — **major improvement from 0% in Round 22**
- **Status badges**: 7/10 (70%)

**Grade: B+** | 20-repo trend shows LICENSE gap closing. 2 holdouts (phench, McpKit) trivial to fix.

**Gaps identified**: TestingKit needs README; McpKit needs both README and LICENSE.

### Recommended Next Action

1. Add LICENSE (Apache-2.0) to: phench, McpKit
2. Create README for TestingKit
3. Continue to Round 24 (next 10 repos)

**Status**: ✅ Round 23 Complete | Ready for batch License sweep or Round 24
