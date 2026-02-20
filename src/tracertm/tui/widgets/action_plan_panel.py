"""Action plan panel for quality runner TUI.

Displays by-file issues from quality logs.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from textual.widgets import Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Static = object

FILE_LINE_PATTERNS = [
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs)):(\d+):(\d+):\s*(.+)$"),
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs)):(\d+):\s*(.+)$"),
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs))\((\d+),(\d+)\):\s*(.+)$"),
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs))\((\d+)\):\s*(.+)$"),
]
GOFMT_FILE = re.compile(r"^\s*(.+\.go)\s*$")

from tracertm.tui.quality_root import DAG_CONFIG, LOG_DIR, ROOT

SPLIT_STEPS_FALLBACK = [
    ("naming", "Naming", "lint", "Python"),
    ("go-lint", "Go lint", "lint", "Go"),
    ("go-proto", "Go proto", "lint", "Go"),
    ("py-lint", "Python lint", "lint", "Python"),
    ("py-type", "Python type", "lint", "Python"),
    ("fe-lint", "Frontend lint", "lint", "Frontend"),
    ("fe-type", "Frontend type", "lint", "Frontend"),
    ("go-build", "Go build", "test", "Go"),
    ("go-test", "Go test", "test", "Go"),
    ("py-test", "Python test", "test", "Python"),
    ("fe-build", "Frontend build", "test", "Frontend"),
    ("fe-test", "Frontend test", "test", "Frontend"),
]


def _load_split_steps() -> list[tuple[str, str, str, str]]:
    """Derive SPLIT_STEPS from quality-dag.yaml when available."""
    if not DAG_CONFIG.exists():
        return SPLIT_STEPS_FALLBACK
    try:
        import yaml
        data = yaml.safe_load(DAG_CONFIG.read_text())
        steps = data.get("steps", {})
    except Exception:
        return SPLIT_STEPS_FALLBACK
    if not steps:
        return SPLIT_STEPS_FALLBACK

    def _suite(name: str) -> str:
        if name.startswith("py-") or name == "naming":
            return "Python"
        if name.startswith("go-"):
            return "Go"
        if name.startswith("fe-"):
            return "Frontend"
        return "Python"

    def _category(name: str) -> str:
        return "test" if "-test" in name or "-build" in name else "lint"

    return [(name, cfg.get("display", name), _category(name), _suite(name)) for name, cfg in steps.items()]


SPLIT_STEPS = _load_split_steps()


def _normalize_path(raw: str, cwd: Path) -> str:
    raw = raw.strip()
    for prefix in ("./backend/", "backend/", "./", ""):
        if raw.startswith(prefix):
            p = (cwd / (raw[len(prefix) :] if prefix else raw)).resolve()
            try:
                return str(p.relative_to(cwd))
            except ValueError:
                return raw
    return raw


def _extract_by_file(text: str, cwd: Path, suite: str) -> dict[str, list[tuple[int | None, str]]]:
    by_file: dict[str, list[tuple[int | None, str]]] = defaultdict(list)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("make[", "$ ")) or "*** [" in line:
            continue
        for pat in FILE_LINE_PATTERNS:
            m = pat.match(line)
            if m:
                g = m.groups()
                fp = _normalize_path(g[0], cwd)
                msg = (g[3] if len(g) == 4 else g[2]).strip()
                by_file[fp].append((int(g[1]), msg))
                break
        else:
            if suite == "Go":
                m = GOFMT_FILE.match(line)
                if m and "vet" not in line and "gofmt" not in line:
                    by_file[_normalize_path(m.group(1), cwd)].append((None, "gofmt: needs formatting"))
    return dict(by_file)


def load_action_plan() -> str:
    """Parse logs and return formatted action plan string."""
    cwd = ROOT
    by_file: dict[str, list[tuple[str, int | None, str]]] = defaultdict(list)

    for stem, display_name, _cat, suite in SPLIT_STEPS:
        log_path = LOG_DIR / f"{stem}.log"
        if not log_path.exists():
            continue
        try:
            text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for fp, entries in _extract_by_file(text, cwd, suite).items():
            for line_no, msg in entries:
                by_file[fp].append((display_name, line_no, msg))

    if not by_file:
        return "[dim]No issues found. Run quality to see results.[/]"

    lines = []
    for fp in sorted(by_file.keys()):
        entries = by_file[fp]
        parts = []
        for step_name, line_no, msg in entries:
            loc = f":{line_no}" if line_no else ""
            suffix = "..." if len(msg) > 60 else ""
            parts.append(f"{step_name}{loc}: {msg[:60]}{suffix}")
        lines.append(f"[bold]{fp}[/]\n  " + "\n  ".join(parts))
    return "\n\n".join(lines)


if TEXTUAL_AVAILABLE:

    class ActionPlanPanel(Static):
        """Static widget showing by-file issues from quality logs."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__("", *args, **kwargs)

        def on_mount(self) -> None:
            self.refresh_content()

        def refresh_content(self) -> None:
            """Parse logs and update displayed content."""
            self.update(load_action_plan())
