"""Core budget data structures and enums.

Provides generic resource budget and allocation models that work with any type of
constrained resource (tokens, API calls, costs, etc.).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class BudgetPeriod(Enum):
    """
    Budget tracking periods.
    """

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AllocationStrategy(Enum):
    """
    Resource allocation strategies.
    """

    FIXED = "fixed"  # Fixed allocation per request
    PROPORTIONAL = "proportional"  # Proportional to request complexity
    DYNAMIC = "dynamic"  # Dynamic based on usage patterns
    PRIORITY = "priority"  # Priority-based allocation
    ADAPTIVE = "adaptive"  # Learn from historical patterns


@dataclass
class ResourceBudget:
    """Generic resource budget configuration.

    Can be used for tokens, API calls, cloud costs, or any constrained resource.
    """

    # Resource identification
    resource_type: str  # e.g., "tokens", "api_calls", "compute_hours", "cost_usd"
    period: BudgetPeriod

    # Budget amounts (using generic units)
    total_units: float
    allocated_units: float = 0.0
    used_units: float = 0.0
    reserved_units: float = 0.0

    # Optional cost tracking (in USD)
    total_budget_usd: float | None = None
    allocated_budget_usd: float = 0.0
    used_budget_usd: float = 0.0

    # Time window
    period_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    period_end: datetime | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def available_units(self) -> float:
        """
        Calculate available resource units.
        """
        return max(0.0, self.total_units - self.allocated_units - self.reserved_units)

    @property
    def utilization_rate(self) -> float:
        """
        Calculate utilization rate.
        """
        if self.total_units == 0:
            return 0.0
        return min(1.0, (self.used_units / self.total_units))

    @property
    def allocation_rate(self) -> float:
        """
        Calculate allocation rate.
        """
        if self.total_units == 0:
            return 0.0
        return min(1.0, (self.allocated_units / self.total_units))

    @property
    def is_exhausted(self) -> bool:
        """
        Check if budget is exhausted.
        """
        return self.available_units <= 0

    def is_near_limit(self, threshold: float = 0.8) -> bool:
        """
        Check if near budget limit.
        """
        return self.utilization_rate > threshold

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "resource_type": self.resource_type,
            "period": self.period.value,
            "total_units": self.total_units,
            "allocated_units": self.allocated_units,
            "used_units": self.used_units,
            "reserved_units": self.reserved_units,
            "available_units": self.available_units,
            "utilization_rate": self.utilization_rate,
            "allocation_rate": self.allocation_rate,
            "total_budget_usd": self.total_budget_usd,
            "allocated_budget_usd": self.allocated_budget_usd,
            "used_budget_usd": self.used_budget_usd,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "is_exhausted": self.is_exhausted,
            "is_near_limit": self.is_near_limit(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class ResourceAllocation:
    """Individual resource allocation.

    Tracks allocation of resources for a specific request or operation.
    """

    # Identification
    allocation_id: str
    request_id: str
    resource_type: str  # e.g., "tokens", "api_calls", etc.

    # Optional context
    model_name: str | None = None
    operation_type: str | None = None

    # Resource amounts
    requested_units: float = 0.0
    allocated_units: float = 0.0
    used_units: float = 0.0

    # Cost tracking
    estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0

    # Priority and strategy
    priority: int = 5  # 1-10, higher is more important
    strategy: AllocationStrategy = AllocationStrategy.DYNAMIC

    # Status
    is_active: bool = True
    is_completed: bool = False
    exceeded_allocation: bool = False

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    allocated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    @property
    def remaining_units(self) -> float:
        """
        Calculate remaining resource units.
        """
        return max(0.0, self.allocated_units - self.used_units)

    @property
    def usage_rate(self) -> float:
        """
        Calculate usage rate.
        """
        if self.allocated_units == 0:
            return 0.0
        return min(1.0, self.used_units / self.allocated_units)

    @property
    def efficiency_score(self) -> float:
        """Calculate allocation efficiency score.

        Returns 1.0 for perfect efficiency (used exactly what was allocated), lower
        values indicate waste, higher values indicate exceeded allocation.
        """
        if self.allocated_units == 0:
            return 0.0
        return self.used_units / self.allocated_units

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "allocation_id": self.allocation_id,
            "request_id": self.request_id,
            "resource_type": self.resource_type,
            "model_name": self.model_name,
            "operation_type": self.operation_type,
            "requested_units": self.requested_units,
            "allocated_units": self.allocated_units,
            "used_units": self.used_units,
            "remaining_units": self.remaining_units,
            "usage_rate": self.usage_rate,
            "efficiency_score": self.efficiency_score,
            "estimated_cost_usd": self.estimated_cost_usd,
            "actual_cost_usd": self.actual_cost_usd,
            "priority": self.priority,
            "strategy": self.strategy.value,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "exceeded_allocation": self.exceeded_allocation,
            "metadata": self.metadata,
            "allocated_at": self.allocated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
