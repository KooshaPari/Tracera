"""FastAPI entrypoint for Tracera REST APIs."""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI
from tracertm.api.middleware.authz import ApiAuthzMiddleware
from tracertm.api.middleware.request_id import RequestIdMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from tracertm.api.observability import configure_api_logging, log_request_metrics
from tracertm.api.routers.auth import router as auth_router
from tracertm.api.routers.code_trace import router as code_trace_router
from tracertm.api.routers.comments import router as comments_router
from tracertm.api.routers.evidence import router as evidence_router
from tracertm.api.routers.impact import router as impact_router
from tracertm.api.routers.impact_scoring import router as impact_scoring_router
from tracertm.api.routers.ingest import router as ingest_router
from tracertm.api.routers.org_intel import router as org_intel_router
from tracertm.api.routers.sdlc_pm import router as sdlc_pm_router
from tracertm.api.routers.traceability import router as traceability_router


configure_api_logging()
logger = logging.getLogger("tracertm")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Attach request timing and correlation-aware access logs."""

    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        log_request_metrics(
            logger,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=elapsed_ms,
        )
        return response


def create_app() -> FastAPI:
    """Create the Tracera API application."""
    app = FastAPI(title="Tracera API", version="0.2.0")
    app.add_middleware(LoggingMiddleware)
    # Request-ID middleware: read X-Request-Id from inbound request, or
    # generate a uuid4, store in the module-level ContextVar, and echo
    # the value on the response. See phenotype_request_id.fastapi.
    app.add_middleware(RequestIdMiddleware)
    # API authn/authz enforcement.
    app.add_middleware(ApiAuthzMiddleware)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(code_trace_router, prefix="/api/v1")
    app.include_router(comments_router, prefix="/api/v1")
    app.include_router(traceability_router, prefix="/api/v1")
    app.include_router(sdlc_pm_router, prefix="/api/v1")
    app.include_router(evidence_router, prefix="/api/v1")
    app.include_router(org_intel_router, prefix="/api/v1")
    app.include_router(impact_router, prefix="/api/v1")
    app.include_router(impact_scoring_router, prefix="/api/v1")
    app.include_router(ingest_router, prefix="/api/v1")

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> dict[str, str]:
        """Liveness probe — process is up and serving HTTP.

        Excluded from OpenAPI schema (operational endpoint for orchestrators).
        """
        return {"status": "ok"}

    @app.get("/health", include_in_schema=True)
    async def health() -> dict[str, str]:
        """Public liveness alias for orchestrators and load balancers."""
        return {"status": "ok"}

    @app.get("/readyz", include_in_schema=False)
    async def readyz() -> dict[str, str]:
        """Readiness probe — minimal check; orchestrator-driven verification.

        Excluded from OpenAPI schema (operational endpoint for orchestrators).
        Returns version + liveness; deeper downstream checks are deferred to
        orchestrator-side probes per ADR-OPS-HEALTH-001.
        """
        return {"status": "ready", "version": app.version}

    @app.get("/ready", include_in_schema=True)
    async def ready() -> dict[str, str]:
        """Public readiness alias for orchestrators and uptime checks."""
        return {"status": "ready", "version": app.version}

    return app


app = create_app()
