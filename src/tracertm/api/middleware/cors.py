"""CORS middleware configuration for TraceRTM API.

This module configures Cross-Origin Resource Sharing (CORS) to allow:
- Gateway service (port 4000)
- Frontend development server (ports 3000, 5173)
- Local development origins only

External clients must use the gateway; no wildcard origins are allowed.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application.

    Args:
        app: FastAPI application instance

    Environment Variables:
        CORS_ORIGINS: Comma-separated list of allowed origins.
                     Defaults to localhost gateway + frontend dev servers.
    """
    # Parse CORS origins from environment (gateway + frontend only; no wildcards)
    # External clients must use the gateway; allow gateway (4000) + frontend origins
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:4000,http://127.0.0.1:4000,"
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:3000,http://127.0.0.1:3000"
        ),
    ).split(",")

    # Add CORS middleware with strict origin whitelist
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
