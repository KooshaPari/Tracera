"""Quality root path for TUI. Supports QUALITY_ROOT for shared-project usage."""

from pathlib import Path
import os

# Default: trace root (trace/src/tracertm/tui/quality_root.py -> trace/)
_DEFAULT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


def get_quality_root() -> Path:
    """Project root for quality runs. Uses QUALITY_ROOT env when set."""
    root = os.environ.get("QUALITY_ROOT")
    if root:
        return Path(root).resolve()
    return _DEFAULT_ROOT


ROOT = get_quality_root()
LOG_DIR = ROOT / ".quality" / "logs"
LAST_RUN_JSON = ROOT / ".quality" / "last-run.json"
DAG_CONFIG = ROOT / "config" / "quality-dag.yaml"
FIX_AGENTS_JSON = ROOT / ".quality" / "fix-agents.json"
