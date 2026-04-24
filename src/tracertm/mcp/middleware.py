"""MCP Auth Middleware for TraceRTM.

Provides:
- Token refresh logic
- Scope-based access control
- Error handling for expired tokens
- Logging and tracing
"""

from __future__ import annotations

import logging
import time

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

# Seconds considered "expiring soon" for token warning (5 minutes)
_TOKEN_EXPIRING_SOON_SEC = 300


class AuthMiddleware(Middleware):
    """Validates token claims and enforces scope-based access control."""

    def __init__(self, required_scopes: list[str] | None = None) -> None:
        """Initialize auth middleware.

        Args:
            required_scopes: List of scopes required for all tools
        """
        self.required_scopes = required_scopes or []
        self._tool_scopes: dict[str, list[str]] = {}

    def register_tool_scopes(self, tool_name: str, scopes: list[str]) -> None:
        """Register required scopes for a specific tool.

        Args:
            tool_name: Name of the tool
            scopes: List of required scopes
        """
        self._tool_scopes[tool_name] = scopes

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        tool_name: str,
        _arguments: dict[str, object],
    ) -> None:
        """Intercept tool calls to enforce auth.

        Args:
            ctx: Middleware context
            tool_name: Name of the tool being called
            arguments: Tool arguments

        Raises:
            PermissionError: If token expired or scopes insufficient
        """
        try:
            # Check if context has auth info
            if not hasattr(ctx, "auth"):
                logger.warning("No auth context for tool: %s", tool_name)
                next_fn = getattr(ctx, "next", None)
                if next_fn is not None and callable(next_fn):
                    await next_fn()
                return

            auth = getattr(ctx, "auth", None)
            if not isinstance(auth, dict):
                logger.warning("Auth context invalid for tool: %s", tool_name)
                next_fn = getattr(ctx, "next", None)
                if next_fn is not None and callable(next_fn):
                    await next_fn()
                return

            # Validate token freshness
            await self._validate_token(auth)

            # Check scopes
            required_scopes = self._get_required_scopes(tool_name)
            if required_scopes:
                self._validate_scopes(auth, required_scopes, tool_name)

            logger.debug("Auth validated for tool: %s", tool_name)

        except PermissionError:
            logger.exception("Auth error for %s", tool_name)
            raise
        except Exception:
            logger.exception("Unexpected auth error for %s", tool_name)
            raise

        # Continue to next middleware
        next_fn = getattr(ctx, "next", None)
        if next_fn is not None and callable(next_fn):
            await next_fn()

    async def _validate_token(self, auth: dict[str, object]) -> None:
        """Validate token freshness and potentially refresh.

        Args:
            auth: Auth context with token claims

        Raises:
            PermissionError: If token expired and cannot refresh
        """
        claims = auth.get("claims", {})
        if not isinstance(claims, dict):
            claims = {}

        # Check expiration
        exp = claims.get("exp")
        if exp is None:
            logger.debug("Token has no expiration")
            return

        now = time.time()
        expires_in = exp - now

        if expires_in < 0:
            # Track auth failure in metrics if available
            try:
                from tracertm.mcp.metrics import track_auth_failure

                track_auth_failure("expired_token")
            except ImportError:
                pass

            msg = f"Token expired {abs(expires_in):.0f}s ago"
            raise PermissionError(msg)

        # Warn if expiring soon (within 5 minutes)
        if expires_in < _TOKEN_EXPIRING_SOON_SEC:
            logger.warning("Token expiring soon: %.0fs remaining", expires_in)

    def _get_required_scopes(self, tool_name: str) -> list[str]:
        """Get required scopes for tool.

        Args:
            tool_name: Name of tool

        Returns:
            List of required scopes
        """
        # Tool-specific scopes take precedence
        if tool_name in self._tool_scopes:
            return self._tool_scopes[tool_name]

        # Otherwise use global scopes
        return self.required_scopes

    def _validate_scopes(self, auth: dict[str, object], required_scopes: list[str], tool_name: str) -> None:
        """Validate that token has required scopes.

        Args:
            auth: Auth context
            required_scopes: List of required scopes
            tool_name: Name of tool

        Raises:
            PermissionError: If scopes insufficient
        """
        if not required_scopes:
            return

        claims = auth.get("claims", {})
        if not isinstance(claims, dict):
            claims = {}
        token_scopes = (claims.get("scope") or "").split()

        missing_scopes = set(required_scopes) - set(token_scopes)

        if missing_scopes:
            # Track auth failure in metrics if available
            try:
                from tracertm.mcp.metrics import track_auth_failure

                track_auth_failure("missing_scopes")
            except ImportError:
                pass

            msg = f"Tool '{tool_name}' requires scopes {missing_scopes}, but token has {set(token_scopes)}"
            raise PermissionError(
                msg,
            )


class LoggingMiddleware(Middleware):
    """Log all tool calls for debugging and tracing."""

    def __init__(self, verbose: bool = False) -> None:
        """Initialize logging middleware.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        tool_name: str,
        arguments: dict[str, object],
    ) -> None:
        """Log tool calls.

        Args:
            ctx: Middleware context
            tool_name: Name of tool
            arguments: Tool arguments
        """
        start_time = time.time()

        log_msg = f"[MCP_TOOL] {tool_name}"
        if self.verbose:
            log_msg += f" with args: {arguments}"

        logger.info(log_msg)

        try:
            next_fn = getattr(ctx, "next", None)
            if next_fn is not None and callable(next_fn):
                await next_fn()
            elapsed = time.time() - start_time
            logger.debug("[MCP_TOOL] %s completed in %.2fs", tool_name, elapsed)
        except Exception:
            elapsed = time.time() - start_time
            logger.exception("[MCP_TOOL] %s failed after %.2fs", tool_name, elapsed)
            raise


class RateLimitMiddleware(Middleware):
    """Rate limit tool calls per user or globally."""

    def __init__(
        self,
        calls_per_minute: int = 60,
        calls_per_hour: int = 1000,
        per_user: bool = True,
    ) -> None:
        """Initialize rate limiter.

        Args:
            calls_per_minute: Max calls per minute
            calls_per_hour: Max calls per hour
            per_user: Rate limit per user (True) or globally (False)
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        self.per_user = per_user
        self._call_times: dict[str, list[float]] = {}

    def _get_key(self, ctx: MiddlewareContext) -> str:
        """Get rate limit key (user ID or global).

        Args:
            ctx: Middleware context

        Returns:
            Rate limit key
        """
        if not self.per_user:
            return "global"

        auth = getattr(ctx, "auth", None)
        if isinstance(auth, dict):
            claims = auth.get("claims", {})
            return str(claims.get("sub", "anonymous"))

        return "anonymous"

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        _tool_name: str,
        _arguments: dict[str, object],
    ) -> None:
        """Check rate limits before allowing tool call.

        Args:
            ctx: Middleware context
            tool_name: Name of tool
            arguments: Tool arguments

        Raises:
            PermissionError: If rate limit exceeded
        """
        key = self._get_key(ctx)
        now = time.time()

        # Initialize call times for key if needed
        if key not in self._call_times:
            self._call_times[key] = []

        call_times = self._call_times[key]

        # Remove old entries
        one_minute_ago = now - 60
        one_hour_ago = now - 3600
        call_times[:] = [t for t in call_times if t > one_hour_ago]

        # Check rate limits
        recent_calls = [t for t in call_times if t > one_minute_ago]

        if len(recent_calls) >= self.calls_per_minute:
            # Track rate limit hit in metrics if available
            try:
                from tracertm.mcp.metrics import track_rate_limit_hit

                track_rate_limit_hit(key, "per_minute")
            except ImportError:
                pass

            msg = f"Rate limit exceeded: {self.calls_per_minute} calls/minute for {key}"
            raise PermissionError(msg)

        if len(call_times) >= self.calls_per_hour:
            # Track rate limit hit in metrics if available
            try:
                from tracertm.mcp.metrics import track_rate_limit_hit

                track_rate_limit_hit(key, "per_hour")
            except ImportError:
                pass

            msg = f"Rate limit exceeded: {self.calls_per_hour} calls/hour for {key}"
            raise PermissionError(msg)

        # Record call
        call_times.append(now)

        logger.debug("Rate limit check passed for %s: %s calls/min", key, len(recent_calls))

        next_fn = getattr(ctx, "next", None)
        if next_fn is not None and callable(next_fn):
            await next_fn()
