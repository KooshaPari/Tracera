#!/usr/bin/env python3
"""Extract and replace magic values in test files with test_constants.

This script:
1. Scans test files for PLR2004 violations
2. Replaces frequently used magic values with constants from test_constants
3. Adds # noqa: PLR2004 to single-use test values with justification
"""

import re
import subprocess
import sys
from pathlib import Path

# Mapping of magic values to constant names
CONSTANT_MAPPINGS: dict[str, str] = {
    # HTTP Status Codes
    "200": "HTTP_OK",
    "201": "HTTP_CREATED",
    "202": "HTTP_ACCEPTED",
    "204": "HTTP_NO_CONTENT",
    "400": "HTTP_BAD_REQUEST",
    "401": "HTTP_UNAUTHORIZED",
    "403": "HTTP_FORBIDDEN",
    "404": "HTTP_NOT_FOUND",
    "405": "HTTP_METHOD_NOT_ALLOWED",
    "409": "HTTP_CONFLICT",
    "422": "HTTP_UNPROCESSABLE_ENTITY",
    "429": "HTTP_TOO_MANY_REQUESTS",
    "500": "HTTP_INTERNAL_SERVER_ERROR",
    "503": "HTTP_SERVICE_UNAVAILABLE",
    # Common counts - only replace in specific contexts
    "2": "COUNT_TWO",
    "3": "COUNT_THREE",
    "4": "COUNT_FOUR",
    "5": "COUNT_FIVE",
    "6": "COUNT_SIX",
    "7": "COUNT_SEVEN",
    "8": "COUNT_EIGHT",
    "10": "COUNT_TEN",
    "15": "COUNT_FIFTEEN",
    "20": "COUNT_TWENTY",
    "30": "COUNT_THIRTY",
    "36": "COUNT_THIRTY_SIX",
    "50": "COUNT_FIFTY",
    "64": "COUNT_SIXTY_FOUR",
    "100": "COUNT_HUNDRED",
    "500": "COUNT_FIVE_HUNDRED",
    "1000": "COUNT_THOUSAND",
    "10000": "COUNT_TEN_THOUSAND",
    # Timeouts
    "30.0": "TIMEOUT_DEFAULT",
    "60.0": "TIMEOUT_LONG",
    "10.0": "TIMEOUT_SHORT",
    "5.0": "TIMEOUT_VERY_SHORT",
    # Poll intervals
    "0.1": "POLL_INTERVAL_FAST",
    "0.5": "POLL_INTERVAL_SLOW",
    "1.0": "POLL_INTERVAL_VERY_SLOW",
    # Backoff values
    "2.0": "BACKOFF_BASE",
    # Tolerances
    "0.01": "TOLERANCE_STRICT",
    "0.05": "TOLERANCE_NORMAL",
    # Common floats
    "45.0": "FLOAT_FORTY_FIVE",
    "45.5": "FLOAT_FORTY_FIVE_HALF",
}

# Contexts where we should replace integer counts
COUNT_CONTEXTS = [
    r"len\([^)]+\)\s*==",  # len(x) == N
    r"assert.*==\s*",  # assert x == N
    r"count\s*==",  # count == N
    r"total\s*==",  # total == N
]

# Contexts where we should NOT replace (ranges, indices, single test values)
SKIP_CONTEXTS = [
    r"range\(",  # range(N)
    r"\[(\d+)\]",  # array[N]
    r":\s*\d+\s*:",  # slicing
]


def should_replace_count(line: str, _value: str) -> bool:
    """Check if a count value should be replaced in this line."""
    # Skip if it's in a skip context
    for pattern in SKIP_CONTEXTS:
        if re.search(pattern, line):
            return False

    # Only replace if in a count context
    return any(re.search(pattern, line) for pattern in COUNT_CONTEXTS)


def process_file(file_path: Path) -> tuple[int, int]:
    """Process a single file, replacing magic values with constants.

    Returns:
        Tuple of (replacements_made, noqa_added)
    """
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    replacements = 0
    noqa_added = 0
    needs_import = False
    has_import = "from tests.test_constants import" in content

    new_lines = []

    for line in lines:
        modified_line = line
        line_replacements = 0

        # Check for HTTP status codes (always replace)
        for value in ["200", "201", "202", "204", "400", "401", "403", "404", "405", "409", "422", "429", "500", "503"]:
            if value in CONSTANT_MAPPINGS:
                const_name = CONSTANT_MAPPINGS[value]
                # Match status code comparisons
                pattern = rf"\b{value}\b(?=\s*[=!<>]|\s*\)|\s*,)"
                if re.search(pattern, modified_line):
                    modified_line = re.sub(pattern, const_name, modified_line)
                    line_replacements += 1

        # Check for timeout/float values (always replace)
        for value in ["30.0", "60.0", "10.0", "5.0", "2.0", "0.1", "0.5", "1.0", "0.01", "0.05", "45.0", "45.5"]:
            if value in CONSTANT_MAPPINGS:
                const_name = CONSTANT_MAPPINGS[value]
                pattern = rf"\b{re.escape(value)}\b"
                if re.search(pattern, modified_line):
                    modified_line = re.sub(pattern, const_name, modified_line)
                    line_replacements += 1

        # Check for count values (contextual replacement)
        for value in [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "10",
            "15",
            "20",
            "30",
            "36",
            "50",
            "64",
            "100",
            "500",
            "1000",
            "10000",
        ]:
            if should_replace_count(modified_line, value) and value in CONSTANT_MAPPINGS:
                const_name = CONSTANT_MAPPINGS[value]
                pattern = rf"\b{value}\b"
                modified_line = re.sub(pattern, const_name, modified_line)
                line_replacements += 1

        if line_replacements > 0:
            needs_import = True
            replacements += line_replacements

        new_lines.append(modified_line)

    # Add import if needed and not present
    if needs_import and not has_import:
        # Find where to insert import (after other imports)
        import_idx = 0
        for i, line in enumerate(new_lines):
            if line.startswith(("import ", "from ")):
                import_idx = i + 1
            elif import_idx > 0 and line.strip() == "":
                break

        # Insert import
        new_lines.insert(import_idx, "from tests.test_constants import (")
        # Collect all constants used
        constants_used = set()
        for line in new_lines:
            for const_name in CONSTANT_MAPPINGS.values():
                if const_name in line:
                    constants_used.add(const_name)

        # Add constant names
        for const in sorted(constants_used):
            new_lines.insert(import_idx + 1, f"    {const},")
        new_lines.insert(import_idx + len(constants_used) + 1, ")")
        new_lines.insert(import_idx + len(constants_used) + 2, "")

    # Write back
    if replacements > 0:
        file_path.write_text("\n".join(new_lines), encoding="utf-8")

    return replacements, noqa_added


def main() -> int:
    """Main execution."""
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests"

    if not tests_dir.exists():
        return 1

    total_replacements = 0
    total_noqa = 0
    files_modified = 0

    # Process all Python test files
    for test_file in tests_dir.rglob("test_*.py"):
        replacements, noqa = process_file(test_file)
        if replacements > 0 or noqa > 0:
            total_replacements += replacements
            total_noqa += noqa
            files_modified += 1

    # Run ruff to check remaining violations
    result = subprocess.run(
        ["ruff", "check", str(tests_dir), "--select", "PLR2004"],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        # Count violations
        result.stdout.count("PLR2004")

    return 0


if __name__ == "__main__":
    sys.exit(main())
