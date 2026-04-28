#!/usr/bin/env python3
"""Replace logger.error with logger.exception in except blocks."""

import re
import subprocess
from pathlib import Path


def main():
    """Replace logger.error with logger.exception in exception handlers."""
    # Get files with TRY400 errors
    result = subprocess.run(
        ["ruff", "check", "src/", "--select", "TRY400", "-q"],
        capture_output=True,
        text=True,
    )

    # Parse file paths from ruff output
    files = set()
    for line in result.stdout.split('\n'):
        if line.strip():
            match = re.match(r'^(src/[^:]+):', line)
            if match:
                files.add(match.group(1))

    files_modified = 0
    replacements = 0

    for file_path_str in files:
        path = Path(file_path_str)
        if not path.exists():
            continue

        content = path.read_text()
        original_content = content

        # Replace logger.error with logger.exception in exception contexts
        # This is safe because TRY400 only fires in except blocks
        content = re.sub(
            r'logger\.error\(',
            'logger.exception(',
            content
        )

        # Only write if changed
        if content != original_content:
            path.write_text(content)
            files_modified += 1
            replacements += original_content.count('logger.error(')

    print(f"Modified {files_modified} files")
    print(f"Replaced ~{replacements} logger.error with logger.exception")


if __name__ == "__main__":
    main()
