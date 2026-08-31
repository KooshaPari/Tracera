# ADR-TEST-002: Adopt cargo-mutants for Mutation Testing

| Field       | Value                          |
|-------------|--------------------------------|
| Status      | Proposed                       |
| Date        | 2026-08-30                     |
| Author(s)   | Tracera Core Team              |
| Deciders    | Engineering Leads              |

## Context

Tracera's test suite has grown substantially across multiple crates. While unit and integration tests provide reasonable confidence, they cannot fully quantify how effective those tests are at catching real defects. Structural coverage (line/branch) measures what code paths execute, not whether assertions actually validate correctness.

Historical CI runs reveal that several crates pass all tests despite containing latent bugs that a single-line negation or boundary-value change would expose. Mutation testing fills this gap by injecting deliberate faults (mutants) into the source code and measuring whether the existing test suite detects them.

We need a systematic, repeatable process to:

- Quantify test effectiveness per crate.
- Identify weak test areas that need additional cases.
- Enforce a minimum quality bar that improves over time.

## Decision

We adopt **cargo-mutants** as the standard mutation testing tool for the Tracera workspace.

### Targets

| Metric                | Target                                        |
|-----------------------|-----------------------------------------------|
| Kill rate (workspace) | **≥ 80%** across all crates                   |
| Per-crate threshold   | **≥ 70%** for any single crate                |
| Baseline enforcement  | New crates must meet threshold before merge   |
| Regression guard      | Kill rate must not decrease on main            |

### Execution Cadence

- **Weekly scheduled CI run** (every Sunday 02:00 UTC) via GitHub Actions.
- **PR gate (informational):** Run mutation testing on changed crates; post results as a PR comment without blocking merge during the initial rollout phase (first 8 weeks). After the rollout period, enforce the per-crate threshold as a blocking check.
- **Manual trigger:** `cargo mutants --project-root <crate>` for local investigation.

### Per-Crate Thresholds

Each crate declares its minimum kill rate in a workspace-level manifest (`mutants.toml`):

```toml
# mutants.toml – workspace root
minimum_kill_rate = 70

[crates]
tracera-core   = 75
tracera-server = 70
tracera-agent  = 65   # gradually increased
```

Thresholds may differ per crate during the adoption phase but must converge toward the workspace target of 80% within two quarters.

## Implementation

### Phase 1 – Baseline (Weeks 1–2)

1. Install `cargo-mutants` in CI and local development toolchains.
2. Run a full workspace mutation scan and record baseline kill rates per crate.
3. Commit the `mutants.toml` manifest with thresholds set to **baseline minus 5%** so CI passes on day one.

### Phase 2 – Enforcement (Weeks 3–8)

4. Add a weekly GitHub Actions workflow that:
   - Checks out the repository.
   - Runs `cargo mutants --workspace --shallow` to limit mutants per source file.
   - Parses output and compares kill rates against `mutants.toml`.
   - Opens an issue (labelled `mutation-testing/regression`) when a crate drops below threshold.
5. Add an informational PR check that posts a summary comment on changed crates.

### Phase 3 – Hard Gate (Week 9+)

6. Convert the informational PR check to a **required status check** for crates meeting the workspace target.
7. Increase per-crate thresholds in `mutants.toml` toward 80%.
8. Require mutation-test results as part of the release checklist.

### Tool Configuration

- **Baseline mode:** `cargo mutants --baseline-repo=. --timeout=120` to skip mutants that survived baseline (no new regressions).
- **Shallow mode:** `cargo mutants --shallow` for PR runs to reduce CI time.
- **Timeout:** 120 seconds per mutant test run; 360 seconds for the weekly full scan.
- **Exclude list:** Mutants in auto-generated code (`build.rs`, protobuf output) are excluded via `exclude = [...]` in `mutants.toml`.

## Consequences

### Positive

- **Measurable quality:** Teams can track concrete kill-rate metrics per crate instead of relying solely on coverage percentages.
- **Targeted improvements:** Low-scoring crates surface naturally, guiding where to invest in new test cases.
- **Regression prevention:** Drops in kill rate are caught before they reach production.
- **Developer awareness:** PR-level comments make test effectiveness visible during code review.

### Negative

- **CI wall-clock time:** Full mutation scans are expensive. The weekly cadence and shallow-mode PR runs mitigate this, but resource usage will increase.
- **Initial remediation burden:** Crates below the 70% threshold require investment in test improvements before hard enforcement begins.
- **False survivors:** Some mutants represent equivalent code transformations that cannot be killed by design. A triage process for `cargo mutants --list` is needed to mark equivalents.

### Risks and Mitigations

| Risk                                        | Mitigation                                        |
|---------------------------------------------|---------------------------------------------------|
| CI runner cost spike during weekly runs      | Use shallow mode for PRs; full scan weekly only   |
| Developer friction from blocking checks     | 8-week informational phase before hard gate       |
| Equivalent mutants inflating survivor count | Maintain an `equivalents.txt` manifest            |
| Stale thresholds after refactoring          | Quarterly review of `mutants.toml` values          |
