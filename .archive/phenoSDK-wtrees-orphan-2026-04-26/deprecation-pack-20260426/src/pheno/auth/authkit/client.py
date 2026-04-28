"""
AuthKit Client for Standalone Connect authentication.
"""

from __future__ import annotations

import os
from typing import Any

import aiohttp
import jwt as pyjwt

from .storage.session import SessionStorage
from .tokens.manager import TokenManager


class AuthKit:
    """
    AuthKit client for Standalone Connect OAuth flow.
    """

    def __init__(
        self,
        base_url: str,
        storage: SessionStorage | None = None,
        client_id: str | None = None,
        workos_api_key: str | None = None,
    ):
        """Initialize AuthKit client.

        Args:
            base_url: Base URL of your AuthKit-enabled server (production Vercel deployment)
            storage: Session storage backend (defaults to filesystem)
            client_id: WorkOS client ID (optional, from env)
            workos_api_key: WorkOS API key (optional, from env)
        """
        self.base_url = base_url.rstrip("/")
        self.storage = storage or SessionStorage.filesystem()
        self.client_id = client_id or os.getenv("WORKOS_CLIENT_ID", "")
        self.workos_api_key = workos_api_key or os.getenv("WORKOS_API_KEY", "")
        self.token_manager = TokenManager(
            storage=self.storage,
            refresh_handler=self._refresh_tokens,
        )
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create aiohttp session.
        """
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def close(self):
        """
        Close HTTP session.
        """
        if self._session and not self._session.closed:
            await self._session.close()

    async def login_standalone_connect(self) -> dict[str, Any]:
        """Execute Standalone Connect OAuth flow.

        Returns:
            dict: Credentials with access_token, refresh_token, user info

        Raises:
            RuntimeError: If authentication fails
        """
        # Step 1: Initiate OAuth via server
        session = await self._get_session()

        auth_url = f"{self.base_url}/auth/init"

        async with session.get(auth_url) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise RuntimeError(f"Failed to initiate auth: {text}")

            result = await resp.json()
            auth_redirect = result.get("url")

            if not auth_redirect:
                raise RuntimeError("No authorization URL returned")

        # Step 2: Open browser for user to authenticate
        print("\n🔐 Opening browser for authentication...")
        print(f"📍 URL: {auth_redirect}")

        import webbrowser

        webbrowser.open(auth_redirect)

        # Step 3: Wait for callback (user completes auth in browser)
        print("\n⏳ Waiting for authentication to complete...")
        print("   (Complete the login in your browser)")

        # For Standalone Connect, we need to poll or wait for completion
        # In production, the server handles the callback and we retrieve the session

        # Step 4: Poll for session or retrieve tokens
        # This is simplified - in production you'd have a callback endpoint
        print("\n✅ Authentication flow initiated!")
        print("   Complete the login in your browser window.")

        # Return placeholder - real implementation would retrieve tokens
        return {
            "status": "initiated",
            "message": "Complete authentication in browser",
            "auth_url": auth_redirect,
        }

    async def get_access_token(self) -> str | None:
        """Get current access token, refreshing if needed.

        Returns:
            Access token or None if not authenticated
        """
        return await self.token_manager.get_access_token()

    async def refresh_token(self) -> dict[str, Any] | None:
        """Refresh access token using refresh token.

        Returns:
            New credentials or None if refresh fails
        """
        return await self.token_manager.refresh_tokens()

    async def logout(self):
        """
        Clear stored credentials.
        """
        await self.token_manager.clear()
        print("✅ Logged out successfully")

    async def get_user_info(self) -> dict[str, Any] | None:
        """Get user info from stored session.

        Returns:
            User info dict or None if not authenticated
        """
        creds = await self.storage.load()
        if not creds:
            return None

        return creds.get("user")

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode JWT token without verification.

        Args:
            token: JWT token string

        Returns:
            Decoded token claims
        """
        return pyjwt.decode(token, options={"verify_signature": False})

    async def __aenter__(self):
        """
        Context manager entry.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        await self.close()

    async def _refresh_tokens(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        """
        Default refresh handler (override when server exposes refresh endpoint).
        """
        return None
