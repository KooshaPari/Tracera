"""
Example usage of TraceRTM sync API client.

This demonstrates how to use the ApiClient for syncing local changes with the backend.
"""

import asyncio
from datetime import datetime, timedelta

from tracertm.api import (
    ApiClient,
    ApiConfig,
    Change,
    ConflictStrategy,
    SyncOperation,
)


async def example_basic_sync() -> None:
    """Basic sync example: upload and download changes."""
    # Create API client with configuration
    config = ApiConfig(
        base_url="https://api.tracertm.io",
        token="your-jwt-token-here",  # Get from auth flow
        timeout=30.0,
        max_retries=3,
    )

    async with ApiClient(config) as client:
        # Check API health
        is_healthy = await client.health_check()
        print(f"API Health: {'✓' if is_healthy else '✗'}")

        if not is_healthy:
            return

        # Create some local changes
        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.CREATE,
                data={
                    "title": "New Feature",
                    "view": "FEATURE",
                    "status": "todo",
                    "description": "Implement new authentication system",
                },
                version=1,
            ),
            Change(
                entity_type="item",
                entity_id="item-002",
                operation=SyncOperation.UPDATE,
                data={
                    "title": "Updated Story",
                    "status": "in_progress",
                },
                version=2,
            ),
        ]

        # Upload local changes
        print("\nUploading changes...")
        upload_result = await client.upload_changes(changes)

        print(f"Applied: {len(upload_result.applied)} changes")
        print(f"Conflicts: {len(upload_result.conflicts)}")
        print(f"Server time: {upload_result.server_time}")

        # Download remote changes since last sync
        last_sync = datetime.utcnow() - timedelta(hours=1)
        print("\nDownloading remote changes...")
        remote_changes = await client.download_changes(since=last_sync)

        print(f"Downloaded: {len(remote_changes)} changes")
        for change in remote_changes:
            print(f"  - {change.operation.value} {change.entity_type}: {change.entity_id}")


async def example_conflict_resolution() -> None:
    """Example of handling sync conflicts."""
    config = ApiConfig.from_config_manager()

    async with ApiClient(config) as client:
        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.UPDATE,
                data={"title": "My Local Version", "version": 5},
                version=5,
            )
        ]

        try:
            # Try to upload changes
            result = await client.upload_changes(changes)
            print(f"Upload successful: {len(result.applied)} changes applied")

        except Exception as e:
            from tracertm.api import ConflictError

            if isinstance(e, ConflictError):
                print(f"\nConflicts detected: {len(e.conflicts)}")

                for conflict in e.conflicts:
                    print(f"\nConflict ID: {conflict.conflict_id}")
                    print(f"  Entity: {conflict.entity_type}#{conflict.entity_id}")
                    print(f"  Local version: {conflict.local_version}")
                    print(f"  Remote version: {conflict.remote_version}")

                    # Auto-resolve: prefer local changes
                    resolved = await client.resolve_conflict(
                        conflict.conflict_id,
                        ConflictStrategy.LOCAL_WINS,
                        merged_data=conflict.local_data,
                    )

                    print(f"  Resolved: {resolved}")
            else:
                print(f"Error: {e}")


async def example_full_bidirectional_sync() -> None:
    """Example of full bidirectional sync with auto-conflict resolution."""
    config = ApiConfig.from_config_manager()

    async with ApiClient(config) as client:
        local_changes = [
            Change(
                entity_type="item",
                entity_id="item-003",
                operation=SyncOperation.CREATE,
                data={"title": "New Item", "status": "todo"},
                version=1,
            )
        ]

        last_sync = datetime.utcnow() - timedelta(days=1)

        # Perform full sync with automatic conflict resolution
        upload_result, remote_changes = await client.full_sync(
            local_changes=local_changes,
            last_sync=last_sync,
            conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
        )

        print(f"Uploaded: {len(upload_result.applied)} changes")
        print(f"Downloaded: {len(remote_changes)} remote changes")
        print(f"Conflicts auto-resolved: {len(upload_result.conflicts)}")


async def example_sync_status() -> None:
    """Example of checking sync status."""
    config = ApiConfig.from_config_manager()

    async with ApiClient(config) as client:
        status = await client.get_sync_status()

        print("Sync Status:")
        print(f"  Online: {status.online}")
        print(f"  Last sync: {status.last_sync}")
        print(f"  Pending changes: {status.pending_changes}")
        print(f"  Conflicts pending: {status.conflicts_pending}")
        print(f"  Server time: {status.server_time}")


async def main() -> None:
    """Run all examples."""
    print("=" * 60)
    print("TraceRTM Sync API Client Examples")
    print("=" * 60)

    try:
        print("\n1. Basic Sync (Upload + Download)")
        print("-" * 60)
        await example_basic_sync()

        print("\n2. Conflict Resolution")
        print("-" * 60)
        await example_conflict_resolution()

        print("\n3. Full Bidirectional Sync")
        print("-" * 60)
        await example_full_bidirectional_sync()

        print("\n4. Sync Status")
        print("-" * 60)
        await example_sync_status()

    except Exception as e:
        print(f"\nExample failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
