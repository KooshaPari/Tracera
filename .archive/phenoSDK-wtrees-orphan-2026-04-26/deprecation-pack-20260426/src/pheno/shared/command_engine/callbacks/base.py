"""
Base callback interfaces and event structures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from ..core import CommandResult, CommandStage


class ProgressCallback(ABC):
    """
    Contract for receiving progress updates during command execution.
    """

    @abstractmethod
    def on_stage_start(self, stage: CommandStage) -> None: ...

    @abstractmethod
    def on_stage_progress(self, stage: CommandStage) -> None: ...

    @abstractmethod
    def on_stage_complete(self, stage: CommandStage) -> None: ...

    @abstractmethod
    def on_stage_error(self, stage: CommandStage) -> None: ...


class CompletionCallback(ABC):
    """
    Contract for receiving final command completion notifications.
    """

    @abstractmethod
    def on_command_complete(self, result: CommandResult) -> None: ...

    @abstractmethod
    def on_command_error(self, result: CommandResult) -> None: ...


@dataclass
class CallbackEvent:
    """
    Immutable record capturing an emitted callback event.
    """

    event_type: str
    timestamp: datetime
    data: dict[str, object]
    stage_name: str | None = None


__all__ = ["CallbackEvent", "CompletionCallback", "ProgressCallback"]
