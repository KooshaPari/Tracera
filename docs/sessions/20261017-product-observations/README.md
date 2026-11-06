# Q1: durable product observations and detector identity

This increment implements a technical API/persistence slice of Tracera's unified
product-model plus trace/session/memory intent. It does not establish a complete
CVP, real-user acceptance, automated repository/session ingestion, or production deployment.

## Contract and ownership

The HTTP contract is [product-observations.openapi.json](../../contracts/product-observations.openapi.json).
Rust typed boundary: `product/persistence.rs`; persistent adapters implement mandatory
`Store` methods. The old unmounted, in-memory `ObservationStore` scaffold was removed
rather than retained as a fallback. Existing source had no external callers.

| Method | Route suffix after `/api/v1/products/{product}/baselines/{baseline}` | Behavior                                                                         |
| ------ | -------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| POST   | `/observations`                                                      | Atomic accepted-intent snapshot plus append-only observations                    |
| GET    | `/observations`                                                      | Complete bounded persisted baseline model; real missing baseline is 404          |
| GET    | `/findings`                                                          | Actual freshness/coverage/contradiction detectors over that same persisted model |

Product, capability, baseline and observation identities are separate. Observation IDs
are unique within a product across baselines. Batch keys are scoped to product and
baseline. Canonically sorted intent/observation arrays make ordering immaterial to
replay. Changed immutable evidence or intent returns 409; invalid input/scope 422;
database failure/timeout 503; body over 10 MiB 413; denied product scope 403. A batch contains 1..500 observations,
at most 1,000 intents; a baseline model is bounded at 5,000 observations. Exceeding
capacity rolls back the batch. Conflicts never create partial models or receipts.

Capabilities referenced by observations must be accepted in the submitted baseline.
Existing global bearer/CSRF middleware remains in force. The mandatory deployment
allowlist is described below. Caller-specific product authorization remains an
unaccepted mature-product obligation.

## Current local setup and authorization

This setup describes source `8dd0e096ae35cabd17b1c057aa7c4daca60fb9b6`.
The process journeys below and in [BENCHMARK-BRIDGE.md](BENCHMARK-BRIDGE.md)
are historical receipts from earlier sources; their foreign-product 404 results
must not be interpreted as the current deployment allowlist behavior.

| Setting                    | Current behavior                                                                                                                                                                                                                                                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `TRACERA_PRODUCT_IDS`      | Mandatory for all four product operations: POST/GET observations, GET findings, POST benchmark-observations. Comma-separated exact, case-sensitive product IDs; surrounding whitespace is trimmed and empty entries ignored. Missing, empty, or nonmatching lists return 403 `product_access_denied` after middleware permits the request. |
| `TRACERA_AUTH_TOKEN`       | One process-global bearer credential. A nonempty value requires exact `Authorization: Bearer ...` on application routes. Missing/empty permits anonymous local mode on loopback, but never bypasses the product allowlist or mutation CSRF checks.                                                                                         |
| `TRACERA_BIND_ADDR`        | Explicit socket address; defaults to `127.0.0.1:8080` when neither this nor `PORT` selects an address. `PORT` selects `0.0.0.0:<port>`.                                                                                                                                                                                                    |
| `TRACERA_PUBLIC_BIND_MODE` | A non-loopback listener requires `authenticated-proxy`, `loopback-published`, or `private-network`, plus a nonempty `TRACERA_AUTH_TOKEN`; otherwise startup refuses the bind.                                                                                                                                                              |
| `DATABASE_URL`             | Required storage URL; use a fresh isolated SQLite database for local experiments.                                                                                                                                                                                                                                                          |

GET observations/findings require no CSRF headers. POST operations additionally
require `Origin: http://127.0.0.1:18000` (or a Referer with that exact origin)
and `x-csrf-token` obtained from this process's `GET /api/v1/csrf-token`.
The canonical origin stays on port 18000 even if the API uses another port.
Tokens are process-local, bounded to the most recent 1,024 issued tokens, and
must be reacquired after restart. The CSRF endpoint is bearer-exempt.

The following disposable loopback example uses a placeholder test credential,
not a production secret. From the repository root, launch an already-built
binary qualified against the source above (set `TRACERA_TEST_BINARY` to its path):

```sh
TRACERA_BIND_ADDR=127.0.0.1:19149 DATABASE_URL=sqlite::memory: \
  TRACERA_PRODUCT_IDS=' alpha, other ' \
  TRACERA_AUTH_TOKEN=ephemeral-local-example-only "$TRACERA_TEST_BINARY"
```

In another terminal, create a synthetic batch and submit it:

```sh
api=http://127.0.0.1:19149
csrf=$(curl -fsS "$api/api/v1/csrf-token" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
curl -sS -o /dev/null -w '%{http_code}\n' \
  -H 'Authorization: Bearer ephemeral-local-example-only' \
  -H 'Origin: http://127.0.0.1:18000' -H "x-csrf-token: $csrf" \
  -H 'Content-Type: application/json' \
  --data '{"product_id":"alpha","baseline":1,"idempotency_key":"setup-example","intents":[{"id":"storage","kind":"Capability","title":"Storage","description":"durability","status":"Accepted","baseline":1}],"observations":[{"id":"setup-obs","product_id":"alpha","baseline":1,"kind":"TestResult","result":"Passed","source":{"collector":"setup-example","version":"1","artifact_ref":"file:synthetic-example"},"recorded_at":"2026-10-16T00:00:00Z","capability_id":"storage"}]}' \
  "$api/api/v1/products/alpha/baselines/1/observations"
```

Expected POST status: 200. With the same bearer header, GET that observations
URL or its `/findings` sibling returns 200 after ingestion. A GET for an
allowlisted but absent baseline returns 404, demonstrating handler reachability.
A GET for product `denied` with valid bearer returns 403. Omitting the bearer
from a GET returns 401 in this configured-token example. For POST, omitting
the origin or issued CSRF token returns 403 even with valid bearer. Restarting
with `TRACERA_PRODUCT_IDS` unset or empty makes all four product operations
return 403 when bearer and (for POST) CSRF requirements are satisfied.

These controls are deployment allowlisting plus a shared bearer, not per-caller
ACLs or proof of tenant/product ownership. Benchmark tenant/run/session fields
remain unsigned asserted source metadata. Loopback without a configured bearer
is intentionally anonymous local mode; an allowlisted absent baseline can reach
its handler and return 404 in that mode. Stop the owned process after use;
this in-memory example loses its synthetic data on exit.

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
