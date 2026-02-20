"""Bulk operation service for Epic 2 (Story 2.8, FR14).

Handles bulk operations with preview, validation, and atomic execution.


Functional Requirements: FR-APP-005
"""

from __future__ import annotations

import csv
import json
import logging
import uuid
from datetime import UTC, datetime
from io import StringIO
from typing import Any

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session  # noqa: TC002

from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.schemas.item import ItemCreate

logger = logging.getLogger(__name__)

BULK_WARN_THRESHOLD = 100


class BulkOperationService:
    """Service for bulk operations with preview (Story 2.8, FR14)."""

    def __init__(self, session: Session) -> None:
        """Initialize bulk operation service."""
        self.session = session

    def bulk_update_preview(
        self,
        project_id: str | uuid.UUID,
        filters: dict[str, Any],
        updates: dict[str, Any],
        limit: int = 5,
    ) -> dict[str, Any]:
        """Preview bulk update without applying changes (Story 2.8, FR14).

        Args:
            project_id: Project ID
            filters: Filter criteria (view, status, etc.)
            updates: Fields to update
            limit: Number of sample items to show

        Returns:
            Preview dictionary with count, samples, warnings, estimated duration
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        # Build query
        query = self.session.query(Item).filter(
            Item.project_id == pid,
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
        if total_count > BULK_WARN_THRESHOLD:
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
        project_id: str | uuid.UUID,
        filters: dict[str, Any],
        updates: dict[str, Any],
        agent_id: str | None = None,
    ) -> dict[str, int]:
        """Execute bulk update atomically (Story 2.8, FR14).

        Args:
            project_id: Project ID
            filters: Filter criteria
            updates: Fields to update
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with items_updated count
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        # Build query
        query = self.session.query(Item).filter(
            Item.project_id == pid,
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
                    project_id=pid,
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
        except Exception:
            self.session.rollback()
            raise
        else:
            return {"items_updated": items_updated}

    def bulk_delete_items(
        self,
        project_id: str | uuid.UUID,
        filters: dict[str, Any],
        agent_id: str | None = None,
    ) -> dict[str, int]:
        """Execute bulk delete atomically (Story 2.8, FR14).

        Args:
            project_id: Project ID
            filters: Filter criteria
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with items_deleted count
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        # Build query
        query = self.session.query(Item).filter(
            Item.project_id == pid,
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
                item.deleted_at = datetime.now(UTC)
                items_deleted += 1

                # Log delete event
                event = Event(
                    project_id=pid,
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
        except Exception:
            self.session.rollback()
            raise
        else:
            return {"items_deleted": items_deleted}

    def bulk_create_preview(
        self,
        _project_id: str | uuid.UUID,
        csv_data: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Preview bulk create from CSV without applying changes (Story 2.8, FR14, FR74).

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
        valid_items: list[dict[str, Any]] = []
        invalid_rows: list[dict[str, Any]] = []

        for row_num, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
            try:
                # Normalize column names (case-insensitive, handle spaces)
                normalized_row: dict[str, str | None] = {}
                for key, value in row.items():
                    normalized_key = key.strip().title()
                    normalized_row[normalized_key] = value.strip() if value else None

                # Extract fields
                title_val = normalized_row.get("Title")
                title = title_val.strip() if title_val else ""
                view_val = normalized_row.get("View")
                view = view_val.strip().upper() if view_val else ""
                type_val = normalized_row.get("Type")
                item_type = type_val.strip() if type_val else ""
                desc_val = normalized_row.get("Description")
                description = desc_val.strip() if desc_val else None
                status_val = normalized_row.get("Status")
                status = (status_val.strip() if status_val else "todo") or "todo"
                priority_val = normalized_row.get("Priority")
                priority = (priority_val.strip() if priority_val else "medium") or "medium"
                owner_val = normalized_row.get("Owner")
                owner = owner_val.strip() if owner_val else None
                parent_val = normalized_row.get("Parent Id")
                parent_id = parent_val.strip() if parent_val else None
                meta_val = normalized_row.get("Metadata")
                metadata_str = meta_val.strip() if meta_val else None

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

                valid_item: dict[str, Any] = {
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
                }
                valid_items.append(valid_item)

            except (ValueError, KeyError, TypeError) as e:
                invalid_rows.append({
                    "row": row_num,
                    "error": str(e),
                    "data": row,
                })

        # Add validation errors for invalid rows
        validation_errors.extend(f"Row {invalid['row']}: {invalid['error']}" for invalid in invalid_rows)

        # Generate warnings
        warnings = []
        total_count = len(valid_items)
        if total_count > BULK_WARN_THRESHOLD:
            warnings.append(f"Large operation: {total_count} items will be created")
        if len(invalid_rows) > 0:
            warnings.append(f"{len(invalid_rows)} row(s) have validation errors and will be skipped")

        # Check for duplicate titles in same view
        title_view_pairs: dict[tuple[str, str], int] = {}
        for item in valid_items:
            data_dict = item.get("data", {})
            key = (
                str(data_dict.get("title", "")),
                str(data_dict.get("view", "")),
            )
            row_num_val = int(item.get("row", 0))
            if key in title_view_pairs:
                warnings.append(
                    f"Duplicate title '{data_dict.get('title', '')}' in view "
                    f"{data_dict.get('view', '')} (rows {title_view_pairs[key]} and {row_num_val})",
                )
            else:
                title_view_pairs[key] = row_num_val

        # Estimate duration (rough: 15ms per item)
        estimated_duration_ms = total_count * 15

        # Build sample preview (first N valid items)
        samples: list[dict[str, Any]] = []
        for item in valid_items[:limit]:
            data_dict = item.get("data", {})
            title_str = str(data_dict.get("title", ""))[:50]
            sample_item: dict[str, Any] = {
                "row": int(item.get("row", 0)),
                "title": title_str,
                "view": str(data_dict.get("view", "")),
                "type": str(data_dict.get("item_type", "")),
                "status": str(data_dict.get("status", "")),
                "priority": str(data_dict.get("priority", "medium")),
                "owner": data_dict.get("owner"),
            }
            samples.append(sample_item)

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
        project_id: str | uuid.UUID,
        csv_data: str,
        agent_id: str | None = None,
    ) -> dict[str, int]:
        """Execute bulk create from CSV atomically (Story 2.8, FR14, FR74).

        Args:
            project_id: Project ID
            csv_data: CSV file content as string
            agent_id: Optional agent ID for logging

        Returns:
            Dictionary with items_created count
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
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

                    # Extract fields - safely handle None values
                    title = (normalized_row.get("Title") or "").strip()
                    view = (normalized_row.get("View") or "").strip().upper()
                    item_type = (normalized_row.get("Type") or "").strip()
                    description = (normalized_row.get("Description") or "").strip() or None
                    status = (normalized_row.get("Status") or "todo").strip() or "todo"
                    priority = (normalized_row.get("Priority") or "medium").strip() or "medium"
                    owner = (normalized_row.get("Owner") or "").strip() or None
                    parent_id = (normalized_row.get("Parent Id") or "").strip() or None
                    metadata_str = (normalized_row.get("Metadata") or "").strip() or None

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
                    new_item: Item = Item(
                        project_id=pid,
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

                    self.session.add(new_item)
                    self.session.flush()  # Get item.id
                    created_items.append(new_item)
                    items_created += 1

                    # Log creation event
                    event_data = {
                        "item_id": new_item.id,
                        "item_title": new_item.title,
                        "view": new_item.view,
                        "item_type": new_item.item_type,
                    }
                    event = Event(
                        project_id=pid,
                        event_type="item_bulk_created",
                        entity_type="item",
                        entity_id=new_item.id,
                        agent_id=agent_id,
                        data=event_data,
                    )
                    self.session.add(event)

                except (ValueError, KeyError, TypeError, OperationalError) as e:
                    logger.debug("Skipping invalid row: %s", e)
                    continue

            # Commit all items (events are optional)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        else:
            return {"items_created": items_created}
