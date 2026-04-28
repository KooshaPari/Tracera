# Capability Recon & Reuse Plan (Initial Report)

Status: draft | Date: 2025-10-12 | Scope: pheno-sdk mono (./pheno-t), KInfra overlap

## Summary
pheno-sdk is a modular toolkit (1042 Python files) covering foundations (pydevkit), auth (unified auth adapters),
observability (observability-kit), transports (grpc-kit, stream-kit), workflows (workflow-kit/Temporal), CLI
(pheno_cli), file watching, config, and more. Biggest reuse wins: observability-kit (logging/metrics/tracing
scaffolds), auth adapters (unified OAuth2/MFA providers), pydevkit (http/retries/security/config), stream-kit
(middleware like circuit breaker/rate limit/retry/timeout). gRPC and MCP testing infra exist; vector stores are
present. Critical gaps: a unified plugin/registry API available across kits, turnkey OpenTelemetry bootstrap
(exporters pre-wired), and a standard for background jobs (choose APScheduler/Arq/Celery) to avoid divergence.
Recommendation: reuse pheno-sdk kits by default, extend via published hooks, and adopt mature externals
(FastAPI, httpx, pydantic v2, OpenTelemetry, Temporal, Typer/Click). Short term: publish capability index,
stabilize extension points, wire OTel exporters + recipes; mid term: unify registries and background jobs.

## pheno-sdk Capability Catalog (slice)
Module/Path | Capability | Maturity | Extension Points | Integration Notes | Owner | Docs/Tests
- adapter-kit/adapter_kit/* | DI, factories, registries | Beta | Container, Factory.Registry | Provide base ABCs; now exports unified Registry | Koosha | README, tests
- adapter-kit/adapter_kit/plugin_registry.py | Unified Plugin Registry | Stable | namespaced keys, metadata | Replaces legacy registries (removed) | Koosha | tests
- auth-adapters/src/pheno/adapters/auth/* | Unified auth adapters | Stable | providers, MFA, token mgmt | OAuth2/MFA providers; FastAPI/Flask extras | Koosha | README, examples
- grpc-kit/grpc_kit/* | gRPC integration | New | interceptors, DI glue | grpcio + optional OTel | Koosha | ADR 0003
- observability-kit/observability_kit/* | Logging, metrics, tracing, rate limiting | Beta | decorators, exporters | Wire OTel exporters; FastAPI/gRPC examples | Koosha | tests
- pydevkit/pydevkit/* | Foundations (http, retries, security, config, fs) | Mature | utils | Widely used; rich optional | Koosha | tests
- stream-kit/stream_kit/* | Streams (WS/SSE), middleware chain | Beta | middleware | Pluggable encoders/parsers | Koosha | examples
- workflow-kit/workflow_kit/* | Workflows (Temporal + patterns) | Beta | orchestrators, saga | temporalio adapters | Koosha | tests
- vector-kit/vector_kit/stores/* | Vector stores (qdrant/faiss/chroma) | New | store interface | Gate GPU deps; configure backends | Koosha | minimal
- pheno_cli/* | CLI (Click/Rich/Textual) | Beta | plugin commands, templates | Optional Typer entry | Koosha | README
- pheno/mcp/qa/* | MCP testing framework | Mature | adapters, runners, logging | Rich logs; fixtures | Koosha | many tests
- docs/adr/0002* | Unified plugin registry ADR | Proposed | Registry[T], entry points | Implemented in adapter_kit.plugin_registry | Koosha | docs

## Internal Reuse Ledger (initial)
Capability | Repo/Path | Status | pheno-sdk overlap | Tests | Owner
- Observability | KInfra/libraries/python/kinfra/* | Active | observability-kit logging/metrics; pydevkit logging | Yes | Koosha
- HTTP/Tunnels | KInfra | Active | stream-kit SSE/WS; pydevkit http | Yes | Koosha
- CLI | KInfra | Active | pheno_cli templates for infra CLIs | Minimal | Koosha

## External Options Matrix (curated)
Capability | Library | Version/License | Fit | Integration | Conflicts | Maintenance
- HTTP client | httpx | >=0.27, BSD | ✅ | async/sync, retries | None | Active
- Web framework | FastAPI | >=0.115, MIT | ✅ | Pydantic v2, ASGI | Starlette pins | Very active
- Validation | pydantic | v2, MIT | ✅ | models/settings | v1 compat | Very active
- CLI | Click/Typer | >=8.1 MIT / >=0.12 MIT | ✅ | Rich/Textual UX | Typer on Click | Active
- gRPC | grpcio | >=1.62, Apache | ✅ | interceptors | Protobuf pins | Active
- Observability | OpenTelemetry | >=1.24, Apache | ✅ | otlp/prometheus | Version coord | Active
- Metrics export | prometheus_client | >=0.20, MIT | ✅ | endpoint, multiproc | None | Active
- Background tasks | APScheduler/Arq/Celery | MIT/BSD | ⚠️ | choose baseline | Ops overhead | Active
- Workflows | temporalio | MIT | ✅ | workers, activities | Server required | Active
- Plugin system | pluggy/stevedore | MIT/Apache | ⚠️ | discovery, hooks | Namespace mgmt | Active
- Feature flags | Flipt/Unleash | MIT/Apache | ⚠️ | hosted/self-hosted | Network deps | Active
- Vector DB | Qdrant/FAISS/Chroma | Apache/FAISS | ⚠️ | adapters exist | GPU costs | Active

## Fit Assessment Matrix (first pass)
Capability | pheno-sdk | Internal reuse | External | Recommendation | Effort | Risks
- HTTP clients | pydevkit+httpx | KInfra uses httpx | httpx | Keep httpx+pydevkit wrappers | Low | None
- HTTP server | thin examples | KInfra APIs | FastAPI | Adopt FastAPI + obs-kit | Med | Migration
- gRPC | grpc-kit | — | grpcio | Use grpc-kit + OTel | Low | Interop
- Auth | auth-adapters | — | FastAPI deps | Use unified auth adapters | Low | Config
- Observability | obs-kit | KInfra logging | OTel+Prom | Wire exporters + recipes | Med | Infra
- Background tasks | partial | minimal | APScheduler/Arq | Choose standard + adapters | Med | Ops
- Workflows | workflow-kit | — | temporalio | Adopt when durable flows needed | Med | Server
- Streaming | stream-kit | — | ASGI | Reuse; polish middleware | Low | Polishing
- CLI | pheno_cli | KInfra | Typer/Click | Reuse + Typer option | Low | Consistency
- Plugins | adapters/registry | — | pluggy | Standardize Registry + optional hooks | Med | API churn
- Feature flags | — | — | Flipt/Unleash | Adopt external | Low | Network
- Vectors | vector-kit | — | providers | Keep adapters, document tradeoffs | Low | Provider drift

## Gaps & Proposals
1) Unified plugin/registry
- Action: Implement adapter_kit.plugin_registry.Registry[T]; re-export in adapter_kit.__init__.
- Next: migrate per-kit registries gradually; keep shims.
- Risks: API churn; dual systems during migration.

2) OpenTelemetry wiring
- Action: observability-kit to ship turnkey OTel setup (metrics/traces/logs) + Prometheus exporter + FastAPI/gRPC recipes.
- Next: examples + docs; small adapters for grpc-kit and pheno_cli templates.
- Risks: dependency/version coordination.

3) Background tasks baseline
- Action: endorse APScheduler (in-proc) + Arq (Redis) for async job queues; add adapters and guides.
- Risks: Redis ops overhead.

4) HTTP server scaffold
- Action: thin FastAPI bootstrap (health/metrics/auth/logging) in api-gateway-kit; avoid heavy reimplementation.
- Risks: scope creep.

5) Docs & tests consolidation
- Action: per-kit "Integration Notes" pages; add tests for adapters (authkit flows, stream-kit middleware chain).

## Appendix
Commands (read-only, ./pheno-t):
- find . -name pyproject.toml | sort
- grep -RInE "TODO|FIXME|WIP|ADR" -- .
- grep -RInE "FastAPI|aiohttp|httpx|requests|grpc|typer|click|pydantic|opentelemetry|rich" -- .
- find . -name "*.py" | wc -l

Notable Paths:
- Observability: observability-kit/observability_kit/*
- Auth: pheno/auth/*
- gRPC: grpc-kit/grpc_kit/*
- Streams: stream-kit/stream_kit/*
- Workflows: workflow-kit/workflow_kit/*
- Foundations: pydevkit/pydevkit/*
- CLI: pheno_cli/*
- MCP QA: pheno/mcp/qa/*



## Internal Reuse Ledger — KInfra scan (detailed)
Capability | Evidence (KInfra) | pheno-sdk mapping | Recommendation
- HTTP clients | adapters/cloud/neon.py uses httpx; smart_infra_manager uses requests | pydevkit.http + httpx | Standardize on httpx via pydevkit; add retries/backoff helpers
- Status/health/metrics | status_page/* generates HTML/JSON; many logging.getLogger calls | observability-kit + prometheus_client | Keep status page; add Prometheus/OTel exporters and gauges
- Process/tunnels | service_manager/*, tunneling/*, utils/process.py | process-monitor-sdk (monitor UI) | Keep KInfra core; reuse obs-kit for monitoring hooks
- Middleware (aiohttp) | middleware/* stack/fallback/health/templates | api-gateway-kit (FastAPI scaffold) | Keep aiohttp for KInfra; use gateway-kit in app services
- Config/env | config-kit (Config + loaders) | Use pheno-sdk config-kit exclusively; remove shims and legacy paths
- Registry | tunneling/registry.py | adapter_kit.PluginRegistry | Migrate to unified Registry (namespaced keys)
- CLI | minimal | pheno_cli | Use pheno_cli for scaffolds and tasks
- Background tasks | asyncio usage; no scheduler | APScheduler/Arq | Adopt baseline where scheduling needed

Notes
- KInfra primarily orchestrates local processes/tunnels and serves status/fallback pages; keep domain-specific code.
- Where HTTP servers are needed, prefer FastAPI + api-gateway-kit; KInfra middleware can remain aiohttp-focused.

## External Options Matrix — expanded notes
- OTel exporters (official docs): https://opentelemetry.io/docs/languages/python/exporters/ (Collector recommended)
- FastAPI observability example: https://github.com/blueswen/fastapi-observability (OTel + Prometheus patterns)
- Prometheus client libs: https://prometheus.io/docs/instrumenting/clientlibs/ (python)
- Temporal Python SDK: https://github.com/temporalio/sdk-python (workers/activities best practices)
- Background jobs: APScheduler (in-proc sched), Arq (async Redis), Celery (distributed, heavier). Choose APScheduler+Arq baseline.
- Plugin system: prefer pluggy (pytest-proven) or minimal custom Registry; stevedore if entrypoint discovery only is desired.

## Draft changes prepared (not pushed)
- adapter-kit:
  - adapter_kit/plugin_registry.py (new) – unified registry per ADR-0002
  - adapter_kit/__init__.py – export PluginRegistry
  - docs update: docs/kits/adapter-kit.md – section on PluginRegistry
- api-gateway-kit:
  - api_gateway_kit/middleware/stack.py (new) – compose gateway middleware around async handlers
  - api_gateway_kit/middleware/__init__.py – export add_gateway_stack
  - examples/pipeline_example.py (new)
  - docs update: docs/kits/api-gateway-kit.md – note on pipeline composition helper
- observability-kit: no code changes; bootstrap and FastAPI example already present

Next: optional ASGI adapter for api-gateway-kit to integrate with FastAPI/Starlette; expand registry adoption examples in other kits.
