"""Observer pattern implementation for the reactive system.

This module contains the Observer class for managing subscriptions and notifications.
"""

import asyncio
import weakref
from collections.abc import Callable
from threading import RLock
from typing import Any


class Observer:
    """Observer pattern implementation with priority-based notifications and weak
    references to prevent memory leaks.

    Features:
    - Priority-based notification ordering
    - Weak references to observers
    - Automatic cleanup of dead references
    - Support for async and sync callbacks
    - Error isolation (one observer failure doesn't affect others)

    Example:
        >>> observer = Observer()
        >>>
        >>> def on_change(old_val, new_val):
        ...     print(f"Changed: {old_val} -> {new_val}")
        >>>
        >>> # Subscribe with priority (higher = called first)
        >>> observer.subscribe(on_change, priority=10)
        >>>
        >>> # Notify all observers
        >>> await observer.notify(old_value=5, new_value=10)
        >>>
        >>> # Unsubscribe
        >>> observer.unsubscribe(on_change)
    """

    def __init__(self):
        self._observers: list[tuple[int, Callable, bool]] = []  # (priority, callback, is_weak)
        self._weak_refs: dict[int, weakref.ref] = {}
        self._lock = RLock()
        self._next_id = 0

    def subscribe(self, callback: Callable, priority: int = 0, weak: bool = True) -> int:
        """Subscribe to notifications.

        Args:
            callback: Function to call on notification (signature: callback(old_val, new_val))
            priority: Priority level (higher values called first)
            weak: Use weak reference to prevent memory leaks

        Returns:
            Subscription ID for later unsubscription
        """
        with self._lock:
            sub_id = self._next_id
            self._next_id += 1

            if weak:
                # Store weak reference (use WeakMethod for bound methods)
                import inspect

                if inspect.ismethod(callback):
                    ref = weakref.WeakMethod(callback, lambda _: self._cleanup_dead_ref(sub_id))
                else:
                    ref = weakref.ref(callback, lambda _: self._cleanup_dead_ref(sub_id))
                self._weak_refs[sub_id] = ref
                self._observers.append((priority, sub_id, True))
            else:
                # Store strong reference
                self._observers.append((priority, callback, False))

            # Keep sorted by priority (descending)
            self._observers.sort(key=lambda x: x[0], reverse=True)

            return sub_id

    def unsubscribe(self, callback_or_id: Callable | int):
        """Unsubscribe from notifications.

        Args:
            callback_or_id: Either the callback function or subscription ID
        """
        with self._lock:
            if isinstance(callback_or_id, int):
                # Remove by ID
                self._observers = [
                    (p, cb, w) for p, cb, w in self._observers if not (w and cb == callback_or_id)
                ]
                self._weak_refs.pop(callback_or_id, None)
            else:
                # Remove by callback
                self._observers = [
                    (p, cb, w)
                    for p, cb, w in self._observers
                    if not (not w and cb == callback_or_id)
                ]

    async def notify(self, old_value: Any, new_value: Any, **kwargs):
        """Notify all observers of a change.

        Args:
            old_value: Previous value
            new_value: New value
            **kwargs: Additional metadata passed to observers
        """
        with self._lock:
            observers = self._observers.copy()

        for _priority, callback_or_id, is_weak in observers:
            try:
                # Resolve callback
                if is_weak:
                    ref = self._weak_refs.get(callback_or_id)
                    if ref is None:
                        continue
                    callback = ref()
                    if callback is None:
                        # Dead reference, will be cleaned up
                        continue
                else:
                    callback = callback_or_id

                # Call callback (handle both sync and async)
                if asyncio.iscoroutinefunction(callback):
                    await callback(old_value, new_value, **kwargs)
                else:
                    callback(old_value, new_value, **kwargs)

            except Exception as e:
                # Isolate errors - one failing observer shouldn't break others
                print(f"Error in observer callback: {e}")

    def notify_sync(self, old_value: Any, new_value: Any, **kwargs):
        """Synchronous notification (blocks until all observers called).

        Args:
            old_value: Previous value
            new_value: New value
            **kwargs: Additional metadata passed to observers
        """
        with self._lock:
            observers = self._observers.copy()

        for _priority, callback_or_id, is_weak in observers:
            try:
                # Resolve callback
                if is_weak:
                    ref = self._weak_refs.get(callback_or_id)
                    if ref is None:
                        continue
                    callback = ref()
                    if callback is None:
                        continue
                else:
                    callback = callback_or_id

                # Call sync callback only
                if not asyncio.iscoroutinefunction(callback):
                    callback(old_value, new_value, **kwargs)

            except Exception as e:
                print(f"Error in observer callback: {e}")

    def _cleanup_dead_ref(self, sub_id: int):
        """
        Clean up dead weak reference.
        """
        with self._lock:
            self._observers = [
                (p, cb, w) for p, cb, w in self._observers if not (w and cb == sub_id)
            ]
            self._weak_refs.pop(sub_id, None)

    def clear(self):
        """
        Remove all observers.
        """
        with self._lock:
            self._observers.clear()
            self._weak_refs.clear()

    def observer_count(self) -> int:
        """
        Get number of active observers.
        """
        with self._lock:
            return len(self._observers)
