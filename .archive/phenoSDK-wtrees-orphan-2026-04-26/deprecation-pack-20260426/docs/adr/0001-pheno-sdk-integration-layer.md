# ADR 0001: Pheno-SDK as Integration Layer, Not Reinvention

- Status: Proposed
- Date: 2025-10-12
- Decision Makers: Pheno-SDK Core Team
- Tags: integration, architecture, standards, dependencies, observability, cli, workflows

## Context
Pheno-SDK contains 20+ focused kits covering DI/composition, configuration, persistence, interfaces (HTTP/CLI/streaming/events), workflows/orchestration, and observability. Many primitives are also solved well in mature OSS (FastAPI, Typer, HTTPX, Pydantic, SQLAlchemy, OpenTelemetry, Temporal, etc.).

We want to reduce maintenance burden and maximize developer ergonomics by adopting best-of-breed OSS primitives while keeping Pheno-SDK as the cohesive glue: shared config/DI/registries, adapters, patterns, and examples.

Constraints/Assumptions:
- Python 3.10+; Linux/macOS; containers/serverless [Assumption]
- Prefer permissive licenses (MIT/Apache-2.0)
- Projects across the portfolio should share conventions and tooling

## Decision
Adopt an integration-first strategy:

1. HTTP/API: Standardize on FastAPI/Starlette for ASGI; keep api-gateway-kit as a thin layer of middlewares and integration helpers.
2. CLI: Rebase CLI on Typer (Click ecosystem); provide thin wrappers in cli-builder-kit for shared UX/conventions.
3. Config: Keep config-kit (Pydantic v2 models + env/file loaders). Align closely with Pydantic Settings semantics.
4. HTTP client: Prefer HTTPX; expose retry/timeouts/pooling policies via pydevkit wrappers.
5. Observability: Standardize on OpenTelemetry for traces/metrics and structlog for structured logs. Provide setup helpers and FastAPI/HTTPX instrumentation.
6. Persistence: Prefer SQLAlchemy for relational ORM/queries. Keep db-kit adapters for Supabase/Postgres/Neon and storage-kit for cloud providers.
7. Workflows/Orchestration: Use Temporal for durable workflows; preserve workflow-kit Saga/declarative flows for in-process orchestrations. Provide adapters between them.
8. DI/Composition: Keep adapter-kit Container/registries as the core glue. Offer optional interop with dependency-injector via adapter shims.

## Alternatives Considered
- Build-everything-in-house: Higher maintenance burden, slower features, less ecosystem leverage.
- Hard-depend on a single orchestrator or logging stack: Reduces flexibility, increases lock-in.

## Consequences
Pros:
- Leverage mature, well-documented ecosystems; faster delivery
- Lower maintenance footprint; fewer bespoke primitives
- Better compatibility across projects; stronger docs/examples

Cons:
- Some migration effort (CLI to Typer, OTEL logging, Temporal workflows)
- Need interop layers (DI adapter; event/stream alignment)

## Scope & Phasing
- Phase 1 (quick wins):
  - Typer migration plan for cli-builder-kit/pheno_cli
  - Observability bootstrap helpers (OTEL + structlog) for FastAPI/HTTPX
  - Capability matrix docs and upgrade guides
- Phase 2:
  - Plugin registry mini-kit; refactor registries to use it
  - Temporal endorsement with examples; clear guidance when to use Saga vs Temporal
- Phase 3:
  - gRPC support (grpc-kit) with interceptors and DI integration
  - Auth system consolidation (Authlib + JWT), unify token/refresh flows across kits

## Open Questions
- Any org constraints on licenses (Apache-2.0 vs MIT) or cloud dependencies?
- Platform targets (serverless limits, offline needs, GPU requirements)?

## References
- Repo HEAD: see git log in appendix of Foundations Recon
- External libs: FastAPI (MIT), Typer (MIT), Pydantic (MIT), HTTPX (BSD-3), SQLAlchemy (MIT), OpenTelemetry (Apache-2.0), Temporal (MIT)
