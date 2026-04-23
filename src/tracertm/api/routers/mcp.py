"""MCP HTTP router for TraceRTM.

Provides HTTP endpoints for MCP (Model Context Protocol) communication:
- POST /api/v1/mcp/messages - JSON-RPC 2.0 endpoint for MCP messages
- GET /api/v1/mcp/sse - Server-Sent Events endpoint for streaming responses
- GET /api/v1/mcp/tools - Tool discovery endpoint
- OPTIONS /api/v1/mcp/messages - CORS preflight support

All endpoints use FastAPI's auth_guard for authentication, so MCP auth is disabled
when using HTTP transport (auth is handled at the FastAPI layer).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import TYPE_CHECKING, Annotated, Any, cast

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from mcp.server.fastmcp import FastMCP

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from tracertm.api.deps import auth_guard
from tracertm.core.context import current_account_id, current_user_id
from tracertm.mcp.core import get_mcp

logger = logging.getLogger(__name__)


def _mcp() -> object:
    """Lazy MCP server for HTTP (no env required for API startup)."""
    return get_mcp("http")


# =============================================================================
# Router Setup
# =============================================================================


router = APIRouter(prefix="/mcp", tags=["MCP"])


# =============================================================================
# Request/Response Models
# =============================================================================


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request."""

    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name")
    params: dict[str, Any] | None = Field(None, description="Method parameters")
    id: str | int | None = Field(None, description="Request ID")


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response."""

    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    result: object | None = None
    error: dict[str, Any] | None = None
    id: str | int | None = None


class ToolInfo(BaseModel):
    """Information about an available MCP tool."""

    name: str
    description: str | None = None
    input_schema: dict[str, Any] | None = Field(None, alias="inputSchema")


class ToolsListResponse(BaseModel):
    """Response for tools list endpoint."""

    tools: list[ToolInfo]


# =============================================================================
# Helper Functions
# =============================================================================


def _set_user_context(claims: dict[str, Any]) -> None:
    """Set user context variables from auth claims.

    Args:
        claims: Auth claims dict from auth_guard
    """
    # Extract user ID from claims (sub is the standard claim)
    user_id = claims.get("sub")
    if user_id:
        current_user_id.set(user_id)
        logger.debug("Set user context: %s", user_id)

    # Extract account ID if present (WorkOS specific)
    account_id = claims.get("org_id") or claims.get("account_id")
    if account_id:
        current_account_id.set(account_id)
        logger.debug("Set account context: %s", account_id)


async def _handle_mcp_call(method: str, params: dict[str, Any] | None, claims: dict[str, Any]) -> object:
    """Handle an MCP method call.

    Args:
        method: MCP method name (e.g., "tools/list", "tools/call")
        params: Method parameters
        claims: Auth claims from auth_guard

    Returns:
        Method result

    Raises:
        HTTPException: If method is invalid or execution fails
    """
    # Set user context for this request
    _set_user_context(claims)

    try:
        # Route to appropriate MCP handler
        if method == "tools/list":
            return await _list_tools()
        if method == "tools/call":
            return await _call_tool(params or {})
        if method == "resources/list":
            return await _list_resources()
        if method == "resources/read":
            return await _read_resource(params or {})
        if method == "prompts/list":
            return await _list_prompts()
        if method == "prompts/get":
            return await _get_prompt(params or {})
        raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error handling MCP call %s", method)
        raise HTTPException(status_code=500, detail=f"Internal error: {e!s}") from e


async def _list_tools() -> dict[str, Any]:
    """List available MCP tools.

    Returns:
        Dict with tools list
    """
    # Get tools from MCP server
    tools_list = await cast("FastMCP", _mcp()).list_tools()

    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters.model_json_schema()
                if hasattr(tool.parameters, "model_json_schema")
                else {},
            }
            for tool in tools_list
        ],
    }


async def _call_tool(params: dict[str, Any]) -> dict[str, Any]:
    """Call an MCP tool.

    Args:
        params: Tool call parameters (name, arguments)

    Returns:
        Tool execution result

    Raises:
        HTTPException: If tool not found or execution fails
    """
    tool_name = params.get("name")
    if not tool_name:
        raise HTTPException(status_code=400, detail="Tool name required")

    arguments = params.get("arguments", {})

    # Execute tool through MCP server
    try:
        result = await cast("FastMCP", _mcp()).call_tool(tool_name, arguments)
    except Exception as e:
        logger.exception("Error calling tool %s", tool_name)
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {e!s}") from e
    else:
        return {"content": result}


async def _list_resources() -> dict[str, Any]:
    """List available MCP resources.

    Returns:
        Dict with resources list
    """
    resources_list = await cast("FastMCP", _mcp()).list_resources()

    return {
        "resources": [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mimeType,
            }
            for resource in resources_list
        ],
    }


async def _read_resource(params: dict[str, Any]) -> dict[str, Any]:
    """Read an MCP resource.

    Args:
        params: Resource read parameters (uri)

    Returns:
        Resource content

    Raises:
        HTTPException: If resource not found
    """
    uri = params.get("uri")
    if not uri:
        raise HTTPException(status_code=400, detail="Resource URI required")

    try:
        result = await cast("FastMCP", _mcp()).read_resource(uri)
    except Exception as e:
        logger.exception("Error reading resource %s", uri)
        raise HTTPException(status_code=404, detail=f"Resource not found: {e!s}") from e
    else:
        return {"contents": result}


async def _list_prompts() -> dict[str, Any]:
    """List available MCP prompts.

    Returns:
        Dict with prompts list
    """
    prompts_list = await cast("FastMCP", _mcp()).list_prompts()

    return {
        "prompts": [
            {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": prompt.arguments,
            }
            for prompt in prompts_list
        ],
    }


async def _get_prompt(params: dict[str, Any]) -> dict[str, Any]:
    """Get an MCP prompt.

    Args:
        params: Prompt get parameters (name, arguments)

    Returns:
        Prompt content

    Raises:
        HTTPException: If prompt not found
    """
    name = params.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Prompt name required")

    arguments = params.get("arguments", {})

    try:
        result = await cast("FastMCP", _mcp()).get_prompt(name, arguments)
    except Exception as e:
        logger.exception("Error getting prompt %s", name)
        raise HTTPException(status_code=404, detail=f"Prompt not found: {e!s}") from e
    else:
        return {"messages": result}


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/config")
async def mcp_config() -> dict[str, Any]:
    """Return MCP configuration for frontend clients."""
    base_url = (
        os.getenv("TRACERTM_MCP_BASE_URL")
        or os.getenv("MCP_BASE_URL")
        or os.getenv("FASTMCP_SERVER_BASE_URL")
    )
    auth_mode = (os.getenv("TRACERTM_MCP_AUTH_MODE") or "oauth").lower().strip()
    return {
        "mcp_base_url": base_url,
        "auth_mode": auth_mode,
        "requires_auth": auth_mode not in {"disabled", "none", "off"},
    }


@router.options("/messages")
async def mcp_messages_options() -> Response:
    """Handle CORS preflight for MCP messages endpoint.

    Returns:
        Response with CORS headers
    """
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        },
    )


@router.post("/messages", response_model=JSONRPCResponse)
async def mcp_messages(
    request: JSONRPCRequest,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> JSONRPCResponse:
    """Handle JSON-RPC 2.0 MCP messages.

    This endpoint processes MCP protocol messages using JSON-RPC 2.0 format.
    Authentication is handled by FastAPI's auth_guard, and user context is
    automatically set for all tool executions.

    Args:
        request: JSON-RPC request
        claims: Auth claims from auth_guard

    Returns:
        JSON-RPC response
    """
    logger.debug("MCP message: %s", request.method)

    try:
        result = await _handle_mcp_call(request.method, request.params, claims)

        return JSONRPCResponse(
            jsonrpc="2.0",
            result=result,
            error=None,
            id=request.id,
        )
    except HTTPException as e:
        return JSONRPCResponse(
            jsonrpc="2.0",
            result=None,
            error={
                "code": e.status_code,
                "message": e.detail,
            },
            id=request.id,
        )
    except Exception as e:
        logger.exception("Unexpected error in MCP message handler")
        return JSONRPCResponse(
            jsonrpc="2.0",
            result=None,
            error={
                "code": 500,
                "message": f"Internal server error: {e!s}",
            },
            id=request.id,
        )


@router.get("/sse")
async def mcp_sse(
    request: Request,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> EventSourceResponse:
    """Server-Sent Events endpoint for streaming MCP responses.

    This endpoint provides real-time streaming of MCP events using SSE.
    Useful for long-running operations or real-time updates.

    Supports both generic SSE connections and task-specific progress streaming
    via the ?task_id= query parameter.

    Args:
        request: FastAPI request object (for query params)
        claims: Auth claims from auth_guard

    Returns:
        SSE stream
    """
    _set_user_context(claims)

    # Get optional task_id for task-specific streaming
    task_id = request.query_params.get("task_id")

    async def event_generator() -> AsyncGenerator[dict[str, Any], None]:
        """Generate SSE events."""
        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "status": "connected",
                    "user_id": current_user_id.get(),
                    "task_id": task_id,
                }),
            }

            if task_id:
                # Task-specific streaming
                # In a production system, you'd look up the task and stream its progress
                # For now, send a placeholder message
                yield {
                    "event": "info",
                    "data": json.dumps({
                        "message": f"Streaming progress for task: {task_id}",
                    }),
                }

            # Keep connection alive with heartbeat
            while True:
                await asyncio.sleep(30)
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({
                        "status": "alive",
                        "timestamp": asyncio.get_event_loop().time(),
                    }),
                }
        except asyncio.CancelledError:
            logger.debug("SSE connection cancelled (task_id: %s)", task_id)
        except Exception as e:
            logger.exception("Error in SSE generator (task_id: %s)", task_id)
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())


@router.get("/tools", response_model=ToolsListResponse)
async def mcp_tools(
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> ToolsListResponse:
    """List available MCP tools.

    This endpoint provides a simple way to discover available MCP tools
    without using JSON-RPC protocol.

    Args:
        claims: Auth claims from auth_guard

    Returns:
        List of available tools
    """
    _set_user_context(claims)

    tools_data = await _list_tools()

    return ToolsListResponse(tools=[ToolInfo(**tool) for tool in cast("list[dict[str, Any]]", tools_data["tools"])])


# =============================================================================
# Health Check
# =============================================================================


@router.get("/health")
async def mcp_health() -> dict[str, Any]:
    """MCP router health check.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "mcp",
        "transport": "http",
    }
