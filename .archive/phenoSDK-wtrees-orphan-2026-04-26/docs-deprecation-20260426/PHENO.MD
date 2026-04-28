# Pheno SDK - Complete Architecture Blueprint

**Status:** `Active`  
**Version:** `0.5.0`  
**Last Updated:** `2025-10-19`  
**Next Review:** `2025-12-15`  
**Maintainers:** `Pheno SDK Architecture Guild`  
**Repository:** `Internal monorepo (kush/pheno-sdk)`  

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Summary](#architecture-summary)
4. [Hexagonal Layers & Component Inventory](#hexagonal-layers--component-inventory)
5. [Dependency Flows](#dependency-flows)
6. [Design Patterns](#design-patterns)
7. [Integration Points](#integration-points)
8. [Observability & Operations](#observability--operations)
9. [LOC & Complexity](#loc--complexity)
10. [Technical Debt & Risks](#technical-debt--risks)
11. [Action Plan](#action-plan)
12. [Document History](#document-history)
13. [Appendix A – LOC Violations](#appendix-a--loc-violations)

---

## 🎯 Project Overview

### Purpose
**What:** Pheno SDK is a modular platform toolkit that provides domain-driven building blocks for orchestrating services, MCP agents, AI workflows, and infrastructure automation.  
**Why:** It standardises how internal teams build and operate AI-enabled systems, enforcing hexagonal architecture boundaries, reusable adapters, and consistent operational tooling.  
**Who:** Internal platform engineers, AI/LLM workflow teams, QA automation, and infrastructure operations squads.

### Key Capabilities
- Full hexagonal architecture skeleton with domain, application, ports, and adapters (`src/pheno/domain`, `src/pheno/application`, `src/pheno/ports`, `src/pheno/adapters`).
- Rich infrastructure orchestration kits covering service lifecycle, tunnelling, proxy gateways, telemetry, and resource governance (`src/pheno/infra`, `src/pheno/kits`).
- MCP (Model Context Protocol) server, tools, and agent orchestration pipelines (`src/pheno/mcp`).
- LLM provider abstraction layer with OpenAI, Anthropic, Google, and LangGraph adapters (`src/pheno/llm`, `src/pheno/adapters/llm`).
- Quality, testing, and observability frameworks (QA dashboards, metrics collectors, tracing helpers).

### Project Metrics

| Metric | Current Value | Target | Status |
|--------|---------------|--------|--------|
| **Lines of Code** | ~296,505 (Python) | N/A | 📊 Baseline |
| **Test Coverage** | Unknown (coverage artefacts incomplete) | >80% | ⚠️ Needs measurement |
| **Active Users** | Internal platform teams | N/A | 📊 Informational |
| **Uptime** | Delivered via consuming hosts | 99.9% | ✅ No runtime SLA (library) |
| **Response Time (p95)** | Driven by host services | <300 ms | 📊 Host-dependent |
| **Technical Debt Ratio** | High (84 files >500 LOC) | <10% | ⚠️ Needs remediation |

### Stakeholders

| Role | Name/Team | Responsibility | Contact |
|------|-----------|----------------|---------|
| Product Owner | TBD (Platform PM) | Backlog prioritisation & roadmap | `#pheno-product` |
| Tech Lead | Pheno SDK Architecture Guild | Architecture governance & reviews | `#pheno-architecture` |
| DevOps Lead | Unified Infra Team | Release, packaging, CI/CD | `#pheno-devops` |
| QA Lead | MCP QA Guild | Quality automation & regression suites | `#pheno-qa` |

---

## 🛠️ Technology Stack

| Layer | Technologies | Notes |
|-------|--------------|-------|
| **Language / Runtime** | Python 3.11–3.13, asyncio | Async-first, multi-runtime support |
| **Web & APIs** | FastAPI, Starlette, Typer CLI, Textual TUI | Driving adapters for REST/CLI/TUI experiences |
| **Data / Persistence** | Supabase/Postgres (pgvector), SQLAlchemy, Redis, in-memory stores | Reusable repository adapters and resource templates |
| **Messaging & Events** | In-memory event bus, Redis Pub/Sub, async callbacks | Implements EventPublisher/EventBus ports |
| **LLM & AI** | OpenAI, Anthropic, Google, LangGraph, Autogen | Adapter registry selects providers at runtime |
| **Observability** | OpenTelemetry, Prometheus-style metrics, custom dashboards | Metrics collectors, tracing helpers, CLI telemetry |
| **Security** | Pydantic-based config, cryptography, password/encryption managers | Credential management & sandbox enforcement |
| **Testing & QA** | Pytest suites, MCP QA dashboards, snapshot tooling | Extensive test harness under `src/pheno/testing` |
| **Build & Tooling** | Poetry/uv, Ruff, Prospector, Bandit, Makefiles | Automation pipelines and quality gates |

---

## 🧠 Architecture Summary

Pheno SDK adopts a layered hexagonal architecture with a clear separation between business logic (domain + application) and infrastructural concerns (adapters + infra kits). Ports are expressed as Python protocols to maintain loose coupling, and adapters are registered through a unified adapter registry, which also powers kit-level dependency injection.

**Highlights**
- Domain entities (`domain/entities/*.py`) encapsulate business invariants and raise domain events without referencing infrastructure.
- Application use cases (`application/use_cases`) coordinate domain aggregates via repositories, event publishers, and service ports defined in `application/ports`.
- Adapter registry (`core/registry/adapters`) implements dependency inversion, enabling runtime selection, health checks, and plugin hooks.
- Infrastructure (`infrastructure`, `infra`, `providers`, `kits`) delivers driven adapters (SQLAlchemy, Supabase, Redis, telemetry, tunnelling) and operational automation.
- Driving adapters (REST API, CLI, MCP server, events) reside under `adapters/`.

**Hexagonal Best-Practices Alignment**
- ✅ **Explicit ports**: All critical dependencies are expressed as protocols (`application/ports`, `ports/*`).
- ✅ **Domain isolation**: Domain packages have no outbound imports to infrastructure.
- ✅ **Adapter registry**: Centralised wiring avoids implicit singletons and enables testing with in-memory adapters.
- ⚠️ **Adapter thinness**: Several infrastructure modules (e.g. `infra/*`) combine orchestration logic and UI orchestration, making them difficult to substitute.
- ⚠️ **Boundary enforcement**: Static checks exist (analytics/architecture), but cross-layer imports (e.g. workflows invoking infra helpers directly) should be monitored.
- ⚠️ **Complexity control**: 84 files exceed 500 LOC, challenging the maintainability expectation for hexagonal architecture.

---

## 🧱 Hexagonal Layers & Component Inventory

### Domain Layer (`src/pheno/domain`)

| Area | File(s) | Key Constructs | Notes |
|------|---------|----------------|-------|
| Base types | `domain/base.py` | `Entity`, `ValueObject`, `AggregateRoot`, `DomainEvent` | Provides aggregate life-cycle, event tracking, immutability contracts. |
| Auth | `domain/auth/types.py` | `AuthToken`, `SessionContext`, auth errors | Shared auth vocabulary for application and infra layers. |
| Entities | `domain/entities/{configuration,deployment,service,user}.py` | Aggregate roots for service lifecycle, deployment orchestration, configuration management, user lifecycle | Enforce invariants, emit events (`ServiceStarted`, `DeploymentPromoted`, etc.). |
| Events | `domain/events/{deployment,infrastructure,user}.py` | Domain event classes for lifecycle transitions | Used by use cases and event publishers. |
| Exceptions | `domain/exceptions/{base,deployment,infrastructure,user}.py` | Typed errors (Validation, State, NotFound) | Supports precise error handling in adapters. |
| Value Objects | `domain/value_objects/{common,deployment,infrastructure}.py` | Strongly typed IDs, status enums, ports, config keys | Guard input validation and state transitions. |
| Models | `domain/models/{process,project,resource,log}.py` | Read-model style projections and value abstractions | Support analytics, logging, and resource representations. |

### Application Layer (`src/pheno/application`)

| Area | File(s) | Responsibilities | Notes |
|------|---------|------------------|-------|
| DTOs | `application/dtos/{configuration,deployment,service,user}.py` | Data-transfer boundaries between adapters and domain | Enforce validation and conversion to VO/Entity types. |
| Ports | `application/ports/{repositories,events,services,queries,primary,comprehensive_database_port,database_port}.py` | Repository, event, service, and query protocols | Core hexagonal contracts; repository port drives all persistence adapters. |
| Auth | `application/auth/manager.py` | Application-level auth orchestration | Bridges domain auth types to infrastructure providers. |
| Use Cases | `application/use_cases/{configuration,deployment,service,user}.py` | Command handlers orchestrating domain aggregates and ports | Example: `CreateServiceUseCase` handles duplication checks, persistence, and event publication. |

### Port Catalogue (`src/pheno/ports`)

| Port Group | File(s) | Responsibilities |
|------------|---------|------------------|
| Auth Providers | `ports/auth/providers.py` | Unified protocol for external auth providers (e.g. OAuth flows). |
| MCP Integration | `ports/mcp/{provider,tool_registry,resource_provider,monitoring,session_manager}.py` | Contracts for MCP tool registration, resource provisioning, monitoring hooks. |
| Observability | `ports/observability.py` | Metrics/telemetry contract consumed by telemetry adapters. |
| Streaming | `ports/stream.py` | Abstract streaming interface backing WebSocket/SSE management. |
| Registry | `ports/registry.py` | Generic registry protocol used widely (tool registries, adapters, resources). |

### Adapter Catalogue (`src/pheno/adapters`, `src/pheno/infrastructure`, `src/pheno/providers`)

| Port(s) | Adapter(s) | Type | Notes |
|---------|------------|------|-------|
| Repository ports | `adapters/persistence/memory.py`, `adapters/persistence/sqlalchemy/*.py` | Driven | In-memory repos for testing; SQLAlchemy for Postgres/Supabase. |
| EventPublisher/EventBus | `adapters/events/{memory_publisher,redis_publisher}.py` | Driven | In-process + Redis Pub/Sub publishing. |
| Primary ports (HTTP) | `adapters/api/app.py`, `adapters/api/routes/*.py` | Driving | FastAPI surface exposing service/deployment/user endpoints. |
| CLI/TUI | `adapters/cli/{adapter.py,commands/*}` | Driving | Typer commands bridging CLI to use cases and infra orchestrations. |
| MCP Server | `adapters/mcp/server.py` | Driving | Wires MCP ports to agent orchestration. |
| LLM Providers | `adapters/llm/{openai_adapter,anthropic_adapter,google_adapter}.py` | Driven | Strategy adapters for LLM requests. |
| Prebuilt Infra | `adapters/prebuilt/{base,http_clients,databases}.py` | Driven | Ready-made adapters for HTTP clients, Redis, etc. |
| Security | `infrastructure/security/{auth_manager,encryption_manager,password_manager}.py` | Driven | Credential lifecycle, encryption helpers. |
| Adapter Registry | `core/registry/adapters/*.py`, `adapters/container.py`, `infrastructure/adapters/container.py` | Wiring | Service locator with health checks and plugin hooks. |

### Infrastructure Layer (Operational Kits)

**`src/pheno/infrastructure`** – Focused infrastructure helpers tightly coupled to the adapter registry (security, container bootstrap).

**`src/pheno/infra`** – Comprehensive operational platform layer:
- **Resource Governance:** `resource_manager.py`, `resource_coordinator.py`, `resource_reference_cache.py` manage Postgres/Redis/API allocations with health dashboards.
- **Tunnel & Proxy Management:** `tunnel_governance.py`, `tunnel_sync`, `proxy_gateway/*` deliver zero-trust tunnelling, health dashboards, and routing.
- **Service Lifecycle:** `service_manager`, `service_templates.py`, `service_infra/*` orchestrate process and deployment lifecycles.
- **CLI & Control Center:** `cli/*.py`, `control_center/desktop/*`, `cli_monitor.py` provide operator UX (Typer + Textual desktop).
- **Telemetry & Monitoring:** `telemetry/{collector,analyzer}.py`, `monitoring/*` integrate metrics, health checks, and resource status boards.
- **Fallback & Status Pages:** `fallback_site/*`, `status_page` serve failover status experiences.
- **Cleanup & Governance:** `cleanup_policies.py`, `process_governance.py`, `process_cleanup.py` enforce process hygiene.
- **Networking & Middleware:** `networking`, `middleware`, `tunneling` provide HTTP/gRPC wrappers, wildcard handlers, port allocation.

**Kits (`src/pheno/kits`)** – High-level packaged solutions:
- **Infra Kit:** `kits/infra/*` extends infra governance for multi-tenant orchestration (service manager, cleanup, resources, tunnel sync).
- **Deploy Kit:** `kits/deploy/*` automates deploy vendor integrations, CLI, and utilities.
- **LLM & MCP Kits:** Provide orchestrated flows over base adapters, enabling quick adoption.

---

## 🔁 Dependency Flows

```
Driving interfaces (API, CLI, MCP, Events)
        ⇣
Application Use Cases (`application/use_cases/*`)
        ⇣
Domain Entities & Value Objects (`domain/*`)
        ⇣
Ports (`application/ports`, `ports/*`)
        ⇣
Driven Adapters (`adapters/*`, `infrastructure/*`, `infra/*`, `providers/*`)
```

- **Inbound dependencies**: Driving adapters depend on application DTOs/use cases; they do not reach into domain or infrastructure directly.
- **Outbound dependencies**: Application layer depends only on domain and port protocols. No direct imports from infra were detected (`rg "pheno.infra" application` returns none).
- **Adapter registry**: `core/registry/adapters` mediates adapter instantiation, avoiding compile-time coupling.
- **Cross-kit usage**: `infra/*` and `kits/*` depend on adapter registry, ports, and resources. They should be treated as infrastructure services rather than part of the core domain.
- **Testing/QA**: `testing/mcp_qa` consumes infra modules directly, introducing bi-directional coupling risk; consider dedicated ports for QA instrumentation.

---

## 🧩 Design Patterns

| Pattern | Location(s) | Purpose | Notes |
|---------|-------------|---------|-------|
| **Aggregate Root & Domain Events** | `domain/base.py`, `domain/entities/*.py`, `domain/events/*.py` | Maintain business invariant boundaries and publish lifecycle events. | Supports event-driven integrations via `EventPublisher`. |
| **Repository Pattern** | `application/ports/repositories.py`, `adapters/persistence/*` | Abstract persistence mechanisms (memory vs SQLAlchemy/Supabase). | Enables test-time substitution and multi-backend support. |
| **Service/Use Case (Application Service)** | `application/use_cases/*.py` | Encapsulate application orchestration logic. | Pure functions + port invocations keep domain isolated. |
| **Adapter Pattern** | `adapters/`, `providers/`, `infrastructure/adapters/container.py` | Translate between external systems and port protocols. | Registry enforces consistent interface. |
| **Strategy / Factory** | `adapters/llm/*.py`, `providers/registry/providers.py`, `kits/infra/core/resources.py` | Select providers/resources at runtime based on configuration. | Adapter registry acts as factory with plugin hooks. |
| **Template Method** | `infra/service_templates.py`, `kits/infra/templates/*` | Provide scaffolding for service definitions, allowing subclasses to override specifics. | Supports standardized deployment processes. |
| **Observer / Event Bus** | `adapters/events/memory_publisher.py`, `adapters/events/redis_publisher.py` | Publish domain events to interested subscribers. | Async and sync handlers supported. |
| **Command Pipeline** | `shared/command_engine/*` | Execute command workflows with callback hooks. | Powers CLI automation and QA tooling. |
| **Service Locator / Registry** | `core/registry/adapters/*`, `ports/registry.py` | Central registry for adapters, ports, and toolkits. | Provides discovery, metrics, and plugin lifecycle. |
| **Builder** | `infra/resource_manager.py`, `infra/resource_templates.py` | Build resource graphs for infra orchestration. | Facilitates declarative resource definitions. |

---

## 🌐 Integration Points

| Integration | Location | Purpose | Notes |
|-------------|----------|---------|-------|
| **Supabase (Postgres, Storage, Realtime)** | `plugins/supabase/*`, `database/*`, `optimization/db_pooling.py`, `storage/backends/supabase.py` | Database, auth, storage, realtime listeners | Pooling, caching, and in-memory fakes provided. |
| **Postgres / SQLAlchemy** | `adapters/persistence/sqlalchemy/*`, `infra/resources` | Persistence adapter for primary domain entities | Async session support with mappers. |
| **Redis** | `adapters/events/redis_publisher.py`, `infra/resource_manager.py`, `workflow/orchestration/agents/task_manager/storage.py` | Event bus, caching, task storage | Optional dependency flagged in resource templates. |
| **LLM Providers (OpenAI, Anthropic, Google)** | `adapters/llm/*`, `llm/providers/*`, `providers/registry/providers.py` | Text/embedding generation, routing strategies | Adapter registry selects provider; fallback to echo/test fakes. |
| **LangGraph / Autogen** | `mcp/agents/adapters/langgraph_adapter.py`, `mcp/agents/adapters/autogen_adapter.py` | Agent orchestration for advanced workflows | Provide bridging to external agent ecosystems. |
| **Temporal Workflow** | `workflow/orchestrators/temporal/client.py` | Integrate with Temporal Cloud/Self-hosted orchestrators | Handles client bootstrap, namespacing, health. |
| **OpenTelemetry / Prometheus** | `observability/metrics/advanced.py`, `infra/telemetry/*` | Metrics instrumentation and export | Integrates HTTP, CLI, and process metrics. |
| **FastAPI** | `adapters/api/app.py`, `optimization/http_pooling.py` | REST API driving adapter and performance helpers | Provided with optimization utilities. |
| **Textual / Typer** | `cli/app/tui/*`, `infra/control_center/desktop/*`, `adapters/cli/adapter.py` | Operator UX (terminal + desktop) | Shared patterns for UI states and sockets. |
| **Vector Stores (pgvector)** | `vector/search/vector_search.py`, `vector/embeddings/service.py` | Semantic search and embedding generation | Supports Supabase pgvector and OpenAI embeddings. |
| **Security Providers** | `credentials/oauth/*`, `security/sandbox/manager.py` | OAuth automation, sandboxing, credential brokering | High LOC modules manage multi-tenant secrets. |
| **CI/CD Integrations** | `cicd/{manager,templates}.py`, `infra/services`, `kits/deploy/*` | Build and deployment pipeline orchestration | Templates for Render, GitHub Actions, etc. |

---

## 📈 Observability & Operations

- **Metrics:** `observability/metrics/advanced.py`, `ports/observability.py`, and `infra/telemetry/{collector,analyzer}.py` capture process metrics, latency, and adapter health. Metrics integrate with OpenTelemetry exporters.
- **Logging:** Central logging via `logging/core/logger.py` with structured logging support. Domain/events integrate through adapter registry instrumentation.
- **Health Checks:** `infrastructure/adapters/container.run_health_checks`, `infra/proxy_gateway/health_dashboard.py`, and QA dashboards validate adapter readiness.
- **Dashboards:** Textual dashboards under `infra/control_center/desktop/*` and QA TUI (`testing/mcp_qa/tui/*`) provide operator visibility.
- **Resilience:** `resilience/{circuit_breaker,error_handling}.py` wrap outbound calls. `optimization/rate_limiting.py` implements adaptive throttling.

---

## 📊 LOC & Complexity

### Summary by Major Area

| Area | Approx LOC (>Python only) | Notes |
|------|---------------------------|-------|
| `domain` | 3,615 | Lean domain core; healthy size. |
| `application` | 2,974 | Use cases + ports remain concise. |
| `adapters` | 6,439 | Manageable but growing; keep adapters thin. |
| `infrastructure` | 676 | Security bootstrap only. |
| `infra` | 38,873 | Significant operational surface; consider modularisation. |
| `mcp` | 16,311 | Agent orchestration complexity; ensure boundaries. |
| `llm` | 4,331 | Provider strategies and optimisers. |
| `testing` | 52,527 | Heavy QA automation footprint (TUI dashboards, OAuth harness). |

### Top 15 High-LOC Modules

| Rank | File | LOC | Impact |
|------|------|-----|--------|
| 1 | `testing/mcp_qa/tui/dashboard.py` | 2,692 | Monolithic QA dashboard; hard to test/extend. |
| 2 | `testing/mcp_qa/tui/widgets.py` | 1,815 | Dense widget definitions without modular splits. |
| 3 | `observability/metrics/advanced.py` | 1,171 | All-in-one metrics DSL; consider breaking into submodules. |
| 4 | `kits/infra/core/resources.py` | 1,164 | Resource catalog builder; isolate per-resource policies. |
| 5 | `testing/mcp_qa/oauth/credential_broker.py` | 1,104 | Complex credential flows; refactor by provider. |
| 6 | `mcp/agents/orchestration.py` | 1,053 | Core agent orchestrator; split per agent strategy. |
| 7 | `kits/infra/tunnel_sync.py` | 1,034 | Sync orchestration; separate scheduling vs I/O. |
| 8 | `testing/mcp_qa/adapters/widget_adapters.py` | 983 | QA adapter consolidation. |
| 9 | `infra/fallback_site/status_pages.py` | 983 | Static + dynamic fallback site generator. |
| 10 | `mcp/tools/decorators.py` | 952 | Decorator aggregation; reorganise by concern. |
| 11 | `kits/infra/service_manager.py` | 937 | Service orchestration; consider service-per-file split. |
| 12 | `testing/mcp_qa/oauth/flow_adapters.py` | 932 | OAuth flows; isolate providers. |
| 13 | `testing/mcp_qa/core/base/test_runner.py` | 929 | Legacy runner; evaluate replacement/retirement. |
| 14 | `testing/mcp_qa/auth/credential_manager.py` | 917 | Auth layering; modularise by credential type. |
| 15 | `testing/mcp_qa/core/reporters_old.py` | 905 | Legacy reporter; candidate for deletion. |

See [Appendix A](#appendix-a--loc-violations) for the full list of 84 files exceeding 500 LOC.

---

## ⚠️ Technical Debt & Risks

- **High LOC concentration:** 84 files exceed 500 LOC, primarily within QA tooling, infra governance, and LLM/MCP orchestration. This violates maintainability targets for hexagonal systems.
- **Monolithic QA dashboards:** `testing/mcp_qa/tui/*` and related OAuth flows tightly couple UI, networking, and storage, hindering reuse and testing.
- **Infra kit sprawl:** `infra/*` mixes CLI, UI, orchestration, and resource policies in shared modules, making upgrades risky and reducing adapter substitutability.
- **Observability overload:** `observability/metrics/advanced.py` centralises advanced DSL logic; onboarding new contributors is challenging.
- **Cross-layer leakage risk:** while no direct imports were found, `infra` modules often orchestrate use cases and domain logic implicitly; enforce boundaries via ports or service facades.
- **Coverage visibility gap:** Coverage artefacts are incomplete; lack of insights hides regressions.
- **Adapter registry single point:** Registry is powerful but complex; improper plugin handling could cause runtime failures. Ensure documented recipes for registering/unregistering.
- **Documentation drift:** Many README/plan documents exist (`PHASE_*`, `REPORTS`) but architecture blueprint was outdated; keep this document and ADRs in sync.

---

## ✅ Action Plan

1. **Modularise high-LOC modules**
   - Split `testing/mcp_qa/tui/dashboard.py` into feature-specific views and services.
   - Break `kits/infra/core/resources.py` into resource-type modules (database, cache, tunnel).
   - Extract provider-specific logic from `testing/mcp_qa/oauth/*` and `credentials/*`.
2. **Introduce guardrails for infra modules**
   - Define explicit ports for QA tooling and infra governance; avoid direct domain access.
   - Extend architecture analytics (`analytics/architecture/*.py`) with import rules to catch violations.
3. **Strengthen adapter thinness**
   - Ensure `infra/*` orchestrators delegate to use cases or services rather than embedding business rules.
   - Provide documentation + templates for writing new adapters that emphasise delegation.
4. **Improve observability modularity**
   - Refactor `observability/metrics/advanced.py` into collector, exporter, and DSL layers.
   - Document standard metrics port implementations and expected tags.
5. **Restore coverage insights**
   - Rewire CI to publish aggregate coverage (Pytest + optional smoke). Gate large PRs on coverage diff.
6. **Update ADRs and knowledge base**
   - Capture current adapter registry strategy, MCP agent orchestration, and infra governance decisions in ADRs.
   - Schedule architecture reviews aligned with `Next Review`.

---

## 📜 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.5.0 | 2025-10-19 | Codex (GPT-5) | Rebuilt blueprint from `BLUEPRINT.md`, added architecture analysis, LOC audit, and action plan. |

**Review Frequency:** Quarterly  
**Next Review:** `2025-12-15`

---

## Appendix A – LOC Violations

Files exceeding 500 LOC (Python, sorted descending):

```
2692	./testing/mcp_qa/tui/dashboard.py
1815	./testing/mcp_qa/tui/widgets.py
1171	./observability/metrics/advanced.py
1164	./kits/infra/core/resources.py
1104	./testing/mcp_qa/oauth/credential_broker.py
1053	./mcp/agents/orchestration.py
1034	./kits/infra/tunnel_sync.py
983	./testing/mcp_qa/adapters/widget_adapters.py
983	./infra/fallback_site/status_pages.py
952	./mcp/tools/decorators.py
937	./kits/infra/service_manager.py
932	./testing/mcp_qa/oauth/flow_adapters.py
929	./testing/mcp_qa/core/base/test_runner.py
917	./testing/mcp_qa/auth/credential_manager.py
905	./testing/mcp_qa/core/reporters_old.py
879	./llm/routing/ensemble.py
857	./storage/repository.py
850	./testing/mcp_qa/execution/intelligent_execution.py
847	./testing/mcp_qa/execution/optimizations.py
847	./testing/mcp_qa/core/optimizations.py
819	./kits/infra/core/cleanup.py
819	./infra/tunnel_governance.py
812	./testing/mcp_qa/collaboration/collaboration.py
799	./patterns/refactoring/extractor.py
795	./infra/project_context.py
795	./analytics/architecture/detector.py
786	./infra/cleanup_policies.py
780	./llm/protocol/optimization.py
762	./async/storage.py
749	./infra/cli/process_governance_cli.py
747	./quality/tools/pattern_detector.py
726	./infra/control_center/desktop/widgets.py
725	./kits/infra/smart_infra_manager.py
725	./infra/control_center/desktop/dialogs.py
722	./credentials/broker.py
715	./cli/simple.py
712	./workflow/orchestrator.py
707	./testing/mcp_qa/tui/widgets_compat.py
702	./async/orchestration.py
696	./mcp/agents/adapters/autogen_adapter.py
689	./cicd/templates.py
686	./credentials/cli.py
682	./analytics/architecture/patterns.py
676	./kits/deploy/cli.py
670	./infra/cli/project_cli.py
660	./testing/mcp_qa/testing/runner_old.py
656	./patterns/refactoring/cli.py
653	./infra/resource_reference_cache.py
653	./infra/proxy_gateway/health_dashboard.py
647	./security/sandbox/manager.py
638	./infra/process_governance.py
638	./architecture/hexagonal.py
633	./patterns/refactoring/validator.py
633	./credentials/hierarchy/models.py
620	./patterns/refactoring/analyzer.py
619	./kits/infra/core/ports.py
618	./analytics/architecture/extensions.py
617	./infra/fallback_site/config_manager.py
616	./resilience/error_handling.py
615	./analytics/architecture/validator.py
611	./workflow/orchestrators/temporal/client.py
611	./exceptions/types.py
608	./workflow/orchestration/cost/workflow_integration.py
606	./async/monitoring.py
605	./infra/telemetry/collector.py
604	./cicd/adapters.py
601	./kits/deploy/vendor.py
591	./testing/mcp_qa/core/streaming.py
590	./testing/mcp_qa/utils/database_utils.py
588	./infra/proxy_gateway/project_routing.py
584	./testing/mcp_qa/execution/pytest_plugin.py
577	./integration/validation/validator.py
571	./testing/mcp_qa/utils/helpers.py
571	./testing/mcp_qa/adapters/fast_http_client.py
568	./mcp/agents/adapters/langgraph_adapter.py
565	./credentials/oauth/automation.py
561	./ports/observability.py
558	./resources/manager.py
558	./infra/control_center/multi_tenant.py
555	./testing/mcp_qa/testing/auth_validator.py
554	./cicd/manager.py
553	./resources/rendering.py
552	./infra/telemetry/analyzer.py
545	./mcp/adapter_base.py
544	./workflow/orchestration/cost/optimizers.py
541	./resilience/circuit_breaker.py
539	./testing/mcp_qa/utils/auth_utils.py
539	./dev/utils/auth.py
537	./infra/resource_coordinator.py
536	./integration/reports/generator.py
535	./testing/mcp_qa/utils/metrics_utils.py
535	./infra/control_center/desktop/main_window.py
533	./quality/export_import.py
532	./vector/search/vector_search.py
530	./ui/tui/widgets/status_dashboard.py
529	./shared/command_engine/callback_handlers.py
527	./infra/global_registry.py
522	./testing/mcp_qa/testing/test_cache.py
522	./optimization/rate_limiting.py
520	./cli/app/tui/control_center.py
516	./observability/monitoring/command_runner.py
516	./llm/optimization/context_folding.py
514	./cli/app/tui/cli_bridge.py
511	./quality/integration.py
511	./infra/control_center/engine.py
510	./cli/app/tui/wireframes.py
508	./kits/deploy/utils.py
507	./cli/registry.py
503	./shared/command_engine/execution_pipeline.py
503	./mcp/resources/project_graph.py
502	./testing/mcp_qa/ui/rich_tui.py
502	./optimization/db_pooling.py
502	./infra/cli/fallback_cli.py
```
