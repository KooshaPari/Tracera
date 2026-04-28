"""
Optional dependencies for the unified progress widget.
"""

from __future__ import annotations

try:  # pragma: no cover - optional dependency
    from rich.console import Console, Group
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TaskID,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:  # pragma: no cover - fallback when Rich unavailable
    Console = Group = Panel = Progress = Table = Text = Layout = Live = object  # type: ignore
    TaskID = object  # type: ignore
    BarColumn = MofNCompleteColumn = SpinnerColumn = TaskProgressColumn = TextColumn = TimeElapsedColumn = TimeRemainingColumn = object  # type: ignore
    HAS_RICH = False


__all__ = [
    "HAS_RICH",
    "BarColumn",
    "Console",
    "Group",
    "Layout",
    "Live",
    "MofNCompleteColumn",
    "Panel",
    "Progress",
    "SpinnerColumn",
    "Table",
    "TaskID",
    "TaskProgressColumn",
    "Text",
    "TextColumn",
    "TimeElapsedColumn",
    "TimeRemainingColumn",
]
