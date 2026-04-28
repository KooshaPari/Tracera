"""
Rich progress callback implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ProgressCallback

if TYPE_CHECKING:
    from ..core import CommandStage


class RichProgressCallback(ProgressCallback):
    """Progress callback that renders Rich progress bars for command stages.

    Requires the ``rich`` library and is intended for advanced terminal UIs.
    The callback keeps a reference to the Rich progress instance so that nested
    command runs share a single UI.
    """

    def __init__(self, console=None):
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.progress import (
                Progress,
                SpinnerColumn,
                TextColumn,
                TimeElapsedColumn,
            )
            from rich.text import Text

            self.console = console or Console()
            self.Progress = Progress
            self.SpinnerColumn = SpinnerColumn
            self.TextColumn = TextColumn
            self.TimeElapsedColumn = TimeElapsedColumn
            self.Panel = Panel
            self.Text = Text
            self._progress = None
            self._task_id = None

        except ImportError:
            raise ImportError("Rich is required for RichProgressCallback")

    def on_stage_start(self, stage: CommandStage) -> None:
        """Initialise or update the Rich progress bar for ``stage``.

        Args:
            stage: Stage metadata provided by the engine.
        """
        if self._progress is None:
            self._progress = self.Progress(
                self.SpinnerColumn(),
                self.TextColumn("[progress.description]{task.description}"),
                self.TimeElapsedColumn(),
                console=self.console,
            )
            self._progress.start()

        self._task_id = self._progress.add_task(stage.description, total=None)

    def on_stage_progress(self, stage: CommandStage) -> None:
        """Update the progress bar description with the latest stage log entry.

        Args:
            stage: Stage metadata including up-to-date logs.
        """
        if self._progress and self._task_id is not None and stage.logs:
            latest_log = stage.logs[-1]
            self._progress.update(
                self._task_id, description=f"{stage.description} - {latest_log}",
            )

    def on_stage_complete(self, stage: CommandStage) -> None:
        """Mark the progress task as complete and display elapsed time.

        Args:
            stage: Stage metadata containing duration information.
        """
        if self._progress and self._task_id is not None:
            duration = stage.duration or 0
            self._progress.update(
                self._task_id,
                description=f"✅ {stage.description} ({duration:.2f}s)",
                completed=True,
            )

    def on_stage_error(self, stage: CommandStage) -> None:
        """Mark the progress task as failed and show the error message.

        Args:
            stage: Stage metadata containing error information.
        """
        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id, description=f"❌ {stage.description} - {stage.error}", completed=True,
            )

    def cleanup(self) -> None:
        """Stop the Rich progress bar and release associated resources.

        Should be invoked once the command completes to avoid leaving the terminal in an
        inconsistent state.
        """
        if self._progress:
            self._progress.stop()
            self._progress = None
