"""OAuth integration handlers for TraceRTM."""

import os
from dataclasses import dataclass
from typing import Any, cast

import httpx
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.clients.github_client import GitHubClient
from tracertm.clients.linear_client import LinearClient
from tracertm.models.integration import IntegrationCredential
from tracertm.repositories.integration_repository import IntegrationCredentialRepository
from tracertm.services.encryption_service import EncryptionService

HTTP_OK = 200
STATE_PARTS_EXTENDED = 4  # state format: scope:project_id:provider or scope:project_id:provider:...


def _parse_oauth_state(state: str) -> tuple[str, str | None, str]:
    """Parse OAuth state parameter.

    Returns:
        tuple of (credential_scope, project_id, provider)

    Raises:
        HTTPException: If state format is invalid
    """
    try:
        parts = state.split(":")
        if len(parts) >= STATE_PARTS_EXTENDED:
            credential_scope = parts[0]
            project_id = parts[1] or None
            provider = parts[2]
        else:
            credential_scope = "project"
            project_id = parts[0]
            provider = parts[1]
    except (IndexError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid state format") from exc
    else:
        return credential_scope, project_id, provider


async def _exchange_oauth_code(provider: str, code: str, redirect_uri: str) -> dict[str, Any]:
    """Exchange OAuth authorization code for access token.

    Args:
        provider: OAuth provider (github, linear)
        code: Authorization code
        redirect_uri: Redirect URI

    Returns:
        Token data from provider

    Raises:
        HTTPException: If exchange fails or provider is unsupported
    """
    async with httpx.AsyncClient() as client:
        if provider == "github":
            token_url = "https://github.com/login/oauth/access_token"
            response = await client.post(
                token_url,
                headers={"Accept": "application/json"},
                data={
                    "client_id": os.environ.get("GITHUB_CLIENT_ID", ""),
                    "client_secret": os.environ.get("GITHUB_CLIENT_SECRET", ""),
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
        elif provider == "linear":
            token_url = "https://api.linear.app/oauth/token"
            response = await client.post(
                token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": os.environ.get("LINEAR_CLIENT_ID", ""),
                    "client_secret": os.environ.get("LINEAR_CLIENT_SECRET", ""),
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        else:
            raise HTTPException(status_code=400, detail=f"OAuth not supported for {provider}")

        if response.status_code != HTTP_OK:
            raise HTTPException(status_code=400, detail=f"Failed to exchange code: {response.text}")

        return response.json()


async def _get_provider_user_info(provider: str, access_token: str) -> dict[str, Any]:
    """Get user information from OAuth provider.

    Args:
        provider: OAuth provider (github, linear)
        access_token: Access token

    Returns:
        User info dict from provider
    """
    user_info: dict[str, Any] = {}

    if provider == "github":
        gh_client = GitHubClient(access_token)
        try:
            user_info = await gh_client.get_authenticated_user()
        finally:
            await gh_client.close()
    elif provider == "linear":
        linear_client = LinearClient(access_token)
        try:
            user_info = await linear_client.get_viewer()
        finally:
            await linear_client.close()

    return user_info


def _parse_token_scopes(provider: str, token_data: dict[str, Any]) -> list[str]:
    """Parse scopes from token response.

    Args:
        provider: OAuth provider
        token_data: Token response data

    Returns:
        List of scope strings
    """
    scope_str = cast("str", token_data.get("scope", ""))
    if provider == "linear":
        return scope_str.split(",")
    return scope_str.split(" ")


async def _find_existing_credential(
    repo: IntegrationCredentialRepository,
    params: "CredentialLookupParams",
) -> IntegrationCredential | None:
    """Find existing credential based on scope.

    Args:
        repo: Integration credential repository
        params: Credential lookup parameters

    Returns:
        Existing credential or None
    """
    sub = params.claims.get("sub")
    if params.credential_scope == "user":
        if not isinstance(sub, str):
            raise HTTPException(status_code=401, detail="User ID not found")
        return await repo.get_global_by_user_and_provider(sub, params.provider)

    if not isinstance(params.project_id, str) or not isinstance(params.provider, str):
        raise HTTPException(status_code=400, detail="Project and provider required")
    return await repo.get_by_project_and_provider(params.project_id, params.provider)


async def _store_or_update_credential(
    repo: IntegrationCredentialRepository,
    params: "CredentialStoreParams",
) -> str:
    """Store or update OAuth credential.

    Args:
        repo: Integration credential repository
        params: Credential storage parameters

    Returns:
        Credential ID
    """
    access_token = params.token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")

    scopes = _parse_token_scopes(params.provider, params.token_data)

    # Check for existing credential
    existing = await _find_existing_credential(
        repo,
        CredentialLookupParams(
            credential_scope=params.credential_scope,
            project_id=params.project_id,
            provider=params.provider,
            claims=params.claims,
        ),
    )

    if existing:
        # Update existing
        await repo.update(
            existing.id,
            token=access_token,
            refresh_token=params.token_data.get("refresh_token"),
            expires_at=None,  # GitHub tokens don't expire
            scopes=scopes,
            provider_user_id=str(params.user_info.get("id", "")),
            provider_metadata={"user": params.user_info},
        )
        return existing.id

    # Create new
    created_by = params.claims.get("sub")
    credential = await repo.create(
        project_id=params.project_id if params.credential_scope != "user" else None,
        provider=params.provider,
        credential_type="oauth",
        token=access_token,
        refresh_token=params.token_data.get("refresh_token"),
        scopes=scopes,
        provider_user_id=str(params.user_info.get("id", "")),
        provider_metadata={"user": params.user_info},
        created_by_user_id=created_by if isinstance(created_by, str) else None,
    )
    return credential.id


def _build_user_response(user_info: dict[str, Any]) -> dict[str, Any]:
    """Build user info response dict.

    Args:
        user_info: User info from provider

    Returns:
        Normalized user info dict
    """
    return {
        "id": user_info.get("id"),
        "login": user_info.get("login") or user_info.get("email"),
        "name": user_info.get("name"),
        "avatar_url": user_info.get("avatar_url") or user_info.get("avatarUrl"),
    }


@dataclass(frozen=True)
class CredentialLookupParams:
    """Parameters for looking up credentials."""

    credential_scope: str
    project_id: str | None
    provider: str
    claims: dict[str, Any]


@dataclass(frozen=True)
class CredentialStoreParams:
    """Parameters for storing credentials."""

    credential_scope: str
    project_id: str | None
    provider: str
    token_data: dict[str, Any]
    user_info: dict[str, Any]
    claims: dict[str, Any]


@dataclass(frozen=True)
class OAuthExchangeParams:
    """Parameters for OAuth exchange."""

    provider: str
    code: str
    redirect_uri: str
    credential_scope: str
    project_id: str | None
    claims: dict[str, Any]


async def _process_oauth_exchange(
    params: OAuthExchangeParams,
    db: AsyncSession,
) -> tuple[str, dict[str, Any]]:
    """Process OAuth token exchange and credential storage.

    Args:
        params: OAuth exchange parameters
        db: Database session

    Returns:
        Tuple of (credential_id, user_info)
    """
    # Exchange code for token
    token_data = await _exchange_oauth_code(
        params.provider,
        params.code,
        params.redirect_uri,
    )
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")

    # Get user info
    user_info = await _get_provider_user_info(params.provider, cast("str", access_token))

    # Store encrypted credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    repo = IntegrationCredentialRepository(db, encryption_service)

    # Store or update credential
    credential_id = await _store_or_update_credential(
        repo=repo,
        params=CredentialStoreParams(
            credential_scope=params.credential_scope,
            project_id=params.project_id,
            provider=params.provider,
            token_data=token_data,
            user_info=user_info,
            claims=params.claims,
        ),
    )

    return credential_id, user_info


async def oauth_callback(
    request: Request,
    data: dict[str, Any],
    claims: dict[str, Any],
    db: AsyncSession,
    ensure_project_access_fn: object,
) -> dict[str, Any]:
    """Handle OAuth callback and store credentials.

    Args:
        request: FastAPI request
        data: Request data with code, state, redirect_uri
        claims: Auth claims from auth_guard
        db: Database session
        ensure_project_access_fn: Function to check project access

    Returns:
        Success response with credential info

    Raises:
        HTTPException: On validation or exchange errors
    """
    enforce_rate_limit(request, claims)

    code = data.get("code")
    state = data.get("state")
    redirect_uri = data.get("redirect_uri")

    if not code or not state or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing code, state, or redirect_uri")

    # Parse state and validate access
    credential_scope, project_id, provider = _parse_oauth_state(cast("str", state))
    if project_id:
        cast("Any", ensure_project_access_fn)(project_id, claims)

    # Process OAuth exchange and store credential
    credential_id, user_info = await _process_oauth_exchange(
        OAuthExchangeParams(
            provider=provider,
            code=cast("str", code),
            redirect_uri=cast("str", redirect_uri),
            credential_scope=credential_scope,
            project_id=project_id,
            claims=claims,
        ),
        db,
    )

    return {
        "success": True,
        "credential_id": credential_id,
        "provider": provider,
        "user": _build_user_response(user_info),
    }
