"""
File-based progress callback implementation.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .base import ProgressCallback

if TYPE_CHECKING:
    from ..core import CommandStage


class FileCallback(ProgressCallback):
    """Progress callback that appends stage updates to a log file.

    Useful for offline auditing of command pipelines. The callback opens the file lazily
    and keeps it open for the lifetime of the run to minimise I/O overhead.
    """

    def __init__(self, log_file: str):
        self.log_file = log_file
        self.file_handle = None

    def _ensure_file(self) -> None:
        """Lazily open the target log file in append mode.

        Avoids unnecessary file handles when no output is produced. This method is safe
        to call multiple times; it only opens the file on the first invocation.
        """
        if self.file_handle is None:
            self.file_handle = open(self.log_file, "a")

    def on_stage_start(self, stage: CommandStage) -> None:
        """Append a start record for ``stage`` to the log file.

        Args:
            stage: Stage metadata containing name and description.
        """
        self._ensure_file()
        timestamp = datetime.now().isoformat()
        self.file_handle.write(f"[{timestamp}] START: {stage.name} - {stage.description}\n")
        self.file_handle.flush()

    def on_stage_progress(self, stage: CommandStage) -> None:
        """Append the most recent log line for ``stage`` to the file.

        Args:
            stage: Stage metadata including log history.
        """
        if stage.logs:
            self._ensure_file()
            latest_log = stage.logs[-1]
            timestamp = datetime.now().isoformat()
            self.file_handle.write(f"[{timestamp}] PROGRESS: {stage.name} - {latest_log}\n")
            self.file_handle.flush()

    def on_stage_complete(self, stage: CommandStage) -> None:
        """Append a completion record with elapsed time.

        Args:
            stage: Stage metadata containing duration information.
        """
        self._ensure_file()
        timestamp = datetime.now().isoformat()
        duration = stage.duration or 0
        self.file_handle.write(f"[{timestamp}] COMPLETE: {stage.name} in {duration:.2f}s\n")
        self.file_handle.flush()

    def on_stage_error(self, stage: CommandStage) -> None:
        """Append an error record for ``stage``.

        Args:
            stage: Stage metadata containing error message.
        """
        self._ensure_file()
        timestamp = datetime.now().isoformat()
        self.file_handle.write(f"[{timestamp}] ERROR: {stage.name} - {stage.error}\n")
        self.file_handle.flush()

    def close(self) -> None:
        """Flush and close the underlying log file handle.

        Safe to call multiple times; subsequent calls are no-ops. Should be invoked at
        the end of a run to ensure file descriptors are released.
        """
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
