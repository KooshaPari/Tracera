"""Markdown parser for TraceRTM local storage.

This module handles parsing and writing of Markdown files with YAML frontmatter
for TraceRTM items (epics, stories, tests, tasks). It implements the format
defined in the Unified Local Storage Architecture.

Format:
- YAML frontmatter with metadata (id, type, status, etc.)
- Markdown body with structured sections (Title, Description, Acceptance Criteria, etc.)
- Separate YAML files for links and configuration
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from pathlib import Path

# Minimum lines required for a table-based history section
_HISTORY_MIN_LINES = 3
# Expected column count for history table rows
_HISTORY_COLUMNS = 4


@dataclass
class LinkData:
    """Represents a traceability link between items."""

    id: str
    source: str  # external_id of source item
    target: str  # external_id of target item
    link_type: str  # implements, tested_by, depends_on, blocks, relates_to
    created: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": self.link_type,
            "created": self.created.isoformat(),
            **({"metadata": self.metadata} if self.metadata else {}),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LinkData:
        """Create from dictionary parsed from YAML."""
        created = data["created"]
        if isinstance(created, str):
            created = datetime.fromisoformat(created)

        return cls(
            id=data["id"],
            source=data["source"],
            target=data["target"],
            link_type=data["type"],
            created=created,
            metadata=data.get("metadata", {}),
        )


@dataclass
class ItemData:
    """Represents a TraceRTM item (epic, story, test, task, wireframe) with metadata and content."""

    # YAML frontmatter fields
    id: str
    external_id: str
    item_type: str  # epic, story, test, task, wireframe
    status: str
    priority: str | None = None
    owner: str | None = None
    parent: str | None = None
    version: int = 1
    created: datetime | None = None
    updated: datetime | None = None
    tags: list[str] = field(default_factory=list)
    links: list[dict[str, str]] = field(default_factory=list)  # Inline links in frontmatter

    # Figma-specific fields (for wireframe type)
    figma_url: str | None = None
    figma_file_key: str | None = None
    figma_node_id: str | None = None
    components: list[str] = field(default_factory=list)
    screens: list[str] = field(default_factory=list)
    implements: list[str] = field(default_factory=list)  # Story/Epic IDs this wireframe implements

    # Markdown body content
    title: str = ""
    description: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    notes: str = ""
    history: list[dict[str, str]] = field(default_factory=list)

    # Additional metadata
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def to_frontmatter_dict(self) -> dict[str, Any]:
        """Convert metadata to frontmatter dictionary."""
        fm: dict[str, Any] = {
            "id": self.id,
            "external_id": self.external_id,
            "type": self.item_type,
            "status": self.status,
            "version": self.version,
        }

        if self.priority:
            fm["priority"] = self.priority
        if self.owner:
            fm["owner"] = self.owner
        if self.parent:
            fm["parent"] = self.parent
        if self.created:
            fm["created"] = self.created.isoformat()
        if self.updated:
            fm["updated"] = self.updated.isoformat()
        if self.tags:
            fm["tags"] = self.tags
        if self.links:
            fm["links"] = self.links

        # Figma-specific fields (for wireframe type)
        if self.figma_url:
            fm["figma_url"] = self.figma_url
        if self.figma_file_key:
            fm["figma_file_key"] = self.figma_file_key
        if self.figma_node_id:
            fm["figma_node_id"] = self.figma_node_id
        if self.components:
            fm["components"] = self.components
        if self.screens:
            fm["screens"] = self.screens
        if self.implements:
            fm["implements"] = self.implements

        # Add custom fields
        fm.update(self.custom_fields)

        return fm

    def to_markdown_body(self) -> str:
        """Convert content to Markdown body."""
        sections = []

        if self.title:
            sections.append(f"# {self.title}")

        # Description
        if self.description:
            sections.extend(("## Description\n", self.description))

        # Figma Preview (for wireframe type)
        if self.item_type == "wireframe" and self.figma_url:
            sections.append("## Figma Preview\n")
            if self.figma_file_key and self.figma_node_id:
                sections.extend((
                    f"![Figma Preview](figma://{self.figma_file_key}/{self.figma_node_id})",
                    f"\n[View in Figma]({self.figma_url})",
                ))
            else:
                sections.append(f"[View in Figma]({self.figma_url})")

        # Components Used (for wireframe type)
        if self.item_type == "wireframe" and self.components:
            sections.append("## Components Used\n")
            sections.extend(f"- {component}" for component in self.components)

        # Screens (for wireframe type)
        if self.item_type == "wireframe" and self.screens:
            sections.append("## Screens\n")
            sections.extend(f"- {screen}" for screen in self.screens)

        # Acceptance Criteria
        if self.acceptance_criteria:
            sections.append("## Acceptance Criteria\n")
            sections.extend(self.acceptance_criteria)

        # Notes
        if self.notes:
            sections.extend(("## Notes\n", self.notes))

        # History
        if self.history:
            sections.extend((
                "## History\n",
                "| Version | Date | Author | Changes |",
                "|---------|------|--------|---------|",
            ))
            sections.extend(
                f"| {entry.get('version', '')} | {entry.get('date', '')} | "
                f"{entry.get('author', '')} | {entry.get('changes', '')} |"
                for entry in self.history
            )

        return "\n\n".join(sections)

    @classmethod
    def from_frontmatter_and_body(cls, fm_data: dict[str, Any], body: str) -> ItemData:
        """Create ItemData from frontmatter dict and markdown body."""
        # Parse dates
        created = fm_data.get("created")
        if created and isinstance(created, str):
            created = datetime.fromisoformat(created)

        updated = fm_data.get("updated")
        if updated and isinstance(updated, str):
            updated = datetime.fromisoformat(updated)

        # Parse body sections
        title, description, acceptance_criteria, notes, history = _parse_markdown_body(body)

        # Extract known fields and put rest in custom_fields
        known_fields = {
            "id",
            "external_id",
            "type",
            "status",
            "priority",
            "owner",
            "parent",
            "version",
            "created",
            "updated",
            "tags",
            "links",
            # Figma-specific fields
            "figma_url",
            "figma_file_key",
            "figma_node_id",
            "components",
            "screens",
            "implements",
        }
        custom_fields = {k: v for k, v in fm_data.items() if k not in known_fields}

        return cls(
            id=fm_data["id"],
            external_id=fm_data["external_id"],
            item_type=fm_data["type"],
            status=fm_data["status"],
            priority=fm_data.get("priority"),
            owner=fm_data.get("owner"),
            parent=fm_data.get("parent"),
            version=fm_data.get("version", 1),
            created=created,
            updated=updated,
            tags=fm_data.get("tags", []),
            links=fm_data.get("links", []),
            # Figma-specific fields
            figma_url=fm_data.get("figma_url"),
            figma_file_key=fm_data.get("figma_file_key"),
            figma_node_id=fm_data.get("figma_node_id"),
            components=fm_data.get("components", []),
            screens=fm_data.get("screens", []),
            implements=fm_data.get("implements", []),
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            notes=notes,
            history=history,
            custom_fields=custom_fields,
        )


def parse_item_markdown(path: Path) -> ItemData:
    """Parse a Markdown file with YAML frontmatter into ItemData.

    Args:
        path: Path to the .md file

    Returns:
        ItemData object with parsed metadata and content

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    if not path.exists():
        msg = f"Item file not found: {path}"
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as f:
        content = f.read()

    # Parse frontmatter manually
    metadata, body = _parse_frontmatter(content)

    if not metadata:
        msg = f"No YAML frontmatter found in {path}"
        raise ValueError(msg)

    # Validate required fields
    required_fields = ["id", "external_id", "type", "status"]
    missing = [f for f in required_fields if f not in metadata]
    if missing:
        msg = f"Missing required frontmatter fields in {path}: {missing}"
        raise ValueError(msg)

    return ItemData.from_frontmatter_and_body(metadata, body)


def write_item_markdown(item: ItemData, path: Path) -> None:
    """Write ItemData to a Markdown file with YAML frontmatter.

    Args:
        item: ItemData object to write
        path: Path to write the .md file to

    Raises:
        ValueError: If required fields are missing
    """
    # Validate required fields
    if not all([item.id, item.external_id, item.item_type, item.status]):
        msg = "ItemData missing required fields (id, external_id, item_type, status)"
        raise ValueError(msg)

    # Create parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Build the content
    content = _build_frontmatter(item.to_frontmatter_dict(), item.to_markdown_body())

    # Write to file
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def parse_links_yaml(path: Path) -> list[LinkData]:
    """Parse .meta/links.yaml file into list of LinkData.

    Args:
        path: Path to links.yaml file

    Returns:
        List of LinkData objects

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the YAML format is invalid
    """
    if not path.exists():
        msg = f"Links file not found: {path}"
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "links" not in data:
        return []

    links = []
    for link_dict in data["links"]:
        try:
            links.append(LinkData.from_dict(link_dict))
        except (KeyError, ValueError) as e:
            msg = f"Invalid link format in {path}: {e}"
            raise ValueError(msg) from e

    return links


def write_links_yaml(links: list[LinkData], path: Path) -> None:
    """Write list of LinkData to .meta/links.yaml file.

    Args:
        links: List of LinkData objects
        path: Path to write links.yaml to
    """
    # Create parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert links to dict format
    data = {
        "links": [link.to_dict() for link in links],
    }

    # Write with comments
    header = """# Traceability links for the project
# Format optimized for both machine parsing and human readability
#
# Link types:
# - implements: Epic → Story, Story → Task
# - tested_by: Story/Task → Test
# - depends_on: object → Any
# - blocks: object → Any
# - relates_to: object → Any
# - wireframe_for: Wireframe → Story/Epic
# - designed_by: Component → Wireframe
# - implemented_in: Wireframe → Code file

"""

    with path.open("w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def parse_config_yaml(path: Path) -> dict[str, Any]:
    """Parse .meta/config.yaml for project settings.

    Args:
        path: Path to config.yaml file

    Returns:
        Dictionary of configuration settings

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not path.exists():
        msg = f"Config file not found: {path}"
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data or {}


def write_config_yaml(config: dict[str, Any], path: Path) -> None:
    """Write configuration dictionary to .meta/config.yaml.

    Args:
        config: Configuration dictionary
        path: Path to write config.yaml to
    """
    # Create parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _parse_markdown_body(body: str) -> tuple[str, str, list[str], str, list[dict[str, str]]]:
    """Parse markdown body into structured sections.

    Args:
        body: Raw markdown content

    Returns:
        Tuple of (title, description, acceptance_criteria, notes, history)
    """
    title = ""
    description = ""
    acceptance_criteria: list[str] = []
    notes = ""
    history: list[dict[str, str]] = []

    # Split by H2 sections
    sections = re.split(r"\n## ", body)

    # First section contains title (H1)
    if sections:
        first_section = sections[0].strip()
        title_match = re.match(r"^# (.+?)(?:\n|$)", first_section)
        if title_match:
            title = title_match.group(1).strip()

    # Parse remaining sections
    for section in sections[1:]:
        section = section.strip()  # noqa: PLW2901
        if not section:
            continue

        # Extract section name and content
        lines = section.split("\n", 1)
        section_name = lines[0].strip().lower()
        section_content = lines[1].strip() if len(lines) > 1 else ""

        if section_name == "description":
            description = section_content
        elif section_name == "acceptance criteria":
            # Parse checkbox items
            for line in section_content.split("\n"):
                line = line.strip()  # noqa: PLW2901
                if line.startswith(("- [", "* [")):
                    acceptance_criteria.append(line)
        elif section_name == "notes":
            notes = section_content
        elif section_name == "history":
            # Parse history table
            history = _parse_history_table(section_content)

    return title, description, acceptance_criteria, notes, history


def _parse_history_table(table_content: str) -> list[dict[str, str]]:
    """Parse markdown table into history entries.

    Args:
        table_content: Markdown table content

    Returns:
        List of history entry dictionaries
    """
    history: list[dict[str, str]] = []
    lines = [line.strip() for line in table_content.split("\n") if line.strip()]

    # Skip header and separator rows
    if len(lines) < _HISTORY_MIN_LINES:
        return history

    # Parse data rows (skip first 2 lines: header and separator)
    for line in lines[2:]:
        if not line.startswith("|"):
            continue

        # Split by | and clean up
        cells = [cell.strip() for cell in line.split("|")[1:-1]]

        if len(cells) >= _HISTORY_COLUMNS:
            history.append({
                "version": cells[0],
                "date": cells[1],
                "author": cells[2],
                "changes": cells[3],
            })

    return history


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content with frontmatter

    Returns:
        Tuple of (metadata dict, body string)
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    yaml_str = match.group(1)
    body = match.group(2).strip()

    try:
        metadata = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError as e:
        msg = f"Invalid YAML frontmatter: {e}"
        raise ValueError(msg) from e

    return metadata, body


def _build_frontmatter(metadata: dict[str, Any], body: str) -> str:
    """Build markdown content with YAML frontmatter.

    Args:
        metadata: Metadata dictionary
        body: Markdown body content

    Returns:
        Complete markdown string with frontmatter
    """
    # Convert metadata to YAML
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Build the complete content
    return f"---\n{yaml_str}---\n\n{body}\n"


def _pluralize_type(item_type: str) -> str:
    """Pluralize item type for directory naming.

    Args:
        item_type: Singular item type (epic, story, test, task, wireframe)

    Returns:
        Pluralized directory name (epics, stories, tests, tasks, wireframes)
    """
    # Handle special cases
    if item_type == "story":
        return "stories"

    # Default: add 's' if not already plural
    return f"{item_type}s" if not item_type.endswith("s") else item_type


def get_item_path(
    base_dir: Path,
    project_name: str,
    item_type: str,
    external_id: str,
) -> Path:
    """Get the file path for an item.

    Args:
        base_dir: Base directory for TraceRTM storage (e.g., ~/.tracertm)
        project_name: Name of the project
        item_type: Type of item (epic, story, test, task)
        external_id: External ID of the item (e.g., EPIC-001)

    Returns:
        Path to the item's markdown file
    """
    # Pluralize the type for directory name
    type_dir = _pluralize_type(item_type)

    return base_dir / "projects" / project_name / type_dir / f"{external_id}.md"


def get_links_path(base_dir: Path, project_name: str) -> Path:
    """Get the path to the links.yaml file.

    Args:
        base_dir: Base directory for TraceRTM storage
        project_name: Name of the project

    Returns:
        Path to links.yaml
    """
    return base_dir / "projects" / project_name / ".meta" / "links.yaml"


def get_config_path(base_dir: Path, project_name: str) -> Path:
    """Get the path to the config.yaml file.

    Args:
        base_dir: Base directory for TraceRTM storage
        project_name: Name of the project

    Returns:
        Path to config.yaml
    """
    return base_dir / "projects" / project_name / ".meta" / "config.yaml"


def list_items(base_dir: Path, project_name: str, item_type: str | None = None) -> list[Path]:
    """List all item markdown files in a project.

    Args:
        base_dir: Base directory for TraceRTM storage
        project_name: Name of the project
        item_type: Optional filter by item type (epic, story, test, task, wireframe)

    Returns:
        List of paths to markdown files
    """
    project_dir = base_dir / "projects" / project_name

    if not project_dir.exists():
        return []

    if item_type:
        type_dir = _pluralize_type(item_type)
        type_path = project_dir / type_dir
        if type_path.exists():
            return sorted(type_path.glob("*.md"))
        return []

    # List all items across all types
    all_items: list[Path] = []
    for item_type_name in ["epic", "story", "test", "task", "wireframe"]:
        type_dir = _pluralize_type(item_type_name)
        type_path = project_dir / type_dir
        if type_path.exists():
            all_items.extend(type_path.glob("*.md"))

    return sorted(all_items)
