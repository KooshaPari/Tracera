#!/usr/bin/env python3
"""TraceRTM MCP Server - FastMCP 2.13+ Implementation.

Exposes a complete TraceRTM-centric MCP interface (Phase 1: Tools):

Tools (21 total):
  Projects (4): create_project, list_projects, select_project, snapshot_project
  Items (7): create_item, get_item, update_item, delete_item, query_items, summarize_view, bulk_update_items
  Links (3): create_link, list_links, show_links
  Traceability (5): find_gaps, get_trace_matrix, analyze_impact, analyze_reverse_impact, project_health
  Graph (2): detect_cycles, shortest_path

See scripts/mcp/TRACERTM_MCP_TOOLS_SUMMARY.md for full reference.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import yaml

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.traceability_service import TraceabilityService
from tracertm.services.traceability_matrix_service import TraceabilityMatrixService
from tracertm.services.impact_analysis_service import ImpactAnalysisService
from tracertm.services.performance_service import PerformanceService
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.services.shortest_path_service import ShortestPathService

# ==========================================================================
# Server initialization
# ==========================================================================

mcp = FastMCP("tracertm-mcp")


# ==========================================================================
# Utilities
# ==========================================================================

def _get_config_manager() -> ConfigManager:
    """Get a ConfigManager instance.

    For now this uses the default config location (~/.config/tracertm).
    Later we can make this project-root aware if needed for tests.
    """

    return ConfigManager()


def _get_db_for_config(config: ConfigManager) -> DatabaseConnection:
    """Create and connect a DatabaseConnection from ConfigManager.

    Raises ToolError with a clear message if database_url is missing.
    """

    database_url = config.get("database_url")
    if not database_url:
        raise ToolError("No database configured. Run 'rtm config init' first.")

    db = DatabaseConnection(database_url)
    db.connect()
    return db


# ==========================================================================
# Tools: Projects
# ==========================================================================


@mcp.tool()
async def create_project(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new TraceRTM project in the configured database.

    This assumes `rtm config init` has already been run to set `database_url`.
    The new project is set as the current project.
    """

    config = _get_config_manager()
    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        project = Project(
            name=name,
            description=description or f"TraceRTM project: {name}",
            project_metadata={"created_via": "mcp"},
        )
        session.add(project)
        session.commit()

        # Set as current project
        config.set("current_project_id", str(project.id))
        config.set("current_project_name", project.name)

        return {
            "project_id": str(project.id),
            "name": project.name,
            "description": project.description or "",
        }


@mcp.tool()
async def list_projects() -> Dict[str, Any]:
    """List all TraceRTM projects.

    Returns a structured list of projects: id, name, description, created_at.
    """

    config = _get_config_manager()
    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        projects: List[Project] = session.query(Project).all()

        return {
            "projects": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "description": p.description or "",
                    "created_at": p.created_at.isoformat()
                    if getattr(p, "created_at", None)
                    else None,
                }
                for p in projects
            ]
        }


@mcp.tool()
async def select_project(project_id: str) -> Dict[str, Any]:
    """Select current project by ID.

    Updates ConfigManager's current_project_id/current_project_name so that
    subsequent item/link operations apply to this project.
    """

    config = _get_config_manager()
    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        project: Optional[Project] = (
            session.query(Project).filter(Project.id == project_id).first()
        )

        if not project:
            raise ToolError(f"Project not found: {project_id}")

        config.set("current_project_id", str(project.id))
        config.set("current_project_name", project.name)

        return {"project_id": str(project.id), "name": project.name}


@mcp.tool()
async def snapshot_project(project_id: str, label: str) -> Dict[str, Any]:
    """Create a lightweight snapshot record for a project.

    For now this writes metadata to
    `~/.config/tracertm/projects/<project_id>/snapshots.yaml`.
    """

    config = _get_config_manager()
    db = _get_db_for_config(config)

    from pathlib import Path
    from sqlalchemy.orm import Session

    # Verify the project exists
    with Session(db.engine) as session:  # type: ignore[arg-type]
        project: Optional[Project] = (
            session.query(Project).filter(Project.id == project_id).first()
        )
        if not project:
            raise ToolError(f"Project not found: {project_id}")

    project_dir = Path(config.projects_dir) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    snapshots_file = project_dir / "snapshots.yaml"

    snapshots: List[Dict[str, Any]] = []
    if snapshots_file.exists():
        existing = yaml.safe_load(snapshots_file.read_text()) or []
        if isinstance(existing, list):
            snapshots = existing

    snapshot_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    snapshots.append({"id": snapshot_id, "label": label, "created_at": created_at})
    snapshots_file.write_text(yaml.safe_dump(snapshots, default_flow_style=False))

    return {"snapshot_id": snapshot_id, "created_at": created_at}


# ==========================================================================
# Tools: Items & Links (full lifecycle + queries)
# ==========================================================================


@mcp.tool()
async def create_item(
    title: str,
    view: str,
    item_type: str,
    description: Optional[str] = None,
    status: str = "todo",
    priority: str = "medium",
    owner: Optional[str] = None,
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a new item in the current TraceRTM project (MCP wrapper).

    Mirrors `rtm item create` semantics but returns structured JSON.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError(
            "No current project. Call select_project first or use the CLI to initialize."
        )

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        item = Item(
            project_id=project_id,
            title=title,
            description=description,
            view=view.upper(),
            item_type=item_type,
            status=status,
            priority=priority,
            owner=owner,
            parent_id=parent_id,
            item_metadata=metadata or {},
        )
        session.add(item)
        session.commit()

        return {
            "id": str(item.id),
            "project_id": str(item.project_id),
            "title": item.title,
            "view": item.view,
            "item_type": item.item_type,
            "status": item.status,
            "priority": item.priority,
            "owner": item.owner,
            "parent_id": item.parent_id,
        }


@mcp.tool()
async def query_items(
    view: Optional[str] = None,
    item_type: Optional[str] = None,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Query items in the current project with simple filters.

    Filters mirror the CLI `rtm item list` command but return JSON.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        query = session.query(Item).filter(
            Item.project_id == project_id, Item.deleted_at.is_(None)
        )

        if view:
            query = query.filter(Item.view == view.upper())
        if item_type:
            query = query.filter(Item.item_type == item_type)
        if status:
            query = query.filter(Item.status == status)
        if owner:
            query = query.filter(Item.owner == owner)

        items = query.limit(max(1, min(limit, 500))).all()

        return {
            "project_id": str(project_id),
            "filters": {
                "view": view.upper() if view else None,
                "item_type": item_type,
                "status": status,
                "owner": owner,
                "limit": limit,
            },
            "items": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "view": i.view,
                    "item_type": i.item_type,
                    "status": i.status,
                    "priority": i.priority,
                    "owner": i.owner,
                }
                for i in items
            ],
        }


@mcp.tool()
async def summarize_view(view: str) -> Dict[str, Any]:
    """Summarize items in a given view for the current project.

    Returns counts by status and a small sample of items.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy import func
    from sqlalchemy.orm import Session

    view_upper = view.upper()

    with Session(db.engine) as session:  # type: ignore[arg-type]
        # Counts by status
        rows = (
            session.query(Item.status, func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                Item.view == view_upper,
            )
            .group_by(Item.status)
            .all()
        )
        counts_by_status = {status: count for status, count in rows}

        total_items = int(sum(counts_by_status.values()))

        # Sample of items (up to 20)
        sample_items = (
            session.query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                Item.view == view_upper,
            )
            .order_by(Item.created_at.desc())
            .limit(20)
            .all()
        )

        return {
            "project_id": str(project_id),
            "view": view_upper,
            "total_items": total_items,
            "counts_by_status": counts_by_status,
            "sample_items": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "item_type": i.item_type,
                    "status": i.status,
                    "priority": i.priority,
                    "owner": i.owner,
                }
                for i in sample_items
            ],
        }


@mcp.tool()
async def get_item(item_id: str) -> Dict[str, Any]:
    """Get a single item by ID (within the current project)."""

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        item = (
            session.query(Item)
            .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
            .first()
        )

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        return {
            "id": str(item.id),
            "project_id": str(item.project_id),
            "title": item.title,
            "description": item.description,
            "view": item.view,
            "item_type": item.item_type,
            "status": item.status,
            "priority": item.priority,
            "owner": item.owner,
            "parent_id": item.parent_id,
            "version": item.version,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            "metadata": item.item_metadata,
        }


@mcp.tool()
async def update_item(
    item_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    owner: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Update an existing item (optimistic locking via SQLAlchemy version)."""

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session
    from sqlalchemy.orm.exc import StaleDataError

    with Session(db.engine) as session:  # type: ignore[arg-type]
        item = (
            session.query(Item)
            .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
            .first()
        )

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        if title is not None:
            item.title = title
        if description is not None:
            item.description = description
        if status is not None:
            item.status = status
        if priority is not None:
            item.priority = priority
        if owner is not None:
            item.owner = owner
        if metadata is not None:
            item.item_metadata = metadata

        try:
            session.commit()
        except StaleDataError as exc:
            raise ToolError(
                f"Update conflict for item {item_id}: modified by another process"
            ) from exc

        return {
            "id": str(item.id),
            "project_id": str(item.project_id),
            "title": item.title,
            "view": item.view,
            "item_type": item.item_type,
            "status": item.status,
            "priority": item.priority,
            "owner": item.owner,
            "version": item.version,
        }


@mcp.tool()
async def delete_item(item_id: str) -> Dict[str, Any]:
    """Soft-delete an item in the current project (sets deleted_at)."""

    from datetime import datetime as _dt

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        item = (
            session.query(Item)
            .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
            .first()
        )

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        item.deleted_at = _dt.utcnow()
        session.commit()

        return {"id": str(item.id), "deleted_at": item.deleted_at.isoformat()}


@mcp.tool()
async def bulk_update_items(
    view: Optional[str] = None,
    status: Optional[str] = None,
    new_status: Optional[str] = None,
) -> Dict[str, Any]:
    """Bulk update item status in the current project.

    Mirrors `rtm item bulk-update` but *without* interactive confirmation.
    """

    if not new_status:
        raise ToolError("new_status is required for bulk_update_items")

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        query = session.query(Item).filter(
            Item.project_id == project_id, Item.deleted_at.is_(None)
        )

        if view:
            query = query.filter(Item.view == view.upper())
        if status:
            query = query.filter(Item.status == status)

        items = query.all()

        for item in items:
            item.status = new_status

        session.commit()

        return {
            "project_id": str(project_id),
            "updated_count": len(items),
            "new_status": new_status,
        }


# ==========================================================================
# Tools: Traceability & Analysis
# ==========================================================================


@mcp.tool()
async def find_gaps(from_view: str, to_view: str) -> Dict[str, Any]:
    """Find items in `from_view` that have no links to items in `to_view`.

    Uses the async TraceabilityService under the hood.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    # Use async engine/session from core.database for services
    from tracertm.core.database import get_session

    async with get_session() as session:
        service = TraceabilityService(session)
        matrix = await service.generate_matrix(
            project_id=str(project_id),
            source_view=from_view.upper(),
            target_view=to_view.upper(),
        )

        return {
            "project_id": str(project_id),
            "from_view": matrix.source_view,
            "to_view": matrix.target_view,
            "coverage_percentage": matrix.coverage_percentage,
            "gaps": matrix.gaps,
            "link_count": len(matrix.links),
        }


@mcp.tool()
async def get_trace_matrix(
    source_view: Optional[str] = None,
    target_view: Optional[str] = None,
) -> Dict[str, Any]:
    """Get a dense traceability matrix for the current project.

    Wraps TraceabilityMatrixService.generate_matrix.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    from tracertm.core.database import get_session

    async with get_session() as session:
        service = TraceabilityMatrixService(session)
        matrix = await service.generate_matrix(
            project_id=str(project_id),
            source_view=source_view.upper() if source_view else None,
            target_view=target_view.upper() if target_view else None,
        )

        return {
            "project_id": matrix.project_id,
            "rows": matrix.rows,
            "columns": matrix.columns,
            "matrix": matrix.matrix,
            "coverage": matrix.coverage,
            "total_links": matrix.total_links,
        }


@mcp.tool()
async def analyze_impact(
    item_id: str,
    max_depth: int = 5,
    link_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Analyze downstream impact of changing an item (BFS)."""

    from tracertm.core.database import get_session

    async with get_session() as session:
        service = ImpactAnalysisService(session)
        result = await service.analyze_impact(
            item_id=item_id,
            max_depth=max_depth,
            link_types=link_types,
        )

        return {
            "root_item_id": result.root_item_id,
            "root_item_title": result.root_item_title,
            "total_affected": result.total_affected,
            "max_depth_reached": result.max_depth_reached,
            "affected_by_depth": result.affected_by_depth,
            "affected_by_view": result.affected_by_view,
            "affected_items": result.affected_items,
            "critical_paths": result.critical_paths,
        }


@mcp.tool()
async def analyze_reverse_impact(
    item_id: str,
    max_depth: int = 5,
) -> Dict[str, Any]:
    """Analyze reverse impact (what depends on this item)."""

    from tracertm.core.database import get_session

    async with get_session() as session:
        service = ImpactAnalysisService(session)
        result = await service.analyze_reverse_impact(
            item_id=item_id,
            max_depth=max_depth,
        )

        return {
            "root_item_id": result.root_item_id,
            "root_item_title": result.root_item_title,
            "total_affected": result.total_affected,
            "max_depth_reached": result.max_depth_reached,
            "affected_by_depth": result.affected_by_depth,
            "affected_by_view": result.affected_by_view,
            "affected_items": result.affected_items,
            "critical_paths": result.critical_paths,
        }


@mcp.tool()
async def project_health() -> Dict[str, Any]:
    """High-level health metrics for the current project.

    Wraps PerformanceService.get_project_statistics.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    from tracertm.core.database import get_session

    async with get_session() as session:
        perf = PerformanceService(session)
        stats = await perf.get_project_statistics(str(project_id))

        return {
            "project_id": str(project_id),
            "item_count": stats["item_count"],
            "link_count": stats["link_count"],
            "density": stats["density"],
            "complexity": stats["complexity"],
            "views": stats["views"],
            "statuses": stats["statuses"],
        }


@mcp.tool()
async def detect_cycles() -> Dict[str, Any]:
    """Detect dependency cycles in the current project graph.

    Wraps CycleDetectionService.detect_cycles.
    """

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    from tracertm.core.database import get_session

    async with get_session() as session:
        service = CycleDetectionService(session)
        result = await service.detect_cycles(project_id=str(project_id))

        return {
            "project_id": str(project_id),
            "has_cycles": result.has_cycles,
            "cycle_count": result.total_cycles,
            "severity": result.severity,
            "affected_items": list(result.affected_items),
            "cycles": [
                {
                    "items": c.items,
                    "length": c.length,
                    "link_types": c.link_types,
                }
                for c in result.cycles
            ],
        }


@mcp.tool()
async def shortest_path(
    source_id: str,
    target_id: str,
) -> Dict[str, Any]:
    """Find the shortest dependency path between two items."""

    from tracertm.core.database import get_session

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    async with get_session() as session:
        service = ShortestPathService(session)
        result = await service.find_shortest_path(
            project_id=str(project_id),
            source_id=source_id,
            target_id=target_id,
        )

        return {
            "source_id": result.source_id,
            "target_id": result.target_id,
            "path": result.path,
            "distance": result.distance,
            "link_types": result.link_types,
            "exists": result.exists,
        }


@mcp.tool()
async def create_link(
    source_id: str,
    target_id: str,
    link_type: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a link between two items in the current project (with metadata)."""

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError(
            "No current project. Call select_project first or use the CLI to initialize."
        )

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        # Verify source and target exist in project
        source = (
            session.query(Item)
            .filter(Item.id == source_id, Item.project_id == project_id)
            .first()
        )
        target = (
            session.query(Item)
            .filter(Item.id == target_id, Item.project_id == project_id)
            .first()
        )

        if not source or not target:
            raise ToolError("Source or target item not found in current project.")

        link = Link(
            project_id=project_id,
            source_item_id=source_id,
            target_item_id=target_id,
            link_type=link_type,
            link_metadata=metadata or {},
        )
        session.add(link)
        session.commit()

        return {
            "id": str(link.id),
            "project_id": str(link.project_id),
            "source_id": str(link.source_item_id),
            "target_id": str(link.target_item_id),
            "link_type": link.link_type,
            "metadata": link.link_metadata,
        }


@mcp.tool()
async def list_links(
    item_id: Optional[str] = None,
    link_type: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """List links in the current project (optionally filtered by item and type)."""

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    with Session(db.engine) as session:  # type: ignore[arg-type]
        query = session.query(Link).filter(Link.project_id == project_id)

        if item_id:
            query = query.filter(
                (Link.source_item_id == item_id) | (Link.target_item_id == item_id)
            )
        if link_type:
            query = query.filter(Link.link_type == link_type)

        links = query.limit(max(1, min(limit, 500))).all()

        return {
            "project_id": str(project_id),
            "count": len(links),
            "links": [
                {
                    "id": str(l.id),
                    "source_id": str(l.source_item_id),
                    "target_id": str(l.target_item_id),
                    "link_type": l.link_type,
                    "metadata": l.link_metadata,
                }
                for l in links
            ],
        }


@mcp.tool()
async def show_links(
    item_id: str,
    view: Optional[str] = None,
) -> Dict[str, Any]:
    """Show all links for a specific item (grouped as incoming/outgoing)."""

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        raise ToolError("No current project. Call select_project first.")

    db = _get_db_for_config(config)

    from sqlalchemy.orm import Session

    view_upper = view.upper() if view else None

    with Session(db.engine) as session:  # type: ignore[arg-type]
        # Resolve item by prefix
        item = (
            session.query(Item)
            .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
            .first()
        )

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        links = (
            session.query(Link)
            .filter(
                ((Link.source_item_id == item.id) | (Link.target_item_id == item.id)),
                Link.project_id == project_id,
            )
            .all()
        )

        outgoing = []
        incoming = []

        for link in links:
            if link.source_item_id == item.id:
                target = session.query(Item).filter(Item.id == link.target_item_id).first()
                if target and (not view_upper or target.view == view_upper):
                    outgoing.append(
                        {
                            "link_id": str(link.id),
                            "type": link.link_type,
                            "target_id": str(target.id),
                            "target_title": target.title,
                            "target_view": target.view,
                        }
                    )
            else:
                source = session.query(Item).filter(Item.id == link.source_item_id).first()
                if source and (not view_upper or source.view == view_upper):
                    incoming.append(
                        {
                            "link_id": str(link.id),
                            "type": link.link_type,
                            "source_id": str(source.id),
                            "source_title": source.title,
                            "source_view": source.view,
                        }
                    )

        return {
            "item": {
                "id": str(item.id),
                "title": item.title,
                "view": item.view,
            },
            "outgoing": outgoing,
            "incoming": incoming,
        }


# ==========================================================================
# Middleware: basic logging (similar to bmm_server)
# ==========================================================================


class LoggingMiddleware(Middleware):
    """Log all tool calls for debugging."""

    async def on_tool_call(self, ctx: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]):
        print(f"[TRACE_RTM_MCP][TOOL] {tool_name} called with args: {arguments}")
        await ctx.next()


mcp.add_middleware(LoggingMiddleware())


# ==========================================================================
# Main entrypoint
# ==========================================================================

if __name__ == "__main__":
    # STDIO transport is ideal for Claude Desktop / droid
    mcp.run()

