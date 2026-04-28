# Multi-Agent Orchestration - Quick Reference

**One-page reference for pheno-sdk multi-agent orchestration**

## Installation

```bash
pip install pheno-sdk

# Choose your framework
pip install crewai>=0.80.0        # CrewAI
pip install langgraph>=0.1.0      # LangGraph
pip install pyautogen>=0.2.0      # AutoGen
```

## Basic Setup

```python
from pheno.mcp.agents import Orchestrator, WorkflowPattern
from pheno.mcp.ports import TaskConfig

# Create orchestrator
orchestrator = Orchestrator(framework="crewai")  # or "langgraph", "autogen"
```

## Create Agents

```python
agent_id = await orchestrator.create_agent(
    name="agent_name",          # Unique name
    role="Agent Role",          # Role description
    goal="Primary goal",        # What agent aims to achieve
    backstory="Background",     # Context/expertise (optional)
    tools=["tool1", "tool2"]    # Tool names (optional)
)
```

## Define Tasks

```python
task = TaskConfig(
    description="What to do",
    agent="agent_name",
    expected_output="What you expect",
    dependencies=["other_task"]  # Optional
)
```

## Workflow Patterns

### Sequential (one after another)
```python
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.SEQUENTIAL,
    tasks=[task1, task2, task3]
)
```

### Parallel (concurrent execution)
```python
from pheno.mcp.agents import DependencyConfig

dependencies = [
    DependencyConfig(task_id="merge", depends_on=["fetch1", "fetch2"])
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.PARALLEL,
    tasks=tasks,
    dependencies=dependencies
)
```

### Hierarchical (manager + workers)
```python
# First task = manager, rest = workers
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.HIERARCHICAL,
    tasks=[manager_task, worker1, worker2]
)
```

### Conditional (based on conditions)
```python
def condition(ctx):
    return ctx["score"] > 0.8

dependencies = [
    DependencyConfig(
        task_id="task2",
        depends_on=["task1"],
        condition=condition
    )
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.CONDITIONAL,
    tasks=tasks,
    dependencies=dependencies
)
```

## Execute Workflow

```python
result = await orchestrator.execute_workflow(
    workflow_id,
    inputs={"key": "value"}  # Optional
)

# Check results
if result.success:
    print(f"Completed in {result.total_duration_ms}ms")
    for task_id, task_result in result.task_results.items():
        print(f"{task_id}: {task_result.output}")
else:
    print(f"Failed: {result.failed_tasks}")
```

## Configuration

### Framework Config
```python
from pheno.mcp.agents import FrameworkConfig

config = FrameworkConfig(
    framework="crewai",
    verbose=True,
    max_iterations=10,
    timeout_seconds=300.0,
    config={"llm_config": {"model": "gpt-4"}}
)

orchestrator = Orchestrator(framework_config=config)
```

### Agent Pool Config
```python
from pheno.mcp.agents import AgentPoolConfig

pool_config = AgentPoolConfig(
    max_agents=10,
    max_concurrent_tasks=5,
    auto_scale=True
)

orchestrator = Orchestrator(pool_config=pool_config)
```

## Port Adapter (Standard Interface)

```python
from pheno.mcp.agents import OrchestratorPortAdapter
from pheno.mcp.ports import AgentConfig, TaskConfig

# Create adapter (implements AgentOrchestratorPort)
adapter = OrchestratorPortAdapter(framework="crewai")

# Use standard port interface
agent_id = await adapter.create_agent(AgentConfig(...))
result = await adapter.execute_task(TaskConfig(...))
results = await adapter.execute_workflow([task1, task2])
status = await adapter.get_agent_status(agent_id)
```

## Monitoring

```python
# Pool statistics
stats = await orchestrator.get_pool_stats()
print(f"Agents: {stats['total_agents']}")
print(f"Idle: {stats['idle_agents']}")
print(f"Completed: {stats['total_tasks_completed']}")

# Workflow status
workflow = await orchestrator.get_workflow_status(workflow_id)
print(f"Status: {workflow.status}")
```

## Error Handling

```python
try:
    result = await orchestrator.execute_workflow(workflow_id)
    if not result.success:
        for task_id in result.failed_tasks:
            error = result.task_results[task_id].error
            print(f"Task {task_id} failed: {error}")
except Exception as e:
    print(f"Workflow error: {e}")
finally:
    await orchestrator.shutdown()
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or specific logger
logging.getLogger('pheno.mcp.agents').setLevel(logging.INFO)
```

## Common Patterns

### Research → Write
```python
researcher = await orchestrator.create_agent(
    name="researcher", role="Research Analyst", ...
)
writer = await orchestrator.create_agent(
    name="writer", role="Writer", ...
)

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.SEQUENTIAL,
    tasks=[
        TaskConfig(description="Research topic", agent="researcher"),
        TaskConfig(description="Write article", agent="writer")
    ]
)
```

### Multi-Source Collection
```python
collectors = [
    await orchestrator.create_agent(name=f"collector_{i}", ...)
    for i in range(3)
]
consolidator = await orchestrator.create_agent(name="consolidator", ...)

tasks = [
    TaskConfig(description="Collect from source 1", agent="collector_0"),
    TaskConfig(description="Collect from source 2", agent="collector_1"),
    TaskConfig(description="Collect from source 3", agent="collector_2"),
    TaskConfig(
        description="Merge all data",
        agent="consolidator",
        dependencies=["task_0", "task_1", "task_2"]
    )
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.PARALLEL,
    tasks=tasks
)
```

## Framework-Specific Features

### CrewAI
- Role-playing agents
- Automatic delegation
- `allow_delegation=True` in config

### LangGraph
- State graphs
- Conditional routing
- Checkpointing support
- LangChain tool integration

### AutoGen
- Conversational agents
- Code execution: `enable_code_execution=True`
- Human-in-the-loop: `human_input_mode="ALWAYS"`
- Group chat orchestration

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No agents available | Increase `max_agents` or enable `auto_scale` |
| Circular dependencies | Check dependency graph, ensure no cycles |
| Timeout errors | Increase `timeout_seconds` in configs |
| Framework not available | `pip install framework-name` |

## Performance Tips

1. **Maximize Parallelism**: Minimize task dependencies
2. **Pool Sizing**: Set `max_concurrent_tasks` based on workload
3. **Timeouts**: Set appropriate values for long tasks
4. **Auto-scaling**: Enable for variable workloads

## Complete Example

```python
import asyncio
from pheno.mcp.agents import Orchestrator, WorkflowPattern
from pheno.mcp.ports import TaskConfig

async def main():
    # Setup
    orchestrator = Orchestrator(framework="crewai")

    # Agents
    researcher = await orchestrator.create_agent(
        name="researcher",
        role="Research Analyst",
        goal="Find information"
    )
    writer = await orchestrator.create_agent(
        name="writer",
        role="Writer",
        goal="Create content"
    )

    # Workflow
    workflow_id = orchestrator.create_workflow(
        pattern=WorkflowPattern.SEQUENTIAL,
        tasks=[
            TaskConfig(description="Research AI trends", agent="researcher"),
            TaskConfig(description="Write blog post", agent="writer")
        ]
    )

    # Execute
    result = await orchestrator.execute_workflow(workflow_id)

    # Results
    if result.success:
        print("Success!")
        for task_id, task_result in result.task_results.items():
            print(f"{task_id}: {task_result.output}")
    else:
        print(f"Failed: {result.failed_tasks}")

    # Cleanup
    await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## More Information

- **Full Guide**: `/docs/mcp/multi_agent_orchestration.md`
- **Examples**: `/examples/multi_agent_orchestration_example.py`
- **Port Verification**: `/examples/port_adapter_verification.py`
- **Source Code**: `/src/pheno/mcp/agents/orchestration.py`

## Support

For issues or questions:
1. Check the FAQ in the full guide
2. Review troubleshooting section
3. Examine example code
4. Enable debug logging
