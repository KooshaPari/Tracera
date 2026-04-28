"""Registry Port.

Protocol interface for generic registry pattern. Provides a unified pattern for all
registries in phenoSDK.
"""

import builtins
from collections.abc import Callable
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")


class Registry(Protocol, Generic[T]):
    """Generic registry protocol.

    Provides a unified pattern for registering and retrieving items.
    All specialized registries should implement this protocol.

    Example:
        >>> registry = ToolRegistry()  # Implements Registry[McpTool]
        >>> registry.register("search", search_tool)
        >>> tool = registry.get("search")
        >>> tools = registry.list()
    """

    def register(self, name: str, item: T, **metadata) -> None:
        """Register an item.

        Args:
            name: Unique identifier for the item
            item: Item to register
            **metadata: Optional metadata

        Example:
            >>> registry.register("search", search_tool, category="tools")
        """
        ...

    def unregister(self, name: str) -> None:
        """Unregister an item.

        Args:
            name: Item identifier

        Example:
            >>> registry.unregister("search")
        """
        ...

    def get(self, name: str) -> T:
        """Get an item by name.

        Args:
            name: Item identifier

        Returns:
            Registered item

        Raises:
            KeyError: If item not found

        Example:
            >>> tool = registry.get("search")
        """
        ...

    def has(self, name: str) -> bool:
        """Check if an item is registered.

        Args:
            name: Item identifier

        Returns:
            True if item exists

        Example:
            >>> if registry.has("search"):
            ...     tool = registry.get("search")
        """
        ...

    def list(self, **filters) -> list[T]:
        """List all registered items.

        Args:
            **filters: Optional filters

        Returns:
            List of registered items

        Example:
            >>> all_tools = registry.list()
            >>> search_tools = registry.list(category="search")
        """
        ...

    def list_names(self) -> builtins.list[str]:
        """List all registered item names.

        Returns:
            List of item names

        Example:
            >>> names = registry.list_names()
            >>> # ["search", "analyze", "transform"]
        """
        ...

    def clear(self) -> None:
        """Clear all registered items.

        Example:
            >>> registry.clear()
        """
        ...

    def count(self) -> int:
        """Get count of registered items.

        Returns:
            Number of items

        Example:
            >>> count = registry.count()
        """
        ...


class SearchableRegistry(Protocol, Generic[T]):
    """Registry with search capabilities.

    Extends basic registry with search and filtering.

    Example:
        >>> registry = SearchableToolRegistry()
        >>> tools = registry.search("database")
        >>> tools = registry.filter(category="data", tags=["sql"])
    """

    def search(self, query: str) -> list[T]:
        """Search for items.

        Args:
            query: Search query

        Returns:
            Matching items

        Example:
            >>> tools = registry.search("database")
        """
        ...

    def filter(self, **criteria) -> list[T]:
        """Filter items by criteria.

        Args:
            **criteria: Filter criteria

        Returns:
            Filtered items

        Example:
            >>> tools = registry.filter(category="data", active=True)
        """
        ...


class ObservableRegistry(Protocol, Generic[T]):
    """Registry with observation capabilities.

    Allows subscribing to registry changes.

    Example:
        >>> registry = ObservableToolRegistry()
        >>> registry.on_register(lambda name, item: print(f"Registered: {name}"))
        >>> registry.register("search", search_tool)  # Triggers callback
    """

    def on_register(self, callback: Callable[[str, T], None]) -> None:
        """Register callback for item registration.

        Args:
            callback: Function called when item is registered

        Example:
            >>> registry.on_register(lambda name, item: logger.info(f"Registered {name}"))
        """
        ...

    def on_unregister(self, callback: Callable[[str], None]) -> None:
        """Register callback for item unregistration.

        Args:
            callback: Function called when item is unregistered

        Example:
            >>> registry.on_unregister(lambda name: logger.info(f"Unregistered {name}"))
        """
        ...


class CategorizedRegistry(Protocol, Generic[T]):
    """Registry with category support.

    Organizes items into categories.

    Example:
        >>> registry = CategorizedToolRegistry()
        >>> registry.register("search", search_tool, category="data")
        >>> data_tools = registry.list_by_category("data")
        >>> categories = registry.list_categories()
    """

    def list_by_category(self, category: str) -> list[T]:
        """List items in a category.

        Args:
            category: Category name

        Returns:
            Items in category

        Example:
            >>> data_tools = registry.list_by_category("data")
        """
        ...

    def list_categories(self) -> list[str]:
        """List all categories.

        Returns:
            List of category names

        Example:
            >>> categories = registry.list_categories()
            >>> # ["data", "ml", "api"]
        """
        ...

    def get_category(self, name: str) -> str | None:
        """Get category of an item.

        Args:
            name: Item name

        Returns:
            Category name or None

        Example:
            >>> category = registry.get_category("search")
            >>> # "data"
        """
        ...


class MetadataRegistry(Protocol, Generic[T]):
    """Registry with metadata support.

    Stores and retrieves metadata for items.

    Example:
        >>> registry = MetadataToolRegistry()
        >>> registry.set_metadata("search", {"version": "1.0", "author": "alice"})
        >>> metadata = registry.get_metadata("search")
    """

    def set_metadata(self, name: str, metadata: dict[str, Any]) -> None:
        """Set metadata for an item.

        Args:
            name: Item name
            metadata: Metadata dictionary

        Example:
            >>> registry.set_metadata("search", {"version": "1.0"})
        """
        ...

    def get_metadata(self, name: str) -> dict[str, Any]:
        """Get metadata for an item.

        Args:
            name: Item name

        Returns:
            Metadata dictionary

        Example:
            >>> metadata = registry.get_metadata("search")
        """
        ...

    def update_metadata(self, name: str, updates: dict[str, Any]) -> None:
        """Update metadata for an item.

        Args:
            name: Item name
            updates: Metadata updates

        Example:
            >>> registry.update_metadata("search", {"version": "1.1"})
        """
        ...


__all__ = [
    "CategorizedRegistry",
    "MetadataRegistry",
    "ObservableRegistry",
    "Registry",
    "SearchableRegistry",
]
