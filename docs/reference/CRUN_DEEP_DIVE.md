# CRUN Deep Dive Analysis
## Multi-Agent Orchestration & Planning Patterns

**Research Date:** 2025-11-20
**Source:** crun codebase analysis
**Focus:** Multi-agent coordination, DAG execution, PERT planning, observability

---

## Executive Summary

crun provides **production-ready patterns** for:
- **3 coordination strategies** (hierarchical, P2P, hybrid)
- **DAG-based execution** with TopologicalSorter and critical path analysis
- **PERT/Monte Carlo** planning with confidence intervals
- **State persistence** via SQLAlchemy + pheno integration
- **OpenTelemetry observability** with graceful degradation
- **ReAct agent pattern** for reasoning loops

**Critical for Trace:** Adopt hybrid coordination, DAG executor, and OpenTelemetry tracing.

---

## 1. Multi-Agent Coordination

### Three Strategies (from coordination_mechanisms.py)

**Strategy 1: Hierarchical (Leader-Follower)**
```python
class HierarchicalCoordinator:
    """Centralized coordination with leader agent."""

    async def coordinate(self, tasks: List[Task]) -> List[Result]:
        # Leader assigns tasks to workers
        workers = self.get_available_workers()
        assignments = self.assign_tasks(tasks, workers)

        # Execute assignments
        results = await asyncio.gather(*[
            worker.execute(task)
            for worker, task in assignments
        ])

        return results
```

**Strategy 2: Peer-to-Peer (Bidding)**
```python
class P2PCoordinator:
    """Decentralized coordination via bidding."""

    async def coordinate(self, tasks: List[Task]) -> List[Result]:
        # Announce tasks to all agents
        await self.broadcast_tasks(tasks)

        # Collect bids (cost estimates)
        bids = await self.collect_bids()

        # Select winners (lowest cost)
        assignments = self.select_winners(bids)

        # Execute
        return await self.execute_assignments(assignments)
```

**Strategy 3: Hybrid (Adaptive)**
```python
class HybridCoordinator:
    """Adaptive strategy switching based on load."""

    async def coordinate(self, tasks: List[Task]) -> List[Result]:
        load = self.measure_system_load()

        if load > 0.7:  # High load
            return await self.hierarchical.coordinate(tasks)
        else:  # Normal load
            return await self.p2p.coordinate(tasks)
```

**Recommendation:** Use **Hybrid** for trace's view orchestration - hierarchical under load, P2P normally.

---

## 2. DAG Execution Engine

### TopologicalSorter Pattern

```python
# execution/dag_executor.py
from graphlib import TopologicalSorter
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED
import asyncio

class DAGExecutor:
    """Execute tasks respecting dependency order."""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def execute(self, tasks: Dict[str, Task], dependencies: Dict[str, List[str]]):
        """Execute DAG with parallel execution where possible."""
        # Build topological order
        ts = TopologicalSorter(dependencies)
        ts.prepare()

        results = {}
        pending = set()

        while ts.is_active():
            # Get ready tasks (dependencies satisfied)
            ready = ts.get_ready()

            # Submit to thread pool
            futures = {}
            for task_id in ready:
                future = self.executor.submit(self.execute_task, tasks[task_id])
                futures[future] = task_id
                pending.add(task_id)

            # Wait for ANY completion (not all)
            done, _ = await asyncio.wait(futures, return_when=FIRST_COMPLETED)

            for future in done:
                task_id = futures[future]
                results[task_id] = future.result()
                ts.done(task_id)
                pending.remove(task_id)

        return results
```

### Critical Path Calculation

```python
def calculate_critical_path(tasks: Dict[str, Task], deps: Dict[str, List[str]]) -> List[str]:
    """Find longest path through DAG (critical path)."""
    # Topological sort
    order = list(TopologicalSorter(deps).static_order())

    # Forward pass: earliest start times
    earliest_start = {task_id: 0 for task_id in tasks}
    for task_id in order:
        task_duration = tasks[task_id].estimated_duration
        for dependent in deps.get(task_id, []):
            earliest_start[dependent] = max(
                earliest_start[dependent],
                earliest_start[task_id] + task_duration
            )

    # Backward pass: latest start times
    project_duration = max(earliest_start.values())
    latest_start = {task_id: project_duration for task_id in tasks}

    for task_id in reversed(order):
        task_duration = tasks[task_id].estimated_duration
        if deps.get(task_id):
            latest_start[task_id] = min(
                latest_start[dep] - task_duration
                for dep in deps[task_id]
            )

    # Critical path: tasks with slack = 0
    critical_path = [
        task_id for task_id in tasks
        if earliest_start[task_id] == latest_start[task_id]
    ]

    return critical_path
```

**Recommendation:** Use for trace's multi-view query optimization - execute independent views in parallel.

---

## 3. PERT & Monte Carlo Planning

### PERT Formula

```python
def pert_estimate(optimistic: float, most_likely: float, pessimistic: float) -> float:
    """PERT three-point estimate."""
    return (optimistic + 4 * most_likely + pessimistic) / 6

# Example
task_duration = pert_estimate(
    optimistic=2.0,   # Best case
    most_likely=4.0,  # Expected
    pessimistic=8.0   # Worst case
)  # Returns: 4.33 hours
```

### Monte Carlo Simulation

```python
import numpy as np

def monte_carlo_simulation(tasks: List[Task], iterations: int = 10000) -> dict:
    """Simulate project duration with uncertainty."""
    simulated_durations = []

    for _ in range(iterations):
        duration = 0
        for task in tasks:
            # Sample from triangular distribution
            sample = np.random.triangular(
                left=task.optimistic,
                mode=task.most_likely,
                right=task.pessimistic
            )
            duration += sample
        simulated_durations.append(duration)

    return {
        "mean": np.mean(simulated_durations),
        "std": np.std(simulated_durations),
        "p50": np.percentile(simulated_durations, 50),
        "p80": np.percentile(simulated_durations, 80),
        "p90": np.percentile(simulated_durations, 90),
        "p95": np.percentile(simulated_durations, 95),
        "p99": np.percentile(simulated_durations, 99),
    }
```

**Recommendation:** Use for trace's query performance estimation (FR54-FR62).

---

## 4. State Management (state_db.py)

### SQLAlchemy + Pheno Pattern

```python
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class TaskState(Base):
    __tablename__ = "task_states"

    id = Column(String, primary_key=True)
    plan_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    retries = Column(Integer, default=0)
    dependencies = Column(JSON, default=list)

class StateDB:
    """State persistence for task execution."""

    async def save_task_state(self, task_id: str, plan_id: str, status: str, **kwargs):
        task_state = TaskState(
            id=task_id,
            plan_id=plan_id,
            status=status,
            **kwargs
        )
        self.session.merge(task_state)
        await self.session.commit()

    async def get_plan_status(self, plan_id: str) -> dict:
        """Get execution status for plan."""
        result = await self.session.execute(
            select(TaskState).where(TaskState.plan_id == plan_id)
        )
        tasks = result.scalars().all()

        return {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t.status == "pending"),
            "running": sum(1 for t in tasks if t.status == "running"),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "failed": sum(1 for t in tasks if t.status == "failed"),
        }
```

**Recommendation:** Adopt for trace's view execution state tracking.

---

## 5. Observability (infrastructure/observability/)

### OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

class TracedOperation:
    """Context manager for traced operations."""

    def __init__(self, operation_name: str, **attributes):
        self.tracer = trace.get_tracer(__name__)
        self.operation_name = operation_name
        self.attributes = attributes

    async def __aenter__(self):
        self.span = self.tracer.start_span(self.operation_name)
        for k, v in self.attributes.items():
            self.span.set_attribute(k, v)
        return self.span

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        self.span.end()

# Usage
async def execute_view_query(view: str, query: dict):
    async with TracedOperation("view_query", view=view, agent_id=agent_id) as span:
        span.set_attribute("query.complexity", calculate_complexity(query))
        result = await query_engine.execute(view, query)
        span.set_attribute("result.count", len(result))
        return result
```

### Metrics Adapter (metrics_adapter.py)

```python
from pheno.metrics import record_metric

class MetricsAdapter:
    def record(self, name: str, value: float, tags: dict):
        record_metric(name=name, value=value, tags=tags)

    def increment(self, name: str, tags: dict):
        self.record(name, 1.0, tags)

    def timing(self, name: str, duration_ms: float, tags: dict):
        self.record(name, duration_ms, tags)

# Usage
metrics.increment("view.query.total", {"view": "FEATURE", "status": "success"})
metrics.timing("view.query.duration", 125.5, {"view": "FEATURE"})
```

**Recommendation:** Integrate OpenTelemetry from start for trace's performance tracking (NFR-P6-P8).

---

## 6. CLI Monitor (cli/monitor/)

### Real-Time Dashboard

```python
from rich.live import Live
from rich.table import Table
import asyncio

async def show_dashboard():
    """Live-updating execution dashboard."""
    with Live(generate_table(), refresh_per_second=4) as live:
        while True:
            await asyncio.sleep(0.25)
            live.update(generate_table())

def generate_table() -> Table:
    table = Table(title="Task Execution Status")
    table.add_column("Task ID")
    table.add_column("Status")
    table.add_column("Progress")

    tasks = get_active_tasks()
    for task in tasks:
        status_color = {
            "pending": "yellow",
            "running": "blue",
            "completed": "green",
            "failed": "red"
        }[task.status]

        table.add_row(
            task.id,
            f"[{status_color}]{task.status}[/{status_color}]",
            f"{task.progress*100:.0f}%"
        )

    return table
```

**Recommendation:** Implement for trace's view execution monitoring.

---

## 7. ReAct Agent Pattern (react_agent.py)

### ICLR 2023 Research Implementation

```python
class ReActAgent:
    """Reasoning and Acting in Language Models."""

    async def execute(self, task: str, max_steps: int = 10):
        """Execute task with THOUGHT → ACTION → OBSERVATION loop."""
        context = []

        for step in range(max_steps):
            # THOUGHT: Reason about next action
            thought = await self.llm.generate(
                f"Task: {task}\nContext: {context}\n\nThought:"
            )
            context.append(f"Thought {step+1}: {thought}")

            # ACTION: Decide and execute action
            action = await self.llm.generate(
                f"{context}\nAction:"
            )
            context.append(f"Action {step+1}: {action}")

            # Execute action
            observation = await self.execute_action(action)
            context.append(f"Observation {step+1}: {observation}")

            # Check completion
            if self.is_complete(observation):
                break

        return {"success": True, "steps": step+1, "result": observation}
```

**Recommendation:** Use for trace's complex multi-step query reasoning.

---

## 8. Recommendations for Trace

### High-Priority Patterns

1. **Hybrid Coordination** → Multi-view orchestration
2. **DAG Executor** → View dependency resolution
3. **State DB** → Query plan caching
4. **OpenTelemetry** → Performance tracing
5. **Metrics Collection** → View performance monitoring
6. **ReAct Pattern** → Complex query reasoning

### Integration Points

| crun Pattern | Trace Application |
|--------------|-------------------|
| Multi-agent coordination | Multi-view query orchestration |
| DAG executor | View dependency graph execution |
| State DB | Query plan persistence |
| PERT planning | Query performance estimation |
| Observability | View execution tracing |
| CLI monitor | Real-time query status dashboard |

### Code Locations Referenced

- `execution/coordination_mechanisms.py` - Multi-agent coordination
- `execution/dag_executor.py` - DAG execution
- `execution/state_db.py` - State persistence
- `execution/react_agent.py` - ReAct pattern
- `core/planning_advanced.py` - PERT/Monte Carlo
- `infrastructure/observability/` - OpenTelemetry
- `infrastructure/metrics_adapter.py` - Metrics
- `cli/monitor/` - CLI dashboard

---

**Status:** Analysis complete
**Next:** Apply orchestration patterns to trace architecture
