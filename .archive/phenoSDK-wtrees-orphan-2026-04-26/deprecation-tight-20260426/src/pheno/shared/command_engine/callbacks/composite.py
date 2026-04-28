"""
Composite progress callback implementations.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING

from .base import ProgressCallback

if TYPE_CHECKING:
    from ..core import CommandStage


class CompositeCallback(ProgressCallback):
    """Progress callback that fans out events to multiple underlying callbacks.

    Exceptions raised by individual callbacks are logged but do not halt other
    callbacks, ensuring best-effort delivery.
    """

    def __init__(self, callbacks: list[ProgressCallback]):
        self.callbacks = callbacks

    def on_stage_start(self, stage: CommandStage) -> None:
        """Forward stage-start events to each delegate.

        Args:
            stage: Stage metadata emitted by the command engine.
        """
        for callback in self.callbacks:
            try:
                callback.on_stage_start(stage)
            except Exception as e:
                logger.warning(f"Callback failed: {e}")

    def on_stage_progress(self, stage: CommandStage) -> None:
        """Forward stage-progress events to each delegate.

        Args:
            stage: Stage metadata containing progress updates.
        """
        for callback in self.callbacks:
            try:
                callback.on_stage_progress(stage)
            except Exception as e:
                logger.warning(f"Callback failed: {e}")

    def on_stage_complete(self, stage: CommandStage) -> None:
        """Forward stage-complete events to each delegate.

        Args:
            stage: Stage metadata containing completion information.
        """
        for callback in self.callbacks:
            try:
                callback.on_stage_complete(stage)
            except Exception as e:
                logger.warning(f"Callback failed: {e}")

    def on_stage_error(self, stage: CommandStage) -> None:
        """Forward stage-error events to each delegate.

        Args:
            stage: Stage metadata containing error details.
        """
        for callback in self.callbacks:
            try:
                callback.on_stage_error(stage)
            except Exception as e:
                logger.warning(f"Callback failed: {e}")
