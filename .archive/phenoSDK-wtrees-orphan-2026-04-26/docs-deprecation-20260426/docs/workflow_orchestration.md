# Workflow Orchestration

The pheno-SDK workflow orchestration module provides comprehensive capabilities for defining and executing complex workflows with support for:

- **DAG-based workflow definitions** - Define workflows as directed acyclic graphs
- **Sequential and parallel execution** - Run steps sequentially or in parallel for optimal performance
- **Conditional branching** - Execute steps based on runtime conditions
- **Error handling and retries** - Robust error handling with configurable retry policies
- **State tracking and persistence** - Track workflow state and persist execution history
- **Event emission** - Subscribe to workflow lifecycle events
- **Workflow triggers** - Support for manual, scheduled, and event-based triggers

## Quick Start

```python
import asyncio
from pheno.workflow.orchestrator import (
    WorkflowOrchestrator,
    build_simple_workflow,
)

# Define step handlers
def fetch_data(context: dict) -> dict:
    return {"records": [1, 2, 3]}

def process_data(context: dict) -> str:
    records = context.get("step_fetch_data_output", {}).get("records", [])
    return f"Processed {len(records)} records"

# Build workflow
workflow = build_simple_workflow(
    "data_pipeline",
    [
        ("fetch_data", fetch_data),
        ("process_data", process_data),
    ],
)

# Execute workflow
async def main():
    orchestrator = WorkflowOrchestrator()
    orchestrator.register_workflow(workflow)

    execution = await orchestrator.execute_workflow(workflow.workflow_id)
    print(f"Status: {execution.status.value}")

asyncio.run(main())
```

## Core Concepts

### Workflow Definition

A workflow is defined as a collection of steps with dependencies:

```python
from pheno.workflow.orchestrator import WorkflowDefinition, WorkflowStep

workflow = WorkflowDefinition(
    workflow_id="my_workflow",
    name="My Workflow",
    description="A sample workflow",
)

# Add steps
workflow.add_step(WorkflowStep(
    step_id="step1",
    handler=my_handler_function,
))

workflow.add_step(WorkflowStep(
    step_id="step2",
    handler=another_handler,
    dependencies=["step1"],  # step2 waits for step1
))
```

### Step Handlers

Step handlers can be synchronous or async functions that receive a context dictionary:

```python
# Synchronous handler
def sync_handler(context: dict) -> any:
    input_data = context.get("input")
    return {"result": "processed"}

# Async handler
async def async_handler(context: dict) -> any:
    await some_async_operation()
    return {"result": "processed"}
```

### Workflow Execution

Execute a workflow with the orchestrator:

```python
orchestrator = WorkflowOrchestrator()
orchestrator.register_workflow(workflow)

execution = await orchestrator.execute_workflow(
    workflow.workflow_id,
    context={"input": "data"},
)

# Check status
print(execution.status)  # COMPLETED, FAILED, etc.

# Access results
for step_id, result in execution.step_results.items():
    print(f"{step_id}: {result.status} - {result.output}")
```

## Features

### 1. Sequential Execution

Steps with dependencies execute in order:

```python
workflow = build_simple_workflow(
    "sequential",
    [
        ("step1", handler1),
        ("step2", handler2),
        ("step3", handler3),
    ],
)
```

### 2. Parallel Execution

Steps without dependencies execute in parallel:

```python
from pheno.workflow.orchestrator import build_parallel_workflow

workflow = build_parallel_workflow(
    "parallel",
    [
        ("task_a", handler_a),
        ("task_b", handler_b),
        ("task_c", handler_c),
    ],
)
```

### 3. Conditional Branching

Execute steps based on runtime conditions:

```python
def should_execute(context: dict) -> bool:
    return context.get("condition", False)

workflow.add_step(WorkflowStep(
    step_id="conditional_step",
    handler=my_handler,
    condition=should_execute,
    dependencies=["previous_step"],
))
```

### 4. Error Handling and Retries

Configure retry policies for resilient workflows:

```python
workflow.add_step(WorkflowStep(
    step_id="resilient_step",
    handler=unreliable_handler,
    retry_policy={
        "max_retries": 3,
        "backoff_factor": 2,  # Exponential backoff: 2^attempt seconds
    },
    timeout=30,  # Timeout in seconds
    on_failure="continue",  # Options: "fail", "continue", "skip_branch"
))
```

### 5. Complex DAG Workflows

Build complex dependency graphs:

```python
workflow = WorkflowDefinition(workflow_id="complex", name="Complex DAG")

# Layer 1: Initialization
workflow.add_step(WorkflowStep(step_id="init", handler=init_handler))

# Layer 2: Parallel processing (depends on init)
workflow.add_step(WorkflowStep(
    step_id="process_a",
    handler=handler_a,
    dependencies=["init"],
))
workflow.add_step(WorkflowStep(
    step_id="process_b",
    handler=handler_b,
    dependencies=["init"],
))

# Layer 3: Aggregation (depends on both parallel steps)
workflow.add_step(WorkflowStep(
    step_id="aggregate",
    handler=aggregate_handler,
    dependencies=["process_a", "process_b"],
))
```

### 6. Event Handling

Subscribe to workflow events:

```python
def on_workflow_start(execution):
    print(f"Workflow {execution.workflow_id} started")

def on_step_complete(execution):
    print(f"Step completed in workflow {execution.workflow_id}")

orchestrator.on_event("workflow.started", on_workflow_start)
orchestrator.on_event("step.completed", on_step_complete)
```

Available events:
- `workflow.started`
- `workflow.completed`
- `workflow.failed`
- `workflow.cancelled`
- `workflow.paused`
- `workflow.resumed`
- `step.started`
- `step.completed`
- `step.failed`
- `step.skipped`
- `step.retrying`

### 7. Workflow Triggers

Define when workflows should execute:

```python
from pheno.workflow.orchestrator import WorkflowTrigger, TriggerType

# Manual trigger (default)
trigger = WorkflowTrigger(
    trigger_type=TriggerType.MANUAL,
    workflow_id=workflow.workflow_id,
)

# Scheduled trigger (cron expression)
trigger = WorkflowTrigger(
    trigger_type=TriggerType.SCHEDULED,
    workflow_id=workflow.workflow_id,
    schedule="0 0 * * *",  # Daily at midnight
)

# Event-based trigger
trigger = WorkflowTrigger(
    trigger_type=TriggerType.EVENT,
    workflow_id=workflow.workflow_id,
    event_pattern={"type": "user.created"},
)

orchestrator.register_trigger(trigger)
```

### 8. State Persistence

Workflow execution state is automatically persisted:

```python
# State is persisted after each workflow execution
execution = await orchestrator.execute_workflow(workflow_id)

# Retrieve execution later
saved_execution = orchestrator.get_execution(execution.execution_id)

# List all executions
all_executions = orchestrator.list_executions()

# Filter by workflow
workflow_executions = orchestrator.list_executions(
    workflow_id="my_workflow"
)

# Filter by status
failed_executions = orchestrator.list_executions(
    status=WorkflowStatus.FAILED
)
```

### 9. Execution Control

Manage running workflows:

```python
# Cancel a running workflow
await orchestrator.cancel_execution(execution_id)

# Pause a workflow (future feature)
await orchestrator.pause_execution(execution_id)

# Resume a paused workflow
await orchestrator.resume_execution(execution_id)
```

## Context and Data Flow

### Context Propagation

The context dictionary flows through all steps:

```python
def step1(context: dict) -> dict:
    # Access initial context
    input_data = context.get("input")

    # Modify context
    context["step1_data"] = "from step 1"

    return {"result": "step1 output"}

def step2(context: dict) -> dict:
    # Access previous step output
    step1_output = context.get("step_step1_output")

    # Access data set by previous step
    step1_data = context.get("step1_data")

    return {"result": "step2 output"}
```

Step outputs are automatically added to context with the key `step_{step_id}_output`.

## Workflow Validation

Workflows are validated before registration:

```python
workflow = WorkflowDefinition(workflow_id="test", name="Test")

# Add steps...

is_valid, errors = workflow.validate()

if not is_valid:
    print(f"Validation errors: {errors}")
else:
    orchestrator.register_workflow(workflow)
```

Validation checks:
- No circular dependencies
- All step dependencies exist
- Proper DAG structure

## Best Practices

### 1. Use Builder Functions

For simple workflows, use builder functions:

```python
# Sequential workflow
workflow = build_simple_workflow(
    "pipeline",
    [("step1", handler1), ("step2", handler2)],
)

# Parallel workflow
workflow = build_parallel_workflow(
    "parallel",
    [("task1", handler1), ("task2", handler2)],
)
```

### 2. Handle Errors Gracefully

Configure appropriate retry policies:

```python
# For flaky operations
retry_policy = {
    "max_retries": 5,
    "backoff_factor": 2,
}

# For critical operations that must succeed
on_failure = "fail"

# For optional operations
on_failure = "continue"
```

### 3. Use Timeouts

Set timeouts for long-running operations:

```python
workflow.add_step(WorkflowStep(
    step_id="long_operation",
    handler=handler,
    timeout=300,  # 5 minutes
))
```

### 4. Leverage Parallel Execution

Identify independent steps that can run in parallel:

```python
# These can run in parallel
workflow.add_step(WorkflowStep(step_id="fetch_users", handler=fetch_users))
workflow.add_step(WorkflowStep(step_id="fetch_orders", handler=fetch_orders))

# This waits for both
workflow.add_step(WorkflowStep(
    step_id="combine",
    handler=combine_data,
    dependencies=["fetch_users", "fetch_orders"],
))
```

### 5. Use Conditions Wisely

Implement business logic through conditions:

```python
def should_send_notification(context: dict) -> bool:
    user_count = context.get("step_count_users_output", 0)
    return user_count > 100

workflow.add_step(WorkflowStep(
    step_id="notify",
    handler=send_notification,
    condition=should_send_notification,
))
```

## Advanced Patterns

### Saga Pattern

For distributed transactions with compensations:

```python
def book_flight(context: dict) -> dict:
    # Book flight
    return {"booking_id": "FL123"}

def cancel_flight(context: dict, result: dict) -> None:
    # Compensation: cancel flight
    booking_id = result.get("booking_id")
    # Cancel logic...

workflow.add_step(WorkflowStep(
    step_id="book_flight",
    handler=book_flight,
    compensate="cancel_flight",  # Name of compensation function
))
```

### Fan-out/Fan-in

Process multiple items in parallel then aggregate:

```python
# Fan-out: Process each item
for i in range(10):
    workflow.add_step(WorkflowStep(
        step_id=f"process_{i}",
        handler=process_item,
        dependencies=["init"],
    ))

# Fan-in: Aggregate results
workflow.add_step(WorkflowStep(
    step_id="aggregate",
    handler=aggregate_results,
    dependencies=[f"process_{i}" for i in range(10)],
))
```

### Dynamic Workflows

Build workflows dynamically based on data:

```python
async def create_dynamic_workflow(items: list) -> WorkflowDefinition:
    workflow = WorkflowDefinition(
        workflow_id="dynamic",
        name="Dynamic Workflow",
    )

    # Add steps dynamically
    for i, item in enumerate(items):
        workflow.add_step(WorkflowStep(
            step_id=f"process_{i}",
            handler=lambda ctx, item=item: process(item),
        ))

    return workflow
```

## Integration with Temporal

The orchestrator is designed to be enhanced with Temporal for distributed workflows:

```python
# Future: Temporal integration
from pheno.workflow.orchestrators.temporal import TemporalWorkflowClient

# The current orchestrator provides the foundation
# Temporal integration can be added for:
# - Distributed execution across multiple workers
# - Long-running workflows (days/weeks)
# - Workflow versioning
# - Advanced scheduling
```

## Examples

See `examples/workflow_examples.py` for complete examples demonstrating:

1. Data Processing Pipeline - Sequential workflow
2. Parallel Processing - Concurrent execution
3. Conditional Workflow - Runtime branching
4. Error Handling - Retry mechanisms
5. Complex DAG - Multi-level dependencies

Run the examples:

```bash
python examples/workflow_examples.py
```

## API Reference

### WorkflowOrchestrator

Main orchestrator class.

**Methods:**
- `register_workflow(workflow)` - Register a workflow definition
- `execute_workflow(workflow_id, context, trigger_type, trigger_data)` - Execute a workflow
- `get_execution(execution_id)` - Get execution by ID
- `list_executions(workflow_id, status)` - List executions with filters
- `cancel_execution(execution_id)` - Cancel a running workflow
- `on_event(event_type, handler)` - Register event handler
- `register_trigger(trigger)` - Register workflow trigger

### WorkflowDefinition

Workflow definition.

**Attributes:**
- `workflow_id: str` - Unique workflow identifier
- `name: str` - Human-readable name
- `steps: dict[str, WorkflowStep]` - Workflow steps
- `description: str` - Optional description
- `timeout: int` - Maximum execution time
- `tags: list[str]` - Tags for categorization

**Methods:**
- `add_step(step)` - Add a step to the workflow
- `validate()` - Validate workflow structure

### WorkflowStep

Workflow step definition.

**Attributes:**
- `step_id: str` - Unique step identifier
- `handler: Callable` - Step handler function
- `dependencies: list[str]` - Step dependencies
- `condition: Callable` - Optional condition for execution
- `retry_policy: dict` - Retry configuration
- `timeout: int` - Step timeout in seconds
- `parallel: bool` - Whether step can run in parallel
- `on_failure: str` - Failure behavior ('fail', 'continue', 'skip_branch')
- `metadata: dict` - Additional metadata

### WorkflowExecution

Workflow execution instance.

**Attributes:**
- `execution_id: str` - Unique execution identifier
- `workflow_id: str` - Workflow identifier
- `status: WorkflowStatus` - Current status
- `context: dict` - Execution context
- `step_results: dict[str, StepResult]` - Step results
- `started_at: datetime` - Start time
- `completed_at: datetime` - Completion time
- `error: str` - Error message if failed
- `events: list[dict]` - Event log
- `trigger_type: TriggerType` - How workflow was triggered
- `trigger_data: dict` - Trigger metadata

### Enums

**WorkflowStatus:**
- `PENDING` - Not yet started
- `RUNNING` - Currently executing
- `COMPLETED` - Successfully completed
- `FAILED` - Failed with error
- `CANCELLED` - Cancelled by user
- `PAUSED` - Paused (future feature)

**StepStatus:**
- `PENDING` - Not yet started
- `RUNNING` - Currently executing
- `COMPLETED` - Successfully completed
- `FAILED` - Failed with error
- `SKIPPED` - Skipped due to condition
- `RETRYING` - Retrying after failure

**TriggerType:**
- `MANUAL` - Manually triggered
- `SCHEDULED` - Scheduled trigger
- `EVENT` - Event-based trigger
- `WEBHOOK` - Webhook trigger

## Performance Considerations

### Parallel Execution

Steps without dependencies automatically execute in parallel:

```python
# These 3 steps run concurrently
workflow.add_step(WorkflowStep(step_id="a", handler=handler_a))
workflow.add_step(WorkflowStep(step_id="b", handler=handler_b))
workflow.add_step(WorkflowStep(step_id="c", handler=handler_c))
```

### Memory Usage

For large workflows:
- Use generators for data processing
- Stream results when possible
- Clean up context data in handlers

### Async Handlers

Use async handlers for I/O-bound operations:

```python
async def fetch_data(context: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## Testing

See `tests/unit/test_workflow_orchestrator.py` for comprehensive test examples.

Run tests:

```bash
pytest tests/unit/test_workflow_orchestrator.py -v
```

## Future Enhancements

Planned features:
- Temporal integration for distributed workflows
- Workflow versioning
- Advanced scheduling (cron, interval)
- Webhook support
- Workflow templates
- Visual workflow builder
- Metrics and monitoring
- Workflow debugging tools
