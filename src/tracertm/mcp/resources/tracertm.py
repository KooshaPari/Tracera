"""Core TraceRTM MCP resources for data access."""

from __future__ import annotations

import yaml
from sqlalchemy.exc import SQLAlchemyError

from tracertm.config.manager import ConfigManager
from tracertm.mcp.core import mcp
from tracertm.storage.local_storage import LocalStorageManager

# Default limit and truncation thresholds for list resources
_DEFAULT_LIST_LIMIT = 100
# Tree/view limits to avoid huge responses
_MAX_TREE_DEPTH = 5
_MAX_ROOTS_DISPLAY = 20
# Maximum items to display in lists
_MAX_ITEM_LIST_DISPLAY = 10
# Maximum children to display in tree view
_MAX_TREE_CHILDREN_DISPLAY = 10
_RESOURCE_READ_ERRORS = (
    AttributeError,
    ImportError,
    LookupError,
    OSError,
    RuntimeError,
    TypeError,
    ValueError,
    SQLAlchemyError,
)


def _get_project_id() -> str | None:
    """Get current project ID from config."""
    config = ConfigManager()
    value = config.get("current_project_id")
    return str(value) if value else None


def _format_yaml(data: object) -> str:
    """Format data as YAML."""
    return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)


@mcp.resource("tracertm://projects")
def projects_list_resource() -> str:
    """List all projects as YAML.

    Returns a YAML-formatted list of all registered projects with their
    basic metadata (ID, name, description, item count, link count).
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.project import Project

            projects = session.query(Project).all()

            result = [
                {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                }
                for project in projects
            ]

            return _format_yaml({"projects": result, "total": len(result)})
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error loading projects: {e}"


@mcp.resource("tracertm://project/{project_id}")
def project_detail_resource(project_id: str) -> str:
    """Project details with item/link counts.

    Args:
        project_id: The project ID to fetch details for.

    Returns YAML with project metadata, item counts by view, and link counts.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.item import Item
            from tracertm.models.link import Link
            from tracertm.models.project import Project

            project = session.query(Project).filter(Project.id.like(f"{project_id}%")).first()

            if not project:
                return f"# Project not found: {project_id}"

            # Count items by view
            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id == project.id,
                    Item.deleted_at.is_(None),
                )
                .all()
            )

            view_counts: dict[str, int] = {}
            status_counts: dict[str, int] = {}
            for item in items:
                view_counts[item.view] = view_counts.get(item.view, 0) + 1
                status_counts[item.status] = status_counts.get(item.status, 0) + 1

            # Count links
            link_count = (
                session
                .query(Link)
                .filter(
                    Link.project_id == project.id,
                )
                .count()
            )

            return _format_yaml({
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                },
                "items": {
                    "total": len(items),
                    "by_view": view_counts,
                    "by_status": status_counts,
                },
                "links": {
                    "total": link_count,
                },
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error loading project: {e}"


@mcp.resource("tracertm://items/{project_id}")
def items_resource(project_id: str) -> str:
    """Items in project (first 100).

    Args:
        project_id: The project ID to fetch items for.

    Returns YAML list of items with basic metadata.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.item import Item

            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id.like(f"{project_id}%"),
                    Item.deleted_at.is_(None),
                )
                .limit(100)
                .all()
            )

            result = [
                {
                    "id": str(item.id)[:8],
                    "title": item.title,
                    "view": item.view,
                    "item_type": item.item_type,
                    "status": item.status,
                    "priority": item.priority,
                    "owner": item.owner,
                }
                for item in items
            ]

            return _format_yaml({
                "items": result,
                "total": len(result),
                "truncated": len(result) >= _DEFAULT_LIST_LIMIT,
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error loading items: {e}"


@mcp.resource("tracertm://links/{project_id}")
def links_resource(project_id: str) -> str:
    """Links in project (first 100).

    Args:
        project_id: The project ID to fetch links for.

    Returns YAML list of links with source/target IDs and link types.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.link import Link

            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id.like(f"{project_id}%"),
                )
                .limit(_DEFAULT_LIST_LIMIT)
                .all()
            )

            result = [
                {
                    "id": str(link.id)[:8],
                    "source_id": str(link.source_item_id)[:8],
                    "target_id": str(link.target_item_id)[:8],
                    "link_type": link.link_type,
                }
                for link in links
            ]

            return _format_yaml({
                "links": result,
                "total": len(result),
                "truncated": len(result) >= _DEFAULT_LIST_LIMIT,
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error loading links: {e}"


@mcp.resource("tracertm://matrix/{project_id}")
def matrix_resource(project_id: str) -> str:
    """Traceability matrix summary.

    Args:
        project_id: The project ID to generate matrix for.

    Returns YAML summary of traceability coverage between views.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.item import Item
            from tracertm.models.link import Link

            # Get all items grouped by view
            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id.like(f"{project_id}%"),
                    Item.deleted_at.is_(None),
                )
                .all()
            )

            if not items:
                return "# No items found in project"

            view_items: dict[str, list[str]] = {}
            for item in items:
                if item.view not in view_items:
                    view_items[item.view] = []
                view_items[item.view].append(str(item.id))

            # Get links
            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id.like(f"{project_id}%"),
                )
                .all()
            )

            # Calculate coverage between views
            coverage: dict[str, dict[str, dict[str, int]]] = {}
            for source_view, source_item_ids in view_items.items():
                coverage[source_view] = {}
                for target_view, target_item_ids in view_items.items():
                    if source_view == target_view:
                        continue
                    source_ids = set(source_item_ids)
                    target_ids = set(target_item_ids)

                    linked_sources = set()
                    for link in links:
                        if str(link.source_item_id) in source_ids and str(link.target_item_id) in target_ids:
                            linked_sources.add(str(link.source_item_id))

                    coverage[source_view][target_view] = {
                        "linked": len(linked_sources),
                        "total": len(source_ids),
                        "percentage": int(round(len(linked_sources) / len(source_ids) * 100, 0)) if source_ids else 0,
                    }

            return _format_yaml({
                "views": list(view_items.keys()),
                "items_by_view": {v: len(ids) for v, ids in view_items.items()},
                "coverage": coverage,
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error generating matrix: {e}"


@mcp.resource("tracertm://health/{project_id}")
def health_resource(project_id: str) -> str:
    """Project health metrics.

    Args:
        project_id: The project ID to check health for.

    Returns YAML with health indicators like orphan items, stale items,
    traceability gaps, and overall health score.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from datetime import UTC, datetime, timedelta

            from tracertm.models.item import Item
            from tracertm.models.link import Link

            # Get all items
            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id.like(f"{project_id}%"),
                    Item.deleted_at.is_(None),
                )
                .all()
            )

            if not items:
                return "# No items found in project"

            # Get links
            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id.like(f"{project_id}%"),
                )
                .all()
            )

            # Find orphan items (no links)
            linked_items = set()
            for link in links:
                linked_items.add(str(link.source_item_id))
                linked_items.add(str(link.target_item_id))
            orphans = [str(i.id)[:8] for i in items if str(i.id) not in linked_items]

            # Find stale items (not updated in 30 days)
            stale_threshold = datetime.now(UTC) - timedelta(days=30)
            stale_items = [str(i.id)[:8] for i in items if i.updated_at and i.updated_at < stale_threshold]

            # Calculate status distribution
            status_counts: dict[str, int] = {}
            for item in items:
                status_counts[item.status] = status_counts.get(item.status, 0) + 1

            # Calculate health score (0-100)
            orphan_penalty = min(len(orphans) / len(items) * 30, 30) if items else 0
            stale_penalty = min(len(stale_items) / len(items) * 20, 20) if items else 0
            blocked_penalty = min(status_counts.get("blocked", 0) / len(items) * 20, 20) if items else 0
            health_score = max(0, 100 - orphan_penalty - stale_penalty - blocked_penalty)

            return _format_yaml({
                "project_id": project_id,
                "total_items": len(items),
                "total_links": len(links),
                "health_score": round(health_score, 1),
                "issues": {
                    "orphan_items": len(orphans),
                    "stale_items": len(stale_items),
                    "blocked_items": status_counts.get("blocked", 0),
                },
                "status_distribution": status_counts,
                "orphan_item_ids": orphans[:_MAX_ITEM_LIST_DISPLAY],  # Show first N items
                "stale_item_ids": stale_items[:_MAX_ITEM_LIST_DISPLAY],  # Show first N items
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error checking health: {e}"


# Materialized view resources
@mcp.resource("tracertm://views/traceability/{project_id}")
def traceability_view_resource(project_id: str) -> str:
    """Traceability view for a project.

    Shows the complete traceability chain from requirements to tests.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.item import Item
            from tracertm.models.link import Link

            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id.like(f"{project_id}%"),
                    Item.deleted_at.is_(None),
                )
                .all()
            )

            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id.like(f"{project_id}%"),
                )
                .all()
            )

            # Build adjacency list
            item_lookup = {str(item.id): item for item in items}
            children: dict[str, list[str]] = {}
            for link in links:
                source = str(link.source_item_id)
                if source not in children:
                    children[source] = []
                children[source].append(str(link.target_item_id))

            # Find root items (no incoming links)
            has_parent = {str(link.target_item_id) for link in links}
            roots = [item for item in items if str(item.id) not in has_parent]

            def build_tree(item_id: str, depth: int = 0) -> dict[str, object]:
                if depth > _MAX_TREE_DEPTH:  # Prevent infinite recursion
                    return {"truncated": True}
                item = item_lookup.get(item_id)
                if not item:
                    return {"missing": item_id[:8]}
                result: dict[str, object] = {
                    "id": item_id[:8],
                    "title": item.title,
                    "view": item.view,
                    "status": item.status,
                }
                if item_id in children:
                    result["children"] = [
                        build_tree(child_id, depth + 1)
                        for child_id in children[item_id][:_MAX_TREE_CHILDREN_DISPLAY]  # Limit children
                    ]
                return result

            trees = [build_tree(str(root.id)) for root in roots[:_MAX_ROOTS_DISPLAY]]  # Limit roots

            return _format_yaml({
                "project_id": project_id,
                "traceability_trees": trees,
                "total_roots": len(roots),
                "truncated": len(roots) > _MAX_ROOTS_DISPLAY,
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error building traceability view: {e}"


@mcp.resource("tracertm://views/impact/{project_id}")
def impact_view_resource(project_id: str) -> str:
    """Impact analysis view for a project.

    Shows items with most downstream dependencies (highest impact).
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.item import Item
            from tracertm.models.link import Link

            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id.like(f"{project_id}%"),
                    Item.deleted_at.is_(None),
                )
                .all()
            )

            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id.like(f"{project_id}%"),
                )
                .all()
            )

            # Build adjacency list
            children: dict[str, list[str]] = {}
            for link in links:
                source = str(link.source_item_id)
                if source not in children:
                    children[source] = []
                children[source].append(str(link.target_item_id))

            # Calculate downstream count for each item
            def count_downstream(item_id: str, visited: set[str] | None = None) -> int:
                if visited is None:
                    visited = set()
                if item_id in visited:
                    return 0
                visited.add(item_id)
                count = 0
                for child_id in children.get(item_id, []):
                    count += 1 + count_downstream(child_id, visited)
                return count

            impact_scores = []
            for item in items:
                item_id = str(item.id)
                downstream = count_downstream(item_id)
                if downstream > 0:
                    impact_scores.append({
                        "id": item_id[:8],
                        "title": item.title,
                        "view": item.view,
                        "status": item.status,
                        "downstream_count": downstream,
                    })

            # Sort by impact
            impact_scores.sort(
                key=lambda x: int(x["downstream_count"]) if isinstance(x["downstream_count"], (int, str)) else 0,
                reverse=True,
            )

            return _format_yaml({
                "project_id": project_id,
                "high_impact_items": impact_scores[:_MAX_ROOTS_DISPLAY],
                "total_with_impact": len(impact_scores),
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error building impact view: {e}"


@mcp.resource("tracertm://views/coverage/{project_id}")
def coverage_view_resource(project_id: str) -> str:
    """Coverage view for a project.

    Shows test coverage and traceability completeness.
    """
    try:
        storage = LocalStorageManager()
        with storage.get_session() as session:
            from tracertm.models.item import Item
            from tracertm.models.link import Link

            items = (
                session
                .query(Item)
                .filter(
                    Item.project_id.like(f"{project_id}%"),
                    Item.deleted_at.is_(None),
                )
                .all()
            )

            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id.like(f"{project_id}%"),
                )
                .all()
            )

            # Group items by view
            view_items: dict[str, list[Item]] = {}
            for item in items:
                if item.view not in view_items:
                    view_items[item.view] = []
                view_items[item.view].append(item)

            # Calculate coverage for each view
            coverage: dict[str, dict[str, object]] = {}
            for view, view_item_list in view_items.items():
                item_ids = {str(item.id) for item in view_item_list}
                linked_ids = set()
                for link in links:
                    if str(link.source_item_id) in item_ids or str(link.target_item_id) in item_ids:
                        linked_ids.add(str(link.source_item_id))
                        linked_ids.add(str(link.target_item_id))

                covered = len(item_ids & linked_ids)
                total = len(item_ids)
                coverage[view] = {
                    "total": total,
                    "covered": covered,
                    "percentage": round(covered / total * 100, 1) if total else 0,
                    "uncovered": [str(item.id)[:8] for item in view_item_list if str(item.id) not in linked_ids][
                        :_MAX_ITEM_LIST_DISPLAY
                    ],
                }

            return _format_yaml({
                "project_id": project_id,
                "coverage_by_view": coverage,
            })
    except _RESOURCE_READ_ERRORS as e:
        return f"# Error building coverage view: {e}"


__all__ = [
    "coverage_view_resource",
    "health_resource",
    "impact_view_resource",
    "items_resource",
    "links_resource",
    "matrix_resource",
    "project_detail_resource",
    "projects_list_resource",
    "traceability_view_resource",
]
