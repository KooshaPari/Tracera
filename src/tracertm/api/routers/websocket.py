"""WebSocket router for real-time updates.

Extracted from main.py as part of Phase 4.1 decomposition.
"""

from fastapi import APIRouter, WebSocket

from tracertm.api.deps import verify_token
from tracertm.api.handlers.websocket import websocket_endpoint

# Create router (no prefix needed for WebSocket root endpoint)
router: APIRouter = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time updates.

    Supports two authentication flows:
    1. Token in query parameter (?token=...) or Authorization header
    2. Accept connection first, then validate token from first message:
       { "type": "auth", "token": "..." }

    Message types:
    - ping: Returns pong
    - subscribe: Subscribe to a channel
    - unsubscribe: Unsubscribe from a channel

    Args:
        websocket: WebSocket connection
    """
    await websocket_endpoint(websocket, verify_token)
