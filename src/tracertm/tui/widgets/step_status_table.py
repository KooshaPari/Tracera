"""Step status table for quality runner TUI.

Displays DAG steps with status (pending/running/passed/failed/skipped) and duration.
"""

from typing import Any

try:
    from textual.widgets import DataTable

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    DataTable = object

from tracertm.tui.quality_root import DAG_CONFIG, LAST_RUN_JSON, LOG_DIR


def load_step_status() -> tuple[list[str], list[tuple[str, str, str]]]:
    """Load step order and status from DAG config and last-run.

    Returns (step_names, rows) where rows are (display, status, duration).
    """
    import json
    import yaml

    steps: dict[str, dict] = {}
    if DAG_CONFIG.exists():
        data = yaml.safe_load(DAG_CONFIG.read_text())
        steps = data.get("steps", {})
    step_order = list(steps.keys()) if steps else []

    results: dict[str, int | str] = {}
    step_details: dict[str, dict] = {}
    if LAST_RUN_JSON.exists():
        try:
            data = json.loads(LAST_RUN_JSON.read_text())
            results = data.get("steps", {})
            step_details = data.get("step_details", {})
        except (json.JSONDecodeError, OSError):
            pass

    def _fmt_duration(sec: float) -> str:
        if sec <= 0:
            return "-"
        return f"{sec:.1f}s" if sec < 60 else f"{sec / 60:.1f}m"

    rows: list[tuple[str, str, str]] = []
    for name in step_order:
        display = steps.get(name, {}).get("display", name)
        code = results.get(name, "pending")
        details = step_details.get(name, {})
        dur_sec = details.get("duration", 0) if isinstance(details, dict) else 0
        duration_str = _fmt_duration(dur_sec) if dur_sec else "-"
        if code == "skipped":
            status = "skipped"
            duration = "-"
        elif isinstance(code, int):
            status = "passed" if code == 0 else "failed"
            duration = duration_str
        else:
            exit_path = LOG_DIR / f"{name}.exit"
            if exit_path.exists():
                try:
                    c = int(exit_path.read_text().strip())
                    status = "passed" if c == 0 else "failed"
                except (ValueError, OSError):
                    status = "running"
            else:
                status = "pending"
            duration = "-"

        icons = {
            "passed": "[green]✓[/]",
            "failed": "[red]✗[/]",
            "skipped": "[dim]⊘[/]",
            "running": "[yellow]●[/]",
            "pending": "[dim]○[/]",
        }
        icon = icons.get(status, "?")
        rows.append((display, f"{icon} {status}", duration))

    return (step_order, rows)


if TEXTUAL_AVAILABLE:

    class StepStatusTable(DataTable):
        """DataTable showing quality DAG step status."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self._step_names: list[str] = []

        def on_mount(self) -> None:
            self.add_columns("Step", "Status", "Duration")
            self.refresh_steps()

        def refresh_steps(self) -> None:
            """Reload step order and status from disk."""
            step_names, rows = load_step_status()
            self._step_names = step_names
            self.clear()
            for display, status, duration in rows:
                self.add_row(display, status, duration)

        def get_selected_step(self) -> str | None:
            """Return step name for currently selected row, or None."""
            if not self._step_names or self.cursor_row is None:
                return None
            idx = self.cursor_row
            if 0 <= idx < len(self._step_names):
                return self._step_names[idx]
            return None
