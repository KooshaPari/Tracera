# ADR-TEST-001: 100% Public Function Test Coverage Policy

- **Status:** Accepted
- **Date:** 2026-08-30
- **Deciders:** Core Platform Team, QA Engineering, Release Engineering
- **Supersedes:** N/A
- **Review Date:** 2026-11-30

---

## Context

### Current State
Our codebase has grown significantly over the past year, and with this growth, the complexity of interactions between modules has increased. We have observed several critical issues in production that were not caught by our existing test suite:

1.  **Regression in Public APIs:** Changes to public interfaces occasionally break downstream consumers without being detected until integration testing or, worse, in production.
2.  **Inconsistent Coverage:** While some modules maintain high coverage, others rely on manual verification or ad-hoc testing.
3.  **Technical Debt:** "Legacy" code often lacks tests, making refactoring risky and expensive.
4.  **Trust Erosion:** Stakeholders have expressed concerns regarding the reliability of our releases due to the sporadic nature of bug discovery.
5.  **Unverified Integrations:** New integrations often ship without sufficient validation, leading to "Day 1" bugs when interacting with third-party services.
6.  **Merge Conflicts:** Without standardized test structures, contributors struggle to locate and extend existing tests, leading to duplicated effort and merge conflicts.

### The Gap
Our current coverage metrics focus primarily on line coverage or module-level thresholds, which fail to capture the criticality of public interfaces. A module might have 80% line coverage but miss testing 100% of its public API surface, leading to a false sense of security.

Specific gaps identified in recent audits:
- **Auth Module:** 3 public methods with no direct unit tests.
- **Data Layer:** 15% of public query builders lack coverage.
- **Utility Functions:** Only 40% of helper functions are covered, despite being used in critical paths.
- **Event System:** 6 public event handlers lack any test coverage despite processing critical payment data.
- **Config Module:** Public configuration loaders are tested only in integration environments, not in isolation.

### Definitions
For the purposes of this ADR, the following terms apply:

- **Public Function:** Any function, method, or trait implementation that is exported (`pub` in Rust, non-`_` prefixed in Python, non-`_` prefixed or documented in Go) and callable from outside its defining module.
- **Coverage Threshold:** The minimum percentage of public functions exercised by at least one test case.
- **Coverage Debt:** The set of existing public functions that do not yet meet the 100% threshold and are tracked for remediation.

### Strategic Goal
To ensure that all public-facing code -- the contract between our modules and the external world -- is rigorously validated before every release. We aim to shift quality left by making test coverage a prerequisite for code entry rather than a remediation step.

---

## Decision

We are adopting a **100% Public Function Coverage** policy for all modules within the `src` directory.

### 1. Tiered Enforcement Gates
To allow for the adoption of this policy without blocking immediate development needs, we will implement a three-tier enforcement system:

| Tier | Name | Behavior | Threshold |
| :--- | :--- | :--- | :--- |
| **Tier 0** | **Report** | Logs coverage results and warnings in CI. No blocking. | 0% (Baseline) |
| **Tier 1** | **Soft Fail** | Marks the build as unstable but allows merging. Requires manual override/approval from a lead. | 85% Public Functions |
| **Tier 2** | **Hard Fail** | Blocks the merge if the threshold is not met. Requires a code change or formal waiver. | 100% Public Functions |

**Rollout Timeline:**
- **Phase 1 (Weeks 1-2):** Tier 0 (Report Only). Teams analyze current state and file coverage debt tickets.
- **Phase 2 (Weeks 3-4):** Tier 1 (Soft Fail). Teams begin remediation of critical paths.
- **Phase 3 (Week 5+):** Tier 2 (Hard Fail). Full enforcement active for all new code.

**Escalation Path:**
When a PR triggers a Tier 1 soft failure, the author must either:
1. Add tests to reach the threshold, or
2. Obtain explicit approval from a designated coverage gatekeeper via a PR comment (`/cover-ok`).

When a PR triggers a Tier 2 hard failure, merging is blocked until the threshold is met or a formal waiver (see Section 4) is approved.

### 2. Test File Naming Conventions
To ensure discoverability and maintainability, all test files must follow these conventions:

- **Location:** Tests must reside in a `tests/` directory mirroring the source structure.
    - Example: `src/auth/login.rs` -> `tests/auth/login_test.rs`
- **Naming Pattern:** `<module_name>_test.rs` or `<module_name>_test.go` or `test_<module_name>.py`.
- **Test Function Prefix:** All test functions must be prefixed with `test_`.
- **Test Module Declaration:** In Rust, use `#[cfg(test)] mod tests;` to include the test module.
- **Fixture Files:** Shared test fixtures go in `tests/fixtures/<module_name>/`.
- **Test Helpers:** Reusable test utilities go in `tests/helpers/mod.rs` (or equivalent).

**Example Structure:**
```
src/
  auth/
    login.rs
    session.rs
tests/
  auth/
    login_test.rs
    session_test.rs
    fixtures/
      login_test_data.json
  helpers/
    mod.rs
```

### 3. CI Enforcement Details
- **Tooling:** We will utilize `cargo-tarpaulin` (Rust) / `go test -cover` (Go) / `pytest-cov` (Python) depending on the module's language.
- **Reporting:** Coverage reports will be uploaded as build artifacts and posted as comments on Pull Requests for visibility.
- **Scope:** Enforcement applies to *modified* files in the PR. New files must meet 100% coverage. Existing files will be brought into compliance via a "coverage debt" backlog.
- **Baseline Comparison:** The CI script will compare the PR's coverage delta against the main branch baseline. Regressions will be flagged separately from existing debt.
- **Retry Logic:** Coverage runs that fail due to transient test infrastructure issues (flaky tests, OOM kills) may be retried up to 2 times before being treated as genuine failures.

**Example CI Config (GitHub Actions):**
```yaml
- name: Run Coverage
  run: |
    cargo tarpaulin --out xml --output-dir coverage --skip-clean
- name: Enforce Threshold
  run: |
    python scripts/check_coverage.py coverage/cobertura.xml --min-pub-func 100
```

### 4. Waiver Process
Exceptions can be granted for:
- **Auto-generated code:** Code generated by protobuf, gRPC, or similar tools.
- **Deprecated modules:** Modules scheduled for removal within the current quarter.
- **Complex UI Logic:** Direct DOM manipulation logic that is difficult to unit test (must use integration tests instead).
- **FFI/Unsafe Code:** Functions that are inherently untestable in isolation due to system dependencies.
- **Proof-of-Concept Code:** Temporary code explicitly flagged for removal within 30 days.

Waivers must be requested via the "Tech Debt" issue tracker and approved by a Senior Engineer. All waivers expire after **90 days** and must be re-justified.

---

## Alternatives Considered

1. **Line Coverage Only (Rejected):** This was the previous approach and failed to catch public API regressions. Line coverage does not distinguish between exercised private helper logic and untested public entry points.
2. **90% Threshold (Rejected):** A 90% threshold would allow up to 1 in 10 public functions to be untested, which is unacceptable for critical modules like auth and payment processing.
3. **Branch Coverage (Rejected):** While branch coverage is more granular than line coverage, it still does not specifically target the public API surface and would require significantly more complex tooling.

---

## Consequences

### Positive
- **High Reliability:** Public APIs are rigorously tested, reducing the likelihood of breaking changes.
- **Refactoring Confidence:** Developers can refactor code with the assurance that regressions will be caught.
- **Documentation:** Tests serve as executable documentation for public functions.
- **Onboarding:** New team members can learn the system by reading tests.
- **API Stability:** Consumers of our public APIs can trust that changes are validated.

### Negative
- **Increased CI Time:** Running full coverage analysis may increase build times by 10-15%.
- **Initial Overhead:** Teams will need to spend time writing tests for existing uncovered code.
- **False Sense of Security:** 100% coverage does not guarantee 100% correctness (e.g., edge cases might still be missed).
- **Developer Friction:** Initial resistance to "red builds" may slow down velocity temporarily.

### Mitigation
- **Caching:** We will implement aggressive caching for coverage data to minimize CI time impact.
- **Dedicated Sprints:** We will allocate 20% of capacity in upcoming sprints specifically for "Coverage Debt" remediation.
- **Code Review:** We will rely on thorough code reviews to catch edge cases that unit tests might miss.
- **Training:** Conduct workshops on effective testing strategies to reduce the learning curve.

---

## Review Cadence

This ADR will be reviewed every **3 months** or upon significant changes to our tech stack or development process.

### Metrics to Monitor
- **PR Build Time:** Monitor for significant regressions.
- **Defect Escape Rate:** Track the number of bugs reaching production that would have been caught by coverage.
- **Developer Sentiment:** Survey developers quarterly on the impact of this policy on their workflow.
- **Coverage Trend:** Track the growth of total coverage over time to ensure we are converging on the goal.
- **Waiver Count:** Track the number of active waivers and their justification.

---

## References

- [Tracera Quality Standards](https://internal.tracera.com/standards/quality)
- [Coverage Tooling Docs](https://docs.tracera.com/tools/coverage)
- [Existing Test Guidelines](https://internal.tracera.com/contributing/testing)
- [Previous ADR on Unit Testing](https://internal.tracera.com/adr/TEST-000)

---

*This ADR is a living document and may be updated as we learn more from its implementation.*
