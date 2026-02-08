"""Edge case tests for markdown_parser.py.

Tests cover:
- Malformed YAML frontmatter
- Missing link references
- Unicode and special characters
- Very long content
- Nested markdown structures
- Invalid frontmatter types
- Empty and boundary conditions
"""

from datetime import datetime
from pathlib import Path

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    get_config_path,
    get_item_path,
    get_links_path,
    list_items,
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
    write_config_yaml,
    write_item_markdown,
    write_links_yaml,
)


class TestMarkdownParserEdgeCases:
    """Test edge cases in markdown parsing."""

    def test_parse_malformed_yaml_frontmatter(self, tmp_path: Path) -> None:
        """Test parsing with malformed YAML frontmatter."""
        md_file = tmp_path / "malformed.md"

        # Invalid YAML syntax
        md_file.write_text(
            """---
id: test-1
type: epic
status: todo
broken: [unclosed bracket
---
# Title
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="Invalid YAML frontmatter"):
            parse_item_markdown(md_file)

    def test_parse_missing_required_fields(self, tmp_path: Path) -> None:
        """Test parsing with missing required frontmatter fields."""
        md_file = tmp_path / "missing_fields.md"

        # Missing 'status' field
        md_file.write_text(
            """---
id: test-1
external_id: TEST-001
type: epic
---
# Title
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="Missing required frontmatter fields"):
            parse_item_markdown(md_file)

    def test_parse_missing_frontmatter_entirely(self, tmp_path: Path) -> None:
        """Test parsing file with no frontmatter."""
        md_file = tmp_path / "no_frontmatter.md"

        md_file.write_text("# Just a title\n\nSome content", encoding="utf-8")

        with pytest.raises(ValueError, match="No YAML frontmatter found"):
            parse_item_markdown(md_file)

    def test_parse_unicode_characters(self, tmp_path: Path) -> None:
        """Test parsing with various Unicode characters."""
        md_file = tmp_path / "unicode.md"

        # Unicode in frontmatter and body
        md_file.write_text(
            """---
id: test-unicode
external_id: UNICODE-001
type: epic
status: todo
priority: high
owner: 用户 👤
tags:
  - 标签
  - émoji 🎉
  - עברית
---
# Unicode Title 🚀

## Description

This contains unicode: 日本語, العربية, Ελληνικά
Emoji: 🔥 💯 ✨

## Notes

RTL text: مرحبا بك
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert item.owner == "用户 👤"
        assert "标签" in item.tags
        assert "🚀" in item.title

    def test_parse_very_long_content(self, tmp_path: Path) -> None:
        """Test parsing of very long documents."""
        md_file = tmp_path / "long.md"

        # Generate long description (10,000 lines)
        long_description = "\n".join([f"Line {i} of content" for i in range(10000)])

        md_file.write_text(
            f"""---
id: test-long
external_id: LONG-001
type: epic
status: todo
---
# Long Document

## Description

{long_description}
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert "Line 9999" in item.description

    def test_parse_nested_markdown_structures(self, tmp_path: Path) -> None:
        """Test deeply nested markdown structures."""
        md_file = tmp_path / "nested.md"

        md_file.write_text(
            """---
id: test-nested
external_id: NESTED-001
type: epic
status: todo
---
# Title

## Description

- Level 1
  - Level 2
    - Level 3
      - Level 4
        - Level 5

> Blockquote
> > Nested blockquote
> > > Triple nested

| Col1 | Col2 |
|------|------|
| Cell | Cell |
| With | Pipe \\| |

```python
def nested():
    if True:
        if True:
            if True:
                return "deep"
```
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert "Level 5" in item.description
        assert "Triple nested" in item.description

    def test_parse_invalid_frontmatter_types(self, tmp_path: Path) -> None:
        """Test frontmatter with invalid field types."""
        md_file = tmp_path / "invalid_types.md"

        # Tags as string instead of list, created as int
        md_file.write_text(
            """---
id: test-types
external_id: TYPES-001
type: epic
status: todo
tags: not_a_list
created: 12345
---
# Title
""",
            encoding="utf-8",
        )

        # Should handle gracefully or raise clear error
        item = parse_item_markdown(md_file)
        assert item.tags == "not_a_list"  # Will be stored as-is
        assert item.created == 12345  # Will be stored as-is

    def test_parse_empty_frontmatter_values(self, tmp_path: Path) -> None:
        """Test parsing with empty/null frontmatter values."""
        md_file = tmp_path / "empty.md"

        md_file.write_text(
            """---
id: test-empty
external_id: EMPTY-001
type: epic
status: todo
priority: null
owner:
tags: []
---
# Title

## Description


## Notes

""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert item.priority is None
        assert item.owner is None or item.owner == ""  # Could be None or empty
        assert item.tags == []
        assert item.description == ""
        assert item.notes == ""

    def test_parse_acceptance_criteria_formats(self, tmp_path: Path) -> None:
        """Test parsing different acceptance criteria formats."""
        md_file = tmp_path / "criteria.md"

        md_file.write_text(
            """---
id: test-ac
external_id: AC-001
type: story
status: todo
---
# Title

## Acceptance Criteria

- [ ] Unchecked item
- [x] Checked item
- [-] Partial item
* [ ] Asterisk format
* [x] Asterisk checked

Not a checkbox item
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        # Should capture checkbox items
        assert len(item.acceptance_criteria) >= COUNT_FOUR
        assert any("Unchecked" in ac for ac in item.acceptance_criteria)

    def test_parse_history_table_variations(self, tmp_path: Path) -> None:
        """Test parsing history tables with variations."""
        md_file = tmp_path / "history.md"

        md_file.write_text(
            """---
id: test-hist
external_id: HIST-001
type: epic
status: todo
---
# Title

## History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1 | 2024-01-01 | Alice | Initial |
| 2 | 2024-01-02 | Bob | Updated with pipes \\| in text |
| 3 | 2024-01-03 | | Empty author |
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert len(item.history) == COUNT_THREE
        assert item.history[0]["version"] == "1"
        # Table parsing may preserve escaped pipes
        assert "pipes" in item.history[1]["changes"]
        assert item.history[2]["author"] == ""

    def test_parse_figma_wireframe_fields(self, tmp_path: Path) -> None:
        """Test parsing wireframe with Figma-specific fields."""
        md_file = tmp_path / "wireframe.md"

        md_file.write_text(
            """---
id: wf-001
external_id: WF-001
type: wireframe
status: todo
figma_url: https://figma.com/file/abc/design
figma_file_key: abc123
figma_node_id: 1:2
components:
  - Button
  - Input
screens:
  - Login
  - Dashboard
implements:
  - STORY-001
  - STORY-002
---
# Login Screen

## Description

Wireframe for login page
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert item.item_type == "wireframe"
        assert item.figma_url == "https://figma.com/file/abc/design"
        assert "Button" in item.components
        assert "Login" in item.screens
        assert "STORY-001" in item.implements

    def test_write_and_read_roundtrip(self, tmp_path: Path) -> None:
        """Test that writing and reading preserves data."""
        md_file = tmp_path / "roundtrip.md"

        original = ItemData(
            id="test-roundtrip",
            external_id="RT-001",
            item_type="epic",
            status="in_progress",
            priority="high",
            owner="Alice",
            parent="PARENT-001",
            version=2,
            created=datetime(2024, 1, 1, 12, 0, 0),
            updated=datetime(2024, 1, 2, 14, 30, 0),
            tags=["important", "urgent"],
            title="Test Title",
            description="Test Description\nMultiple lines",
            acceptance_criteria=["- [ ] Criterion 1", "- [ ] Criterion 2"],
            notes="Some notes",
        )

        write_item_markdown(original, md_file)
        parsed = parse_item_markdown(md_file)

        assert parsed.id == original.id
        assert parsed.external_id == original.external_id
        assert parsed.item_type == original.item_type
        assert parsed.status == original.status
        assert parsed.priority == original.priority
        assert parsed.owner == original.owner
        assert parsed.title == original.title

    def test_write_item_missing_required_fields(self, tmp_path: Path) -> None:
        """Test writing item with missing required fields."""
        md_file = tmp_path / "missing.md"

        item = ItemData(
            id="",  # Missing
            external_id="",  # Missing
            item_type="",  # Missing
            status="",  # Missing
        )

        with pytest.raises(ValueError, match="missing required fields"):
            write_item_markdown(item, md_file)

    def test_parse_links_yaml_empty(self, tmp_path: Path) -> None:
        """Test parsing empty links.yaml."""
        links_file = tmp_path / "links.yaml"
        links_file.write_text("links: []\n", encoding="utf-8")

        links = parse_links_yaml(links_file)
        assert links == []

    def test_parse_links_yaml_invalid_format(self, tmp_path: Path) -> None:
        """Test parsing links.yaml with invalid format."""
        links_file = tmp_path / "links.yaml"

        # Missing required fields
        links_file.write_text(
            """links:
  - id: link-1
    source: EPIC-001
    # Missing target and type
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="Invalid link format"):
            parse_links_yaml(links_file)

    def test_parse_config_yaml_empty(self, tmp_path: Path) -> None:
        """Test parsing empty config.yaml."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        config = parse_config_yaml(config_file)
        assert config == {}

    def test_parse_config_yaml_complex(self, tmp_path: Path) -> None:
        """Test parsing complex config.yaml."""
        config_file = tmp_path / "config.yaml"

        config_file.write_text(
            """name: Test Project
description: A complex project
settings:
  auto_link: true
  priorities:
    - low
    - medium
    - high
team:
  - name: Alice
    role: developer
  - name: Bob
    role: tester
counters:
  epic: 5
  story: 23
""",
            encoding="utf-8",
        )

        config = parse_config_yaml(config_file)
        assert config["name"] == "Test Project"
        assert config["settings"]["auto_link"] is True
        assert len(config["team"]) == COUNT_TWO
        assert config["counters"]["epic"] == COUNT_FIVE

    def test_link_data_to_dict_and_from_dict(self) -> None:
        """Test LinkData serialization roundtrip."""
        original = LinkData(
            id="link-1",
            source="EPIC-001",
            target="STORY-001",
            link_type="implements",
            created=datetime(2024, 1, 1, 12, 0, 0),
            metadata={"key": "value"},
        )

        data = original.to_dict()
        parsed = LinkData.from_dict(data)

        assert parsed.id == original.id
        assert parsed.source == original.source
        assert parsed.target == original.target
        assert parsed.link_type == original.link_type
        assert parsed.metadata == original.metadata

    def test_link_data_from_dict_with_string_date(self) -> None:
        """Test LinkData parsing with ISO date string."""
        data = {
            "id": "link-1",
            "source": "EPIC-001",
            "target": "STORY-001",
            "type": "implements",
            "created": "2024-01-01T12:00:00Z",
        }

        link = LinkData.from_dict(data)
        assert isinstance(link.created, datetime)

    def test_get_item_path_various_types(self, tmp_path: Path) -> None:
        """Test get_item_path for different item types."""
        base_dir = tmp_path

        # Test epic
        path = get_item_path(base_dir, "MyProject", "epic", "EPIC-001")
        assert path == base_dir / "projects" / "MyProject" / "epics" / "EPIC-001.md"

        # Test story (should pluralize to 'stories')
        path = get_item_path(base_dir, "MyProject", "story", "STORY-001")
        assert path == base_dir / "projects" / "MyProject" / "stories" / "STORY-001.md"

        # Test wireframe
        path = get_item_path(base_dir, "MyProject", "wireframe", "WF-001")
        assert path == base_dir / "projects" / "MyProject" / "wireframes" / "WF-001.md"

    def test_get_links_path(self, tmp_path: Path) -> None:
        """Test get_links_path."""
        path = get_links_path(tmp_path, "MyProject")
        assert path == tmp_path / "projects" / "MyProject" / ".meta" / "links.yaml"

    def test_get_config_path(self, tmp_path: Path) -> None:
        """Test get_config_path."""
        path = get_config_path(tmp_path, "MyProject")
        assert path == tmp_path / "projects" / "MyProject" / ".meta" / "config.yaml"

    def test_list_items_nonexistent_project(self, tmp_path: Path) -> None:
        """Test list_items with non-existent project."""
        items = list_items(tmp_path, "NonExistent")
        assert items == []

    def test_list_items_empty_project(self, tmp_path: Path) -> None:
        """Test list_items with empty project."""
        project_dir = tmp_path / "projects" / "EmptyProject"
        project_dir.mkdir(parents=True)

        items = list_items(tmp_path, "EmptyProject")
        assert items == []

    def test_list_items_with_type_filter(self, tmp_path: Path) -> None:
        """Test list_items with item type filter."""
        project_dir = tmp_path / "projects" / "TestProject"
        epics_dir = project_dir / "epics"
        stories_dir = project_dir / "stories"
        epics_dir.mkdir(parents=True)
        stories_dir.mkdir(parents=True)

        # Create test files
        (epics_dir / "EPIC-001.md").write_text("# Epic 1")
        (epics_dir / "EPIC-002.md").write_text("# Epic 2")
        (stories_dir / "STORY-001.md").write_text("# Story 1")

        # List all
        all_items = list_items(tmp_path, "TestProject")
        assert len(all_items) == COUNT_THREE

        # List only epics
        epics = list_items(tmp_path, "TestProject", item_type="epic")
        assert len(epics) == COUNT_TWO
        assert all("EPIC" in p.name for p in epics)

        # List only stories
        stories = list_items(tmp_path, "TestProject", item_type="story")
        assert len(stories) == 1
        assert "STORY" in stories[0].name

    def test_item_data_to_markdown_body_with_figma(self) -> None:
        """Test ItemData.to_markdown_body with Figma fields."""
        item = ItemData(
            id="wf-1",
            external_id="WF-001",
            item_type="wireframe",
            status="todo",
            title="Login Page",
            description="Login wireframe",
            figma_url="https://figma.com/abc",
            figma_file_key="abc123",
            figma_node_id="1:2",
            components=["Button", "Input"],
            screens=["Login"],
        )

        md_body = item.to_markdown_body()

        assert "# Login Page" in md_body
        assert "## Figma Preview" in md_body
        assert "figma://abc123/1:2" in md_body
        assert "## Components Used" in md_body
        assert "- Button" in md_body
        assert "## Screens" in md_body
        assert "- Login" in md_body

    def test_parse_file_not_found(self, tmp_path: Path) -> None:
        """Test parsing non-existent file."""
        md_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parse_item_markdown(md_file)

    def test_parse_links_file_not_found(self, tmp_path: Path) -> None:
        """Test parsing non-existent links.yaml."""
        links_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            parse_links_yaml(links_file)

    def test_parse_config_file_not_found(self, tmp_path: Path) -> None:
        """Test parsing non-existent config.yaml."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            parse_config_yaml(config_file)

    def test_write_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that write functions create parent directories."""
        # Test write_item_markdown
        deep_path = tmp_path / "a" / "b" / "c" / "item.md"
        item = ItemData(
            id="test",
            external_id="TEST-001",
            item_type="epic",
            status="todo",
            title="Test",
        )
        write_item_markdown(item, deep_path)
        assert deep_path.exists()

        # Test write_links_yaml
        links_path = tmp_path / "x" / "y" / "z" / "links.yaml"
        write_links_yaml([], links_path)
        assert links_path.exists()

        # Test write_config_yaml
        config_path = tmp_path / "p" / "q" / "r" / "config.yaml"
        write_config_yaml({"test": "value"}, config_path)
        assert config_path.exists()

    def test_special_characters_in_markdown(self, tmp_path: Path) -> None:
        """Test handling special markdown characters."""
        md_file = tmp_path / "special.md"

        md_file.write_text(
            """---
id: special
external_id: SPECIAL-001
type: epic
status: todo
---
# Title with *asterisks* and _underscores_

## Description

Text with `backticks` and **bold** and ***bold italic***

Links: [text](url) and ![image](url)

Inline code: `code` and code block:

```
block
```

Escapes: \\* \\_ \\` \\[
""",
            encoding="utf-8",
        )

        item = parse_item_markdown(md_file)
        assert "*asterisks*" in item.title
        assert "backticks" in item.description
        assert "\\*" in item.description  # Escaped characters preserved
