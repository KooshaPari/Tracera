# MCP SDK Kit

## At a Glance
- **Purpose:** Provide monitoring, metrics, and performance utilities tailored to Model Context Protocol (MCP) servers.
- **Best For:** MCP agents and servers that need workflow observability, agent metrics, and runtime optimization.
- **Key Building Blocks:** Workflow monitoring integration, agent metrics collectors, performance optimizer, FastAPI adapters.

## Core Capabilities
- Track MCP workflow executions, durations, inputs/outputs, and errors.
- Collect agent-level metrics (success rates, output volume, XML tag usage, latency).
- Optimize MCP runtime with connection pooling, memory tuning, and health checks.
- Integrate with FastAPI/Textual dashboards for live monitoring.
- Emit observability signals (logs, metrics, traces) consistent with Pheno-SDK standards.

## Getting Started

### Installation
```
pip install mcp-sdk-kit
```

### Minimal Example
```python
from mcp_sdk.workflow import WorkflowMonitoringIntegration

monitoring = WorkflowMonitoringIntegration(enable_background_monitoring=True)
await monitoring.start_monitoring()

span_id = monitoring.get_monitoring_context("workflow-123", "agent")
# Execute workflow...
monitoring.record_workflow_completion(
    span_id=span_id,
    workflow_id="workflow-123",
    workflow_type="agent",
    duration_seconds=2.4,
    success=True,
)
```

## How It Works
- Workflow monitoring lives in `mcp_sdk.workflow`; it plugs into workflow-kit or custom MCP loops.
- Metrics collectors in `mcp_sdk.metrics` aggregate per-agent execution stats and expose summaries.
- Performance optimizer in `mcp_sdk.performance` runs system checks, warms caches, and coordinates resource usage.
- Integrations offer FastAPI routers and background tasks to expose monitoring APIs.

## Usage Recipes
- Attach monitoring endpoints to your MCP server:
  ```python
  from fastapi import FastAPI
  from mcp_sdk.workflow import WorkflowMonitoringIntegration

  app = FastAPI()
  integration = WorkflowMonitoringIntegration()
  integration.integrate_with_fastapi(app)
  ```
- Record agent metrics around each tool invocation for dashboards and alerts.
- Schedule periodic optimization checks using workflow-kit scheduler to keep MCP nodes healthy.
- Emit stream-kit updates (progress, status) to TUIs for live observers.

## Interoperability
- Observability-kit handles logging/metrics/tracing emitted by MCP SDK kit.
- Workflow-kit integrates to coordinate long-running MCP workflows and compensation logic.
- Process-monitor-sdk can host MCP monitoring endpoints alongside other process UIs.
- Resource-management-kit controls token budgets for LLM calls triggered by MCP agents.

## Operations & Observability
- Configure monitoring intervals, retention, and alert thresholds via config-kit.
- Export metrics such as `mcp_workflow_duration_seconds` and `mcp_agent_errors_total`.
- Track XML output compliance to detect malformed agent responses.
- Integrate with deploy-kit to package monitoring endpoints with MCP deployments.

## Testing & QA
- Mock MCP workflows in tests to verify metrics and monitoring events.
- Use provided fixtures in `tests/` to simulate agent executions and verify summaries.
- Validate FastAPI integration with test clients to ensure endpoints respond as expected.

## Troubleshooting
- **Missing workflow spans:** ensure `get_monitoring_context` is called before workflow execution.
- **Metrics not updating:** confirm `complete_execution` is invoked and task IDs are unique.
- **Performance optimizer failing:** check system dependencies and credentials for underlying services.

## Primary API Surface
- `WorkflowMonitoringIntegration(workflow_engine=None, enable_background_monitoring=False, monitoring_interval_seconds=60)`
- `WorkflowMonitoringIntegration.start_monitoring()` / `stop_monitoring()` / `integrate_with_fastapi(app)`
- `AgentMetricsCollector()` – `start_execution`, `complete_execution`, `get_summary`
- `PerformanceOptimizer()` – `initialize_system`, `perform_comprehensive_optimization`, `get_performance_summary`

## Additional Resources
- Examples: `mcp-sdk-kit/examples/`
- Tests: `mcp-sdk-kit/tests/`
- Related guides: [Operations](../guides/operations.md), [Patterns](../concepts/patterns.md)
