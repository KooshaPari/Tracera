# ADR — dispatch-mcp

Repo-local architecture decisions for the Phenotype dispatch/orchestration
tools. dispatch-mcp provides MCP-based dispatch, orchestration, and
worker-management facilities for the Phenotype fleet.

---

## ADR-071 — MCP Dispatch Protocol

**Status:** Accepted

**Context:** Agents need a standardized protocol to dispatch tasks to worker
tiers. Without a formal protocol, each agent implements ad-hoc dispatch,
fragmenting the orchestration surface.

**Decision:** Adopt a lightweight MCP-based dispatch protocol where a
dispatch request carries a `profile` (worker tier identifier) and a
`prompt` (the task specification). The MCP transport carries the full
request/response lifecycle including status, error, and result channels.

**Rationale:** MCP provides a well-defined JSON-RPC transport layer with
streaming support, tool discovery, and resource exposure. Building dispatch
on top of MCP avoids re-inventing transport and lets dispatch workers be
discoverable MCP servers themselves.

**Fleet Cross-References:**
- ADR-003 (McpKit Merged) — MCP tooling foundation
- ADR-037 (pheno-mcp-router Substrate) — MCP routing substrate
- ADR-050 (Router Rebuild: Option B) — router architecture that dispatch workers consume
- ADR-052 (Plugin SDK Spec) — plugin model for dispatch worker extensions

---

## ADR-072 — Multi-Provider Routing for Dispatch

**Status:** Accepted

**Context:** dispatch-mcp must route tasks to the appropriate LLM provider
(OpenAI, Anthropic, Google, local models) based on task requirements,
cost constraints, and availability.

**Decision:** Implement provider selection as a pluggable dispatch profile.
Each profile declares a preferred provider list, fallback order, and cost
ceiling. The dispatch layer selects a provider per task, not per session.

**Rationale:** Per-task provider selection allows cost optimization (cheap
model for simple tasks, reasoning model for complex ones). Pluggable
profiles let repo owners define their own dispatch policies without
modifying the dispatch core.

**Fleet Cross-References:**
- ADR-050 (Router Rebuild: Option B) — router provider-selection patterns
- ADR-051 (Bifrost as Library) — transport-layer provider abstraction
- ADR-052 (Plugin SDK Spec) — plugin interface for custom provider selectors
- ADR-040 (Test Coverage Gates) — coverage requirements for provider shims

---

## ADR-073 — Worker Lifecycle Management

**Status:** Accepted

**Context:** Dispatch workers may be long-running (server-mode) or
ephemeral (per-task). Without lifecycle management, workers leak resources
and task isolation is unpredictable.

**Decision:** Implement a three-state worker lifecycle: `idle` (pooled,
warm), `active` (processing a task), `draining` (finishing in-flight tasks,
not accepting new ones). Workers report their state via MCP resource
exposure. The dispatch orchestrator manages transitions and enforces a
configurable `max_drain_seconds` timeout.

**Rationale:** Three-state lifecycle is industry-standard (Kubernetes,
Nomad) and maps cleanly to MCP resource/status patterns. The orchestrator
can scale the worker pool based on active vs. idle counts.

**Fleet Cross-References:**
- ADR-006 (Circuit Breaker Pattern) — circuit breaker for worker health
- ADR-046 (Federation mTLS + OIDC) — worker-to-orchestrator authentication
- ADR-048 (Substrate Graduation Path) — worker lifecycle graduation checks
- ADR-049 (App-Substrate Drift Detector) — lifecycle policy drift detection

---

## ADR-074 — Dispatch Observability & Tracing

**Status:** Accepted

**Context:** Debugging dispatch failures requires end-to-end trace context
across the orchestrator, dispatch worker, and LLM provider call. Without
tracing, a failure at any layer is opaque.

**Decision:** Each dispatch request carries a W3C `traceparent` header
propagated through the MCP transport to the worker and then to the provider
call. Workers emit OpenTelemetry spans for dispatch, execution, and
result-handling phases.

**Rationale:** W3C trace context is the industry standard for distributed
tracing. OTel spans emitted by workers flow into `pheno-tracing` (ADR-036)
for fleet-wide observability dashboards. No custom tracing protocol needed.

**Fleet Cross-References:**
- ADR-036 (pheno-tracing Substrate Canonical) — canonical tracing substrate
- ADR-036B (pheno-tracing Re-affirmed) — tracing commitment reaffirmed
- ADR-050 (Router Rebuild: Option B) — router tracing spans (dispatch consumer)
- ADR-007 (Semantic Caching) — trace context for cache-key derivation

---

## Fleet ADR Map

| Local ID | Fleet ADR | Subject |
|----------|-----------|---------|
| ADR-071 | ADR-071 | dispatch-mcp MCP Dispatch Protocol |
| ADR-072 | ADR-072 | dispatch-mcp Multi-Provider Routing |
| ADR-073 | ADR-073 | dispatch-mcp Worker Lifecycle Management |
| ADR-074 | ADR-074 | dispatch-mcp Observability & Tracing |

For the complete fleet-wide index covering ADR-001..074, see
[`docs/adr/INDEX.md`](../../docs/adr/INDEX.md).
