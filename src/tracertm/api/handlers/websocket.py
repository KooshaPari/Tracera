"""WebSocket endpoint handler.

Extracted from main.py to reduce complexity (C901 violation).
Breaks down websocket_endpoint (complexity 29) into focused functions.
"""

import asyncio
import contextlib
import logging
from collections.abc import Callable
from json import JSONDecodeError

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


async def close_websocket_once(
    websocket: WebSocket,
    ws_closed_flag: dict[str, bool],
    code: int | None = None,
    reason: str = "",
) -> None:
    """Close WebSocket connection exactly once.

    Args:
        websocket: WebSocket connection
        ws_closed_flag: Dictionary with 'closed' boolean flag
        code: Optional close code
        reason: Close reason string
    """
    if ws_closed_flag.get("closed"):
        return
    ws_closed_flag["closed"] = True
    try:
        if code is not None:
            await websocket.close(code=code, reason=reason)
        else:
            await websocket.close()
    except (RuntimeError, WebSocketDisconnect) as exc:
        logger.debug("WebSocket close ignored for %s: %s", websocket.client, exc)


def extract_token_from_request(websocket: WebSocket) -> str | None:
    """Extract auth token from WebSocket query params or headers.

    Args:
        websocket: WebSocket connection

    Returns:
        Token string or None if not found
    """
    # Try query parameter first
    if "token" in websocket.query_params:
        return websocket.query_params["token"]

    # Try Authorization header (case-insensitive)
    auth_header = websocket.headers.get("Authorization") or websocket.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(None, 1)[1].strip()

    return None


async def receive_auth_message(websocket: WebSocket, timeout_seconds: float = 10.0) -> str | None:
    """Receive auth message from WebSocket client.

    Waits for first message with format: { "type": "auth", "token": "..." }

    Args:
        websocket: WebSocket connection
        timeout_seconds: Timeout in seconds

    Returns:
        Token string or None if auth failed

    Raises:
        TimeoutError: If no message received within timeout
        WebSocketDisconnect: If client disconnected
    """
    msg = await asyncio.wait_for(websocket.receive_json(), timeout=timeout_seconds)
    if isinstance(msg, dict) and msg.get("type") == "auth":
        token = (msg.get("token") or "").strip()
        return token or None
    return None


async def _log_disconnect_before_auth(websocket: WebSocket, exc: WebSocketDisconnect) -> None:
    code = getattr(exc, "code", None)
    if code in {1000, 1001}:
        logger.info("WebSocket client disconnected before auth from %s (code=%s)", websocket.client, code)
    else:
        logger.warning("WebSocket disconnected before auth from %s: %s", websocket.client, exc)


async def _receive_token_after_accept(
    websocket: WebSocket,
    ws_closed: dict[str, bool],
    timeout_seconds: float = 10.0,
) -> str | None:
    try:
        token = await receive_auth_message(websocket, timeout_seconds=timeout_seconds)
    except TimeoutError:
        logger.info("WebSocket auth timeout (no auth message) from %s", websocket.client)
        await close_websocket_once(websocket, ws_closed, 1008, "Authentication timeout")
        return None
    except WebSocketDisconnect as exc:
        await _log_disconnect_before_auth(websocket, exc)
        return None
    except (JSONDecodeError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning("WebSocket failed to receive auth message from %s: %s", websocket.client, exc)
        await close_websocket_once(websocket, ws_closed, 1008, "Invalid auth")
        return None

    if not token:
        await handle_auth_failure(websocket, ws_closed, "Missing auth message")
        return None
    return token


async def _verify_token_or_close(
    websocket: WebSocket,
    ws_closed: dict[str, bool],
    token: str,
    verify_token_func: Callable[[str], dict[str, object]],
) -> dict[str, object] | None:
    try:
        claims = verify_token_func(token)
        logger.info("WebSocket authenticated: user=%s from %s", claims.get("sub"), websocket.client)
    except (RuntimeError, TypeError, ValueError) as exc:
        logger.warning("WebSocket rejected: invalid token from %s: %s", websocket.client, exc)
        await handle_auth_failure(websocket, ws_closed, str(exc))
        return None
    else:
        return claims


async def handle_auth_failure(
    websocket: WebSocket,
    ws_closed: dict[str, bool],
    message: str,
    code: int = 1008,
) -> None:
    """Send auth failure message and close WebSocket.

    Args:
        websocket: WebSocket connection
        ws_closed: Dictionary with 'closed' boolean flag
        message: Error message
        code: WebSocket close code (default 1008 = policy violation)
    """
    with contextlib.suppress(WebSocketDisconnect):
        await websocket.send_json({"type": "auth_failed", "message": message})
    await close_websocket_once(websocket, ws_closed, code, message)


async def authenticate_websocket(
    websocket: WebSocket,
    verify_token_func: Callable[[str], dict[str, object]],
) -> dict[str, object] | None:
    """Authenticate WebSocket connection.

    Tries token from query/header first, then waits for auth message.

    Args:
        websocket: WebSocket connection
        verify_token_func: Function to verify tokens

    Returns:
        Claims dictionary if authenticated, None otherwise
    """
    ws_closed = {"closed": False}

    # Try token from query or header first
    token = extract_token_from_request(websocket)

    # Accept connection so we can receive messages
    await websocket.accept()

    # If no token yet, expect auth in first message
    if not token:
        token = await _receive_token_after_accept(websocket, ws_closed, timeout_seconds=10.0)
        if not token:
            return None

    # Verify token
    if not token:
        await handle_auth_failure(websocket, ws_closed, "No token provided")
        return None

    return await _verify_token_or_close(websocket, ws_closed, token, verify_token_func)


async def send_auth_success(websocket: WebSocket) -> bool:
    """Send auth success message to client.

    Args:
        websocket: WebSocket connection

    Returns:
        True if message sent successfully, False if client disconnected
    """
    try:
        await websocket.send_json({"type": "auth_success"})
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected before auth_success from %s", websocket.client)
        return False
    else:
        return True


async def handle_websocket_message(websocket: WebSocket, data: dict[str, object]) -> None:
    """Handle incoming WebSocket message.

    Args:
        websocket: WebSocket connection
        data: Message data dictionary
    """
    msg_type = data.get("type")

    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    elif msg_type == "subscribe":
        channel = data.get("channel", "*")
        await websocket.send_json({"type": "subscribed", "channel": channel})
    elif msg_type == "unsubscribe":
        channel = data.get("channel", "*")
        await websocket.send_json({"type": "unsubscribed", "channel": channel})
    else:
        await websocket.send_json({"type": "echo", "data": data})


async def websocket_message_loop(websocket: WebSocket) -> None:
    """Main WebSocket message receive/send loop.

    Args:
        websocket: WebSocket connection

    Raises:
        WebSocketDisconnect: When client disconnects
    """
    while True:
        try:
            data = await websocket.receive_json()
            await handle_websocket_message(websocket, data)
        except WebSocketDisconnect:
            raise
        except (JSONDecodeError, RuntimeError, TypeError, ValueError) as e:
            logger.exception("WebSocket error")
            await websocket.send_json({"type": "error", "message": str(e)})


async def websocket_endpoint(
    websocket: WebSocket,
    verify_token_func: Callable[[str], dict[str, object]],
) -> None:
    """WebSocket endpoint for real-time updates.

    Refactored to reduce complexity from 29 to ~5.

    Supports two auth flows:
    1. Token in query (?token=) or Authorization header
    2. Accept first, then validate token from first message { "type": "auth", "token": "..." }

    Args:
        websocket: WebSocket connection
        verify_token_func: Function to verify auth tokens
    """
    ws_closed = False

    try:
        # Authenticate connection
        claims = await authenticate_websocket(websocket, verify_token_func)
        if not claims:
            return

        # Send auth success
        if not await send_auth_success(websocket):
            return

        # Handle messages
        await websocket_message_loop(websocket)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except (RuntimeError, TypeError, ValueError, JSONDecodeError):
        logger.exception("WebSocket connection error")
    finally:
        if not ws_closed:
            with contextlib.suppress(RuntimeError, WebSocketDisconnect):
                await websocket.close()
