"""Agent process list for quality runner TUI.

Displays fix agent jobs (name, status). Placeholder until fix runner is implemented.
"""

import json
from pathlib import Path
from typing import Any

try:
    from textual.widgets import Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Static = object

from tracertm.tui.quality_root import FIX_AGENTS_JSON


def load_agent_list() -> str:
    """Read fix-agents.json and return formatted string."""
    if not FIX_AGENTS_JSON.exists():
        return "[dim]No fix agents running. Press 'f' to run fix agents after quality fails.[/]"
    try:
        data = json.loads(FIX_AGENTS_JSON.read_text())
        agents = data.get("agents", [])
        if not agents:
            return "[dim]No fix agents.[/]"
        lines = [f"  {a.get('name', '?')}: {a.get('status', '?')}" for a in agents]
        return "Fix Agents:\n" + "\n".join(lines)
    except (json.JSONDecodeError, OSError):
        return "[dim]Error reading fix agents.[/]"


if TEXTUAL_AVAILABLE:

    class AgentProcessList(Static):
        """Static widget showing fix agent jobs."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__("", *args, **kwargs)

        def on_mount(self) -> None:
            self.refresh_content()

        def refresh_content(self) -> None:
            """Read fix-agents.json and update display."""
            self.update(load_agent_list())
