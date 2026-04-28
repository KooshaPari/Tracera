# Pheno-SDK Capability & Fit Matrix

This matrix maps capabilities to current pheno-sdk modules, internal reuse candidates, and external options with recommendations.

| Capability | Pheno Module(s) | Internal Reuse | External Option(s) | Fit | Recommendation | Notes |
|---|---|---|---|---|---|---|
| Dependency Injection | adapter-kit (di, registry) | — | dependency-injector (BSD-3) | Partial | Keep adapter-kit; add interop shim | Avoid dual DI confusion; document recipes |
| Configuration | config-kit | pydevkit.config | Pydantic Settings (MIT) | Excellent | Keep config-kit; align with Pydantic Settings | Consolidate overlap with pydevkit |
| HTTP API (ASGI) | api-gateway-kit (middlewares) | stream-kit examples | FastAPI/Starlette (MIT/BSD) | Excellent | Adopt FastAPI; keep thin middlewares | Provide plugins for tracing/auth |
| HTTP Client | pydevkit.http | — | HTTPX (BSD-3) | Excellent | Prefer HTTPX via pydevkit wrappers | Retries, timeouts, pools |
| Persistence (RDBMS) | db-kit | — | SQLAlchemy 2 (MIT) | Excellent | Use SQLAlchemy; keep adapters | Async engines supported |
| Object Storage | storage-kit | — | boto3/gcs/azure SDKs | Excellent | Keep storage-kit; standardize async | Auth profiles, retries |
| Streaming (WS/SSE) | stream-kit | — | Starlette websockets/SSE | Excellent | Keep as glue; rely on ASGI | Ensure backpressure, middleware |
| Events/Webhooks | event-kit | — | FastAPI webhooks + signing | Partial | Keep signers; align with FastAPI | HMAC signature conventions |
| Workflows (local) | workflow-kit | orchestrator-kit | — | Partial | Keep Saga/declarative | For local/non-durable flows |
| Durable Orchestration | — | orchestrator-kit | Temporal (MIT), Prefect/Dagster (Apache-2.0) | Excellent | Endorse Temporal; adapters | Clear guidance when to choose |
| Observability | observability-kit | pydevkit.logging/tracing | OpenTelemetry, structlog | Excellent | Standardize OTEL + structlog | Ship bootstrap helpers |
| CLI | cli-builder-kit, pheno_cli | — | Typer (MIT) | Excellent | Rebase on Typer | Keep UX wrappers |
| Auth/Security | auth-adapters, mcp-QA utils | pydevkit.security | Authlib, python-jose | Complete | Unified auth adapters | Token refresh, session mgmt |
| gRPC | — | — | grpcio (Apache-2.0) | Missing | Add grpc-kit | Interceptors, codegen helpers |
| Vectors | vector-kit | — | Qdrant/FAISS/Chroma | Partial | Add adapters; doc tradeoffs | Local vs remote backends |

## Risks & Considerations
- Ensure license compatibility (MIT/Apache-2.0 preferred).
- Avoid heavy runtime conflicts; favor optional extras.
- Provide stable adapter interfaces and version pin guidance.
