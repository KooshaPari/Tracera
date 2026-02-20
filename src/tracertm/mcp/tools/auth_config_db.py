"""Priority 1 MCP tools: Authentication, Configuration, Database.

This module provides critical infrastructure tools for TraceRTM:
- Auth tools: login, status, logout
- Config tools: init, show, set, get, unset, list
- DB tools: init, status, migrate, rollback, reset

All responses follow the standard MCP format with ok, action, data, and actor fields.
"""

from __future__ import annotations

import asyncio
import time
from typing import Final, cast

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.mcp.core import mcp

# HTTP status codes for comparisons
_STATUS_OK: Final[int] = 200
_STATUS_BAD_REQUEST: Final[int] = 400
# WorkOS poll intervals
_DEFAULT_POLL_INTERVAL = 5
_DEFAULT_EXPIRES_IN = 600
_SLOW_DOWN_INCREMENT = 5

_TOOL_OPERATION_ERRORS = (
    RuntimeError,
    ValueError,
    TypeError,
    OSError,
    LookupError,
    ConnectionError,
    TimeoutError,
    ImportError,
)


def _start_device_flow(
    authkit_domain: str,
    client_id: str,
    scopes: str | None,
    connect_endpoint: bool,
) -> tuple[str, str, str, int, int]:
    """Start WorkOS device flow and return polling parameters.

    Returns:
        Tuple of (device_code, user_code, verification_uri, interval, expires_in)
    """
    import httpx

    authkit_domain = authkit_domain.rstrip("/")
    device_endpoint = (
        f"{authkit_domain}/oauth2/device_authorization" if connect_endpoint else f"{authkit_domain}/authorize/device"
    )

    payload = {"client_id": client_id}
    if scopes:
        payload["scope"] = scopes

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(device_endpoint, data=payload)
            if resp.status_code >= _STATUS_BAD_REQUEST:
                msg = f"Device auth start failed: {resp.status_code} {resp.text}"
                raise RuntimeError(msg)

            data = resp.json()
            device_code = data.get("device_code")
            user_code = data.get("user_code")
            verification_uri = data.get("verification_uri")
            interval = int(data.get("interval", _DEFAULT_POLL_INTERVAL))
            expires_in = int(data.get("expires_in", _DEFAULT_EXPIRES_IN))

            if not device_code or not user_code or not verification_uri:
                msg = "Device auth response missing required fields"
                raise RuntimeError(msg)

            return device_code, user_code, verification_uri, interval, expires_in
    except (httpx.HTTPError, ValueError, TypeError) as e:
        msg = f"Device auth start failed: {e!s}"
        raise RuntimeError(msg) from e


def _poll_for_token(
    authkit_domain: str,
    device_code: str,
    client_id: str,
    interval: int,
    expires_in: int,
) -> dict[str, object]:
    """Poll for access token using device code.

    Returns:
        Dict with access_token and token metadata
    """
    import httpx

    token_endpoint = f"{authkit_domain.rstrip('/')}/oauth2/token"
    deadline = time.time() + expires_in

    try:
        with httpx.Client(timeout=30.0) as client:
            while time.time() < deadline:
                time.sleep(interval)
                token_payload = {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": client_id,
                }
                token_resp = client.post(token_endpoint, data=token_payload)

                if token_resp.status_code == _STATUS_OK:
                    token_data = token_resp.json()
                    access_token = token_data.get("access_token")
                    if not access_token:
                        msg = "Token response missing access_token"
                        raise RuntimeError(msg)

                    return {
                        "access_token": access_token,
                        "token_type": token_data.get("token_type", "Bearer"),
                        "expires_in": token_data.get("expires_in"),
                    }

                error = (
                    token_resp.json().get("error")
                    if token_resp.headers.get("content-type", "").startswith("application/json")
                    else None
                )

                if error == "authorization_pending":
                    continue
                if error == "slow_down":
                    interval += _SLOW_DOWN_INCREMENT
                    continue
                if error == "expired_token":
                    msg = "Device code expired. Please try login again."
                    raise RuntimeError(msg)
                if error == "access_denied":
                    msg = "Access denied. Please approve device login."
                    raise RuntimeError(msg)

                msg = f"Token request failed: {token_resp.status_code} {token_resp.text}"
                raise RuntimeError(msg)
    except (httpx.HTTPError, ValueError, TypeError) as e:
        msg = f"Token polling failed: {e!s}"
        raise RuntimeError(msg) from e

    msg = "Device code expired. Please try login again."
    raise RuntimeError(msg)


def _actor_from_context(ctx: object | None) -> dict[str, object] | None:
    """Extract actor info from MCP context."""
    if ctx is None:
        return None
    try:
        from fastmcp.server.dependencies import get_access_token
    except ImportError:
        return None

    token = get_access_token()
    if token is None:
        return None

    claims = getattr(token, "claims", {}) or {}
    return {
        "client_id": getattr(token, "client_id", None),
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "auth_type": claims.get("auth_type"),
    }


def _wrap(result: object, ctx: object | None, action: str) -> dict[str, object]:
    """Wrap result in standard MCP response format."""
    return {
        "ok": True,
        "action": action,
        "data": result,
        "actor": _actor_from_context(ctx),
    }


def _error(message: str, action: str, code: str = "ERROR") -> dict[str, object]:
    """Return error response."""
    return {
        "ok": False,
        "action": action,
        "error": message,
        "error_code": code,
    }


# ==========================================================================
# Authentication Tools
# ==========================================================================


@mcp.tool()
def auth_login(
    ctx: object,
    authkit_domain: str,
    client_id: str,
    scopes: str | None = None,
    connect_endpoint: bool = False,
) -> dict[str, object]:
    """Authenticate via WorkOS AuthKit device flow.

    Args:
        ctx: MCP context (for actor extraction)
        authkit_domain: WorkOS AuthKit domain (e.g., https://your-app.authkit.app)
        client_id: WorkOS AuthKit client ID
        scopes: Space-separated OAuth scopes (optional)
        connect_endpoint: Use /oauth2/device_authorization endpoint (WorkOS Connect)

    Returns:
        MCP response with access_token and device flow info
    """
    try:
        # Start device flow
        device_code, user_code, verification_uri, interval, expires_in = _start_device_flow(
            authkit_domain,
            client_id,
            scopes,
            connect_endpoint,
        )

        # Poll for token
        token_data = _poll_for_token(authkit_domain, device_code, client_id, interval, expires_in)

        # Store token in config
        config = ConfigManager()
        config.set("api_token", token_data["access_token"])

        return _wrap(
            {
                "access_token": token_data["access_token"],
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in"),
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": verification_uri,
                "config_path": str(config.config_path),
                "message": "Login successful. Token stored in ~/.tracertm/config.yaml",
            },
            ctx,
            "auth_login",
        )

    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Authentication failed: {e!s}", "auth_login", "AUTH_ERROR")


@mcp.tool()
def auth_status(ctx: object) -> dict[str, object]:
    """Check authentication token status.

    Returns:
        MCP response with token status
    """
    try:
        config = ConfigManager()
        token = config.get("api_token")

        return _wrap(
            {
                "authenticated": bool(token),
                "has_token": bool(token),
                "config_path": str(config.config_path),
            },
            ctx,
            "auth_status",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to check auth status: {e!s}", "auth_status", "STATUS_ERROR")


@mcp.tool()
def auth_logout(ctx: object) -> dict[str, object]:
    """Clear stored authentication token.

    Returns:
        MCP response confirming logout
    """
    try:
        config = ConfigManager()
        config.set("api_token", None)

        return _wrap(
            {
                "message": "Authentication token cleared",
                "config_path": str(config.config_path),
            },
            ctx,
            "auth_logout",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to logout: {e!s}", "auth_logout", "LOGOUT_ERROR")


# ==========================================================================
# Configuration Tools
# ==========================================================================


@mcp.tool()
def config_init(ctx: object, database_url: str) -> dict[str, object]:
    """Initialize TraceRTM configuration.

    Args:
        ctx: MCP context
        database_url: Database URL (SQLite: sqlite:///path.db or PostgreSQL)

    Returns:
        MCP response with config initialization status
    """
    try:
        config_manager = ConfigManager()
        config_manager.init(database_url=database_url)

        return _wrap(
            {
                "message": "Configuration initialized successfully",
                "config_path": str(config_manager.config_path),
                "database_url": database_url,
            },
            ctx,
            "config_init",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Configuration initialization failed: {e!s}", "config_init")


@mcp.tool()
def config_show(ctx: object) -> dict[str, object]:
    """Show current configuration.

    Returns:
        MCP response with all config values
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load()

        # Mask sensitive values
        config_dict = config.model_dump()
        if config_dict.get("database_url"):
            # Mask password in database URL
            url = config_dict["database_url"]
            if "@" in url:
                config_dict["database_url"] = url.split("@")[-1]

        if "api_token" in config_dict:
            config_dict["api_token"] = "***" if config_dict["api_token"] else None

        return _wrap(
            {
                "config": config_dict,
                "config_path": str(config_manager.config_path),
            },
            ctx,
            "config_show",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to load configuration: {e!s}", "config_show")


@mcp.tool()
def config_set(ctx: object, key: str, value: str | None) -> dict[str, object]:
    """Set a configuration value.

    Args:
        ctx: MCP context
        key: Configuration key (e.g., current_project_id, database_url)
        value: Configuration value (None to clear)

    Returns:
        MCP response with updated value
    """
    try:
        config_manager = ConfigManager()
        config_manager.set(key, value)

        return _wrap(
            {
                "key": key,
                "value": value,
                "message": f"Set {key} = {value}",
            },
            ctx,
            "config_set",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to set configuration: {e!s}", "config_set")


@mcp.tool()
def config_get(ctx: object, key: str) -> dict[str, object]:
    """Get a configuration value.

    Args:
        ctx: MCP context
        key: Configuration key to retrieve

    Returns:
        MCP response with the requested value
    """
    try:
        config_manager = ConfigManager()
        value = config_manager.get(key)

        return _wrap(
            {
                "key": key,
                "value": value,
            },
            ctx,
            "config_get",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get configuration: {e!s}", "config_get")


@mcp.tool()
def config_unset(ctx: object, key: str) -> dict[str, object]:
    """Unset a configuration value.

    Args:
        ctx: MCP context
        key: Configuration key to unset

    Returns:
        MCP response confirming unset
    """
    try:
        config_manager = ConfigManager()
        config_manager.set(key, None)

        return _wrap(
            {
                "key": key,
                "message": f"Unset {key}",
            },
            ctx,
            "config_unset",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to unset configuration: {e!s}", "config_unset")


@mcp.tool()
async def config_list(ctx: object) -> dict[str, object]:
    """List all configuration values.

    Returns:
        MCP response with all configuration key-value pairs
    """
    await asyncio.sleep(0)
    try:
        config_manager = ConfigManager()

        # Try get_all method first, fall back to load().model_dump()
        if hasattr(config_manager, "get_all") and callable(config_manager.get_all):
            raw = config_manager.get_all()
        else:
            raw = config_manager.load().model_dump()
        config_dict: dict[str, object] = cast("dict[str, object]", raw) if isinstance(raw, dict[str, object]) else {}  # type: ignore[misc]

        # Mask sensitive values
        display_config: dict[str, object] = {}
        for key, value in config_dict.items():
            if key == "database_url" and value and "@" in value:  # type: ignore[operator]
                display_config[key] = value.split("@")[-1]  # type: ignore[attr-defined]
            elif key == "api_token":
                display_config[key] = "***" if value else None
            else:
                display_config[key] = value

        return _wrap(
            {
                "config": display_config,
                "count": len(display_config),
            },
            ctx,
            "config_list",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to list configuration: {e!s}", "config_list")


# ==========================================================================
# Database Tools
# ==========================================================================


@mcp.tool()
async def db_init(ctx: object, database_url: str | None = None) -> dict[str, object]:
    """Initialize database configuration and prepare schema.

    Args:
        ctx: MCP context
        database_url: Optional database URL to set before initialization

    Returns:
        MCP response with initialization status
    """
    await asyncio.sleep(0)
    try:
        config_manager = ConfigManager()

        if database_url:
            config_manager.set("database_url", database_url)

        return _wrap(
            {
                "message": "Database init complete (configuration prepared)",
                "next_step": "Run db_migrate to create tables",
                "config_path": str(config_manager.config_path),
            },
            ctx,
            "db_init",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Database init failed: {e!s}", "db_init")


@mcp.tool()
async def db_status(ctx: object) -> dict[str, object]:
    """Check database health status.

    Returns:
        MCP response with database health information
    """
    await asyncio.sleep(0)
    try:
        config_manager = ConfigManager()
        config = config_manager.load()

        if not config.database_url:
            return _error(
                "Database URL not configured. Run config_init first.",
                "db_status",
                "NO_DATABASE_URL",
            )

        db = DatabaseConnection(config.database_url)
        db.connect()
        health = db.health_check()
        db.close()

        if health.get("status") == "connected":
            return _wrap(
                {
                    "status": "connected",
                    "version": health.get("version", "unknown"),
                    "tables": health.get("tables", 0),
                    "pool_size": health.get("pool_size", 0),
                    "checked_out": health.get("checked_out", 0),
                },
                ctx,
                "db_status",
            )
        return _error(
            f"Database error: {health.get('error')}",
            "db_status",
            "DATABASE_ERROR",
        )

    except FileNotFoundError as e:
        return _error(str(e), "db_status", "FILE_NOT_FOUND")
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Database check failed: {e!s}", "db_status", "CHECK_FAILED")


@mcp.tool()
async def db_migrate(ctx: object) -> dict[str, object]:
    """Run database migrations (create tables).

    Returns:
        MCP response with migration status
    """
    await asyncio.sleep(0)
    try:
        config_manager = ConfigManager()
        config = config_manager.load()

        if not config.database_url:
            return _error(
                "Database URL not configured. Run config_init first.",
                "db_migrate",
                "NO_DATABASE_URL",
            )

        db = DatabaseConnection(config.database_url)
        db.connect()

        db.create_tables()

        health = db.health_check()
        db.close()

        return _wrap(
            {
                "message": "Database tables created successfully",
                "tables_created": health.get("tables", 0),
            },
            ctx,
            "db_migrate",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Migration failed: {e!s}", "db_migrate", "MIGRATION_FAILED")


@mcp.tool()
async def db_rollback(ctx: object, confirm: bool = False) -> dict[str, object]:
    """Rollback database (drop all tables).

    WARNING: This will delete all data!

    Args:
        ctx: MCP context
        confirm: Must be True to proceed (safety check)

    Returns:
        MCP response with rollback status
    """
    await asyncio.sleep(0)
    try:
        if not confirm:
            return _error(
                "Rollback requires confirm=True (safety check for destructive operation)",
                "db_rollback",
                "CONFIRMATION_REQUIRED",
            )

        config_manager = ConfigManager()
        config = config_manager.load()

        if not config.database_url:
            return _error(
                "Database URL not configured",
                "db_rollback",
                "NO_DATABASE_URL",
            )

        db = DatabaseConnection(config.database_url)
        db.connect()
        db.drop_tables()
        db.close()

        return _wrap(
            {
                "message": "Database tables dropped successfully (DESTRUCTIVE OPERATION)",
            },
            ctx,
            "db_rollback",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Rollback failed: {e!s}", "db_rollback", "ROLLBACK_FAILED")


@mcp.tool()
async def db_reset(ctx: object, confirm: bool = False) -> dict[str, object]:
    """Reset database by dropping and recreating tables.

    WARNING: This will delete all data!

    Args:
        ctx: MCP context
        confirm: Must be True to proceed (safety check)

    Returns:
        MCP response with reset status
    """
    await asyncio.sleep(0)
    try:
        if not confirm:
            return _error(
                "Reset requires confirm=True (safety check for destructive operation)",
                "db_reset",
                "CONFIRMATION_REQUIRED",
            )

        config_manager = ConfigManager()
        config = config_manager.load()

        if not config.database_url:
            return _error(
                "Database URL not configured",
                "db_reset",
                "NO_DATABASE_URL",
            )

        db = DatabaseConnection(config.database_url)
        db.connect()
        db.drop_tables()
        db.create_tables()
        db.close()

        return _wrap(
            {
                "message": "Database reset complete (all tables recreated)",
            },
            ctx,
            "db_reset",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Reset failed: {e!s}", "db_reset", "RESET_FAILED")
