#!/usr/bin/env python3
"""
Demo script showing TUI integration with LocalStorageManager.

This script demonstrates:
1. Creating a project and items using StorageAdapter
2. Simulating sync operations
3. Creating and resolving conflicts
4. Using the TUI programmatically
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from tracertm.storage.conflict_resolver import (
    ConflictResolver,
    ConflictStrategy,
    EntityVersion,
    VectorClock,
)
from tracertm.tui.adapters.storage_adapter import StorageAdapter


def demo_basic_operations():
    """Demonstrate basic storage operations."""
    print("=" * 60)
    print("Demo 1: Basic Storage Operations")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        # Initialize storage adapter
        adapter = StorageAdapter(base_dir=Path(tmpdir))

        # Create project
        print("\n1. Creating project...")
        project = adapter.create_project(
            name="demo-project",
            description="Demo project for TUI integration",
            metadata={"team": "platform", "status": "active"},
        )
        print(f"   ✓ Created project: {project.name} (ID: {str(project.id)[:8]}...)")

        # Create items
        print("\n2. Creating items...")
        epic = adapter.create_item(
            project=project,
            title="User Authentication System",
            item_type="epic",
            external_id="EPIC-001",
            description="Implement complete authentication system",
            priority="high",
        )
        print(f"   ✓ Created epic: {epic.title} (ID: {str(epic.id)[:8]}...)")

        story1 = adapter.create_item(
            project=project,
            title="Login Page",
            item_type="story",
            external_id="STORY-001",
            description="Create login page with email/password",
            parent_id=str(epic.id),
            status="in_progress",
        )
        print(f"   ✓ Created story: {story1.title} (ID: {str(story1.id)[:8]}...)")

        story2 = adapter.create_item(
            project=project,
            title="Password Reset",
            item_type="story",
            external_id="STORY-002",
            description="Implement password reset flow",
            parent_id=str(epic.id),
        )
        print(f"   ✓ Created story: {story2.title} (ID: {str(story2.id)[:8]}...)")

        test = adapter.create_item(
            project=project,
            title="Test Login Flow",
            item_type="test",
            external_id="TEST-001",
            description="E2E test for login",
        )
        print(f"   ✓ Created test: {test.title} (ID: {str(test.id)[:8]}...)")

        # Create links
        print("\n3. Creating traceability links...")
        link1 = adapter.create_link(
            project=project,
            source_id=str(story1.id),
            target_id=str(epic.id),
            link_type="implements",
        )
        print(f"   ✓ Created link: {story1.title} → {epic.title}")

        link2 = adapter.create_link(
            project=project,
            source_id=str(test.id),
            target_id=str(story1.id),
            link_type="tests",
        )
        print(f"   ✓ Created link: {test.title} → {story1.title}")

        # List items
        print("\n4. Listing items...")
        all_items = adapter.list_items(project)
        print(f"   Total items: {len(all_items)}")
        for item in all_items:
            print(f"   - {item.item_type.upper()}: {item.title} [{item.status}]")

        # Get statistics
        print("\n5. Project statistics...")
        stats = adapter.get_project_stats(project)
        print(f"   Total items: {stats['total_items']}")
        print(f"   Total links: {stats['total_links']}")
        print("   Items by type:")
        for item_type, count in stats["items_by_type"].items():
            print(f"     - {item_type}: {count}")
        print("   Items by status:")
        for status, count in stats["items_by_status"].items():
            print(f"     - {status}: {count}")

        # Pending changes
        print("\n6. Sync queue...")
        pending = adapter.get_pending_changes_count()
        print(f"   Pending changes: {pending}")

        print("\n✓ Demo completed successfully!")


def demo_conflict_resolution():
    """Demonstrate conflict detection and resolution."""
    print("\n" + "=" * 60)
    print("Demo 2: Conflict Resolution")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        adapter = StorageAdapter(base_dir=Path(tmpdir))
        project = adapter.create_project("conflict-demo")

        # Simulate conflicting versions
        print("\n1. Creating conflicting versions...")

        # Local version
        local_clock = VectorClock(
            client_id="client-001",
            version=5,
            timestamp=datetime.now() - timedelta(minutes=5),
        )
        local_version = EntityVersion(
            entity_id="item-123",
            entity_type="item",
            data={
                "title": "Feature A (Local Edit)",
                "status": "in_progress",
                "description": "Local changes",
            },
            vector_clock=local_clock,
            content_hash="abc123",
        )
        print(f"   ✓ Local version: v{local_clock.version} @ {local_clock.timestamp}")

        # Remote version (concurrent)
        remote_clock = VectorClock(
            client_id="client-002",
            version=6,
            timestamp=datetime.now() - timedelta(minutes=3),
        )
        remote_version = EntityVersion(
            entity_id="item-123",
            entity_type="item",
            data={
                "title": "Feature A (Remote Edit)",
                "status": "done",
                "description": "Remote changes",
            },
            vector_clock=remote_clock,
            content_hash="def456",
        )
        print(f"   ✓ Remote version: v{remote_clock.version} @ {remote_clock.timestamp}")

        # Detect conflict
        print("\n2. Detecting conflict...")
        session = adapter.storage.get_session()
        try:
            resolver = ConflictResolver(session, default_strategy=ConflictStrategy.LAST_WRITE_WINS)

            conflict = resolver.detect_conflict(local_version, remote_version)
            if conflict:
                print(f"   ✓ Conflict detected: {conflict.id}")
                print(f"     Entity: {conflict.entity_type} - {conflict.entity_id}")
                print(f"     Local: v{conflict.local_version.vector_clock.version}")
                print(f"     Remote: v{conflict.remote_version.vector_clock.version}")

                # Show differences
                from tracertm.storage.conflict_resolver import compare_versions

                diffs = compare_versions(local_version, remote_version)
                print("\n3. Data differences:")
                if diffs["modified"]:
                    print(f"   Modified fields: {', '.join(diffs['modified'])}")
                if diffs["added"]:
                    print(f"   Added in remote: {', '.join(diffs['added'])}")
                if diffs["removed"]:
                    print(f"   Removed in remote: {', '.join(diffs['removed'])}")

                # Resolve conflict
                print("\n4. Resolving conflict (strategy: LAST_WRITE_WINS)...")
                resolved = resolver.resolve(conflict)
                print(f"   ✓ Resolved using: {resolved.strategy_used.value}")
                winner = "remote" if resolved.version == remote_version else "local"
                print(f"   ✓ Winner: {winner} version")
                print(f"   ✓ Final title: {resolved.version.data['title']}")
                print(f"   ✓ Final status: {resolved.version.data['status']}")

                # Show backup
                if conflict.backup_path:
                    print("\n5. Backup created at:")
                    print(f"   {conflict.backup_path}")
                    print("   Files:")
                    for file in conflict.backup_path.iterdir():
                        print(f"     - {file.name}")
            else:
                print("   ✗ No conflict detected (unexpected)")

        finally:
            session.close()

        print("\n✓ Demo completed successfully!")


async def demo_sync_operations():
    """Demonstrate sync operations (mock)."""
    print("\n" + "=" * 60)
    print("Demo 3: Sync Operations")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        adapter = StorageAdapter(base_dir=Path(tmpdir))
        project = adapter.create_project("sync-demo")

        # Create some items
        print("\n1. Creating items for sync...")
        for i in range(5):
            adapter.create_item(
                project=project,
                title=f"Feature {i + 1}",
                item_type="epic",
                external_id=f"EPIC-{i + 1:03d}",
            )
        print("   ✓ Created 5 items")

        # Check sync status
        print("\n2. Checking sync status...")
        state = adapter.get_sync_status()
        print(f"   Status: {state.status.value}")
        print(f"   Pending changes: {state.pending_changes}")
        print(f"   Last sync: {state.last_sync or 'Never'}")

        # Note: Actual sync requires API client integration
        print("\n3. Sync operation...")
        print("   (Skipping - requires API client integration)")
        print("   To enable sync:")
        print("   - Implement API client")
        print("   - Pass to StorageAdapter constructor")
        print("   - Call: await adapter.trigger_sync()")

        print("\n✓ Demo completed!")


def demo_reactive_callbacks():
    """Demonstrate reactive callbacks."""
    print("\n" + "=" * 60)
    print("Demo 4: Reactive Callbacks")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        adapter = StorageAdapter(base_dir=Path(tmpdir))

        # Register callbacks
        print("\n1. Registering callbacks...")

        def on_sync_status(state):
            print(f"   [CALLBACK] Sync status changed: {state.status.value}")

        def on_conflict(conflict):
            print(f"   [CALLBACK] Conflict detected: {conflict.entity_type} {conflict.entity_id}")

        def on_item_change(item_id):
            print(f"   [CALLBACK] Item changed: {item_id[:8]}...")

        unregister_sync = adapter.on_sync_status_change(on_sync_status)
        unregister_conflict = adapter.on_conflict_detected(on_conflict)
        unregister_item = adapter.on_item_change(on_item_change)

        print("   ✓ Callbacks registered")

        # Trigger callbacks
        print("\n2. Creating item (triggers callback)...")
        project = adapter.create_project("callback-demo")
        item = adapter.create_item(project=project, title="Test Item", item_type="epic")

        print("\n3. Updating item (triggers callback)...")
        adapter.update_item(project=project, item_id=str(item.id), status="done")

        # Unregister
        print("\n4. Unregistering callbacks...")
        unregister_sync()
        unregister_conflict()
        unregister_item()
        print("   ✓ Callbacks unregistered")

        print("\n5. Creating item (no callback)...")
        item2 = adapter.create_item(project=project, title="Test Item 2", item_type="story")

        print("\n✓ Demo completed!")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("TraceRTM TUI LocalStorage Integration Demo")
    print("=" * 60)

    demo_basic_operations()
    demo_conflict_resolution()

    # Sync operations demo (async)
    print("\nRunning async demo...")
    asyncio.run(demo_sync_operations())

    demo_reactive_callbacks()

    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)
    print("\nTo launch the TUI:")
    print("  rtm tui dashboard")
    print("\nTo launch legacy TUI:")
    print("  rtm tui dashboard --legacy")
    print()


if __name__ == "__main__":
    main()
