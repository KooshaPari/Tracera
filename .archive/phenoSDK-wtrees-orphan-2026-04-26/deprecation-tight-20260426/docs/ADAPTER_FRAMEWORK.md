# Adapter Framework

This document introduces the adapter framework that unifies technology-facing integrations for `pheno-sdk`. The design follows hexagonal architecture principles: the domain communicates only through ports, while adapters live at the edge translating between the core and external systems. Adapters announce their **abstraction level** so orchestrators can select the right integration for each deployment.

## Abstraction Level Taxonomy

Each adapter carries a numeric abstraction level between **0.01** and **0.99**. Lower values hug the underlying API, higher values offer opinionated, plug-and-play behaviour. Levels are grouped into the following bands:

| Level Band | Intent | Primary Concerns | Typical Use |
| ---------- | ------ | ---------------- | ----------- |
| `0.01 – 0.15` Direct Mapping | Mirror hardware or raw APIs with minimal indirection. | Latency, protocol fidelity, vendor quirks. | SDK shims, sensor drivers. |
| `0.16 – 0.35` Protocol Wrapper | Add lifecycle and error handling while keeping the call shape intact. | Connection pooling, retries, diagnostics. | HTTP clients, database connectors. |
| `0.36 – 0.55` Service Orchestration | Introduce policy, composition, and cross-cutting concerns. | Resilience, observability, policy injection. | Aggregators, workflow drivers. |
| `0.56 – 0.75` Domain-Aware Adapter | Translate payloads into canonical domain contracts. | Domain validation, schema consistency, invariants. | CQRS handlers, domain-aware queues. |
| `0.76 – 0.99` Plug-and-Play | Provide safe defaults and golden-path configurations. | Guardrails, compliance, progressive delivery. | Managed tunnels, turnkey observability. |

Normalising to this scale enables compatibility decisions to be automated. For example, a production deployment can prefer adapters above `0.6` while a lab environment opts for `0.2` to gain raw control.

## Core Primitives

`pheno.adapters.base` introduces shared primitives:

- `AdapterConfig` – captures names, abstraction levels, capabilities, and fixed parameters.
- `AdapterContext` – carries inbound/outbound ports plus ambient metadata.
- `PrimaryPort` & `SecondaryPort` protocols – mirror hexagonal architecture port semantics.
- `BaseAdapter` – lifecycle-aware adapter base class with `start`, `invoke`, and `stop`.
- `StatelessAdapter` – convenience subclass for adapters without explicit resources.
- `ABSTRACTION_TAXONOMY` with helper utilities `normalize_abstraction_level` and `describe_abstraction_level`.

All adapters inherit from `BaseAdapter` (or `StatelessAdapter`) to ensure consistent behaviour.

## Registry System

`pheno.adapters.registry.FrameworkAdapterRegistry` composes the existing core registry and adds framework-specific metadata handling:

```python
from pheno.adapters.registry import get_framework_registry
from pheno.adapters.base import AdapterConfig
from pheno.core.registry.adapters import AdapterType

registry = get_framework_registry()

registry.register(
    adapter_type=AdapterType.EVENT,
    adapter_class=MyHttpAdapter,
    name="partner_http",
    config=AdapterConfig(
        name="partner_http",
        abstraction_level=0.34,
        capabilities=("http", "rest"),
        fixed_parameters={"timeout": 5},
    ),
    tags=("partner", "critical"),
    description="Managed HTTP adapter for Partner API v2.",
)
```

Metadata recorded by the registry includes abstraction level, band label, capabilities, tags, and a serialised default configuration. A small helper factory ensures adapters receive an `AdapterConfig` and `AdapterContext`, optionally auto-starting them on creation.

### Helpful APIs

- `FrameworkAdapterRegistry.list_by_band(...)` – retrieve adapters whose levels fall within a range.
- `FrameworkAdapterRegistry.classify(...)` – look up the taxonomy band for a registered adapter.
- `FrameworkAdapterRegistry.get_underlying()` – access the underlying `AdapterRegistry` when lower-level operations are required.

## Example Adapters

The `pheno.adapters.examples` module registers reference adapters covering common integration points:

| Adapter | Type | Level | Highlights |
| ------- | ---- | ----- | ---------- |
| `HttpAdapter` (`http_client`) | `AdapterType.EVENT` | `0.32` | Protocol wrapper that can dry-run or execute HTTP requests. |
| `SqliteAdapter` (`sqlite_local`) | `AdapterType.DATABASE` | `0.28` | Direct SQLite access for migrations or diagnostics. |
| `InMemoryMessagingAdapter` (`in_memory_queue`) | `AdapterType.EVENT` | `0.62` | Domain-aware publish/consume with in-memory queue backing. |
| `LocalInferenceAdapter` (`local_inference`) | `AdapterType.LLM` | `0.74` | Wraps callable ML models while enforcing structured payloads. |
| `SshTunnelingAdapter` (`ssh_tunneling`) | `AdapterType.DEPLOY` | `0.88` | Emits ready-to-run SSH tunnel commands with guardrail defaults. |

These adapters demonstrate best practices referenced in canonical adapter pattern guidance (GoF Adapter Pattern, “Hexagonal Architecture: Three Principles” by Alistair Cockburn, and “Ports & Adapters in Practice” from ThoughtWorks Technology Radar) by separating configuration, lifecycle, and invocation responsibilities.

## Implementing a New Adapter

1. **Model the port contract** – define payloads and responses aligned with your domain ports.
2. **Choose an abstraction level** – use `describe_abstraction_level` to validate the intended band.
3. **Subclass `BaseAdapter` or `StatelessAdapter`** – implement `start`, `invoke`, and optional `stop`.
4. **Register the adapter** – call `FrameworkAdapterRegistry.register`, capturing metadata and defaults.
5. **Integrate with ports** – connect inbound/outbound ports via `AdapterContext` so the domain never depends on infrastructure details.

## Hexagonal Architecture Alignment

- **Ports & Contracts:** `PrimaryPort` and `SecondaryPort` protocols keep domain boundaries explicit.
- **Adapters as Infrastructure:** Concrete adapters reside at the edge, driven by configuration rather than hard-coded dependencies.
- **Configurability:** Abstraction levels and metadata enable environment-specific wiring without touching domain code.
- **Testability:** Stateless adapters and minimal side-effects make it easy to substitute in-memory implementations during testing.

## Operational Notes

- Adapters default to auto-start; pass `auto_start=False` should manual control be required.
- The registry serialises default configurations to aid observability and documentation tooling.
- Example adapters intentionally avoid network or vendor-specific dependencies to remain runnable inside the sandbox. Swap them out or extend them with production-ready libraries as needed.

By grounding adapters in explicit contracts, lifecycle management, and reproducible abstraction levels, `pheno-sdk` earns consistent integration behaviour across deployments ranging from experimental lab setups (levels `0.1 – 0.3`) to fully managed platforms (`0.8 – 0.99`).
