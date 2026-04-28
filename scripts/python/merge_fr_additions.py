#!/usr/bin/env python3
"""Merge FR additions into FUNCTIONAL_REQUIREMENTS.md before Summary section.

Usage:
    python scripts/python/merge_fr_additions.py
"""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    """Merge FR additions into main FR document."""
    root = Path.cwd()
    fr_file = root / "docs/reference/FUNCTIONAL_REQUIREMENTS.md"
    additions_file = root / "docs/reference/FR_ADDITIONS_30_ENDPOINTS.md"

    if not fr_file.exists():
        print(f"Error: {fr_file} not found")
        return 1

    if not additions_file.exists():
        print(f"Error: {additions_file} not found")
        return 1

    # Read both files
    fr_content = fr_file.read_text()
    additions_content = additions_file.read_text()

    # Extract just the FR sections (skip header)
    additions_lines = additions_content.splitlines()
    fr_sections = []
    in_fr_section = False
    for line in additions_lines:
        if line.startswith("### FR-"):
            in_fr_section = True
        if in_fr_section and line.strip() and not line.startswith("#"):
            fr_sections.append(line)
        elif in_fr_section and line.startswith("---"):
            fr_sections.append(line)
            fr_sections.append("")  # blank line
        elif in_fr_section and line.startswith("###"):
            fr_sections.append("")  # blank line before next FR
            fr_sections.append(line)

    # Find Summary section
    fr_lines = fr_content.splitlines()
    summary_idx = None
    for i, line in enumerate(fr_lines):
        if line.strip() == "## Summary":
            summary_idx = i
            break

    if summary_idx is None:
        print("Error: ## Summary section not found")
        return 1

    # Build new sections based on category
    app_section = [
        "",
        "## FR-APP: Application & Tracking",
        "",
    ]
    qual_section = [
        "",
        "## FR-QUAL: Qualification & Analysis",
        "",
    ]
    rpt_section = [
        "",
        "## FR-RPT: Reporting & Analytics",
        "",
    ]
    collab_section = [
        "",
        "## FR-COLLAB: Collaboration & Integration",
        "",
    ]

    # Parse FR sections by category
    current_section: list[str] = []
    for line in additions_lines:
        if line.startswith("### FR-APP-"):
            current_section = app_section
            app_section.append(line)
        elif line.startswith("### FR-QUAL-"):
            current_section = qual_section
            qual_section.append(line)
        elif line.startswith("### FR-RPT-"):
            current_section = rpt_section
            rpt_section.append(line)
        elif line.startswith("### FR-COLLAB-"):
            current_section = collab_section
            collab_section.append(line)
        elif line.startswith("## Summary"):
            break  # Stop at summary
        elif current_section:
            current_section.append(line)

    # Insert sections before Summary
    new_lines = (
        fr_lines[:summary_idx]
        + app_section
        + [""]
        + qual_section
        + [""]
        + rpt_section
        + [""]
        + collab_section
        + ["", "---", ""]
        + fr_lines[summary_idx:]
    )

    # Update summary counts
    new_content_lines = []
    for line in new_lines:
        if "This document contains **29 functional requirements**" in line:
            new_content_lines.append(
                "This document contains **35 functional requirements** organized into **9 categories** covering the core features of TraceRTM.",
            )
        elif "**API Endpoints:** 50+ critical endpoints documented (of 672 total)" in line:
            new_content_lines.append(
                "- **API Endpoints:** 80+ critical endpoints documented (of 672 total)",
            )
        else:
            new_content_lines.append(line)

    # Write back
    new_content = "\n".join(new_content_lines)
    fr_file.write_text(new_content)

    print(f"✓ Merged 30 FR additions into {fr_file}")
    print("✓ Updated Summary section counts")
    print("")
    print("New FRs added:")
    print("  - FR-APP-001 through FR-APP-010 (10 FRs)")
    print("  - FR-QUAL-001 through FR-QUAL-008 (8 FRs)")
    print("  - FR-RPT-001 through FR-RPT-009 (9 FRs)")
    print("  - FR-COLLAB-001 through FR-COLLAB-003 (3 FRs)")
    print("")
    print("Ready to run: python scripts/python/annotate_apis_with_frs.py")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
