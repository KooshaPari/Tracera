"""
Watchdog handler for reacting to configuration file updates.
"""

import logging
import time
from collections.abc import Callable

from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """
    Debounces filesystem events and forwards YAML changes.
    """

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback
        self._debounce_seconds = 1.0
        self._last_modified: dict[str, float] = {}

    def on_modified(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return

        current_time = time.time()
        last_time = self._last_modified.get(event.src_path, 0)
        if current_time - last_time < self._debounce_seconds:
            return

        self._last_modified[event.src_path] = current_time

        if event.src_path.endswith((".yaml", ".yml")):
            logger.info("Config file changed: %s", event.src_path)
            self._callback(event.src_path)


__all__ = ["ConfigFileHandler"]
