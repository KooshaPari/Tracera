# PR Series A3–A20: Implementation Plans

Status: Draft
Date: 2025-10-12
Owners: Pheno-SDK maintainers
Width: <= 120 cols

---

## A3: Finish HTTP consolidation (docs/examples sweep)
- Summary: Replace remaining uses of deprecated urllib HTTPClient with httpx factories.
- Scope: docs/, examples/, tests where applicable; add migration/codemod note.
- Changes: Update imports/usages, ensure quick starts show create_client/create_async_client.
- Affected: docs/kits/pydevkit.md, examples/, kit READMEs referencing HTTPClient.
- Tests: Grep-based check; run example snippets where feasible.
- Acceptance: No external usage of pydevkit HTTPClient remains outside its module.
- Risks/Mitigation: Missed refs → repo-wide grep; reviewers checklist.
- Rollback: Revert doc/example changes; keep HTTPClient as compat.
- Dependencies: A1.

## A4: httpx tracing hooks + testing utilities (respx)
- Summary: Standardize httpx request/response hooks for tracing; add respx for httpx mocking in tests.
- Scope: pydevkit/http/httpx_client.py, tests/, docs/guides.
- Changes: Optional event_hooks for OTel spans; testing utilities/fixtures using respx.
- Affected: pydevkit.http, any tests mocking HTTP.
- Tests: Unit tests verifying hooks fire; respx mocks for sample calls.
- Acceptance: Hooks can be enabled/disabled; examples produce spans; tests pass.
- Risks/Mitigation: Overhead → opt-in hooks; documented toggle.
- Rollback: Disable hooks; keep factories intact.
- Dependencies: A2.

## A5: Observability bootstrap helpers (OTel + Prom client)
- Summary: Thin convenience module to init OTel + Prometheus consistently.
- Scope: observability-kit bootstrap util; docs/guides; examples.
- Changes: Function(s) to set service/env/version, OTLP exporter (optional), add default collectors.
- Affected: observability-kit, templates using bootstrap.
- Tests: Unit tests on init functions; example app shows /metrics and spans locally.
- Acceptance: Minimal code to enable tracing/metrics; docs are clear.
- Risks/Mitigation: Conflicts with custom init → make optional, clearly documented.
- Rollback: Remove bootstrap; leave standard libs.
- Dependencies: A2.

## A6: /metrics integration in templates and examples
- Summary: Ensure Prometheus /metrics is wired in starter templates/examples.
- Scope: pheno_cli templates, example apps; docs updates.
- Changes: Add /metrics endpoint, default collectors; note on deployment.
- Affected: pheno_cli/templates, examples.
- Tests: Template smoke check; requests to /metrics return text exposition.
- Acceptance: GET /metrics returns valid metrics across templates.
- Risks/Mitigation: Endpoint conflicts → configurable path; doc note.
- Rollback: Remove endpoint wiring; keep docs.
- Dependencies: A5.

## A7: NATS connection factory (DI-ready)
- Summary: Provide standardized NATS (nc) + JetStream access via factory and DI patterns.
- Scope: New module for NATSConnectionFactory; config (URL/creds/TLS), health, shutdown hooks.
- Changes: Factory class/helpers; container registration patterns; examples.
- Affected: adapter-kit integration points; event-kit callers.
- Tests: Unit tests with mocks; optional integration if NATS is available.
- Acceptance: Example connects, publishes a message, shuts down cleanly.
- Risks/Mitigation: Cred variations → document options; robust error messages.
- Rollback: Keep as optional util; no cross-kit coupling.
- Dependencies: None.

## A8: JetStream utilities (streams/consumers/work queues)
- Summary: Helper APIs for common JetStream patterns with sane defaults.
- Scope: Create stream/consumer/work-queue helpers; backoff/ack policies parameters.
- Changes: Utility functions; documentation; example setup code.
- Affected: event-kit utils or new nats_utils module.
- Tests: Integration tests gated by env; unit tests for config generation.
- Acceptance: Example consumer receives messages; work-queue pattern demonstrated.
- Risks/Mitigation: Env reliance → optional integration; docker-compose recipe in docs.
- Rollback: Keep helpers internal; no callers forced.
- Dependencies: A7.

## A9: Refactor event-kit to NATS (publish/subscribe)
- Summary: Replace in-memory/custom bus with NATS JetStream streams/consumers.
- Scope: Map event APIs to js.publish and durable consumers; idempotency via headers/keys.
- Changes: event-kit core; remove legacy bus; docs migration.
- Affected: event-kit, its examples, dependent docs.
- Tests: Publish/consume integration test; idempotent handler test.
- Acceptance: At-least-once delivery with explicit acks; examples run.
- Risks/Mitigation: Ordering semantics change → handler idempotency guidance.
- Rollback: Feature flag old bus for one release if needed.
- Dependencies: A7–A8.

## A10: Webhook delivery via NATS + httpx; dead-letter support
- Summary: Robust webhook engine with queued retries and DLQ.
- Scope: Produce tasks to NATS work queue; httpx retry/backoff; DLQ stream; signed payloads.
- Changes: event-kit webhooks; metrics for attempts/success/failure.
- Affected: event-kit/webhooks, docs.
- Tests: Simulated transient failures then success; DLQ path verification.
- Acceptance: Reliable retries; DLQ populated after max attempts; metrics exported.
- Risks/Mitigation: Spikes → configurable concurrency/backoff.
- Rollback: Direct-send fallback behind feature flag.
- Dependencies: A4, A7–A9.

## A11: db-kit Postgres standardization (SQLAlchemy + asyncpg)
- Summary: Make Postgres canonical; deprecate other DB adapters.
- Scope: Async engine/session factories; repo patterns; health checks; pool tuning.
- Changes: db-kit core; docs; examples; deprecation notes for other adapters.
- Affected: db-kit, downstream examples.
- Tests: Async DB integration with Postgres; transaction boundaries; health checks.
- Acceptance: Examples run; deprecations documented; CI unit tests pass.
- Risks/Mitigation: Migration effort → provide Alembic templates and guide.
- Rollback: Keep non-PG adapters disabled by default for one release.
- Dependencies: None.

## A12: pgvector helpers and Alembic ops
- Summary: First-class embeddings with ANN index helpers.
- Scope: Column types; ivfflat/hnsw index creation params; Alembic ops to enable extension.
- Changes: db-kit helpers; docs; examples.
- Affected: db-kit.
- Tests: Migration apply/rollback; similarity queries produce results.
- Acceptance: Sample nearest-neighbor query works; indexes created.
- Risks/Mitigation: Extension missing → doc how to enable; guard code.
- Rollback: Helpers optional; no default dependency.
- Dependencies: A11.

## A13: Postgres FTS helpers
- Summary: Reusable utilities for tsvector + ranking with GIN.
- Scope: Generated columns; index helpers; search functions.
- Changes: db-kit FTS module; docs.
- Affected: db-kit.
- Tests: FTS search ranking test; migration examples.
- Acceptance: Demo search returns expected ranked results.
- Risks/Mitigation: Locale/stopwords → configurable text search config.
- Rollback: Optional module; no core coupling.
- Dependencies: A11.

## A14: Postgres-backed app-side rate limiter
- Summary: Token bucket with bursts; no Redis.
- Scope: DDL + helper functions; optional FastAPI middleware; partitioning guidance.
- Changes: New limiter module; docs; examples.
- Affected: api-gateway-kit or pydevkit; example services.
- Tests: Concurrency tests; rate/burst correctness; middleware behavior.
- Acceptance: Correct allow/deny; high-contention still stable.
- Risks/Mitigation: Hot keys → advisory locks + sharding; TTL cleanup task.
- Rollback: Disable middleware; leave helper off by default.
- Dependencies: A11.

## A15: Real-time simplification (WebSockets/SSE)
- Summary: Prefer Starlette websockets and sse-starlette; reduce bespoke orchestration.
- Scope: Update stream-kit surface; keep only minimal glue where it adds value.
- Changes: Remove complex channel middleware/encoders if redundant; docs.
- Affected: stream-kit, examples.
- Tests: WS/SSE examples run; simplified API remains functional.
- Acceptance: Leaner surface; parity documented.
- Risks/Mitigation: Feature loss → document alternatives or keep thin wrappers.
- Rollback: Legacy APIs behind deprecated compatibility layer.
- Dependencies: None.

## A16: Remove Redis references; add NATS KV examples
- Summary: Eliminate Redis from docs/code paths; prefer NATS KV or Postgres.
- Scope: Docs sweep; examples updated; concurrency/storage notes updated.
- Changes: Replace Redis samples; add NATS KV how-to.
- Affected: docs/, examples/; resource-management-kit docs.
- Tests: N/A (docs); sample code snippets run locally where feasible.
- Acceptance: Grep shows no Redis recommendations by default.
- Risks/Mitigation: Users needing Redis → appendix note with caveats.
- Rollback: Docs-only revert.
- Dependencies: A7–A8.

## A17: ADR updates and naming consolidation (ADR-0001)
- Summary: Apply canonical names; remove legacy parallel packages.
- Scope: api_gateway → api_gateway_kit; observability → observability_kit; TUI merge; imports/tests/docs.
- Changes: Codemods; import updates; removal of legacy dupes; migration notes.
- Affected: multiple kits and docs.
- Tests: Full test suite; imports sanity checks; lint.
- Acceptance: CI green; no references to legacy names remain.
- Risks/Mitigation: Wide blast radius → staged PRs per kit; thorough review.
- Rollback: Temporary shims (prefer to avoid) if critical breakages.
- Dependencies: A5–A6 (obs), general stability.

## A18: CLI templates update (web-service blueprint)
- Summary: Canonical template using NATS + PG + httpx + OTel/Prom + /metrics.
- Scope: pheno_cli/templates; docs; scaffold tests.
- Changes: New/updated template; wiring for DI, config, healthz/metrics; example docker-compose.
- Affected: pheno_cli.
- Tests: Scaffold then run basic checks; lint; unit test the template generator.
- Acceptance: Generated service starts; healthz and /metrics respond.
- Risks/Mitigation: Template drift → periodic validation job.
- Rollback: Keep old template as deprecated fallback.
- Dependencies: A5–A7, A11.

## A19: Observability dashboards and exporter examples
- Summary: Provide Grafana dashboards and OTLP exporter samples; remove custom exporters.
- Scope: Dashboard JSON; docs for OTLP endpoint config; remove bespoke exporters.
- Changes: observability-kit examples; docs.
- Affected: observability-kit; docs.
- Tests: N/A (manual validation); include screenshots/steps.
- Acceptance: Users can import dashboard; spans export with sample config.
- Risks/Mitigation: Env variance → mark optional; fallback docs.
- Rollback: Retain exporters if removal blocks users (last resort).
- Dependencies: A5–A6.

## A20: CI and tests hardening for new baseline
- Summary: Update CI to reflect new stack; improve test strategy (mock by default, opt-in integration).
- Scope: Workflows; license/banned-deps checks; toggled NATS/PG integration jobs; respx adoption.
- Changes: .github/workflows; tests; docs/contributing.
- Affected: CI + tests repo-wide.
- Tests: CI runs; unit tests pass without NATS/PG; integration jobs pass when services available.
- Acceptance: Reliable pipeline; clear contributor guidance.
- Risks/Mitigation: Flaky integration → short timeouts, retries, opt-in env.
- Rollback: Disable integration job; keep unit tests stable.
- Dependencies: A3–A4, A7–A14 as relevant.
