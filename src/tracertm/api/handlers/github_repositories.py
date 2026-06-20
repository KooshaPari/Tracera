"""GitHub repository endpoint handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from fastapi import Depends, HTTPException, Request

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.handlers.github_shared import (
    IssueListParams,
    RepoListParams,
    _fetch_repos_from_credential,
    _fetch_repos_from_installation,
    _format_issue_response,
    _format_repo_response,
    _get_credential_client,
    _get_installation_client,
    _verify_account_access,
)
from tracertm.clients.github_client import GitHubClient
from tracertm.clients.github_client import IssueListParams as GitHubIssueListParams

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def list_github_repos(
    request: Request,
    params: RepoListParams = Depends(),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List GitHub repositories accessible via GitHub App installation or OAuth credential."""
    enforce_rate_limit(request, claims)

    user_id = cast("str | None", claims.get("sub")) if isinstance(claims, dict) else None
    if params.account_id and user_id:
        await _verify_account_access(params.account_id, user_id, db)

    client: GitHubClient | None = None
    repos: list[dict] = []

    try:
        if params.installation_id:
            client, installation = await _get_installation_client(
                params.installation_id, params.account_id, db
            )
            repos = await _fetch_repos_from_installation(
                client,
                installation,
                params.search,
                params.per_page,
                params.page,
            )
        elif params.credential_id:
            client = await _get_credential_client(params.credential_id, claims, db)
            repos = await _fetch_repos_from_credential(
                client, params.search, params.per_page, params.page
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either installation_id or credential_id is required",
            )
    finally:
        if client:
            await client.close()

    return {
        "repos": [_format_repo_response(r) for r in repos],
        "page": params.page,
        "per_page": params.per_page,
    }


async def create_github_repo(
    request: Request,
    data: dict[str, Any],
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new GitHub repository."""
    enforce_rate_limit(request, claims)

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    installation_id = data.get("installation_id")
    account_id = data.get("account_id")
    name = data.get("name")
    description = data.get("description")
    private = data.get("private", False)
    org = data.get("org")

    if not installation_id or not name:
        raise HTTPException(status_code=400, detail="installation_id and name are required")

    if account_id:
        await _verify_account_access(cast("str", account_id), cast("str", user_id), db)

    client, installation = await _get_installation_client(
        cast("str", installation_id), cast("str | None", account_id), db
    )

    try:
        org_name = org or (installation.account_login if installation.target_type == "Organization" else None)
        repo = await client.create_repo(
            name=name,
            description=description,
            private=private,
            org=org_name,
        )
    finally:
        await client.close()

    return _format_repo_response(repo)


async def list_github_issues(
    request: Request,
    params: IssueListParams = Depends(),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List GitHub issues for a repository."""
    enforce_rate_limit(request, claims)

    client = await _get_credential_client(params.credential_id, claims, db)

    try:
        issues = await client.list_issues(
            owner=params.owner,
            repo=params.repo,
            params=GitHubIssueListParams(
                state=params.state,
                per_page=params.per_page,
                page=params.page,
            ),
        )
    finally:
        await client.close()

    filtered_issues = [i for i in issues if "pull_request" not in i]

    return {
        "issues": [_format_issue_response(i) for i in filtered_issues],
        "page": params.page,
        "per_page": params.per_page,
    }
