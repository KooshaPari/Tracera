"""Account API endpoints for TraceRTM."""

from __future__ import annotations

import hashlib
import re
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.models.account_user import AccountRole
from tracertm.repositories.account_repository import AccountRepository
from tracertm.schemas.account import AccountCreate, AccountResponse

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


def _get_user_id(claims: dict[str, Any] | None) -> str:
    """Extract the authenticated user ID from JWT claims."""
    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


def _build_account_slug(name: str, slug: str | None) -> str:
    """Build a normalized account slug when one is not provided."""
    if slug:
        return slug
    generated = re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))
    if generated:
        return generated
    return "account-" + hashlib.md5(name.encode(), usedforsecurity=False).hexdigest()[:8]


@router.get("")
async def list_accounts_endpoint(
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all accounts for the current user."""
    user_id = _get_user_id(claims)
    account_repo = AccountRepository(db)
    accounts = await account_repo.list_by_user(user_id)
    return {
        "accounts": [AccountResponse.model_validate(acc) for acc in accounts],
        "total": len(accounts),
    }


@router.post("")
async def create_account_endpoint(
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new account."""
    user_id = _get_user_id(claims)

    try:
        account_data = AccountCreate.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    account_slug = _build_account_slug(account_data.name, account_data.slug)
    account_repo = AccountRepository(db)

    existing = await account_repo.get_by_slug(account_slug)
    if existing:
        raise HTTPException(status_code=400, detail=f"Account slug '{account_slug}' already exists")

    account = await account_repo.create(
        name=account_data.name,
        slug=account_slug,
        account_type=account_data.account_type,
    )
    await account_repo.add_user(account.id, user_id, AccountRole.OWNER)
    await db.commit()
    return AccountResponse.model_validate(account)


@router.post("/{account_id}/switch")
async def switch_account_endpoint(
    account_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Switch active account context."""
    user_id = _get_user_id(claims)
    account_repo = AccountRepository(db)

    role = await account_repo.get_user_role(account_id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied to this account")

    account = await account_repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "account": {
            "id": account.id,
            "name": account.name,
            "slug": account.slug,
            "account_type": account.account_type,
        },
        "message": "Account switched successfully",
    }
