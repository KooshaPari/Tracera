# Tracera Helios ingestion implementation

## Boundary

`tracera-server/src/ingest.rs::persist_issues` is the existing store-backed boundary that creates story, evidence, and trace-link records. `benchmark_run_to_issue` is a minimal adapter from a valid Helios `benchmark_run` JSON envelope into `NormalisedIssue`; callers can pass the result to `persist_issues` without dashboard changes.

## Contract test

Added `benchmark_contract_tests::valid_benchmark_envelope_maps_to_trace_issue`, asserting Helios source, passed status, and content-addressed run URI.

## Validation

- `cargo test -p tracera-server benchmark_contract_tests --lib --no-default-features` -> exit 101: package has no library target.
- `cargo test -p tracera-server --bin tracera-server benchmark_contract_tests` -> exit 124 after 15s while compiling dependencies (`aws-lc-sys`, sqlx, axum); no test result claimed.

The adapter is intentionally narrow: it validates run ID, preserves result status/replay hash in the issue body, and uses `urn:helios:run:<run_id>` as the evidence URI. No secrets or external network calls are introduced.
