#!/usr/bin/env python3
"""Pre-commit hook to validate Python module metadata.

Checks that all Python modules have required inline metadata in docstrings.

State: STABLE
Since: 0.3.0
"""

import re
import sys
from pathlib import Path


REQUIRED_FIELDS = ["State", "Since", "Tests", "Docs"]
OPTIONAL_FIELDS = [
    "Specs", "Stories", "Version_Changed", "Specified_By", "Implements",
    "Verified_By", "Coverage", "Explained_By", "Demonstrated_By",
    "Decided_By", "ADR", "Depends_On", "Imports", "Exports", "Extends",
    "Inherits_From", "Composed_Of", "Implements_Interface", "Supersedes",
    "Conflicts_With", "Migrates_From", "Prerequisite_Of", "Alternative_To",
    "Raises", "Handles", "Emits", "Listens_To", "Requested_By",
    "Approved_By", "Roadmap", "Tags", "Keywords", "Performance",
    "Benchmarks", "Security", "Vulnerability_ID", "PyPI", "GitHub",
    "StackOverflow"
]

VALID_STATES = [
    "DRAFT", "PROPOSED", "IN_REVIEW", "APPROVED", "IN_PROGRESS",
    "IMPLEMENTED", "RELEASED", "STABLE", "DEPRECATED", "LEGACY",
    "SUNSET", "REMOVED", "ARCHIVED", "EXPERIMENTAL", "ALPHA",
    "BETA", "RC", "BROKEN", "NEEDS_UPDATE", "PLANNED", "BACKLOG",
    "DEFERRED", "REJECTED", "SUPERSEDED", "MERGED"
]


def extract_docstring(file_path: Path) -> str | None:
    """Extract module docstring from Python file."""
    try:
        with open(file_path) as f:
            content = f.read()

        # Match module docstring
        match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)

        # Try single quotes
        match = re.search(r"^'''(.*?)'''", content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)

        return None
    except Exception:
        return None


def validate_metadata(docstring: str, file_path: Path) -> list[str]:
    """Validate metadata in docstring."""
    errors = []

    # Check for required fields
    for field in REQUIRED_FIELDS:
        pattern = rf"^{field}:\s*(.+)$"
        if not re.search(pattern, docstring, re.MULTILINE):
            errors.append(f"Missing required field: {field}")

    # Validate State field
    state_match = re.search(r"^State:\s*(\w+)", docstring, re.MULTILINE)
    if state_match:
        state = state_match.group(1)
        if state not in VALID_STATES:
            errors.append(f"Invalid state: {state} (must be one of {', '.join(VALID_STATES)})")

    # Validate Since field (version format)
    since_match = re.search(r"^Since:\s*([\d.]+)", docstring, re.MULTILINE)
    if since_match:
        since = since_match.group(1)
        if not re.match(r"^\d+\.\d+\.\d+$", since):
            errors.append(f"Invalid version format for Since: {since} (expected X.Y.Z)")

    return errors


def main():
    """Run validation on provided files."""
    exit_code = 0

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)

        # Skip __init__.py files without code
        if file_path.name == "__init__.py":
            try:
                with open(file_path) as f:
                    content = f.read()
                # Skip if only has docstring and imports
                if len([l for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]) < 10:
                    continue
            except:
                pass

        docstring = extract_docstring(file_path)
        if not docstring:
            print(f"❌ {file_path}: No module docstring found")
            exit_code = 1
            continue

        errors = validate_metadata(docstring, file_path)
        if errors:
            print(f"❌ {file_path}:")
            for error in errors:
                print(f"   - {error}")
            exit_code = 1
        else:
            print(f"✅ {file_path}: Metadata valid")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
