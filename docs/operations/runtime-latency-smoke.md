# Runtime latency smoke

`scripts/runtime-latency-smoke.py` is a bounded, read-only local latency
smoke. It uses only Python's standard library and defaults to loopback, so it
does not require credentials or modify the database. The default mix covers
`/health`, `/ready`, `/evidence`, and `/sdlc-pm/sprints`.

Start the existing ephemeral runtime smoke in one terminal, then run:

```sh
python3 scripts/runtime-latency-smoke.py --base-url http://127.0.0.1:8080
python3 scripts/runtime-latency-smoke.py --requests 200 --concurrency 8 --json
```

The command reports p50/p95/p99/max latency, request rate, status/error
counts, and failure totals. A non-zero exit means a transport failure, a
server-side 5xx, or an explicitly configured latency threshold was exceeded.
HTTP 4xx responses are reported separately so a contract or auth failure is
not conflated with a runtime outage. The default path mix includes `/` so the
frontend and API are checked together.

For a bounded local SLO check, configure thresholds either with flags or
environment variables. Values are milliseconds; `0` disables a threshold:

```sh
TRACERA_LATENCY_P95_MS=250 TRACERA_LATENCY_MAX_MS=1000 \
  python3 scripts/runtime-latency-smoke.py --base-url http://127.0.0.1:18081
```

Threshold failures are reported as `latency threshold: FAIL: ...` on stderr
and return exit code 1. The check is read-only and has no service mutation.

This is a local smoke, not a capacity claim. Run it against a dedicated
staging deployment before changing production limits.

Latest local debug-binary sample (2026-07-19, SQLite, loopback, 80 requests,
concurrency 4, warmup 0): 1,967.30 requests/s, p50 0.81 ms, p95 1.38 ms,
p99 23.90 ms, 0 failures, and 0 client errors. The p99 tail is recorded
explicitly; repeat with warmup before comparing release-to-release.

CI runs the same bounded harness in `.github/workflows/runtime-latency-smoke.yml`.
That job builds the release server and frontend, starts an ephemeral loopback
SQLite instance, waits for `/health` and `/ready`, then records latency JSON.
The separate `scripts/test-runtime-latency-smoke.sh` contract test uses a
temporary standard-library HTTP server, so harness changes are testable without
requiring a pre-running Tracera service or credentials.

## Release-build note (macOS)

On 2026-07-19, a clean `CARGO_TARGET_DIR` release build on macOS failed while
loading the freshly compiled `sqlx_macros` dylib with `mis-aligned LINKEDIT
string pool`. Debug builds and runtime smoke remain healthy. Until the local
Apple linker/toolchain issue is isolated, release latency measurements must be
collected in CI/Linux rather than presented as a local release SLO.
