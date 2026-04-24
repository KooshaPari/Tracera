"""Streaming and pagination MCP tools for large data operations."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import Progress

from tracertm.config.manager import ConfigManager
from tracertm.storage.local_storage import LocalStorageManager

logger = logging.getLogger(__name__)

try:
    from tracertm.mcp.core import mcp
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]


def _get_project_id(project_id: str | None = None) -> str:
    """Get project ID from arg or config."""
    if project_id:
        return project_id
    config = ConfigManager()
    current = config.get("current_project_id")
    if not current:
        msg = "project_id is required or select a project first."
        raise ToolError(msg)
    return str(current)


@mcp.tool(description="Stream impact analysis with progress updates")
async def stream_impact_analysis(
    item_id: str,
    max_depth: int = 5,
    progress: Any = Progress(),
) -> dict[str, object]:
    """Analyze impact depth-by-depth with progress updates.

    Performs impact analysis in stages, returning results at each depth level.
    Uses Progress() to stream progress updates to the client.

    Args:
        item_id: The item ID to analyze impact for.
        max_depth: Maximum depth to traverse (default 5).
        progress: Progress tracker for worker-safe updates.

    Returns:
        Complete impact analysis results with items at each depth level.
    """
    storage = LocalStorageManager()

    with storage.get_session() as session:
        from tracertm.models.item import Item
        from tracertm.models.link import Link

        # Find the item
        item = (
            session
            .query(Item)
            .filter(
                Item.id.like(f"{item_id}%"),
                Item.deleted_at.is_(None),
            )
            .first()
        )

        if not item:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        project_id = item.project_id

        # Get all links for the project
        links = session.query(Link).filter(Link.project_id == project_id).all()

        # Build adjacency list
        children: dict[str, list[str]] = {}
        for link in links:
            source = str(link.source_item_id)
            if source not in children:
                children[source] = []
            children[source].append(str(link.target_item_id))

        # Get all items for lookup
        all_items = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .all()
        )
        item_lookup = {str(i.id): i for i in all_items}

        # Traverse depth by depth
        results: dict[str, list[dict[str, object]]] = {}
        visited: set[str] = set()
        current_level: set[str] = {str(item.id)}

        current_progress = 0
        await progress.set_total(max_depth)

        for depth in range(max_depth + 1):
            if not current_level:
                break

            # Report progress via worker-safe dependency
            try:
                increment = depth - current_progress
                if increment > 0:
                    await progress.increment(increment)
                    current_progress = depth
                await progress.set_message(
                    f"Analyzing depth {depth}: found {len(current_level)} items, total visited: {len(visited)}",
                )
            except (AttributeError, RuntimeError, TypeError, ValueError) as e:
                # Progress reporting is optional, but log failures
                logger.debug("Progress reporting failed: %s", e)

            # Record items at this depth
            level_items: list[dict[str, object]] = []
            for item_id_str in current_level:
                if item_id_str in visited:
                    continue
                visited.add(item_id_str)
                item_data = item_lookup.get(item_id_str)
                if item_data:
                    level_items.append({
                        "id": item_id_str[:8],
                        "title": item_data.title,
                        "view": item_data.view,
                        "status": item_data.status,
                    })

            if level_items:
                results[f"depth_{depth}"] = level_items

            # Get next level
            next_level: set[str] = set()
            for item_id_str in current_level:
                for child_id in children.get(item_id_str, []):
                    if child_id not in visited:
                        next_level.add(child_id)
            current_level = next_level

        return {
            "ok": True,
            "root_item": {
                "id": str(item.id)[:8],
                "title": item.title,
            },
            "max_depth_reached": len(results) - 1 if results else 0,
            "total_impacted": len(visited) - 1,  # Exclude root
            "impact_by_depth": results,
        }


@mcp.tool(description="Get traceability matrix page")
def get_matrix_page(
    project_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    source_view: str | None = None,
    target_view: str | None = None,
    _ctx: object | None = None,
) -> dict[str, object]:
    """Get paginated matrix rows.

    Returns a page of traceability matrix entries showing source-to-target
    relationships with coverage information.

    Args:
        project_id: Project ID (uses current if not specified).
        page: Page number (1-indexed).
        page_size: Items per page (default 50, max 100).
        source_view: Filter by source view.
        target_view: Filter by target view.
        ctx: MCP context.

    Returns:
        Paginated matrix rows with source, target, and link information.
    """
    project_id = _get_project_id(project_id)
    page_size = min(page_size, 100)  # Cap at 100
    offset = (page - 1) * page_size

    storage = LocalStorageManager()
    with storage.get_session() as session:
        from tracertm.models.item import Item
        from tracertm.models.link import Link

        # Get items
        item_query = session.query(Item).filter(
            Item.project_id.like(f"{project_id}%"),
            Item.deleted_at.is_(None),
        )
        if source_view:
            item_query = item_query.filter(Item.view == source_view.upper())

        items = item_query.all()
        item_lookup = {str(item.id): item for item in items}

        # Get links
        links = session.query(Link).filter(Link.project_id.like(f"{project_id}%")).all()

        # Build matrix rows
        rows = []
        for item in items:
            item_id = str(item.id)
            outgoing_links = [link for link in links if str(link.source_item_id) == item_id]

            for link in outgoing_links:
                target = item_lookup.get(str(link.target_item_id))
                if target and (not target_view or target.view == target_view.upper()):
                    rows.append({
                        "source_id": item_id[:8],
                        "source_title": item.title,
                        "source_view": item.view,
                        "target_id": str(link.target_item_id)[:8],
                        "target_title": target.title,
                        "target_view": target.view,
                        "link_type": link.link_type,
                    })

        total_rows = len(rows)
        total_pages = (total_rows + page_size - 1) // page_size
        paginated_rows = rows[offset : offset + page_size]

        return {
            "ok": True,
            "page": page,
            "page_size": page_size,
            "total_rows": total_rows,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "rows": paginated_rows,
        }


@mcp.tool(description="Get impact at specific depth level")
def get_impact_by_depth(
    item_id: str,
    depth: int,
    _ctx: object | None = None,
) -> dict[str, object]:
    """Get impact results for a single depth level.

    Useful for lazy loading impact results one level at a time.

    Args:
        item_id: The item ID to analyze impact for.
        depth: The specific depth level to retrieve (0 = root).
        ctx: MCP context.

    Returns:
        Items at the specified depth level.
    """
    storage = LocalStorageManager()

    with storage.get_session() as session:
        from tracertm.models.item import Item
        from tracertm.models.link import Link

        # Find the item
        item = (
            session
            .query(Item)
            .filter(
                Item.id.like(f"{item_id}%"),
                Item.deleted_at.is_(None),
            )
            .first()
        )

        if not item:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        project_id = item.project_id

        # Get all links for the project
        links = session.query(Link).filter(Link.project_id == project_id).all()

        # Build adjacency list
        children: dict[str, list[str]] = {}
        for link in links:
            source = str(link.source_item_id)
            if source not in children:
                children[source] = []
            children[source].append(str(link.target_item_id))

        # Get all items for lookup
        all_items = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .all()
        )
        item_lookup = {str(i.id): i for i in all_items}

        # Traverse to the specified depth
        visited: set[str] = set()
        current_level: set[str] = {str(item.id)}

        for d in range(depth + 1):
            if not current_level:
                break

            if d == depth:
                # This is the depth we want
                level_items = []
                for item_id_str in current_level:
                    if item_id_str in visited:
                        continue
                    item_data = item_lookup.get(item_id_str)
                    if item_data:
                        level_items.append({
                            "id": item_id_str[:8],
                            "title": item_data.title,
                            "view": item_data.view,
                            "status": item_data.status,
                            "has_children": bool(children.get(item_id_str)),
                        })

                return {
                    "ok": True,
                    "depth": depth,
                    "items": level_items,
                    "count": len(level_items),
                }

            # Mark as visited and move to next level
            visited.update(current_level)

            next_level: set[str] = set()
            for item_id_str in current_level:
                for child_id in children.get(item_id_str, []):
                    if child_id not in visited:
                        next_level.add(child_id)
            current_level = next_level

        # Depth not reached
        return {
            "ok": True,
            "depth": depth,
            "items": [],
            "count": 0,
            "message": f"No items at depth {depth}",
        }


@mcp.tool(description="Get paginated items list")
def get_items_page(
    project_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    view: str | None = None,
    status: str | None = None,
    item_type: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    _ctx: object | None = None,
) -> dict[str, object]:
    """Get paginated items list with filtering.

    Args:
        project_id: Project ID (uses current if not specified).
        page: Page number (1-indexed).
        page_size: Items per page (default 50, max 100).
        view: Filter by view.
        status: Filter by status.
        item_type: Filter by item type.
        sort_by: Sort field (created_at, updated_at, title).
        sort_order: Sort order (asc or desc).
        ctx: MCP context.

    Returns:
        Paginated items with metadata.
    """
    project_id = _get_project_id(project_id)
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    storage = LocalStorageManager()
    with storage.get_session() as session:
        from tracertm.models.item import Item

        query = session.query(Item).filter(
            Item.project_id.like(f"{project_id}%"),
            Item.deleted_at.is_(None),
        )

        if view:
            query = query.filter(Item.view == view.upper())
        if status:
            query = query.filter(Item.status == status.lower())
        if item_type:
            query = query.filter(Item.item_type == item_type.lower())

        # Sorting
        order_col: object
        if sort_by == "title":
            order_col = Item.title
        elif sort_by == "updated_at":
            order_col = Item.updated_at
        else:
            order_col = Item.created_at

        query = query.order_by(order_col.asc()) if sort_order.lower() == "asc" else query.order_by(order_col.desc())

        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size

        items = query.offset(offset).limit(page_size).all()

        result_items = [
            {
                "id": str(item.id)[:8],
                "title": item.title,
                "view": item.view,
                "item_type": item.item_type,
                "status": item.status,
                "priority": item.priority,
                "owner": item.owner,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ]

        return {
            "ok": True,
            "page": page,
            "page_size": page_size,
            "total_items": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "items": result_items,
        }


@mcp.tool(description="Get paginated links list")
def get_links_page(
    project_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    link_type: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    _ctx: object | None = None,
) -> dict[str, object]:
    """Get paginated links list with filtering.

    Args:
        project_id: Project ID (uses current if not specified).
        page: Page number (1-indexed).
        page_size: Items per page (default 50, max 100).
        link_type: Filter by link type.
        source_id: Filter by source item ID.
        target_id: Filter by target item ID.
        ctx: MCP context.

    Returns:
        Paginated links with source/target details.
    """
    project_id = _get_project_id(project_id)
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    storage = LocalStorageManager()
    with storage.get_session() as session:
        from tracertm.models.item import Item
        from tracertm.models.link import Link

        query = session.query(Link).filter(Link.project_id.like(f"{project_id}%"))

        if link_type:
            query = query.filter(Link.link_type == link_type)
        if source_id:
            query = query.filter(Link.source_item_id.like(f"{source_id}%"))
        if target_id:
            query = query.filter(Link.target_item_id.like(f"{target_id}%"))

        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size

        links = query.offset(offset).limit(page_size).all()

        # Get item details
        item_ids = set()
        for link in links:
            item_ids.add(str(link.source_item_id))
            item_ids.add(str(link.target_item_id))

        items = session.query(Item).filter(Item.id.in_(item_ids)).all()
        item_lookup = {str(item.id): item for item in items}

        result_links = []
        for link in links:
            source = item_lookup.get(str(link.source_item_id))
            target = item_lookup.get(str(link.target_item_id))
            result_links.append({
                "id": str(link.id)[:8],
                "source_id": str(link.source_item_id)[:8],
                "source_title": source.title if source else None,
                "target_id": str(link.target_item_id)[:8],
                "target_title": target.title if target else None,
                "link_type": link.link_type,
                "created_at": link.created_at.isoformat() if link.created_at else None,
            })

        return {
            "ok": True,
            "page": page,
            "page_size": page_size,
            "total_links": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "links": result_links,
        }
