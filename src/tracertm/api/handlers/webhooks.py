"""GitHub App webhook handlers.

Functional Requirements: FR-COLLAB-004
"""

from typing import cast

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.config.github_app import get_github_app_config
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository


async def verify_webhook_signature(request: Request) -> tuple[bytes, str, dict[str, object]]:
    """Verify GitHub webhook signature and extract event data.

    Args:
        request: FastAPI request object

    Returns:
        Tuple of (body, event_type, payload)

    Raises:
        HTTPException: If signature verification fails
    """
    config = get_github_app_config()

    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()

    if not config.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    return body, event_type, payload


async def handle_installation_created(
    payload: dict[str, object],
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
) -> dict[str, object]:
    """Handle GitHub App installation created event.

    Args:
        payload: GitHub webhook payload
        installation_repo: Installation repository
        db: Database session

    Returns:
        Response dict with status and installation_id
    """
    installation_data = cast("dict[str, object]", payload.get("installation", {}))
    installation_id = cast("int", installation_data.get("id"))

    # Extract installation details
    account_data = cast("dict[str, object]", installation_data.get("account", {}))
    account_login = cast("str", account_data.get("login", ""))
    target_type = cast("str", installation_data.get("target_type", "Organization"))
    target_id = cast("int", account_data.get("id"))

    # Create installation record
    # Note: account_id is empty and will be linked via separate endpoint
    installation = await installation_repo.create(
        account_id="",  # Will be set via link endpoint
        installation_id=installation_id,
        account_login=account_login,
        target_type=target_type,
        target_id=target_id,
        permissions=cast("dict[str, object]", installation_data.get("permissions", {})),
        repository_selection=cast("str", installation_data.get("repository_selection", "all")),
    )

    await db.commit()

    return {"status": "created", "installation_id": installation.id}


async def handle_installation_deleted(
    payload: dict[str, object],
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
) -> dict[str, object]:
    """Handle GitHub App installation deleted event.

    Args:
        payload: GitHub webhook payload
        installation_repo: Installation repository
        db: Database session

    Returns:
        Response dict with status
    """
    installation_data = cast("dict[str, object]", payload.get("installation", {}))
    installation_id = cast("int", installation_data.get("id"))

    existing = await installation_repo.get_by_github_installation_id(installation_id)
    if existing:
        await installation_repo.delete(existing.id)
        await db.commit()

    return {"status": "deleted"}


async def handle_installation_suspended(
    payload: dict[str, object],
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
    suspended: bool,
) -> dict[str, object]:
    """Handle GitHub App installation suspend/unsuspend event.

    Args:
        payload: GitHub webhook payload
        installation_repo: Installation repository
        db: Database session
        suspended: True for suspend, False for unsuspend

    Returns:
        Response dict with status
    """
    installation_data = cast("dict[str, object]", payload.get("installation", {}))
    installation_id = cast("int", installation_data.get("id"))

    existing = await installation_repo.get_by_github_installation_id(installation_id)
    if existing:
        await installation_repo.update(
            existing.id,
            suspended_at=suspended,
        )
        await db.commit()

    status = "suspend" if suspended else "unsuspend"
    return {"status": status}


async def process_installation_event(
    payload: dict[str, object],
    installation_repo: GitHubAppInstallationRepository,
    db: AsyncSession,
) -> dict[str, object]:
    """Process GitHub App installation events.

    Args:
        payload: GitHub webhook payload
        installation_repo: Installation repository
        db: Database session

    Returns:
        Response dict with event status
    """
    action = payload.get("action")

    if action == "created":
        return await handle_installation_created(payload, installation_repo, db)

    if action == "deleted":
        return await handle_installation_deleted(payload, installation_repo, db)

    if action == "suspend":
        return await handle_installation_suspended(payload, installation_repo, db, suspended=True)

    if action == "unsuspend":
        return await handle_installation_suspended(payload, installation_repo, db, suspended=False)

    return {"status": "ok"}


async def github_app_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Handle GitHub App webhook events.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Response dict with event status

    Raises:
        HTTPException: If signature verification fails
    """
    # Verify webhook signature and extract event data
    _body, event_type, payload = await verify_webhook_signature(request)

    installation_repo = GitHubAppInstallationRepository(db)

    # Route to appropriate event handler
    if event_type == "installation":
        return await process_installation_event(payload, installation_repo, db)

    # Default response for unhandled events
    return {"status": "ok"}
