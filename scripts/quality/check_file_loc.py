#!/usr/bin/env python3
"""File length guard (LOC) to prevent mega-files.

Reads config from config/loc-guard.json and supports env overrides:
- MAX_LOC
- ALLOWLIST_FILE
"""

from __future__ import annotations

import argparse
import json
import os
from fnmatch import fnmatch
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("config/loc-guard.json")
DEFAULT_MAX_LOC = 500
DEFAULT_ALLOWLIST = Path("config/loc-allowlist.txt")

RED = "\033[0;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[0;32m"
NC = "\033[0m"


def load_config(path: Path) -> dict:
    """Load config."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "max_loc": DEFAULT_MAX_LOC,
        "allowlist_file": str(DEFAULT_ALLOWLIST),
        "search_dirs": ["src", "backend", "internal", "frontend/apps", "frontend/packages", "cli"],
        "exclude_dirs": [
            "node_modules",
            ".git",
            ".venv",
            "dist",
            "coverage",
            "playwright-report",
            "storybook-static",
            "docs",
            "ARCHIVE",
            "CONFIG",
            "test-results",
            "openapi",
            "proto",
        ],
        "exclude_paths": ["frontend/apps/web/src/api/schema.ts"],
        "exclude_patterns": [
            "*_pb2.py",
            "*_pb2_grpc.py",
            "*.gen.ts",
            "*.generated.*",
            "*.sql.go",
            "*.d.ts",
            "*.d.mts",
            "*.d.cts",
            "routeTree.gen.ts",
        ],
        "extensions": [".py", ".go", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"],
    }


def load_allowlist(path: Path) -> dict[str, int]:
    """Load allowlist."""
    if not path.exists():
        return {}
    allowlist: dict[str, int] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            allowlist[parts[0]] = int(parts[1])
        except ValueError:
            continue
    return allowlist


def should_exclude(path: Path, exclude_dirs: list[str], exclude_paths: set[str], exclude_patterns: list[str]) -> bool:
    """Should exclude."""
    path_str = str(path)
    if path_str in exclude_paths:
        return True
    if any(part in path.parts for part in exclude_dirs):
        return True
    name = path.name
    return any(fnmatch(name, pattern) for pattern in exclude_patterns)


def iter_files(
    roots: list[Path],
    extensions: set[str],
    exclude_dirs: list[str],
    exclude_paths: set[str],
    exclude_patterns: list[str],
) -> list[Path]:
    """Iter files."""
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in extensions:
                continue
            if should_exclude(path, exclude_dirs, exclude_paths, exclude_patterns):
                continue
            files.append(path)
    return files


def main() -> int:
    """Main."""
    parser = argparse.ArgumentParser(description="Check file length (LOC) guard")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--max-loc", type=int, default=None)
    parser.add_argument("--allowlist", default=None)
    args = parser.parse_args()

    config = load_config(Path(args.config))
    max_loc = args.max_loc or int(os.getenv("MAX_LOC", config.get("max_loc", DEFAULT_MAX_LOC)))
    allowlist_path = args.allowlist or os.getenv("ALLOWLIST_FILE", config.get("allowlist_file", str(DEFAULT_ALLOWLIST)))
    allowlist = load_allowlist(Path(allowlist_path))

    roots = [Path(p) for p in config.get("search_dirs", [])]
    exclude_dirs = list(config.get("exclude_dirs", []))
    exclude_paths = set(config.get("exclude_paths", []))
    exclude_patterns = list(config.get("exclude_patterns", []))
    extensions = set(config.get("extensions", []))

    violations: list[str] = []
    for path in iter_files(roots, extensions, exclude_dirs, exclude_paths, exclude_patterns):
        try:
            lines = sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        rel_path = str(path)
        allow_max = allowlist.get(rel_path)
        if allow_max is not None:
            if lines > allow_max:
                violations.append(f"{lines}:{rel_path} (allowlist max {allow_max})")
        elif lines > max_loc:
            violations.append(f"{lines}:{rel_path}")

    if violations:
        for entry in sorted(violations, key=lambda v: int(v.split(":", 1)[0]), reverse=True):
            _count, _rest = entry.split(":", 1)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
