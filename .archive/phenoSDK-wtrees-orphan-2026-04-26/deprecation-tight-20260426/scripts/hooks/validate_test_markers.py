#!/usr/bin/env python3
"""Pre-commit hook to validate pytest markers in test files.

Checks that test functions have appropriate markers for specs, stories, and features.

State: STABLE
Since: 0.3.0
"""

import re
import sys
from pathlib import Path


REQUIRED_MARKERS = ["feature"]  # All tests must have feature marker
RECOMMENDED_MARKERS = ["spec", "story"]  # At least one recommended


def extract_test_functions(file_path: Path) -> list[dict]:
    """Extract test functions and their markers."""
    try:
        with open(file_path) as f:
            content = f.read()

        test_functions = []
        pattern = r'((?:@pytest\.mark\.\w+.*\n)*)(    def (test_\w+))'

        for match in re.finditer(pattern, content):
            markers_text = match.group(1)
            func_name = match.group(3)

            # Extract marker types
            markers = {}
            for marker_match in re.finditer(r'@pytest\.mark\.(\w+)', markers_text):
                marker_type = marker_match.group(1)
                markers[marker_type] = True

            test_functions.append({
                "name": func_name,
                "markers": markers,
                "has_markers": len(markers) > 0
            })

        return test_functions
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def validate_test_markers(test_functions: list[dict], file_path: Path) -> list[str]:
    """Validate test markers."""
    errors = []

    if not test_functions:
        return errors

    for test in test_functions:
        # Check required markers
        for required in REQUIRED_MARKERS:
            if required not in test["markers"]:
                errors.append(f"{test['name']}: Missing required marker @pytest.mark.{required}")

        # Check recommended markers
        has_recommended = any(marker in test["markers"] for marker in RECOMMENDED_MARKERS)
        if not has_recommended:
            errors.append(
                f"{test['name']}: Missing recommended marker "
                f"(should have @pytest.mark.spec or @pytest.mark.story)"
            )

    return errors


def main():
    """Run validation on provided files."""
    exit_code = 0

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)

        test_functions = extract_test_functions(file_path)
        if not test_functions:
            # No test functions found, skip
            continue

        errors = validate_test_markers(test_functions, file_path)
        if errors:
            print(f"❌ {file_path}:")
            for error in errors:
                print(f"   - {error}")
            exit_code = 1
        else:
            print(f"✅ {file_path}: {len(test_functions)} tests with valid markers")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
