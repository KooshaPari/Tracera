"""FastAPI application for TraceRTM."""

from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection

# Create FastAPI app
app = FastAPI(
    title="TraceRTM API",
    description="Traceability Requirements Tracking Management API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    config_manager = ConfigManager()
    database_url = config_manager.get("database_url")

    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")

    db = DatabaseConnection(database_url)
    db.connect()

    try:
        yield db.session
    finally:
        await db.session.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TraceRTM API",
    }


# Items endpoints
@app.get("/api/v1/items")
async def list_items(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List items in a project."""
    from tracertm.repositories.item_repository import ItemRepository

    repo = ItemRepository(db)
    items = await repo.get_by_project(project_id)

    return {
        "total": len(items),
        "items": [
            {
                "id": str(item.id),
                "title": item.title,
                "view": item.view,
                "status": item.status,
            }
            for item in items[skip : skip + limit]
        ],
    }


@app.get("/api/v1/items/{item_id}")
async def get_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific item."""
    from tracertm.repositories.item_repository import ItemRepository

    repo = ItemRepository(db)
    item = await repo.get_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "id": str(item.id),
        "title": item.title,
        "description": item.description,
        "view": item.view,
        "status": item.status,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


# Links endpoints
@app.get("/api/v1/links")
async def list_links(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List links in a project."""
    from tracertm.repositories.link_repository import LinkRepository

    repo = LinkRepository(db)
    links = await repo.get_by_project(project_id)

    return {
        "total": len(links),
        "links": [
            {
                "id": str(link.id),
                "source_id": str(link.source_item_id),
                "target_id": str(link.target_item_id),
                "type": link.link_type,
            }
            for link in links[skip : skip + limit]
        ],
    }


# Analysis endpoints
@app.get("/api/v1/analysis/impact/{item_id}")
async def get_impact_analysis(
    item_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get impact analysis for an item."""
    from tracertm.services.impact_analysis_service import ImpactAnalysisService

    service = ImpactAnalysisService(db)
    result = await service.analyze_impact(item_id)

    return {
        "root_item_id": result.root_item_id,
        "total_affected": result.total_affected,
        "max_depth": result.max_depth_reached,
        "affected_items": result.affected_items,
    }


@app.get("/api/v1/analysis/cycles/{project_id}")
async def detect_cycles(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Detect cycles in project dependency graph."""
    from tracertm.services.cycle_detection_service import CycleDetectionService

    service = CycleDetectionService(db)
    result = await service.detect_cycles(project_id)

    return {
        "has_cycles": result.has_cycles,
        "total_cycles": result.total_cycles,
        "severity": result.severity,
        "affected_items": list(result.affected_items),
    }


@app.get("/api/v1/analysis/shortest-path")
async def find_shortest_path(
    project_id: str,
    source_id: str,
    target_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Find shortest path between two items."""
    from tracertm.services.shortest_path_service import ShortestPathService

    service = ShortestPathService(db)
    result = await service.find_shortest_path(project_id, source_id, target_id)

    return {
        "exists": result.exists,
        "distance": result.distance,
        "path": result.path,
        "link_types": result.link_types,
    }


# Projects endpoints
@app.get("/api/v1/projects")
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all projects."""
    from tracertm.repositories.project_repository import ProjectRepository

    repo = ProjectRepository(db)
    projects = await repo.get_all()

    return {
        "total": len(projects),
        "projects": [
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "metadata": project.metadata,
            }
            for project in projects[skip : skip + limit]
        ],
    }


@app.get("/api/v1/projects/{project_id}")
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project."""
    from tracertm.repositories.project_repository import ProjectRepository

    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "metadata": project.metadata,
    }


class CreateProjectRequest(BaseModel):
    """Request model for create project endpoint."""
    name: str
    description: str | None = None
    metadata: dict | None = None


@app.post("/api/v1/projects")
async def create_project(
    request: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    from tracertm.repositories.project_repository import ProjectRepository

    repo = ProjectRepository(db)
    project = await repo.create(
        name=request.name,
        description=request.description,
        metadata=request.metadata,
    )

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "metadata": project.metadata,
    }


class UpdateProjectRequest(BaseModel):
    """Request model for update project endpoint."""
    name: str | None = None
    description: str | None = None
    metadata: dict | None = None


@app.put("/api/v1/projects/{project_id}")
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update a project."""
    from tracertm.repositories.project_repository import ProjectRepository

    repo = ProjectRepository(db)
    project = await repo.update(
        project_id=project_id,
        name=request.name,
        description=request.description,
        metadata=request.metadata,
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "metadata": project.metadata,
    }


@app.delete("/api/v1/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project."""
    from tracertm.repositories.project_repository import ProjectRepository
    from tracertm.repositories.item_repository import ItemRepository
    from tracertm.repositories.link_repository import LinkRepository
    from sqlalchemy import delete
    from tracertm.models.project import Project
    from tracertm.models.item import Item
    from tracertm.models.link import Link

    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete all items and links for this project (cascade delete)
    link_repo = LinkRepository(db)
    item_repo = ItemRepository(db)
    
    # Get all links and items for the project
    links = await link_repo.get_by_project(project_id)
    items = await item_repo.list_all(project_id)
    
    # Delete links
    for link in links:
        await link_repo.delete(str(link.id))
    
    # Delete items (this should cascade delete their links too)
    # Note: ItemRepository.delete may not exist, so we'll use SQL directly
    from tracertm.models.item import Item
    await db.execute(delete(Item).where(Item.project_id == project_id))
    
    # Delete project
    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()

    return {"success": True, "message": "Project deleted successfully"}


# Export/Import endpoints
@app.get("/api/v1/projects/{project_id}/export")
async def export_project(
    project_id: str,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
):
    """Export project data to various formats."""
    from tracertm.services.export_import_service import ExportImportService

    service = ExportImportService(db)

    if format == "json":
        result = await service.export_to_json(project_id)
    elif format == "csv":
        result = await service.export_to_csv(project_id)
    elif format == "markdown":
        result = await service.export_to_markdown(project_id)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Supported formats: json, csv, markdown",
        )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


class ImportRequest(BaseModel):
    """Request model for import endpoint."""
    format: str
    data: str


@app.post("/api/v1/projects/{project_id}/import")
async def import_project(
    project_id: str,
    request: ImportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import project data from various formats."""
    from tracertm.services.export_import_service import ExportImportService

    service = ExportImportService(db)

    if request.format == "json":
        result = await service.import_from_json(project_id, request.data)
    elif request.format == "csv":
        result = await service.import_from_csv(project_id, request.data)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {request.format}. Supported formats: json, csv",
        )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# Sync endpoints
@app.get("/api/v1/projects/{project_id}/sync/status")
async def get_sync_status(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get sync status for a project."""
    from tracertm.services.sync_service import SyncService

    service = SyncService(db)
    # In a real implementation, this would check actual sync status
    # For now, return a mock status
    return {
        "project_id": project_id,
        "status": "synced",
        "last_synced": None,
        "pending_changes": 0,
    }


@app.post("/api/v1/projects/{project_id}/sync")
async def sync_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Execute sync for a project."""
    from tracertm.services.sync_service import SyncService

    service = SyncService(db)
    result = await service.sync()

    return {
        "project_id": project_id,
        "status": "synced",
        "result": result,
    }


# Advanced Search endpoint
class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search endpoint."""
    query: str | None = None
    filters: dict | None = None


@app.post("/api/v1/projects/{project_id}/search/advanced")
async def advanced_search(
    project_id: str,
    request: AdvancedSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Advanced search with filters and query."""
    from tracertm.services.search_service import SearchService

    service = SearchService(db)
    results = await service.search(query=request.query, filters=request.filters or {})

    return {
        "project_id": project_id,
        "query": request.query,
        "filters": request.filters,
        "results": results,
        "total": len(results),
    }


# Link update endpoint
class UpdateLinkRequest(BaseModel):
    """Request model for update link endpoint."""
    link_type: str | None = None
    metadata: dict | None = None


@app.put("/api/v1/links/{link_id}")
async def update_link(
    link_id: str,
    request: UpdateLinkRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update a link."""
    from tracertm.repositories.link_repository import LinkRepository

    repo = LinkRepository(db)
    link = await repo.get_by_id(link_id)

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if request.link_type is not None:
        link.link_type = request.link_type
    if request.metadata is not None:
        link.metadata = request.metadata

    await db.flush()
    await db.refresh(link)

    return {
        "id": str(link.id),
        "source_id": str(link.source_item_id),
        "target_id": str(link.target_item_id),
        "type": link.link_type,
        "metadata": link.metadata,
    }


# Graph neighbors endpoint
@app.get("/api/v1/projects/{project_id}/graph/neighbors")
async def get_graph_neighbors(
    project_id: str,
    item_id: str,
    direction: str = "both",  # "in", "out", "both"
    db: AsyncSession = Depends(get_db),
):
    """Get neighbors of an item in the graph."""
    from tracertm.repositories.link_repository import LinkRepository

    repo = LinkRepository(db)

    neighbors = []
    if direction in ("out", "both"):
        out_links = await repo.get_by_source(item_id)
        neighbors.extend(
            {
                "id": str(link.id),
                "item_id": str(link.target_item_id),
                "link_type": link.link_type,
                "direction": "out",
            }
            for link in out_links
        )

    if direction in ("in", "both"):
        in_links = await repo.get_by_target(item_id)
        neighbors.extend(
            {
                "id": str(link.id),
                "item_id": str(link.source_item_id),
                "link_type": link.link_type,
                "direction": "in",
            }
            for link in in_links
        )

    return {
        "project_id": project_id,
        "item_id": item_id,
        "direction": direction,
        "neighbors": neighbors,
        "total": len(neighbors),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
