"""
Bulk operation service for Epic 2 (Story 2.8, FR14).

Handles bulk operations with preview, validation, and atomic execution.
"""

import csv
import json
from datetime import datetime
from io import StringIO
from typing import Any

from sqlalchemy.orm import Session

from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.schemas.item import ItemCreate


class BulkOperationService:
    """
    Service for bulk operations with preview (Story 2.8, FR14).
    """

    def __init__(self, session: Session):
        """Initialize bulk operation service."""
        self.session = session

    def bulk_update_preview(
        self,
        project_id: str,
        filters: dict[str, Any],
        updates: dict[str, Any],
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Preview bulk update without applying changes (Story 2.8, FR14).

        Args:
            project_id: Project ID
            filters: Filter criteria (view, status, etc.)
            updates: Fields to update
            limit: Number of sample items to show

        Returns:
            Preview dictionary with count, samples, warnings, estimated duration
        """
        # Build query
        query = self.session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        # Apply filters
        if "view" in filters:
            query = query.filter(Item.view == filters["view"].upper())
        if "status" in filters:
            query = query.filter(Item.status == filters["status"])
        if "item_type" in filters:
            query = query.filter(Item.item_type == filters["item_type"])
        if "priority" in filters:
            query = query.filter(Item.priority == filters["priority"])
        if "owner" in filters:
            query = query.filter(Item.owner == filters["owner"])

        # Get total count
        total_count = query.count()

        # Get sample items (first N)
        sample_items = query.limit(limit).all()

        # Generate warnings
        warnings = []
        if total_count > 100:
            warnings.append(f"Large operation: {total_count} items will be updated")
        if "status" in updates:
            # Check for status conflicts
            current_statuses = {item.status for item in sample_items}
            if len(current_statuses) > 1:
                warnings.append(f"Mixed statuses in sample: {current_statuses}")

        # Estimate duration (rough: 10ms per item)
        estimated_duration_ms = total_count * 10

        # Build sample preview
        samples = []
        for item in sample_items:
            sample = {
                "id": item.id[:8],
                "title": item.title[:50],
                "current": {
                    "status": item.status,
                    "priority": item.priority,
                    "owner": item.owner,
                },
                "new": {
                    "status": updates.get("status", item.status),
                    "priority": updates.get("priority", item.priority),
                    "owner": updates.get("owner", item.owner),
                },
            }
            samples.append(sample)

        return {
            "total_count": total_count,
            "sample_items": samples,
            "warnings": warnings,
            "estimated_duration_ms": estimated_duration_ms,
            "updates": updates,
        }

    def bulk_update_items(
        self,
        project_id: str,
        filters: dict[str, Any],
        updates: dict[str, Any],
        agent_id: str | None = None,
    ) -> dict[str, int]:
        """
        Execute bulk update atomically (Story 2.8, FR14).

        Args:
            project_id: Project ID
            filters: Filter criteria
            updates: Fields to update
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with items_updated count
        """
        # Build query
        query = self.session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        # Apply filters
        if "view" in filters:
            query = query.filter(Item.view == filters["view"].upper())
        if "status" in filters:
            query = query.filter(Item.status == filters["status"])
        if "item_type" in filters:
            query = query.filter(Item.item_type == filters["item_type"])
        if "priority" in filters:
            query = query.filter(Item.priority == filters["priority"])
        if "owner" in filters:
            query = query.filter(Item.owner == filters["owner"])

        items = query.all()
        items_updated = 0

        try:
            for item in items:
                # Update fields
                if "status" in updates:
                    item.status = updates["status"]
                if "priority" in updates:
                    item.priority = updates["priority"]
                if "owner" in updates:
                    item.owner = updates["owner"]
                if "title" in updates:
                    item.title = updates["title"]
                if "description" in updates:
                    item.description = updates["description"]

                items_updated += 1

                # Log update event
                event = Event(
                    project_id=project_id,
                    event_type="item_bulk_updated",
                    entity_type="item",
                    entity_id=item.id,
                    agent_id=agent_id,
                    data={
                        "updates": updates,
                        "item_id": item.id,
                        "item_title": item.title,
                    },
                )
                self.session.add(event)

            self.session.commit()

            return {"items_updated": items_updated}
        except Exception:
            self.session.rollback()
            raise

    def bulk_delete_items(
        self,
        project_id: str,
        filters: dict[str, Any],
        agent_id: str | None = None,
    ) -> dict[str, int]:
        """
        Execute bulk delete atomically (Story 2.8, FR14).

        Args:
            project_id: Project ID
            filters: Filter criteria
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with items_deleted count
        """
        # Build query
        query = self.session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        # Apply filters
        if "view" in filters:
            query = query.filter(Item.view == filters["view"].upper())
        if "status" in filters:
            query = query.filter(Item.status == filters["status"])
        if "item_type" in filters:
            query = query.filter(Item.item_type == filters["item_type"])

        items = query.all()
        items_deleted = 0

        try:
            for item in items:
                # Soft delete
                item.deleted_at = datetime.utcnow()
                items_deleted += 1

                # Log delete event
                event = Event(
                    project_id=project_id,
                    event_type="item_bulk_deleted",
                    entity_type="item",
                    entity_id=item.id,
                    agent_id=agent_id,
                    data={
                        "item_id": item.id,
                        "item_title": item.title,
                    },
                )
                self.session.add(event)

            self.session.commit()

            return {"items_deleted": items_deleted}
        except Exception:
            self.session.rollback()
            raise

    def bulk_create_preview(
        self,
        project_id: str,
        csv_data: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Preview bulk create from CSV without applying changes (Story 2.8, FR14, FR74).

        Args:
            project_id: Project ID
            csv_data: CSV file content as string
            limit: Number of sample items to show

        Returns:
            Preview dictionary with count, samples, validation errors, warnings, estimated duration
        """
        reader = csv.DictReader(StringIO(csv_data))
        headers = reader.fieldnames or []
        rows = list(reader)

        if not rows:
            return {
                "total_count": 0,
                "sample_items": [],
                "validation_errors": ["CSV file is empty or has no data rows"],
                "warnings": [],
                "estimated_duration_ms": 0,
            }

        # Validate CSV headers
        required_headers = ["Title", "View", "Type"]
        # Normalize headers for comparison (case-insensitive)
        normalized_headers = [h.strip().title() for h in headers]
        missing_headers = [h for h in required_headers if h not in normalized_headers]

        validation_errors = []
        if missing_headers:
            validation_errors.append(f"Missing required CSV columns: {', '.join(missing_headers)}")

        # Validate and parse each row
        valid_items = []
        invalid_rows = []

        for row_num, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
            try:
                # Normalize column names (case-insensitive, handle spaces)
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = key.strip().title()
                    normalized_row[normalized_key] = value.strip() if value else None

                # Extract fields
                title = normalized_row.get("Title", "").strip()
                view = normalized_row.get("View", "").strip().upper()
                item_type = normalized_row.get("Type", "").strip()
                description = normalized_row.get("Description", "").strip() or None
                status = normalized_row.get("Status", "todo").strip() or "todo"
                priority = normalized_row.get("Priority", "medium").strip() or "medium"
                owner = normalized_row.get("Owner", "").strip() or None
                parent_id = normalized_row.get("Parent Id", "").strip() or None
                metadata_str = normalized_row.get("Metadata", "").strip() or None

                # Parse metadata JSON if provided
                metadata = {}
                if metadata_str:
                    try:
                        metadata = json.loads(metadata_str)
                    except json.JSONDecodeError:
                        invalid_rows.append({
                            "row": row_num,
                            "error": f"Invalid JSON in Metadata column: {metadata_str[:50]}",
                        })
                        continue

                # Validate with Pydantic
                item_data = ItemCreate(
                    title=title,
                    description=description,
                    view=view,
                    item_type=item_type,
                    status=status,
                    parent_id=parent_id,
                    metadata=metadata,
                )

                valid_items.append({
                    "row": row_num,
                    "data": {
                        "title": item_data.title,
                        "view": item_data.view,
                        "item_type": item_data.item_type,
                        "status": item_data.status,
                        "description": item_data.description,
                        "priority": priority,
                        "owner": owner,
                        "parent_id": item_data.parent_id,
                        "metadata": item_data.metadata,
                    },
                })

            except Exception as e:
                invalid_rows.append({
                    "row": row_num,
                    "error": str(e),
                    "data": row,
                })

        # Add validation errors for invalid rows
        for invalid in invalid_rows:
            validation_errors.append(f"Row {invalid['row']}: {invalid['error']}")

        # Generate warnings
        warnings = []
        total_count = len(valid_items)
        if total_count > 100:
            warnings.append(f"Large operation: {total_count} items will be created")
        if len(invalid_rows) > 0:
            warnings.append(f"{len(invalid_rows)} row(s) have validation errors and will be skipped")

        # Check for duplicate titles in same view
        title_view_pairs = {}
        for item in valid_items:
            key = (item["data"]["title"], item["data"]["view"])
            if key in title_view_pairs:
                warnings.append(f"Duplicate title '{item['data']['title']}' in view {item['data']['view']} (rows {title_view_pairs[key]} and {item['row']})")
            else:
                title_view_pairs[key] = item["row"]

        # Estimate duration (rough: 15ms per item)
        estimated_duration_ms = total_count * 15

        # Build sample preview (first N valid items)
        samples = []
        for item in valid_items[:limit]:
            samples.append({
                "row": item["row"],
                "title": item["data"]["title"][:50],
                "view": item["data"]["view"],
                "type": item["data"]["item_type"],
                "status": item["data"]["status"],
                "priority": item["data"].get("priority", "medium"),
                "owner": item["data"].get("owner"),
            })

        return {
            "total_count": total_count,
            "sample_items": samples,
            "validation_errors": validation_errors,
            "warnings": warnings,
            "estimated_duration_ms": estimated_duration_ms,
            "invalid_rows_count": len(invalid_rows),
        }

    def bulk_create_items(
        self,
        project_id: str,
        csv_data: str,
        agent_id: str | None = None,
    ) -> dict[str, int]:
        """
        Execute bulk create from CSV atomically (Story 2.8, FR14, FR74).

        Args:
            project_id: Project ID
            csv_data: CSV file content as string
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with items_created count
        """
        reader = csv.DictReader(StringIO(csv_data))
        rows = list(reader)

        items_created = 0
        created_items = []

        try:
            for row in rows:
                try:
                    # Normalize column names (case-insensitive, handle spaces)
                    normalized_row = {}
                    for key, value in row.items():
                        normalized_key = key.strip().title()
                        normalized_row[normalized_key] = value.strip() if value else None

                    # Extract fields
                    title = normalized_row.get("Title", "").strip()
                    view = normalized_row.get("View", "").strip().upper()
                    item_type = normalized_row.get("Type", "").strip()
                    description = normalized_row.get("Description", "").strip() or None
                    status = normalized_row.get("Status", "todo").strip() or "todo"
                    priority = normalized_row.get("Priority", "medium").strip() or "medium"
                    owner = normalized_row.get("Owner", "").strip() or None
                    parent_id = normalized_row.get("Parent Id", "").strip() or None
                    metadata_str = normalized_row.get("Metadata", "").strip() or None

                    # Parse metadata JSON if provided
                    metadata = {}
                    if metadata_str:
                        try:
                            metadata = json.loads(metadata_str)
                        except json.JSONDecodeError:
                            # Skip invalid rows
                            continue

                    # Validate with Pydantic
                    item_data = ItemCreate(
                        title=title,
                        description=description,
                        view=view,
                        item_type=item_type,
                        status=status,
                        parent_id=parent_id,
                        metadata=metadata,
                    )

                    # Create item
                    item = Item(
                        project_id=project_id,
                        title=item_data.title,
                        description=item_data.description,
                        view=item_data.view,
                        item_type=item_data.item_type,
                        status=item_data.status,
                        priority=priority,
                        owner=owner,
                        parent_id=item_data.parent_id,
                        item_metadata=item_data.metadata,
                        version=1,
                    )

                    self.session.add(item)
                    self.session.flush()  # Get item.id
                    created_items.append(item)
                    items_created += 1

                    # Log creation event
                    event_data = {
                        "item_id": item.id,
                        "item_title": item.title,
                        "view": item.view,
                        "item_type": item.item_type,
                    }
                    event = Event(
                        project_id=project_id,
                        event_type="item_bulk_created",
                        entity_type="item",
                        entity_id=item.id,
                        agent_id=agent_id,
                        data=event_data,
                    )
                    self.session.add(event)

                except Exception:
                    # Skip invalid rows and continue
                    continue

            # Commit all items (events are optional)
            self.session.commit()

            return {"items_created": items_created}
        except Exception:
            self.session.rollback()
            raise
