"""Graph utilities API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_cache_service, get_db
from tracertm.models.graph import Graph
from tracertm.repositories.link_repository import LinkRepository
from tracertm.services.cache_service import CacheService

router = APIRouter(prefix="/projects/{project_id}", tags=["graphs"])


def ensure_project_access(project_id: str, claims: dict[str, Any] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


@router.get("/graph/neighbors")
async def get_graph_neighbors(
    project_id: str,
    item_id: str,
    direction: str = "both",  # "in", "out", "both"
    graph_id: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get neighbors of an item in the graph."""
    ensure_project_access(project_id, claims)
    repo = LinkRepository(db)

    neighbors: list[dict[str, Any]] = []
    if direction in {"out", "both"}:
        out_links = await repo.get_by_source(item_id, graph_id=graph_id)
        neighbors.extend(
            {
                "id": str(link.id),
                "item_id": str(link.target_item_id),
                "link_type": link.link_type,
                "graph_id": link.graph_id,
                "direction": "out",
            }
            for link in out_links
        )

    if direction in {"in", "both"}:
        in_links = await repo.get_by_target(item_id, graph_id=graph_id)
        neighbors.extend(
            {
                "id": str(link.id),
                "item_id": str(link.source_item_id),
                "link_type": link.link_type,
                "graph_id": link.graph_id,
                "direction": "in",
            }
            for link in in_links
        )

    return {
        "project_id": project_id,
        "item_id": item_id,
        "graph_id": graph_id,
        "direction": direction,
        "neighbors": neighbors,
        "total": len(neighbors),
    }


@router.get("/graphs")
async def list_graphs(
    project_id: str,
    graph_type: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
):
    """List graphs for a project (cached for 5 minutes)."""
    ensure_project_access(project_id, claims)

    cache_key = cache._generate_key("graph", project_id=project_id, graph_type=graph_type)
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    query = select(Graph).where(Graph.project_id == project_id)
    if graph_type:
        query = query.where(Graph.graph_type == graph_type)
    result = await db.execute(query.order_by(Graph.name))
    graphs = result.scalars().all()

    response = {
        "project_id": project_id,
        "graphs": [
            {
                "id": graph.id,
                "name": graph.name,
                "graph_type": graph.graph_type,
                "description": graph.description,
                "root_item_id": graph.root_item_id,
                "graph_version": graph.graph_version,
                "graph_rules": graph.graph_rules,
                "metadata": graph.graph_metadata,
            }
            for graph in graphs
        ],
        "total": len(graphs),
    }

    await cache.set(cache_key, response, cache_type="graph")
    return response


@router.get("/graph")
async def get_graph_projection(
    project_id: str,
    graph_id: str | None = None,
    graph_type: str | None = None,
    include_nodes: bool = True,
    include_links: bool = True,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
):
    """Get a graph projection by graph_id or graph_type (cached for 10 minutes)."""
    ensure_project_access(project_id, claims)

    cache_key = cache._generate_key(
        "graph_full",
        project_id=project_id,
        graph_id=graph_id,
        graph_type=graph_type,
        include_nodes=include_nodes,
        include_links=include_links,
    )
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    from tracertm.services.graph_service import GraphService

    service = GraphService(db)
    data = await service.get_graph(
        project_id=project_id,
        graph_id=graph_id,
        graph_type=graph_type,
        include_nodes=include_nodes,
        include_links=include_links,
    )

    result = {"project_id": project_id, **data}
    await cache.set(cache_key, result, cache_type="graph_full")
    return result


@router.get("/graphs/{graph_id}/validate")
async def validate_graph(
    project_id: str,
    graph_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Validate a graph against edge/node rules."""
    ensure_project_access(project_id, claims)
    from tracertm.services.graph_validation_service import GraphValidationService

    service = GraphValidationService(db)
    return await service.validate_graph(project_id=project_id, graph_id=graph_id)


@router.post("/graphs/{graph_id}/snapshot")
async def create_graph_snapshot(
    project_id: str,
    graph_id: str,
    created_by: str | None = None,
    description: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Create a graph snapshot."""
    ensure_project_access(project_id, claims)
    ensure_write_permission(claims, action="create_snapshot")
    from tracertm.services.graph_snapshot_service import GraphSnapshotService

    service = GraphSnapshotService(db)
    snapshot = await service.create_snapshot(
        project_id=project_id,
        graph_id=graph_id,
        created_by=created_by,
        description=description,
    )
    return {
        "snapshot_id": snapshot.id,
        "version": snapshot.version,
        "hash": snapshot.snapshot_hash,
    }


@router.get("/graphs/{graph_id}/snapshot")
async def get_graph_snapshot(
    project_id: str,
    graph_id: str,
    version: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get a graph snapshot by version (latest if omitted)."""
    from tracertm.services.graph_snapshot_service import GraphSnapshotService

    service = GraphSnapshotService(db)
    snapshot = await service.get_snapshot(
        project_id=project_id,
        graph_id=graph_id,
        version=version,
    )
    if not snapshot:
        return {"error": "snapshot_not_found"}
    return {
        "snapshot_id": snapshot.id,
        "version": snapshot.version,
        "hash": snapshot.snapshot_hash,
        "payload": snapshot.snapshot_json,
    }


@router.get("/graphs/{graph_id}/diff")
async def diff_graph_snapshots(
    project_id: str,
    graph_id: str,
    from_version: int,
    to_version: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Diff two graph snapshots."""
    from tracertm.services.graph_snapshot_service import GraphSnapshotService

    service = GraphSnapshotService(db)
    return await service.diff_snapshots(
        project_id=project_id,
        graph_id=graph_id,
        from_version=from_version,
        to_version=to_version,
    )


@router.get("/graphs/{graph_id}/report")
async def graph_report(
    project_id: str,
    graph_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Graph QA report for coverage and missing mappings."""
    from tracertm.services.graph_report_service import GraphReportService

    service = GraphReportService(db)
    return await service.build_report(project_id=project_id, graph_id=graph_id)
