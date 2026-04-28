"""
Custom text stream wrappers used during capture.
"""

from __future__ import annotations

import contextlib
import io
import threading
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from collections.abc import Callable


class StreamWriter(io.StringIO):
    def __init__(
        self, original_stream: TextIO | None, callback: Callable[[str], None], source: str,
    ):
        super().__init__()
        self._original_stream = original_stream
        self._callback = callback
        self._source = source
        self._lock = threading.RLock()

    def write(self, text: str) -> int:  # pragma: no cover - exercised indirectly
        with self._lock:
            if self._original_stream:
                try:
                    self._original_stream.write(text)
                    self._original_stream.flush()
                except Exception:
                    pass

            if text and text.strip():
                self._callback(text)

            return len(text)

    def flush(self) -> None:  # pragma: no cover - exercised indirectly
        with self._lock:
            if self._original_stream:
                with contextlib.suppress(Exception):
                    self._original_stream.flush()


__all__ = ["StreamWriter"]
