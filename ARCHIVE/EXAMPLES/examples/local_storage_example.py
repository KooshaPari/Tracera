"""
Example usage of LocalStorageManager for TraceRTM.

This demonstrates the hybrid SQLite + Markdown storage system.
"""

from pathlib import Path

from tracertm.storage import LocalStorageManager


def main():
    """Demonstrate LocalStorageManager usage."""
    # Initialize storage (uses ~/.tracertm by default)
    # For this example, use a temporary directory
    storage_dir = Path.home() / ".tracertm_example"
    storage_dir.mkdir(exist_ok=True)

    manager = LocalStorageManager(base_dir=storage_dir)
    print(f"✓ Initialized storage at {storage_dir}")

    # Create a project
    project_storage = manager.get_project_storage("my-app")
    project = project_storage.create_or_update_project(
        name="my-app",
        description="My awesome application",
        metadata={"version": "1.0", "team": "Engineering"},
    )
    print(f"✓ Created project: {project.name} (ID: {project.id})")

    # Get item storage for the project
    item_storage = project_storage.get_item_storage(project)

    # Create an epic
    epic = item_storage.create_item(
        title="User Authentication System",
        item_type="epic",
        external_id="EPIC-001",
        description="Implement complete user authentication with OAuth2 and JWT",
        status="in_progress",
        priority="high",
        owner="@auth-team",
        metadata={"tags": ["security", "auth", "mvp"]},
    )
    print(f"✓ Created epic: {epic.title} ({epic.item_metadata.get('external_id')})")

    # Create stories under the epic
    story1 = item_storage.create_item(
        title="User Registration",
        item_type="story",
        external_id="STORY-001",
        description="As a user, I want to register with email and password",
        status="todo",
        priority="high",
        parent_id=epic.id,
        metadata={"tags": ["registration"]},
    )
    print(f"✓ Created story: {story1.title} ({story1.item_metadata.get('external_id')})")

    story2 = item_storage.create_item(
        title="OAuth2 Login",
        item_type="story",
        external_id="STORY-002",
        description="As a user, I want to login with Google/GitHub OAuth",
        status="todo",
        priority="high",
        parent_id=epic.id,
        metadata={"tags": ["oauth", "social-login"]},
    )
    print(f"✓ Created story: {story2.title} ({story2.item_metadata.get('external_id')})")

    # Create a test for the registration story
    test1 = item_storage.create_item(
        title="Test User Registration Flow",
        item_type="test",
        external_id="TEST-001",
        description="Verify user can register with valid email and password",
        status="todo",
        priority="high",
        metadata={"test_type": "integration"},
    )
    print(f"✓ Created test: {test1.title} ({test1.item_metadata.get('external_id')})")

    # Create traceability links
    link1 = item_storage.create_link(
        source_id=epic.id,
        target_id=story1.id,
        link_type="implements",
        metadata={"note": "Epic contains this story"},
    )
    print(f"✓ Created link: {epic.item_metadata.get('external_id')} → {story1.item_metadata.get('external_id')}")

    link2 = item_storage.create_link(
        source_id=epic.id,
        target_id=story2.id,
        link_type="implements",
    )
    print(f"✓ Created link: {epic.item_metadata.get('external_id')} → {story2.item_metadata.get('external_id')}")

    link3 = item_storage.create_link(
        source_id=story1.id,
        target_id=test1.id,
        link_type="tested_by",
    )
    print(f"✓ Created link: {story1.item_metadata.get('external_id')} → {test1.item_metadata.get('external_id')}")

    # List all items
    print("\n📋 All items:")
    all_items = item_storage.list_items()
    for item in all_items:
        print(f"  - {item.item_type.upper()}: {item.title} ({item.status})")

    # Search items
    print("\n🔍 Search for 'OAuth':")
    results = manager.search_items("OAuth", project_id=project.id)
    for item in results:
        print(f"  - {item.item_type.upper()}: {item.title}")

    # Check generated files
    print("\n📁 Generated files:")
    project_dir = storage_dir / "projects" / "my-app"

    epic_file = project_dir / "epics" / "EPIC-001.md"
    if epic_file.exists():
        print(f"  ✓ {epic_file.relative_to(storage_dir)}")
        print("    First lines:")
        lines = epic_file.read_text().split("\n")[:10]
        for line in lines:
            print(f"    {line}")

    links_file = project_dir / ".meta" / "links.yaml"
    if links_file.exists():
        print(f"\n  ✓ {links_file.relative_to(storage_dir)}")
        print("    Content:")
        for line in links_file.read_text().split("\n")[:20]:
            print(f"    {line}")

    # Check sync queue
    print("\n🔄 Sync queue:")
    sync_queue = manager.get_sync_queue()
    print(f"  {len(sync_queue)} items pending sync")
    for entry in sync_queue[:3]:
        print(
            f"  - {entry['operation']} {entry['entity_type']}: {entry['payload'].get('title', entry['payload'].get('name', 'N/A'))}"
        )

    # Update sync state
    manager.update_sync_state("last_sync", "2024-01-20T14:30:00Z")
    last_sync = manager.get_sync_state("last_sync")
    print(f"\n✓ Updated sync state: last_sync = {last_sync}")

    print(f"\n✅ Example complete! Check the generated files at:\n   {project_dir}")


if __name__ == "__main__":
    main()
