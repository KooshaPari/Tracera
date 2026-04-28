#!/usr/bin/env python3
"""Generate dependency graphs from cross-link database.

Produces Mermaid diagrams and DOT graphs showing module dependencies,
spec relationships, and traceability chains.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_generate_dependency_graph.py
Docs: docs/EXTENDED_CROSS_LINKING.md
Depends_On: scripts/extract_cross_links.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent.parent


class DependencyGraphGenerator:
    """Generate dependency graphs and traceability diagrams."""

    def __init__(self, db_path: Path):
        """Initialize with cross-link database."""
        with open(db_path) as f:
            self.db = json.load(f)

    def generate_module_dependency_graph(self) -> str:
        """Generate Mermaid diagram of module dependencies."""
        lines = [
            "```mermaid",
            "graph TD",
        ]

        # Build dependency edges
        edges = set()
        nodes = set()

        for module_id, module in self.db["modules"].items():
            # Simplify module ID for display
            node_id = module_id.replace("src/pheno/", "").replace(".py", "").replace("/", "_")
            nodes.add((node_id, module.get("links", {}).get("state", "UNKNOWN")))

            # Process depends_on links
            depends_on = module.get("links", {}).get("depends_on", [])
            for dep in depends_on:
                dep_node = dep.replace("pheno.", "").replace(".", "_")
                edges.add((node_id, dep_node))

            # Process extends links
            extends = module.get("links", {}).get("extends", [])
            for ext in extends:
                ext_node = ext.replace("pheno.", "").replace(".", "_")
                edges.add((node_id, ext_node))

        # Add node definitions with state-based styling
        state_colors = {
            "STABLE": "#28a745",
            "IN_PROGRESS": "#ffc107",
            "EXPERIMENTAL": "#17a2b8",
            "DEPRECATED": "#dc3545",
            "UNKNOWN": "#6c757d",
        }

        for node, state in sorted(nodes):
            color = state_colors.get(state, "#6c757d")
            lines.append(f'    {node}["{node}"]')
            lines.append(f'    style {node} fill:{color},color:#fff')

        # Add edges
        for src, dst in sorted(edges):
            lines.append(f"    {src} --> {dst}")

        lines.append("```")
        return "\n".join(lines)

    def generate_spec_traceability_graph(self, spec_id: str) -> str:
        """Generate Mermaid diagram showing spec → story → code → test chain."""
        lines = [
            "```mermaid",
            "graph LR",
            f'    SPEC["{spec_id}"]',
            '    style SPEC fill:#007bff,color:#fff',
        ]

        # Find all artifacts linked to this spec
        impl_nodes = []
        test_nodes = []
        doc_nodes = []
        story_nodes = []

        # Search modules
        for module_id, module in self.db["modules"].items():
            specs = module.get("links", {}).get("specs", [])
            if spec_id in specs:
                node_id = f"M_{module_id.replace('/', '_').replace('.py', '')}"
                impl_nodes.append(node_id)
                lines.append(f'    {node_id}["{module_id}"]')
                lines.append(f'    style {node_id} fill:#28a745,color:#fff')
                lines.append(f"    SPEC --> {node_id}")

                # Get stories from this module
                stories = module.get("links", {}).get("stories", [])
                for story in stories:
                    story_node = f"S_{story}"
                    if story_node not in story_nodes:
                        story_nodes.append(story_node)
                        lines.append(f'    {story_node}["{story}"]')
                        lines.append(f'    style {story_node} fill:#ffc107,color:#000')
                        lines.append(f"    {story_node} --> {node_id}")

        # Search tests
        for test_id, test in self.db["tests"].items():
            specs = test.get("links", {}).get("specs", [])
            if spec_id in specs:
                node_id = f"T_{test_id.replace('/', '_').replace('.py', '')}"
                test_nodes.append(node_id)
                lines.append(f'    {node_id}["{test_id}"]')
                lines.append(f'    style {node_id} fill:#17a2b8,color:#fff')
                # Link tests to implementations
                for impl_node in impl_nodes:
                    lines.append(f"    {impl_node} -.test.-> {node_id}")

        # Search docs
        for doc_id, doc in self.db["docs"].items():
            doc_specs = doc.get("links", {}).get("specs", [])
            if isinstance(doc_specs, list) and spec_id in doc_specs:
                node_id = f"D_{doc_id.replace('/', '_').replace('.mdx', '').replace('.md', '')}"
                doc_nodes.append(node_id)
                lines.append(f'    {node_id}["{doc_id}"]')
                lines.append(f'    style {node_id} fill:#6f42c1,color:#fff')
                lines.append(f"    SPEC -.doc.-> {node_id}")

        lines.append("```")
        return "\n".join(lines)

    def generate_all_specs_traceability(self) -> str:
        """Generate overview traceability diagram for all specs."""
        lines = [
            "```mermaid",
            "graph TD",
        ]

        # Group specs by state
        by_state = defaultdict(list)
        for module_id, module in self.db["modules"].items():
            specs = module.get("links", {}).get("specs", [])
            state = module.get("links", {}).get("state", "UNKNOWN")
            for spec in specs:
                by_state[spec].append(state)

        # Create spec nodes with predominant state
        state_colors = {
            "STABLE": "#28a745",
            "IN_PROGRESS": "#ffc107",
            "EXPERIMENTAL": "#17a2b8",
            "DEPRECATED": "#dc3545",
            "UNKNOWN": "#6c757d",
        }

        spec_states = {}
        for spec, states in by_state.items():
            # Predominant state
            if "STABLE" in states:
                spec_states[spec] = "STABLE"
            elif "IN_PROGRESS" in states:
                spec_states[spec] = "IN_PROGRESS"
            elif "EXPERIMENTAL" in states:
                spec_states[spec] = "EXPERIMENTAL"
            else:
                spec_states[spec] = states[0] if states else "UNKNOWN"

        # Add spec nodes
        for spec in sorted(spec_states.keys()):
            state = spec_states[spec]
            color = state_colors.get(state, "#6c757d")
            node_id = spec.replace("-", "_")
            lines.append(f'    {node_id}["{spec}"]')
            lines.append(f'    style {node_id} fill:{color},color:#fff')

        # Add supersedes relationships
        for module_id, module in self.db["modules"].items():
            specs = module.get("links", {}).get("specs", [])
            supersedes = module.get("links", {}).get("supersedes", [])

            for spec in specs:
                for old_spec in supersedes:
                    if old_spec.startswith("SPEC-"):
                        spec_node = spec.replace("-", "_")
                        old_node = old_spec.replace("-", "_")
                        lines.append(f"    {spec_node} -.supersedes.-> {old_node}")

        lines.append("```")
        return "\n".join(lines)

    def generate_markdown_report(self, output_path: Path):
        """Generate comprehensive dependency graph report."""
        lines = [
            "# Dependency & Traceability Graphs",
            "",
            f"**Generated**: {Path(__file__).name}",
            "",
            "---",
            "",
            "## Module Dependency Graph",
            "",
            "Shows dependencies between modules (`Depends_On`, `Extends`).",
            "",
        ]

        # Module dependency graph
        lines.append(self.generate_module_dependency_graph())
        lines.extend(["", "---", "", "## Specification Traceability Overview", ""])
        lines.append(self.generate_all_specs_traceability())
        lines.extend(["", "---", "", "## Individual Spec Traceability", ""])

        # Generate graphs for top 10 specs
        spec_counts = defaultdict(int)
        for module in self.db["modules"].values():
            for spec in module.get("links", {}).get("specs", []):
                spec_counts[spec] += 1

        top_specs = sorted(spec_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        for spec_id, count in top_specs:
            lines.extend([
                f"### {spec_id}",
                "",
                f"**References**: {count}",
                "",
            ])
            lines.append(self.generate_spec_traceability_graph(spec_id))
            lines.extend(["", ""])

        # Write report
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  ✓ Report saved to: {output_path}")


def main():
    """Generate dependency graphs."""
    print("=" * 70)
    print("Generating Dependency & Traceability Graphs")
    print("=" * 70)
    print()

    # Load cross-link database
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"
    if not db_path.exists():
        print(f"❌ Cross-link database not found: {db_path}")
        print("   Run: python scripts/extract_cross_links.py")
        return

    generator = DependencyGraphGenerator(db_path)

    # Generate report
    print("Generating dependency graphs...")
    output = PROJECT_ROOT / "docs" / "DEPENDENCY_GRAPHS.md"
    generator.generate_markdown_report(output)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Report: {output}")
    print()
    print("✅ Dependency graph generation complete!")
    print()
    print("Next steps:")
    print("  1. Review: cat docs/DEPENDENCY_GRAPHS.md")
    print("  2. Render: Open in Markdown viewer with Mermaid support")
    print("  3. Export: Use mermaid-cli to generate PNG/SVG")


if __name__ == "__main__":
    main()
