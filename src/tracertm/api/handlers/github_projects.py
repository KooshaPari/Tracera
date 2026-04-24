"""GitHub project endpoint handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, Request

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.handlers.github_shared import (
    ProjectListParams,
    _format_project_response,
    _get_credential_client,
    _get_installation_client,
    _require_int,
    _require_str,
)
from tracertm.clients.github_client import GitHubClient

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.github_project_repository import GitHubProjectRepository
from tracertm.services.github_project_service import GitHubProjectService


async def list_github_projects(
    request: Request,
    params: ProjectListParams = Depends(),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List GitHub Projects v2 for an owner."""
    enforce_rate_limit(request, claims)

    client: GitHubClient | None = None
    try:
        if params.installation_id:
            client, _ = await _get_installation_client(params.installation_id, None, db)
        elif params.credential_id:
            client = await _get_credential_client(params.credential_id, claims, db)
        else:
            raise HTTPException(status_code=400, detail="Either installation_id or credential_id is required")

        projects = await client.list_projects_graphql(owner=params.owner, is_org=params.is_org)
    finally:
        if client:
            await client.close()

    return {"projects": [_format_project_response(p) for p in projects]}


async def auto_link_github_projects(
    request: Request,
    data: dict[str, Any],
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Auto-link GitHub Projects for a repository."""
    from tracertm.api.middleware.auth import ensure_project_access

    enforce_rate_limit(request, claims)

    project_id = _require_str(data, "project_id")
    github_repo_owner = _require_str(data, "github_repo_owner")
    github_repo_name = _require_str(data, "github_repo_name")
    installation_id = _require_str(data, "installation_id")
    github_repo_id = _require_int(data, "github_repo_id")

    ensure_project_access(project_id, claims)

    client, _ = await _get_installation_client(installation_id, None, db)

    try:
        service = GitHubProjectService(db)
        linked_projects = await service.auto_link_projects_for_repo(
            project_id=project_id,
            github_repo_owner=github_repo_owner,
            github_repo_name=github_repo_name,
            github_repo_id=github_repo_id,
            client=client,
        )
    finally:
        await client.close()

    return {"linked_projects": linked_projects, "total": len(linked_projects)}


async def list_linked_github_projects(
    request: Request,
    project_id: str | None = None,
    github_repo_id: int | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List linked GitHub Projects."""
    from tracertm.api.middleware.auth import ensure_project_access

    enforce_rate_limit(request, claims)

    repo = GitHubProjectRepository(db)

    if project_id:
        ensure_project_access(project_id, claims)
        projects = await repo.get_by_project_id(project_id)
    elif github_repo_id:
        projects = await repo.get_by_repo(github_repo_id)
    else:
        raise HTTPException(status_code=400, detail="Either project_id or github_repo_id is required")

    return {
        "projects": [
            {
                "id": p.id,
                "project_id": p.project_id,
                "github_repo_id": p.github_repo_id,
                "github_repo_owner": p.github_repo_owner,
                "github_repo_name": p.github_repo_name,
                "github_project_id": p.github_project_id,
                "github_project_number": p.github_project_number,
                "auto_sync": p.auto_sync,
                "sync_config": p.sync_config,
            }
            for p in projects
        ],
        "total": len(projects),
    }


async def unlink_github_project(
    request: Request,
    github_project_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Unlink a GitHub Project from an integrated project."""
    from tracertm.api.middleware.auth import ensure_project_access

    enforce_rate_limit(request, claims)

    repo = GitHubProjectRepository(db)
    github_project = await repo.get_by_id(github_project_id)

    if not github_project:
        raise HTTPException(status_code=404, detail="GitHub Project link not found")

    ensure_project_access(github_project.project_id, claims)

    await repo.delete(github_project_id)
    await db.commit()

    return {"status": "unlinked"}
