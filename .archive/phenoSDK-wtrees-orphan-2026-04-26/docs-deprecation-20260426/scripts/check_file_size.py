#!/usr/bin/env python3
"""Check that all Python files are under the line limit.

Usage:
    python scripts/check_file_size.py [--max LINES] [--target LINES]

Examples:
    python scripts/check_file_size.py
    python scripts/check_file_size.py --max 500 --target 350
"""

import argparse
import sys
from pathlib import Path


def check_file_size(
    max_lines: int = 500,
    target_lines: int = 350,
    src_dir: str = "src"
) -> int:
    """Check file sizes and report violations.

    Args:
        max_lines: Hard maximum line count (error if exceeded)
        target_lines: Target line count (warning if exceeded)
        src_dir: Source directory to scan

    Returns:
        Exit code (0=success, 1=errors found)
    """
    errors = []
    warnings = []

    src_path = Path(src_dir)
    if not src_path.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return 1

    for file in src_path.rglob("*.py"):
        # Skip generated files and migrations
        if any(part in file.parts for part in ["migrations", "__pycache__", ".next"]):
            continue

        line_count = sum(1 for _ in file.open())

        if line_count > max_lines:
            errors.append((file, line_count))
        elif line_count > target_lines:
            warnings.append((file, line_count))

    # Report errors
    if errors:
        print(f"\n❌ {len(errors)} files exceed {max_lines} lines (HARD MAX):\n")
        for file, count in sorted(errors, key=lambda x: -x[1])[:20]:
            excess = count - max_lines
            print(f"  {file}: {count} lines (+{excess} over limit)")

        if len(errors) > 20:
            print(f"\n  ... and {len(errors) - 20} more files")

        print(f"\n💡 Decompose these files into smaller, focused modules")
        return 1

    # Report warnings
    if warnings:
        print(f"\n⚠️  {len(warnings)} files exceed {target_lines} lines (TARGET):\n")
        for file, count in sorted(warnings, key=lambda x: -x[1])[:10]:
            excess = count - target_lines
            print(f"  {file}: {count} lines (+{excess} over target)")

        if len(warnings) > 10:
            print(f"\n  ... and {len(warnings) - 10} more files")

    # Success
    total_files = sum(1 for _ in src_path.rglob("*.py"))
    print(f"\n✅ All {total_files} files under {max_lines} lines")

    if warnings:
        compliant = total_files - len(warnings)
        pct = (compliant / total_files) * 100
        print(f"📊 {compliant}/{total_files} files ({pct:.1f}%) under target ({target_lines} lines)")

    return 0


def main() -> int:
    """Parse arguments and run file size check."""
    parser = argparse.ArgumentParser(
        description="Check Python file sizes against limits"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=500,
        help="Hard maximum line count (default: 500)"
    )
    parser.add_argument(
        "--target",
        type=int,
        default=350,
        help="Target line count (default: 350)"
    )
    parser.add_argument(
        "--src",
        default="src",
        help="Source directory to scan (default: src)"
    )

    args = parser.parse_args()

    return check_file_size(
        max_lines=args.max,
        target_lines=args.target,
        src_dir=args.src
    )


if __name__ == "__main__":
    sys.exit(main())
