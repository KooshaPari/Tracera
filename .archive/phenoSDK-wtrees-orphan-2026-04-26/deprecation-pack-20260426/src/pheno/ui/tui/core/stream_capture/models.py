"""
Data models representing captured output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .levels import LogLevel
from .rich_support import HAS_RICH, Text

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class CapturedLine:
    """
    A single captured line with metadata.
    """

    text: str
    timestamp: datetime
    source: str  # "stdout", "stderr", "logger"
    level: LogLevel | None = None
    logger_name: str | None = None
    thread_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def format_rich(self, show_timestamp: bool = True, show_level: bool = True) -> Text | str:
        if not HAS_RICH:
            return self.text

        from rich.text import Text  # Local import to satisfy type checkers

        text = Text()

        if show_timestamp:
            ts = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
            text.append(f"[{ts}] ", style="dim")

        if show_level and self.level:
            level_styles = {
                LogLevel.DEBUG: "dim cyan",
                LogLevel.INFO: "blue",
                LogLevel.WARNING: "yellow",
                LogLevel.ERROR: "red",
                LogLevel.CRITICAL: "bold red on white",
            }
            text.append(f"{self.level.value:8} ", style=level_styles.get(self.level, "white"))
        elif show_level:
            source_styles = {"stdout": "green", "stderr": "red", "logger": "blue"}
            text.append(f"{self.source:8} ", style=source_styles.get(self.source, "white"))

        if self.logger_name:
            text.append(f"[{self.logger_name}] ", style="cyan")

        text.append(self.text)
        return text


__all__ = ["CapturedLine"]
