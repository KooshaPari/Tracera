# API and Governance Audit

Updated 2026-07-28. This is an evidence ledger, not a claim of frontend/backend
parity. A route is considered implemented only when the gateway ownership,
authentication boundary, request/response schema, and a live contract test are
all present.

## Current topology

```text
Rich browser -> 127.0.0.1:18000 (nginx oracle gateway)
                 |-> python:8000 (published as 18080)
                 |-> go:8080     (published as 18081)
Stable Rust server -> loopback:8080 (separate product/runtime)
Grapheon         -> host:8080 (reserved; never bind or stop)
```

The gateway smoke contract (`scripts/rich-oracle-smoke.py`) validates the
loopback-only `:18000` origin and treats 401/403/405 as reachability, not as
successful business authorization. It does not prove payload schemas.

## Evidence

The Rust route registry (`crates/tracera-server/src/main.rs:527-551`) exposes
health, evidence, ingest, SDLC, problems, org-intel, and AI-DD analysis routes.
It does **not** expose the rich CRUD surface (`/api/v1/projects`,
`/api/v1/items`, `/api/v1/links`, graph/search/auth/agents routes).

The rich web source calls substantially more than the Rust registry, including
item-specs, test-suites, integrations, auth, storage, metrics, equivalence,
graph, search, and notifications. Existing mocks in
`frontend/apps/web/src/mocks/handlers.ts` are not server evidence.

The gateway config currently assigns `/api/v1/items` and `/api/v1/projects` to
Python before a broad Go matcher, while links are Go-owned. Graph/search and
traceability explicitly fail closed with 503 until authenticated ownership is
proven. This is a deliberate safety behavior, not parity.

## Prioritized governance actions

| Priority | Action | Release gate |
| --- | --- | --- |
| P0 | Publish one machine-readable route ownership manifest: path pattern, method, owner, auth policy, schema reference, live-test ID. | CI rejects unlisted routes and duplicate owners. |
| P0 | Add live contract tests through `:18000` for projects/items/links and preflight routes; assert status, content type, and schema, not only reachability. | No desktop promotion on 401-only smoke. |
| P0 | Make `VITE_API_URL` mandatory for rich builds or default only to `http://127.0.0.1:18000`; remove remaining `localhost:4000` defaults from production code. | Static scan has zero production `:4000` defaults. |
| P1 | Resolve ownership of graph/search/traceability and remove the 503 fail-closed placeholders only after auth and schemas are tested. | Gateway route tests prove owner and auth. |
| P1 | Generate OpenAPI/typed clients from the gateway-owned schemas; keep Rust evidence routes in a separate API namespace. | Generated client diff reviewed in CI. |
| P1 | Add CI drift check comparing frontend paths to the ownership manifest and Rust route registry. | CI reports missing/extra routes with provenance. |
| P2 | Mark the Go sidecar as optional only in explicit capability metadata; never display it healthy when absent. | Readiness UI reflects dependency state. |
| P2 | Add desktop startup contract asserting rich gateway origin `:18000`; legacy bundled `:18081` remains explicit opt-in. | Packaging test and launch log agree. |

## Non-claims / risks

- A 401 proves a route is reachable, not that the route's schema or business
  behavior is correct.
- Mock Service Worker responses do not satisfy production API parity.
- The Rust server on `:8080` and oracle gateway on `:18000` are different
  products. Do not route the rich frontend to `:8080`.
- The Go sidecar is not currently proven healthy by this audit; the gateway may
  serve Python-owned routes while Go-owned routes remain unavailable.
