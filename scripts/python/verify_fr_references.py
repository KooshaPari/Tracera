#!/usr/bin/env python3
"""Pre-commit validation script for FR/ADR/Epic references in docstrings.

This script:
1. Extracts FR/ADR/Epic IDs from docstrings in changed files
2. Verifies IDs exist in master docs (FUNCTIONAL_REQUIREMENTS.md, PRD.md, adr/*.md)
3. Returns exit code 1 if invalid ID found
4. Warns if missing FR reference in new service/API
5. Can be used as pre-commit hook

Usage:
    # Validate specific files
    python scripts/python/verify_fr_references.py file1.py file2.py

    # Validate all changed files in git
    python scripts/python/verify_fr_references.py --git-staged

    # Validate all service/API files
    python scripts/python/verify_fr_references.py --all

Exit Codes:
    0: All references valid
    1: Invalid references found
    2: Configuration error
"""

from __future__ import annotations

import argparse
import ast
import logging
import re
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ReferenceValidator:
    """Validate FR/ADR/Epic references in docstrings."""

    def __init__(self, root: Path) -> None:
        """Initialize validator."""
        self.root = root
        self.valid_frs: set[str] = set()
        self.valid_epics: set[str] = set()
        self.valid_user_stories: set[str] = set()
        self.valid_adrs: set[str] = set()
        self.errors: list[str] = []
        self.warnings: list[str] = []

        # Load valid IDs
        self._load_valid_ids()

    def _load_valid_ids(self) -> None:
        """Load valid FR/ADR/Epic IDs from master docs."""
        # Load FRs from FUNCTIONAL_REQUIREMENTS.md (primary location in docs/)
        fr_file = self.root / "docs/FUNCTIONAL_REQUIREMENTS.md"
        if not fr_file.exists():
            # Fallback to docs/reference/ if not found in docs/
            fr_file = self.root / "docs/reference/FUNCTIONAL_REQUIREMENTS.md"

        if fr_file.exists():
            content = fr_file.read_text()
            self.valid_frs = set(re.findall(r"FR-[A-Z]+-\d+", content))
            self.valid_user_stories = set(re.findall(r"US-[A-Z]+-\d+", content))
            logger.info(f"Loaded {len(self.valid_frs)} valid FRs")
            logger.info(f"Loaded {len(self.valid_user_stories)} valid User Stories")
        else:
            logger.warning(f"FR file not found: {fr_file}")

        # Load Epics from PRD.md (primary location in docs/)
        prd_file = self.root / "docs/PRD.md"
        if not prd_file.exists():
            # Fallback to docs/reference/ if not found in docs/
            prd_file = self.root / "docs/reference/PRD.md"

        if prd_file.exists():
            content = prd_file.read_text()
            # Match E1, E1.1, E1.1.2 format (Epic IDs must start with digit)
            self.valid_epics = set(re.findall(r"E\d+(?:\.\d+)*", content))
            logger.info(f"Loaded {len(self.valid_epics)} valid Epics")
        else:
            logger.warning(f"PRD file not found: {prd_file}")

        # Load ADRs from docs/adr/*.md
        adr_dir = self.root / "docs/adr"
        if adr_dir.exists():
            for adr_file in adr_dir.glob("ADR-*.md"):
                adr_match = re.match(r"ADR-(\d+)", adr_file.stem)
                if adr_match:
                    self.valid_adrs.add(f"ADR-{adr_match.group(1)}")
            logger.info(f"Loaded {len(self.valid_adrs)} valid ADRs")
        else:
            logger.warning(f"ADR directory not found: {adr_dir}")

    def validate_file(self, file_path: Path) -> bool:
        """Validate FR references in file.

        Returns:
            True if all references valid, False otherwise
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        # Skip non-code files
        if file_path.suffix not in {".py", ".go", ".ts", ".tsx"}:
            logger.debug(f"Skipping non-code file: {file_path}")
            return True

        # Only validate Python files for now (Go/TS support can be added later)
        if file_path.suffix != ".py":
            logger.debug(f"Skipping non-Python file (not yet supported): {file_path}")
            return True

        logger.info(f"Validating {file_path}")

        # Parse AST
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.exception(f"Syntax error in {file_path}: {e}")
            return False

        # Extract references from docstrings
        references = self._extract_references(tree)

        # Validate references
        return self._validate_references(references, file_path)

    def _extract_references(
        self,
        tree: ast.AST,
    ) -> dict[str, list[str]]:
        """Extract FR/ADR/Epic references from docstrings."""
        references: dict[str, list[str]] = {
            "frs": [],
            "epics": [],
            "user_stories": [],
            "adrs": [],
        }

        for node in ast.walk(tree):
            if not isinstance(
                node,
                ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Module,
            ):
                continue

            docstring = ast.get_docstring(node)
            if not docstring:
                continue

            # Extract FR IDs
            frs = re.findall(r"FR-[A-Z]+-\d+", docstring)
            references["frs"].extend(frs)

            # Extract Epic IDs (must start with E followed by digit, then optional .digit pairs)
            epics = re.findall(r"E\d+(?:\.\d+)*", docstring)
            references["epics"].extend(epics)

            # Extract User Story IDs
            user_stories = re.findall(r"US-[A-Z]+-\d+", docstring)
            references["user_stories"].extend(user_stories)

            # Extract ADR IDs
            adrs = re.findall(r"ADR-\d+", docstring)
            references["adrs"].extend(adrs)

        # Deduplicate
        for key, value in references.items():
            references[key] = sorted(set(value))

        return references

    def _validate_references(
        self,
        references: dict[str, list[str]],
        file_path: Path,
    ) -> bool:
        """Validate extracted references."""
        valid = True

        # Check FRs
        for fr in references["frs"]:
            if fr not in self.valid_frs:
                self.errors.append(f"{file_path}: Invalid FR reference: {fr}")
                valid = False

        # Check Epics
        for epic in references["epics"]:
            if epic not in self.valid_epics:
                self.errors.append(f"{file_path}: Invalid Epic reference: {epic}")
                valid = False

        # Check User Stories
        for us in references["user_stories"]:
            if us not in self.valid_user_stories:
                self.errors.append(f"{file_path}: Invalid User Story reference: {us}")
                valid = False

        # Check ADRs
        for adr in references["adrs"]:
            if adr not in self.valid_adrs:
                self.errors.append(f"{file_path}: Invalid ADR reference: {adr}")
                valid = False

        # Warn if service/API file has no FR references
        if self._is_service_or_api_file(file_path):
            if not references["frs"]:
                self.warnings.append(
                    f"{file_path}: Service/API file has no FR references",
                )

        return valid

    def _is_service_or_api_file(self, file_path: Path) -> bool:
        """Check if file is a service or API file."""
        path_str = str(file_path)
        return "services/" in path_str or "api/routers/" in path_str

    def report_results(self) -> None:
        """Report validation results."""
        if self.errors:
            logger.error("\n=== ERRORS ===")
            for error in self.errors:
                logger.error(error)

        if self.warnings:
            logger.warning("\n=== WARNINGS ===")
            for warning in self.warnings:
                logger.warning(warning)

        if not self.errors and not self.warnings:
            logger.info("✓ All FR/ADR/Epic references are valid")

    def has_errors(self) -> bool:
        """Check if any errors found."""
        return len(self.errors) > 0


def get_staged_files() -> list[Path]:
    """Get list of staged Python files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = result.stdout.strip().split("\n")
        # Filter Python files
        return [Path(f) for f in files if f.endswith(".py")]
    except subprocess.CalledProcessError as e:
        logger.exception(f"Failed to get staged files: {e}")
        return []


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Files to validate (default: none)",
    )
    parser.add_argument(
        "--git-staged",
        action="store_true",
        help="Validate all staged Python files",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all service/API files",
    )
    args = parser.parse_args()

    # Locate project root
    root = Path.cwd()
    if not (root / "pyproject.toml").exists():
        logger.error("Not in project root (pyproject.toml not found)")
        return 2

    # Initialize validator
    validator = ReferenceValidator(root)

    # Determine files to validate
    files: list[Path] = []

    if args.git_staged:
        files = get_staged_files()
        if not files:
            logger.info("No staged Python files to validate")
            return 0
    elif args.all:
        services_dir = root / "src/tracertm/services"
        routers_dir = root / "src/tracertm/api/routers"
        files.extend(services_dir.glob("**/*.py"))
        files.extend(routers_dir.glob("**/*.py"))
    elif args.files:
        files = args.files
    else:
        parser.print_help()
        return 2

    # Validate files
    for file_path in files:
        validator.validate_file(file_path)

    # Report results
    validator.report_results()

    return 0 if not validator.has_errors() else 1


if __name__ == "__main__":
    sys.exit(main())
