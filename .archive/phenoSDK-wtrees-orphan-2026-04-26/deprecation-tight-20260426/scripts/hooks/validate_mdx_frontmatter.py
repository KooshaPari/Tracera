#!/usr/bin/env python3
"""Pre-commit hook to validate MDX frontmatter.

Checks that MDX files have valid YAML frontmatter with required fields.

State: STABLE
Since: 0.3.0
"""

import re
import sys
from pathlib import Path
import yaml


REQUIRED_FIELDS = ["title"]
RECOMMENDED_FIELDS = ["description", "state", "tags"]


def extract_frontmatter(file_path: Path) -> dict | None:
    """Extract YAML frontmatter from MDX file."""
    try:
        with open(file_path) as f:
            content = f.read()

        if not content.startswith("---"):
            return None

        # Find end of frontmatter
        end_idx = content.find("\n---\n", 3)
        if end_idx == -1:
            end_idx = content.find("\n---", 3)
            if end_idx == -1:
                return None

        # Parse YAML
        frontmatter_text = content[3:end_idx]
        return yaml.safe_load(frontmatter_text)
    except Exception as e:
        return None


def validate_frontmatter(frontmatter: dict | None, file_path: Path) -> list[str]:
    """Validate frontmatter fields."""
    errors = []

    if frontmatter is None:
        errors.append("Missing YAML frontmatter (should start with ---)")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Check recommended fields
    missing_recommended = [f for f in RECOMMENDED_FIELDS if f not in frontmatter]
    if missing_recommended:
        errors.append(f"Missing recommended fields: {', '.join(missing_recommended)}")

    # Validate state if present
    if "state" in frontmatter:
        valid_states = [
            "STABLE", "IN_PROGRESS", "EXPERIMENTAL", "DEPRECATED",
            "ARCHIVED", "PLANNED", "DRAFT"
        ]
        if frontmatter["state"] not in valid_states:
            errors.append(
                f"Invalid state: {frontmatter['state']} "
                f"(must be one of {', '.join(valid_states)})"
            )

    # Validate tags if present
    if "tags" in frontmatter:
        if not isinstance(frontmatter["tags"], list):
            errors.append("tags field must be a list")

    return errors


def main():
    """Run validation on provided files."""
    exit_code = 0

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)

        frontmatter = extract_frontmatter(file_path)
        errors = validate_frontmatter(frontmatter, file_path)

        if errors:
            print(f"❌ {file_path}:")
            for error in errors:
                print(f"   - {error}")
            exit_code = 1
        else:
            print(f"✅ {file_path}: Frontmatter valid")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
