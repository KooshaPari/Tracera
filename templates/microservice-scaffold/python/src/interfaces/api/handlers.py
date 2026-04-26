"""API handlers."""
from fastapi import APIRouter, HTTPException, Depends
from ..application.commands import CreateCommand, DeleteCommand
from ..application.queries import GetByIDQuery, ListQuery
from ..application.handlers import CommandHandler, QueryHandler
from ..domain.errors import NotFoundError, ValidationError
from ..infrastructure.adapters.persistence import PostgresAdapter
from ..infrastructure.adapters.messaging import NatsAdapter
from ..infrastructure.config import settings

router = APIRouter()


def get_handlers():
    """Get command and query handlers."""
    # This would normally use dependency injection
    # For simplicity, returning None - implement proper DI
    return None, None


@router.post("/entities")
async def create_entity(cmd: CreateCommand):
    """Create an entity."""
    handlers = get_handlers()
    if handlers is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    cmd_handler, _ = handlers
    try:
        entity = await cmd_handler.handle_create(cmd)
        return {"id": str(entity.id)}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={"code": e.code, "field": e.field})


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get an entity by ID."""
    handlers = get_handlers()
    if handlers is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    _, query_handler = handlers
    try:
        from uuid import UUID
        query = GetByIDQuery(id=UUID(entity_id))
        entity = await query_handler.handle_get_by_id(query)
        return {
            "id": str(entity.id),
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")


@router.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete an entity."""
    handlers = get_handlers()
    if handlers is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    cmd_handler, _ = handlers
    try:
        from uuid import UUID
        cmd = DeleteCommand(id=UUID(entity_id))
        await cmd_handler.handle_delete(cmd)
        return {"status": "deleted"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")


@router.get("/entities")
async def list_entities(page: int = 1, page_size: int = 20):
    """List entities."""
    handlers = get_handlers()
    if handlers is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    _, query_handler = handlers
    query = ListQuery(page=page, page_size=page_size)
    entities = await query_handler.handle_list(query)
    return {
        "items": [
            {
                "id": str(e.id),
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat(),
            }
            for e in entities
        ],
        "page": page,
        "page_size": page_size,
    }
