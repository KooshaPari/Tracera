"""Textual integrations for reactive state management.

Provides StateStore and Textual-specific reactive widgets integration with transactions,
time-travel debugging, and persistence.
"""

import json
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any

from .observer import Observer
from .reactive_primitives import ReactiveProperty
from .state import StateChange, Transaction

# Widget type (would be imported from textual.widgets)
ReactiveWidget = Any


class StateStore:
    """Centralized state management with transactions, time-travel, and persistence.

    Features:
    - Hierarchical state storage (dot notation: "user.profile.name")
    - Transaction support for atomic updates
    - Time-travel debugging (undo/redo)
    - State persistence (JSON)
    - Observer pattern for state changes
    - Wildcard subscriptions ("user.*")
    - Change history tracking
    - Weak references to prevent memory leaks

    Example:
        >>> store = StateStore()
        >>> store.set_state("user.name", "Alice")
        >>> store.set_state("user.age", 30)
        >>> print(store.get_state("user.name"))  # "Alice"
        >>>
        >>> # Subscribe to changes
        >>> store.subscribe("user.name", lambda old, new: print(f"Name: {old} -> {new}"))
        >>>
        >>> # Transaction
        >>> with store.transaction() as tx:
        ...     store.set_state("user.name", "Bob")
        ...     store.set_state("user.age", 31)
        >>>
        >>> # Time-travel
        >>> store.undo()
        >>> store.redo()
        >>> store.get_history()
    """

    def __init__(self, persistence_file: Path | None = None):
        self._initialize_state_containers()
        self._initialize_locks_and_transactions()
        self._persistence_file = persistence_file
        self._load_persisted_state()

    def _initialize_state_containers(self) -> None:
        """
        Initialize all state storage containers.
        """
        self._state = {}
        self._observers = {}
        self._history = []
        self._undo_stack = []
        self._redo_stack = []

    def _initialize_locks_and_transactions(self) -> None:
        """
        Initialize thread safety and transaction state.
        """
        self._lock = RLock()
        self._current_transaction = None

    def _load_persisted_state(self) -> None:
        """
        Load persisted state from file if available.
        """
        if not self._persistence_file or not self._persistence_file.exists():
            return

        try:
            with open(self._persistence_file) as f:
                self._state = json.load(f)
        except Exception as e:
            print(f"Failed to load persisted state: {e}")

    def get_state(self, path: str, default: Any = None) -> Any:
        """Get state value using dot notation.

        Args:
            path: Dot-separated path to state value
            default: Default value if path doesn't exist

        Returns:
            State value at path
        """
        return self._get_nested_value(self._state, path, default)

    def set_state(self, path: str, value: Any) -> None:
        """Set state value using dot notation.

        Args:
            path: Dot-separated path to state value
            value: New value to set
        """
        old_value = self._get_nested_value(self._state, path)

        if self._current_transaction:
            # Add to transaction
            self._current_transaction.add_change(StateChange(path, old_value, value))
        else:
            # Apply immediately
            self._apply_change(StateChange(path, old_value, value))

    def subscribe(self, pattern: str, callback, priority: int = 0, weak: bool = True) -> int:
        """Subscribe to state changes matching a pattern.

        Args:
            pattern: Pattern to match (exact path or wildcard like "user.*")
            callback: Function called with (old_value, new_value, **kwargs)
            priority: Subscription priority (higher = called first)
            weak: Whether to use weak reference (avoid memory leaks)

        Returns:
            Subscription ID for unsubscribing
        """
        if pattern not in self._observers:
            self._observers[pattern] = Observer()

        return self._observers[pattern].subscribe(callback, priority, weak)

    def unsubscribe(self, pattern: str, callback_or_id) -> None:
        """Unsubscribe from state changes.

        Args:
            pattern: Pattern originally subscribed to
            callback_or_id: Callback function or subscription ID
        """
        if pattern in self._observers:
            self._observers[pattern].unsubscribe(callback_or_id)

    @contextmanager
    def transaction(self) -> "TransactionContext":
        """Context manager for atomic state updates.

        Usage:
            >>> with store.transaction() as tx:
            ...     store.set_state("user.name", "Bob")
            ...     store.set_state("user.age", 31)
            ...     # Changes applied atomically when context exits
        """
        return TransactionContext(self)

    def undo(self) -> bool:
        """Undo the last state change.

        Returns:
            True if undo was successful, False otherwise
        """
        if not self._history:
            return False

        change = self._history.pop()
        self._undo_stack.append(change)
        self._apply_change(StateChange(change.path, change.new_value, change.old_value))
        return True

    def redo(self) -> bool:
        """Redo the last undone state change.

        Returns:
            True if redo was successful, False otherwise
        """
        if not self._undo_stack:
            return False

        change = self._undo_stack.pop()
        self._redo_stack.append(change)
        self._apply_change(StateChange(change.path, change.old_value, change.new_value))
        return True

    def get_history(self, limit: int | None = None) -> list[StateChange]:
        """Get the history of state changes.

        Args:
            limit: Maximum number of changes to return

        Returns:
            List of state changes
        """
        history = self._history.copy()
        if limit:
            history = history[-limit:]
        return history

    def persist_state(self) -> bool:
        """Persist current state to file.

        Returns:
            True if successful, False otherwise
        """
        if not self._persistence_file:
            return False

        try:
            with open(self._persistence_file, "w") as f:
                json.dump(self._state, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to persist state: {e}")
            return False

    def get_all_state(self) -> dict:
        """
        Get a copy of the entire state.
        """
        return self._state.copy()

    def clear_state(self) -> None:
        """
        Clear all state and history.
        """
        with self._lock:
            self._state.clear()
            self._history.clear()
            self._undo_stack.clear()
            self._redo_stack.clear()

    def _get_nested_value(self, data: dict, path: str, default: Any = None) -> Any:
        """
        Get value from nested dictionary using dot notation.
        """
        keys = path.split(".")
        current = data

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]

        return current

    def _set_nested_value(self, data: dict, path: str, value: Any) -> None:
        """
        Set value in nested dictionary using dot notation.
        """
        keys = path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _delete_nested_value(self, data: dict, path: str) -> None:
        """
        Delete value from nested dictionary using dot notation.
        """
        keys = path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                return
            current = current[key]

        if keys[-1] in current:
            del current[keys[-1]]

    def _apply_change(self, change: StateChange) -> None:
        """
        Apply a state change and notify observers.
        """
        self._set_nested_value(self._state, change.path, change.new_value)
        self._history.append(change)
        self._notify_observers(change)

    def _notify_observers(self, change: StateChange) -> None:
        """
        Notify observers of state change.
        """
        # Notify exact path observers
        if change.path in self._observers:
            self._observers[change.path].notify_sync(
                change.old_value, change.new_value, path=change.path,
            )

        # Notify wildcard observers
        for pattern, observer in self._observers.items():
            if pattern.endswith("*") and change.path.startswith(pattern[:-1]):
                observer.notify_sync(change.old_value, change.new_value, path=change.path)


class TransactionContext:
    """
    Context manager for state store transactions.
    """

    def __init__(self, store: StateStore):
        self.store = store
        self.transaction = None

    def __enter__(self) -> Transaction:
        self.transaction = Transaction()
        self.store._current_transaction = self.transaction
        return self.transaction

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            # Commit transaction
            self.transaction.commit()
            for change in self.transaction.changes:
                self.store._history.append(change)
                self.store._notify_observers(change)
        else:
            # Rollback on error
            for change in reversed(self.transaction.changes):
                self.store._set_nested_value(self.store._state, change.path, change.old_value)

        self.store._current_transaction = None
        return False


# ============================================================================
# Reactive Widget Base Class
# ============================================================================


class ReactiveWidget:
    """Base class for widgets that use reactive properties.

    Integrates with Textual widgets and provides:
    - Auto-refresh on property changes
    - Automatic observer registration
    - Performance optimizations
    """

    def __init__(self):
        self._reactive_properties = []
        self._auto_refresh_enabled = True

    def _discover_reactive_properties(self) -> None:
        """
        Discover reactive properties on the widget.
        """
        for attr_name in dir(self):
            attr = getattr(type(self), attr_name, None)
            if isinstance(attr, ReactiveProperty):
                if attr_name not in self._reactive_properties:
                    self._reactive_properties.append(attr_name)
                    # Subscribe to changes with automatic refresh
                    attr.subscribe(self._on_property_changed, weak=False)

    def _on_property_changed(self, old_value, new_value, **kwargs) -> None:
        """
        Handle reactive property changes.
        """
        if self._auto_refresh_enabled:
            self.refresh()

    def refresh(self) -> None:
        """
        Refresh the widget display.
        """
        # This would be implemented by Textual widgets
        if hasattr(self, "refresh"):
            self.refresh()

    def enable_auto_refresh(self, enabled: bool = True) -> None:
        """
        Enable or disable automatic refresh on property changes.
        """
        self._auto_refresh_enabled = enabled

    def get_reactive_properties(self) -> list[str]:
        """
        Get list of reactive property names.
        """
        return self._reactive_properties.copy()


__all__ = [
    "ReactiveWidget",
    "StateStore",
    "TransactionContext",
]
