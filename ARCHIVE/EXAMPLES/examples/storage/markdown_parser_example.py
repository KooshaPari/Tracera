#!/usr/bin/env python3
"""Example usage of the TraceRTM Markdown parser.

This example demonstrates:
1. Creating and writing ItemData (epics, stories, tests, tasks)
2. Parsing existing markdown files
3. Managing traceability links
4. Working with project configuration

Run this example:
    python examples/storage/markdown_parser_example.py
"""

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

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


def example_create_epic() -> ItemData:
    """Create an epic item."""
    return ItemData(
        id="550e8400-e29b-41d4-a716-446655440000",
        external_id="EPIC-001",
        item_type="epic",
        status="in_progress",
        priority="high",
        owner="@team-lead",
        version=1,
        created=datetime(2024, 1, 15, 10, 30, 0),
        updated=datetime(2024, 1, 20, 14, 22, 0),
        tags=["authentication", "security", "mvp"],
        title="User Authentication System",
        description="""Implement a complete user authentication system supporting OAuth2, JWT tokens,
and session management.

This epic covers all authentication-related functionality for the MVP release.""",
        acceptance_criteria=[
            "- [ ] Users can sign up with email/password",
            "- [ ] OAuth2 integration with Google, GitHub",
            "- [ ] JWT token refresh mechanism",
            "- [ ] Session timeout after 24 hours",
            "- [x] Password reset flow",
        ],
        notes="""### Technical Considerations

- Use bcrypt for password hashing
- Store refresh tokens in Redis
- Implement rate limiting on auth endpoints""",
        history=[
            {"version": "3", "date": "2024-01-20", "author": "@dev", "changes": "Added OAuth requirements"},
            {"version": "2", "date": "2024-01-18", "author": "@pm", "changes": "Updated acceptance criteria"},
            {"version": "1", "date": "2024-01-15", "author": "@pm", "changes": "Initial creation"},
        ],
    )


def example_create_story() -> ItemData:
    """Create a story item."""
    return ItemData(
        id="660e8400-e29b-41d4-a716-446655440001",
        external_id="STORY-001",
        item_type="story",
        status="todo",
        priority="high",
        owner="@developer",
        parent="EPIC-001",
        version=1,
        created=datetime(2024, 1, 16, 9, 0, 0),
        updated=datetime(2024, 1, 16, 9, 0, 0),
        tags=["authentication", "backend"],
        title="Implement JWT token generation and validation",
        description="Create JWT token generation and validation logic for user authentication.",
        acceptance_criteria=[
            "- [ ] Generate JWT tokens on successful login",
            "- [ ] Validate JWT tokens on protected endpoints",
            "- [ ] Handle token expiration gracefully",
            "- [ ] Include user roles in token claims",
        ],
        notes="Use PyJWT library for token handling.",
    )


def example_create_test() -> ItemData:
    """Create a test item."""
    return ItemData(
        id="770e8400-e29b-41d4-a716-446655440002",
        external_id="TEST-001",
        item_type="test",
        status="draft",
        priority="medium",
        owner="@qa-engineer",
        version=1,
        created=datetime(2024, 1, 17, 11, 0, 0),
        updated=datetime(2024, 1, 17, 11, 0, 0),
        tags=["authentication", "integration"],
        title="Test JWT token lifecycle",
        description="Integration test for JWT token generation, validation, and expiration.",
        acceptance_criteria=[
            "- [ ] Test token generation with valid credentials",
            "- [ ] Test token validation on protected routes",
            "- [ ] Test token expiration handling",
            "- [ ] Test invalid token rejection",
        ],
    )


def example_create_links() -> list[LinkData]:
    """Create traceability links."""
    return [
        LinkData(
            id="link-001",
            source="EPIC-001",
            target="STORY-001",
            link_type="implements",
            created=datetime(2024, 1, 16, 9, 0, 0),
        ),
        LinkData(
            id="link-002",
            source="STORY-001",
            target="TEST-001",
            link_type="tested_by",
            created=datetime(2024, 1, 17, 11, 0, 0),
        ),
    ]


def main() -> None:
    """Run the example."""
    print("TraceRTM Markdown Parser Example")
    print("=" * 60)
    print()

    # Use temporary directory for demo
    with TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        project_name = "demo-project"

        print(f"Working directory: {base_dir}")
        print()

        # 1. Create and write items
        print("1. Creating and writing items...")
        print("-" * 60)

        epic = example_create_epic()
        epic_path = get_item_path(base_dir, project_name, "epic", epic.external_id)
        write_item_markdown(epic, epic_path)
        print(f"✓ Written epic to: {epic_path}")

        story = example_create_story()
        story_path = get_item_path(base_dir, project_name, "story", story.external_id)
        write_item_markdown(story, story_path)
        print(f"✓ Written story to: {story_path}")

        test = example_create_test()
        test_path = get_item_path(base_dir, project_name, "test", test.external_id)
        write_item_markdown(test, test_path)
        print(f"✓ Written test to: {test_path}")
        print()

        # 2. Create and write links
        print("2. Creating traceability links...")
        print("-" * 60)

        links = example_create_links()
        links_path = get_links_path(base_dir, project_name)
        write_links_yaml(links, links_path)
        print(f"✓ Written {len(links)} links to: {links_path}")
        print()

        # 3. Create project configuration
        print("3. Creating project configuration...")
        print("-" * 60)

        config = {
            "project": {
                "name": project_name,
                "version": "1.0.0",
                "description": "Demo project for TraceRTM",
            },
            "settings": {
                "auto_sync": True,
                "conflict_strategy": "last_write_wins",
            },
            "agents": {
                "enabled": ["pm", "dev", "qa"],
            },
        }

        config_path = get_config_path(base_dir, project_name)
        write_config_yaml(config, config_path)
        print(f"✓ Written config to: {config_path}")
        print()

        # 4. Parse items back
        print("4. Parsing items back from files...")
        print("-" * 60)

        parsed_epic = parse_item_markdown(epic_path)
        print(f"✓ Parsed epic: {parsed_epic.external_id} - {parsed_epic.title}")
        print(f"  Status: {parsed_epic.status}, Priority: {parsed_epic.priority}")
        print(f"  Tags: {', '.join(parsed_epic.tags)}")
        print(f"  Acceptance criteria: {len(parsed_epic.acceptance_criteria)} items")

        parsed_story = parse_item_markdown(story_path)
        print(f"✓ Parsed story: {parsed_story.external_id} - {parsed_story.title}")
        print(f"  Parent: {parsed_story.parent}")
        print()

        # 5. Parse links
        print("5. Parsing traceability links...")
        print("-" * 60)

        parsed_links = parse_links_yaml(links_path)
        for link in parsed_links:
            print(f"✓ {link.source} --[{link.link_type}]--> {link.target}")
        print()

        # 6. Parse config
        print("6. Parsing project configuration...")
        print("-" * 60)

        parsed_config = parse_config_yaml(config_path)
        print(f"✓ Project: {parsed_config['project']['name']}")
        print(f"✓ Auto-sync: {parsed_config['settings']['auto_sync']}")
        print(f"✓ Enabled agents: {', '.join(parsed_config['agents']['enabled'])}")
        print()

        # 7. List all items
        print("7. Listing all items in project...")
        print("-" * 60)

        all_items = list_items(base_dir, project_name)
        print(f"✓ Found {len(all_items)} total items:")
        for item_path in all_items:
            print(f"  - {item_path.relative_to(base_dir)}")

        # List by type
        epics = list_items(base_dir, project_name, "epic")
        stories = list_items(base_dir, project_name, "story")
        tests = list_items(base_dir, project_name, "test")
        print(f"✓ By type: {len(epics)} epics, {len(stories)} stories, {len(tests)} tests")
        print()

        # 8. Display example file content
        print("8. Example markdown file content:")
        print("=" * 60)
        with open(epic_path) as f:
            print(f.read())
        print("=" * 60)
        print()

        print("Example completed successfully!")


if __name__ == "__main__":
    main()
