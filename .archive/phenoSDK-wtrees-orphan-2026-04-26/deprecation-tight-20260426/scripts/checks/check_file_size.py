#!/usr/bin/env python3
"""Check file size limit for Python files.

Ensures consistent file sizes to prevent code bloat.
"""

import argparse
import ast
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """
    Count lines of code in a Python file.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())

        # Count actual lines of code by walking the AST
        line_numbers = set()
        for node in ast.walk(tree):
            if hasattr(node, "lineno"):
                line_numbers.update(
                    range(node.lineno, getattr(node, "end_lineno", node.lineno) + 1),
                )

        return len(line_numbers)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Error parsing {file_path}: {e}")
        return -1


def main():
    parser = argparse.ArgumentParser(description="Check file size limits")
    parser.add_argument(
        "--max-lines", type=int, default=500, help="Maximum allowed lines of code per file",
    )
    parser.add_argument("files", nargs="*", help="Files to check")

    args = parser.parse_args()

    if not args.files:
        print("No files provided for size checking")
        return 0

    violations = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists() or not path.suffix == ".py":
            continue

        lines = count_lines(path)
        if lines > args.max_lines:
            violations.append((path, lines))
            print(f"❌ {path}: {lines} lines (max: {args.max_lines})")
        elif lines >= 0:
            print(f"✅ {path}: {lines} lines")
        else:
            print(f"⚠️  {path}: Could not analyze")

    if violations:
        print("\n❌ File size violations found:")
        for path, lines in violations:
            ratio = lines / args.max_lines
            print(f"  - {path}: {lines} lines ({ratio:.1f}x limit)")
        return 1
    print(f"\n✅ All files under {args.max_lines} lines limit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
