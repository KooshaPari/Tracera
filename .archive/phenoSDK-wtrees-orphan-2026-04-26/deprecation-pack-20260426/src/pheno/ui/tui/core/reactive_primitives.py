"""
Reactive Primitives - Core reactive property infrastructure.

Provides the foundational ReactiveProperty descriptor and instance classes
with support for validation, debouncing, and observer notifications.
"""

import asyncio
from collections.abc import Callable
from threading import RLock
from typing import Any, Generic, TypeVar

from .observer import Observer

# Type variables
T = TypeVar("T")


class ReactivePropertyInstance(Generic[T]):
    """
    Instance of a reactive property bound to a specific object.
    """

    def __init__(self, descriptor: "ReactiveProperty[T]", obj: Any):
        self.descriptor = descriptor
        self.obj = obj
        self._value = descriptor.default
        self._lock = RLock()

    @property
    def value(self) -> T:
        """
        Get the current value.
        """
        return self._value

    def set(self, value: T):
        """
        Set the value with validation and notification.
        """
        with self._lock:
            # Validate if validator provided
            if self.descriptor.validator and not self.descriptor.validator(value):
                raise ValueError(f"Invalid value for {self.descriptor.name}: {value}")

            old_value = self._value
            self._value = value

            # Record change
            from .state import StateChange

            change = StateChange(
                path=f"{self.obj.__class__.__name__}.{self.descriptor.name}",
                old_value=old_value,
                new_value=value,
            )
            self.descriptor._change_history.append(change)

            # Notify observers
            if self.descriptor.debounce:
                self._debounced_notify(old_value, value)
            else:
                self.descriptor.observer.notify_sync(old_value, value)

    def _debounced_notify(self, old_value: T, new_value: T):
        """
        Notify observers with debouncing.
        """
        if self.descriptor._debounce_task:
            self.descriptor._debounce_task.cancel()

        async def debounced_notify():
            await asyncio.sleep(self.descriptor.debounce)
            await self.descriptor.observer.notify(old_value, new_value)

        self.descriptor._debounce_task = asyncio.create_task(debounced_notify())

    def subscribe(self, callback: Callable, priority: int = 0, weak: bool = True) -> int:
        """
        Subscribe to changes in this property.
        """
        return self.descriptor.observer.subscribe(callback, priority, weak)

    def unsubscribe(self, callback_or_id: Callable | int):
        """
        Unsubscribe from changes in this property.
        """
        self.descriptor.observer.unsubscribe(callback_or_id)


class ReactiveProperty(Generic[T]):
    """Reactive property descriptor with auto-refresh, debouncing, and validation.

    Features:
    - Automatic observer notification on change
    - Debouncing support (coalesce rapid changes)
    - Validation hooks
    - Change history tracking
    - Type preservation
    - Integration with Textual's reactive system

    Example:
        >>> class MyWidget:
        ...     count = ReactiveProperty(default=0, debounce=0.1)
        ...     name = ReactiveProperty(default="", validator=lambda x: len(x) > 0)
        ...
        ...     def __init__(self):
        ...         self.count.subscribe(self._on_count_changed)
        ...
        ...     def _on_count_changed(self, old_val, new_val):
        ...         print(f"Count: {old_val} -> {new_val}")
        >>>
        >>> widget = MyWidget()
        >>> widget.count = 5  # Triggers notification
    """

    def __init__(
        self,
        default: T | None = None,
        validator: Callable[[T], bool] | None = None,
        debounce: float | None = None,
        layout: bool = False,
    ):
        self.default = default
        self.validator = validator
        self.debounce = debounce
        self.layout = layout
        self.observer = Observer()
        self._debounce_task: asyncio.Task | None = None
        self._change_history: list[StateChange] = []

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None) -> "ReactivePropertyInstance[T]":
        if obj is None:
            return self

        if not hasattr(obj, self.private_name):
            setattr(obj, self.private_name, ReactivePropertyInstance(self, obj))

        return getattr(obj, self.private_name)

    def __set__(self, obj, value: T):
        if not hasattr(obj, self.private_name):
            setattr(obj, self.private_name, ReactivePropertyInstance(self, obj))

        instance = getattr(obj, self.private_name)
        instance.set(value)

    def get_change_history(self) -> list[StateChange]:
        """
        Get the history of changes for this property.
        """
        return self._change_history.copy()

    def clear_history(self) -> None:
        """
        Clear the change history.
        """
        self._change_history.clear()


__all__ = [
    "ReactiveProperty",
    "ReactivePropertyInstance",
]
