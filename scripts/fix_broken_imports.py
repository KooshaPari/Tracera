#!/usr/bin/env python3
"""Fix files where 'from typing import Any' was inserted inside multi-line import blocks."""

import re
from pathlib import Path

BROKEN_FILES = Path("/tmp/broken_files.txt").read_text(encoding="utf-8").strip().split("\n")
BASE = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/trace")


def fix_file(filepath: str) -> bool:
    """Fix a file with broken import insertion."""
    path = BASE / filepath
    if not path.exists():
        return False

    content = path.read_text()
    lines = content.split("\n")

    # Pattern: a line that is "from typing import Any" that appears inside
    # a multi-line from X import ( block
    modified = False
    typing_import_line = None
    new_lines = []
    i = 0
    in_import_block = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect if we're entering a multi-line import
        if re.match(r"^from\s+\S+\s+import\s*\($", stripped) or (
            re.match(r"^from\s+\S+\s+import\s*\(", stripped) and not stripped.endswith(")")
        ):
            in_import_block = True

        # Check if this line is the misplaced "from typing import Any"
        if stripped == "from typing import Any" and in_import_block:
            # This is the broken import - remove it from here
            typing_import_line = line
            modified = True
            i += 1
            continue

        if in_import_block and ")" in stripped:
            in_import_block = False

        new_lines.append(line)
        i += 1

    if not modified or typing_import_line is None:
        # Try alternate pattern: "from typing import Any" on same line as "from X import ("
        # e.g., "from X import (\nfrom typing import Any\n    Symbol,"
        return False

    # Now insert "from typing import Any" at the right place
    # Find the right insertion point - before the first third-party/local import
    # or after the last stdlib import
    content_new = "\n".join(new_lines)

    # Check if "from typing import Any" already exists elsewhere
    if "from typing import Any" in content_new:
        # Already have it, just write without the duplicate
        path.write_text(content_new)
        return True

    # Check if there's already a "from typing import" line we can extend
    typing_import_match = re.search(r"^(from typing import )(.+)$", content_new, re.MULTILINE)
    if typing_import_match:
        existing_imports = typing_import_match.group(2)
        if "Any" not in existing_imports:
            content_new = content_new.replace(
                typing_import_match.group(0), f"{typing_import_match.group(1)}Any, {existing_imports}"
            )
        path.write_text(content_new)
        return True

    # Need to add "from typing import Any" as a new import line
    # Insert it right before the first "from" import that isn't __future__
    lines_new = content_new.split("\n")
    insert_at = 0
    found_imports = False
    for j, ln in enumerate(lines_new):
        s = ln.strip()
        if s.startswith("from __future__"):
            insert_at = j + 1
            found_imports = True
            continue
        if s.startswith(("import ", "from ")):
            if not found_imports:
                insert_at = j
            found_imports = True
            # If this is a stdlib import (typing, os, sys, etc.), put after it
            if any(
                s.startswith((f"import {m}", f"from {m}"))
                for m in [
                    "abc",
                    "ast",
                    "asyncio",
                    "collections",
                    "contextlib",
                    "copy",
                    "dataclasses",
                    "datetime",
                    "decimal",
                    "enum",
                    "functools",
                    "hashlib",
                    "importlib",
                    "inspect",
                    "io",
                    "itertools",
                    "json",
                    "logging",
                    "math",
                    "operator",
                    "os",
                    "pathlib",
                    "platform",
                    "random",
                    "re",
                    "shutil",
                    "signal",
                    "socket",
                    "string",
                    "subprocess",
                    "sys",
                    "tempfile",
                    "textwrap",
                    "threading",
                    "time",
                    "traceback",
                    "typing",
                    "unittest",
                    "urllib",
                    "uuid",
                    "warnings",
                    "weakref",
                ]
            ):
                insert_at = j + 1
            else:
                # Third-party or local import - insert before this
                break
        elif found_imports and s and not s.startswith("#"):
            break

    lines_new.insert(insert_at, "from typing import Any")
    # Add blank line after if next line is not blank
    if insert_at + 1 < len(lines_new) and lines_new[insert_at + 1].strip():
        if not lines_new[insert_at + 1].strip().startswith("import") and not lines_new[
            insert_at + 1
        ].strip().startswith("from"):
            lines_new.insert(insert_at + 1, "")

    path.write_text("\n".join(lines_new))
    return True


def main() -> None:
    """Fix all broken files."""
    fixed = 0
    len(BROKEN_FILES)
    for f in BROKEN_FILES:
        f = f.strip()
        if not f:
            continue
        if fix_file(f):
            fixed += 1


if __name__ == "__main__":
    main()
