"""Generic OAuth2 provider implementation for the ``pheno`` namespace.

Migrated from the legacy package so CLI, QA, and adapters share one implementation.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pheno.domain.auth.types import (
    AuthResult,
    AuthTokens,
    Credentials,
    ProviderType,
    TokenError,
)
from pheno.ports.auth.providers import AuthProvider


class OAuth2GenericProvider(AuthProvider):
    """
    OAuth2 provider that supports any compliant authorization server.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        super().__init__(name, config)
        self.auth_url = config.get("auth_url")
        self.token_url = config.get("token_url")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.scope = config.get("scope", "")
        self.userinfo_url = config.get("userinfo_url")
        self.revoke_url = config.get("revoke_url")
        self.token_endpoint_auth_method = config.get(
            "token_endpoint_auth_method",
            "client_secret_post",
        )

        if not all([self.auth_url, self.token_url, self.client_id]):
            raise ValueError("Missing required OAuth2 configuration")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OAUTH2

    async def authenticate(self, credentials: Credentials) -> AuthResult:
        if not credentials.authorization_code:
            return AuthResult(
                success=False,
                error="Authorization code required for OAuth2 flow",
                error_code="missing_authorization_code",
            )

        try:
            tokens = await self._exchange_code_for_tokens(credentials)
            user_info = await self._get_user_info(tokens) if self.userinfo_url else None
            return AuthResult(success=True, tokens=tokens, user_info=user_info)
        except Exception as exc:
            return AuthResult(
                success=False,
                error=str(exc),
                error_code="oauth2_authentication_failed",
            )

    async def refresh(self, tokens: AuthTokens) -> AuthTokens:
        if not tokens.refresh_token:
            raise TokenError("No refresh token available")
        try:
            return await self._refresh_tokens(tokens.refresh_token)
        except Exception as exc:
            raise TokenError(f"Token refresh failed: {exc}") from exc

    async def revoke(self, tokens: AuthTokens) -> bool:
        if not self.revoke_url:
            return False
        try:
            await self._revoke_tokens(tokens.access_token)
            return True
        except Exception:
            return False

    def supports_refresh(self) -> bool:
        return bool(self.token_url and self.client_secret)

    def get_auth_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
            "state": state,
            "scope": self.scope,
        }
        return f"{self.auth_url}?{urlencode(params)}"

    async def _exchange_code_for_tokens(self, credentials: Credentials) -> AuthTokens:
        data = {
            "grant_type": "authorization_code",
            "code": credentials.authorization_code,
            "client_id": self.client_id,
            "redirect_uri": credentials.redirect_uri or self.redirect_uri,
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret
        response = await self._make_token_request(data)
        return self._parse_token_response(response)

    async def _refresh_tokens(self, refresh_token: str) -> AuthTokens:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret
        response = await self._make_token_request(data)
        return self._parse_token_response(response)

    async def _make_token_request(self, data: dict[str, Any]) -> dict[str, Any]:
        body = urlencode(data).encode("utf-8")
        req = Request(
            self.token_url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(req) as resp:  # pragma: no cover - network IO
            return json.loads(resp.read().decode("utf-8"))

    def _parse_token_response(self, response: dict[str, Any]) -> AuthTokens:
        access_token = response.get("access_token")
        if not access_token:
            raise TokenError("No access token in response")
        expires_in = response.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        return AuthTokens(
            access_token=access_token,
            refresh_token=response.get("refresh_token"),
            id_token=response.get("id_token"),
            token_type=response.get("token_type", "Bearer"),
            expires_at=expires_at,
            scope=response.get("scope"),
            metadata=response,
        )

    async def _get_user_info(self, tokens: AuthTokens) -> dict[str, Any] | None:
        req = Request(
            self.userinfo_url,
            headers={"Authorization": f"{tokens.token_type} {tokens.access_token}"},
        )
        try:
            with urlopen(req) as resp:  # pragma: no cover
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    async def _revoke_tokens(self, access_token: str) -> None:
        data = {"token": access_token}
        if self.client_secret:
            data["client_secret"] = self.client_secret
        body = urlencode(data).encode("utf-8")
        req = Request(
            self.revoke_url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(req):  # pragma: no cover
            return


__all__ = ["OAuth2GenericProvider"]
