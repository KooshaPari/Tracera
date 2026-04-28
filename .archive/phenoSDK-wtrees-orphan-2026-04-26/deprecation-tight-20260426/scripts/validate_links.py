#!/usr/bin/env python3
"""Validate cross-link integrity across the codebase.

Checks that all cross-links point to existing artifacts, identifies broken
links, and reports on link health metrics.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_validate_links.py
Docs: docs/EXTENDED_CROSS_LINKING.md
Depends_On: scripts/extract_cross_links.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent.parent


class CrossLinkValidator:
    """Validate cross-link integrity and report issues."""

    def __init__(self, db_path: Path):
        """Initialize with cross-link database."""
        with open(db_path) as f:
            self.db = json.load(f)

        self.errors = []
        self.warnings = []
        self.stats = {
            "total_links": 0,
            "valid_links": 0,
            "broken_links": 0,
            "dangling_refs": 0,
        }

        # Build artifact indexes
        self.all_artifacts = set()
        self.all_specs = set()
        self.all_stories = set()
        self.all_modules = set()
        self.all_tests = set()
        self.all_docs = set()

        self._build_indexes()

    def _build_indexes(self):
        """Build indexes of all artifacts for validation."""
        # Collect all artifact IDs
        for module_id in self.db["modules"].keys():
            self.all_artifacts.add(module_id)
            self.all_modules.add(module_id)

        for test_id in self.db["tests"].keys():
            self.all_artifacts.add(test_id)
            self.all_tests.add(test_id)

        for doc_id in self.db["docs"].keys():
            self.all_artifacts.add(doc_id)
            self.all_docs.add(doc_id)

        # Collect all spec/story IDs
        for module in self.db["modules"].values():
            specs = module.get("links", {}).get("specs", [])
            stories = module.get("links", {}).get("stories", [])
            self.all_specs.update(specs)
            self.all_stories.update(stories)

        for test in self.db["tests"].values():
            specs = test.get("links", {}).get("specs", [])
            stories = test.get("links", {}).get("stories", [])
            self.all_specs.update(specs)
            self.all_stories.update(stories)

    def validate_file_references(self):
        """Validate that all file paths exist."""
        print("Validating file references...")

        for module_id, module in self.db["modules"].items():
            path = PROJECT_ROOT / module_id
            if not path.exists():
                self.errors.append({
                    "type": "missing_file",
                    "artifact": module_id,
                    "message": f"Module file does not exist: {path}",
                })
                self.stats["broken_links"] += 1
            else:
                self.stats["valid_links"] += 1
            self.stats["total_links"] += 1

        for test_id, test in self.db["tests"].items():
            path = PROJECT_ROOT / test_id
            if not path.exists():
                self.errors.append({
                    "type": "missing_file",
                    "artifact": test_id,
                    "message": f"Test file does not exist: {path}",
                })
                self.stats["broken_links"] += 1
            else:
                self.stats["valid_links"] += 1
            self.stats["total_links"] += 1

        for doc_id, doc in self.db["docs"].items():
            path = PROJECT_ROOT / doc_id
            if not path.exists():
                self.errors.append({
                    "type": "missing_file",
                    "artifact": doc_id,
                    "message": f"Doc file does not exist: {path}",
                })
                self.stats["broken_links"] += 1
            else:
                self.stats["valid_links"] += 1
            self.stats["total_links"] += 1

        print(f"  ✓ Checked {self.stats['total_links']} file references")

    def validate_cross_references(self):
        """Validate cross-references between artifacts."""
        print("Validating cross-references...")

        link_count = 0

        # Validate module cross-references
        for module_id, module in self.db["modules"].items():
            links = module.get("links", {})

            # Validate tests references
            tests = links.get("tests", [])
            for test_ref in tests:
                link_count += 1
                # Test ref may be a directory, check if any tests exist under it
                test_files = list(PROJECT_ROOT.glob(f"{test_ref}**/test_*.py"))
                if not test_files and test_ref not in self.all_tests:
                    self.warnings.append({
                        "type": "broken_test_ref",
                        "artifact": module_id,
                        "target": test_ref,
                        "message": f"Referenced test not found: {test_ref}",
                    })

            # Validate docs references
            docs = links.get("docs", [])
            for doc_ref in docs:
                link_count += 1
                if not (PROJECT_ROOT / doc_ref).exists():
                    self.warnings.append({
                        "type": "broken_doc_ref",
                        "artifact": module_id,
                        "target": doc_ref,
                        "message": f"Referenced doc not found: {doc_ref}",
                    })

            # Validate supersedes references
            supersedes = links.get("supersedes", [])
            for old_ref in supersedes:
                link_count += 1
                if old_ref not in self.all_artifacts and not old_ref.startswith("SPEC-"):
                    self.warnings.append({
                        "type": "broken_supersedes_ref",
                        "artifact": module_id,
                        "target": old_ref,
                        "message": f"Superseded artifact not found: {old_ref}",
                    })

            # Validate depends_on references
            depends_on = links.get("depends_on", [])
            for dep_ref in depends_on:
                link_count += 1
                # Convert pheno.module notation to file path
                module_path = f"src/{dep_ref.replace('.', '/')}/__init__.py"
                if not (PROJECT_ROOT / module_path).exists():
                    alt_path = f"src/{dep_ref.replace('.', '/')}.py"
                    if not (PROJECT_ROOT / alt_path).exists():
                        self.warnings.append({
                            "type": "broken_dependency_ref",
                            "artifact": module_id,
                            "target": dep_ref,
                            "message": f"Dependency not found: {dep_ref}",
                        })

        print(f"  ✓ Validated {link_count} cross-references")

    def validate_spec_coverage(self):
        """Validate that specs have implementations and tests."""
        print("Validating spec coverage...")

        for spec_id in sorted(self.all_specs):
            has_impl = False
            has_test = False

            # Check implementations
            for module in self.db["modules"].values():
                if spec_id in module.get("links", {}).get("specs", []):
                    has_impl = True
                    break

            # Check tests
            for test in self.db["tests"].values():
                if spec_id in test.get("links", {}).get("specs", []):
                    has_test = True
                    break

            if not has_impl:
                self.warnings.append({
                    "type": "spec_no_impl",
                    "artifact": spec_id,
                    "message": f"Spec has no implementation: {spec_id}",
                })
                self.stats["dangling_refs"] += 1

            if not has_test:
                self.warnings.append({
                    "type": "spec_no_test",
                    "artifact": spec_id,
                    "message": f"Spec has no tests: {spec_id}",
                })

        print(f"  ✓ Validated {len(self.all_specs)} specs")

    def validate_story_coverage(self):
        """Validate that stories have implementations."""
        print("Validating story coverage...")

        for story_id in sorted(self.all_stories):
            has_impl = False

            # Check implementations
            for module in self.db["modules"].values():
                if story_id in module.get("links", {}).get("stories", []):
                    has_impl = True
                    break

            if not has_impl:
                self.warnings.append({
                    "type": "story_no_impl",
                    "artifact": story_id,
                    "message": f"Story has no implementation: {story_id}",
                })
                self.stats["dangling_refs"] += 1

        print(f"  ✓ Validated {len(self.all_stories)} stories")

    def generate_report(self, output_path: Path):
        """Generate validation report."""
        lines = [
            "# Cross-Link Validation Report",
            "",
            f"**Generated**: {Path(__file__).name}",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"- **Total Links**: {self.stats['total_links']}",
            f"- **Valid Links**: {self.stats['valid_links']}",
            f"- **Broken Links**: {self.stats['broken_links']}",
            f"- **Dangling References**: {self.stats['dangling_refs']}",
            f"- **Total Errors**: {len(self.errors)}",
            f"- **Total Warnings**: {len(self.warnings)}",
            "",
        ]

        # Overall status
        if len(self.errors) == 0 and len(self.warnings) == 0:
            lines.extend([
                "**Status**: ✅ All links valid",
                "",
            ])
        elif len(self.errors) == 0:
            lines.extend([
                f"**Status**: 🟡 {len(self.warnings)} warnings",
                "",
            ])
        else:
            lines.extend([
                f"**Status**: ❌ {len(self.errors)} errors, {len(self.warnings)} warnings",
                "",
            ])

        # Errors section
        if self.errors:
            lines.extend([
                "---",
                "",
                "## Errors",
                "",
            ])

            # Group by type
            by_type = defaultdict(list)
            for error in self.errors:
                by_type[error["type"]].append(error)

            for error_type, errors in sorted(by_type.items()):
                lines.extend([
                    f"### {error_type.replace('_', ' ').title()}",
                    "",
                ])
                for error in errors:
                    lines.append(f"- **{error['artifact']}**: {error['message']}")
                lines.append("")

        # Warnings section
        if self.warnings:
            lines.extend([
                "---",
                "",
                "## Warnings",
                "",
            ])

            # Group by type
            by_type = defaultdict(list)
            for warning in self.warnings:
                by_type[warning["type"]].append(warning)

            for warning_type, warnings in sorted(by_type.items()):
                lines.extend([
                    f"### {warning_type.replace('_', ' ').title()}",
                    "",
                ])
                for warning in warnings[:20]:  # Limit to first 20
                    lines.append(f"- **{warning['artifact']}**: {warning['message']}")
                if len(warnings) > 20:
                    lines.append(f"- ... and {len(warnings) - 20} more")
                lines.append("")

        # Write report
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  ✓ Report saved to: {output_path}")


def main():
    """Validate cross-links."""
    print("=" * 70)
    print("Validating Cross-Link Integrity")
    print("=" * 70)
    print()

    # Load cross-link database
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"
    if not db_path.exists():
        print(f"❌ Cross-link database not found: {db_path}")
        print("   Run: python scripts/extract_cross_links.py")
        return

    validator = CrossLinkValidator(db_path)

    # Run validations
    print()
    validator.validate_file_references()
    validator.validate_cross_references()
    validator.validate_spec_coverage()
    validator.validate_story_coverage()

    # Generate report
    print()
    print("Generating validation report...")
    output = PROJECT_ROOT / "docs" / "CROSS_LINK_VALIDATION.md"
    validator.generate_report(output)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Total Links: {validator.stats['total_links']}")
    print(f"  Valid: {validator.stats['valid_links']}")
    print(f"  Broken: {validator.stats['broken_links']}")
    print(f"  Errors: {len(validator.errors)}")
    print(f"  Warnings: {len(validator.warnings)}")
    print()

    if len(validator.errors) == 0 and len(validator.warnings) == 0:
        print("✅ All cross-links are valid!")
    elif len(validator.errors) == 0:
        print(f"🟡 {len(validator.warnings)} warnings found")
    else:
        print(f"❌ {len(validator.errors)} errors found")

    print()
    print("Report: docs/CROSS_LINK_VALIDATION.md")


if __name__ == "__main__":
    main()
