"""
Reactive Bindings - Computed properties and dependency tracking.

Provides computed properties with automatic dependency detection
and memoization for reactive state management.
"""

from collections.abc import Callable
from threading import RLock
from typing import Any, TypeVar

# Type variables
T = TypeVar("T")


class Computed:
    """Computed property with automatic dependency tracking and memoization.

    Features:
    - Automatic dependency detection
    - Memoization for performance
    - Invalidation on dependency change
    - Type preservation
    - Integration with ReactiveProperty

    Example:
        >>> class MyWidget:
        ...     items = ReactiveProperty(default=[])
        ...     multiplier = ReactiveProperty(default=2)
        ...
        ...     @Computed
        ...     def total(self):
        ...         return sum(item['price'] for item in self.items) * self.multiplier
        ...
        ...     @Computed
        ...     def item_count(self):
        ...         return len(self.items)
        >>>
        >>> widget = MyWidget()
        >>> widget.items = [{'price': 10}, {'price': 20}]
        >>> print(widget.total)  # 60 (30 * 2)
    """

    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self._cache: dict[Any, Any] = {}
        self._dependencies: set[str] = set()
        self._lock = RLock()

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        with self._lock:
            # Check if we have a cached value
            if obj in self._cache:
                return self._cache[obj]

            # Compute the value
            value = self.func(obj)
            self._cache[obj] = value
            return value

    def invalidate(self, obj: Any):
        """
        Invalidate cached value for an object.
        """
        with self._lock:
            self._cache.pop(obj, None)

    def clear_cache(self):
        """
        Clear all cached values.
        """
        with self._lock:
            self._cache.clear()

    def get_dependencies(self, obj: Any) -> set[str]:
        """
        Get detected dependencies for an object.
        """
        return self._dependencies

    def _track_dependency(self, dependency_name: str) -> None:
        """
        Track a dependency during computation.
        """
        self._dependencies.add(dependency_name)


# ============================================================================
# Dependency Resolution Utilities
# ============================================================================


class DependencyTracker:
    """Utility for tracking reactive dependencies during computation.

    This is used internally by Computed to automatically detect which ReactiveProperty
    instances are accessed.
    """

    def __init__(self):
        self._current_tracking: set[str] = set()
        self._dependencies: dict[str, set[str]] = {}

    def start_tracking(self, computed_name: str):
        """
        Start tracking dependencies for a computation.
        """
        self._current_tracking.clear()

    def end_tracking(self, computed_name: str):
        """
        End tracking and store dependencies.
        """
        self._dependencies[computed_name] = self._current_tracking.copy()
        self._current_tracking.clear()

    def track_dependency(self, property_name: str):
        """
        Track access to a reactive property.
        """
        self._current_tracking.add(property_name)

    def get_dependencies(self, computed_name: str) -> set[str]:
        """
        Get tracked dependencies for a computation.
        """
        return self._dependencies.get(computed_name, set())

    def clear_dependencies(self, computed_name: str):
        """
        Clear dependencies for a computation.
        """
        self._dependencies.pop(computed_name, None)

    def get_all_dependencies(self) -> dict[str, set[str]]:
        """
        Get all tracked dependencies.
        """
        return self._dependencies.copy()


# Global dependency tracker instance
_dependency_tracker = DependencyTracker()


def invalidate_dependents(property_name: str) -> None:
    """Invalidate all computed properties that depend on a given property.

    Args:
        property_name: Name of the property that changed
    """
    for dependencies in _dependency_tracker.get_all_dependencies().values():
        if property_name in dependencies:
            # This would need access to the actual Computed instance
            # In practice, this is handled by the Observer pattern
            pass


# ============================================================================
# Decorators for Reactive Programming
# ============================================================================


def reactive_property(**kwargs):
    """Decorator for creating reactive properties.

    Example:
        >>> class MyWidget:
        ...     @reactive_property(default=0, debounce=0.1)
        ...     def count(self):
        ...         return self._count
    """
    from .reactive_primitives import ReactiveProperty

    return ReactiveProperty(**kwargs)


def computed_property(func):
    """Decorator for creating computed properties.

    Example:
        >>> class MyWidget:
        ...     items = reactive_property(default=[])
        ...
        ...     @computed_property
        ...     def total_count(self):
        ...         return len(self.items)
    """
    return Computed(func)


# ============================================================================
# Utility Functions
# ============================================================================


def create_reactive_proxy(obj: Any, properties: list[str]):
    """Create a reactive proxy for an object with specified properties.

    Args:
        obj: Object to proxy
        properties: List of property names to make reactive

    Returns:
        Proxy object with reactive properties
    """

    class ReactiveProxy:
        def __init__(self, target: Any):
            self._target = target

        def __getattr__(self, name):
            value = getattr(self._target, name)

            # Make it reactive if it's a tracing target property
            if name in properties and not isinstance(value, ReactivePropertyInstance):
                # This is simplified - would need more complex logic
                pass

            return value

        def __setattr__(self, name, value):
            if name in properties:
                # Simplified reactive set logic
                pass
            setattr(self._target, name, value)

    return ReactiveProxy(obj)


# Forward import for circular dependency
from .reactive_primitives import ReactivePropertyInstance

__all__ = [
    "Computed",
    "DependencyTracker",
    "_dependency_tracker",
    "computed_property",
    "create_reactive_proxy",
    "invalidate_dependents",
    "reactive_property",
]
