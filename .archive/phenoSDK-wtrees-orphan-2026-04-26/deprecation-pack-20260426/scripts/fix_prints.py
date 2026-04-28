#!/usr/bin/env python3
"""Replace print() statements with logging in pheno package."""

import re
import subprocess
from pathlib import Path


def main():
    """Replace print statements with appropriate logging calls."""
    # Get all Python files with print statements in src/pheno
    result = subprocess.run(
        ["rg", "print\\(", "src/pheno/", "-l"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("No files with print statements found")
        return

    files = result.stdout.strip().split('\n')
    files_modified = 0
    prints_replaced = 0

    for file_path in files:
        if not file_path:
            continue

        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()
        original_content = content

        # Check if logging is already imported
        has_logging = 'import logging' in content

        # Track if we need to add logging import
        need_logging = False

        # Replace different print patterns
        replacements = [
            # Error messages
            (r'print\(f"Error ([^"]+)"\)', r'logger.error(f"\1")'),
            (r"print\(f'Error ([^']+)'\)", r"logger.error(f'\1')"),
            (r'print\("Error ([^"]+)"\)', r'logger.error("\1")'),
            (r"print\('Error ([^']+)'\)", r"logger.error('\1')"),

            # Warning messages
            (r'print\(f"Warning ([^"]+)"\)', r'logger.warning(f"\1")'),
            (r"print\(f'Warning ([^']+)'\)", r"logger.warning(f'\1')"),

            # Debug/Info messages with format strings
            (r'print\(f"([^"]+)"\)', r'logger.info(f"\1")'),
            (r"print\(f'([^']+)'\)", r"logger.info(f'\1')"),

            # Simple string messages
            (r'print\("([^"]+)"\)', r'logger.info("\1")'),
            (r"print\('([^']+)'\)", r"logger.info('\1')"),
        ]

        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                need_logging = True

        # Add logging import and logger if needed
        if need_logging and not has_logging:
            # Find the right place to add import (after other imports)
            lines = content.split('\n')
            import_line_idx = 0

            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_line_idx = i + 1
                elif line and not line.startswith('#') and import_line_idx > 0:
                    break

            # Add logging import and logger
            if import_line_idx > 0:
                lines.insert(import_line_idx, 'import logging')
                lines.insert(import_line_idx + 1, '')
                lines.insert(import_line_idx + 2, 'logger = logging.getLogger(__name__)')
                lines.insert(import_line_idx + 3, '')
                content = '\n'.join(lines)

        # Only write if content changed
        if content != original_content:
            path.write_text(content)
            files_modified += 1
            # Count replacements
            prints_replaced += len(re.findall(r'logger\.(error|warning|info|debug)\(', content))

    print(f"Modified {files_modified} files")
    print(f"Replaced ~{prints_replaced} print statements with logging")


if __name__ == "__main__":
    main()
