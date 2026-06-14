"""FastAPI entrypoint for Tracera REST APIs."""

from __future__ import annotations

from fastapi import FastAPI
from phenotype_request_id.fastapi import RequestIdMiddleware

from tracertm.api.routers.traceability import router as traceability_router


def create_app() -> FastAPI:
    """Create the Tracera API application."""
    app = FastAPI(title="Tracera API", version="0.2.0")
    # Request-ID middleware: read X-Request-Id from inbound request, or
    # generate a uuid4, store in the module-level ContextVar, and echo
    # the value on the response. See phenotype_request_id.fastapi.
    app.add_middleware(RequestIdMiddleware)
    app.include_router(traceability_router, prefix="/api/v1")
    return app


app = create_app()
