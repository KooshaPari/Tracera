# Traceability Link Index

**Generated:** 2026-02-12
**Source:** docs/generated/traceability_links.json

## Overview

This document provides a comprehensive index of all traceability links discovered in the codebase, connecting functional requirements (FRs) to code implementations, tests, and documentation.

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Links** | 1,595 |
| **FRs with Links** | 5 |
| **Code Files Linked** | 0 |
| **Test Files** | 108 |
| **Documentation Files** | Multiple |

## Links by Type

| Link Type | Count | Description |
|-----------|-------|-------------|
| **tested_by** | 1,587 | Test files that verify functionality |
| **traces_to** | 6 | FR-to-FR or FR-to-User Story traceability |
| **implements** | 2 | Code implementations of FRs |

## Links by Confidence Level

| Confidence | Count | Percentage |
|------------|-------|------------|
| **Medium** | 1,589 | 99.6% |
| **High** | 6 | 0.4% |
| **Low** | 0 | 0.0% |

**Note:** Most links are auto-discovered through test file matching (medium confidence). High confidence links are explicitly declared in documentation.

## Top FRs by Link Count

| Rank | FR ID | Links | Status |
|------|-------|-------|--------|
| 1 | FR-DISC-001 | 2 | Active |
| 2 | FR-DISC-002 | 1 | Active |
| 3 | FR-DISC-003 | 1 | Active |
| 4 | FR-DISC-004 | 1 | Active |
| 5 | FR-DISC-005 | 1 | Active |

## Orphaned Functional Requirements

**Definition:** FRs with no code or test links.

| FR ID | Category | Status | Notes |
|-------|----------|--------|-------|
| FSR-ABS-001 | Functional Safety | Active | No implementation or test links found |

**Total Orphaned FRs:** 1

## Orphaned Code

**Definition:** Code files with no FR links.

**Note:** The current discovery system identified 0 code files with explicit FR links through docstrings or comments. This indicates that either:
1. Code files lack explicit FR references in their docstrings/comments
2. FR references use non-standard formats not captured by the pattern matching

**Recommendation:** Add explicit FR references to code file docstrings in the format:
```python
"""
Module description.

Implements:
    - FR-XXX-001: Description
    - FR-YYY-002: Description
"""
```

## Test Coverage Overview

| Category | Count |
|----------|-------|
| **Total Test Files** | 108 |
| **Test Links** | 1,587 |
| **Average Links per Test** | 14.7 |

**Test File Distribution:**
- Python tests: Located in `src/tracertm/tests/` and `tests/`
- Go tests: Located in `backend/`
- TypeScript tests: Located in `frontend/`

## Link Quality Metrics

| Metric | Value |
|--------|-------|
| **Auto-Discovery Rate** | 100.0% |
| **Manual Links** | 0 |
| **High Confidence Links** | 6 (0.4%) |
| **Medium Confidence Links** | 1,589 (99.6%) |
| **Low Confidence Links** | 0 (0.0%) |

## Recommendations

### 1. Increase Explicit FR References
- Add FR references to code file docstrings
- Use standardized format: `Implements: FR-XXX-001`
- Target coverage: >80% of code files with FR references

### 2. Improve Link Confidence
- Convert auto-discovered test links to explicit references
- Add FR references to test file docstrings
- Target: >50% high-confidence links

### 3. Address Orphaned FRs
- FSR-ABS-001: Add implementation and tests
- Review all FRs for implementation status
- Archive or implement orphaned FRs

### 4. Enhance Code Coverage
- Current: 0 code files with explicit FR links
- Target: >80% of production code with FR references
- Add FR references to service modules, API routers, and core modules

## Link Discovery Process

The link discovery system uses multiple strategies:

1. **Documentation Scanning:** Extracts explicit `Implements:`, `Tested by:`, `Traces to:` references from markdown files
2. **Code Docstring Analysis:** Scans Python, Go, and TypeScript docstrings for FR references
3. **Test File Matching:** Auto-discovers test-to-source relationships based on file naming conventions
4. **Confidence Scoring:**
   - High: Explicit declarations in documentation or docstrings
   - Medium: Auto-discovered through naming patterns
   - Low: Weak pattern matches (currently none)

## Next Steps

1. **Run validation:** `python scripts/python/validate_traceability.py --verbose`
2. **Review orphaned FRs:** Prioritize FSR-ABS-001 for implementation
3. **Add FR references:** Update code docstrings with explicit FR references
4. **Monitor coverage:** Track FR-to-code link growth over time
5. **Generate reports:** Use `python scripts/python/generate_status_dashboard.py` for updated metrics

## Related Documentation

- [Traceability System Guide](../guides/TRACEABILITY_SYSTEM_GUIDE.md)
- [FR Test Coverage Report](FR_TEST_COVERAGE.md)
- [Status Dashboard](STATUS_DASHBOARD.md)
- [QA Atlas](../reference/CODEBASE_QA_ATLAS.md)

---

*This document is auto-generated. Do not edit manually. Run `python scripts/python/discover_traceability_links.py` to regenerate.*
