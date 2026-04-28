#!/usr/bin/env python3
"""Render a Mermaid dependency graph from tools/dependency_analysis.json.

- Shows bipartite graph: Kits -> Top dependencies (used by >= min_count kits)
- Output: docs/DEPENDENCY_GRAPH.md
"""

import json
from pathlib import Path

ROOT = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk")
ANALYSIS = ROOT / "tools" / "dependency_analysis.json"
OUT = ROOT / "docs" / "DEPENDENCY_GRAPH.md"
MIN_COUNT = 3  # only show deps used by >= 3 kits for readability


def sanitize(name: str) -> str:
    return name.lower().replace("-", "_").replace(" ", "_").replace("/", "_")


def main():
    data = json.loads(ANALYSIS.read_text())

    kit_deps: dict[str, dict[str, str]] = data.get("kit_dependencies", {})
    # Compute counts from summary
    most_common: list[tuple[str, int]] = data.get("summary", {}).get("most_common_dependencies", [])
    top_deps = [dep for dep, cnt in most_common if cnt >= MIN_COUNT]

    # Build edge list kit -> dep if kit uses dep in top_deps
    edges: list[tuple[str, str]] = []
    kits: list[str] = sorted(kit_deps.keys())

    for kit, deps in kit_deps.items():
        for dep in deps.keys():
            if dep in top_deps:
                edges.append((kit, dep))

    # Build Mermaid content
    lines: list[str] = []
    lines.append("# Dependency Graph (Mermaid)")
    lines.append("")
    lines.append(
        "This graph shows kit-to-dependency relationships for dependencies used by at least "
        + str(MIN_COUNT)
        + " kits.",
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append("  %% Kits")
    lines.append("  subgraph Kits")
    for kit in kits:
        lines.append(f'    kit_{sanitize(kit)}["{kit}"]')
    lines.append("  end")
    lines.append("  %% Dependencies (top)")
    lines.append("  subgraph Deps_\u22653")
    for dep in top_deps:
        lines.append(f'    dep_{sanitize(dep)}["{dep}"]')
    lines.append("  end")
    lines.append("  %% Edges")
    for kit, dep in edges:
        lines.append(f"  kit_{sanitize(kit)} --> dep_{sanitize(dep)}")
    lines.append("```")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"✅ Wrote Mermaid graph to {OUT}")


if __name__ == "__main__":
    main()
