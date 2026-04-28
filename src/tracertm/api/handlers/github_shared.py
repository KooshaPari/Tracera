"""GitHub integration shared types and helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException

from tracertm.clients.github_client import GitHubClient
from tracertm.config.github_app import get_github_app_config
from tracertm.repositories.account_repository import AccountRepository
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
from tracertm.repositories.integration_repository import (
    IntegrationCredentialRepository,
)
from tracertm.services.encryption_service import EncryptionService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.github_app_installation import GitHubAppInstallation


@dataclass(frozen=True)
class RepoListParams:
    """Parameters for listing repositories."""

    account_id: str | None = None
    installation_id: str | None = None
    credential_id: str | None = None
    search: str | None = None
    per_page: int = 30
    page: int = 1


@dataclass(frozen=True)
class IssueListParams:
    """Parameters for listing issues."""

    owner: str
    repo: str
    credential_id: str
    state: str = "open"
    per_page: int = 30
    page: int = 1


@dataclass(frozen=True)
class ProjectListParams:
    """Parameters for listing GitHub projects."""

    owner: str
    installation_id: str | None = None
    credential_id: str | None = None
    is_org: bool = True


async def _verify_account_access(
    account_id: str,
    user_id: str,
    db: AsyncSession,
) -> None:
    """Verify user has access to account."""
    account_repo = AccountRepository(db)
    role = await account_repo.get_user_role(account_id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied to this account")


async def _get_installation_client(
    installation_id: str,
    account_id: str | None,
    db: AsyncSession,
) -> tuple[GitHubClient, Any]:
    """Get GitHub client from app installation."""
    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(installation_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    if account_id and installation.account_id != account_id:
        raise HTTPException(status_code=403, detail="Installation does not belong to this account")

    config = get_github_app_config()
    if not config.is_configured():
        raise HTTPException(status_code=500, detail="GitHub App is not configured")

    client = await GitHubClient.from_app_installation(
        app_id=config.app_id,
        private_key=config.private_key,
        installation_id=installation.installation_id,
    )

    return client, installation


async def _get_credential_client(
    credential_id: str,
    claims: dict[str, Any],
    db: AsyncSession,
) -> GitHubClient:
    """Get GitHub client from OAuth credential."""
    from tracertm.api.middleware.auth import ensure_credential_access

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    if credential.provider != "github":
        raise HTTPException(status_code=400, detail="Credential is not for GitHub")

    token = cred_repo.decrypt_token(credential)
    return GitHubClient(token)


def _require_str(payload: dict[str, Any], key: str) -> str:
    """Read a required string field from a payload."""
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise HTTPException(status_code=400, detail=f"Invalid {key}")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    """Read a required int field from a payload."""
    value = payload.get(key)
    if isinstance(value, int):
        return value
    if value is None:
        raise HTTPException(status_code=400, detail=f"Missing {key}")
    try:
        return int(str(value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {key}") from exc


async def _fetch_repos_from_installation(
    client: GitHubClient,
    installation: GitHubAppInstallation,
    search: str | None,
    per_page: int,
    page: int,
) -> list[dict]:
    """Fetch repositories from GitHub App installation."""
    if search:
        result = await client.search_repos(
            query=search,
            per_page=per_page,
            page=page,
        )
        return result.get("items", [])

    repos_result = await client.list_installation_repos(
        installation_id=installation.installation_id,
        per_page=per_page,
        page=page,
    )

    if isinstance(repos_result, dict):
        return repos_result.get("repositories", [])
    return repos_result if isinstance(repos_result, list) else []


async def _fetch_repos_from_credential(
    client: GitHubClient,
    search: str | None,
    per_page: int,
    page: int,
) -> list[dict]:
    """Fetch repositories from OAuth credential."""
    if search:
        result = await client.search_repos(
            query=search,
            per_page=per_page,
            page=page,
        )
        return result.get("items", [])

    return await client.list_user_repos(per_page=per_page, page=page)


def _format_repo_response(repo: dict) -> dict:
    """Format a single repository response."""
    return {
        "id": repo["id"],
        "name": repo["name"],
        "full_name": repo["full_name"],
        "description": repo.get("description"),
        "html_url": repo["html_url"],
        "private": repo["private"],
        "owner": {
            "login": repo["owner"]["login"],
            "avatar_url": repo["owner"]["avatar_url"],
        },
        "default_branch": repo.get("default_branch", "main"),
        "updated_at": repo.get("updated_at"),
        "created_at": repo.get("created_at"),
    }


def _format_issue_response(issue: dict) -> dict:
    """Format a single issue response."""
    return {
        "id": issue["id"],
        "number": issue["number"],
        "title": issue["title"],
        "state": issue["state"],
        "html_url": issue["html_url"],
        "body": issue.get("body", "")[:500] if issue.get("body") else None,
        "user": {
            "login": issue["user"]["login"],
            "avatar_url": issue["user"]["avatar_url"],
        },
        "labels": [label["name"] for label in issue.get("labels", [])],
        "assignees": [assignee["login"] for assignee in issue.get("assignees", [])],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
    }


def _format_project_response(project: dict) -> dict:
    """Format a single project response."""
    return {
        "id": project["id"],
        "title": project["title"],
        "description": project.get("shortDescription"),
        "url": project["url"],
        "closed": project.get("closed", False),
        "public": project.get("public", False),
        "created_at": project.get("createdAt"),
        "updated_at": project.get("updatedAt"),
    }


def _format_installation_response(installation: GitHubAppInstallation) -> dict:
    """Format a single installation response."""
    return {
        "id": installation.id,
        "installation_id": installation.installation_id,
        "account_login": installation.account_login,
        "target_type": installation.target_type,
        "permissions": installation.permissions,
        "repository_selection": installation.repository_selection,
        "suspended_at": installation.suspended_at.isoformat() if installation.suspended_at else None,
        "created_at": installation.created_at.isoformat(),
    }
