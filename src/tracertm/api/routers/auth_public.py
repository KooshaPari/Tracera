"""Public authentication API endpoints for TraceRTM.

The existing `auth.py` router already owns the authenticated `me` and `logout`
paths, so this router only carries the remaining public-only entry points.
"""

from fastapi import APIRouter

from tracertm.api.handlers.auth import (
    login_endpoint,
    signup_endpoint,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth-public"])

router.post("/signup")(signup_endpoint)
router.post("/login")(login_endpoint)
