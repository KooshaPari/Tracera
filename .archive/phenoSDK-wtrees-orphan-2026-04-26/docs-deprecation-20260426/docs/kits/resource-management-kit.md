# Resource Management Kit

## At a Glance
- **Purpose:** Track and allocate budgets for constrained resources such as tokens, API calls, or infrastructure cost.
- **Best For:** LLM workloads, API quota enforcement, or any scenario that needs usage tracking with predictive planning.
- **Key Building Blocks:** `ResourceBudgetManager`, allocation strategies, storage backends (memory/Redis), predictive analyzer.

## Core Capabilities
- Define budgets per resource and period (hourly, daily, weekly, monthly).
- Allocate resources using fixed, proportional, priority, or adaptive strategies.
- Track usage history and derive statistics (efficiency, peaks, exhaustion forecasts).
- Pluggable storage backends for persistent tracking (in-memory default, Redis optional).
- Predictive analytics to recommend future budgets and detect exhaustion risk.

## Getting Started

### Installation
```
pip install resource-management-kit
# Redis extras
pip install "resource-management-kit[redis]"
```

### Minimal Example
```python
from resource_management import ResourceBudgetManager, BudgetPeriod

manager = ResourceBudgetManager()
manager.set_budget("tokens", BudgetPeriod.DAILY, total_units=1_000_000)

allocation = manager.allocate_resource(
    request_id="req-1",
    resource_type="tokens",
    requested_units=5_000,
    model_name="gpt-4o",
)

manager.update_usage(allocation.allocation_id, used_units=4_500)
status = manager.get_budget_status("tokens", BudgetPeriod.DAILY)
print(status["used_units"], status["remaining_units"])
```

## How It Works
- Budgets live in `budget.ResourceBudget`; allocations in `budget.ResourceAllocation`.
- `ResourceBudgetManager` coordinates storage, strategies, and history tracking.
- Allocation strategies implemented in `allocators.py` determine how much to grant when requests exceed limits.
- `trackers.HistoricalAnalyzer` and `predictive_planner` derive trends and future recommendations.
- Storage backends implement `BaseStorage` (in-memory by default, Redis optional).

## Usage Recipes
- Configure per-operation strategies (generation vs. analysis) to tune consumption.
- Track cost in USD alongside units to balance financial budgets.
- Feed usage metrics into observability-kit for dashboards (`resource_units_used_total`).
- Integrate with orchestrator-kit to throttle multi-agent workflows based on remaining budget.

## Interoperability
- Pair with config-kit to load budget definitions from YAML or env vars.
- Use event-kit to emit allocation/release events for auditing.
- Stream budget updates to dashboards via stream-kit or TUI consoles.

## Operations & Observability
- Schedule periodic calls to `predict_budget_exhaustion` to alert before depletion.
- Persist history with Redis storage to survive restarts.
- Expose budget status through process-monitor-sdk APIs for runtime introspection.

## Testing & QA
- In-memory storage enables fast tests without external dependencies.
- Use deterministic timestamps by injecting custom clock functions (see tests).
- Validate new strategies through property-based tests ensuring allocations never exceed budgets.

## Troubleshooting
- **Allocation denied:** check remaining units and strategy thresholds; adjust resource limits or priorities.
- **Redis backend errors:** verify connection parameters and prefix configuration.
- **Prediction off:** ensure historical data covers enough periods; tune analyzer window size.

## Primary API Surface
- `ResourceBudgetManager(storage=None)`
- `set_budget(resource_type, period, total_units, total_budget_usd=None)`
- `set_resource_limit(model_name, max_units)`
- `set_operation_strategy(operation, AllocationStrategy)`
- `allocate_resource(request_id, resource_type, requested_units, **metadata)`
- `update_usage(allocation_id, used_units, actual_cost_usd=None)`
- `complete_allocation(allocation_id)`
- `get_budget_status(resource_type, period)`
- `predictive_planner.predict_budget_exhaustion(budget, resource_type)`

## Additional Resources
- Examples: `resource-management-kit/examples/`
- Tests: `resource-management-kit/tests/`
- Related guides: [Operations](../guides/operations.md), [Patterns](../concepts/patterns.md)
