#!/usr/bin/env python3
"""Script to systematically fix test_api_comprehensive.py.

Applies all AsyncMock and fixture corrections.
"""

import pathlib
import re


def fix_test_file() -> None:
    """Apply all fixes to the test file."""
    file_path = "tests/unit/api/test_api_comprehensive.py"

    content = pathlib.Path(file_path).read_text(encoding="utf-8")

    # Fix 1: Update create_query_chain signature
    content = re.sub(
        r"def create_query_chain\(\):",
        "def create_query_chain(*args, **kwargs):",
        content,
    )

    # Fix 2: Fix all _retry_request patches with MagicMock to AsyncMock
    # Pattern: patch.object(api_client, "_retry_request", MagicMock(
    content = re.sub(
        r'patch\.object\(api_client, "_retry_request", MagicMock\(',
        'patch.object(api_client, "_retry_request", AsyncMock(',
        content,
    )

    # Fix 3: Fix standalone MagicMock patches that should be AsyncMock
    # Look for: with patch.object(api_client, "_retry_request", MagicMock(return_value=
    # But AsyncMock(return_value= is already correct, so we're selective

    # Fix 4: Fix lines with patch.object and side_effect that need AsyncMock
    content = re.sub(
        r'patch\.object\(\s*api_client,\s*"_retry_request",\s*MagicMock\(side_effect=',
        'patch.object(api_client, "_retry_request", AsyncMock(side_effect=',
        content,
    )

    # Write back
    pathlib.Path(file_path).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    fix_test_file()
