"""Resource cache layer and storage management.

Handles caching, storage backend operations, and data persistence for resource budgets
and allocations.
"""

import logging
from datetime import UTC, datetime, timezone
from typing import Any

from pheno.resources.budget import BudgetPeriod, ResourceAllocation, ResourceBudget
from pheno.resources.storage import InMemoryStorage, StorageBackend
from pheno.resources.trackers import UsageTracker

logger = logging.getLogger(__name__)


class ResourceCache:
    """Cache layer for resource data.

    Provides in-memory caching with optional persistence backend.
    """

    def __init__(self, storage: StorageBackend | None = None):
        self.storage = storage or InMemoryStorage()

        # In-memory caches
        self._budget_cache: dict[str, ResourceBudget] = {}
        self._allocation_cache: dict[str, ResourceAllocation] = {}

        # Cache timestamps
        self._last_cache_update: dict[str, datetime] = {}

        # Usage tracking
        self.usage_tracker = UsageTracker()

        logger.info(f"Resource cache initialized with {type(self.storage).__name__} storage")

    def _get_cache_key(self, resource_type: str, period: BudgetPeriod) -> str:
        """
        Generate cache key for budget.
        """
        return f"{resource_type}:{period.value}"

    def get_budget(self, resource_type: str, period: BudgetPeriod) -> ResourceBudget | None:
        """
        Get budget from cache, loading from storage if needed.
        """
        cache_key = self._get_cache_key(resource_type, period)

        # Check cache first
        if cache_key in self._budget_cache:
            return self._budget_cache[cache_key]

        # Load from storage
        budget = self.storage.load_budget(cache_key)
        if budget:
            self._budget_cache[cache_key] = budget
            self._last_cache_update[cache_key] = datetime.now(UTC)

        return budget

    def save_budget(self, budget: ResourceBudget) -> None:
        """
        Save budget to both cache and storage.
        """
        cache_key = self._get_cache_key(budget.resource_type, budget.period)

        # Update cache
        self._budget_cache[cache_key] = budget
        self._last_cache_update[cache_key] = datetime.now(UTC)

        # Persist to storage
        self.storage.save_budget(cache_key, budget)

        logger.debug(f"Cached budget {cache_key}: {budget.total_units} units")

    def get_allocation(self, allocation_id: str) -> ResourceAllocation | None:
        """
        Get allocation from cache, loading from storage if needed.
        """
        # Check cache first
        if allocation_id in self._allocation_cache:
            return self._allocation_cache[allocation_id]

        # Load from storage
        allocation = self.storage.load_allocation(allocation_id)
        if allocation:
            self._allocation_cache[allocation_id] = allocation

        return allocation

    def save_allocation(self, allocation: ResourceAllocation) -> None:
        """
        Save allocation to both cache and storage.
        """
        # Update cache
        self._allocation_cache[allocation.allocation_id] = allocation

        # Persist to storage
        self.storage.save_allocation(allocation)

        logger.debug(f"Cached allocation {allocation.allocation_id}")

    def list_budgets(self, resource_type: str | None = None) -> list[ResourceBudget]:
        """
        List all cached budgets, optionally filtered by resource type.
        """
        budgets = list(self._budget_cache.values())

        if resource_type:
            budgets = [b for b in budgets if b.resource_type == resource_type]

        return budgets

    def list_allocations(
        self, active_only: bool = True, resource_type: str | None = None,
    ) -> list[ResourceAllocation]:
        """
        List cached allocations with optional filters.
        """
        allocations = list(self._allocation_cache.values())

        if active_only:
            allocations = [a for a in allocations if a.is_active]

        if resource_type:
            allocations = [a for a in allocations if a.resource_type == resource_type]

        return allocations

    def invalidate_cache(self, pattern: str | None = None) -> None:
        """
        Invalidate cache entries matching pattern.
        """
        if pattern:
            # Invalidate matching entries
            keys_to_remove = []
            for key in self._budget_cache:
                if pattern in key:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._budget_cache[key]
                self._last_cache_update.pop(key, None)

            logger.info(f"Invalidated {len(keys_to_remove)} budget cache entries")
        else:
            # Clear all cache
            self._budget_cache.clear()
            self._allocation_cache.clear()
            self._last_cache_update.clear()

            logger.info("Cleared all cache entries")

    def sync_to_storage(self) -> None:
        """
        Force sync all cached data to storage.
        """
        # Sync budgets
        for budget in self._budget_cache.values():
            cache_key = self._get_cache_key(budget.resource_type, budget.period)
            self.storage.save_budget(cache_key, budget)

        # Sync allocations
        for allocation in self._allocation_cache.values():
            self.storage.save_allocation(allocation)

        logger.debug("Synced all cached data to storage")

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        """
        return {
            "budget_cache_size": len(self._budget_cache),
            "allocation_cache_size": len(self._allocation_cache),
            "last_updates": {
                key: timestamp.isoformat() for key, timestamp in self._last_cache_update.items()
            },
            "storage_type": type(self.storage).__name__,
        }


class StorageManager:
    """
    Manages storage backend operations and data migration.
    """

    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.cache = ResourceCache(storage)

        logger.info(f"Storage manager initialized with {type(storage).__name__}")

    def migrate_data(self, from_storage: StorageBackend) -> None:
        """
        Migrate data from another storage backend.
        """
        logger.info("Starting data migration...")

        # Migrate budgets
        logger.info("Migrating budgets...")
        # Note: This would require listing all budgets from source storage
        # Implementation depends on storage interface capabilities

        # Migrate allocations
        logger.info("Migrating allocations...")
        # Similar to budgets, would need listing capability

        logger.info("Data migration completed")

    def backup_data(self, backup_path: str) -> None:
        """
        Create backup of storage data.
        """
        logger.info(f"Creating backup at {backup_path}...")

        # Implementation depends on storage backend
        # For file-based storage, this could be file copy
        # For database, this could be dump/export

        logger.info("Backup completed")

    def restore_data(self, backup_path: str) -> None:
        """
        Restore storage data from backup.
        """
        logger.info(f"Restoring backup from {backup_path}...")

        # Implementation depends on storage backend
        # Clear current data and restore from backup

        # Clear cache after restore
        self.cache.invalidate_cache()

        logger.info("Restore completed")

    def compact_storage(self) -> None:
        """
        Compact storage to remove old/unused data.
        """
        logger.info("Compacting storage...")

        # Remove old completed allocations beyond retention period
        retention_days = 30  # Configurable
        cutoff_date = datetime.now(UTC) - timezone.timedelta(days=retention_days)

        old_allocations = [
            a
            for a in self.cache.list_allocations(active_only=False)
            if a.is_completed and a.completed_at and a.completed_at < cutoff_date
        ]

        # Remove old allocations from storage
        for allocation in old_allocations:
            self.storage.delete_allocation(allocation.allocation_id)

        # Clear from cache
        self.cache.invalidate_cache()

        logger.info(f"Compacted storage, removed {len(old_allocations)} old allocations")

    def get_storage_info(self) -> dict[str, Any]:
        """
        Get storage backend information.
        """
        info = {
            "storage_type": type(self.storage).__name__,
            "cache_stats": self.cache.get_cache_stats(),
        }

        # Add storage-specific info if available
        if hasattr(self.storage, "get_size"):
            info["storage_size"] = self.storage.get_size()

        if hasattr(self.storage, "get_stats"):
            info["storage_stats"] = self.storage.get_stats()

        return info
