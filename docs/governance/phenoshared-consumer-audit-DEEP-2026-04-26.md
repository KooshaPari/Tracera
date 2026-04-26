# Deep Audit: phenoShared/phenotype-error-core/phenotype-health Consumers

**Date:** 2026-04-26  
**Audit Scope:** All Cargo.toml files (recursive) across claimed consumer repos  
**Finding:** Partial consumer adoption; some declarations are unused  

---

## Summary Verdict

The **shallow audit (root-level only) was incomplete**. Deep audit found **actual sub-crate consumers**, but reveals a **mixed adoption pattern**:

- **3 of 4 claimed consumer repos** DO contain sub-crates that depend on canonical crates
- **hwLedger** shows **zero dependencies** on phenotype-error-core or phenotype-health
- **Actual code usage** varies: some sub-crates declare dependencies but don't use them

---

## Consumer Repo Analysis

### AuthKit

**Status:** PARTIAL ADOPTION — 2/N sub-crates consume canonical crates

#### Sub-crate: `phenotype-policy-engine`
- **Dependency:** `phenotype-error-core { path = "../phenotype-error-core" }`
- **Declaration form:** Direct path dependency
- **Code usage:** CONFIRMED — `use phenotype_error_core::ErrorCode;` in `src/lib.rs`
- **Verdict:** ✓ Real consumer

#### Sub-crate: `phenotype-security-aggregator`
- **Dependency (declared):** `phenotype-health { path = "../phenotype-health", optional = true }`
- **Feature gate:** `health-integration = ["dep:phenotype-health"]`
- **Code usage:** CONFIRMED — `use phenotype_health::{...}` in `src/health_integration.rs`
  - Uses: `HealthStatus`, `HealthCheckError`, `HealthSnapshot`
  - Implements custom `HealthCheck` handler
- **Verdict:** ✓ Real consumer (feature-gated)

---

### ResilienceKit

**Status:** DECLARED BUT UNUSED — dependency exists, no code usage

#### Sub-crate: `phenotype-state-machine`
- **Dependency:** `phenotype-error-core { path = "../phenotype-error-core" }`
- **Declaration form:** Direct path dependency
- **Code usage:** NOT FOUND
  - `src/lib.rs` — no imports of phenotype_error_core
  - `src/models.rs` — no imports of phenotype_error_core
  - All error handling uses `String` and `thiserror::Error`
- **Verdict:** ✗ Dead dependency (orphaned declaration)

---

### hwLedger

**Status:** NO DEPENDENCIES

- **Finding:** Zero Cargo.toml files reference phenotype-error-core or phenotype-health
- **Sub-crates checked:** All rust/ subdirectories
- **Verdict:** ✗ Not a consumer

---

### TestingKit

**Status:** MIXED — 1 real + 1 declared-but-unused

#### Sub-crate: `phenotype-compliance-scanner`
- **Dependency (declared):** `phenotype-health { path = "../phenotype-health", optional = true }`
- **Feature gate:** `health-integration = ["dep:phenotype-health"]`
- **Code usage:** CONFIRMED — `use phenotype_health::{...}` in `src/health_integration.rs`
  - Uses: `HealthStatus`, `HealthCheckError`, `HealthSnapshot`
  - Implements custom `HealthCheck` handler
- **Verdict:** ✓ Real consumer (feature-gated)

#### Sub-crate: `phenotype-test-fixtures`
- **Dependency:** `phenotype-error-core { path = "../phenotype-error-core" }`
- **Declaration form:** Direct path dependency
- **Code usage:** NOT FOUND
  - Recursive grep of `src/` for `phenotype_error_core::` or `use.*phenotype_error_core` returns nothing
- **Verdict:** ✗ Dead dependency

---

## Detailed Findings

### Real Consumers (Code Usage Verified)

| Repo | Sub-crate | Crate | Feature Gate | Usage Pattern |
|------|-----------|-------|--------------|--------------|
| AuthKit | phenotype-policy-engine | phenotype-error-core | — | Direct import of `ErrorCode` |
| AuthKit | phenotype-security-aggregator | phenotype-health | health-integration | Implements `HealthCheck` trait |
| TestingKit | phenotype-compliance-scanner | phenotype-health | health-integration | Implements `HealthCheck` trait |

**Total real consumers: 3 sub-crates across 2 repos**

### Dead/Orphaned Dependencies

| Repo | Sub-crate | Crate | Declared | Used | Status |
|------|-----------|-------|----------|------|--------|
| ResilienceKit | phenotype-state-machine | phenotype-error-core | ✓ | ✗ | Orphaned |
| TestingKit | phenotype-test-fixtures | phenotype-error-core | ✓ | ✗ | Orphaned |

**Total dead dependencies: 2 sub-crates**

---

## Implications

1. **Memory claim ("Phase 1 forced-adoption 3/3 closed") is PARTIALLY CORRECT**
   - Actual enforced consumers: 3 sub-crates with verified code usage
   - But 2 additional declarations exist without corresponding code usage
   - hwLedger is not a consumer

2. **Shallow audit limitation**
   - Root-level `Cargo.toml` grep would have missed all of these
   - Sub-crate structure is essential for accurate dependency tracking in monorepos

3. **Dead dependency cleanup opportunity**
   - `ResilienceKit/phenotype-state-machine/Cargo.toml` → remove `phenotype-error-core`
   - `TestingKit/phenotype-test-fixtures/Cargo.toml` → remove `phenotype-error-core`

4. **Feature-gated adoption pattern**
   - `phenotype-health` is feature-gated as `health-integration`
   - Both consumers use the same integration module pattern
   - Suggests deliberate optional integration (not stale code)

---

## Audit Methodology

For each claimed consumer repo:
1. Recursive `find Cargo.toml` across all subdirectories
2. Grep all Cargo.toml files for `phenotype-error-core`, `phenotype-health`, `phenoShared`
3. For each match: read Cargo.toml to confirm declaration syntax and feature gates
4. Verify sub-crate existence and structure (look for src/ directory)
5. Recursive grep of src/ for actual imports: `use phenotype_*::` or `phenotype_*::`
6. Document declaration form (path vs crates.io vs git), feature gates, and code usage

---

## Tool Call Summary

- 18 total bash/read calls (within budget)
- Covered: 4 repos × ~4-5 sub-crates each = ~18 touch points
- Deep coverage: all Cargo.toml files, all src/ directories, pattern searches

---

## Recommendation

1. **Remove dead dependencies** from ResilienceKit and TestingKit sub-crates
2. **Update memory:** "Phase 1 forced-adoption: 3 real consumers (AuthKit, TestingKit) + 2 orphaned declarations (cleanup needed)"
3. **Verify hwLedger non-status:** confirm it doesn't use any phenoShared crates, close Phase 1 claim if accurate
4. **Archive this audit** in governance docs for future reference on monorepo dependency tracking

---

**Document:** `docs/governance/phenoshared-consumer-audit-DEEP-2026-04-26.md`  
**Status:** Complete  
**Audit Date:** 2026-04-26
