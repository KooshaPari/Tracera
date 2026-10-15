# Tracera OTel instrumentation spec (Tracera side)

Status: proposed, 2026-10-14. Implementer: pipeline agent. Backend (collector, Tempo/Loki/Prometheus, Grafana in podman on the desk behind Access) is owned by the desk lane; this spec only defines what Tracera emits and how it reaches the collector.

## 0. Grounding and conflicts
- User rule (engineering-principles, Oct 11): errors must be auto-captured, not pasted by him; browser error/console/failed-fetch beacon plus OTel; every deploy. Backend: OTel collector -> Tempo/Loki/Prometheus -> Grafana, self-hosted on desk.
- Repo today: `crates/tracera-server/src/observability.rs` has `init_tracing()` (fmt subscriber only, marked `#[allow(dead_code)]`) and `is_otel_configured()` (checks OTEL_EXPORTER_OTLP_ENDPOINT). No OTLP exporter is wired. So the server does not export anything yet. (Read via GitHub on default branch; not run.)
- CONFLICT: ADR-OBS-001 (Accepted 2026-08-30) names Jaeger for traces and Prometheus for metrics. The user's backend is Tempo/Loki/Prometheus/Grafana. Because we emit OTLP only, the code is backend-neutral; but the ADR needs an amendment (Jaeger -> Tempo, add Loki). Needs user/owner OK before editing the ADR; do not edit silently.
- Status of the existing browser beacon (noted shipped Oct 11 in memory): contract not re-read here; implementer should reconcile section 4 with it, not duplicate.

## 1. Architecture
```
 browser (web app) --OTLP/HTTP via same-origin /otel proxy--+
 Rust server (tracera-server, mcp, atlas) --OTLP gRPC-------+--> OTel Collector (desk, tailnet) --> Tempo / Loki / Prometheus --> Grafana
 CLI / MCP clients --OTLP (opt-in env) ----------------------+
```
- Single endpoint via env: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`, `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`.
- Browser never talks to the collector directly: Access-gated same-origin proxy route `/otel/v1/{traces,logs}` forwards to the collector, adds no secrets to the client, enforces size/rate caps.
- Failure mode: exporter errors must never break requests; bounded queue, drop-oldest, and a self-metric `tracera_otel_dropped_total`.

## 2. Resource attributes (all signals)
`service.name` (tracera-server | tracera-web | tracera-mcp | tracera-cli | tracera-atlas), `service.version` (git sha), `deployment.environment` (prod|staging|dev), `host.name` (desk|mac), `tracera.deploy.hostname` (tracera.pheno.studio), `tracera.db` (sqlite|postgres, so the pending Postgres cutover is visible).

## 3. Server (Rust)
1. Replace `init_tracing()` with: `tracing` + `tracing-opentelemetry` + `opentelemetry-otlp`; keep fmt layer for stdout (JSON in prod). Call it from `main` (currently dead code). Enable OTLP only when `is_otel_configured()`.
2. Spans: axum/tower layer (`tower-http` TraceLayer) producing one server span per request with `http.request.method`, `http.route` (matched route template, never raw path with IDs), `http.response.status_code`. Extract W3C `traceparent` (ADR already standardizes TraceContext).
3. DB spans around sqlx/diesel calls (whichever is used): `db.system`, `db.operation`, no query parameters.
4. Stub visibility (ties to gap GAP-021): any route that returns the stub envelope increments `tracera_stub_responses_total{route}` and sets span attribute `tracera.stub=true`. This makes "empty because unimplemented" queryable.
5. Domain spans: graph read/write (`tracera.graph.op`, `tracera.project.id`, item/link counts), matrix build, export, import, baseline create/diff, MCP tool call (`mcp.tool`, `mcp.client`), WorkOS auth callback (outcome only, no tokens).
6. Metrics (OTLP): `http.server.request.duration` histogram, `http.server.active_requests`, `tracera_db_pool_in_use`, `tracera_graph_items`/`tracera_graph_links` gauges per project, `tracera_stub_responses_total`, `tracera_otel_dropped_total`.
7. Logs: bridge `tracing` events at WARN+ to OTLP logs with trace_id/span_id so Loki entries link to Tempo traces. Every ERROR carries `error.type`.

## 4. Browser
1. Web SDK (`@opentelemetry/sdk-trace-web`) with fetch/XHR instrumentation; inject `traceparent` on same-origin API calls so a click links to the server span.
2. Auto-captured (ties to the user's "not pasted by him" rule): uncaught errors, unhandled rejections, `console.error`, failed fetch (status >= 400 or network error) with route template, React error boundary, and a distinct event `tracera.api.stub_or_empty_masked` when a wrapper swallows a failure into `[]`/`{}` (GAP-002/003/004/006). Fix the wrappers separately; this event proves when they fire.
3. Page/lens spans: `tracera.view` with `view.name`, render time, and `view.state` in {loading, ok, empty, error, not_implemented}.
4. Web vitals as metrics (LCP, INP, CLS).
5. Privacy: no item titles/bodies, no user email; user id is the WorkOS id hashed. Cap attribute length 256. Sampling: 100% errors, 10% traces default (env override).
6. Reuse the existing beacon endpoint if it already receives these; otherwise add `/otel` proxy as in section 1.

## 5. MCP / CLI / agents
- MCP tool calls emit a span per call with agent identity (`agent.name`, `agent.harness`) so the agents pane and Grafana share a key. Audit-log entries (cockpit Phase 1) carry `trace_id`.
- CLI: opt-in via `TRACERA_OTEL=1`; spans for each command; no payload content.

## 6. Dashboards and alerts (hand to desk lane as requirements)
- Dashboard "Tracera health": request rate/error rate/p95 by route; stub-response rate by route (target 0 for routes marked implemented); masked-empty events; DB pool; web vitals; graph size per project.
- Alerts: 5xx rate > 2% for 5 min; p95 > 1.5 s for 10 min; any `tracera.api.stub_or_empty_masked` on a route marked implemented; exporter drop rate > 0; no telemetry received from tracera-server for 10 min (dead-man).
- Where alerts go: Discord (comms SSOT per ssot-map) via the desk lane.

## 7. Acceptance (implementer, with receipts)
1. With endpoint unset: app runs, zero export attempts. With endpoint set: server spans appear in Tempo within 30 s of a request (screenshot/query receipt).
2. One browser action produces a single trace spanning browser -> server -> DB.
3. Forcing a failed fetch in the browser creates an error log in Loki with trace id, without the user doing anything.
4. A stubbed route increments `tracera_stub_responses_total`.
5. Kill the collector: requests still succeed, drop counter increments.
6. Overhead < 5% CPU under load test (ADR-OBS-001 target).
7. No PII/secret in sampled spans (check with a grep over a captured export).

## 8. Open questions for owner
1. ADR-OBS-001 amendment (Jaeger -> Tempo, add Loki): approve?
2. Collector address reachable from the desk podman services and from the browser proxy: desk lane to supply (tailnet hostname/port).
3. Default trace sampling 10% OK, or 100% while traffic is only one user?
