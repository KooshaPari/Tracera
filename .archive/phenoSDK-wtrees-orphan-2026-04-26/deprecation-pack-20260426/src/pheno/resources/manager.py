"""Resource Budget Manager - Main orchestration class.

Manages resource budgets and allocations with flexible storage and allocation strategies.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from pheno.resources.allocators import get_allocator
from pheno.resources.budget import (
    AllocationStrategy,
    BudgetPeriod,
    ResourceAllocation,
    ResourceBudget,
)
from pheno.resources.storage import StorageBackend

# Re-export components for backward compatibility
from .cache_layer import ResourceCache, StorageManager
from .loaders import AllocationLoader, BudgetLoader, ResourceLimitsLoader
from .rendering import BudgetStatusRenderer

logger = logging.getLogger(__name__)


class ResourceBudgetManager:
    """Manages resource budgets and allocations.

    Supports multiple resource types (tokens, API calls, costs, etc.) with flexible
    allocation strategies and storage backends.
    """

    def __init__(
        self,
        storage: StorageBackend | None = None,
        default_strategy: AllocationStrategy = AllocationStrategy.DYNAMIC,
    ):
        """Initialize the resource budget manager.

        Args:
            storage: Storage backend
            default_strategy: Default allocation strategy
        """
        self.default_strategy = default_strategy

        # Initialize storage and cache layer
        self.cache_layer = ResourceCache(storage)
        self.storage_manager = StorageManager(self.cache_layer.storage)

        # Initialize loaders and rendering
        self.budget_loader = BudgetLoader()
        self.allocation_loader = AllocationLoader()
        self.limits_loader = ResourceLimitsLoader()
        self.renderer = BudgetStatusRenderer()

        # Active budgets by (resource_type, period)
        self.budgets: dict[tuple[str, BudgetPeriod], ResourceBudget] = {}

        # Active allocations
        self.allocations: dict[str, ResourceAllocation] = {}

        # Historical data
        self.allocation_history: list[ResourceAllocation] = []

        # Resource limits (e.g., model-specific limits)
        self.resource_limits: dict[str, dict[str, Any]] = {}

        # Strategy mapping by operation type
        self.operation_strategies: dict[str, AllocationStrategy] = {}

        logger.info(
            f"Resource budget manager initialized with {type(self.cache_layer.storage).__name__} storage",
        )

    def set_budget(
        self,
        resource_type: str,
        period: BudgetPeriod,
        total_units: float,
        total_budget_usd: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ResourceBudget:
        """
        Set or update a budget for a resource and period.
        """
        # Calculate period end
        now = datetime.now(UTC)
        if period == BudgetPeriod.HOURLY:
            period_end = now + timedelta(hours=1)
        elif period == BudgetPeriod.DAILY:
            period_end = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            period_end = now + timedelta(days=7 - now.weekday())
        else:  # MONTHLY
            next_month = now.month + 1 if now.month < 12 else 1
            next_year = now.year if now.month < 12 else now.year + 1
            period_end = now.replace(
                year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0,
            ) - timedelta(seconds=1)

        budget = ResourceBudget(
            resource_type=resource_type,
            period=period,
            total_units=total_units,
            total_budget_usd=total_budget_usd,
            period_start=now,
            period_end=period_end,
            metadata=metadata or {},
        )

        # Store in memory
        key = (resource_type, period)
        self.budgets[key] = budget

        # Persist through cache layer
        self.cache_layer.save_budget(budget)

        logger.info(
            f"Set {period.value} budget for {resource_type}: {total_units} units, ${total_budget_usd or 0:.2f}",
        )

        return budget

    def allocate_resource(
        self,
        request_id: str,
        resource_type: str,
        requested_units: float,
        operation_type: str | None = None,
        model_name: str | None = None,
        priority: int = 5,
        estimated_cost_usd: float = 0.0,
        strategy: AllocationStrategy | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ResourceAllocation | None:
        """
        Allocate resources for a request.
        """
        # Validate and adjust request
        adjusted_units = self._validate_and_adjust_request(model_name, requested_units)
        if adjusted_units is None:
            return None

        # Determine allocation strategy
        strategy = self._determine_allocation_strategy(strategy, operation_type)

        # Get relevant budgets
        resource_budgets = self._get_resource_budgets(resource_type)
        if not resource_budgets:
            return None

        # Calculate allocation
        allocated_units = self._calculate_allocation(
            adjusted_units,
            resource_budgets,
            strategy,
            resource_type,
            model_name,
            operation_type,
            priority,
        )
        if allocated_units <= 0:
            return None

        # Validate budget constraints
        if not self._validate_budget_constraints(
            resource_budgets, allocated_units, estimated_cost_usd, resource_type,
        ):
            return None

        # Create and store allocation
        allocation = self._create_and_store_allocation(
            request_id,
            resource_type,
            adjusted_units,
            allocated_units,
            strategy,
            estimated_cost_usd,
            model_name,
            operation_type,
            priority,
            metadata,
        )

        # Update budgets
        self._update_budgets(resource_budgets, allocated_units, estimated_cost_usd)

        logger.debug(
            f"Allocated {allocated_units} units of {resource_type} for {request_id} using {strategy.value} strategy",
        )

        return allocation

    def _validate_and_adjust_request(
        self, model_name: str | None, requested_units: float,
    ) -> float | None:
        """
        Validate request and adjust units based on limits.
        """
        if model_name and model_name in self.resource_limits:
            limits = self.resource_limits[model_name]
            max_units = limits.get("max_units", requested_units)
            if requested_units > max_units:
                logger.warning(
                    f"Request exceeds limit for {model_name}: {requested_units} > {max_units}",
                )
                return max_units
        return requested_units

    def _determine_allocation_strategy(
        self, strategy: AllocationStrategy | None, operation_type: str | None,
    ) -> AllocationStrategy:
        """
        Determine the allocation strategy to use.
        """
        if strategy is None:
            return self.operation_strategies.get(operation_type, self.default_strategy)
        return strategy

    def _get_resource_budgets(self, resource_type: str) -> dict[str, ResourceBudget] | None:
        """
        Get relevant budgets for the resource type.
        """
        resource_budgets = {
            period.value: budget
            for (rtype, period), budget in self.budgets.items()
            if rtype == resource_type
        }

        if not resource_budgets:
            logger.warning(f"No budgets configured for resource type: {resource_type}")
            return None

        return resource_budgets

    def _calculate_allocation(
        self,
        requested_units: float,
        resource_budgets: dict[str, ResourceBudget],
        strategy: AllocationStrategy,
        resource_type: str,
        model_name: str | None,
        operation_type: str | None,
        priority: int,
    ) -> float:
        """
        Calculate allocation using the specified strategy.
        """
        allocator = get_allocator(strategy)
        context = {
            "resource_type": resource_type,
            "model_name": model_name,
            "operation_type": operation_type,
            "priority": priority,
            "max_limit": requested_units,
        }

        allocated_units = allocator.calculate_allocation(
            requested_units,
            resource_budgets,
            context,
            self.allocation_history,
        )

        if allocated_units <= 0:
            logger.warning("Cannot allocate resources")
            return 0

        return allocated_units

    def _validate_budget_constraints(
        self,
        resource_budgets: dict[str, ResourceBudget],
        allocated_units: float,
        estimated_cost_usd: float,
        resource_type: str,
    ) -> bool:
        """
        Validate that all budgets can accommodate the allocation.
        """
        for budget in resource_budgets.values():
            if budget.available_units < allocated_units:
                logger.warning(
                    f"Insufficient {budget.period.value} budget for {resource_type}: "
                    f"{budget.available_units} < {allocated_units}",
                )
                return False

            if budget.total_budget_usd and estimated_cost_usd > 0:
                available_budget = budget.total_budget_usd - budget.allocated_budget_usd
                if estimated_cost_usd > available_budget:
                    logger.warning(f"Would exceed {budget.period.value} cost budget")
                    return False

        return True

    def _create_and_store_allocation(
        self,
        request_id: str,
        resource_type: str,
        requested_units: float,
        allocated_units: float,
        strategy: AllocationStrategy,
        estimated_cost_usd: float,
        model_name: str | None,
        operation_type: str | None,
        priority: int,
        metadata: dict[str, Any] | None,
    ) -> ResourceAllocation:
        """
        Create and store the resource allocation.
        """
        allocation = self.allocation_loader.create_allocation(
            request_id=request_id,
            resource_type=resource_type,
            requested_units=requested_units,
            allocated_units=allocated_units,
            strategy=strategy,
            estimated_cost_usd=estimated_cost_usd,
            model_name=model_name,
            operation_type=operation_type,
            priority=priority,
            metadata=metadata,
        )

        self.allocations[allocation.allocation_id] = allocation
        self.cache_layer.save_allocation(allocation)

        return allocation

    def _update_budgets(
        self,
        resource_budgets: dict[str, ResourceBudget],
        allocated_units: float,
        estimated_cost_usd: float,
    ) -> None:
        """
        Update budgets with the allocated resources.
        """
        for budget in resource_budgets.values():
            budget.allocated_units += allocated_units
            budget.allocated_budget_usd += estimated_cost_usd
            budget.last_updated = datetime.now(UTC)
            self.cache_layer.save_budget(budget)

    def update_usage(
        self,
        allocation_id: str,
        used_units: float,
        actual_cost_usd: float = 0.0,
    ) -> bool:
        """
        Update resource usage for an allocation.
        """
        allocation = self.allocations.get(allocation_id)
        if not allocation:
            logger.warning(f"Allocation {allocation_id} not found")
            return False

        units_delta = used_units - allocation.used_units
        cost_delta = actual_cost_usd - allocation.actual_cost_usd

        # Update allocation
        allocation.used_units = used_units
        allocation.actual_cost_usd = actual_cost_usd

        if used_units > allocation.allocated_units:
            allocation.exceeded_allocation = True
            logger.warning(
                f"Allocation {allocation_id} exceeded: {used_units} > {allocation.allocated_units}",
            )

        # Update budgets
        resource_type = allocation.resource_type
        for (rtype, _period), budget in self.budgets.items():
            if rtype == resource_type:
                budget.used_units += units_delta
                budget.used_budget_usd += cost_delta
                budget.last_updated = datetime.now(UTC)
                self.cache_layer.save_budget(budget)

        # Track usage (using cache layer's internal tracker)
        self.cache_layer.usage_tracker.record_usage(
            resource_type=allocation.resource_type,
            units=units_delta,
            cost_usd=cost_delta,
            metadata={
                "allocation_id": allocation_id,
                "model_name": allocation.model_name,
                "operation_type": allocation.operation_type,
            },
        )

        # Persist allocation update
        self.cache_layer.save_allocation(allocation)

        return True

    def complete_allocation(
        self,
        allocation_id: str,
        final_units: float | None = None,
        final_cost: float | None = None,
    ) -> bool:
        """
        Mark an allocation as completed.
        """
        allocation = self.allocations.get(allocation_id)
        if not allocation:
            logger.warning(f"Allocation {allocation_id} not found")
            return False

        # Update final usage if provided
        if final_units is not None:
            self.update_usage(
                allocation_id,
                final_units,
                final_cost or allocation.actual_cost_usd,
            )

        # Mark as completed
        allocation.is_active = False
        allocation.is_completed = True
        allocation.completed_at = datetime.now(UTC)

        # Move to history
        self.allocation_history.append(allocation)
        if len(self.allocation_history) > 10000:
            self.allocation_history = self.allocation_history[-10000:]

        # Free up allocated resources
        freed_units = allocation.allocated_units - allocation.used_units
        if freed_units > 0:
            resource_type = allocation.resource_type
            for (rtype, _period), budget in self.budgets.items():
                if rtype == resource_type:
                    budget.allocated_units = max(0.0, budget.allocated_units - freed_units)
                    self.cache_layer.save_budget(budget)

        # Persist allocation update
        self.cache_layer.save_allocation(allocation)

        logger.debug(f"Completed allocation {allocation_id}: {allocation.used_units} units used")

        return True

    def get_budget_status(
        self,
        resource_type: str,
        period: BudgetPeriod | None = None,
    ) -> dict[str, Any]:
        """
        Get budget status.
        """
        if period:
            key = (resource_type, period)
            budget = self.budgets.get(key)
            if not budget:
                return {"error": f"No budget set for {resource_type} {period.value}"}
            return budget.to_dict()

        # Return all budgets for this resource type
        return {
            period.value: self.budgets[(resource_type, period)].to_dict()
            for resource_type_key, period in self.budgets
            if resource_type_key == resource_type
        }

    def get_allocation_statistics(self, resource_type: str | None = None) -> dict[str, Any]:
        """
        Get allocation statistics.
        """
        active_allocations = [
            a
            for a in self.allocations.values()
            if a.is_active and (not resource_type or a.resource_type == resource_type)
        ]

        completed_allocations = [
            a
            for a in self.allocation_history
            if a.is_completed and (not resource_type or a.resource_type == resource_type)
        ]

        if not self.allocation_history and not active_allocations:
            return {"status": "no_data"}

        exceeded_allocations = [a for a in completed_allocations if a.exceeded_allocation]

        return {
            "resource_type": resource_type or "all",
            "active_allocations": len(active_allocations),
            "completed_allocations": len(completed_allocations),
            "total_allocations": len(self.allocation_history) + len(active_allocations),
            "exceeded_rate": (
                len(exceeded_allocations) / len(completed_allocations)
                if completed_allocations
                else 0
            ),
            "resource_stats": {
                "total_allocated": sum(a.allocated_units for a in self.allocation_history),
                "total_used": sum(a.used_units for a in self.allocation_history),
                "average_efficiency": (
                    sum(a.efficiency_score for a in completed_allocations)
                    / len(completed_allocations)
                    if completed_allocations
                    else 0
                ),
            },
            "cost_stats": {
                "total_estimated": sum(a.estimated_cost_usd for a in self.allocation_history),
                "total_actual": sum(a.actual_cost_usd for a in self.allocation_history),
            },
            "strategy_distribution": {
                strategy.value: len([a for a in self.allocation_history if a.strategy == strategy])
                for strategy in AllocationStrategy
            },
        }

    def render_budget_status(self, format_type: str = "text") -> str:
        """
        Render budget status using renderer.
        """
        return self.renderer.render_budget_status(self.budgets, format_type)

    def render_allocation_report(self, format_type: str = "text") -> str:
        """
        Render allocation report using renderer.
        """
        return self.renderer.render_allocation_report(list(self.allocations.values()), format_type)

    def set_resource_limit(
        self,
        identifier: str,
        max_units: float,
        **kwargs,
    ) -> None:
        """
        Set resource limits for a specific identifier.
        """
        self.resource_limits[identifier] = {"max_units": max_units, **kwargs}
        logger.info(f"Set resource limit for {identifier}: {max_units} units")

    def set_operation_strategy(
        self,
        operation_type: str,
        strategy: AllocationStrategy,
    ) -> None:
        """
        Set allocation strategy for an operation type.
        """
        self.operation_strategies[operation_type] = strategy
        logger.info(f"Set {strategy.value} strategy for {operation_type} operations")


# Fix imports
from datetime import timedelta
