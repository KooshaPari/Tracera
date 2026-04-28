"""
pheno.resources - Resource budget management

A flexible, generic resource budget management system for tokens, API quotas,
cloud costs, and other constrained resources.

Migrated from resource-management-kit into pheno namespace.

Features:
- Generic resource budgeting (tokens, API calls, costs, etc.)
- Multiple budget periods (hourly, daily, weekly, monthly)
- Flexible allocation strategies (fixed, proportional, dynamic, priority, adaptive)
- Redis and in-memory storage backends
- Time-series data support
- Historical analysis and predictive planning

Usage:
    from pheno.resources import ResourceBudgetManager, BudgetPeriod

    # Create budget manager
    manager = ResourceBudgetManager(
        total_budget=10000,
        period=BudgetPeriod.DAILY
    )

    # Allocate resources
    allocation = manager.allocate("service-a", 1000)
"""

from __future__ import annotations

from .allocators import (
    AdaptiveAllocator,
    BaseAllocator,
    DynamicAllocator,
    FixedAllocator,
    PriorityAllocator,
    ProportionalAllocator,
)
from .budget import (
    AllocationStrategy,
    BudgetPeriod,
    ResourceAllocation,
    ResourceBudget,
)
from .manager import ResourceBudgetManager
from .storage import (
    InMemoryStorage,
    RedisStorage,
    StorageBackend,
)
from .trackers import (
    HistoricalAnalyzer,
    PredictivePlanner,
    UsageTracker,
)

__version__ = "0.1.0"

__all__ = [
    "AdaptiveAllocator",
    "AllocationStrategy",
    # Allocators
    "BaseAllocator",
    # Enums
    "BudgetPeriod",
    "DynamicAllocator",
    "FixedAllocator",
    "HistoricalAnalyzer",
    "InMemoryStorage",
    "PredictivePlanner",
    "PriorityAllocator",
    "ProportionalAllocator",
    "RedisStorage",
    "ResourceAllocation",
    # Core classes
    "ResourceBudget",
    "ResourceBudgetManager",
    # Storage
    "StorageBackend",
    # Trackers
    "UsageTracker",
]
