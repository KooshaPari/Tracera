"""Enhanced error handling for MCP tools with LLM-friendly messages.

Provides:
- Contextual error messages for common issues
- Recovery suggestions
- Sanitization of sensitive data
- Structured error responses
"""

from __future__ import annotations

import logging
import re

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class LLMFriendlyError(Exception):
    """Base exception for LLM-friendly errors with recovery hints."""

    def __init__(
        self,
        message: str,
        recovery_hint: str | None = None,
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize LLM-friendly error.

        Args:
            message: Human-readable error message
            recovery_hint: Suggested recovery action
            context: Additional context (sanitized)
        """
        super().__init__(message)
        self.message = message
        self.recovery_hint = recovery_hint
        self.context = context or {}

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, object] = {
            "error": self.message,
            "type": type(self).__name__,
        }

        if self.recovery_hint:
            result["recovery_hint"] = self.recovery_hint

        if self.context:
            result["context"] = self.context

        return result


class ProjectNotSelectedError(LLMFriendlyError):
    """Raised when no project is selected."""

    def __init__(self) -> None:
        """Initialize project not selected error."""
        super().__init__(
            message="No project is currently selected.",
            recovery_hint=(
                "Use create_project() to create a new project, "
                "or select_project(project_id='...') to select an existing one. "
                "Use list_projects() to see available projects."
            ),
        )


class ProjectNotFoundError(LLMFriendlyError):
    """Raised when project doesn't exist."""

    def __init__(self, project_id: str) -> None:
        """Initialize project not found error.

        Args:
            project_id: ID of the project that was not found
        """
        super().__init__(
            message=f"Project '{project_id}' not found.",
            recovery_hint=("Use list_projects() to see available projects, or create_project() to create a new one."),
            context={"project_id": project_id},
        )


class ItemNotFoundError(LLMFriendlyError):
    """Raised when item doesn't exist."""

    def __init__(self, item_id: str, project_id: str | None = None) -> None:
        """Initialize item not found error.

        Args:
            item_id: ID of the item that was not found
            project_id: Optional ID of the project
        """
        context: dict[str, object] = {"item_id": item_id}
        if project_id:
            context["project_id"] = project_id

        super().__init__(
            message=f"Item '{item_id}' not found.",
            recovery_hint=("Use query_items() to search for items, or create_item() to create a new one."),
            context=context,
        )


class InvalidLinkError(LLMFriendlyError):
    """Raised when link creation fails."""

    def __init__(self, source_id: str, target_id: str, reason: str) -> None:
        """Initialize invalid link error.

        Args:
            source_id: ID of the source item
            target_id: ID of the target item
            reason: Reason for failure
        """
        super().__init__(
            message=f"Cannot create link from '{source_id}' to '{target_id}': {reason}",
            recovery_hint=(
                "Verify both items exist with get_item(), "
                "check for circular dependencies with detect_cycles(), "
                "and ensure link types are valid."
            ),
            context={
                "source_id": source_id,
                "target_id": target_id,
                "reason": reason,
            },
        )


class DatabaseError(LLMFriendlyError):
    """Raised when database operations fail."""

    def __init__(self, operation: str, original_error: str) -> None:
        """Initialize database error.

        Args:
            operation: Name of the failed operation
            original_error: Original error message
        """
        super().__init__(
            message=f"Database operation '{operation}' failed.",
            recovery_hint=(
                "Check database connection with 'rtm config show', "
                "ensure database is properly initialized with 'rtm config init', "
                "and verify credentials are correct."
            ),
            context={
                "operation": operation,
                "error": self._sanitize_db_error(original_error),
            },
        )

    @staticmethod
    def _sanitize_db_error(error: str) -> str:
        """Remove sensitive information from database errors."""
        error = re.sub(r"://[^:]+:([^@]+)@", r"://***:***@", error)

        return re.sub(r"/[/\w.-]+\.db", r"***.db", error)


class ValidationError(LLMFriendlyError):
    """Raised when input validation fails."""

    def __init__(self, field: str, value: object, reason: str) -> None:
        """Initialize validation error.

        Args:
            field: Name of the field that failed validation
            value: Invalid value
            reason: Reason for failure
        """
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            recovery_hint=(
                "Check the tool documentation for valid field values, "
                "ensure required fields are provided, "
                "and verify data types are correct."
            ),
            context={
                "field": field,
                "value": str(value)[:100],
                "reason": reason,
            },
        )


class AuthorizationError(LLMFriendlyError):
    """Raised when user lacks required permissions."""

    def __init__(self, required_scopes: list[str], user_scopes: list[str]) -> None:
        """Initialize authorization error.

        Args:
            required_scopes: List of required scopes
            user_scopes: List of user's current scopes
        """
        super().__init__(
            message="Insufficient permissions for this operation.",
            recovery_hint=("Request access from your administrator, or use a token with appropriate scopes."),
            context={
                "required": required_scopes,
                "available": user_scopes,
                "missing": list(set(required_scopes) - set(user_scopes)),
            },
        )


class RateLimitError(LLMFriendlyError):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit_type: str, limit: int, wait_seconds: float | None = None) -> None:
        """Initialize rate limit error.

        Args:
            limit_type: Type of limit exceeded
            limit: Limit value
            wait_seconds: Optional seconds to wait
        """
        message = f"Rate limit exceeded: {limit} calls per {limit_type}."
        hint = "Wait before making more requests"
        if wait_seconds:
            hint += f" (approximately {wait_seconds:.0f} seconds)"

        super().__init__(
            message=message,
            recovery_hint=hint,
            context={
                "limit_type": limit_type,
                "limit": limit,
                "wait_seconds": wait_seconds,
            },
        )


class ErrorEnhancementMiddleware(Middleware):
    """Middleware that enhances errors with LLM-friendly messages."""

    def __init__(self, include_stack_traces: bool = False) -> None:
        """Initialize error enhancement middleware.

        Args:
            include_stack_traces: Include stack traces in errors (for debugging)
        """
        self.include_stack_traces = include_stack_traces

    def _enhance_error(self, error: Exception, tool_name: str) -> Exception:
        """Convert generic errors to LLM-friendly errors.

        Args:
            error: Original error
            tool_name: Name of the tool that failed

        Returns:
            Enhanced error
        """
        if isinstance(error, LLMFriendlyError):
            return error

        error_str = str(error).lower()

        if "database" in error_str or "sql" in error_str or "connection" in error_str:
            return DatabaseError(
                operation=tool_name,
                original_error=str(error),
            )

        if "not found" in error_str:
            import re

            id_match = re.search(r"'([^']+)'", str(error))
            item_id = id_match.group(1) if id_match else "unknown"
            return ItemNotFoundError(item_id)

        if "permission" in error_str or "forbidden" in error_str:
            return LLMFriendlyError(
                message="Permission denied for this operation.",
                recovery_hint="Check your access permissions and token scopes.",
            )

        return LLMFriendlyError(
            message=f"Tool '{tool_name}' failed: {error}",
            recovery_hint="Check tool arguments and try again. Use tool documentation for guidance.",
            context={"tool": tool_name, "error_type": type(error).__name__},
        )

    async def on_tool_call(
        self,
        ctx: MiddlewareContext,
        tool_name: str,
        _arguments: dict[str, object],
    ) -> None:
        """Enhance errors from tool calls.

        Args:
            ctx: Middleware context
            tool_name: Name of the tool
            arguments: Tool arguments
        """
        try:
            next_fn = getattr(ctx, "next", None)
            if next_fn is not None and callable(next_fn):
                await next_fn()
        except Exception as e:
            enhanced = self._enhance_error(e, tool_name)

            if isinstance(enhanced, LLMFriendlyError):
                error_dict = enhanced.to_dict()
                logger.exception("[ERROR_HANDLER] %s: %s", tool_name, error_dict)

                msg = (
                    f"{enhanced.message}\n\n"
                    f"Recovery hint: {enhanced.recovery_hint or 'None'}\n"
                    f"Context: {enhanced.context}"
                )
                raise ToolError(
                    msg,
                ) from e

            raise


def create_error_response(error: Exception) -> dict[str, object]:
    """Create a standardized error response.

    Args:
        error: Exception to convert

    Returns:
        Error response dictionary
    """
    if isinstance(error, LLMFriendlyError):
        return error.to_dict()

    return {
        "error": str(error),
        "type": type(error).__name__,
    }


__all__ = [
    "AuthorizationError",
    "DatabaseError",
    "ErrorEnhancementMiddleware",
    "InvalidLinkError",
    "ItemNotFoundError",
    "LLMFriendlyError",
    "ProjectNotFoundError",
    "ProjectNotSelectedError",
    "RateLimitError",
    "ValidationError",
    "create_error_response",
]
