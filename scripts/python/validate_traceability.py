#!/usr/bin/env python3
"""Validate traceability integrity across documentation.

This script verifies:
- All FR IDs in code exist in FUNCTIONAL_REQUIREMENTS.md
- All Epic IDs in FRs exist in PRD.md
- All ADR IDs referenced exist in docs/adr/
- No orphaned FRs (missing Epic trace)
- No orphaned code (missing FR reference)

Exit codes:
    0: All validations passed
    1: Validation failures detected

Usage:
    python scripts/python/validate_traceability.py [options]
    python scripts/python/validate_traceability.py --help
    python scripts/python/validate_traceability.py --verbose
    python scripts/python/validate_traceability.py --check-code
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Pattern matchers
FR_ID_PATTERN = re.compile(r'(FR-[A-Z]+-\d{3})')
EPIC_ID_PATTERN = re.compile(r'(EPIC-\d{3})')
ADR_ID_PATTERN = re.compile(r'(ADR-\d{4})')


@dataclass
class ValidationResult:
    """Validation result container."""
    passed: bool
    category: str
    message: str
    details: list[str] = field(default_factory=list)


class TraceabilityValidator:
    """Validate traceability integrity."""

    def __init__(self, project_root: Path, verbose: bool = False, check_code: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.check_code = check_code

        # Paths
        self.fr_status_path = project_root / "docs" / "FUNCTIONAL_REQUIREMENTS_STATUS.json"
        self.adr_status_path = project_root / "docs" / "ADR_STATUS.json"
        self.fr_doc_path = project_root / "docs" / "reference" / "FUNCTIONAL_REQUIREMENTS.md"
        self.prd_path = project_root / "docs" / "reference" / "PRD.md"
        self.adr_dir = project_root / "docs" / "adr"

        # Validation results
        self.results: list[ValidationResult] = []
        self.errors = 0
        self.warnings = 0

    def log(self, msg: str, level: str = "INFO") -> None:
        """Log message if verbose enabled."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = {
                "INFO": "ℹ️",
                "ERROR": "❌",
                "WARNING": "⚠️",
                "SUCCESS": "✅"
            }.get(level, "")
            print(f"{prefix} {msg}")

    def load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON file."""
        with path.open("r") as f:
            return json.load(f)

    def load_text(self, path: Path) -> str:
        """Load text file."""
        return path.read_text(encoding="utf-8")

    def extract_ids_from_text(self, text: str, pattern: re.Pattern) -> set[str]:
        """Extract IDs from text using pattern."""
        return set(pattern.findall(text))

    def add_result(self, passed: bool, category: str, message: str, details: list[str] | None = None) -> None:
        """Add validation result."""
        result = ValidationResult(
            passed=passed,
            category=category,
            message=message,
            details=details or []
        )
        self.results.append(result)

        if not passed:
            self.errors += 1
            self.log(f"FAILED: {message}", "ERROR")
            if details:
                for detail in details[:5]:  # Show first 5
                    self.log(f"  - {detail}", "ERROR")
                if len(details) > 5:
                    self.log(f"  ... and {len(details) - 5} more", "ERROR")
        else:
            self.log(f"PASSED: {message}", "SUCCESS")

    def validate_fr_ids_exist(self) -> None:
        """Validate all FR IDs in code exist in FUNCTIONAL_REQUIREMENTS.md."""
        self.log("Validating FR IDs exist in documentation...")

        # Load FR status
        fr_status = self.load_json(self.fr_status_path)
        valid_fr_ids = set(fr_status["functional_requirements"].keys())

        # Load FR doc
        fr_doc = self.load_text(self.fr_doc_path)
        documented_fr_ids = self.extract_ids_from_text(fr_doc, FR_ID_PATTERN)

        # Check all status FRs are documented
        missing_in_doc = valid_fr_ids - documented_fr_ids

        if missing_in_doc:
            self.add_result(
                False,
                "FR Documentation",
                f"{len(missing_in_doc)} FRs in status file but not documented",
                sorted(missing_in_doc)
            )
        else:
            self.add_result(
                True,
                "FR Documentation",
                f"All {len(valid_fr_ids)} FRs documented in FUNCTIONAL_REQUIREMENTS.md"
            )

        # If check_code enabled, scan code for FR references
        if self.check_code:
            self._validate_code_fr_references(valid_fr_ids)

    def _validate_code_fr_references(self, valid_fr_ids: set[str]) -> None:
        """Validate FR references in code are valid."""
        self.log("Validating FR references in code...")

        invalid_refs: list[str] = []

        # Scan Python files
        for py_file in self.project_root.glob("src/**/*.py"):
            content = self._safe_read(py_file)
            if content:
                fr_ids = self.extract_ids_from_text(content, FR_ID_PATTERN)
                for fr_id in fr_ids:
                    if fr_id not in valid_fr_ids:
                        rel_path = py_file.relative_to(self.project_root)
                        invalid_refs.append(f"{rel_path}: {fr_id}")

        # Scan Go files
        for go_file in self.project_root.glob("backend/**/*.go"):
            content = self._safe_read(go_file)
            if content:
                fr_ids = self.extract_ids_from_text(content, FR_ID_PATTERN)
                for fr_id in fr_ids:
                    if fr_id not in valid_fr_ids:
                        rel_path = go_file.relative_to(self.project_root)
                        invalid_refs.append(f"{rel_path}: {fr_id}")

        # Scan TypeScript files
        for ts_file in self.project_root.glob("frontend/**/*.{ts,tsx}"):
            content = self._safe_read(ts_file)
            if content:
                fr_ids = self.extract_ids_from_text(content, FR_ID_PATTERN)
                for fr_id in fr_ids:
                    if fr_id not in valid_fr_ids:
                        rel_path = ts_file.relative_to(self.project_root)
                        invalid_refs.append(f"{rel_path}: {fr_id}")

        if invalid_refs:
            self.add_result(
                False,
                "Code FR References",
                f"{len(invalid_refs)} invalid FR references in code",
                invalid_refs
            )
        else:
            self.add_result(
                True,
                "Code FR References",
                "All FR references in code are valid"
            )

    def _safe_read(self, path: Path) -> str | None:
        """Safely read file, return None on error."""
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return None

    def validate_epic_ids_exist(self) -> None:
        """Validate all Epic IDs in FRs exist in PRD.md."""
        self.log("Validating Epic IDs exist in PRD...")

        # Load FR status
        fr_status = self.load_json(self.fr_status_path)

        # Extract Epic IDs from FRs
        epic_ids_in_frs: set[str] = set()
        for fr in fr_status["functional_requirements"].values():
            if "epic" in fr and fr["epic"]:
                epic_ids_in_frs.add(fr["epic"])

        # Load PRD
        if not self.prd_path.exists():
            self.add_result(
                False,
                "Epic Validation",
                "PRD.md not found",
                [str(self.prd_path)]
            )
            return

        prd_content = self.load_text(self.prd_path)
        documented_epics = self.extract_ids_from_text(prd_content, EPIC_ID_PATTERN)

        # Check all Epic IDs exist
        missing_epics = epic_ids_in_frs - documented_epics

        if missing_epics:
            self.add_result(
                False,
                "Epic Validation",
                f"{len(missing_epics)} Epic IDs referenced but not in PRD",
                sorted(missing_epics)
            )
        else:
            self.add_result(
                True,
                "Epic Validation",
                f"All {len(epic_ids_in_frs)} Epic IDs documented in PRD"
            )

    def validate_adr_ids_exist(self) -> None:
        """Validate all ADR IDs referenced exist in docs/adr/."""
        self.log("Validating ADR IDs exist...")

        # Load ADR status
        adr_status = self.load_json(self.adr_status_path)
        valid_adr_ids = set(adr_status["architecture_decisions"].keys())

        # Check ADR files exist
        missing_adr_files: list[str] = []

        for adr_id in sorted(valid_adr_ids):
            # Expected file: docs/adr/ADR-0001-title.md
            adr_files = list(self.adr_dir.glob(f"{adr_id}-*.md"))

            if not adr_files:
                missing_adr_files.append(adr_id)

        if missing_adr_files:
            self.add_result(
                False,
                "ADR Files",
                f"{len(missing_adr_files)} ADR files missing",
                missing_adr_files
            )
        else:
            self.add_result(
                True,
                "ADR Files",
                f"All {len(valid_adr_ids)} ADR files exist in docs/adr/"
            )

        # Scan code for ADR references
        if self.check_code:
            self._validate_code_adr_references(valid_adr_ids)

    def _validate_code_adr_references(self, valid_adr_ids: set[str]) -> None:
        """Validate ADR references in code are valid."""
        self.log("Validating ADR references in code...")

        invalid_refs: list[str] = []

        # Scan all markdown files in docs/
        for md_file in self.project_root.glob("docs/**/*.md"):
            content = self._safe_read(md_file)
            if content:
                adr_ids = self.extract_ids_from_text(content, ADR_ID_PATTERN)
                for adr_id in adr_ids:
                    if adr_id not in valid_adr_ids:
                        rel_path = md_file.relative_to(self.project_root)
                        invalid_refs.append(f"{rel_path}: {adr_id}")

        if invalid_refs:
            self.add_result(
                False,
                "Code ADR References",
                f"{len(invalid_refs)} invalid ADR references in docs",
                invalid_refs
            )
        else:
            self.add_result(
                True,
                "Code ADR References",
                "All ADR references in docs are valid"
            )

    def check_orphaned_frs(self) -> None:
        """Check for orphaned FRs (no Epic trace)."""
        self.log("Checking for orphaned FRs...")

        # Load FR status
        fr_status = self.load_json(self.fr_status_path)

        orphaned_frs: list[str] = []

        for fr_id, fr in fr_status["functional_requirements"].items():
            epic = fr.get("epic", "")
            if not epic or epic.strip() == "":
                orphaned_frs.append(fr_id)

        if orphaned_frs:
            # This is a warning, not an error
            self.warnings += 1
            self.add_result(
                False,
                "Orphaned FRs",
                f"{len(orphaned_frs)} FRs have no Epic trace",
                orphaned_frs
            )
        else:
            self.add_result(
                True,
                "Orphaned FRs",
                "All FRs have Epic trace"
            )

    def check_orphaned_code(self) -> None:
        """Check for orphaned code (no FR reference).

        Note: This is a heuristic check - not all code needs FR references.
        Only checks service files and API routers.
        """
        if not self.check_code:
            return

        self.log("Checking for orphaned code (services/routers without FR references)...")

        orphaned_files: list[str] = []

        # Check Python service files
        for service_file in self.project_root.glob("src/tracertm/services/*_service.py"):
            content = self._safe_read(service_file)
            if content:
                fr_ids = self.extract_ids_from_text(content, FR_ID_PATTERN)
                if not fr_ids:
                    rel_path = service_file.relative_to(self.project_root)
                    orphaned_files.append(str(rel_path))

        # Check API routers
        for router_file in self.project_root.glob("src/tracertm/api/v1/routers/**/*.py"):
            content = self._safe_read(router_file)
            if content:
                fr_ids = self.extract_ids_from_text(content, FR_ID_PATTERN)
                if not fr_ids:
                    rel_path = router_file.relative_to(self.project_root)
                    orphaned_files.append(str(rel_path))

        if orphaned_files:
            # This is a warning, not an error
            self.warnings += 1
            self.add_result(
                False,
                "Orphaned Code",
                f"{len(orphaned_files)} service/router files have no FR references",
                orphaned_files
            )
        else:
            self.add_result(
                True,
                "Orphaned Code",
                "All service/router files have FR references"
            )

    def validate(self) -> bool:
        """Run all validations.

        Returns:
            True if all critical validations passed, False otherwise
        """
        self.log("=" * 60)
        self.log("Starting Traceability Validation")
        self.log("=" * 60)

        # Critical validations (must pass)
        self.validate_fr_ids_exist()
        self.validate_epic_ids_exist()
        self.validate_adr_ids_exist()

        # Warning-level checks
        self.check_orphaned_frs()
        self.check_orphaned_code()

        # Print summary
        self._print_summary()

        # Return True if no critical errors
        return self.errors == 0

    def _print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("📋 Validation Summary")
        print("=" * 60)

        # Group by category
        categories: dict[str, list[ValidationResult]] = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        # Print each category
        for category, results in sorted(categories.items()):
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            status = "✅" if passed == total else "❌"

            print(f"\n{status} {category}: {passed}/{total} checks passed")

            for result in results:
                prefix = "  ✅" if result.passed else "  ❌"
                print(f"{prefix} {result.message}")

        # Overall status
        print("\n" + "=" * 60)
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        if self.errors == 0:
            print(f"✅ VALIDATION PASSED: {passed_count}/{total_count} checks passed")
            if self.warnings > 0:
                print(f"⚠️  {self.warnings} warnings (non-blocking)")
        else:
            print(f"❌ VALIDATION FAILED: {self.errors} errors, {self.warnings} warnings")
            print(f"   {passed_count}/{total_count} checks passed")

        print("=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate traceability integrity across documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0: All validations passed
  1: Validation failures detected

Examples:
  python scripts/python/validate_traceability.py
  python scripts/python/validate_traceability.py --verbose
  python scripts/python/validate_traceability.py --check-code --verbose
        """
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--check-code",
        action="store_true",
        help="Scan code files for invalid FR/ADR references (slow)"
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Run validation
    validator = TraceabilityValidator(project_root, verbose=args.verbose, check_code=args.check_code)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
