"""Resource allocation strategies.

Provides different algorithms for allocating resources based on various strategies like
fixed, proportional, dynamic, priority, and adaptive.
"""

from abc import ABC, abstractmethod
from typing import Any

from pheno.resources.budget import (
    AllocationStrategy,
    ResourceAllocation,
    ResourceBudget,
)


class BaseAllocator(ABC):
    """
    Base class for resource allocators.
    """

    @abstractmethod
    def calculate_allocation(
        self,
        requested_units: float,
        budgets: dict[str, ResourceBudget],
        context: dict[str, Any],
        allocation_history: list[ResourceAllocation] | None = None,
    ) -> float:
        """Calculate resource allocation based on strategy.

        Args:
            requested_units: Amount of resources requested
            budgets: Available budgets
            context: Additional context (model_name, limits, etc.)
            allocation_history: Historical allocations for learning

        Returns:
            Allocated resource units
        """


class FixedAllocator(BaseAllocator):
    """Fixed allocation strategy.

    Allocates the minimum of requested units and configured limits.
    """

    def calculate_allocation(
        self,
        requested_units: float,
        budgets: dict[str, ResourceBudget],
        context: dict[str, Any],
        allocation_history: list[ResourceAllocation] | None = None,
    ) -> float:
        """
        Calculate fixed allocation.
        """
        max_limit = context.get("max_limit", requested_units)
        return min(requested_units, max_limit)


class ProportionalAllocator(BaseAllocator):
    """Proportional allocation strategy.

    Allocates resources proportional to available budget.
    """

    def __init__(self, max_allocation_rate: float = 0.1):
        """Initialize proportional allocator.

        Args:
            max_allocation_rate: Maximum percentage of available budget to allocate (0.0-1.0)
        """
        self.max_allocation_rate = max_allocation_rate

    def calculate_allocation(
        self,
        requested_units: float,
        budgets: dict[str, ResourceBudget],
        context: dict[str, Any],
        allocation_history: list[ResourceAllocation] | None = None,
    ) -> float:
        """
        Calculate proportional allocation.
        """
        if not budgets:
            return requested_units

        # Find minimum available budget across all periods
        min_available = min(b.available_units for b in budgets.values())

        # Allocate up to max_allocation_rate of available budget
        max_allocation = min_available * self.max_allocation_rate

        return min(requested_units, max_allocation)


class DynamicAllocator(BaseAllocator):
    """Dynamic allocation strategy.

    Adjusts allocation based on current utilization levels.
    """

    def __init__(
        self,
        low_utilization_threshold: float = 0.5,
        high_utilization_threshold: float = 0.8,
        low_multiplier: float = 1.0,
        medium_multiplier: float = 0.8,
        high_multiplier: float = 0.5,
    ):
        """Initialize dynamic allocator.

        Args:
            low_utilization_threshold: Threshold for low utilization
            high_utilization_threshold: Threshold for high utilization
            low_multiplier: Multiplier when utilization is low
            medium_multiplier: Multiplier when utilization is medium
            high_multiplier: Multiplier when utilization is high
        """
        self.low_threshold = low_utilization_threshold
        self.high_threshold = high_utilization_threshold
        self.low_mult = low_multiplier
        self.medium_mult = medium_multiplier
        self.high_mult = high_multiplier

    def calculate_allocation(
        self,
        requested_units: float,
        budgets: dict[str, ResourceBudget],
        context: dict[str, Any],
        allocation_history: list[ResourceAllocation] | None = None,
    ) -> float:
        """
        Calculate dynamic allocation based on utilization.
        """
        if not budgets:
            return requested_units

        # Calculate average utilization across all budgets
        avg_utilization = sum(b.utilization_rate for b in budgets.values()) / len(budgets)

        # Adjust allocation based on utilization
        if avg_utilization < self.low_threshold:
            multiplier = self.low_mult
        elif avg_utilization < self.high_threshold:
            multiplier = self.medium_mult
        else:
            multiplier = self.high_mult

        return requested_units * multiplier


class PriorityAllocator(BaseAllocator):
    """Priority-based allocation strategy.

    Allocates more resources to higher priority requests.
    """

    def __init__(self, max_priority: int = 10):
        """Initialize priority allocator.

        Args:
            max_priority: Maximum priority value
        """
        self.max_priority = max_priority

    def calculate_allocation(
        self,
        requested_units: float,
        budgets: dict[str, ResourceBudget],
        context: dict[str, Any],
        allocation_history: list[ResourceAllocation] | None = None,
    ) -> float:
        """
        Calculate priority-based allocation.
        """
        priority = context.get("priority", self.max_priority // 2)

        # Scale allocation based on priority (higher priority = more allocation)
        priority_multiplier = priority / self.max_priority

        base_allocation = requested_units * priority_multiplier

        return min(requested_units, base_allocation)


class AdaptiveAllocator(BaseAllocator):
    """Adaptive allocation strategy.

    Learns from historical patterns to optimize allocations.
    """

    def __init__(
        self,
        history_window: int = 100,
        buffer_multiplier: float = 1.2,
        min_samples: int = 5,
    ):
        """Initialize adaptive allocator.

        Args:
            history_window: Number of historical allocations to consider
            buffer_multiplier: Multiplier to add buffer to learned average
            min_samples: Minimum samples needed before using adaptive logic
        """
        self.history_window = history_window
        self.buffer_multiplier = buffer_multiplier
        self.min_samples = min_samples

    def calculate_allocation(
        self,
        requested_units: float,
        budgets: dict[str, ResourceBudget],
        context: dict[str, Any],
        allocation_history: list[ResourceAllocation] | None = None,
    ) -> float:
        """
        Calculate adaptive allocation based on historical patterns.
        """
        if not allocation_history or len(allocation_history) < self.min_samples:
            # Fall back to proportional allocation if not enough history
            fallback = ProportionalAllocator()
            return fallback.calculate_allocation(
                requested_units, budgets, context, allocation_history,
            )

        # Filter for similar allocations
        resource_type = context.get("resource_type")
        model_name = context.get("model_name")
        operation_type = context.get("operation_type")

        similar_allocations = [
            a
            for a in allocation_history[-self.history_window :]
            if a.is_completed
            and a.resource_type == resource_type
            and (not model_name or a.model_name == model_name)
            and (not operation_type or a.operation_type == operation_type)
        ]

        if len(similar_allocations) < self.min_samples:
            # Not enough similar allocations, fall back
            fallback = ProportionalAllocator()
            return fallback.calculate_allocation(
                requested_units, budgets, context, allocation_history,
            )

        # Calculate average actual usage from similar allocations
        avg_usage = sum(a.used_units for a in similar_allocations) / len(similar_allocations)

        # Add buffer to account for variance
        learned_allocation = avg_usage * self.buffer_multiplier

        return min(requested_units, learned_allocation)


def get_allocator(strategy: AllocationStrategy, **kwargs) -> BaseAllocator:
    """Get allocator instance for a given strategy.

    Args:
        strategy: Allocation strategy
        **kwargs: Additional arguments for allocator initialization

    Returns:
        Allocator instance
    """
    allocators = {
        AllocationStrategy.FIXED: FixedAllocator,
        AllocationStrategy.PROPORTIONAL: ProportionalAllocator,
        AllocationStrategy.DYNAMIC: DynamicAllocator,
        AllocationStrategy.PRIORITY: PriorityAllocator,
        AllocationStrategy.ADAPTIVE: AdaptiveAllocator,
    }

    allocator_class = allocators.get(strategy)
    if not allocator_class:
        raise ValueError(f"Unknown allocation strategy: {strategy}")

    return allocator_class(**kwargs)
