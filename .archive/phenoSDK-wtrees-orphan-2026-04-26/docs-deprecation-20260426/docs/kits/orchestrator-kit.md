# Orchestrator Kit

## At a Glance
- **Purpose:** Coordinate multi-agent workflows with dependency graphs, messaging, and shared context.
- **Best For:** LLM agent orchestration, back-office automation, or any multi-step pipeline needing dependency awareness.
- **Key Building Blocks:** `Orchestrator`, agent registry, dependency resolver, messaging gateways, cost tracking.

## Core Capabilities
- Register agents with dependencies and execute them in topological order.
- Share context and results across agents via a state store.
- Track execution status, timing, and failures with detailed telemetry.
- Integrate messaging gateways (LLMs, HTTP APIs, custom adapters).
- Provide patterns for fan-out/fan-in, retries, and compensation.

## Getting Started

### Installation
```
pip install orchestrator-kit
```

### Minimal Example
```python
from orchestrator_kit import Orchestrator

orchestrator = Orchestrator()

@orchestrator.agent("fetch")
async def fetch_data(ctx):
    return {"items": [1, 2, 3]}

@orchestrator.agent("process", dependencies=["fetch"])
async def process_data(ctx):
    values = ctx.results["fetch"]["items"]
    ctx.store("sum", sum(values))

await orchestrator.execute()
print(orchestrator.context.state["sum"])  # 6
```

## How It Works
- Agents register via decorator or API, returning callables that accept an execution context.
- Dependency graphs are resolved before execution; cycles raise errors at registration time.
- Context (`ExecutionContext`) exposes `results`, `state`, config, and messaging clients.
- Messaging adapters in `orchestrator_kit.messaging` connect to external systems (LLMs, HTTP, etc.).
- Cost tracking and instrumentation live in `orchestrator_kit.cost` and `orchestrator_kit.monitoring`.

## Usage Recipes
- Implement agent pipelines for document ingestion (fetch → chunk → embed → index) combining storage-kit/vector-kit.
- Add retries by decorating agents with `@orchestrator.retry(max_attempts=3)`.
- Use workflow-kit to trigger orchestrations as part of larger sagas.
- Broadcast agent status over stream-kit to power real-time dashboards.

## Interoperability
- Pull configuration and credentials through config-kit.
- Persist orchestration history with db-kit or event-kit for auditing.
- Combine with mcp-sdk-kit to orchestrate multi-agent MCP sessions.

## Operations & Observability
- Enable observability-kit integration: log agent start/finish, record metrics per agent.
- Use process-monitor-sdk to expose orchestrator health endpoints.
- Define SLAs per agent and emit alerts when execution exceeds thresholds.

## Testing & QA
- Use the in-memory execution mode for unit tests; provide fake messaging adapters.
- Assert dependency resolution by inspecting `orchestrator.graph`.
- Snapshot context state after orchestration to confirm expected results.

## Troubleshooting
- **Dependency cycle detected:** review agent registration order and remove circular references.
- **Result missing:** ensure upstream agent returns a value or writes to context via `ctx.store`.
- **External call failures:** wrap messaging adapters with retries or fallback agents.

## Primary API Surface
- `Orchestrator()`
- Decorators: `@orchestrator.agent(name, dependencies=None)`
- `orchestrator.register_agent(name, handler, dependencies=None)`
- `await orchestrator.execute(targets=None)`
- `orchestrator.get_status()` / `context.results`
- Messaging adapters: `messaging.OpenAIAdapter`, `messaging.HTTPAdapter`

## Additional Resources
- Examples: `orchestrator-kit/examples/`
- Tests: `orchestrator-kit/tests/`
- Related concepts: [Patterns](../concepts/patterns.md), [Operations](../guides/operations.md)
