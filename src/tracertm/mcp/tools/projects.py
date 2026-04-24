"""Project management MCP tools.

Provides tools for creating, listing, selecting, and snapshotting projects.


Functional Requirements: FR-MCP-002, FR-APP-006
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml
from fastmcp.exceptions import ToolError
from sqlalchemy import select

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base_async import (
    get_config_manager,
    get_mcp_session,
    set_current_project,
    wrap_success,
)
from tracertm.models.project import Project


@mcp.tool(description="Create a new project")
async def create_project(
    name: str,
    description: str | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Create a new project and set it as current.

    Args:
        name: Project name (required)
        description: Optional project description

    Returns:
        Created project details with id, name, description
    """
    if not name:
        msg = "Project name is required."
        raise ToolError(msg)

    async with get_mcp_session() as session:
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=description or "",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(project)
        await session.commit()

        # Set as current project
        await set_current_project(str(project.id))

        return wrap_success(
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
            },
            "create",
            ctx,
        )


@mcp.tool(description="List all projects")
async def list_projects(
    ctx: object | None = None,
) -> dict[str, object]:
    """List all available projects.

    Returns:
        List of projects with id, name, description, created_at
    """
    async with get_mcp_session() as session:
        result_set = await session.execute(select(Project))
        projects = result_set.scalars().all()
        result = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
        return wrap_success(result, "list", ctx)


@mcp.tool(description="Select a project as current")
async def select_project(
    project_id: str,
    ctx: object | None = None,
) -> dict[str, object]:
    """Set a project as the current working project.

    Args:
        project_id: Project ID or prefix to match

    Returns:
        Selected project details
    """
    if not project_id:
        msg = "project_id is required."
        raise ToolError(msg)

    async with get_mcp_session() as session:
        # Try exact match first
        result = await session.execute(select(Project).filter(Project.id == project_id))
        project = result.scalar_one_or_none()

        # Try prefix match if no exact match
        if not project:
            result = await session.execute(select(Project).filter(Project.id.like(f"{project_id}%")))
            project = result.scalar_one_or_none()

        if not project:
            msg = f"Project not found: {project_id}"
            raise ToolError(msg)

        await set_current_project(str(project.id))

        return wrap_success(
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "message": f"Switched to project '{project.name}'",
            },
            "select",
            ctx,
        )


@mcp.tool(description="Create a project snapshot")
async def snapshot_project(
    project_id: str,
    label: str,
    ctx: object | None = None,
) -> dict[str, object]:
    """Create a lightweight snapshot record for a project.

    Snapshots are stored in ~/.tracertm/projects/<project_id>/snapshots.yaml.

    Args:
        project_id: Project ID to snapshot
        label: Human-readable label for the snapshot

    Returns:
        Snapshot details including timestamp and label
    """
    if not project_id or not label:
        msg = "project_id and label are required."
        raise ToolError(msg)

    async with get_mcp_session() as session:
        result = await session.execute(select(Project).filter(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            msg = f"Project not found: {project_id}"
            raise ToolError(msg)

        # Create snapshot record
        config = get_config_manager()
        snapshots_dir = Path(config.config_dir) / "projects" / project_id
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        snapshots_file = snapshots_dir / "snapshots.yaml"

        # Load existing snapshots
        if snapshots_file.exists():
            with snapshots_file.open() as f:
                snapshots = yaml.safe_load(f) or []
        else:
            snapshots = []

        # Add new snapshot
        snapshot = {
            "id": str(uuid.uuid4()),
            "label": label,
            "timestamp": datetime.now(UTC).isoformat(),
            "project_id": project_id,
            "project_name": project.name,
        }
        snapshots.append(snapshot)

        # Save snapshots
        with snapshots_file.open("w") as f:
            yaml.safe_dump(snapshots, f, default_flow_style=False)

        return wrap_success(snapshot, "snapshot", ctx)


__all__ = [
    "create_project",
    "list_projects",
    "select_project",
    "snapshot_project",
]
