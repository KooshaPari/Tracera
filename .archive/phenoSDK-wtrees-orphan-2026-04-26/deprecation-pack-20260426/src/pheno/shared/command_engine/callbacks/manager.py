"""
Callback manager for the command engine.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .base import CallbackEvent, CompletionCallback, ProgressCallback

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..core import CommandResult, CommandStage


class CallbackManager:
    """Orchestrates registration and execution of command engine callbacks.

    The manager keeps separate registries for progress, completion, and event-style
    callbacks while recording a history of emitted events for later inspection (e.g.,
    testing or analytics).
    """

    def __init__(self):
        self._progress_callbacks: list[ProgressCallback] = []
        self._completion_callbacks: list[CompletionCallback] = []
        self._event_callbacks: dict[str, list[Callable]] = {}
        self._events: list[CallbackEvent] = []

    def register_progress_callback(self, callback: ProgressCallback) -> None:
        """Register a progress callback to receive stage lifecycle updates.

        Args:
            callback: ProgressCallback implementation.
        """
        self._progress_callbacks.append(callback)

    def register_completion_callback(self, callback: CompletionCallback) -> None:
        """Register a completion callback to receive final command notifications.

        Args:
            callback: CompletionCallback implementation.
        """
        self._completion_callbacks.append(callback)

    def register_event_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callable that reacts to emitted events of ``event_type``.

        Args:
            event_type: Event category string.
            callback: Callable accepting a :class:`CallbackEvent`.
        """
        if event_type not in self._event_callbacks:
            self._event_callbacks[event_type] = []
        self._event_callbacks[event_type].append(callback)

    def trigger_stage_start(self, stage: CommandStage) -> None:
        """Invoke registered callbacks for the start of ``stage``.

        Args:
            stage: Stage metadata about to execute.
        """
        for callback in self._progress_callbacks:
            try:
                callback.on_stage_start(stage)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

        self._emit_event("stage_start", {"stage": stage.name}, stage.name)

    def trigger_stage_progress(self, stage: CommandStage) -> None:
        """Invoke registered callbacks when ``stage`` reports progress.

        Args:
            stage: Stage metadata with updated progress information.
        """
        for callback in self._progress_callbacks:
            try:
                callback.on_stage_progress(stage)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

        self._emit_event("stage_progress", {"stage": stage.name}, stage.name)

    def trigger_stage_complete(self, stage: CommandStage) -> None:
        """Invoke registered callbacks after ``stage`` completes.

        Args:
            stage: Stage metadata including duration and logs.
        """
        for callback in self._progress_callbacks:
            try:
                callback.on_stage_complete(stage)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

        self._emit_event("stage_complete", {"stage": stage.name}, stage.name)

    def trigger_stage_error(self, stage: CommandStage) -> None:
        """Invoke registered callbacks after ``stage`` fails.

        Args:
            stage: Stage metadata including error information.
        """
        for callback in self._progress_callbacks:
            try:
                callback.on_stage_error(stage)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

        self._emit_event("stage_error", {"stage": stage.name, "error": stage.error}, stage.name)

    def trigger_command_complete(self, result: CommandResult) -> None:
        """Notify completion callbacks that the command has finished.

        Args:
            result: CommandResult capturing success status and metrics.
        """
        for callback in self._completion_callbacks:
            try:
                if result.success:
                    callback.on_command_complete(result)
                else:
                    callback.on_command_error(result)
            except Exception as e:
                logger.warning(f"Completion callback failed: {e}")

        self._emit_event(
            "command_complete",
            {"success": result.success, "exit_code": result.exit_code, "duration": result.duration},
        )

    def _emit_event(
        self, event_type: str, data: dict[str, Any], stage_name: str | None = None,
    ) -> None:
        """Emit an event to registered callbacks and store it in the history.

        Args:
            event_type: Event category string.
            data: Structured payload for the event.
            stage_name: Optional stage associated with the event.
        """
        event = CallbackEvent(
            event_type=event_type, timestamp=datetime.now(), data=data, stage_name=stage_name,
        )

        self._events.append(event)

        # Trigger event-specific callbacks
        if event_type in self._event_callbacks:
            for callback in self._event_callbacks[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.warning(f"Event callback failed: {e}")

    def get_events(self, event_type: str | None = None) -> list[CallbackEvent]:
        """Retrieve a snapshot of recorded events.

        Args:
            event_type: Optional filter limiting results to a specific type.

        Returns:
            List of matching :class:`CallbackEvent` records.
        """
        if event_type:
            return [event for event in self._events if event.event_type == event_type]
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear the in-memory event history.

        Useful at the start of a new command execution when historical events are no
        longer relevant.
        """
        self._events.clear()
