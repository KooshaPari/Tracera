#!/usr/bin/env python3
"""Detect obvious comments that don't add value.

Usage:
    python scripts/check_obvious_comments.py [--fix]

Examples:
    python scripts/check_obvious_comments.py
    python scripts/check_obvious_comments.py --fix  # Remove obvious comments
"""

import argparse
import re
import sys
from pathlib import Path


OBVIOUS_PATTERNS = [
    # Simple actions
    (r'^\s*#\s*(Get|Set|Return|Create|Update|Delete)\s+\w+\s*$', 'obvious-action'),
    (r'^\s*#\s*(Increment|Decrement)\s+\w+\s*$', 'obvious-operation'),
    (r'^\s*#\s*(Initialize|Setup)\s+\w+\s*$', 'obvious-init'),
    (r'^\s*#\s*(Call|Invoke)\s+\w+\s*$', 'obvious-call'),

    # Redundant type descriptions
    (r'^\s*#\s*(String|Integer|Boolean|List|Dict)\s*$', 'redundant-type'),

    # Code restatements
    (r'^\s*#\s*for\s+\w+\s+in\s+', 'restates-loop'),
    (r'^\s*#\s*if\s+\w+\s*[=<>]', 'restates-condition'),
]


def is_obvious_comment(line: str) -> tuple[bool, str]:
    """Check if a comment is obvious.

    Args:
        line: Line of code to check

    Returns:
        (is_obvious, reason) tuple
    """
    for pattern, reason in OBVIOUS_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True, reason

    return False, ""


def check_obvious_comments(fix: bool = False) -> int:
    """Check for obvious comments.

    Args:
        fix: If True, remove obvious comments from files

    Returns:
        Exit code (0=success, 1=issues found)
    """
    issues = []
    files_modified = 0

    for file in Path("src").rglob("*.py"):
        # Skip generated files
        if any(part in file.parts for part in ["migrations", "__pycache__", ".next"]):
            continue

        file_issues = []
        lines = list(file.open())

        for i, line in enumerate(lines, 1):
            is_obvious, reason = is_obvious_comment(line)
            if is_obvious:
                file_issues.append((i, line.strip(), reason))
                issues.append((file, i, line.strip(), reason))

        # Fix mode: remove obvious comments
        if fix and file_issues:
            new_lines = []
            obvious_line_numbers = {issue[0] for issue in file_issues}

            for i, line in enumerate(lines, 1):
                if i not in obvious_line_numbers:
                    new_lines.append(line)

            # Write back modified file
            file.write_text("".join(new_lines))
            files_modified += 1
            print(f"✓ Fixed {file} ({len(file_issues)} comments removed)")

    # Report results
    if issues:
        if not fix:
            print(f"\n⚠️  Found {len(issues)} obvious comments in {len(set(i[0] for i in issues))} files:\n")

            # Group by file
            by_file = {}
            for file, line_no, line, reason in issues:
                by_file.setdefault(file, []).append((line_no, line, reason))

            # Show top 10 files
            for file, file_issues in sorted(by_file.items(), key=lambda x: -len(x[1]))[:10]:
                print(f"\n{file} ({len(file_issues)} issues):")
                for line_no, line, reason in file_issues[:5]:
                    print(f"  Line {line_no}: {line}")
                    print(f"    Reason: {reason}")

                if len(file_issues) > 5:
                    print(f"  ... and {len(file_issues) - 5} more")

            total_files = len(by_file)
            if total_files > 10:
                print(f"\n... and {total_files - 10} more files")

            print(f"\n💡 Run with --fix to automatically remove obvious comments")
            return 1
        else:
            print(f"\n✅ Removed {len(issues)} obvious comments from {files_modified} files")
            return 0

    print("\n✅ No obvious comments found")
    return 0


def main() -> int:
    """Parse arguments and run comment check."""
    parser = argparse.ArgumentParser(
        description="Check for obvious comments that don't add value"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically remove obvious comments"
    )

    args = parser.parse_args()
    return check_obvious_comments(fix=args.fix)


if __name__ == "__main__":
    sys.exit(main())
