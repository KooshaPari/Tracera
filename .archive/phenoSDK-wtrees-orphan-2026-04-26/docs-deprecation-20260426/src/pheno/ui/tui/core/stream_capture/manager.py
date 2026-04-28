"""
Core stream capture implementation.
"""

from __future__ import annotations

import logging
import sys
import threading
from collections import deque
from contextlib import contextmanager
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self, TextIO

from .handlers import LoggingHandler
from .models import CapturedLine
from .rich_support import HAS_RICH, Console
from .writers import StreamWriter

if TYPE_CHECKING:
    from collections.abc import Callable

    from .levels import LogLevel


class StreamCapture:
    def __init__(
        self,
        *,
        capture_stdout: bool = True,
        capture_stderr: bool = True,
        capture_logging: bool = False,
        max_lines: int = 10000,
        enable_formatting: bool = True,
        filter_fn: Callable[[CapturedLine], bool] | None = None,
        console: Console | None = None,
        progress: Any | None = None,
    ) -> None:
        self.capture_stdout = capture_stdout
        self.capture_stderr = capture_stderr
        self.capture_logging = capture_logging
        self.max_lines = max_lines
        self.enable_formatting = enable_formatting
        self.filter_fn = filter_fn
        self.console = console or (Console() if HAS_RICH else None)
        self.progress = progress

        self._lock = threading.RLock()
        self._lines: deque[CapturedLine] = deque(maxlen=max_lines)
        self._original_stdout: TextIO | None = None
        self._original_stderr: TextIO | None = None
        self._original_handlers: list[logging.Handler] = []
        self._is_capturing = False

    def _append_line(self, line: CapturedLine) -> None:
        if self.filter_fn and not self.filter_fn(line):
            return
        with self._lock:
            self._lines.append(line)

    def _on_line_captured(self, text: str, source: str) -> None:
        line = CapturedLine(text=text.rstrip("\n"), timestamp=datetime.now(), source=source)
        self._append_line(line)

    def _on_log_captured(self, line: CapturedLine) -> None:
        self._append_line(line)

    def start(self) -> None:
        if self._is_capturing:
            return

        if self.capture_stdout:
            self._original_stdout = sys.stdout
            sys.stdout = StreamWriter(
                self._original_stdout, lambda text: self._on_line_captured(text, "stdout"), "stdout",
            )

        if self.capture_stderr:
            self._original_stderr = sys.stderr
            sys.stderr = StreamWriter(
                self._original_stderr, lambda text: self._on_line_captured(text, "stderr"), "stderr",
            )

        if self.capture_logging:
            handler = LoggingHandler(self._on_log_captured)
            handler.setFormatter(logging.Formatter("%(message)s"))
            logging.root.addHandler(handler)
            self._original_handlers.append(handler)

        self._is_capturing = True

    def stop(self) -> None:
        if not self._is_capturing:
            return

        if self.capture_stdout and self._original_stdout:
            sys.stdout = self._original_stdout
            self._original_stdout = None

        if self.capture_stderr and self._original_stderr:
            sys.stderr = self._original_stderr
            self._original_stderr = None

        if self.capture_logging:
            for handler in self._original_handlers:
                logging.root.removeHandler(handler)
            self._original_handlers.clear()

        self._is_capturing = False

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def get_lines(
        self,
        *,
        count: int | None = None,
        level: LogLevel | None = None,
        source: str | None = None,
    ) -> list[CapturedLine]:
        with self._lock:
            lines = list(self._lines)

        if level:
            lines = [line for line in lines if line.level == level]
        if source:
            lines = [line for line in lines if line.source == source]
        if count:
            lines = lines[-count:]
        return lines

    def get_text(self, *, count: int | None = None, formatted: bool = True, **filters) -> str:
        lines = self.get_lines(count=count, **filters)
        if not formatted or not HAS_RICH:
            return "\n".join(line.text for line in lines)

        console = Console()
        with console.capture() as capture:
            for line in lines:
                console.print(line.format_rich() if self.enable_formatting else line.text)
        return capture.get()

    def clear(self) -> None:
        with self._lock:
            self._lines.clear()

    def export(self, filepath: str, *, format: str = "text") -> None:
        lines = self.get_lines()

        if format == "text":
            with open(filepath, "w") as handle:
                for line in lines:
                    handle.write(f"{line.text}\n")
            return

        if format == "json":
            import json

            payload = [
                {
                    "text": line.text,
                    "timestamp": line.timestamp.isoformat(),
                    "source": line.source,
                    "level": line.level.value if line.level else None,
                    "logger": line.logger_name,
                    "metadata": line.metadata,
                }
                for line in lines
            ]
            with open(filepath, "w") as handle:
                json.dump(payload, handle, indent=2)
            return

        if format == "html":
            if not HAS_RICH:
                raise RuntimeError("Rich required for HTML export")

            console = Console(record=True)
            for line in lines:
                console.print(line.format_rich())
            html = console.export_html()
            with open(filepath, "w") as handle:
                handle.write(html)
            return

        raise ValueError(f"Unknown format: {format}")


@contextmanager
def capture_output(*, capture_logging: bool = False, max_lines: int = 1000):
    capture = StreamCapture(capture_logging=capture_logging, max_lines=max_lines)
    capture.start()
    try:
        yield capture
    finally:
        capture.stop()


__all__ = ["StreamCapture", "capture_output"]
