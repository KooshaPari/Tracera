"""GitHub integration handlers and helpers for reducing complexity."""

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.clients.github_client import GitHubClient
from tracertm.clients.github_client import IssueListParams as GitHubIssueListParams
from tracertm.config.github_app import get_github_app_config
from tracertm.repositories.account_repository import AccountRepository
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
from tracertm.repositories.github_project_repository import GitHubProjectRepository
from tracertm.repositories.integration_repository import (
    IntegrationCredentialRepository,
    IntegrationSyncQueueRepository,
)
from tracertm.repositories.webhook_repository import WebhookRepository
from tracertm.services.encryption_service import EncryptionService
from tracertm.services.github_project_service import GitHubProjectService

if TYPE_CHECKING:
    from tracertm.models.github_app_installation import GitHubAppInstallation

if TYPE_CHECKING:
    from tracertm.models.github_app_installation import GitHubAppInstallation

# ==================== HELPER FUNCTIONS ====================


@dataclass(frozen=True)
class RepoListParams:
    account_id: str | None = None
    installation_id: str | None = None
    credential_id: str | None = None
    search: str | None = None
    per_page: int = 30
    page: int = 1


@dataclass(frozen=True)
class IssueListParams:
    owner: str
    repo: str
    credential_id: str
    state: str = "open"
    per_page: int = 30
    page: int = 1


@dataclass(frozen=True)
class ProjectListParams:
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
        "suspended_at": (installation.suspended_at.isoformat() if installation.suspended_at else None),
        "created_at": installation.created_at.isoformat(),
    }


# ==================== REPOSITORY HANDLERS ====================


async def list_github_repos(
    request: Request,
    params: RepoListParams = Depends(),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List GitHub repositories accessible via GitHub App installation or OAuth credential."""
    enforce_rate_limit(request, claims)

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if params.account_id and user_id:
        await _verify_account_access(params.account_id, user_id, db)

    client: GitHubClient | None = None
    repos: list[dict] = []

    try:
        if params.installation_id:
            client, installation = await _get_installation_client(params.installation_id, params.account_id, db)
            repos = await _fetch_repos_from_installation(
                client, installation, params.search, params.per_page, params.page,
            )
        elif params.credential_id:
            client = await _get_credential_client(params.credential_id, claims, db)
            repos = await _fetch_repos_from_credential(client, params.search, params.per_page, params.page)
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
        await _verify_account_access(account_id, user_id, db)

    client, installation = await _get_installation_client(installation_id, account_id, db)

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


# ==================== GITHUB APP INSTALLATION HANDLERS ====================


async def get_github_app_install_url(
    account_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get GitHub App installation URL for an account."""
    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    await _verify_account_access(account_id, user_id, db)

    config = get_github_app_config()
    if not config.is_configured():
        raise HTTPException(status_code=500, detail="GitHub App is not configured")

    state = secrets.token_urlsafe(32)
    state_data = f"{account_id}:{state}"
    install_url = config.get_installation_url(state=state_data)

    return {
        "install_url": install_url,
        "state": state_data,
    }


async def _handle_installation_created(
    payload: dict,
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
) -> dict:
    """Handle installation created webhook event."""
    installation_data = payload.get("installation", {})
    installation_id = installation_data.get("id")
    account_login = installation_data.get("account", {}).get("login", "")
    target_type = installation_data.get("target_type", "Organization")
    target_id = installation_data.get("account", {}).get("id")

    installation = await installation_repo.create(
        account_id="",  # Will be set via separate endpoint
        installation_id=installation_id,
        account_login=account_login,
        target_type=target_type,
        target_id=target_id,
        permissions=installation_data.get("permissions", {}),
        repository_selection=installation_data.get("repository_selection", "all"),
    )

    await db.commit()
    return {"status": "created", "installation_id": installation.id}


async def _handle_installation_deleted(
    payload: dict,
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
) -> dict:
    """Handle installation deleted webhook event."""
    installation_data = payload.get("installation", {})
    installation_id = installation_data.get("id")

    existing = await installation_repo.get_by_github_installation_id(installation_id)
    if existing:
        await installation_repo.delete(existing.id)
        await db.commit()

    return {"status": "deleted"}


async def _handle_installation_suspended(
    payload: dict,
    action: str,
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
) -> dict:
    """Handle installation suspend/unsuspend webhook event."""
    installation_data = payload.get("installation", {})
    installation_id = installation_data.get("id")

    existing = await installation_repo.get_by_github_installation_id(installation_id)
    if existing:
        await installation_repo.update(
            existing.id,
            suspended_at=(action == "suspend"),
        )
        await db.commit()

    return {"status": action}


async def github_app_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Handle GitHub App webhook events."""
    config = get_github_app_config()

    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()

    if not config.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    installation_repo = GitHubAppInstallationRepository(db)

    if event_type == "installation":
        action = payload.get("action")

        if action == "created":
            return await _handle_installation_created(payload, installation_repo, db)

        if action == "deleted":
            return await _handle_installation_deleted(payload, installation_repo, db)

        if action in {"suspend", "unsuspend"}:
            return await _handle_installation_suspended(payload, action, installation_repo, db)

    return {"status": "ok"}


async def list_github_app_installations(
    account_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List GitHub App installations for an account."""
    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    await _verify_account_access(account_id, user_id, db)

    installation_repo = GitHubAppInstallationRepository(db)
    installations = await installation_repo.list_by_account(account_id)

    return {
        "installations": [_format_installation_response(inst) for inst in installations],
        "total": len(installations),
    }


async def link_github_app_installation(
    installation_id: str,
    data: dict[str, Any],
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Link a GitHub App installation to an account."""
    user_id = claims.get("sub") if isinstance(claims, dict) else None
    account_id = data.get("account_id")

    if not user_id or not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")

    await _verify_account_access(account_id, user_id, db)

    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(installation_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    if installation.account_id and installation.account_id != account_id:
        raise HTTPException(status_code=400, detail="Installation already linked to another account")

    installation.account_id = account_id
    await db.commit()

    return {
        "status": "linked",
        "installation_id": installation.id,
        "account_id": account_id,
    }


async def delete_github_app_installation(
    installation_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Delete a GitHub App installation."""
    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(installation_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    if installation.account_id:
        await _verify_account_access(installation.account_id, user_id, db)

    await installation_repo.delete(installation_id)
    await db.commit()

    return {"status": "deleted"}


# ==================== GITHUB PROJECTS HANDLERS ====================


async def list_github_projects(
    request: Request,
    params: ProjectListParams = Depends(),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List GitHub Projects v2 for an owner."""
    enforce_rate_limit(request, claims)

    client: GitHubClient | None = None

    try:
        if params.installation_id:
            client, _ = await _get_installation_client(params.installation_id, None, db)
        elif params.credential_id:
            client = await _get_credential_client(params.credential_id, claims, db)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either installation_id or credential_id is required",
            )

        projects = await client.list_projects_graphql(owner=params.owner, is_org=params.is_org)
    finally:
        if client:
            await client.close()

    return {
        "projects": [_format_project_response(p) for p in projects],
    }


async def auto_link_github_projects(
    request: Request,
    data: dict[str, Any],
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
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

    return {
        "linked_projects": linked_projects,
        "total": len(linked_projects),
    }


async def list_linked_github_projects(
    request: Request,
    project_id: str | None = None,
    github_repo_id: int | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
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
):
    """Unlink a GitHub Project from a TraceRTM project."""
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


# ==================== WEBHOOK HANDLERS ====================


async def receive_github_webhook(
    request: Request,
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Receive GitHub webhook events."""
    from tracertm.models.webhook_integration import WebhookStatus

    webhook_repo = WebhookRepository(db)
    webhook = await webhook_repo.get_by_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if webhook.status != WebhookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Webhook is inactive")

    body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256", "")

    if webhook.webhook_secret:
        expected_signature = "sha256=" + hmac.new(webhook.webhook_secret.encode(), body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature_header, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    payload = await request.json()

    metadata = webhook.webhook_metadata or {}
    raw_credential_id = metadata.get("credential_id")
    if not isinstance(raw_credential_id, str) or not raw_credential_id:
        raise HTTPException(status_code=400, detail="Webhook missing credential_id")
    raw_mapping_id = metadata.get("mapping_id")
    mapping_id = raw_mapping_id if isinstance(raw_mapping_id, str) and raw_mapping_id else webhook_id

    queue_repo = IntegrationSyncQueueRepository(db)
    await queue_repo.enqueue(
        credential_id=raw_credential_id,
        mapping_id=mapping_id,
        event_type=f"webhook:{event_type}",
        direction="pull",
        payload={
            "webhook_id": webhook_id,
            "event_type": event_type,
            "delivery_id": request.headers.get("X-GitHub-Delivery"),
            "data": payload,
        },
    )

    await webhook_repo.create_log(
        webhook_id=webhook_id,
        event_type=event_type,
        payload_size_bytes=len(body),
        success=True,
        status_code=200,
    )

    return {"received": True, "event": event_type}
