#!/usr/bin/env python3
"""Generate specification coverage matrix from cross-link database.

Produces comprehensive coverage reports showing which specs have implementations,
tests, and documentation, with state tracking and completeness metrics.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_generate_spec_coverage.py
Docs: docs/EXTENDED_CROSS_LINKING.md
Depends_On: scripts/extract_cross_links.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent.parent


class SpecCoverageGenerator:
    """Generate specification coverage matrices and reports."""

    def __init__(self, db_path: Path):
        """Initialize with cross-link database."""
        with open(db_path) as f:
            self.db = json.load(f)

        self.spec_coverage = defaultdict(lambda: {
            "implementations": [],
            "tests": [],
            "docs": [],
            "stories": [],
            "state": "UNKNOWN",
            "since": None,
        })

    def build_coverage_matrix(self):
        """Build comprehensive spec coverage matrix."""
        print("Building specification coverage matrix...")

        # Process modules
        for module_id, module in self.db["modules"].items():
            specs = module["links"].get("specs", [])
            state = module["links"].get("state", "UNKNOWN")
            since = module["links"].get("since")

            for spec in specs:
                self.spec_coverage[spec]["implementations"].append({
                    "type": "module",
                    "id": module_id,
                    "state": state,
                })
                # Update spec state (highest precedence: STABLE > IN_PROGRESS > EXPERIMENTAL)
                if state == "STABLE":
                    self.spec_coverage[spec]["state"] = "STABLE"
                elif state == "IN_PROGRESS" and self.spec_coverage[spec]["state"] != "STABLE":
                    self.spec_coverage[spec]["state"] = "IN_PROGRESS"
                elif self.spec_coverage[spec]["state"] == "UNKNOWN":
                    self.spec_coverage[spec]["state"] = state

                if since:
                    self.spec_coverage[spec]["since"] = since

        # Process tests
        for test_id, test in self.db["tests"].items():
            specs = test["links"].get("specs", [])
            for spec in specs:
                self.spec_coverage[spec]["tests"].append({
                    "type": "test",
                    "id": test_id,
                })

            # Also check function-level markers
            for func_name, markers in test.get("functions", {}).items():
                func_specs = markers.get("spec", [])
                for spec in func_specs:
                    self.spec_coverage[spec]["tests"].append({
                        "type": "test_function",
                        "id": f"{test_id}::{func_name}",
                    })

        # Process docs
        for doc_id, doc in self.db["docs"].items():
            specs = doc["links"].get("specs", [])
            if isinstance(specs, list):
                for spec in specs:
                    self.spec_coverage[spec]["docs"].append({
                        "type": "doc",
                        "id": doc_id,
                    })
            elif isinstance(specs, dict):
                # MDX frontmatter may have specs as dict
                for spec in specs.keys():
                    self.spec_coverage[spec]["docs"].append({
                        "type": "doc",
                        "id": doc_id,
                    })

        print(f"  ✓ Found {len(self.spec_coverage)} specifications")
        return self.spec_coverage

    def calculate_completeness(self, spec_id: str, coverage: Dict) -> Dict:
        """Calculate completeness metrics for a specification."""
        has_impl = len(coverage["implementations"]) > 0
        has_test = len(coverage["tests"]) > 0
        has_docs = len(coverage["docs"]) > 0

        completeness = 0
        if has_impl:
            completeness += 40
        if has_test:
            completeness += 30
        if has_docs:
            completeness += 30

        status = "❌ Missing"
        if completeness == 100:
            status = "✅ Complete"
        elif completeness >= 70:
            status = "🟡 Partial"
        elif completeness >= 40:
            status = "🟠 Incomplete"

        return {
            "has_impl": has_impl,
            "has_test": has_test,
            "has_docs": has_docs,
            "completeness": completeness,
            "status": status,
        }

    def generate_markdown_report(self, output_path: Path):
        """Generate comprehensive Markdown coverage report."""
        lines = [
            "# Specification Coverage Matrix",
            "",
            f"**Generated**: {Path(__file__).name}",
            f"**Total Specifications**: {len(self.spec_coverage)}",
            "",
            "---",
            "",
            "## Coverage Summary",
            "",
        ]

        # Calculate summary stats
        total_specs = len(self.spec_coverage)
        complete = sum(1 for cov in self.spec_coverage.values()
                      if self.calculate_completeness("", cov)["completeness"] == 100)
        partial = sum(1 for cov in self.spec_coverage.values()
                     if 70 <= self.calculate_completeness("", cov)["completeness"] < 100)
        incomplete = sum(1 for cov in self.spec_coverage.values()
                        if 40 <= self.calculate_completeness("", cov)["completeness"] < 70)
        missing = total_specs - complete - partial - incomplete

        lines.extend([
            "| Status | Count | Percentage |",
            "|--------|-------|------------|",
            f"| ✅ Complete | {complete} | {complete/total_specs*100:.1f}% |",
            f"| 🟡 Partial | {partial} | {partial/total_specs*100:.1f}% |",
            f"| 🟠 Incomplete | {incomplete} | {incomplete/total_specs*100:.1f}% |",
            f"| ❌ Missing | {missing} | {missing/total_specs*100:.1f}% |",
            "",
            "---",
            "",
            "## Coverage by State",
            "",
        ])

        # Group by state
        by_state = defaultdict(list)
        for spec_id, coverage in sorted(self.spec_coverage.items()):
            state = coverage["state"]
            by_state[state].append((spec_id, coverage))

        for state in ["STABLE", "IN_PROGRESS", "EXPERIMENTAL", "DEPRECATED", "UNKNOWN"]:
            if state not in by_state:
                continue

            lines.extend([
                f"### {state} Specifications",
                "",
                "| Spec ID | State | Impl | Tests | Docs | Status |",
                "|---------|-------|------|-------|------|--------|",
            ])

            for spec_id, coverage in sorted(by_state[state]):
                metrics = self.calculate_completeness(spec_id, coverage)
                impl_icon = "✅" if metrics["has_impl"] else "❌"
                test_icon = "✅" if metrics["has_test"] else "❌"
                docs_icon = "✅" if metrics["has_docs"] else "❌"

                lines.append(
                    f"| {spec_id} | {state} | {impl_icon} | {test_icon} | {docs_icon} | "
                    f"{metrics['status']} ({metrics['completeness']}%) |"
                )

            lines.extend(["", ""])

        # Detailed coverage
        lines.extend([
            "---",
            "",
            "## Detailed Coverage",
            "",
        ])

        for spec_id, coverage in sorted(self.spec_coverage.items()):
            metrics = self.calculate_completeness(spec_id, coverage)
            lines.extend([
                f"### {spec_id}",
                "",
                f"**State**: {coverage['state']}",
                f"**Since**: {coverage.get('since', 'N/A')}",
                f"**Completeness**: {metrics['completeness']}% {metrics['status']}",
                "",
            ])

            if coverage["implementations"]:
                lines.append("**Implementations**:")
                for impl in coverage["implementations"]:
                    lines.append(f"- `{impl['id']}` ({impl.get('state', 'UNKNOWN')})")
                lines.append("")

            if coverage["tests"]:
                lines.append("**Tests**:")
                for test in coverage["tests"]:
                    lines.append(f"- `{test['id']}`")
                lines.append("")

            if coverage["docs"]:
                lines.append("**Documentation**:")
                for doc in coverage["docs"]:
                    lines.append(f"- `{doc['id']}`")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Write report
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  ✓ Report saved to: {output_path}")

    def generate_json_report(self, output_path: Path):
        """Generate JSON coverage report for programmatic use."""
        report = {
            "total_specs": len(self.spec_coverage),
            "summary": {},
            "by_state": defaultdict(list),
            "detailed": {},
        }

        # Summary
        for spec_id, coverage in self.spec_coverage.items():
            metrics = self.calculate_completeness(spec_id, coverage)
            status_key = metrics["status"].split()[1].lower()  # Extract status word
            if status_key not in report["summary"]:
                report["summary"][status_key] = 0
            report["summary"][status_key] += 1

            # By state
            state = coverage["state"]
            report["by_state"][state].append(spec_id)

            # Detailed
            report["detailed"][spec_id] = {
                "state": coverage["state"],
                "since": coverage.get("since"),
                "implementations": coverage["implementations"],
                "tests": coverage["tests"],
                "docs": coverage["docs"],
                "metrics": metrics,
            }

        # Convert defaultdict to dict for JSON
        report["by_state"] = dict(report["by_state"])

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, sort_keys=True)

        print(f"  ✓ JSON report saved to: {output_path}")


def main():
    """Generate specification coverage reports."""
    print("=" * 70)
    print("Generating Specification Coverage Matrix")
    print("=" * 70)
    print()

    # Load cross-link database
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"
    if not db_path.exists():
        print(f"❌ Cross-link database not found: {db_path}")
        print("   Run: python scripts/extract_cross_links.py")
        return

    generator = SpecCoverageGenerator(db_path)
    coverage = generator.build_coverage_matrix()

    # Generate Markdown report
    print()
    print("Generating Markdown report...")
    md_output = PROJECT_ROOT / "docs" / "SPEC_COVERAGE_MATRIX.md"
    generator.generate_markdown_report(md_output)

    # Generate JSON report
    print("Generating JSON report...")
    json_output = PROJECT_ROOT / "docs" / "spec_coverage.json"
    generator.generate_json_report(json_output)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Total specifications: {len(coverage)}")
    print(f"  Markdown report: {md_output}")
    print(f"  JSON report: {json_output}")
    print()
    print("✅ Specification coverage matrix generation complete!")
    print()
    print("Next steps:")
    print("  1. Review: cat docs/SPEC_COVERAGE_MATRIX.md")
    print("  2. Validate: python scripts/validate_links.py")
    print("  3. Generate graphs: python scripts/generate_dependency_graph.py")


if __name__ == "__main__":
    main()
