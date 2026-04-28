"""
Reactive State Management System with Auto-Refresh - Refactored Version

This module provides a comprehensive reactive state management system with:
- Centralized state management (StateStore)
- Observable properties with auto-refresh (ReactiveProperty)
- Observer pattern implementation
- Computed/derived properties with automatic dependency tracking
- Transaction support for batch updates
- Time-travel debugging (undo/redo)
- State persistence
- Weak references to prevent memory leaks
- Debouncing support
- Change history tracking

This module re-exports reactive functionality from specialized modules:
- Reactive primitives: ReactiveProperty, ReactivePropertyInstance
- Reactive bindings: Computed, DependencyTracker, decorators
- Textual integrations: StateStore, ReactiveWidget, TransactionContext

Example Usage:
    >>> from pheno.ui.tui.core.reactive import StateStore, ReactiveProperty, Computed, ReactiveWidget
    >>>
    >>> # Example 1: ReactiveProperty with auto-refresh
    >>> class CounterWidget(ReactiveWidget):
    ...     count = ReactiveProperty(default=0, debounce=0.1)
    ...
    ...     def watch_count(self, old_val, new_val):
    ...         # Auto-called when count changes (thanks to watch_ prefix)
    ...         print(f"Count changed: {old_val} -> {new_val}")
    ...         self.refresh()  # Auto-refresh the widget
    >>>
    >>> # Example 2: Computed properties with auto-caching
    >>> class CartWidget(ReactiveWidget):
    ...     items = ReactiveProperty(default=[])
    ...
    ...     @Computed
    ...     def total(self):
    ...         # Automatically recomputed when items changes
    ...         return sum(item['price'] for item in self.items)
    ...
    ...     @Computed
    ...     def item_count(self):
    ...         return len(self.items)
    >>>
    >>> # Example 3: Centralized state with StateStore
    >>> store = StateStore()
    >>> store.set_state("user.name", "Alice")
    >>> store.set_state("user.age", 30)
    >>>
    >>> # Subscribe to state changes
    >>> store.subscribe("user.name", lambda old, new, **kw: print(f"Name: {old} -> {new}"))
    >>> store.subscribe("user.*", lambda old, new, **kw: print(f"User changed at {kw['path']}"))
    >>>
    >>> # Example 4: Transactions for atomic batch updates
    >>> with store.transaction() as tx:
    ...     store.set_state("user.name", "Bob")
    ...     store.set_state("user.age", 31)
    ...     # Both changes are applied atomically
    >>>
    >>> # Example 5: Time-travel debugging
    >>> store.undo()  # Undo last change
    >>> store.redo()  # Redo undone change
    >>> store.get_history()  # Get change history
"""

from .reactive_bindings import (
    Computed,
    DependencyTracker,
    _dependency_tracker,
    computed_property,
    create_reactive_proxy,
    invalidate_dependents,
    reactive_property,
)

# Re-export from specialized modules for backward compatibility
from .reactive_primitives import ReactiveProperty, ReactivePropertyInstance
from .textual_integrations import ReactiveWidget, StateStore, TransactionContext

__all__ = [
    # Reactive bindings
    "Computed",
    "DependencyTracker",
    # Reactive primitives
    "ReactiveProperty",
    "ReactivePropertyInstance",
    "ReactiveWidget",
    # Textual integrations
    "StateStore",
    "TransactionContext",
    "_dependency_tracker",
    "computed_property",
    "create_reactive_proxy",
    "invalidate_dependents",
    "reactive_property",
]
