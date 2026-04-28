#!/usr/bin/env python3
"""Generate test coverage report from cross-link database.

Produces comprehensive test coverage reports showing which modules/specs/stories
have test coverage, test completeness, and coverage gaps.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_generate_test_coverage_report.py
Docs: docs/EXTENDED_CROSS_LINKING.md
Depends_On: scripts/extract_cross_links.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent.parent


class TestCoverageReportGenerator:
    """Generate test coverage reports from cross-links."""

    def __init__(self, db_path: Path):
        """Initialize with cross-link database."""
        with open(db_path) as f:
            self.db = json.load(f)

        self.coverage_data = {
            "modules": {},
            "specs": {},
            "stories": {},
            "summary": {
                "total_modules": 0,
                "modules_with_tests": 0,
                "total_specs": 0,
                "specs_with_tests": 0,
                "total_stories": 0,
                "stories_with_tests": 0,
                "total_test_files": 0,
                "total_test_functions": 0,
            },
        }

    def calculate_module_coverage(self):
        """Calculate test coverage for each module."""
        print("Calculating module test coverage...")

        for module_id, module in self.db["modules"].items():
            self.coverage_data["summary"]["total_modules"] += 1

            # Find tests for this module
            test_files = []
            test_functions = []

            # Check test path references
            test_paths = module.get("links", {}).get("tests", [])
            if isinstance(test_paths, str):
                test_paths = [test_paths]

            for test_path in test_paths:
                # Find matching test files
                for test_id in self.db["tests"].keys():
                    if test_path in test_id:
                        test_files.append(test_id)
                        # Count functions
                        test_functions.extend(self.db["tests"][test_id].get("functions", {}).keys())

            # Check verified_by references
            verified_by = module.get("links", {}).get("verified_by", [])
            if isinstance(verified_by, str):
                verified_by = [verified_by]

            for test_file in verified_by:
                if test_file not in test_files:
                    test_files.append(test_file)

            has_tests = len(test_files) > 0

            self.coverage_data["modules"][module_id] = {
                "state": module.get("links", {}).get("state", "UNKNOWN"),
                "specs": module.get("links", {}).get("specs", []),
                "stories": module.get("links", {}).get("stories", []),
                "test_files": test_files,
                "test_functions": test_functions,
                "has_tests": has_tests,
                "test_count": len(test_functions),
            }

            if has_tests:
                self.coverage_data["summary"]["modules_with_tests"] += 1

        print(f"  ✓ Analyzed {self.coverage_data['summary']['total_modules']} modules")

    def calculate_spec_coverage(self):
        """Calculate test coverage for each specification."""
        print("Calculating specification test coverage...")

        # Collect all specs
        all_specs = set()
        for module in self.db["modules"].values():
            specs = module.get("links", {}).get("specs", [])
            all_specs.update(specs)

        for test in self.db["tests"].values():
            specs = test.get("links", {}).get("specs", [])
            all_specs.update(specs)

        self.coverage_data["summary"]["total_specs"] = len(all_specs)

        # Calculate coverage for each spec
        for spec_id in all_specs:
            test_files = []
            test_functions = []
            implementations = []

            # Find tests
            for test_id, test in self.db["tests"].items():
                specs = test.get("links", {}).get("specs", [])
                if spec_id in specs:
                    test_files.append(test_id)

                # Check function-level markers
                for func_name, markers in test.get("functions", {}).items():
                    if spec_id in markers.get("spec", []):
                        test_functions.append(f"{test_id}::{func_name}")

            # Find implementations
            for module_id, module in self.db["modules"].items():
                specs = module.get("links", {}).get("specs", [])
                if spec_id in specs:
                    implementations.append(module_id)

            has_tests = len(test_files) > 0 or len(test_functions) > 0

            self.coverage_data["specs"][spec_id] = {
                "implementations": implementations,
                "test_files": test_files,
                "test_functions": test_functions,
                "has_tests": has_tests,
                "test_count": len(test_functions),
            }

            if has_tests:
                self.coverage_data["summary"]["specs_with_tests"] += 1

        print(f"  ✓ Analyzed {len(all_specs)} specifications")

    def calculate_story_coverage(self):
        """Calculate test coverage for each user story."""
        print("Calculating user story test coverage...")

        # Collect all stories
        all_stories = set()
        for module in self.db["modules"].values():
            stories = module.get("links", {}).get("stories", [])
            all_stories.update(stories)

        for test in self.db["tests"].values():
            stories = test.get("links", {}).get("stories", [])
            all_stories.update(stories)

        self.coverage_data["summary"]["total_stories"] = len(all_stories)

        # Calculate coverage for each story
        for story_id in all_stories:
            test_files = []
            test_functions = []
            implementations = []

            # Find tests
            for test_id, test in self.db["tests"].items():
                stories = test.get("links", {}).get("stories", [])
                if story_id in stories:
                    test_files.append(test_id)

                # Check function-level markers
                for func_name, markers in test.get("functions", {}).items():
                    if story_id in markers.get("story", []):
                        test_functions.append(f"{test_id}::{func_name}")

            # Find implementations
            for module_id, module in self.db["modules"].items():
                stories = module.get("links", {}).get("stories", [])
                if story_id in stories:
                    implementations.append(module_id)

            has_tests = len(test_files) > 0 or len(test_functions) > 0

            self.coverage_data["stories"][story_id] = {
                "implementations": implementations,
                "test_files": test_files,
                "test_functions": test_functions,
                "has_tests": has_tests,
                "test_count": len(test_functions),
            }

            if has_tests:
                self.coverage_data["summary"]["stories_with_tests"] += 1

        print(f"  ✓ Analyzed {len(all_stories)} user stories")

    def calculate_test_statistics(self):
        """Calculate test file and function statistics."""
        print("Calculating test statistics...")

        self.coverage_data["summary"]["total_test_files"] = len(self.db["tests"])

        total_functions = 0
        for test in self.db["tests"].values():
            total_functions += len(test.get("functions", {}))

        self.coverage_data["summary"]["total_test_functions"] = total_functions

        print(f"  ✓ Found {total_functions} test functions in {len(self.db['tests'])} files")

    def generate_markdown_report(self, output_path: Path):
        """Generate comprehensive Markdown coverage report."""
        lines = [
            "# Test Coverage Report",
            "",
            f"**Auto-generated** from cross-link database.",
            "",
            "---",
            "",
            "## Summary",
            "",
        ]

        # Summary statistics
        summary = self.coverage_data["summary"]
        module_pct = (summary["modules_with_tests"] / summary["total_modules"] * 100) if summary["total_modules"] > 0 else 0
        spec_pct = (summary["specs_with_tests"] / summary["total_specs"] * 100) if summary["total_specs"] > 0 else 0
        story_pct = (summary["stories_with_tests"] / summary["total_stories"] * 100) if summary["total_stories"] > 0 else 0

        lines.extend([
            "| Category | Total | With Tests | Coverage |",
            "|----------|-------|------------|----------|",
            f"| **Modules** | {summary['total_modules']} | {summary['modules_with_tests']} | {module_pct:.1f}% |",
            f"| **Specifications** | {summary['total_specs']} | {summary['specs_with_tests']} | {spec_pct:.1f}% |",
            f"| **User Stories** | {summary['total_stories']} | {summary['stories_with_tests']} | {story_pct:.1f}% |",
            "",
            "**Test Files**: " + str(summary["total_test_files"]),
            "**Test Functions**: " + str(summary["total_test_functions"]),
            "",
            "---",
            "",
            "## Module Coverage",
            "",
        ])

        # Group modules by state
        by_state = defaultdict(list)
        for module_id, coverage in sorted(self.coverage_data["modules"].items()):
            state = coverage["state"]
            by_state[state].append((module_id, coverage))

        for state in ["STABLE", "IN_PROGRESS", "EXPERIMENTAL", "DEPRECATED", "UNKNOWN"]:
            if state not in by_state:
                continue

            lines.extend([
                f"### {state} Modules",
                "",
                "| Module | Tests | Functions | Status |",
                "|--------|-------|-----------|--------|",
            ])

            for module_id, coverage in sorted(by_state[state]):
                status = "✅" if coverage["has_tests"] else "❌"
                test_count = coverage["test_count"]
                test_files = len(coverage["test_files"])

                module_name = module_id.replace("src/pheno/", "").replace("/__init__.py", "")
                lines.append(
                    f"| `{module_name}` | {test_files} | {test_count} | {status} |"
                )

            lines.extend(["", ""])

        # Specification coverage
        lines.extend([
            "---",
            "",
            "## Specification Coverage",
            "",
            "| Spec ID | Implementations | Test Files | Test Functions | Status |",
            "|---------|-----------------|------------|----------------|--------|",
        ])

        for spec_id, coverage in sorted(self.coverage_data["specs"].items()):
            status = "✅" if coverage["has_tests"] else "❌"
            impl_count = len(coverage["implementations"])
            test_files = len(coverage["test_files"])
            test_funcs = len(coverage["test_functions"])

            lines.append(
                f"| {spec_id} | {impl_count} | {test_files} | {test_funcs} | {status} |"
            )

        lines.extend(["", ""])

        # User story coverage
        lines.extend([
            "---",
            "",
            "## User Story Coverage",
            "",
            "| Story ID | Implementations | Test Files | Test Functions | Status |",
            "|----------|-----------------|------------|----------------|--------|",
        ])

        for story_id, coverage in sorted(self.coverage_data["stories"].items()):
            status = "✅" if coverage["has_tests"] else "❌"
            impl_count = len(coverage["implementations"])
            test_files = len(coverage["test_files"])
            test_funcs = len(coverage["test_functions"])

            lines.append(
                f"| {story_id} | {impl_count} | {test_files} | {test_funcs} | {status} |"
            )

        lines.extend(["", ""])

        # Modules without tests
        untested = [
            (module_id, coverage)
            for module_id, coverage in self.coverage_data["modules"].items()
            if not coverage["has_tests"]
        ]

        if untested:
            lines.extend([
                "---",
                "",
                "## Modules Without Tests",
                "",
                "| Module | State | Specs | Stories |",
                "|--------|-------|-------|---------|",
            ])

            for module_id, coverage in sorted(untested):
                module_name = module_id.replace("src/pheno/", "").replace("/__init__.py", "")
                specs = ", ".join(coverage["specs"]) if coverage["specs"] else "-"
                stories = ", ".join(coverage["stories"]) if coverage["stories"] else "-"
                lines.append(
                    f"| `{module_name}` | {coverage['state']} | {specs} | {stories} |"
                )

            lines.extend(["", ""])

        # Write report
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  ✓ Report saved to: {output_path}")


def main():
    """Generate test coverage report."""
    print("=" * 70)
    print("Generating Test Coverage Report")
    print("=" * 70)
    print()

    # Load cross-link database
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"
    if not db_path.exists():
        print(f"❌ Cross-link database not found: {db_path}")
        print("   Run: python scripts/extract_cross_links.py")
        return

    generator = TestCoverageReportGenerator(db_path)

    # Calculate coverage
    print()
    generator.calculate_module_coverage()
    generator.calculate_spec_coverage()
    generator.calculate_story_coverage()
    generator.calculate_test_statistics()

    # Generate report
    print()
    print("Generating coverage report...")
    output = PROJECT_ROOT / "docs" / "TEST_COVERAGE_REPORT.md"
    generator.generate_markdown_report(output)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    summary = generator.coverage_data["summary"]
    print(f"  Modules: {summary['modules_with_tests']}/{summary['total_modules']}")
    print(f"  Specs: {summary['specs_with_tests']}/{summary['total_specs']}")
    print(f"  Stories: {summary['stories_with_tests']}/{summary['total_stories']}")
    print(f"  Test Files: {summary['total_test_files']}")
    print(f"  Test Functions: {summary['total_test_functions']}")
    print()
    print("✅ Test coverage report generation complete!")
    print()
    print("Report: docs/TEST_COVERAGE_REPORT.md")


if __name__ == "__main__":
    main()
