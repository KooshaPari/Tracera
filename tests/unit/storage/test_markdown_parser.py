"""Unit tests for MarkdownParser.

Tests parsing and writing markdown files with YAML frontmatter
for various item types (epics, stories, tests, tasks).
"""

from datetime import UTC, datetime

# ============================================================================
# FIXTURES
# ============================================================================
from typing import Any

import pytest
import yaml

from tests.test_constants import COUNT_FOUR, COUNT_THREE, COUNT_TWO


@pytest.fixture
def temp_markdown_dir(tmp_path: Any) -> None:
    """Fixture: Temporary Markdown Directory.

    Provides: Clean directory for markdown files
    """
    md_dir = tmp_path / "markdown"
    md_dir.mkdir()
    return md_dir


@pytest.fixture
def sample_epic_markdown() -> str:
    """Sample epic markdown with frontmatter."""
    return """---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: "EPIC-001"
type: epic
status: in_progress
priority: high
owner: "@team-lead"
parent: null
version: 3
created: 2024-01-15T10:30:00Z
updated: 2024-01-20T14:22:00Z
tags:
  - authentication
  - security
  - mvp
links:
  - type: implements
    target: "STORY-001"
  - type: implements
    target: "STORY-002"
---

# User Authentication System

## Description

Implement a complete user authentication system supporting OAuth2, JWT tokens,
and session management.

## Acceptance Criteria

- [ ] Users can sign up with email/password
- [ ] OAuth2 integration with Google, GitHub
- [ ] JWT token refresh mechanism
- [ ] Session timeout after 24 hours
- [x] Password reset flow

## Notes

This epic covers all authentication-related functionality for the MVP release.

### Technical Considerations

- Use bcrypt for password hashing
- Store refresh tokens in Redis
- Implement rate limiting on auth endpoints

## History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3 | 2024-01-20 | @dev | Added OAuth requirements |
| 2 | 2024-01-18 | @pm | Updated acceptance criteria |
| 1 | 2024-01-15 | @pm | Initial creation |
"""


@pytest.fixture
def sample_story_markdown() -> str:
    """Sample story markdown with frontmatter."""
    return """---
id: "story-001"
external_id: "STORY-001"
type: story
status: todo
priority: medium
owner: "@developer"
parent: "EPIC-001"
version: 1
created: 2024-01-16T09:00:00Z
updated: 2024-01-16T09:00:00Z
tags:
  - authentication
  - api
---

# Implement User Registration API

## Description

Create REST API endpoint for user registration with email/password.

## Acceptance Criteria

- [ ] POST /api/auth/register endpoint
- [ ] Email validation
- [ ] Password strength requirements
- [ ] Return JWT token on success

## Technical Notes

Use bcrypt with cost factor 12 for password hashing.
"""


@pytest.fixture
def sample_test_markdown() -> str:
    """Sample test markdown with frontmatter."""
    return """---
id: "test-001"
external_id: "TEST-001"
type: test
status: passed
priority: high
owner: "@qa"
parent: "STORY-001"
version: 1
created: 2024-01-17T10:00:00Z
updated: 2024-01-17T15:00:00Z
tags:
  - integration
  - api
---

# Test User Registration with Valid Data

## Test Steps

1. Send POST request to /api/auth/register
2. Include valid email and password
3. Verify 201 Created response
4. Verify JWT token in response
5. Verify user exists in database

## Expected Result

User is created and JWT token is returned.
"""


# ============================================================================
# TEST CLASSES - Frontmatter Parsing
# ============================================================================


class TestMarkdownParserFrontmatter:
    """Test Suite: Markdown Parser - Frontmatter Parsing.

    Tests parsing YAML frontmatter from markdown files
    """

    @pytest.mark.unit
    def test_parse_epic_frontmatter(self, sample_epic_markdown: Any) -> None:
        """TC-MP.1.1: Parse Epic Frontmatter - Success.

        Given: Epic markdown with valid frontmatter
        When: Frontmatter is parsed
        Then: All metadata fields are extracted correctly
        """
        # Arrange
        content = sample_epic_markdown

        # Act
        parts = content.split("---", 2)
        assert len(parts) == COUNT_THREE
        frontmatter_text = parts[1].strip()
        frontmatter = yaml.safe_load(frontmatter_text)

        # Assert
        assert frontmatter["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert frontmatter["external_id"] == "EPIC-001"
        assert frontmatter["type"] == "epic"
        assert frontmatter["status"] == "in_progress"
        assert frontmatter["priority"] == "high"
        assert frontmatter["owner"] == "@team-lead"
        assert frontmatter["version"] == COUNT_THREE
        assert len(frontmatter["tags"]) == COUNT_THREE
        assert len(frontmatter["links"]) == COUNT_TWO

    @pytest.mark.unit
    def test_parse_story_frontmatter(self, sample_story_markdown: Any) -> None:
        """TC-MP.1.2: Parse Story Frontmatter - Success.

        Given: Story markdown with valid frontmatter
        When: Frontmatter is parsed
        Then: All metadata fields are extracted correctly
        """
        # Arrange
        content = sample_story_markdown

        # Act
        parts = content.split("---", 2)
        frontmatter_text = parts[1].strip()
        frontmatter = yaml.safe_load(frontmatter_text)

        # Assert
        assert frontmatter["external_id"] == "STORY-001"
        assert frontmatter["type"] == "story"
        assert frontmatter["parent"] == "EPIC-001"
        assert "authentication" in frontmatter["tags"]

    @pytest.mark.unit
    def test_parse_test_frontmatter(self, sample_test_markdown: Any) -> None:
        """TC-MP.1.3: Parse Test Frontmatter - Success.

        Given: Test markdown with valid frontmatter
        When: Frontmatter is parsed
        Then: All metadata fields are extracted correctly
        """
        # Arrange
        content = sample_test_markdown

        # Act
        parts = content.split("---", 2)
        frontmatter_text = parts[1].strip()
        frontmatter = yaml.safe_load(frontmatter_text)

        # Assert
        assert frontmatter["external_id"] == "TEST-001"
        assert frontmatter["type"] == "test"
        assert frontmatter["status"] == "passed"
        assert frontmatter["parent"] == "STORY-001"

    @pytest.mark.unit
    def test_extract_body_content(self, sample_epic_markdown: Any) -> None:
        """TC-MP.1.4: Extract Body Content - Success.

        Given: Markdown with frontmatter and body
        When: Body is extracted
        Then: Content without frontmatter is returned
        """
        # Arrange
        content = sample_epic_markdown

        # Act
        parts = content.split("---", 2)
        body = parts[2].strip()

        # Assert
        assert body.startswith("# User Authentication System")
        assert "## Description" in body
        assert "## Acceptance Criteria" in body
        assert "## History" in body

    @pytest.mark.unit
    def test_parse_empty_frontmatter(self) -> None:
        """TC-MP.1.5: Parse Empty Frontmatter - Graceful Handling.

        Given: Markdown with empty frontmatter
        When: Frontmatter is parsed
        Then: Empty dict or None is returned
        """
        # Arrange
        content = """---
---

# Content without metadata
"""

        # Act
        parts = content.split("---", 2)
        frontmatter_text = parts[1].strip()
        frontmatter = yaml.safe_load(frontmatter_text) if frontmatter_text else {}

        # Assert
        assert frontmatter == {} or frontmatter is None

    @pytest.mark.unit
    def test_parse_malformed_yaml(self) -> None:
        """TC-MP.1.6: Parse Malformed YAML - Error Handling.

        Given: Markdown with invalid YAML frontmatter
        When: Parsing is attempted
        Then: YAML error is raised
        """
        # Arrange
        content = """---
invalid: yaml: structure:
  - bad indent
---

# Content
"""

        # Act & Assert
        parts = content.split("---", 2)
        frontmatter_text = parts[1].strip()

        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(frontmatter_text)


# ============================================================================
# TEST CLASSES - Content Writing
# ============================================================================


class TestMarkdownParserWriting:
    """Test Suite: Markdown Parser - Content Writing.

    Tests writing markdown files with frontmatter
    """

    @pytest.mark.unit
    def test_write_epic_markdown(self, temp_markdown_dir: Any) -> None:
        """TC-MP.2.1: Write Epic Markdown - Success.

        Given: Epic metadata and content
        When: Markdown file is written
        Then: File contains valid frontmatter and body
        """
        # Arrange
        metadata = {
            "id": "epic-001",
            "external_id": "EPIC-001",
            "type": "epic",
            "status": "todo",
            "priority": "high",
            "version": 1,
            "created": datetime.now(UTC).isoformat(),
            "updated": datetime.now(UTC).isoformat(),
            "tags": ["auth", "security"],
        }
        body = "# Epic Title\n\nDescription here."

        # Act
        file_path = temp_markdown_dir / "EPIC-001.md"
        frontmatter_yaml = yaml.dump(metadata, default_flow_style=False)
        content = f"---\n{frontmatter_yaml}---\n\n{body}"
        file_path.write_text(content)

        # Assert
        assert file_path.exists()
        written_content = file_path.read_text()
        assert "---" in written_content
        assert "EPIC-001" in written_content
        assert "# Epic Title" in written_content

    @pytest.mark.unit
    def test_write_story_markdown(self, temp_markdown_dir: Any) -> None:
        """TC-MP.2.2: Write Story Markdown - Success.

        Given: Story metadata and content
        When: Markdown file is written
        Then: File is created with correct structure
        """
        # Arrange
        metadata = {
            "id": "story-001",
            "external_id": "STORY-001",
            "type": "story",
            "parent": "EPIC-001",
            "status": "in_progress",
            "version": 1,
        }
        body = "# Story Title\n\n## Details"

        # Act
        file_path = temp_markdown_dir / "STORY-001.md"
        frontmatter_yaml = yaml.dump(metadata, default_flow_style=False)
        content = f"---\n{frontmatter_yaml}---\n\n{body}"
        file_path.write_text(content)

        # Assert
        assert file_path.exists()
        parts = file_path.read_text().split("---", 2)
        assert len(parts) == COUNT_THREE
        parsed_metadata = yaml.safe_load(parts[1])
        assert parsed_metadata["parent"] == "EPIC-001"

    @pytest.mark.unit
    def test_update_existing_markdown(self, temp_markdown_dir: Any, sample_epic_markdown: Any) -> None:
        """TC-MP.2.3: Update Existing Markdown - Success.

        Given: Existing markdown file
        When: File is updated with new metadata
        Then: Version is incremented and content preserved
        """
        # Arrange
        file_path = temp_markdown_dir / "EPIC-001.md"
        file_path.write_text(sample_epic_markdown)

        # Act - Read, modify, write
        content = file_path.read_text()
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()

        # Update version
        frontmatter["version"] += 1
        frontmatter["status"] = "done"

        # Write back
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
        new_content = f"---\n{frontmatter_yaml}---\n\n{body}"
        file_path.write_text(new_content)

        # Assert
        updated_content = file_path.read_text()
        updated_parts = updated_content.split("---", 2)
        updated_frontmatter = yaml.safe_load(updated_parts[1])

        assert updated_frontmatter["version"] == COUNT_FOUR
        assert updated_frontmatter["status"] == "done"

    @pytest.mark.unit
    def test_preserve_content_formatting(self, temp_markdown_dir: Any) -> None:
        """TC-MP.2.4: Preserve Content Formatting - Success.

        Given: Markdown with specific formatting
        When: File is read and written
        Then: Formatting is preserved
        """
        # Arrange
        original_content = """---
id: test-001
type: test
---

# Test Title

## Section 1

- List item 1
- List item 2

## Section 2

```python
def test():
    pass
```

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
"""

        file_path = temp_markdown_dir / "test.md"
        file_path.write_text(original_content)

        # Act
        content = file_path.read_text()

        # Assert
        assert "```python" in content
        assert "| Column 1 | Column 2 |" in content
        assert "- List item 1" in content


# ============================================================================
# TEST CLASSES - Links Parsing
# ============================================================================


class TestMarkdownParserLinks:
    """Test Suite: Markdown Parser - Links Parsing.

    Tests parsing traceability links from frontmatter
    """

    @pytest.mark.unit
    def test_parse_implements_links(self, sample_epic_markdown: Any) -> None:
        """TC-MP.3.1: Parse Implements Links - Success.

        Given: Epic with implements links
        When: Links are parsed from frontmatter
        Then: Link targets are extracted
        """
        # Arrange
        content = sample_epic_markdown

        # Act
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        links = frontmatter.get("links", [])

        # Assert
        assert len(links) == COUNT_TWO
        assert links[0]["type"] == "implements"
        assert links[0]["target"] == "STORY-001"
        assert links[1]["target"] == "STORY-002"

    @pytest.mark.unit
    def test_parse_multiple_link_types(self) -> None:
        """TC-MP.3.2: Parse Multiple Link Types - Success.

        Given: Item with various link types
        When: Links are parsed
        Then: All link types are identified
        """
        # Arrange
        content = """---
id: story-001
links:
  - type: implements
    target: EPIC-001
  - type: tested_by
    target: TEST-001
  - type: depends_on
    target: STORY-002
  - type: blocks
    target: STORY-003
---

# Content
"""

        # Act
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        links = frontmatter["links"]

        # Assert
        link_types = [link["type"] for link in links]
        assert "implements" in link_types
        assert "tested_by" in link_types
        assert "depends_on" in link_types
        assert "blocks" in link_types

    @pytest.mark.unit
    def test_parse_no_links(self) -> None:
        """TC-MP.3.3: Parse No Links - Graceful Handling.

        Given: Item without links
        When: Links are parsed
        Then: Empty list is returned
        """
        # Arrange
        content = """---
id: story-001
type: story
---

# Content
"""

        # Act
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        links = frontmatter.get("links", [])

        # Assert
        assert links == []


# ============================================================================
# TEST CLASSES - Tags Parsing
# ============================================================================


class TestMarkdownParserTags:
    """Test Suite: Markdown Parser - Tags Parsing.

    Tests parsing tags from frontmatter
    """

    @pytest.mark.unit
    def test_parse_tags_list(self, sample_epic_markdown: Any) -> None:
        """TC-MP.4.1: Parse Tags List - Success.

        Given: Item with tags
        When: Tags are parsed
        Then: All tags are extracted
        """
        # Arrange
        content = sample_epic_markdown

        # Act
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        tags = frontmatter.get("tags", [])

        # Assert
        assert len(tags) == COUNT_THREE
        assert "authentication" in tags
        assert "security" in tags
        assert "mvp" in tags

    @pytest.mark.unit
    def test_parse_empty_tags(self) -> None:
        """TC-MP.4.2: Parse Empty Tags - Graceful Handling.

        Given: Item without tags
        When: Tags are parsed
        Then: Empty list is returned
        """
        # Arrange
        content = """---
id: item-001
type: story
---

# Content
"""

        # Act
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        tags = frontmatter.get("tags", [])

        # Assert
        assert tags == []

    @pytest.mark.unit
    def test_write_tags(self, temp_markdown_dir: Any) -> None:
        """TC-MP.4.3: Write Tags - Success.

        Given: Item metadata with tags
        When: Markdown is written
        Then: Tags are formatted as YAML list
        """
        # Arrange
        metadata = {"id": "item-001", "type": "epic", "tags": ["tag1", "tag2", "tag3"]}
        body = "# Content"

        # Act
        file_path = temp_markdown_dir / "item.md"
        frontmatter_yaml = yaml.dump(metadata, default_flow_style=False)
        content = f"---\n{frontmatter_yaml}---\n\n{body}"
        file_path.write_text(content)

        # Assert
        written_content = file_path.read_text()
        assert "tags:" in written_content
        assert "- tag1" in written_content
        assert "- tag2" in written_content


# ============================================================================
# TEST CLASSES - Content Extraction
# ============================================================================


class TestMarkdownParserContentExtraction:
    """Test Suite: Markdown Parser - Content Extraction.

    Tests extracting specific sections from markdown
    """

    @pytest.mark.unit
    def test_extract_acceptance_criteria(self, sample_epic_markdown: Any) -> None:
        """TC-MP.5.1: Extract Acceptance Criteria - Success.

        Given: Epic with acceptance criteria section
        When: Section is extracted
        Then: Criteria list is returned
        """
        # Arrange
        content = sample_epic_markdown

        # Act
        parts = content.split("---", 2)
        body = parts[2]

        # Simple extraction (in real implementation, use proper markdown parser)
        criteria_section = body.split("## Acceptance Criteria")[1].split("##")[0]

        # Assert
        assert "Users can sign up with email/password" in criteria_section
        assert "OAuth2 integration" in criteria_section
        assert "[x] Password reset flow" in criteria_section

    @pytest.mark.unit
    def test_extract_description(self, sample_epic_markdown: Any) -> None:
        """TC-MP.5.2: Extract Description Section - Success.

        Given: Markdown with description section
        When: Description is extracted
        Then: Section text is returned
        """
        # Arrange
        content = sample_epic_markdown

        # Act
        parts = content.split("---", 2)
        body = parts[2]
        description_section = body.split("## Description")[1].split("##")[0].strip()

        # Assert
        assert "authentication system" in description_section
        assert "OAuth2" in description_section

    @pytest.mark.unit
    def test_extract_technical_notes(self, sample_story_markdown: Any) -> None:
        """TC-MP.5.3: Extract Technical Notes - Success.

        Given: Story with technical notes
        When: Notes are extracted
        Then: Technical details are returned
        """
        # Arrange
        content = sample_story_markdown

        # Act
        parts = content.split("---", 2)
        body = parts[2]

        # Assert
        assert "bcrypt" in body
        assert "cost factor 12" in body


# ============================================================================
# TEST CLASSES - Error Handling
# ============================================================================


class TestMarkdownParserErrorHandling:
    """Test Suite: Markdown Parser - Error Handling.

    Tests handling of invalid or malformed markdown
    """

    @pytest.mark.unit
    def test_missing_frontmatter_delimiters(self) -> None:
        """TC-MP.6.1: Missing Frontmatter Delimiters - Error Detection.

        Given: Markdown without proper --- delimiters
        When: Parsing is attempted
        Then: Error is detected
        """
        # Arrange
        content = """
id: test-001

# Content without frontmatter
"""

        # Act
        parts = content.split("---", 2)

        # Assert
        # Should not have proper frontmatter structure
        assert len(parts) < COUNT_THREE

    @pytest.mark.unit
    def test_invalid_yaml_syntax(self) -> None:
        """TC-MP.6.2: Invalid YAML Syntax - Error Handling.

        Given: Frontmatter with invalid YAML
        When: Parsing is attempted
        Then: YAML error is raised
        """
        # Arrange
        content = """---
id: test-001
invalid yaml structure
  - missing colon
---

# Content
"""

        # Act & Assert
        parts = content.split("---", 2)
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(parts[1])

    @pytest.mark.unit
    def test_missing_required_fields(self) -> None:
        """TC-MP.6.3: Missing Required Fields - Validation.

        Given: Frontmatter without required fields
        When: Metadata is validated
        Then: Missing fields are detected
        """
        # Arrange
        content = """---
id: test-001
---

# Content
"""

        # Act
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        # Assert
        assert "id" in frontmatter
        assert "type" not in frontmatter  # Missing required field
        assert "status" not in frontmatter  # Missing required field


# ============================================================================
# NOTES
# ============================================================================

"""
COVERAGE AREAS:

1. Frontmatter Parsing:
   - Epic, Story, Test formats
   - Metadata extraction
   - Body content separation
   - Error handling

2. Content Writing:
   - Create new markdown files
   - Update existing files
   - Version tracking
   - Format preservation

3. Links Parsing:
   - Various link types
   - Multiple links
   - Empty links

4. Tags Parsing:
   - Tag lists
   - Empty tags
   - Tag formatting

5. Content Extraction:
   - Acceptance criteria
   - Descriptions
   - Technical notes

6. Error Handling:
   - Malformed YAML
   - Missing delimiters
   - Invalid syntax
   - Field validation

TODO for full implementation:
- Add MarkdownParser class tests (when implemented)
- Add markdown-to-dict conversion tests
- Add dict-to-markdown conversion tests
- Add checksum/hash generation tests
- Add multi-file parsing tests
"""
