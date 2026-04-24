#!/usr/bin/env python3
"""Add YAML frontmatter to documentation pages.

This script adds frontmatter metadata to all markdown files in the docs/ directory
following the state model and cross-linking configuration.
"""

from pathlib import Path

FRONTMATTER_TEMPLATES = {
    "research_overview": {
        "state": "RESEARCH",
        "tags": ["research", "overview"],
        "timeline": "Ongoing reference",
    },
    "research_dimension": {
        "state": "RESEARCH",
        "tags": ["research", "tools"],
        "timeline": "Ongoing reference",
    },
    "research_tools": {
        "state": "RESEARCH",
        "tags": ["research", "tools", "catalog"],
        "timeline": "Ongoing reference",
    },
    "planning_overview": {
        "state": "PLANNED",
        "tags": ["planning", "overview"],
        "timeline": "Weeks 1-12",
    },
    "planning_phase": {
        "state": "PLANNED",
        "tags": ["planning", "phase"],
        "timeline": "Weeks 1-12",
    },
    "planning_timeline": {
        "state": "PLANNED",
        "tags": ["planning", "timeline"],
        "timeline": "Weeks 1-12",
    },
    "specs_overview": {
        "state": "PROPOSAL",
        "tags": ["specifications", "overview"],
        "timeline": "Design phase",
    },
    "specs_architecture": {
        "state": "PROPOSAL",
        "tags": ["specifications", "architecture"],
        "timeline": "Design phase",
    },
    "guide": {
        "state": "COMPLETE",
        "tags": ["guide", "reference"],
        "timeline": "Ongoing reference",
    },
}

PAGE_MAPPINGS = {
    # Research pages
    "docs/research/overview.md": {
        "template": "research_overview",
        "relates_to": [
            "docs/research/dimensions/index.md",
            "docs/planning/overview.md",
        ],
    },
    "docs/research/dimensions/index.md": {
        "template": "research_dimension",
        "relates_to": [
            "docs/research/overview.md",
            "docs/research/dimensions/phenosdk-tools.md",
            "docs/planning/phases/index.md",
        ],
    },
    "docs/research/dimensions/phenosdk-tools.md": {
        "template": "research_dimension",
        "tags_add": ["tools"],
        "relates_to": [
            "docs/planning/phases/index.md#phase-3-features",
            "docs/research/tools-catalog.md",
        ],
    },
    "docs/research/dimensions/trace-testing.md": {
        "template": "research_dimension",
        "tags_add": ["testing"],
        "relates_to": [
            "docs/planning/phases/index.md#phase-2-quality",
        ],
    },
    "docs/research/dimensions/trace-infrastructure.md": {
        "template": "research_dimension",
        "tags_add": ["infrastructure"],
        "relates_to": [
            "docs/planning/phases/index.md#phase-4-infrastructure",
        ],
    },
    "docs/research/dimensions/trace-setup.md": {
        "template": "research_dimension",
        "tags_add": ["setup", "devops"],
        "relates_to": [
            "docs/planning/phases/index.md#phase-1-foundation",
        ],
    },
    "docs/research/dimensions/trace-ultra.md": {
        "template": "research_dimension",
        "tags_add": ["advanced", "specialized"],
        "relates_to": [
            "docs/planning/phases/index.md#phase-5-specialization",
        ],
    },
    "docs/research/tools-catalog.md": {
        "template": "research_tools",
        "relates_to": [
            "docs/research/overview.md",
            "docs/research/tools-matrix.md",
            "docs/planning/tracks.md",
        ],
    },
    "docs/research/tools-matrix.md": {
        "template": "research_tools",
        "relates_to": [
            "docs/research/tools-catalog.md",
            "docs/planning/master-plan.md",
        ],
    },
    "docs/research/packages.md": {
        "template": "research_tools",
        "relates_to": [
            "docs/research/tools-catalog.md",
            "docs/research/overview.md",
        ],
    },
    # Planning pages
    "docs/planning/overview.md": {
        "template": "planning_overview",
        "relates_to": [
            "docs/planning/master-plan.md",
            "docs/research/overview.md",
            "docs/specs/overview.md",
        ],
    },
    "docs/planning/master-plan.md": {
        "template": "planning_phase",
        "relates_to": [
            "docs/planning/overview.md",
            "docs/planning/timeline.md",
            "docs/planning/phases/index.md",
            "docs/research/overview.md",
        ],
    },
    "docs/planning/timeline.md": {
        "template": "planning_timeline",
        "relates_to": [
            "docs/planning/master-plan.md",
            "docs/planning/phases/index.md",
            "docs/planning/checklist.md",
        ],
    },
    "docs/planning/phases/index.md": {
        "template": "planning_phase",
        "relates_to": [
            "docs/planning/overview.md",
            "docs/planning/wbs-pert.md",
            "docs/specs/overview.md",
        ],
    },
    "docs/planning/wbs-pert.md": {
        "template": "planning_phase",
        "tags_add": ["wbs", "pert"],
        "relates_to": [
            "docs/planning/master-plan.md",
            "docs/planning/phases/index.md",
        ],
    },
    "docs/planning/checklist.md": {
        "template": "planning_timeline",
        "tags_add": ["checklist", "execution"],
        "relates_to": [
            "docs/planning/timeline.md",
            "docs/planning/phases/index.md",
        ],
    },
    "docs/planning/tracks.md": {
        "template": "planning_overview",
        "tags_add": ["tracks", "velocity"],
        "relates_to": [
            "docs/planning/overview.md",
            "docs/planning/master-plan.md",
            "docs/research/tools-catalog.md",
        ],
    },
    # Specs pages
    "docs/specs/overview.md": {
        "template": "specs_overview",
        "relates_to": [
            "docs/specs/architecture/index.md",
            "docs/specs/proposals/index.md",
            "docs/planning/master-plan.md",
            "docs/research/overview.md",
        ],
    },
    "docs/specs/architecture/index.md": {
        "template": "specs_architecture",
        "relates_to": [
            "docs/specs/overview.md",
            "docs/specs/integration/index.md",
            "docs/research/dimensions/trace-infrastructure.md",
        ],
    },
    "docs/specs/proposals/index.md": {
        "template": "specs_overview",
        "tags_add": ["proposals", "adr"],
        "relates_to": [
            "docs/specs/overview.md",
            "docs/research/overview.md",
        ],
    },
    "docs/specs/technical/index.md": {
        "template": "specs_overview",
        "tags_add": ["technical", "standards"],
        "relates_to": [
            "docs/specs/overview.md",
            "docs/specs/architecture/index.md",
        ],
    },
    "docs/specs/integration/index.md": {
        "template": "specs_overview",
        "tags_add": ["integration", "patterns"],
        "relates_to": [
            "docs/specs/overview.md",
            "docs/specs/architecture/index.md",
        ],
    },
    # Guide pages
    "docs/guide/state-model.md": {
        "template": "guide",
        "relates_to": [
            "docs/research/overview.md",
            "docs/planning/overview.md",
            "docs/specs/overview.md",
        ],
    },
}


def create_frontmatter(
    template: str,
    config: dict,
    tags_add: list[str] | None = None,
) -> str:
    """Create YAML frontmatter from template."""
    base = FRONTMATTER_TEMPLATES[template].copy()

    # Add additional tags
    if tags_add:
        base["tags"].extend(tags_add)

    # Add configuration
    base.update({k: v for k, v in config.items() if k not in {"template", "tags_add"}})

    # Build YAML
    lines = ["---"]

    # State
    lines.append(f"state: {base['state']}")

    # Tags
    tags_str = ", ".join(f'"{tag}"' for tag in base["tags"])
    lines.append(f"tags: [{tags_str}]")

    # Timeline
    if "timeline" in base:
        lines.append(f'timeline: "{base["timeline"]}"')

    # Relates to
    if base.get("relates_to"):
        lines.append("relates_to:")
        lines.extend(f'  - "{rel}"' for rel in base["relates_to"])

    # Implemented in
    if "implemented_in" in base:
        lines.append(f'implemented_in: "{base["implemented_in"]}"')

    lines.append("---\n")

    return "\n".join(lines)


def has_frontmatter(content: str) -> bool:
    """Check if file already has frontmatter."""
    return content.startswith("---\n")


def remove_existing_frontmatter(content: str) -> str:
    """Remove existing frontmatter from content."""
    if not content.startswith("---\n"):
        return content

    # Find closing ---
    lines = content.split("\n")
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1 :])

    return content


def add_frontmatter_to_file(base_path: Path, filepath: str) -> bool:
    """Add frontmatter to a single file."""
    if filepath not in PAGE_MAPPINGS:
        return False

    config = PAGE_MAPPINGS[filepath].copy()
    template = config.pop("template")
    if not isinstance(template, str):
        return False
    tags_add = config.pop("tags_add", None)
    if tags_add is not None and not isinstance(tags_add, list):
        tags_add = None

    full_path = base_path / filepath

    try:
        content = Path(full_path).read_text(encoding="utf-8")

        # Remove existing frontmatter if present
        if has_frontmatter(content):
            content = remove_existing_frontmatter(content)

        # Create new frontmatter
        frontmatter = create_frontmatter(template, config, tags_add)

        # Write back
        Path(full_path).write_text(frontmatter + content, encoding="utf-8")

        return True
    except Exception:
        return False


def main() -> None:
    """Add frontmatter to all documentation pages."""
    base_path = Path(__file__).parent.parent

    len(PAGE_MAPPINGS)
    success = 0

    for filepath in sorted(PAGE_MAPPINGS.keys()):
        full_path = base_path / filepath

        if full_path.exists() and add_frontmatter_to_file(base_path, filepath):
            success += 1


if __name__ == "__main__":
    main()
