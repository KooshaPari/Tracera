# Q1 follow-on: benchmark envelope to durable observation

The existing `ingest::benchmark_run_to_issue` adapter is now mounted at:

`POST /api/v1/products/{product}/baselines/{baseline}/benchmark-observations`

The request explicitly assigns `product_id`, `baseline`, `capability_id`, accepted
`intents`, source `recorded_at`, and the existing benchmark `envelope`. The OpenAPI
contract is in `docs/contracts/product-observations.openapi.json`.

This is a fixture-qualified adapter, not an authenticated external producer integration.
Tenant/run/session identities are asserted source metadata, never proof of tenant ownership
or product authorization. Existing global bearer, CSRF, body limit and timeout remain active.

The adapter reuses existing run/session/attempt/status/replay validation. Schema version
1.0.0 and a bounded tenant identifier are required. It retains tenant, run, session,
attempt and replay identities in typed `ObservationSource.causality`, with SHA-256 of
the complete canonical JSON envelope. Changed result or provenance conflicts rather than
mutating evidence. Product/capability identities are never inferred from session IDs.

Status mapping: `passed -> Passed`, `failed/timeout -> Failed`, `cancelled -> Unknown`.
Recorded time is caller-supplied source time and must remain unchanged on retry.

## Verification

- Mounted route regression first failed 404, then passed ingestion, exact retry,
  alternate wire key ordering, readback, conflicting result/provenance 409,
  invalid session/schema/tenant/capability/future time 422, foreign path 422.
- Anonymous access to the new mounted route returns 401 when bearer protection is configured.
- Full suite: 96 library, 123 binary, four existing DB and six SQLite tests passed.
  An additional historical raw Q1 database payload replay test separately passed.
- Historical fixture `testdata/q1-legacy-observation-rows.json` contains actual raw rows
  from the owned Q1 synthetic process run, not newly serialized approximations. New code
  replays those unchanged stored bytes; optional causality None is omitted on serialization.
- Strict server/MCP all-target clippy, formatting and diff checks passed.
- A fresh local binary on unique port 19148 accepted the checked-in Helios envelope fixture,
  persisted causality, produced an evidence-linked freshness finding, survived process restart
  with identical read output, replayed without duplication and returned foreign-product 404.
  The owned candidate was stopped. See `benchmark-runtime-receipt.json`.

The preserved Q1 commit is `3fd3310fb98fdd2f9bca99eddd669f974fb1fb61`.
This follow-on is a separate commit and must not be credited to that immutable snapshot.
No merge, production call, shared database, screenshot or real-user validation occurred.

Next: authenticated producer binding and a genuine trace/session producer receipt,
then source-change reconciliation and a user-facing complete journey. The benchmark fixture
is explicitly insufficient evidence for those gates.
