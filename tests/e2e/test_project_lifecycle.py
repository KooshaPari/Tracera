"""End-to-end project lifecycle test with a live FastAPI app.

The app is assembled in-process, but requests go through HTTPX ASGI transport
so the workflow exercises real HTTP request/response handling instead of mocks.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

pytestmark = [pytest.mark.integration, pytest.mark.slow]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _src_root() -> Path:
    return _repo_root() / "src"


def _install_namespace_stubs() -> None:
    tracertm_root = _src_root() / "tracertm"
    for package_dir in [tracertm_root, *[path for path in tracertm_root.rglob("*") if path.is_dir()]]:
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            continue
        package_name = "tracertm" if package_dir == tracertm_root else "tracertm." + ".".join(
            package_dir.relative_to(tracertm_root).parts
        )
        module = sys.modules.get(package_name)
        if module is None:
            module = types.ModuleType(package_name)
            sys.modules[package_name] = module
        module.__path__ = [str(package_dir)]  # type: ignore[attr-defined]


def _install_test_stubs() -> None:
    concurrency_module = types.ModuleType("tracertm.core.concurrency")
    concurrency_module.ConcurrencyError = RuntimeError  # type: ignore[attr-defined]
    sys.modules["tracertm.core.concurrency"] = concurrency_module


_install_namespace_stubs()
_install_test_stubs()

from tracertm.models.graph import Graph
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.repositories.project_repository import ProjectRepository


class _ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    metadata: dict[str, Any] | None = None


class _ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


class _ItemCreate(BaseModel):
    project_id: str
    title: str
    type: str
    view: str | None = None
    status: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


class _LinkCreate(BaseModel):
    project_id: str
    source_id: str
    target_id: str
    type: str
    metadata: dict[str, Any] | None = None


class _FakeCacheService:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        return self._store.get(key)

    async def set(self, key: str, value: Any, *_: Any, **__: Any) -> None:
        self._store[key] = value

    async def clear_prefix(self, prefix: str) -> None:
        for key in [name for name in self._store if name.startswith(f"tracertm:{prefix}:")]:
            self._store.pop(key, None)

    async def invalidate_project(self, project_id: str) -> None:
        del project_id
        self._store.clear()

    def _generate_key(self, prefix: str, **kwargs: Any) -> str:
        return f"tracertm:{prefix}:test"


@pytest_asyncio.fixture
async def app(test_db_engine: Any) -> AsyncGenerator[FastAPI, None]:
    cache = _FakeCacheService()
    default_graph_ids: dict[str, str] = {}
    async_session_factory = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as async_db_session:
        async def get_db() -> AsyncGenerator[Any, None]:
            yield async_db_session

        async def get_cache_service() -> _FakeCacheService:
            return cache

        def auth_guard() -> dict[str, Any]:
            return {
                "sub": "e2e-user",
                "email": "kooshapari@gmail.com",
                "role": "admin",
            }

        application = FastAPI()

        @application.get("/health")
        async def health_check() -> dict[str, str]:
            return {"status": "healthy", "service": "TraceRTM API"}

        @application.get("/api/v1/projects")
        async def list_projects(
            skip: int = 0,
            limit: int = 100,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
            _cache: _FakeCacheService = Depends(get_cache_service),
        ) -> dict[str, Any]:
            repo = ProjectRepository(db)
            projects = await repo.get_all()
            payload = [
                {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "metadata": getattr(project, "project_metadata", None) or {},
                }
                for project in projects[skip : skip + limit]
            ]
            return {"total": len(projects), "projects": payload}

        @application.get("/api/v1/projects/{project_id}")
        async def get_project(
            project_id: str,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
            _cache: _FakeCacheService = Depends(get_cache_service),
        ) -> dict[str, Any]:
            project = await ProjectRepository(db).get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            return {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "metadata": getattr(project, "project_metadata", None) or {},
            }

        @application.post("/api/v1/projects")
        async def create_project(
            request: _ProjectCreate,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
            cache_service: _FakeCacheService = Depends(get_cache_service),
        ) -> dict[str, Any]:
            project = await ProjectRepository(db).create(
                name=request.name,
                description=request.description,
                metadata=request.metadata,
            )
            graph = Graph(
                id=str(uuid4()),
                project_id=project.id,
                name="Default graph",
                graph_type="default",
                description="Default project graph",
            )
            db.add(graph)
            default_graph_ids[str(project.id)] = str(graph.id)
            await db.commit()
            await cache_service.clear_prefix("projects")
            return {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "metadata": getattr(project, "project_metadata", None) or {},
            }

        @application.put("/api/v1/projects/{project_id}")
        async def update_project(
            project_id: str,
            request: _ProjectUpdate,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
        ) -> dict[str, Any]:
            project = await ProjectRepository(db).update(
                project_id=project_id,
                name=request.name,
                description=request.description,
                metadata=request.metadata,
            )
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            await db.commit()
            return {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "metadata": getattr(project, "project_metadata", None) or {},
            }

        @application.delete("/api/v1/projects/{project_id}")
        async def delete_project(
            project_id: str,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
        ) -> dict[str, Any]:
            await db.execute(delete(Link).where(Link.project_id == project_id))
            await db.execute(delete(Item).where(Item.project_id == project_id))
            await db.execute(delete(Graph).where(Graph.project_id == project_id))
            project = await ProjectRepository(db).get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            await db.delete(project)
            await db.commit()
            return {"success": True, "message": "Project deleted successfully"}

        @application.post("/api/v1/items")
        async def create_item(
            request: _ItemCreate,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
            cache_service: _FakeCacheService = Depends(get_cache_service),
        ) -> dict[str, Any]:
            item = Item(
                project_id=request.project_id,
                title=request.title,
                view=(request.view or request.type.upper()).upper(),
                item_type=request.type,
                description=request.description,
                status=request.status or "todo",
                item_metadata=request.metadata or {},
                priority=0,
            )
            db.add(item)
            await db.commit()
            await db.refresh(item)
            await cache_service.invalidate_project(request.project_id)
            return {
                "id": str(item.id),
                "title": item.title,
                "view": item.view,
                "status": item.status,
                "type": item.item_type,
                "description": item.description,
                "priority": getattr(item, "priority", None),
            }

        @application.post("/api/v1/links")
        async def create_link(
            request: _LinkCreate,
            _claims: dict[str, Any] = Depends(auth_guard),
            db: Any = Depends(get_db),
            cache_service: _FakeCacheService = Depends(get_cache_service),
        ) -> dict[str, Any]:
            graph_id = default_graph_ids.get(request.project_id)
            if not graph_id:
                raise HTTPException(status_code=404, detail="Project graph not found")
            link = Link(
                project_id=request.project_id,
                graph_id=graph_id,
                source_id=request.source_id,
                target_id=request.target_id,
                type=request.type,
                metadata=request.metadata or {},
            )
            db.add(link)
            await db.commit()
            await db.refresh(link)
            await cache_service.invalidate_project(request.project_id)
            return {
                "id": str(link.id),
                "source_id": str(link.source_item_id),
                "target_id": str(link.target_item_id),
                "type": link.link_type,
                "metadata": getattr(link, "link_metadata", None) or {},
            }

        yield application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_project_lifecycle_roundtrip(client: AsyncClient) -> None:
    project_name = f"E2E Project {uuid4()}"

    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": project_name,
            "description": "Project lifecycle E2E",
            "metadata": {"source": "pytest"},
        },
    )
    assert create_response.status_code == 200, create_response.text
    project = create_response.json()
    project_id = project["id"]

    list_response = await client.get("/api/v1/projects")
    assert list_response.status_code == 200, list_response.text
    projects = list_response.json()["projects"]
    assert any(entry["id"] == project_id for entry in projects)

    item_response = await client.post(
        "/api/v1/items",
        json={
            "project_id": project_id,
            "title": "Lifecycle item",
            "type": "feature",
            "view": "FEATURE",
            "status": "todo",
            "description": "Created through the live app",
            "metadata": {"origin": "e2e"},
        },
    )
    assert item_response.status_code == 200, item_response.text
    item = item_response.json()
    item_id = item["id"]

    update_response = await client.put(
        f"/api/v1/projects/{project_id}",
        json={
            "name": f"{project_name} updated",
            "description": "Updated project description",
            "metadata": {"source": "pytest", "updated": True},
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated_project = update_response.json()
    assert updated_project["name"].endswith("updated")

    link_response = await client.post(
        "/api/v1/links",
        json={
            "project_id": project_id,
            "source_id": item_id,
            "target_id": item_id,
            "type": "RELATES_TO",
            "metadata": {"kind": "self-check"},
        },
    )
    assert link_response.status_code == 200, link_response.text
    link = link_response.json()
    assert link["source_id"] == item_id
    assert link["target_id"] == item_id

    delete_response = await client.delete(f"/api/v1/projects/{project_id}")
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["success"] is True

    after_delete = await client.get(f"/api/v1/projects/{project_id}")
    assert after_delete.status_code == 404
