#!/usr/bin/env python
"""
Demo script showing project-local .trace/ storage workflow.

This demonstrates the complete lifecycle:
1. Initialize a new project with .trace/
2. Create items (epic, stories, tests)
3. Index into SQLite
4. Query across projects
"""

import tempfile
from pathlib import Path

from tracertm.storage.local_storage import LocalStorageManager


def main():
    """Run the project-local storage demo."""
    print("=" * 60)
    print("TraceRTM Project-Local Storage Demo")
    print("=" * 60)

    # Create temporary directories for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Initialize storage manager
        storage = LocalStorageManager(base_dir=base_dir / ".tracertm")
        print(f"\nGlobal index: {storage.db_path}")

        # ========================================
        # 1. Initialize Project
        # ========================================
        print("\n" + "=" * 60)
        print("1. Initializing new project...")
        print("=" * 60)

        project_path = base_dir / "my-awesome-app"
        project_path.mkdir(parents=True)

        trace_dir, project_id = storage.init_project(
            project_path,
            project_name="My Awesome App",
            description="A demo application showing TraceRTM project-local storage",
        )

        print(f"✓ Created .trace/ at: {trace_dir}")
        print(f"✓ Project ID: {project_id}")
        print(f"✓ Structure:")
        for item in sorted(trace_dir.rglob("*")):
            if item.is_file():
                rel_path = item.relative_to(trace_dir)
                print(f"  - {rel_path}")

        # ========================================
        # 2. Get Project Storage
        # ========================================
        print("\n" + "=" * 60)
        print("2. Getting project storage...")
        print("=" * 60)

        project_storage = storage.get_project_storage_for_path(project_path)
        print(f"✓ Project storage mode: {'local' if project_storage.is_project_local else 'legacy'}")
        print(f"✓ Project directory: {project_storage.project_dir}")

        # Get or create project in database
        project = project_storage.get_project()
        if not project:
            project = project_storage.create_or_update_project(
                name="My Awesome App",
                description="A demo application",
            )

        item_storage = project_storage.get_item_storage(project)

        # ========================================
        # 3. Create Items
        # ========================================
        print("\n" + "=" * 60)
        print("3. Creating items...")
        print("=" * 60)

        # Create Epic
        _, epic_id = storage.increment_project_counter(project_path, "epic")
        epic = item_storage.create_item(
            title="User Authentication System",
            item_type="epic",
            external_id=epic_id,
            description="Implement complete user authentication with OAuth2 support",
            status="in_progress",
            priority="high",
            owner="@alice",
        )
        print(f"✓ Created Epic: {epic_id} - {epic.title}")
        epic_md = trace_dir / "epics" / f"{epic_id}.md"
        print(f"  File: {epic_md.relative_to(project_path)}")

        # Create Story 1
        _, story1_id = storage.increment_project_counter(project_path, "story")
        story1 = item_storage.create_item(
            title="Login Page UI",
            item_type="story",
            external_id=story1_id,
            description="Create login page with email and password fields",
            status="in_progress",
            priority="high",
            owner="@bob",
            parent_id=epic.id,
        )
        print(f"✓ Created Story: {story1_id} - {story1.title}")

        # Create Story 2
        _, story2_id = storage.increment_project_counter(project_path, "story")
        story2 = item_storage.create_item(
            title="OAuth2 Integration",
            item_type="story",
            external_id=story2_id,
            description="Integrate OAuth2 with Google and GitHub",
            status="todo",
            priority="medium",
            owner="@alice",
            parent_id=epic.id,
        )
        print(f"✓ Created Story: {story2_id} - {story2.title}")

        # Create Test
        _, test_id = storage.increment_project_counter(project_path, "test")
        test = item_storage.create_item(
            title="Login Flow Tests",
            item_type="test",
            external_id=test_id,
            description="Test complete login flow with valid and invalid credentials",
            status="todo",
            priority="high",
            owner="@carol",
        )
        print(f"✓ Created Test: {test_id} - {test.title}")

        # Create links
        link1 = item_storage.create_link(
            source_id=epic.id,
            target_id=story1.id,
            link_type="implements",
        )
        link2 = item_storage.create_link(
            source_id=story1.id,
            target_id=test.id,
            link_type="tested_by",
        )
        print(f"✓ Created {2} traceability links")

        # ========================================
        # 4. Show Counters
        # ========================================
        print("\n" + "=" * 60)
        print("4. Current counters...")
        print("=" * 60)

        counters = storage.get_project_counters(project_path)
        for item_type, count in counters.items():
            print(f"  {item_type}: {count} (next: {item_type.upper()}-{count+1:03d})")

        # ========================================
        # 5. Index Project
        # ========================================
        print("\n" + "=" * 60)
        print("5. Indexing project into SQLite...")
        print("=" * 60)

        counts = storage.index_project(project_path)
        print(f"✓ Indexed {sum(counts.values())} items:")
        for type_name, count in counts.items():
            if count > 0:
                print(f"  - {type_name}: {count}")

        # ========================================
        # 6. Query Items
        # ========================================
        print("\n" + "=" * 60)
        print("6. Querying items...")
        print("=" * 60)

        # List all epics
        epics = item_storage.list_items(item_type="epic")
        print(f"\nEpics ({len(epics)}):")
        for epic in epics:
            ext_id = epic.item_metadata.get("external_id", epic.id[:8])
            print(f"  {ext_id}: {epic.title} [{epic.status}]")

        # List all stories
        stories = item_storage.list_items(item_type="story")
        print(f"\nStories ({len(stories)}):")
        for story in stories:
            ext_id = story.item_metadata.get("external_id", story.id[:8])
            parent_info = f" (parent: {story.parent_id[:8]})" if story.parent_id else ""
            print(f"  {ext_id}: {story.title} [{story.status}]{parent_info}")

        # Full-text search
        search_results = storage.search_items("authentication", project_id=project.id)
        print(f"\nSearch 'authentication' ({len(search_results)} results):")
        for item in search_results:
            ext_id = item.item_metadata.get("external_id", item.id[:8])
            print(f"  {ext_id}: {item.title} ({item.item_type})")

        # ========================================
        # 7. Show Markdown Files
        # ========================================
        print("\n" + "=" * 60)
        print("7. Generated markdown files...")
        print("=" * 60)

        print(f"\nEpic file: {epic_md.relative_to(project_path)}")
        print("-" * 60)
        print(epic_md.read_text()[:400] + "...")

        story_md = trace_dir / "stories" / f"{story1_id}.md"
        print(f"\nStory file: {story_md.relative_to(project_path)}")
        print("-" * 60)
        print(story_md.read_text()[:400] + "...")

        # ========================================
        # 8. Show Links YAML
        # ========================================
        print("\n" + "=" * 60)
        print("8. Traceability links...")
        print("=" * 60)

        links_yaml = trace_dir / ".meta" / "links.yaml"
        print(f"\nLinks file: {links_yaml.relative_to(project_path)}")
        print("-" * 60)
        print(links_yaml.read_text())

        # ========================================
        # 9. Detect Current Project
        # ========================================
        print("\n" + "=" * 60)
        print("9. Auto-detect current project...")
        print("=" * 60)

        # Simulate being in a subdirectory
        src_dir = project_path / "src" / "components"
        src_dir.mkdir(parents=True)

        import os
        original_cwd = os.getcwd()
        os.chdir(src_dir)

        detected_path = storage.get_current_project_path()
        if detected_path:
            print(f"✓ Detected project from {src_dir.relative_to(base_dir)}")
            print(f"  Project path: {detected_path.relative_to(base_dir)}")
        else:
            print("✗ No project detected")

        os.chdir(original_cwd)

        # ========================================
        # Summary
        # ========================================
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"✓ Project initialized at: {project_path.relative_to(base_dir)}")
        print(f"✓ Markdown files in: .trace/")
        print(f"✓ SQLite index at: {storage.db_path.relative_to(base_dir)}")
        print(f"✓ Created {len(epics)} epic, {len(stories)} stories, 1 test")
        print(f"✓ All items indexed and searchable")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
