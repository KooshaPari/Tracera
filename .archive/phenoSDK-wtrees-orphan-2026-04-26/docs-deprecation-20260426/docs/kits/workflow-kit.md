# Workflow Kit

## At a Glance
- **Purpose:** Implement sagas, background workflows, and state machines with built-in compensation, scheduling, and monitoring.
- **Best For:** Distributed transactions, background job orchestration, scheduled workflows, and complex process automation.
- **Key Building Blocks:** `Saga`, `Workflow`, `WorkflowEngine`, `WorkflowScheduler`, `StateMachine`, persistence adapters.

## Core Capabilities
- Saga pattern with compensating actions to guarantee consistency.
- Sequential workflows with async step execution and context passing.
- Scheduling system for interval/cron-based workflow triggers.
- State machine utilities for modeling finite state transitions.
- Monitoring hooks for metrics, logging, and progress dashboards.
- Persistence layer for workflow state and replay.

## Getting Started

### Installation
```
pip install workflow-kit
# Extras
pip install "workflow-kit[scheduler]" "workflow-kit[tui]"
```

### Minimal Example
```python
from workflow_kit import Saga, SagaExecutor

saga = Saga("process_order")

@saga.step("reserve", compensate="release")
async def reserve(ctx):
    await inventory.reserve(ctx["order_id"])

@saga.compensation("release")
async def release(ctx):
    await inventory.release(ctx["order_id"])

executor = SagaExecutor()
await executor.execute(saga, {"order_id": "123"})
```

## How It Works
- `patterns.saga` defines Saga primitives; `execution.saga.SagaExecutor` handles orchestration and compensation.
- `core.workflow.Workflow` represents sequential steps; `WorkflowEngine` executes them with context merging.
- Scheduling uses `scheduling.WorkflowScheduler` to run workflows on intervals or cron expressions.
- State machines live in `core.state_machine` and support event triggers, guards, and actions.
- Monitoring modules integrate with observability-kit and TUI dashboards.

## Usage Recipes
- Combine workflow-kit with db-kit to persist workflow state and resume after crashes.
- Trigger stream-kit updates to show progress of long-running tasks.
- Use orchestrator-kit to hand off complex multi-agent sections while workflow-kit coordinates top-level flow.
- Schedule nightly maintenance jobs (cleanup, reindex, backups) with `WorkflowScheduler`.

## Interoperability
- Observability-kit metrics/loggers track execution time, failures, compensations.
- Event-kit publishes workflow events for downstream consumers.
- Config-kit loads workflow and scheduler settings (timeouts, retries, concurrency).
- Storage-kit stores artifacts generated during workflows.

## Operations & Observability
- Monitor metrics: `workflow_executions_total`, `workflow_failures_total`, `saga_compensations_total`.
- Configure retries and backoff strategies per step.
- Persist state to survive restarts; use provided adapters or implement custom persistence.
- Dashboard progress using TUI kit or stream-kit clients.

## Testing & QA
- Use `workflow_kit.testing` helpers to simulate workflows with deterministic clocks.
- Assert compensation logic in sagas by forcing step failures in tests.
- Snapshot scheduler plans to confirm cron/interval configuration.

## Troubleshooting
- **Stuck workflow:** inspect persistence store to identify pending steps; resume manually if needed.
- **Compensation failure:** design idempotent compensation functions and log errors with context.
- **Scheduler drift:** ensure the event loop or worker process stays alive; adjust tick intervals.

## Primary API Surface
- `Saga(name)` / `@saga.step(name, compensate=None)` / `@saga.compensation(name)`
- `SagaExecutor(options)` / `execute(saga, context)`
- `Workflow(name)` / `workflow.add_step(name, handler)` / `WorkflowEngine.execute(workflow, context)`
- `WorkflowScheduler.schedule_interval(name, handler, minutes=5)`
- `StateMachine(initial_state)` / `add_state` / `add_transition` / `trigger`

## Additional Resources
- Examples: `workflow-kit/examples/`
- Tests: `workflow-kit/tests/`
- Related guides: [Patterns](../concepts/patterns.md), [Operations](../guides/operations.md)
