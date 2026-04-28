#!/usr/bin/env python3
"""Analyze change impact using cross-link database.

Given a module, spec, or story ID, analyzes all affected artifacts through
cross-links to show the blast radius of changes.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_analyze_change_impact.py
Docs: docs/EXTENDED_CROSS_LINKING.md
Depends_On: scripts/extract_cross_links.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import argparse


PROJECT_ROOT = Path(__file__).parent.parent


class ChangeImpactAnalyzer:
    """Analyze change impact across codebase using cross-links."""

    def __init__(self, db_path: Path):
        """Initialize with cross-link database."""
        with open(db_path) as f:
            self.db = json.load(f)

    def analyze_module_impact(self, module_id: str) -> Dict:
        """Analyze impact of changing a module."""
        if module_id not in self.db["modules"]:
            return {"error": f"Module not found: {module_id}"}

        module = self.db["modules"][module_id]
        links = module.get("links", {})

        impact = {
            "changed_module": module_id,
            "state": links.get("state", "UNKNOWN"),
            "directly_affected": {
                "specs": [],
                "stories": [],
                "tests": [],
                "docs": [],
                "dependent_modules": [],
            },
            "indirectly_affected": {
                "modules": [],
                "tests": [],
            },
            "blast_radius": {
                "total_artifacts": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        }

        # Direct impacts - specs and stories
        impact["directly_affected"]["specs"] = links.get("specs", [])
        impact["directly_affected"]["stories"] = links.get("stories", [])

        # Direct impacts - tests
        test_paths = links.get("tests", [])
        if isinstance(test_paths, str):
            test_paths = [test_paths]

        for test_id in self.db["tests"].keys():
            for test_path in test_paths:
                if test_path in test_id:
                    impact["directly_affected"]["tests"].append(test_id)

        # Direct impacts - docs
        doc_refs = links.get("docs", [])
        if isinstance(doc_refs, str):
            doc_refs = [doc_refs]
        impact["directly_affected"]["docs"] = doc_refs

        # Direct impacts - dependent modules
        for other_id, other in self.db["modules"].items():
            deps = other.get("links", {}).get("depends_on", [])
            if isinstance(deps, str):
                deps = [deps]

            module_name = module_id.replace("src/pheno/", "pheno.").replace("/__init__.py", "").replace("/", ".")
            for dep in deps:
                if module_name in dep or dep in module_name:
                    impact["directly_affected"]["dependent_modules"].append(other_id)

            # Check extends
            extends = other.get("links", {}).get("extends", [])
            if isinstance(extends, str):
                extends = [extends]
            for ext in extends:
                if module_name in ext:
                    impact["directly_affected"]["dependent_modules"].append(other_id)

        # Indirect impacts - modules implementing same specs/stories
        for spec in impact["directly_affected"]["specs"]:
            for other_id, other in self.db["modules"].items():
                if other_id == module_id:
                    continue
                if spec in other.get("links", {}).get("specs", []):
                    if other_id not in impact["indirectly_affected"]["modules"]:
                        impact["indirectly_affected"]["modules"].append(other_id)

        # Indirect impacts - tests for affected specs/stories
        for spec in impact["directly_affected"]["specs"]:
            for test_id, test in self.db["tests"].items():
                if spec in test.get("links", {}).get("specs", []):
                    if test_id not in impact["indirectly_affected"]["tests"]:
                        impact["indirectly_affected"]["tests"].append(test_id)

        # Calculate blast radius
        total = (
            len(impact["directly_affected"]["specs"])
            + len(impact["directly_affected"]["stories"])
            + len(impact["directly_affected"]["tests"])
            + len(impact["directly_affected"]["docs"])
            + len(impact["directly_affected"]["dependent_modules"])
            + len(impact["indirectly_affected"]["modules"])
            + len(impact["indirectly_affected"]["tests"])
        )

        impact["blast_radius"]["total_artifacts"] = total

        # Severity based on:
        # - STABLE modules with many dependents = CRITICAL
        # - Modules with specs/stories = HIGH
        # - Modules with tests = MEDIUM
        # - Everything else = LOW

        if links.get("state") == "STABLE" and len(impact["directly_affected"]["dependent_modules"]) > 3:
            impact["blast_radius"]["critical"] = total
        elif len(impact["directly_affected"]["specs"]) > 0 or len(impact["directly_affected"]["stories"]) > 0:
            impact["blast_radius"]["high"] = total
        elif len(impact["directly_affected"]["tests"]) > 0:
            impact["blast_radius"]["medium"] = total
        else:
            impact["blast_radius"]["low"] = total

        return impact

    def analyze_spec_impact(self, spec_id: str) -> Dict:
        """Analyze impact of changing a specification."""
        impact = {
            "changed_spec": spec_id,
            "implementations": [],
            "tests": [],
            "docs": [],
            "stories": [],
            "blast_radius": 0,
        }

        # Find implementations
        for module_id, module in self.db["modules"].items():
            if spec_id in module.get("links", {}).get("specs", []):
                impact["implementations"].append(module_id)

        # Find tests
        for test_id, test in self.db["tests"].items():
            if spec_id in test.get("links", {}).get("specs", []):
                impact["tests"].append(test_id)

        # Find docs
        for doc_id, doc in self.db["docs"].items():
            doc_specs = doc.get("links", {}).get("specs", [])
            if isinstance(doc_specs, list) and spec_id in doc_specs:
                impact["docs"].append(doc_id)
            elif isinstance(doc_specs, dict) and spec_id in doc_specs.keys():
                impact["docs"].append(doc_id)

        # Find related stories
        for module_id in impact["implementations"]:
            module = self.db["modules"][module_id]
            stories = module.get("links", {}).get("stories", [])
            for story in stories:
                if story not in impact["stories"]:
                    impact["stories"].append(story)

        impact["blast_radius"] = (
            len(impact["implementations"])
            + len(impact["tests"])
            + len(impact["docs"])
            + len(impact["stories"])
        )

        return impact

    def analyze_story_impact(self, story_id: str) -> Dict:
        """Analyze impact of changing a user story."""
        impact = {
            "changed_story": story_id,
            "implementations": [],
            "specs": [],
            "tests": [],
            "blast_radius": 0,
        }

        # Find implementations
        for module_id, module in self.db["modules"].items():
            if story_id in module.get("links", {}).get("stories", []):
                impact["implementations"].append(module_id)

        # Find tests
        for test_id, test in self.db["tests"].items():
            if story_id in test.get("links", {}).get("stories", []):
                impact["tests"].append(test_id)

        # Find specs
        for module_id in impact["implementations"]:
            module = self.db["modules"][module_id]
            specs = module.get("links", {}).get("specs", [])
            for spec in specs:
                if spec not in impact["specs"]:
                    impact["specs"].append(spec)

        impact["blast_radius"] = (
            len(impact["implementations"])
            + len(impact["tests"])
            + len(impact["specs"])
        )

        return impact

    def generate_impact_report(self, target: str, output_path: Path):
        """Generate impact analysis report for a target."""
        lines = [
            "# Change Impact Analysis",
            "",
            f"**Target**: `{target}`",
            "",
            "---",
            "",
        ]

        # Determine target type
        if target.startswith("SPEC-"):
            impact = self.analyze_spec_impact(target)
            lines.extend(self._format_spec_impact(impact))
        elif target.startswith("US-"):
            impact = self.analyze_story_impact(target)
            lines.extend(self._format_story_impact(impact))
        else:
            # Assume module
            impact = self.analyze_module_impact(target)
            lines.extend(self._format_module_impact(impact))

        # Write report
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  ✓ Report saved to: {output_path}")

    def _format_module_impact(self, impact: Dict) -> List[str]:
        """Format module impact as Markdown."""
        if "error" in impact:
            return [f"**Error**: {impact['error']}"]

        lines = [
            "## Module Impact Analysis",
            "",
            f"**Module**: `{impact['changed_module']}`",
            f"**State**: {impact['state']}",
            "",
            "### Blast Radius",
            "",
            f"**Total Affected Artifacts**: {impact['blast_radius']['total_artifacts']}",
            "",
        ]

        # Severity
        if impact["blast_radius"]["critical"] > 0:
            lines.extend([
                "**Severity**: 🔴 **CRITICAL**",
                "",
                "This is a STABLE module with many dependents. Changes require careful review.",
                "",
            ])
        elif impact["blast_radius"]["high"] > 0:
            lines.extend([
                "**Severity**: 🟠 **HIGH**",
                "",
                "This module implements specifications or user stories. Changes may break contracts.",
                "",
            ])
        elif impact["blast_radius"]["medium"] > 0:
            lines.extend([
                "**Severity**: 🟡 **MEDIUM**",
                "",
                "This module has test coverage. Update tests after changes.",
                "",
            ])
        else:
            lines.extend([
                "**Severity**: 🟢 **LOW**",
                "",
                "Limited impact. Safe to modify.",
                "",
            ])

        # Direct impacts
        lines.extend([
            "### Directly Affected",
            "",
        ])

        if impact["directly_affected"]["specs"]:
            lines.append(f"**Specifications** ({len(impact['directly_affected']['specs'])}): {', '.join(impact['directly_affected']['specs'])}")
            lines.append("")

        if impact["directly_affected"]["stories"]:
            lines.append(f"**User Stories** ({len(impact['directly_affected']['stories'])}): {', '.join(impact['directly_affected']['stories'])}")
            lines.append("")

        if impact["directly_affected"]["tests"]:
            lines.append(f"**Test Files** ({len(impact['directly_affected']['tests'])}):")
            for test in impact["directly_affected"]["tests"]:
                lines.append(f"- `{test}`")
            lines.append("")

        if impact["directly_affected"]["docs"]:
            lines.append(f"**Documentation** ({len(impact['directly_affected']['docs'])}):")
            for doc in impact["directly_affected"]["docs"]:
                lines.append(f"- `{doc}`")
            lines.append("")

        if impact["directly_affected"]["dependent_modules"]:
            lines.append(f"**Dependent Modules** ({len(impact['directly_affected']['dependent_modules'])}):")
            for mod in impact["directly_affected"]["dependent_modules"]:
                lines.append(f"- `{mod}`")
            lines.append("")

        # Indirect impacts
        if impact["indirectly_affected"]["modules"] or impact["indirectly_affected"]["tests"]:
            lines.extend([
                "### Indirectly Affected",
                "",
            ])

            if impact["indirectly_affected"]["modules"]:
                lines.append(f"**Modules** ({len(impact['indirectly_affected']['modules'])}): {', '.join(impact['indirectly_affected']['modules'][:5])}")
                if len(impact["indirectly_affected"]["modules"]) > 5:
                    lines.append(f"... and {len(impact['indirectly_affected']['modules']) - 5} more")
                lines.append("")

            if impact["indirectly_affected"]["tests"]:
                lines.append(f"**Tests** ({len(impact['indirectly_affected']['tests'])}): {', '.join(impact['indirectly_affected']['tests'][:5])}")
                if len(impact["indirectly_affected"]["tests"]) > 5:
                    lines.append(f"... and {len(impact['indirectly_affected']['tests']) - 5} more")
                lines.append("")

        return lines

    def _format_spec_impact(self, impact: Dict) -> List[str]:
        """Format spec impact as Markdown."""
        lines = [
            "## Specification Impact Analysis",
            "",
            f"**Specification**: `{impact['changed_spec']}`",
            f"**Blast Radius**: {impact['blast_radius']} artifacts",
            "",
        ]

        if impact["implementations"]:
            lines.append(f"**Implementations** ({len(impact['implementations'])}):")
            for impl in impact["implementations"]:
                lines.append(f"- `{impl}`")
            lines.append("")

        if impact["tests"]:
            lines.append(f"**Tests** ({len(impact['tests'])}):")
            for test in impact["tests"]:
                lines.append(f"- `{test}`")
            lines.append("")

        if impact["docs"]:
            lines.append(f"**Documentation** ({len(impact['docs'])}):")
            for doc in impact["docs"]:
                lines.append(f"- `{doc}`")
            lines.append("")

        if impact["stories"]:
            lines.append(f"**Related Stories** ({len(impact['stories'])}): {', '.join(impact['stories'])}")
            lines.append("")

        return lines

    def _format_story_impact(self, impact: Dict) -> List[str]:
        """Format story impact as Markdown."""
        lines = [
            "## User Story Impact Analysis",
            "",
            f"**User Story**: `{impact['changed_story']}`",
            f"**Blast Radius**: {impact['blast_radius']} artifacts",
            "",
        ]

        if impact["implementations"]:
            lines.append(f"**Implementations** ({len(impact['implementations'])}):")
            for impl in impact["implementations"]:
                lines.append(f"- `{impl}`")
            lines.append("")

        if impact["tests"]:
            lines.append(f"**Tests** ({len(impact['tests'])}):")
            for test in impact["tests"]:
                lines.append(f"- `{test}`")
            lines.append("")

        if impact["specs"]:
            lines.append(f"**Specifications** ({len(impact['specs'])}): {', '.join(impact['specs'])}")
            lines.append("")

        return lines


def main():
    """Analyze change impact."""
    parser = argparse.ArgumentParser(description="Analyze change impact for a module, spec, or story")
    parser.add_argument("target", help="Module ID, SPEC-XXX, or US-XXX to analyze")
    parser.add_argument("-o", "--output", help="Output file (default: docs/CHANGE_IMPACT.md)")

    args = parser.parse_args()

    print("=" * 70)
    print("Change Impact Analysis")
    print("=" * 70)
    print()

    # Load cross-link database
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"
    if not db_path.exists():
        print(f"❌ Cross-link database not found: {db_path}")
        print("   Run: python scripts/extract_cross_links.py")
        return

    analyzer = ChangeImpactAnalyzer(db_path)

    # Analyze target
    print(f"Analyzing impact of: {args.target}")
    print()

    output = Path(args.output) if args.output else PROJECT_ROOT / "docs" / "CHANGE_IMPACT.md"
    analyzer.generate_impact_report(args.target, output)

    print()
    print("✅ Change impact analysis complete!")
    print()
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
