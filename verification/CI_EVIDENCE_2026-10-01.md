# Tracera CI Evidence — 2026-10-01

**Candidate observed:** `c9d7dc81f82bf834b6a564c797e0596c0e5f4183`  
**Evidence class:** native GitHub CI observation; not product acceptance.

## Positive checks

Observed successes include:
- TS/JS tests;
- TS/JS lint;
- Python tests on 3.11, 3.12 and 3.13 in the primary CI;
- dependency review;
- security scan;
- CodeQL with no new alerts in PR changes;
- agent security scans for Rust/Python/JS;
- secret scan.

These are supporting evidence only.

## Negative / classified

### Rust lint — branch-local formatting failure

`cargo fmt --check` reports diffs across newly introduced/modified product surfaces including:
- `product/assessment.rs`;
- `product/dependencies.rs`;
- `product/invalidation.rs`;
- `product/invalidation_service.rs`;
- `product/persistence.rs`;
- SQLite product persistence;
- product DB integration tests.

**Classification:** branch-local implementation hygiene defect.

This is mechanically repairable but is production/source modification and therefore not changed in the current non-code-only phase.

### Rust tests — branch-local test/API mismatch

The native Rust test build fails compiling `tracera-server/tests/db_integration.rs` with five E0599 errors:
- three uses of a missing `SqliteStore::pool()` method;
- two uses of a missing `SqliteStore::connect(...)` associated function.

The failure occurs before the relevant integration tests execute.

**Classification:** concrete branch-local implementation/test-harness mismatch. Authored product-persistence tests are therefore **NOT EXECUTED**, not failed semantically.

The correct next runtime step is to reconcile the integration fixture with the actual supported `SqliteStore` construction/query surface without weakening the test oracle.

### Python lint / agent Python checks

Agent/alternate CI reports broad Python lint/test failures while the primary Python test matrix is green.

**Classification:** CI/profile divergence requiring job-specific reconciliation; primary Python runtime tests are positive evidence, but aggregate Python quality is not green.

### Required aggregate jobs

`ci / lint`, `ci / test`, `CI`, and agent-required aggregate are red because constituent jobs are red/skipped.

**Classification:** candidate is not CI-green.

## Promotion state

**Not promotable.**

The mature semantic contract remains accepted, but runtime/product completion remains false. Rust formatting is a concrete branch-local defect; Rust-test semantics and browser/historical evidence remain open.
