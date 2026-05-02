#!/usr/bin/env python3
"""Entry point for quality runner TUI.

Usage:
  task quality:tui
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

try:
    from tracertm.tui.apps.quality_runner_app import TEXTUAL_AVAILABLE, QualityRunnerApp
except ImportError:
    sys.exit(1)

if not TEXTUAL_AVAILABLE:
    sys.exit(1)


def main() -> int:  # noqa: D103
    app = QualityRunnerApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
