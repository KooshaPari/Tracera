"""OAuth integration API endpoints for TraceRTM.

Implements:
- OAuth flow initiation (GitHub, Linear)
- OAuth callback handling
- Integration credential management (CRUD)
- Credential validation
"""

from __future__ import annotations

import logging
import os
import secrets
import urllib.parse
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.clients.github_client import GitHubClient
from tracertm.clients.linear_client import LinearClient
from tracertm.repositories.integration_repository import IntegrationCredentialRepository
from tracertm.schemas.integration import IntegrationProvider
from tracertm.services.encryption_service import EncryptionService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.integration import IntegrationCredential

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integrations", tags=["oauth", "integrations"])


# ==================== HELPER FUNCTIONS ====================


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project.

    Note: This function should be imported from main.py or moved to a shared module.
    For now, we import it from the parent scope.
    """
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_credential_access(credential: IntegrationCredential | None, claims: dict[str, object] | None) -> None:
    """Check access to a credential (project or user scoped)."""
    if credential is None:
        raise HTTPException(status_code=404, detail="Credential not found")
    if credential.project_id:
        ensure_project_access(credential.project_id, claims)
        return
    user_id = claims.get("sub") if claims else None
    if not user_id or credential.created_by_user_id != user_id:
        raise HTTPException(status_code=403, detail="Credential access denied")


# ==================== REQUEST/RESPONSE MODELS ====================


class OAuthStartRequest(BaseModel):
    """Request to start OAuth flow."""

    project_id: str | None = Field(None, description="Project ID for project-scoped credentials")
    provider: str = Field(..., description="OAuth provider (github, linear)")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: list[str] | None = Field(None, description="OAuth scopes")
    credential_scope: str = Field("project", description="Credential scope (project or user)")


class OAuthCallbackRequest(BaseModel):
    """Request for OAuth callback."""

    code: str = Field(..., description="OAuth authorization code")
    state: str = Field(..., description="OAuth state parameter")
    redirect_uri: str = Field(..., description="OAuth redirect URI")


# ==================== OAUTH FLOW ENDPOINTS ====================


@router.post("/oauth/start")
async def start_oauth_flow(
    request: Request,
    data: dict[str, object],
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Start OAuth flow for an external integration provider.

    Generates authorization URL and state token for CSRF protection.

    Args:
        request: FastAPI request
        data: Request data with provider, redirect_uri, scopes
        claims: Auth claims from auth_guard
        db: Database session

    Returns:
        OAuth authorization URL and state token
    """
    enforce_rate_limit(request, claims)

    project_id = data.get("project_id")
    provider = data.get("provider")
    redirect_uri = data.get("redirect_uri")
    scopes = data.get("scopes", [])
    credential_scope = data.get("credential_scope", "project")

    if project_id:
        ensure_project_access(cast("str", project_id), claims)

    # Validate provider
    valid_providers = [p.value for p in IntegrationProvider]
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session or temporary storage (in production, use Redis/DB)
    # For now, encode project_id and provider in state
    state_data = f"{credential_scope}:{project_id or ''}:{provider}:{state}"

    # Build OAuth URL based on provider
    if provider == "github":
        client_id = os.environ.get("GITHUB_CLIENT_ID", "")
        oauth_url = "https://github.com/login/oauth/authorize"
        default_scopes = ["repo", "read:org", "read:user", "project"]
        scope_str = " ".join(cast("list[str]", scopes) or default_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "state": state_data,
        }
    elif provider == "linear":
        client_id = os.environ.get("LINEAR_CLIENT_ID", "")
        oauth_url = "https://linear.app/oauth/authorize"
        default_scopes = ["read", "write", "issues:create", "comments:create"]
        scope_str = ",".join(cast("list[str]", scopes) or default_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "state": state_data,
            "response_type": "code",
        }
    else:
        raise HTTPException(status_code=400, detail=f"OAuth not supported for {provider}")

    auth_url = f"{oauth_url}?{urllib.parse.urlencode(params)}"

    return {
        "auth_url": auth_url,
        "state": state_data,
        "provider": provider,
    }


@router.post("/oauth/callback")
async def oauth_callback(
    request: Request,
    data: dict[str, object],
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Handle OAuth callback and store credentials.

    Exchanges authorization code for access token and stores encrypted credentials.

    Args:
        request: FastAPI request
        data: Request data with code, state, redirect_uri
        claims: Auth claims from auth_guard
        db: Database session

    Returns:
        Success response with credential info
    """
    from tracertm.api.handlers.oauth import oauth_callback as oauth_callback_handler

    return await oauth_callback_handler(
        request=request,
        data=data,
        claims=claims,
        db=db,
        ensure_project_access_fn=ensure_project_access,
    )


# ==================== CREDENTIAL MANAGEMENT ENDPOINTS ====================


@router.get("/credentials")
async def list_credentials(
    request: Request,
    project_id: str | None = None,
    include_global: bool = True,
    claims: dict[str, object] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """List integration credentials for a project or user.

    Args:
        request: FastAPI request
        project_id: Optional project ID to filter by
        include_global: Include user-scoped credentials
        claims: Auth claims from auth_guard
        db: Database session

    Returns:
        List of credentials with metadata
    """
    enforce_rate_limit(request, claims)
    if project_id:
        ensure_project_access(project_id, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    repo = IntegrationCredentialRepository(db, encryption_service)

    if project_id:
        sub = claims.get("sub") if include_global else None
        credentials = await repo.get_by_project(
            project_id,
            include_global_user_id=sub if isinstance(sub, str) else None,
        )
    else:
        sub = claims.get("sub")
        if not isinstance(sub, str):
            credentials = []
        else:
            credentials = await repo.list_by_user(sub)

    return {
        "credentials": [
            {
                "id": c.id,
                "provider": c.provider,
                "credential_type": c.credential_type,
                "status": c.status,
                "scopes": c.scopes,
                "provider_user_id": c.provider_user_id,
                "provider_metadata": c.provider_metadata,
                "last_validated_at": c.last_validated_at.isoformat() if c.last_validated_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in credentials
        ],
        "total": len(credentials),
    }


@router.post("/credentials/{credential_id}/validate")
async def validate_credential(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Validate an integration credential by testing API access.

    Args:
        request: FastAPI request
        credential_id: Credential ID to validate
        claims: Auth claims from auth_guard
        db: Database session

    Returns:
        Validation result with user info if valid
    """
    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    # Decrypt token and validate
    token = repo.decrypt_token(credential)
    valid = False
    user_info = {}
    error = None

    client: GitHubClient | LinearClient | None = None
    try:
        if credential.provider == "github":
            client = GitHubClient(token)
            try:
                user_info = await client.get_authenticated_user()
                valid = True
            finally:
                await client.close()
        elif credential.provider == "linear":
            client = LinearClient(token)
            try:
                user_info = await client.get_viewer()
                valid = True
            finally:
                await client.close()
    except Exception as e:
        error = str(e)

    # Update validation status
    await repo.update_validation_status(
        credential_id,
        valid=valid,
        error=error,
    )

    return {
        "valid": valid,
        "credential_id": credential_id,
        "provider": credential.provider,
        "user": user_info if valid else None,
        "error": error,
        "validated_at": datetime.now(UTC).isoformat(),
    }


@router.delete("/credentials/{credential_id}")
async def delete_credential(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Delete an integration credential.

    Args:
        request: FastAPI request
        credential_id: Credential ID to delete
        claims: Auth claims from auth_guard
        db: Database session

    Returns:
        Success response
    """
    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    await repo.delete(credential_id)

    return {"success": True, "deleted_id": credential_id}


@router.get("/stats")
async def get_integration_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Get integration statistics for a project."""
    from tracertm.api.handlers.integrations import get_integration_stats_handler

    return await get_integration_stats_handler(request, project_id, claims, db)
