#!/usr/bin/env python3
"""Auto-migration script for pheno-sdk consolidation.

Rewrites common imports from kit-specific modules to the new consolidated paths.
Dry-run by default; pass --apply to write changes.

Usage:
  python tools/migrate_imports.py <path> [--apply]
"""

import argparse
import re
from pathlib import Path

MAPPINGS: dict[str, str] = {
    # TUI kit specific mappings (order matters - more specific first)
    r"from\s+tui_kit\.([a-zA-Z_][a-zA-Z0-9_.]*)\s+import": "from pheno.ui.tui.\1 import",
    r"from\s+tui_kit\s+import": "from pheno.ui.tui import",
    r"import\s+tui_kit": "import pheno.ui.tui as tui_kit",
    # Core areas
    r"from\s+db_kit\s+import": "from pheno.data.db import",
    r"from\s+observability_kit\s+import": "from pheno.infra.observability import",
    r"from\s+stream_kit\s+import": "from pheno.web.streaming import",
    r"from\s+adapter_kit\s+import": "from pheno.core.adapters import",
    r"from\s+config_kit\s+import": "from pheno.core.config import",
    r"from\s+event_kit\s+import": "from pheno.data.events import",
    r"from\s+vector_kit\s+import": "from pheno.data.vectors import",
    r"from\s+storage_kit\s+import": "from pheno.data.storage import",
    r"from\s+workflow_kit\s+import": "from pheno.ai.workflows import",
    r"from\s+orchestrator_kit\s+import": "from pheno.ai.orchestrator import",
}

FILE_PATTERNS = (".py",)


def migrate_file(path: Path, apply: bool = False) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text
    for pattern, replacement in MAPPINGS.items():
        text = re.sub(pattern, replacement, text)

    if text != original:
        if apply:
            path.write_text(text, encoding="utf-8")
        return 1
    return 0


def scan_and_migrate(root: Path, apply: bool = False) -> int:
    changed = 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in FILE_PATTERNS:
            try:
                changed += migrate_file(p, apply=apply)
            except Exception:
                pass
    return changed


def main():
    ap = argparse.ArgumentParser(description="Pheno-SDK import migration tool")
    ap.add_argument("path", type=str, help="Directory to scan")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default dry-run)")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    count = scan_and_migrate(root, apply=args.apply)
    if args.apply:
        print(f"✅ Applied migration to {count} files in {root}")
    else:
        print(f"🔎 Dry-run: {count} files would be modified in {root} (use --apply to write)")


if __name__ == "__main__":
    main()
