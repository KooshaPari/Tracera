# Multi-Agent Orchestration Guide

Complete guide to using pheno-sdk's multi-agent orchestration framework for building complex AI workflows with CrewAI, LangGraph, and AutoGen.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Workflow Patterns](#workflow-patterns)
5. [Framework Integration](#framework-integration)
6. [Configuration Reference](#configuration-reference)
7. [Performance Tuning](#performance-tuning)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Overview

The Multi-Agent Orchestration framework provides a unified interface for building complex AI workflows across multiple agent frameworks. It abstracts the complexity of coordinating multiple AI agents while providing powerful features like:

- **Framework Agnostic**: Supports CrewAI, LangGraph, AutoGen, and custom implementations
- **Workflow Patterns**: Sequential, Parallel, Hierarchical, and Conditional execution
- **Resource Management**: Agent pool management with automatic scaling
- **Dependency Resolution**: Automatic task ordering based on dependencies
- **Production Ready**: Full logging, error handling, and monitoring support

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Agent Pool  │  │  Dependency  │  │   Workflow   │ │
│  │   Manager    │  │   Resolver   │  │   Executor   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│   CrewAI   │ │LangGraph │ │  AutoGen    │
│  Adapter   │ │ Adapter  │ │  Adapter    │
└────────────┘ └──────────┘ └─────────────┘
```

## Quick Start

### Installation

```bash
# Install pheno-sdk
pip install pheno-sdk

# Install framework of choice
pip install crewai>=0.80.0  # For CrewAI
pip install langgraph>=0.1.0 langchain-openai  # For LangGraph
pip install pyautogen>=0.2.0  # For AutoGen
```

### Basic Example

```python
import asyncio
from pheno.mcp.agents.orchestration import (
    Orchestrator,
    WorkflowPattern,
    AgentPoolConfig,
)
from pheno.mcp.ports import TaskConfig

async def main():
    # Create orchestrator with CrewAI
    orchestrator = Orchestrator(
        framework="crewai",
        pool_config=AgentPoolConfig(max_agents=10)
    )

    # Create agents
    researcher_id = await orchestrator.create_agent(
        name="researcher",
        role="Research Analyst",
        goal="Find and analyze relevant information",
        backstory="Expert researcher with 10 years of experience"
    )

    writer_id = await orchestrator.create_agent(
        name="writer",
        role="Technical Writer",
        goal="Create clear and concise documentation",
        backstory="Senior technical writer specializing in AI"
    )

    # Define tasks
    tasks = [
        TaskConfig(
            description="Research the latest trends in AI orchestration",
            agent="researcher",
            expected_output="Research summary with key findings"
        ),
        TaskConfig(
            description="Write a blog post based on the research",
            agent="writer",
            expected_output="500-word blog post",
            dependencies=["task_0"]  # Depends on research task
        )
    ]

    # Create and execute workflow
    workflow_id = orchestrator.create_workflow(
        pattern=WorkflowPattern.SEQUENTIAL,
        tasks=tasks
    )

    result = await orchestrator.execute_workflow(workflow_id)

    print(f"Workflow Status: {result.status}")
    print(f"Output: {result.output}")
    print(f"Completed Tasks: {len(result.task_results)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Concepts

### Orchestrator

The central coordinator for multi-agent workflows. Manages agents, tasks, and execution patterns.

```python
from pheno.mcp.agents.orchestration import (
    Orchestrator,
    FrameworkConfig,
    AgentPoolConfig
)

# Initialize orchestrator
orchestrator = Orchestrator(
    framework="crewai",  # or "langgraph", "autogen", "custom"
    framework_config=FrameworkConfig(
        framework="crewai",
        allow_delegation=True,
        verbose=True,
        max_iterations=10
    ),
    pool_config=AgentPoolConfig(
        max_agents=10,
        max_concurrent_tasks=5,
        auto_scale=True
    )
)
```

### Agent Pool

Manages a pool of agents for efficient task execution with resource limits.

**Features:**
- Automatic agent allocation and release
- Health monitoring
- Resource limit enforcement
- Statistics tracking

```python
# Get pool statistics
stats = await orchestrator.get_pool_stats()
print(f"Total agents: {stats['total_agents']}")
print(f"Idle agents: {stats['idle_agents']}")
print(f"Tasks completed: {stats['total_tasks_completed']}")
```

### Dependency Resolver

Automatically orders tasks based on dependencies using topological sorting.

```python
from pheno.mcp.agents.orchestration import DependencyConfig

# Define task dependencies
dependencies = [
    DependencyConfig(
        task_id="task_2",
        depends_on=["task_0", "task_1"],  # Depends on both
        required_outputs=["analysis_result"],  # Requires specific output
        condition=lambda ctx: ctx["task_0"]["score"] > 0.8  # Custom condition
    )
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.PARALLEL,
    tasks=tasks,
    dependencies=dependencies
)
```

### Workflow Result

Contains complete execution information including all task results.

```python
result = await orchestrator.execute_workflow(workflow_id)

# Check overall success
if result.success:
    print("All tasks completed successfully")

# Access individual task results
for task_id, task_result in result.task_results.items():
    print(f"Task {task_id}:")
    print(f"  Status: {task_result.status}")
    print(f"  Output: {task_result.output}")
    print(f"  Duration: {task_result.duration_ms}ms")

# Check for failures
if result.failed_tasks:
    print(f"Failed tasks: {result.failed_tasks}")
```

## Workflow Patterns

### Sequential Pattern

Tasks execute one after another in order. Each task waits for the previous to complete.

**Use Cases:**
- Linear data processing pipelines
- Step-by-step analysis workflows
- Document generation workflows

```python
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.SEQUENTIAL,
    tasks=[
        TaskConfig(description="Step 1: Gather data", agent="data_collector"),
        TaskConfig(description="Step 2: Analyze data", agent="analyst"),
        TaskConfig(description="Step 3: Generate report", agent="reporter"),
    ]
)

result = await orchestrator.execute_workflow(workflow_id)
```

**Execution Flow:**
```
Task 1 → Task 2 → Task 3 → Complete
```

### Parallel Pattern

Tasks execute concurrently, respecting dependencies. Maximum parallelism within dependency constraints.

**Use Cases:**
- Independent data processing
- Multi-source information gathering
- Parallel analysis tasks

```python
from pheno.mcp.agents.orchestration import DependencyConfig

# Tasks 1 and 2 run in parallel, then task 3
tasks = [
    TaskConfig(description="Fetch from API A", agent="fetcher_a"),
    TaskConfig(description="Fetch from API B", agent="fetcher_b"),
    TaskConfig(description="Merge results", agent="merger"),
]

dependencies = [
    DependencyConfig(
        task_id="task_2",  # Merger task
        depends_on=["task_0", "task_1"]  # Depends on both fetchers
    )
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.PARALLEL,
    tasks=tasks,
    dependencies=dependencies
)
```

**Execution Flow:**
```
       ┌─ Task 1 ─┐
Start ─┤          ├─ Task 3 → Complete
       └─ Task 2 ─┘
```

### Hierarchical Pattern

Manager agent delegates to worker agents. First task is the manager, rest are workers.

**Use Cases:**
- Project management scenarios
- Supervisor-worker patterns
- Delegated task execution

```python
tasks = [
    TaskConfig(
        description="Plan project and delegate tasks",
        agent="project_manager"
    ),
    TaskConfig(description="Design database schema", agent="db_engineer"),
    TaskConfig(description="Create API endpoints", agent="backend_dev"),
    TaskConfig(description="Build UI components", agent="frontend_dev"),
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.HIERARCHICAL,
    tasks=tasks
)
```

**Execution Flow:**
```
                Manager (Task 1)
                     │
        ┌────────────┼────────────┐
        │            │            │
    Worker 1     Worker 2     Worker 3
    (Task 2)     (Task 3)     (Task 4)
```

### Conditional Pattern

Tasks execute based on runtime conditions and previous results.

**Use Cases:**
- Decision tree workflows
- Adaptive processing pipelines
- Error recovery workflows

```python
def should_analyze_sentiment(ctx):
    """Only analyze if text is long enough"""
    return len(ctx.get("text", "")) > 100

dependencies = [
    DependencyConfig(
        task_id="sentiment_analysis",
        depends_on=["text_extraction"],
        condition=should_analyze_sentiment
    )
]

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.CONDITIONAL,
    tasks=tasks,
    dependencies=dependencies
)
```

## Framework Integration

### CrewAI Integration

CrewAI excels at role-playing AI agents with specific roles and goals.

```python
from pheno.mcp.agents.orchestration import Orchestrator, FrameworkConfig

# Configure CrewAI
orchestrator = Orchestrator(
    framework="crewai",
    framework_config=FrameworkConfig(
        framework="crewai",
        allow_delegation=True,
        verbose=True,
        config={
            "llm_config": {
                "model": "gpt-4",
                "temperature": 0.7
            }
        }
    )
)

# Create specialized agents
researcher = await orchestrator.create_agent(
    name="senior_researcher",
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI",
    backstory="You're a seasoned researcher with a knack for uncovering trends",
    tools=["search", "scrape_website"]
)

writer = await orchestrator.create_agent(
    name="tech_writer",
    role="Tech Content Strategist",
    goal="Craft compelling content on tech advancements",
    backstory="You're a renowned content strategist",
    tools=["write_file"]
)
```

**CrewAI-Specific Features:**
- Role-based agent design
- Automatic delegation between agents
- Built-in tool integration
- Process types: sequential, hierarchical

### LangGraph Integration

LangGraph provides graph-based, stateful workflows with explicit state management.

```python
from pheno.mcp.agents.orchestration import Orchestrator

# Configure LangGraph
orchestrator = Orchestrator(
    framework="langgraph",
    framework_config=FrameworkConfig(
        framework="langgraph",
        config={
            "llm_config": {
                "model": "gpt-4"
            }
        }
    )
)

# Create agent nodes
analyst = await orchestrator.create_agent(
    name="data_analyst",
    role="Data Analysis Agent",
    goal="Analyze data and provide insights",
    tools=["python_repl", "data_loader"]
)

# LangGraph creates a state graph internally
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.SEQUENTIAL,
    tasks=[
        TaskConfig(description="Load dataset", agent="data_analyst"),
        TaskConfig(description="Analyze patterns", agent="data_analyst"),
        TaskConfig(description="Generate visualizations", agent="data_analyst"),
    ]
)
```

**LangGraph-Specific Features:**
- Stateful workflows with type-safe state
- Cyclic graphs for iterative processing
- Conditional routing
- Checkpointing and persistence
- Integration with LangChain tools

**Advanced: Custom State Graph**

```python
from langgraph.graph import StateGraph, END
from pheno.mcp.agents.adapters.langgraph_adapter import LangGraphAdapter

adapter = LangGraphAdapter(framework_config)

# Create custom graph structure
# (See LangGraph documentation for advanced patterns)
```

### AutoGen Integration

AutoGen specializes in conversational multi-agent systems with human-in-the-loop support.

```python
from pheno.mcp.agents.orchestration import Orchestrator

# Configure AutoGen
orchestrator = Orchestrator(
    framework="autogen",
    framework_config=FrameworkConfig(
        framework="autogen",
        config={
            "llm_config": {
                "model": "gpt-4",
                "api_key": "your-api-key"
            },
            "enable_code_execution": True,
            "human_input_mode": "NEVER"  # or "ALWAYS", "TERMINATE"
        }
    )
)

# Create assistant agent
assistant = await orchestrator.create_agent(
    name="coding_assistant",
    role="Python Developer",
    goal="Write and debug Python code",
    backstory="Expert Python developer"
)

# Create user proxy agent (can execute code)
user_proxy = await orchestrator.create_agent(
    name="user_proxy",
    role="User Proxy Agent",
    goal="Execute code and provide feedback",
    backstory="Executes code on behalf of user"
)

# Execute conversational workflow
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.SEQUENTIAL,
    tasks=[
        TaskConfig(
            description="Write a function to calculate fibonacci numbers",
            agent="coding_assistant"
        ),
        TaskConfig(
            description="Test the function with n=10",
            agent="user_proxy"
        ),
    ]
)
```

**AutoGen-Specific Features:**
- Conversational agents
- Code execution capabilities
- Human-in-the-loop modes
- Group chat orchestration
- Teaching agent patterns

**Group Chat Example:**

```python
# Multiple agents in group conversation
agents = [
    await orchestrator.create_agent(name="planner", role="Project Planner", ...),
    await orchestrator.create_agent(name="coder", role="Coder", ...),
    await orchestrator.create_agent(name="reviewer", role="Code Reviewer", ...),
]

# AutoGen will manage group chat dynamics
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.HIERARCHICAL,  # Planner as manager
    tasks=[...]
)
```

## Configuration Reference

### FrameworkConfig

Framework-specific configuration options.

```python
from pheno.mcp.agents.orchestration import FrameworkConfig, AgentFramework

config = FrameworkConfig(
    framework=AgentFramework.CREWAI,
    version="0.80.0",  # Optional version pinning
    config={
        "llm_config": {
            "model": "gpt-4-turbo",
            "temperature": 0.7,
            "max_tokens": 2000,
            "api_key": "your-api-key"
        },
        # AutoGen specific
        "enable_code_execution": True,
        "human_input_mode": "NEVER",
        # Custom config
        "custom_param": "value"
    },
    tool_registry={
        "search": search_function,
        "calculator": calculator_function
    },
    allow_delegation=True,
    verbose=True,
    max_iterations=10,
    timeout_seconds=300.0
)
```

### AgentPoolConfig

Agent pool management configuration.

```python
from pheno.mcp.agents.orchestration import AgentPoolConfig

pool_config = AgentPoolConfig(
    max_agents=10,                    # Maximum agents in pool
    max_concurrent_tasks=5,           # Max tasks running concurrently
    idle_timeout_seconds=300.0,       # Timeout for idle agents
    health_check_interval_seconds=60, # Health check frequency
    auto_scale=False,                 # Auto-scale agent pool
    min_agents=1                      # Minimum agents when auto-scaling
)
```

### WorkflowConfig

Workflow execution configuration.

```python
from pheno.mcp.agents.orchestration import WorkflowConfig, WorkflowPattern

workflow_config = WorkflowConfig(
    pattern=WorkflowPattern.PARALLEL,
    max_retries=3,              # Retry failed tasks
    retry_delay_seconds=1.0,    # Delay between retries
    timeout_seconds=600.0,      # Overall workflow timeout
    continue_on_error=False,    # Continue if task fails
    collect_metrics=True        # Collect execution metrics
)

workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.PARALLEL,
    tasks=tasks,
    config=workflow_config
)
```

### AgentConfig

Agent configuration (via create_agent parameters).

```python
agent_id = await orchestrator.create_agent(
    name="unique_agent_name",
    role="Agent Role",
    goal="Agent's primary goal",
    backstory="Agent's background and expertise",
    tools=["tool1", "tool2"],  # Tool names from registry
    metadata={
        "department": "research",
        "priority": "high"
    }
)
```

### TaskConfig

Task configuration.

```python
from pheno.mcp.ports import TaskConfig

task = TaskConfig(
    description="Detailed task description",
    agent="agent_name",
    expected_output="Description of expected output",
    dependencies=["task_0", "task_1"],  # Task IDs this depends on
    metadata={
        "priority": 1,
        "category": "analysis"
    }
)
```

## Performance Tuning

### Agent Pool Optimization

```python
# For CPU-intensive tasks
pool_config = AgentPoolConfig(
    max_agents=20,
    max_concurrent_tasks=10,
    auto_scale=True,
    min_agents=5
)

# For I/O-intensive tasks
pool_config = AgentPoolConfig(
    max_agents=50,
    max_concurrent_tasks=30,
    auto_scale=True,
    min_agents=10
)
```

### Parallel Execution

Maximize parallelism by minimizing dependencies:

```python
# Bad: Sequential dependencies
tasks = [
    TaskConfig(description="Task 1", agent="a1"),
    TaskConfig(description="Task 2", agent="a2", dependencies=["task_0"]),
    TaskConfig(description="Task 3", agent="a3", dependencies=["task_1"]),
]

# Good: Parallel where possible
tasks = [
    TaskConfig(description="Task 1", agent="a1"),
    TaskConfig(description="Task 2", agent="a2"),  # No dependency
    TaskConfig(description="Task 3", agent="a3", dependencies=["task_0", "task_1"]),
]
```

### Timeout Management

```python
# Set appropriate timeouts
framework_config = FrameworkConfig(
    timeout_seconds=180.0,  # Per-agent timeout
    max_iterations=15
)

workflow_config = WorkflowConfig(
    timeout_seconds=600.0,  # Overall workflow timeout
    retry_delay_seconds=2.0
)
```

### Resource Monitoring

```python
# Monitor agent pool health
stats = await orchestrator.get_pool_stats()

if stats['busy_agents'] / stats['total_agents'] > 0.8:
    # Pool is heavily utilized
    print("Consider increasing max_agents")

if stats['total_tasks_failed'] > 0:
    # Tasks are failing
    print(f"Task failure rate: {stats['total_tasks_failed']}")
```

## Best Practices

### 1. Agent Design

**DO:**
- Give agents clear, specific roles
- Provide detailed backstories for context
- Assign relevant tools only
- Use descriptive names

```python
# Good
agent = await orchestrator.create_agent(
    name="financial_analyst",
    role="Senior Financial Analyst",
    goal="Analyze financial data and provide investment insights",
    backstory="15 years of experience in equity analysis",
    tools=["financial_data_api", "calculator"]
)

# Bad
agent = await orchestrator.create_agent(
    name="agent1",
    role="Analyst",
    goal="Analyze stuff",
    tools=["tool1", "tool2", "tool3", "tool4"]  # Too many
)
```

### 2. Task Design

**DO:**
- Write clear, actionable task descriptions
- Specify expected outputs
- Break complex tasks into smaller ones
- Use dependencies appropriately

```python
# Good
task = TaskConfig(
    description="Analyze Q4 2024 revenue data and identify trends. "
                "Focus on YoY growth and seasonal patterns.",
    agent="financial_analyst",
    expected_output="Summary report with key metrics and trend analysis",
    dependencies=["data_collection_task"]
)

# Bad
task = TaskConfig(
    description="Do analysis",
    agent="agent1"
)
```

### 3. Error Handling

Always handle workflow errors:

```python
try:
    result = await orchestrator.execute_workflow(workflow_id)

    if not result.success:
        print(f"Workflow failed: {result.error}")
        print(f"Failed tasks: {result.failed_tasks}")

        # Implement retry logic
        for task_id in result.failed_tasks:
            # Retry or handle individually
            pass

except Exception as e:
    logger.error(f"Workflow execution error: {e}", exc_info=True)
    # Implement fallback logic
```

### 4. Logging and Monitoring

Enable comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set debug level for orchestration
logging.getLogger('pheno.mcp.agents.orchestration').setLevel(logging.DEBUG)

# Monitor workflow execution
result = await orchestrator.execute_workflow(workflow_id)
logger.info(f"Workflow {workflow_id} completed in {result.total_duration_ms}ms")
```

### 5. Testing

Test workflows in isolation:

```python
import pytest

@pytest.mark.asyncio
async def test_research_workflow():
    orchestrator = Orchestrator(framework="crewai")

    # Create test agents
    researcher_id = await orchestrator.create_agent(...)

    # Create simple workflow
    workflow_id = orchestrator.create_workflow(
        pattern=WorkflowPattern.SEQUENTIAL,
        tasks=[...]
    )

    # Execute and verify
    result = await orchestrator.execute_workflow(workflow_id)
    assert result.success
    assert len(result.task_results) == 3
```

## Troubleshooting

### Common Issues

#### 1. No Agents Available

**Error:** `TaskResult(status=FAILED, error="No available agents")`

**Solutions:**
```python
# Increase max_agents
pool_config = AgentPoolConfig(max_agents=20)

# Or enable auto-scaling
pool_config = AgentPoolConfig(auto_scale=True, max_agents=50)

# Check pool stats
stats = await orchestrator.get_pool_stats()
print(f"Available: {stats['idle_agents']}/{stats['total_agents']}")
```

#### 2. Circular Dependencies

**Error:** `ValueError: Circular dependencies detected`

**Solutions:**
```python
# Review dependency graph
# Ensure no cycles: A → B → C → A

# Use dependency resolver to check
from pheno.mcp.agents.orchestration import DependencyResolver

resolver = DependencyResolver()
# Add dependencies...
execution_order = resolver.get_execution_order(task_ids)
```

#### 3. Timeout Errors

**Error:** Task exceeds timeout

**Solutions:**
```python
# Increase timeouts
framework_config = FrameworkConfig(
    timeout_seconds=600.0  # 10 minutes
)

workflow_config = WorkflowConfig(
    timeout_seconds=1800.0  # 30 minutes
)

# Or split long tasks into smaller ones
```

#### 4. Framework Not Available

**Error:** `ImportError: CrewAI is not available`

**Solutions:**
```bash
# Install missing framework
pip install crewai>=0.80.0
pip install langgraph>=0.1.0
pip install pyautogen>=0.2.0
```

#### 5. Task Failures

**Problem:** Tasks failing frequently

**Debug steps:**
```python
result = await orchestrator.execute_workflow(workflow_id)

# Check failed tasks
for task_id in result.failed_tasks:
    task_result = result.task_results[task_id]
    print(f"Task {task_id} failed:")
    print(f"  Error: {task_result.error}")
    print(f"  Agent: {task_result.agent_id}")
    print(f"  Duration: {task_result.duration_ms}ms")

# Enable verbose logging
framework_config = FrameworkConfig(verbose=True)
```

## FAQ

### General Questions

**Q: Which framework should I use?**

A: It depends on your use case:
- **CrewAI**: Role-playing agents, task delegation, simpler setup
- **LangGraph**: Complex stateful workflows, conditional logic, fine control
- **AutoGen**: Conversational agents, code execution, human-in-the-loop

**Q: Can I mix frameworks in one workflow?**

A: Not directly in a single orchestrator, but you can:
- Use multiple orchestrators
- LangGraph can integrate CrewAI crews as nodes
- Build custom adapters for hybrid approaches

**Q: How many agents should I create?**

A: Start with:
- 1 agent per distinct role/responsibility
- Increase based on parallelism needs
- Monitor pool utilization and adjust

**Q: What's the overhead of the orchestration layer?**

A: Minimal (< 10ms per task typically). The framework adapter calls add small overhead, but the benefits of unified API and advanced features outweigh this.

### Performance Questions

**Q: How do I optimize for throughput?**

A:
1. Use parallel workflow pattern
2. Minimize dependencies
3. Increase max_concurrent_tasks
4. Enable auto-scaling
5. Use appropriate timeouts

**Q: Can workflows handle thousands of tasks?**

A: Yes, but consider:
- Breaking into smaller sub-workflows
- Using conditional execution to skip unnecessary tasks
- Monitoring memory usage
- Using appropriate pool sizing

### Integration Questions

**Q: How do I add custom tools?**

A:
```python
def my_custom_tool(arg1: str, arg2: int) -> str:
    """My custom tool."""
    return f"Result: {arg1} {arg2}"

framework_config = FrameworkConfig(
    tool_registry={
        "my_tool": my_custom_tool
    }
)

agent = await orchestrator.create_agent(
    tools=["my_tool"]
)
```

**Q: Can I use custom LLM providers?**

A: Yes, configure in framework_config:
```python
framework_config = FrameworkConfig(
    config={
        "llm_config": {
            "model": "custom-model",
            "api_base": "https://api.custom.com",
            "api_key": "key"
        }
    }
)
```

**Q: How do I integrate with existing code?**

A: Create a custom adapter:
```python
from pheno.mcp.agents.orchestration import Orchestrator

orchestrator = Orchestrator(framework="custom")

# Set your custom adapter
orchestrator.set_adapter(my_custom_adapter)
```

### Debugging Questions

**Q: How do I debug failed workflows?**

A:
```python
# Enable debug logging
import logging
logging.getLogger('pheno.mcp').setLevel(logging.DEBUG)

# Examine result details
result = await orchestrator.execute_workflow(workflow_id)
print(f"Status: {result.status}")
print(f"Error: {result.error}")
print(f"Failed tasks: {result.failed_tasks}")

# Check individual task results
for task_id, task_result in result.task_results.items():
    if not task_result.success:
        print(f"Task {task_id} error: {task_result.error}")
```

**Q: How do I trace execution?**

A:
```python
# Enable verbose mode
framework_config = FrameworkConfig(verbose=True)

# Monitor pool stats
stats = await orchestrator.get_pool_stats()

# Check workflow status during execution
workflow_status = await orchestrator.get_workflow_status(workflow_id)
```

### Advanced Questions

**Q: Can I implement custom workflow patterns?**

A: Yes, extend WorkflowPattern:
```python
from pheno.mcp.agents.orchestration import WorkflowPattern

# Use CUSTOM pattern and implement logic in adapter
workflow_id = orchestrator.create_workflow(
    pattern=WorkflowPattern.CUSTOM,
    tasks=tasks
)
```

**Q: How do I handle long-running workflows?**

A:
```python
# Use appropriate timeouts
workflow_config = WorkflowConfig(
    timeout_seconds=3600.0,  # 1 hour
    collect_metrics=True
)

# Consider breaking into sub-workflows
# Implement checkpointing (LangGraph supports this)
```

**Q: Can I pause and resume workflows?**

A: This depends on the framework:
- **LangGraph**: Yes, supports checkpointing
- **CrewAI/AutoGen**: Not natively, implement at application level

## Next Steps

- Review the [examples](/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/examples/multi_agent_orchestration_example.py)
- Explore [framework-specific documentation](#framework-integration)
- Check the [API reference](/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/src/pheno/mcp/agents/orchestration.py)
- Join the community for support

## Related Documentation

- [MCP Tool Decorators Guide](./tool_decorators_guide.md)
- [Agent Ports Reference](../pheno/mcp/ports.py)
- [CrewAI Documentation](https://docs.crewai.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
