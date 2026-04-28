#!/usr/bin/env python3
"""
OpenSpec Format Validator

Validates OpenSpec spec.md files for correct structure, format, and content.
Checks YAML frontmatter, required sections, requirement format, scenario format,
and internal references.

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: Script error (file not found, etc.)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import yaml


class ValidationError:
    """Represents a validation error with location and details."""

    def __init__(self, file_path: Path, line_num: Optional[int], message: str, severity: str = "error"):
        self.file_path = file_path
        self.line_num = line_num
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        location = f"{self.file_path}"
        if self.line_num:
            location += f":{self.line_num}"
        return f"{self.severity.upper()}: {location} - {self.message}"


class OpenSpecValidator:
    """Validates OpenSpec specification files."""

    # Required frontmatter fields for capability specs
    REQUIRED_FRONTMATTER_CAPABILITY = ["capability_id", "version", "status"]

    # Required frontmatter fields for change delta specs
    REQUIRED_FRONTMATTER_DELTA = []  # Delta specs may have different requirements

    # Required sections for capability specs
    REQUIRED_SECTIONS_CAPABILITY = ["Overview", "Requirements", "API Surface"]

    # Required sections for delta specs
    REQUIRED_SECTIONS_DELTA = []  # Delta specs use ADDED/MODIFIED/REMOVED structure

    # Valid requirement ID pattern
    REQUIREMENT_ID_PATTERN = re.compile(r"^[A-Z]+-\d+$")

    def __init__(self, strict: bool = True):
        self.strict = strict
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single spec.md file."""
        if not file_path.exists():
            self.errors.append(
                ValidationError(file_path, None, f"File not found: {file_path}", "error")
            )
            return False

        content = file_path.read_text()
        lines = content.split("\n")

        # Determine if this is a capability spec or delta spec
        is_delta = "/changes/" in str(file_path)

        # Validate frontmatter (if present)
        has_frontmatter = self._validate_frontmatter(file_path, content, is_delta)

        # Validate required sections
        self._validate_sections(file_path, content, is_delta)

        # Validate requirements format
        self._validate_requirements(file_path, lines, is_delta)

        # Validate scenarios
        self._validate_scenarios(file_path, lines)

        # Validate internal references
        self._validate_references(file_path, content)

        return len(self.errors) == 0

    def _validate_frontmatter(self, file_path: Path, content: str, is_delta: bool) -> bool:
        """Validate YAML frontmatter if present."""
        # Check if file starts with frontmatter delimiter
        if not content.startswith("---"):
            # Frontmatter is optional, so this is just a warning
            self.warnings.append(
                ValidationError(
                    file_path, 1, "No YAML frontmatter found (optional but recommended)", "warning"
                )
            )
            return False

        # Extract frontmatter
        try:
            end_idx = content.index("---", 3)
            frontmatter_text = content[3:end_idx].strip()
            frontmatter = yaml.safe_load(frontmatter_text)
        except ValueError:
            self.errors.append(
                ValidationError(file_path, 1, "Frontmatter closing delimiter '---' not found", "error")
            )
            return False
        except yaml.YAMLError as e:
            self.errors.append(
                ValidationError(file_path, 1, f"Invalid YAML in frontmatter: {e}", "error")
            )
            return False

        # Validate required fields
        required_fields = (
            self.REQUIRED_FRONTMATTER_DELTA if is_delta else self.REQUIRED_FRONTMATTER_CAPABILITY
        )

        if frontmatter:
            for field in required_fields:
                if field not in frontmatter:
                    self.errors.append(
                        ValidationError(
                            file_path, 1, f"Missing required frontmatter field: {field}", "error"
                        )
                    )

        return True

    def _validate_sections(self, file_path: Path, content: str, is_delta: bool) -> None:
        """Validate required sections are present."""
        required_sections = (
            self.REQUIRED_SECTIONS_DELTA if is_delta else self.REQUIRED_SECTIONS_CAPABILITY
        )

        for section in required_sections:
            # Look for section headers (## or #)
            pattern = rf"^##?\s+{re.escape(section)}\s*$"
            if not re.search(pattern, content, re.MULTILINE):
                self.errors.append(
                    ValidationError(file_path, None, f"Missing required section: {section}", "error")
                )

        # For delta specs, check for at least one delta section
        if is_delta:
            has_delta = any(
                re.search(rf"^##\s+{delta}\s+Requirements\s*$", content, re.MULTILINE)
                for delta in ["ADDED", "MODIFIED", "REMOVED", "RENAMED"]
            )
            if not has_delta:
                self.errors.append(
                    ValidationError(
                        file_path,
                        None,
                        "Delta spec must have at least one of: ADDED, MODIFIED, REMOVED, RENAMED Requirements",
                        "error",
                    )
                )

    def _validate_requirements(self, file_path: Path, lines: List[str], is_delta: bool) -> None:
        """Validate requirement format."""
        requirement_pattern = re.compile(r"^###\s+Requirement:\s+(.+?)\s+\(([A-Z]+-\d+)\)\s*$")

        for line_num, line in enumerate(lines, start=1):
            if line.startswith("### Requirement:"):
                match = requirement_pattern.match(line)
                if not match:
                    self.errors.append(
                        ValidationError(
                            file_path,
                            line_num,
                            "Invalid requirement format. Expected: '### Requirement: <description> (<ID>)'",
                            "error",
                        )
                    )
                else:
                    req_id = match.group(2)
                    if not self.REQUIREMENT_ID_PATTERN.match(req_id):
                        self.errors.append(
                            ValidationError(
                                file_path,
                                line_num,
                                f"Invalid requirement ID format: {req_id}. Expected: PREFIX-NUMBER (e.g., AUTH-001)",
                                "error",
                            )
                        )

    def _validate_scenarios(self, file_path: Path, lines: List[str]) -> None:
        """Validate scenario format (Given/When/Then or WHEN/THEN/AND)."""
        scenario_pattern = re.compile(r"^####\s+Scenario:\s+(.+)$")
        scenario_locations: List[int] = []

        # Find all scenarios
        for line_num, line in enumerate(lines, start=1):
            if scenario_pattern.match(line):
                scenario_locations.append(line_num)

        # Check each scenario has proper structure
        for scenario_line in scenario_locations:
            # Look ahead for WHEN/THEN or Given/When/Then
            scenario_block = lines[scenario_line : min(scenario_line + 15, len(lines))]
            scenario_text = "\n".join(scenario_block)

            has_when = re.search(r"^\s*-?\s*\*?\*?WHEN\*?\*?", scenario_text, re.MULTILINE | re.IGNORECASE)
            has_then = re.search(r"^\s*-?\s*\*?\*?THEN\*?\*?", scenario_text, re.MULTILINE | re.IGNORECASE)
            has_given = re.search(r"^\s*-?\s*\*?\*?GIVEN\*?\*?", scenario_text, re.MULTILINE | re.IGNORECASE)

            if not has_when or not has_then:
                self.errors.append(
                    ValidationError(
                        file_path,
                        scenario_line,
                        "Scenario must include at least WHEN and THEN clauses",
                        "error",
                    )
                )

    def _validate_references(self, file_path: Path, content: str) -> None:
        """Validate internal references to other requirements or specs."""
        # Find all requirement IDs defined in this file
        defined_ids: Set[str] = set()
        for match in re.finditer(r"### Requirement:.*?\(([A-Z]+-\d+)\)", content):
            defined_ids.add(match.group(1))

        # Find all references to requirement IDs
        reference_pattern = re.compile(r"\b([A-Z]+-\d+)\b")
        for match in reference_pattern.finditer(content):
            ref_id = match.group(1)
            # Skip if this is the definition itself
            if ref_id not in defined_ids:
                # This is a reference to external requirement - just warn
                self.warnings.append(
                    ValidationError(
                        file_path,
                        None,
                        f"Reference to external requirement: {ref_id} (ensure it exists elsewhere)",
                        "warning",
                    )
                )

    def print_results(self) -> None:
        """Print validation results."""
        if self.warnings:
            print("\n=== WARNINGS ===")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print("\n=== ERRORS ===")
            for error in self.errors:
                print(f"  {error}")
            print(f"\nTotal errors: {len(self.errors)}")
        else:
            print("\n✓ All validations passed!")

        if self.warnings:
            print(f"Total warnings: {len(self.warnings)}")


def validate_openspec_directory(openspec_dir: Path, strict: bool = True) -> int:
    """
    Validate all spec.md files in the openspec directory.

    Args:
        openspec_dir: Root openspec directory
        strict: If True, warnings are treated as errors

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    validator = OpenSpecValidator(strict=strict)
    spec_files = list(openspec_dir.rglob("spec.md"))

    if not spec_files:
        print(f"No spec.md files found in {openspec_dir}")
        return 2

    print(f"Validating {len(spec_files)} spec files...\n")

    for spec_file in spec_files:
        print(f"Validating: {spec_file.relative_to(openspec_dir)}")
        validator.validate_file(spec_file)

    validator.print_results()

    # Determine exit code
    has_errors = len(validator.errors) > 0
    has_warnings = len(validator.warnings) > 0

    if has_errors:
        return 1
    elif strict and has_warnings:
        print("\nStrict mode: Treating warnings as errors")
        return 1
    else:
        return 0


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate OpenSpec specification files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all specs in default location
  python scripts/validate_openspec.py

  # Validate with strict mode (warnings as errors)
  python scripts/validate_openspec.py --strict

  # Validate custom directory
  python scripts/validate_openspec.py --dir /path/to/openspec
        """,
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("openspec"),
        help="OpenSpec directory to validate (default: openspec/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )

    args = parser.parse_args()

    if not args.dir.exists():
        print(f"Error: Directory not found: {args.dir}")
        return 2

    return validate_openspec_directory(args.dir, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
