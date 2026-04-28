"""Playwright adapter for OAuth flows.

Provides headless browser automation for OAuth flows that require interactive login.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class PlaywrightOAuthAdapter:
    """Adapter for Playwright-based OAuth automation.

    Requires playwright to be installed separately.
    This is a lightweight adapter that can work with or without playwright.

    Example:
        # Requires: pip install playwright && playwright install
        adapter = PlaywrightOAuthAdapter()

        tokens = adapter.authenticate(
            auth_url="https://oauth.example.com/authorize",
            success_pattern="code="
        )
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 60000,
    ):
        """Initialize Playwright adapter.

        Args:
            headless: Run browser in headless mode
            timeout: Default timeout in milliseconds

        Raises:
            ImportError: If playwright is not installed
        """
        self.headless = headless
        self.timeout = timeout
        self._playwright = None
        self._browser = None
        self._context = None

    def _ensure_playwright(self):
        """
        Ensure playwright is available.
        """
        if self._playwright is None:
            try:
                from playwright.sync_api import sync_playwright

                self._playwright_lib = sync_playwright
            except ImportError:
                raise ImportError(
                    "Playwright is not installed. Install with: "
                    "pip install playwright && playwright install",
                )

    def authenticate(
        self,
        auth_url: str,
        _success_pattern: str,
        credentials: dict[str, str] | None = None,
        _fill_callback: Callable | None = None,
    ) -> dict[str, Any]:
        """Perform OAuth authentication using Playwright.

        Args:
            auth_url: Authorization URL to navigate to
            success_pattern: URL pattern indicating success
            credentials: Optional credentials for auto-fill
            fill_callback: Custom callback for filling forms

        Returns:
            Dictionary with authentication result

        Raises:
            NotImplementedError: Playwright integration requires full implementation
        """
        raise NotImplementedError(
            "Full Playwright integration requires additional implementation. "
            "Install playwright and implement custom OAuth flow handling.",
        )

    def start_browser(self) -> None:
        """
        Start Playwright browser.
        """
        self._ensure_playwright()
        raise NotImplementedError("Playwright browser startup not implemented")

    def stop_browser(self) -> None:
        """
        Stop Playwright browser.
        """
        if self._browser:
            with contextlib.suppress(Exception):
                self._browser.close()
            self._browser = None
            self._context = None

    def __enter__(self):
        """
        Context manager entry.
        """
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.stop_browser()


class MockBrowserAdapter:
    """Mock browser adapter for testing OAuth flows.

    Simulates browser interactions without requiring Playwright.

    Example:
        adapter = MockBrowserAdapter(
            mock_response={"code": "test_auth_code"}
        )
        result = adapter.authenticate("https://example.com")
    """

    def __init__(self, mock_response: dict[str, Any] | None = None):
        """Initialize mock adapter.

        Args:
            mock_response: Mock response to return
        """
        self.mock_response = mock_response or {}

    def authenticate(
        self,
        auth_url: str,
        _success_pattern: str = "",
        credentials: dict[str, str] | None = None,
        _fill_callback: Callable | None = None,
    ) -> dict[str, Any]:
        """Simulate authentication.

        Args:
            auth_url: Authorization URL (not used)
            success_pattern: Success pattern (not used)
            credentials: Credentials (not used)
            fill_callback: Fill callback (not used)

        Returns:
            Mock response
        """
        return self.mock_response

    def start_browser(self) -> None:
        """
        Mock browser start.
        """

    def stop_browser(self) -> None:
        """
        Mock browser stop.
        """

    def __enter__(self):
        """
        Context manager entry.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """


__all__ = ["MockBrowserAdapter", "PlaywrightOAuthAdapter"]
