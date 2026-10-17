# Q1: durable product observations and detector identity

This increment implements a technical API/persistence slice of Tracera's unified
product-model plus trace/session/memory intent. It does not establish a complete
CVP, real-user acceptance, automated repository/session ingestion, or production deployment.

## Contract and ownership

The HTTP contract is [product-observations.openapi.json](../../contracts/product-observations.openapi.json).
Rust typed boundary: `product/persistence.rs`; persistent adapters implement mandatory
`Store` methods. The old unmounted, in-memory `ObservationStore` scaffold was removed
rather than retained as a fallback. Existing source had no external callers.

| Method | Route suffix after `/api/v1/products/{product}/baselines/{baseline}` | Behavior |
|---|---|---|
| POST | `/observations` | Atomic accepted-intent snapshot plus append-only observations |
| GET | `/observations` | Complete bounded persisted baseline model; real missing baseline is 404 |
| GET | `/findings` | Actual freshness/coverage/contradiction detectors over that same persisted model |

Product, capability, baseline and observation identities are separate. Observation IDs
are unique within a product across baselines. Batch keys are scoped to product and
baseline. Canonically sorted intent/observation arrays make ordering immaterial to
replay. Changed immutable evidence or intent returns 409; invalid input/scope 422;
database failure/timeout 503; body over 10 MiB 413. A batch contains 1..500 observations,
at most 1,000 intents; a baseline model is bounded at 5,000 observations. Exceeding
capacity rolls back the batch. Conflicts never create partial models or receipts.

Capabilities referenced by observations must be accepted in the submitted baseline.
Existing global bearer/CSRF middleware remains in force. Product filtering is an identity
boundary, not a new per-product authorization system. Per-product authorization remains
an unaccepted mature-product obligation.

## Assurance

- Four identity regression tests failed before detector repairs; detector suite then passed 17 tests.
- Two real SQLite persistence tests failed against the absent implementation, then passed.
- Extended SQLite tests prove restart, exact replay, concurrent replay, late-conflict rollback,
  immutable baseline/capability rejection, product/baseline isolation, canonical ordering,
  and capacity rollback.
- Actual PostgreSQL test on an isolated temporary local cluster proves concurrent exact replay,
  late-conflict rollback, reconnect persistence and foreign-product absence. It is explicitly
  ignored in the default suite and was separately invoked with the isolated database URL.
- Mounted application tests prove POST/read/detection, 404/422/409/503, anonymous 401,
  valid bearer access, and oversized 413. Existing auth is not bypassed.
- Full server verification: 96 library tests, 121 binary tests, 4 existing database tests,
  5 new SQLite tests passed. One PostgreSQL test separately passed.
- `cargo clippy -p tracera-server -p tracera-mcp --all-targets -- -D warnings` passed.
- Formatting and diff checks passed. macOS linker emitted an existing undocumented
  `-no_compact_unwind` warning during linked tests; no functional test failure resulted.

The first full run exposed a pre-existing stub-handler test threshold (`>=48`) despite
35 literal registrations in both exact main and candidate `router.rs`. The oracle now
asserts exactly 35 and still probes every discovered registration. Those are mini-router
handler tests, not proof of full application reachability. Extracted families retain
separate tests. Three existing `items_after_test_module` clippy failures were fixed by
moving unchanged test blocks to the ends of their files.

## Actual process journey

A local candidate on unique loopback port 19147 and fresh SQLite file accepted a seeded
stale observation, returned it durably, produced a real freshness finding with its evidence
ID, returned 404 for another product, restarted with byte-equivalent model output, and
returned an idempotent replay receipt. The owned candidate was stopped. This is seeded
technical evidence; it is not a discovered real-product discrepancy or user feedback.

Build binary SHA-256: `47a7a5bba1eaff02264b6c338ee0d748312c83b8012cd3b1d4512f91656e0daf`.
Runtime receipt is retained beside this note. Local cached builds fit the workstation;
no remote compute, shared database, production restart, screenshot, or merge was used.

## Next actual outcome

Connect a real trace/session evidence producer to this durable contract, retain source
anchors and provenance, then demonstrate a discrepancy, source update, and restart in
one bounded user journey. The generic evidence API alone does not complete that bridge.
