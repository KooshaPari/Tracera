"""Linear integration router."""

from __future__ import annotations

import os
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.routers.oauth import ensure_credential_access
from tracertm.clients.linear_client import LinearClient
from tracertm.repositories.integration_repository import IntegrationCredentialRepository
from tracertm.services.encryption_service import EncryptionService

router = APIRouter(prefix="/api/v1/integrations/linear", tags=["linear"])


async def _get_linear_client(db: AsyncSession, credential_id: str, claims: dict[str, object]) -> LinearClient:
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    if credential.provider != "linear":
        raise HTTPException(status_code=400, detail="Credential is not for Linear")

    token = cred_repo.decrypt_token(credential)
    return LinearClient(token)


@router.get("/teams")
async def list_linear_teams(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """List Linear teams accessible with the credential."""
    enforce_rate_limit(request, claims)
    client = await _get_linear_client(db, credential_id, claims)

    try:
        teams = await client.list_teams()
    finally:
        await client.close()

    return {
        "teams": [
            {
                "id": team["id"],
                "name": team["name"],
                "key": team["key"],
                "description": team.get("description"),
                "icon": team.get("icon"),
                "color": team.get("color"),
            }
            for team in teams
        ],
    }


@router.get("/teams/{team_id}/issues")
async def list_linear_issues(
    request: Request,
    team_id: str,
    credential_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    first: int = 50,
) -> dict[str, Any]:
    """List Linear issues for a team."""
    enforce_rate_limit(request, claims)
    client = await _get_linear_client(db, credential_id, claims)

    try:
        issues_result = await client.list_issues(team_id=team_id, first=first)
        issues = cast("list[dict[str, Any]]", issues_result.get("nodes", []))
    finally:
        await client.close()

    return {
        "issues": [
            {
                "id": issue["id"],
                "identifier": issue["identifier"],
                "title": issue["title"],
                "description": issue.get("description", "")[:500] if issue.get("description") else None,
                "state": issue.get("state", {}).get("name"),
                "priority": issue.get("priority"),
                "url": issue["url"],
                "assignee": issue.get("assignee", {}).get("name") if issue.get("assignee") else None,
                "labels": [label["name"] for label in issue.get("labels", {}).get("nodes", [])],
                "created_at": issue.get("createdAt"),
                "updated_at": issue.get("updatedAt"),
            }
            for issue in issues
        ],
    }


@router.get("/projects")
async def list_linear_projects(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _first: int = 50,
) -> dict[str, Any]:
    """List Linear projects."""
    enforce_rate_limit(request, claims)
    client = await _get_linear_client(db, credential_id, claims)

    try:
        projects = await client.list_projects()
    finally:
        await client.close()

    return {
        "projects": [
            {
                "id": project["id"],
                "name": project["name"],
                "description": project.get("description"),
                "state": project.get("state"),
                "progress": project.get("progress"),
                "url": project["url"],
                "start_date": project.get("startDate"),
                "target_date": project.get("targetDate"),
            }
            for project in projects
        ],
    }
