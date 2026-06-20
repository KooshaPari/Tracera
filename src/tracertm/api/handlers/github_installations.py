"""GitHub App installation endpoint handlers."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING, Any, cast

from fastapi import Depends, HTTPException

from tracertm.api.deps import auth_guard, get_db
from tracertm.api.handlers.github_shared import (
    _format_installation_response,
    _verify_account_access,
)
from tracertm.config.github_app import get_github_app_config
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_github_app_install_url(
    account_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get GitHub App installation URL for an account."""
    user_id = cast("str | None", claims.get("sub")) if isinstance(claims, dict) else None
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


async def list_github_app_installations(
    account_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List GitHub App installations for an account."""
    user_id = cast("str | None", claims.get("sub")) if isinstance(claims, dict) else None
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
) -> dict[str, Any]:
    """Link a GitHub App installation to an account."""
    user_id = claims.get("sub") if isinstance(claims, dict) else None
    account_id = data.get("account_id")

    if not user_id or not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")

    await _verify_account_access(cast("str", account_id), cast("str", user_id), db)

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
) -> dict[str, Any]:
    """Delete a GitHub App installation."""
    user_id = cast("str | None", claims.get("sub")) if isinstance(claims, dict) else None
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
