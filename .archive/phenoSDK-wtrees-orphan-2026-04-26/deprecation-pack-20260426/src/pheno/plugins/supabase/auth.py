"""
Supabase authentication helpers.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from pheno.plugins.supabase.client import get_supabase
from pheno.security.jwt_utils import decode_jwt

if TYPE_CHECKING:
    from collections.abc import Callable


class SupabaseAuthError(RuntimeError):
    """
    Raised when Supabase auth operations fail.
    """


class SupabaseAuthClient:
    """
    Lightweight helper around Supabase auth endpoints.
    """

    def __init__(
        self,
        *,
        supabase_factory: Callable[[str | None], Any] = get_supabase,
    ) -> None:
        self._factory = supabase_factory
        self._client: Any | None = None
        self._current_token: str | None = None

    # ------------------------------------------------------------------ #
    # Client helpers
    # ------------------------------------------------------------------ #
    def _get_client(self, token: str | None = None):
        token_changed = token and token != self._current_token
        if self._client is None or token_changed:
            self._current_token = token or self._current_token
            self._client = self._factory(self._current_token)
        return self._client

    # ------------------------------------------------------------------ #
    # Token helpers
    # ------------------------------------------------------------------ #
    def validate_token(self, token: str) -> dict[str, Any] | None:
        """
        Decode a JWT token without verifying signature (best-effort).
        """
        try:
            claims = decode_jwt(token, verify=False)
            claims["access_token"] = token
            return claims
        except Exception:
            return None

    async def validate_token_async(self, token: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self.validate_token, token)

    # ------------------------------------------------------------------ #
    # User helpers
    # ------------------------------------------------------------------ #
    def get_user(self, token: str) -> dict[str, Any] | None:
        """
        Return the Supabase user payload for the provided token.
        """
        client = self._get_client(token)
        try:
            response = client.auth.get_user(token)
            user = getattr(response, "user", None)
        except Exception as exc:  # pragma: no cover - supabase dependency
            raise SupabaseAuthError(f"Supabase get_user failed: {exc}") from exc

        if not user or getattr(user, "id", None) is None:
            return None

        metadata = getattr(user, "user_metadata", {}) or {}
        return {
            "id": user.id,
            "email": getattr(user, "email", None),
            "metadata": metadata,
            "roles": metadata.get("roles", []),
        }

    async def get_user_async(self, token: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self.get_user, token)


__all__ = ["SupabaseAuthClient", "SupabaseAuthError"]
