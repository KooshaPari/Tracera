"""TraceRTM MCP Server - FastMCP 3.0.0b1 Implementation.

Exposes a complete TraceRTM-centric MCP interface (Phase 1: Tools):

Tools (21 total):
  Projects (4): create_project, list_projects, select_project, snapshot_project
  Items (7): create_item, get_item, update_item, delete_item, query_items, summarize_view, bulk_update_items
  Links (3): create_link, list_links, show_links
  Traceability (5): find_gaps, get_trace_matrix, analyze_impact, analyze_reverse_impact, project_health
  Graph (2): detect_cycles, shortest_path

See scripts/mcp/TRACERTM_MCP_TOOLS_SUMMARY.md for full reference.


Functional Requirements: FR-MCP-001, FR-MCP-002, FR-MCP-009
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml
from fastmcp.exceptions import ToolError

from tracertm.api.http_client import TraceRTMHttpClient, TraceRTMHttpError
from tracertm.config.manager import ConfigManager
from tracertm.mcp.api_client import get_api_client
from tracertm.mcp.core import mcp

HTTP_NOT_FOUND = 404

# ==========================================================================
# Utilities
# ==========================================================================


def _get_config_manager() -> ConfigManager:
    """Get a ConfigManager instance.

    For now this uses the default config location (~/.tracertm).
    Later we can make this project-root aware if needed for tests.
    """
    return ConfigManager()


def _api_client() -> TraceRTMHttpClient:
    """Get HTTP API client for canonical backend operations."""
    return get_api_client()


# ==========================================================================
# ==========================================================================


@mcp.tool()
async def create_project(name: str, description: str | None = None) -> dict[str, object]:
    """Create a new TraceRTM project in the configured database.

    This assumes `rtm config init` has already been run to set `database_url`.
    The new project is set as the current project.
    """
    await asyncio.sleep(0)
    config = _get_config_manager()
    client = _api_client()
    try:
        project = client.post(
            "/api/v1/projects",
            json={
                "name": name,
                "description": description or f"TraceRTM project: {name}",
                "metadata": {"created_via": "mcp"},
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    project_id = str(project.get("id") or project.get("project_id"))
    config.set("current_project_id", project_id)
    config.set("current_project_name", project.get("name", name))

    return {
        "project_id": project_id,
        "name": project.get("name", name),
        "description": project.get("description") or "",
    }


@mcp.tool()
async def list_projects() -> dict[str, object]:
    """List all TraceRTM projects.

    Returns a structured list of projects: id, name, description, created_at.
    """
    await asyncio.sleep(0)
    client = _api_client()
    try:
        result = client.get("/api/v1/projects")
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    projects = result.get("projects", result if isinstance(result, list) else [])
    return {"projects": projects}


@mcp.tool()
async def select_project(project_id: str) -> dict[str, object]:
    """Select current project by ID.

    Updates ConfigManager's current_project_id/current_project_name so that
    subsequent item/link operations apply to this project.
    """
    await asyncio.sleep(0)
    config = _get_config_manager()
    client = _api_client()
    project: dict[str, object] | None = None
    try:
        project = client.get(f"/api/v1/projects/{project_id}")
    except TraceRTMHttpError:
        # Fallback: prefix match from list
        try:
            listed = client.get("/api/v1/projects")
        except TraceRTMHttpError as exc:
            raise ToolError(str(exc)) from exc
        candidates = listed.get("projects", [])
        for cand in candidates:
            if str(cand.get("id", "")).startswith(project_id):
                project = cand
                break
    if not project:
        msg = f"Project not found: {project_id}"
        raise ToolError(msg)

    config.set("current_project_id", str(project.get("id")))
    config.set("current_project_name", project.get("name"))
    return {"project_id": str(project.get("id")), "name": project.get("name")}


@mcp.tool()
async def snapshot_project(project_id: str, label: str) -> dict[str, object]:
    """Create a lightweight snapshot record for a project.

    For now this writes metadata to
    `~/.tracertm/projects/<project_id>/snapshots.yaml`.
    """
    await asyncio.sleep(0)
    config = _get_config_manager()
    client = _api_client()
    try:
        client.get(f"/api/v1/projects/{project_id}")
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    project_dir = Path(config.projects_dir) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    snapshots_file = project_dir / "snapshots.yaml"

    snapshots: list[dict[str, object]] = []
    if snapshots_file.exists():
        existing = yaml.safe_load(snapshots_file.read_text()) or []
        if isinstance(existing, list):
            snapshots = existing

    snapshot_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat() + "Z"

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
    description: str | None = None,
    status: str = "todo",
    priority: str = "medium",
    owner: str | None = None,
    parent_id: str | None = None,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Create a new item in the current TraceRTM project (MCP wrapper).

    Mirrors `rtm item create` semantics but returns structured JSON.
    """
    await asyncio.sleep(0)
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        item = client.post(
            "/api/v1/items",
            json={
                "project_id": project_id,
                "title": title,
                "type": item_type,
                "view": view.upper(),
                "description": description,
                "status": status,
                "priority": priority,
                "parent_id": parent_id,
                "metadata": metadata or {},
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": item.get("id"),
        "project_id": project_id,
        "title": item.get("title", title),
        "view": item.get("view", view.upper()),
        "item_type": item.get("type", item_type),
        "status": item.get("status", status),
        "priority": item.get("priority", priority),
        "owner": owner,
        "parent_id": parent_id,
    }


@mcp.tool()
async def query_items(
    view: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    limit: int = 50,
) -> dict[str, object]:
    """Query items in the current project with simple filters.

    Filters mirror the CLI `rtm item list` command but return JSON.
    """
    await asyncio.sleep(0)
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            "/api/v1/items",
            params={
                "project_id": project_id,
                "view": view,
                "status": status,
                "limit": max(1, min(limit, 500)),
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    items = result.get("items", result if isinstance(result, list) else [])
    if item_type:
        items = [item for item in items if item.get("type") == item_type or item.get("item_type") == item_type]
    if owner:
        items = [item for item in items if item.get("owner") == owner]
    return {
        "project_id": str(project_id),
        "filters": {
            "view": view.upper() if view else None,
            "item_type": item_type,
            "status": status,
            "owner": owner,
            "limit": limit,
        },
        "items": items,
    }


@mcp.tool()
async def summarize_view(view: str) -> dict[str, object]:
    """Summarize items in a given view for the current project.

    Returns counts by status and a small sample of items.
    """
    await asyncio.sleep(0)
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        summary = client.get(
            "/api/v1/items/summary",
            params={"project_id": project_id, "view": view},
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return summary


@mcp.tool()
async def get_item(item_id: str) -> dict[str, object]:
    """Get a single item by ID (within the current project)."""
    await asyncio.sleep(0)
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        return client.get(f"/api/v1/items/{item_id}")
    except TraceRTMHttpError:
        # Fallback: prefix/external_id match via list
        try:
            result = client.get(
                "/api/v1/items",
                params={"project_id": project_id, "limit": 500},
            )
        except TraceRTMHttpError as exc:
            raise ToolError(str(exc)) from exc
        items = result.get("items", [])
        for entry in items:
            candidate_id = str(entry.get("id", ""))
            external_id = str(entry.get("external_id", ""))
            if candidate_id.startswith(item_id) or external_id.startswith(item_id):
                return entry
        msg = f"Item not found: {item_id}"
        raise ToolError(msg) from None


@mcp.tool()
def update_item(
    item_id: str,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Update an existing item (optimistic locking via SQLAlchemy version)."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    payload = {
        key: value
        for key, value in {
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "owner": owner,
            "metadata": metadata,
        }.items()
        if value is not None
    }

    resolved_id = item_id
    try:
        item = client.put(f"/api/v1/items/{resolved_id}", json=payload)
    except TraceRTMHttpError as exc:
        if exc.status != HTTP_NOT_FOUND:
            raise ToolError(str(exc)) from exc
        try:
            result = client.get(
                "/api/v1/items",
                params={"project_id": project_id, "limit": 500},
            )
        except TraceRTMHttpError as inner_exc:
            raise ToolError(str(inner_exc)) from inner_exc
        candidates = result.get("items", [])
        resolved_id = None  # type: ignore[assignment]
        for entry in candidates:
            candidate_id = str(entry.get("id", ""))
            external_id = str(entry.get("external_id", ""))
            if candidate_id.startswith(item_id) or external_id.startswith(item_id):
                resolved_id = candidate_id
                break
        if not resolved_id:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg) from None
        try:
            item = client.put(f"/api/v1/items/{resolved_id}", json=payload)
        except TraceRTMHttpError as inner_exc:
            raise ToolError(str(inner_exc)) from inner_exc

    return {
        "id": item.get("id", resolved_id),
        "project_id": item.get("project_id", project_id),
        "title": item.get("title", title),
        "view": item.get("view"),
        "item_type": item.get("type") or item.get("item_type"),
        "status": item.get("status", status),
        "priority": item.get("priority", priority),
        "owner": item.get("owner", owner),
        "version": item.get("version"),
    }


@mcp.tool()
def delete_item(item_id: str) -> dict[str, object]:
    """Soft-delete an item in the current project (sets deleted_at)."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    resolved_id = item_id
    try:
        result = client.delete(f"/api/v1/items/{resolved_id}")
    except TraceRTMHttpError as exc:
        if exc.status != HTTP_NOT_FOUND:
            raise ToolError(str(exc)) from exc
        try:
            items = client.get(
                "/api/v1/items",
                params={"project_id": project_id, "limit": 500},
            )
        except TraceRTMHttpError as inner_exc:
            raise ToolError(str(inner_exc)) from inner_exc
        resolved_id = None  # type: ignore[assignment]
        for entry in items.get("items", []):
            candidate_id = str(entry.get("id", ""))
            external_id = str(entry.get("external_id", ""))
            if candidate_id.startswith(item_id) or external_id.startswith(item_id):
                resolved_id = candidate_id
                break
        if not resolved_id:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg) from None
        try:
            result = client.delete(f"/api/v1/items/{resolved_id}")
        except TraceRTMHttpError as inner_exc:
            raise ToolError(str(inner_exc)) from inner_exc

    return {
        "id": result.get("id", resolved_id) if isinstance(result, dict) else resolved_id,
        "status": result.get("status") if isinstance(result, dict) else "deleted",
    }


@mcp.tool()
def bulk_update_items(
    view: str | None = None,
    status: str | None = None,
    new_status: str | None = None,
) -> dict[str, object]:
    """Bulk update item status in the current project.

    Mirrors `rtm item bulk-update` but *without* interactive confirmation.
    """
    if not new_status:
        msg = "new_status is required for bulk_update_items"
        raise ToolError(msg)

    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.post(
            "/api/v1/items/bulk-update",
            json={
                "project_id": project_id,
                "view": view.upper() if view else None,
                "status": status,
                "new_status": new_status,
                "preview": False,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


# ==========================================================================
# ==========================================================================


@mcp.tool()
def find_gaps(from_view: str, to_view: str) -> dict[str, object]:
    """Find items in `from_view` that have no links to items in `to_view`.

    Uses the async TraceabilityService under the hood.
    """
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            "/api/v1/analysis/gaps",
            params={
                "project_id": project_id,
                "from_view": from_view.upper(),
                "to_view": to_view.upper(),
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


@mcp.tool()
def get_trace_matrix(
    source_view: str | None = None,
    target_view: str | None = None,
) -> dict[str, object]:
    """Get a dense traceability matrix for the current project.

    Wraps TraceabilityMatrixService.generate_matrix.
    """
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            "/api/v1/analysis/trace-matrix",
            params={
                "project_id": project_id,
                "source_view": source_view.upper() if source_view else None,
                "target_view": target_view.upper() if target_view else None,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


@mcp.tool()
def analyze_impact(
    item_id: str,
    max_depth: int = 5,
    link_types: list[str] | None = None,
) -> dict[str, object]:
    """Analyze downstream impact of changing an item (BFS)."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            f"/api/v1/analysis/impact/{item_id}",
            params={"project_id": project_id, "max_depth": max_depth},
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    if link_types:
        result["link_types"] = link_types
    return result


@mcp.tool()
def analyze_reverse_impact(
    item_id: str,
    max_depth: int = 5,
) -> dict[str, object]:
    """Analyze reverse impact (what depends on this item)."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            f"/api/v1/analysis/reverse-impact/{item_id}",
            params={"project_id": project_id, "max_depth": max_depth},
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


@mcp.tool()
def project_health() -> dict[str, object]:
    """High-level health metrics for the current project.

    Wraps PerformanceService.get_project_statistics.
    """
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(f"/api/v1/analysis/health/{project_id}")
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


@mcp.tool()
def detect_cycles() -> dict[str, object]:
    """Detect dependency cycles in the current project graph.

    Wraps CycleDetectionService.detect_cycles.
    """
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(f"/api/v1/analysis/cycles/{project_id}")
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


@mcp.tool()
def shortest_path(
    source_id: str,
    target_id: str,
) -> dict[str, object]:
    """Find the shortest dependency path between two items."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            "/api/v1/analysis/shortest-path",
            params={
                "project_id": project_id,
                "source_id": source_id,
                "target_id": target_id,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


@mcp.tool()
def create_link(
    source_id: str,
    target_id: str,
    link_type: str,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Create a link between two items in the current project (with metadata)."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first or use the CLI to initialize."
        raise ToolError(msg)

    client = _api_client()
    try:
        link = client.post(
            "/api/v1/links",
            json={
                "project_id": project_id,
                "source_id": source_id,
                "target_id": target_id,
                "type": link_type,
                "metadata": metadata or {},
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": link.get("id"),
        "project_id": project_id,
        "source_id": link.get("source_id"),
        "target_id": link.get("target_id"),
        "link_type": link.get("type"),
        "metadata": link.get("metadata"),
    }


@mcp.tool()
async def list_links(
    item_id: str | None = None,
    link_type: str | None = None,
    limit: int = 50,
) -> dict[str, object]:
    """List links in the current project (optionally filtered by item and type)."""
    await asyncio.sleep(0)
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    resolved_id = None
    if item_id:
        try:
            items = client.get(
                "/api/v1/items",
                params={"project_id": project_id, "limit": 500},
            )
        except TraceRTMHttpError as exc:
            raise ToolError(str(exc)) from exc
        for entry in items.get("items", []):
            candidate_id = str(entry.get("id", ""))
            external_id = str(entry.get("external_id", ""))
            if candidate_id.startswith(item_id) or external_id.startswith(item_id):
                resolved_id = candidate_id
                break
        if not resolved_id:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg) from None

    links: list[dict[str, object]] = []
    try:
        if resolved_id:
            for params in (
                {"source_id": resolved_id, "limit": max(1, min(limit, 500))},
                {"target_id": resolved_id, "limit": max(1, min(limit, 500))},
            ):
                result = client.get("/api/v1/links", params=params)
                links.extend(result.get("links", []))
        else:
            result = client.get(
                "/api/v1/links",
                params={
                    "project_id": project_id,
                    "limit": max(1, min(limit, 500)),
                },
            )
            links = result.get("links", [])
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    if link_type:
        links = [link for link in links if link.get("type") == link_type or link.get("link_type") == link_type]

    return {
        "project_id": str(project_id),
        "count": len(links),
        "links": [
            {
                "id": str(link.get("id")),
                "source_id": str(link.get("source_id")),
                "target_id": str(link.get("target_id")),
                "link_type": link.get("type") or link.get("link_type"),
                "metadata": link.get("metadata", {}),
            }
            for link in links
        ],
    }


@mcp.tool()
def show_links(
    item_id: str,
    view: str | None = None,
) -> dict[str, object]:
    """Show all links for a specific item (grouped as incoming/outgoing)."""
    config = _get_config_manager()
    project_id = config.get("current_project_id")
    if not project_id:
        msg = "No current project. Call select_project first."
        raise ToolError(msg)

    client = _api_client()
    try:
        result = client.get(
            "/api/v1/links/grouped",
            params={
                "project_id": project_id,
                "item_id": item_id,
                "view": view.upper() if view else None,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return result


# ==========================================================================
# Main entrypoint
# ==========================================================================
