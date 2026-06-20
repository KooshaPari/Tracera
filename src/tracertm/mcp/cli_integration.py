"""Integration layer between CLI and MCP authentication.

Enables CLI tokens to work seamlessly with MCP by:
- Loading CLI tokens for MCP operations
- Updating MCP tokens when CLI tokens refresh
- Handling token expiration gracefully
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from tracertm.mcp.token_manager import TokenInfo, TokenManager, get_token_manager

if TYPE_CHECKING:
    from tracertm.cli.auth import AuthTokens, TokenStorage, get_token_storage
else:
    AuthTokens = Any
    TokenStorage = Any
    get_token_storage = None

logger = logging.getLogger(__name__)


class CLITokenAdapter:
    """Adapts CLI tokens for use with MCP."""

    def __init__(
        self,
        cli_token_storage: TokenStorage | None = None,
        mcp_token_manager: TokenManager | None = None,
    ) -> None:
        """Initialize adapter.

        Args:
            cli_token_storage: CLI token storage instance
            mcp_token_manager: MCP token manager instance
        """
        self.cli_storage = cli_token_storage
        self.mcp_manager = mcp_token_manager or get_token_manager()

    def sync_from_cli(self) -> bool:
        """Sync CLI tokens to MCP storage.

        Returns:
            True if sync successful, False if no tokens available
        """
        if not self.cli_storage:
            logger.debug("CLI token storage not available")
            return False

        try:
            cli_tokens = self.cli_storage.load_tokens()
            if not cli_tokens:
                logger.debug("No CLI tokens found")
                return False

            # Convert CLI tokens to MCP token format
            mcp_token = TokenInfo(
                access_token=cli_tokens.access_token,
                token_type=cli_tokens.token_type,
                expires_at=cli_tokens.expires_at,
                refresh_token=cli_tokens.refresh_token,
                user_id=cli_tokens.user_id,
                email=cli_tokens.email,
                scopes=[],
            )

            # Save to MCP storage
            self.mcp_manager.save_token(mcp_token)
            logger.info("Synced CLI tokens to MCP storage")
        except Exception as e:
            logger.warning("Failed to sync CLI tokens: %s", e)
            return False
        else:
            return True

    def sync_to_cli(self) -> bool:
        """Sync MCP tokens back to CLI storage.

        This is useful when MCP refreshes tokens.

        Returns:
            True if sync successful, False if tokens not available or CLI storage unavailable
        """
        if not self.cli_storage:
            logger.debug("CLI token storage not available")
            return False

        try:
            mcp_token = self.mcp_manager.load_token()
            if not mcp_token:
                logger.debug("No MCP token found")
                return False

            # Convert MCP token to CLI token format
            cli_tokens = AuthTokens(
                access_token=mcp_token.access_token,
                token_type=mcp_token.token_type,
                expires_at=mcp_token.expires_at,
                refresh_token=mcp_token.refresh_token,
                user_id=mcp_token.user_id,
                email=mcp_token.email,
            )

            # Save to CLI storage
            self.cli_storage.save_tokens(cli_tokens)
            logger.info("Synced MCP tokens to CLI storage")
        except Exception as e:
            logger.warning("Failed to sync MCP tokens to CLI: %s", e)
            return False
        else:
            return True

    def get_mcp_token(self, fallback_to_cli: bool = False) -> str | None:
        """Get valid MCP token, optionally falling back to CLI tokens.

        Args:
            fallback_to_cli: If True, try CLI tokens if MCP tokens unavailable

        Returns:
            Access token string or None
        """
        # Try MCP tokens first
        mcp_token = self.mcp_manager.get_valid_token()
        if mcp_token:
            return mcp_token

        # Fall back to CLI tokens if requested
        if fallback_to_cli and self.cli_storage:
            try:
                cli_tokens = self.cli_storage.load_tokens()
                is_expired_fn = getattr(cli_tokens, "is_expired", None) if cli_tokens is not None else None
                expired = is_expired_fn() if callable(is_expired_fn) else True
                if cli_tokens and not expired:
                    # Sync CLI token to MCP for future use
                    self.sync_from_cli()
                    return getattr(cli_tokens, "access_token", None)
            except Exception as e:
                logger.debug("Could not get CLI token: %s", e)

        return None

    def ensure_authenticated(self, fallback_to_cli: bool = False) -> bool:
        """Ensure MCP has valid authentication.

        Args:
            fallback_to_cli: If True, try syncing from CLI if MCP not authenticated

        Returns:
            True if authenticated, False otherwise
        """
        if self.mcp_manager.is_authenticated():
            return True

        if fallback_to_cli:
            return self.sync_from_cli()

        return False


def create_cli_adapter() -> CLITokenAdapter | None:
    """Create CLI token adapter if possible.

    Returns:
        CLITokenAdapter instance or None if CLI not available
    """
    try:
        if get_token_storage is None:
            logger.debug("CLI token storage not available")
            return None

        cli_storage = get_token_storage()
        return CLITokenAdapter(cli_token_storage=cli_storage)
    except Exception as e:
        logger.warning("Could not create CLI adapter: %s", e)
        return None


def get_cli_adapter() -> CLITokenAdapter | None:
    """Get the global CLI adapter instance."""
    global _CLI_ADAPTER
    if "_CLI_ADAPTER" not in globals():
        _CLI_ADAPTER = create_cli_adapter()
    return _CLI_ADAPTER


# Global adapter instance
_CLI_ADAPTER: CLITokenAdapter | None = None


def ensure_cli_mcp_sync() -> None:
    """Optionally sync CLI tokens into MCP storage.

    This is an explicit opt-in helper and is not required for MCP operation.
    """
    adapter = get_cli_adapter()
    if adapter:
        adapter.sync_from_cli()
        logger.info("CLI-MCP token sync completed")
    else:
        logger.debug("CLI-MCP token sync not available")
