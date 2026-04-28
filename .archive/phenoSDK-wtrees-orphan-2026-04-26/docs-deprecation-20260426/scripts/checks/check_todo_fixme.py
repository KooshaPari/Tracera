#!/usr/bin/env python3
"""Check for TODO and FIXME comments in Python files.

Tracks technical debt and ensures proper documentation.
"""

import argparse
import re
import sys
from pathlib import Path

TODO_PATTERN = re.compile(r"#\s*(TODO|FIXME|XXX|HACK|NOTE)\s*[:]*\s*(.+)", re.IGNORECASE)


def check_file_for_todos(file_path: Path, warnings: bool = True) -> list[tuple[int, str, str]]:
    """
    Check a single file for TODO/FIXME comments.
    """
    todos = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []

    for line_num, line in enumerate(lines, 1):
        # Skip comments in docstrings
        if '"""' in line or "'''" in line:
            continue

        match = TODO_PATTERN.search(line)
        if match:
            todo_type = match.group(1).upper()
            todo_text = match.group(2).strip()

            if not warnings and todo_type in ["NOTE"]:
                continue

            todos.append((line_num, todo_type, todo_text))

    return todos


def main():
    parser = argparse.ArgumentParser(description="Check for TODO/FIXME comments")
    parser.add_argument(
        "--strict", action="store_true", help="Treat all TODOs as errors (not just FIXME/XXX/HACK)",
    )
    parser.add_argument(
        "--exclude-note", action="store_true", help="Exclude NOTE comments from warnings",
    )
    parser.add_argument("files", nargs="*", help="Files to check")

    args = parser.parse_args()

    if not args.files:
        print("No files provided for TODO/FIXME checking")
        return 0

    all_todos = {}
    issue_types = ["FIXME", "XXX", "HACK"]
    if args.strict:
        issue_types.extend(["TODO"])

    for file_path in args.files:
        path = Path(file_path)
        if not path.exists() or not path.suffix == ".py":
            continue

        todos = check_file_for_todos(path, warnings=not args.exclude_note)
        if todos:
            all_todos[path] = todos

    if not all_todos:
        print("✅ No TODO/FIXME comments found")
        return 0

    print("📝 Found TODO/FIXME comments:")
    for file_path, todos in all_todos.items():
        print(f"\n📄 {file_path}:")
        for line_num, todo_type, todo_text in todos:
            status = "❌" if todo_type in issue_types else "⚠️"
            print(f"  {status} Line {line_num}: [{todo_type}] {todo_text}")

    # Count issues
    issues = sum(
        1 for todos in all_todos.values() for _, todo_type, _ in todos if todo_type in issue_types
    )

    if issues > 0:
        print(f"\n❌ Found {issues} issue(s) that should be addressed")
        return 1
    print(f"\n⚠️  Found {len(all_todos)} file(s) with TODO/NOTE comments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
