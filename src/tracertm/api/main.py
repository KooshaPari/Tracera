"""FastAPI entrypoint for Tracera REST APIs."""

from __future__ import annotations

from fastapi import FastAPI

from tracertm.api.routers.traceability import router as traceability_router


def create_app() -> FastAPI:
    """Create the Tracera API application."""
    app = FastAPI(title="Tracera API", version="0.2.0")
    app.include_router(traceability_router, prefix="/api/v1")
    return app


app = create_app()
