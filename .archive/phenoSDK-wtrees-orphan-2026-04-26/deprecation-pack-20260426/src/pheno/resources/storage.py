"""Storage backends for resource management data.

Provides both in-memory and Redis-based storage options.
"""

import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pheno.resources.budget import (
    AllocationStrategy,
    BudgetPeriod,
    ResourceAllocation,
    ResourceBudget,
)


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    """

    @abstractmethod
    def save_budget(self, key: str, budget: ResourceBudget) -> None:
        """
        Save a budget.
        """

    @abstractmethod
    def load_budget(self, key: str) -> ResourceBudget | None:
        """
        Load a budget.
        """

    @abstractmethod
    def save_allocation(self, allocation: ResourceAllocation) -> None:
        """
        Save an allocation.
        """

    @abstractmethod
    def load_allocation(self, allocation_id: str) -> ResourceAllocation | None:
        """
        Load an allocation.
        """

    @abstractmethod
    def get_all_allocations(self) -> list[ResourceAllocation]:
        """
        Get all allocations.
        """

    @abstractmethod
    def save_usage_event(self, event: dict[str, Any]) -> None:
        """
        Save a usage event.
        """

    @abstractmethod
    def get_usage_events(
        self,
        resource_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get usage events.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all data.
        """


class InMemoryStorage(StorageBackend):
    """
    In-memory storage backend.
    """

    def __init__(self):
        """
        Initialize in-memory storage.
        """
        self.budgets: dict[str, ResourceBudget] = {}
        self.allocations: dict[str, ResourceAllocation] = {}
        self.usage_events: list[dict[str, Any]] = []

    def save_budget(self, key: str, budget: ResourceBudget) -> None:
        """
        Save a budget.
        """
        self.budgets[key] = budget

    def load_budget(self, key: str) -> ResourceBudget | None:
        """
        Load a budget.
        """
        return self.budgets.get(key)

    def save_allocation(self, allocation: ResourceAllocation) -> None:
        """
        Save an allocation.
        """
        self.allocations[allocation.allocation_id] = allocation

    def load_allocation(self, allocation_id: str) -> ResourceAllocation | None:
        """
        Load an allocation.
        """
        return self.allocations.get(allocation_id)

    def get_all_allocations(self) -> list[ResourceAllocation]:
        """
        Get all allocations.
        """
        return list(self.allocations.values())

    def save_usage_event(self, event: dict[str, Any]) -> None:
        """
        Save a usage event.
        """
        self.usage_events.append(event)

    def get_usage_events(
        self,
        resource_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get usage events.
        """
        events = self.usage_events

        if resource_type:
            events = [e for e in events if e.get("resource_type") == resource_type]

        if start_time:
            events = [
                e
                for e in events
                if e.get("timestamp", datetime.min.replace(tzinfo=UTC)) >= start_time
            ]

        if end_time:
            events = [
                e
                for e in events
                if e.get("timestamp", datetime.max.replace(tzinfo=UTC)) <= end_time
            ]

        return events

    def clear(self) -> None:
        """
        Clear all data.
        """
        self.budgets.clear()
        self.allocations.clear()
        self.usage_events.clear()


class RedisStorage(StorageBackend):
    """Redis-based storage backend.

    Provides persistent storage with time-series support.
    """

    def __init__(self, redis_client, prefix: str = "resource_mgmt"):
        """Initialize Redis storage.

        Args:
            redis_client: Redis client instance (redis.Redis)
            prefix: Key prefix for namespacing
        """
        self.redis = redis_client
        self.prefix = prefix

    def _make_key(self, *parts: str) -> str:
        """
        Create a namespaced key.
        """
        return f"{self.prefix}:{':'.join(parts)}"

    def save_budget(self, key: str, budget: ResourceBudget) -> None:
        """
        Save a budget.
        """
        budget_key = self._make_key("budget", key)
        data = self._serialize_budget(budget)
        self.redis.set(budget_key, json.dumps(data))

        # Set expiration if period_end is defined
        if budget.period_end:
            ttl = int((budget.period_end - datetime.now(UTC)).total_seconds())
            if ttl > 0:
                self.redis.expire(budget_key, ttl)

    def load_budget(self, key: str) -> ResourceBudget | None:
        """
        Load a budget.
        """
        budget_key = self._make_key("budget", key)
        data = self.redis.get(budget_key)

        if not data:
            return None

        return self._deserialize_budget(json.loads(data))

    def save_allocation(self, allocation: ResourceAllocation) -> None:
        """
        Save an allocation.
        """
        alloc_key = self._make_key("allocation", allocation.allocation_id)
        data = self._serialize_allocation(allocation)
        self.redis.set(alloc_key, json.dumps(data))

        # Add to index
        index_key = self._make_key("allocations", "index")
        self.redis.sadd(index_key, allocation.allocation_id)

    def load_allocation(self, allocation_id: str) -> ResourceAllocation | None:
        """
        Load an allocation.
        """
        alloc_key = self._make_key("allocation", allocation_id)
        data = self.redis.get(alloc_key)

        if not data:
            return None

        return self._deserialize_allocation(json.loads(data))

    def get_all_allocations(self) -> list[ResourceAllocation]:
        """
        Get all allocations.
        """
        index_key = self._make_key("allocations", "index")
        allocation_ids = self.redis.smembers(index_key)

        allocations = []
        for alloc_id in allocation_ids:
            allocation = self.load_allocation(
                alloc_id.decode() if isinstance(alloc_id, bytes) else alloc_id,
            )
            if allocation:
                allocations.append(allocation)

        return allocations

    def save_usage_event(self, event: dict[str, Any]) -> None:
        """
        Save a usage event.
        """
        # Store in time-series format
        timestamp = event.get("timestamp", datetime.now(UTC))
        ts_key = self._make_key("usage_events", event["resource_type"])

        # Use timestamp as score for sorted set
        score = timestamp.timestamp()
        self.redis.zadd(ts_key, {json.dumps(event, default=str): score})

        # Set TTL for old events (e.g., 90 days)
        self.redis.expire(ts_key, 90 * 24 * 60 * 60)

    def get_usage_events(
        self,
        resource_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get usage events.
        """
        if not resource_type:
            # Get all resource types
            pattern = self._make_key("usage_events", "*")
            keys = self.redis.keys(pattern)
        else:
            keys = [self._make_key("usage_events", resource_type)]

        events = []
        for key in keys:
            # Get events from sorted set
            min_score = start_time.timestamp() if start_time else "-inf"
            max_score = end_time.timestamp() if end_time else "+inf"

            event_data = self.redis.zrangebyscore(key, min_score, max_score)

            for data in event_data:
                event = json.loads(data.decode() if isinstance(data, bytes) else data)
                # Parse timestamp back to datetime
                if isinstance(event.get("timestamp"), str):
                    event["timestamp"] = datetime.fromisoformat(event["timestamp"])
                events.append(event)

        return events

    def clear(self) -> None:
        """
        Clear all data.
        """
        pattern = f"{self.prefix}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    @staticmethod
    def _serialize_budget(budget: ResourceBudget) -> dict[str, Any]:
        """
        Serialize budget to dict.
        """
        return {
            "resource_type": budget.resource_type,
            "period": budget.period.value,
            "total_units": budget.total_units,
            "allocated_units": budget.allocated_units,
            "used_units": budget.used_units,
            "reserved_units": budget.reserved_units,
            "total_budget_usd": budget.total_budget_usd,
            "allocated_budget_usd": budget.allocated_budget_usd,
            "used_budget_usd": budget.used_budget_usd,
            "period_start": budget.period_start.isoformat(),
            "period_end": budget.period_end.isoformat() if budget.period_end else None,
            "metadata": budget.metadata,
            "created_at": budget.created_at.isoformat(),
            "last_updated": budget.last_updated.isoformat(),
        }

    @staticmethod
    def _deserialize_budget(data: dict[str, Any]) -> ResourceBudget:
        """
        Deserialize budget from dict.
        """
        return ResourceBudget(
            resource_type=data["resource_type"],
            period=BudgetPeriod(data["period"]),
            total_units=data["total_units"],
            allocated_units=data.get("allocated_units", 0.0),
            used_units=data.get("used_units", 0.0),
            reserved_units=data.get("reserved_units", 0.0),
            total_budget_usd=data.get("total_budget_usd"),
            allocated_budget_usd=data.get("allocated_budget_usd", 0.0),
            used_budget_usd=data.get("used_budget_usd", 0.0),
            period_start=datetime.fromisoformat(data["period_start"]),
            period_end=(
                datetime.fromisoformat(data["period_end"]) if data.get("period_end") else None
            ),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )

    @staticmethod
    def _serialize_allocation(allocation: ResourceAllocation) -> dict[str, Any]:
        """
        Serialize allocation to dict.
        """
        return {
            "allocation_id": allocation.allocation_id,
            "request_id": allocation.request_id,
            "resource_type": allocation.resource_type,
            "model_name": allocation.model_name,
            "operation_type": allocation.operation_type,
            "requested_units": allocation.requested_units,
            "allocated_units": allocation.allocated_units,
            "used_units": allocation.used_units,
            "estimated_cost_usd": allocation.estimated_cost_usd,
            "actual_cost_usd": allocation.actual_cost_usd,
            "priority": allocation.priority,
            "strategy": allocation.strategy.value,
            "is_active": allocation.is_active,
            "is_completed": allocation.is_completed,
            "exceeded_allocation": allocation.exceeded_allocation,
            "metadata": allocation.metadata,
            "allocated_at": allocation.allocated_at.isoformat(),
            "completed_at": (
                allocation.completed_at.isoformat() if allocation.completed_at else None
            ),
        }

    @staticmethod
    def _deserialize_allocation(data: dict[str, Any]) -> ResourceAllocation:
        """
        Deserialize allocation from dict.
        """
        return ResourceAllocation(
            allocation_id=data["allocation_id"],
            request_id=data["request_id"],
            resource_type=data["resource_type"],
            model_name=data.get("model_name"),
            operation_type=data.get("operation_type"),
            requested_units=data.get("requested_units", 0.0),
            allocated_units=data.get("allocated_units", 0.0),
            used_units=data.get("used_units", 0.0),
            estimated_cost_usd=data.get("estimated_cost_usd", 0.0),
            actual_cost_usd=data.get("actual_cost_usd", 0.0),
            priority=data.get("priority", 5),
            strategy=AllocationStrategy(data.get("strategy", "dynamic")),
            is_active=data.get("is_active", True),
            is_completed=data.get("is_completed", False),
            exceeded_allocation=data.get("exceeded_allocation", False),
            metadata=data.get("metadata", {}),
            allocated_at=datetime.fromisoformat(data["allocated_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
            ),
        )
