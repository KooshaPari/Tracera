"""FastAPI application for TraceRTM."""

from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
