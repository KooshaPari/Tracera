"""
Logging-based progress callback implementation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .base import ProgressCallback

if TYPE_CHECKING:
    from ..core import CommandStage


class LoggingCallback(ProgressCallback):
    """Progress callback that forwards updates to the Python logging subsystem.

    Logging level choices map to stage lifecycle events (info for start/end, debug for
    progress, error for failures).
    """

    def __init__(self, logger_name: str = "command_engine"):
        self.logger = logging.getLogger(logger_name)

    def on_stage_start(self, stage: CommandStage) -> None:
        """Emit an info log for the start of ``stage``.

        Args:
            stage: Stage metadata.
        """
        self.logger.info(f"Starting stage: {stage.name} - {stage.description}")

    def on_stage_progress(self, stage: CommandStage) -> None:
        """Emit a debug log containing the latest stage log entry.

        Args:
            stage: Stage metadata containing log history.
        """
        if stage.logs:
            latest_log = stage.logs[-1]
            self.logger.debug(f"Stage {stage.name}: {latest_log}")

    def on_stage_complete(self, stage: CommandStage) -> None:
        """Emit an info log when ``stage`` finishes successfully.

        Args:
            stage: Stage metadata, including duration.
        """
        duration = stage.duration or 0
        self.logger.info(f"Completed stage: {stage.name} in {duration:.2f}s")

    def on_stage_error(self, stage: CommandStage) -> None:
        """Emit an error log when ``stage`` fails.

        Args:
            stage: Stage metadata containing error details.
        """
        self.logger.error(f"Failed stage: {stage.name} - {stage.error}")
