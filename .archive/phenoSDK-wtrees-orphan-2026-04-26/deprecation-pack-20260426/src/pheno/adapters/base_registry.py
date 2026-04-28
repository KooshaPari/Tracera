"""Base Registry Implementation.

Provides a reusable, thread-safe base implementation of the Registry protocol. Can be
extended for specific use cases.
"""

import builtins
import logging
from collections.abc import Callable
from threading import RLock
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRegistry(Generic[T]):
    """Thread-safe base registry implementation.

    Implements all registry protocols with in-memory storage and thread safety.
    Can be extended for specific use cases.

    Example:
        >>> class ToolRegistry(BaseRegistry[McpTool]):
        ...     pass
        >>>
        >>> registry = ToolRegistry()
        >>> registry.register("search", search_tool)
        >>> tool = registry.get("search")
    """

    def __init__(self):
        self._items: dict[str, T] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._categories: dict[str, str] = {}  # item_name -> category
        self._register_callbacks: list[Callable[[str, T], None]] = []
        self._unregister_callbacks: list[Callable[[str], None]] = []
        self._lock = RLock()  # Thread-safe operations

    # Registry protocol methods

    def register(self, name: str, item: T, **metadata) -> None:
        """
        Register an item (thread-safe).
        """
        with self._lock:
            self._items[name] = item

            # Store metadata
            if metadata:
                self._metadata[name] = metadata

                # Extract category if provided
                if "category" in metadata:
                    self._categories[name] = metadata["category"]

            # Notify callbacks
            for callback in self._register_callbacks:
                try:
                    callback(name, item)
                except Exception as e:
                    logger.exception(f"Error in register callback: {e}")

            logger.debug(f"Registered item: {name}")

    def unregister(self, name: str) -> None:
        """
        Unregister an item (thread-safe).
        """
        with self._lock:
            if name in self._items:
                del self._items[name]

                if name in self._metadata:
                    del self._metadata[name]

                if name in self._categories:
                    del self._categories[name]

                # Notify callbacks
                for callback in self._unregister_callbacks:
                    try:
                        callback(name)
                    except Exception as e:
                        logger.exception(f"Error in unregister callback: {e}")

                logger.debug(f"Unregistered item: {name}")

    def get(self, name: str) -> T:
        """
        Get an item by name (thread-safe).
        """
        with self._lock:
            if name not in self._items:
                raise KeyError(f"Item not found: {name}")
            return self._items[name]

    def has(self, name: str) -> bool:
        """
        Check if an item is registered (thread-safe).
        """
        with self._lock:
            return name in self._items

    def list(self, **filters) -> list[T]:
        """
        List all registered items (thread-safe).
        """
        with self._lock:
            items = list(self._items.values())

            # Apply filters
            if filters:
                items = self._apply_filters(items, filters)

            return items

    def list_names(self) -> builtins.list[str]:
        """
        List all registered item names (thread-safe).
        """
        with self._lock:
            return list(self._items.keys())

    def clear(self) -> None:
        """
        Clear all registered items (thread-safe).
        """
        with self._lock:
            self._items.clear()
            self._metadata.clear()
            self._categories.clear()
            logger.debug("Cleared all items")

    def count(self) -> int:
        """
        Get count of registered items (thread-safe).
        """
        with self._lock:
            return len(self._items)

    # SearchableRegistry methods

    def search(self, query: str) -> builtins.list[T]:
        """
        Search for items (thread-safe).
        """
        with self._lock:
            query_lower = query.lower()
            results = []

            for name, item in self._items.items():
                # Search in name
                if query_lower in name.lower():
                    results.append(item)
                    continue

                # Search in metadata
                if name in self._metadata:
                    metadata = self._metadata[name]
                    if any(query_lower in str(v).lower() for v in metadata.values()):
                        results.append(item)
                        continue

                # Search in item string representation
                if query_lower in str(item).lower():
                    results.append(item)

            return results

    def filter(self, **criteria) -> builtins.list[T]:
        """
        Filter items by criteria (thread-safe).
        """
        with self._lock:
            return self._apply_filters(list(self._items.values()), criteria)

    # ObservableRegistry methods

    def on_register(self, callback: Callable[[str, T], None]) -> None:
        """
        Register callback for item registration.
        """
        self._register_callbacks.append(callback)

    def on_unregister(self, callback: Callable[[str], None]) -> None:
        """
        Register callback for item unregistration.
        """
        self._unregister_callbacks.append(callback)

    # CategorizedRegistry methods

    def list_by_category(self, category: str) -> builtins.list[T]:
        """
        List items in a category.
        """
        names = [name for name, cat in self._categories.items() if cat == category]
        return [self._items[name] for name in names if name in self._items]

    def list_categories(self) -> builtins.list[str]:
        """
        List all categories.
        """
        return list(set(self._categories.values()))

    def get_category(self, name: str) -> str | None:
        """
        Get category of an item.
        """
        return self._categories.get(name)

    # MetadataRegistry methods

    def set_metadata(self, name: str, metadata: dict[str, Any]) -> None:
        """
        Set metadata for an item.
        """
        if name not in self._items:
            raise KeyError(f"Item not found: {name}")

        self._metadata[name] = metadata

        # Update category if provided
        if "category" in metadata:
            self._categories[name] = metadata["category"]

    def get_metadata(self, name: str) -> dict[str, Any]:
        """
        Get metadata for an item.
        """
        return self._metadata.get(name, {}).copy()

    def update_metadata(self, name: str, updates: dict[str, Any]) -> None:
        """
        Update metadata for an item.
        """
        if name not in self._items:
            raise KeyError(f"Item not found: {name}")

        if name not in self._metadata:
            self._metadata[name] = {}

        self._metadata[name].update(updates)

        # Update category if provided
        if "category" in updates:
            self._categories[name] = updates["category"]

    # Helper methods

    def _apply_filters(self, items: builtins.list[T], filters: dict[str, Any]) -> builtins.list[T]:
        """
        Apply filters to items.
        """
        filtered = []

        for item in items:
            if self._item_matches_filters(item, filters):
                filtered.append(item)

        return filtered

    def _item_matches_filters(self, item: T, filters: dict[str, Any]) -> bool:
        """
        Check if an item matches the given filters.
        """
        item_name = self._get_item_name(item)
        if item_name is None:
            return False

        metadata = self._metadata.get(item_name, {})
        return self._metadata_matches_filters(metadata, filters)

    def _get_item_name(self, item: T) -> str | None:
        """
        Get the name of an item by finding it in the registry.
        """
        for name, registered_item in self._items.items():
            if registered_item is item:
                return name
        return None

    def _metadata_matches_filters(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        """
        Check if metadata matches all filter criteria.
        """
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True


__all__ = ["BaseRegistry"]
