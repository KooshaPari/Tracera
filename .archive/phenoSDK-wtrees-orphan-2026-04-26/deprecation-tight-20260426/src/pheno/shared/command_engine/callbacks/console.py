"""
Callback implementation module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ProgressCallback

if TYPE_CHECKING:
    from ..core import CommandStage


class ConsoleProgressCallback(ProgressCallback):
    """Simple progress callback that prints updates to stdout.

    Useful for CLI workflows or debugging command pipelines without a GUI. The callback
    intentionally keeps state minimal so it can be reused across multiple command runs.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def on_stage_start(self, stage: CommandStage) -> None:
        """Print a start marker for ``stage``.

        Args:
            stage: Stage metadata provided by the engine.
        """
        print(f"▶️  {stage.description}...")

    def on_stage_progress(self, stage: CommandStage) -> None:
        """Print intermediate stage progress when verbose output is enabled.

        Args:
            stage: Stage metadata including accumulated logs.
        """
        if self.verbose and stage.logs:
            latest_log = stage.logs[-1]
            print(f"   {latest_log}")

    def on_stage_complete(self, stage: CommandStage) -> None:
        """Print a completion marker with optional duration.

        Args:
            stage: Stage metadata containing completion timing.
        """
        duration = stage.duration
        if duration:
            print(f"✅ {stage.description} completed in {duration:.2f}s")
        else:
            print(f"✅ {stage.description} completed")

    def on_stage_error(self, stage: CommandStage) -> None:
        """Print an error marker for ``stage`` failures.

        Args:
            stage: Stage metadata containing error details.
        """
        print(f"❌ {stage.description} failed: {stage.error}")
