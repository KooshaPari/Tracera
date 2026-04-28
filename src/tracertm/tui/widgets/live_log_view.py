"""Live log view for quality runner TUI.

Displays streaming log content for the selected step.
"""

from pathlib import Path
from typing import Any

try:
    from textual.widgets import RichLog

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    RichLog = object

from tracertm.tui.quality_root import LOG_DIR


if TEXTUAL_AVAILABLE:

    class LiveLogView(RichLog):
        """RichLog that tails a step's log file."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self._current_step: str | None = None
            self._last_size: int = 0

        def show_step(self, step_name: str) -> None:
            """Switch to displaying log for given step."""
            self._current_step = step_name
            self._last_size = 0
            self.clear()
            self._append_new_content()

        def _append_new_content(self) -> None:
            if not self._current_step:
                return
            log_path = LOG_DIR / f"{self._current_step}.log"
            if not log_path.exists():
                self.write(f"[dim]No log for {self._current_step}[/]")
                return
            try:
                text = log_path.read_text(encoding="utf-8", errors="replace")
                size = len(text)
                if size > self._last_size:
                    new_content = text[self._last_size :]
                    self._last_size = size
                    for line in new_content.splitlines():
                        self.write(line)
            except OSError:
                self.write("[red]Error reading log[/]")

        def refresh_log(self) -> None:
            """Append any new content since last read."""
            self._append_new_content()
