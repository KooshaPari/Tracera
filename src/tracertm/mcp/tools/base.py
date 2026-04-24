"""Base utilities for MCP tools.

Provides shared database access patterns, response formatting,
and context resolution used across all tool modules.
"""

from __future__ import annotations

from pathlib import Path

from fastmcp.exceptions import ToolError
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection

# Module-level singletons (lazy initialized)
_config_manager: ConfigManager | None = None
_db_connection: DatabaseConnection | None = None


def get_config_manager() -> ConfigManager:
    """Get or create the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_db_connection() -> DatabaseConnection:
    """Get or create the global DatabaseConnection instance.

    Falls back to local SQLite if no database_url configured.
    """
    global _db_connection
    if _db_connection is None:
        config = get_config_manager()
        database_url = config.get("database_url")
        if not database_url:
            base_dir = Path.home() / ".tracertm"
            base_dir.mkdir(parents=True, exist_ok=True)
            database_url = f"sqlite:///{base_dir / 'tracertm.db'}"

        # Ensure database_url is a string
        if not isinstance(database_url, str):
            database_url = str(database_url)

        _db_connection = DatabaseConnection(database_url)
        _db_connection.connect()
    return _db_connection


def get_session() -> Session:
    """Get a new SQLAlchemy session from the connection."""
    db = get_db_connection()
    return Session(db.engine)


def get_current_project_id() -> str | None:
    """Get the currently selected project ID from config."""
    config = get_config_manager()
    value = config.get("current_project_id")
    return str(value) if value else None


def require_project() -> str:
    """Get current project ID or raise ToolError if not set."""
    project_id = get_current_project_id()
    if not project_id:
        msg = "No project selected. Use project_manage(action='select', payload={'project_id': '...'}) first."
        raise ToolError(
            msg,
        )
    return project_id


def set_current_project(project_id: str) -> None:
    """Set the current project ID in config."""
    config = get_config_manager()
    config.set("current_project_id", project_id)


# Response envelope utilities


def wrap_success(
    data: object,
    action: str,
    ctx: object | None = None,
    lean: bool = True,
) -> dict[str, object] | object:
    """Wrap a successful response in the standard envelope.

    Args:
        data: Response data
        action: Action name
        ctx: MCP context
        lean: If True, return lean response (just data); if False, include metadata

    Returns:
        Formatted response (lean mode returns just data, standard includes metadata)
    """
    if lean:
        # Lean mode: return just the data
        return data
    # Standard mode: include basic metadata
    return {
        "ok": True,
        "action": action,
        "data": data,
        "actor": extract_actor(ctx),
    }


def wrap_error(
    error: str,
    action: str,
    ctx: object | None = None,
    lean: bool = True,
) -> dict[str, object]:
    """Wrap an error response in the standard envelope.

    Args:
        error: Error message
        action: Action name
        ctx: MCP context
        lean: If True, return lean error; if False, include full metadata

    Returns:
        Formatted error response
    """
    if lean:
        return {
            "ok": False,
            "error": error,
        }
    return {
        "ok": False,
        "action": action,
        "error": error,
        "actor": extract_actor(ctx),
    }


def extract_actor(ctx: object | None) -> dict[str, object] | None:
    """Extract actor information from the MCP context."""
    if ctx is None:
        return None

    try:
        from fastmcp.server.dependencies import get_access_token
    except Exception:
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
        "scopes": getattr(token, "scopes", None),
        "project_id": claims.get("project_id"),
        "project_ids": claims.get("project_ids"),
    }


def resolve_project_from_token(
    payload: dict[str, object],
    ctx: object | None,
) -> str | None:
    """Resolve project_id from token claims with access control.

    Priority:
    1. Explicit project_id in payload (validated against token)
    2. Single project_id from token claims
    3. None (caller must handle)

    Raises ToolError if:
    - Token has project restrictions and explicit project_id is not allowed
    - Token has multiple projects but no explicit project_id provided
    """
    project_id = payload.get("project_id")

    if ctx is None:
        return str(project_id) if project_id else None

    try:
        from fastmcp.server.dependencies import get_access_token

        token = get_access_token()
    except Exception:
        return str(project_id) if project_id else None

    if token is None:
        return str(project_id) if project_id else None

    claims = getattr(token, "claims", {}) or {}
    if not isinstance(claims, dict):
        claims = {}

    # Build list of allowed project IDs from token
    allowed: list[str] = []
    if claims.get("project_id"):
        allowed.append(str(claims["project_id"]))

    project_ids = claims.get("project_ids")
    if isinstance(project_ids, str):
        allowed.extend([p.strip() for p in project_ids.split(",") if p.strip()])
    elif isinstance(project_ids, (list, tuple, set)):
        allowed.extend([str(p) for p in project_ids if p])

    # If token has project restrictions, enforce them
    if allowed:
        if project_id:
            if project_id not in allowed:
                msg = "Project access denied for requested project_id."
                raise ToolError(msg)
            return str(project_id) if project_id else None
        if len(allowed) == 1:
            return allowed[0]
        msg = "project_id required for this request (multiple projects available)."
        raise ToolError(msg)

    return str(project_id) if project_id else None


__all__ = [
    "extract_actor",
    "get_config_manager",
    "get_current_project_id",
    "get_db_connection",
    "get_session",
    "require_project",
    "resolve_project_from_token",
    "set_current_project",
    "wrap_error",
    "wrap_success",
]
