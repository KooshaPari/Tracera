"""FastAPI application for Pheno SDK REST API.

This module creates and configures the FastAPI application following hexagonal
architecture principles.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from pheno.adapters.api.routes import (
    configurations_router,
    deployments_router,
    services_router,
    users_router,
)


def create_app(
    title: str = "Pheno SDK API",
    version: str = "1.0.0",
    description: str = "REST API for Pheno SDK following hexagonal architecture",
    enable_cors: bool = True,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        title: API title
        version: API version
        description: API description
        enable_cors: Whether to enable CORS

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        default_response_class=ORJSONResponse,
    )

    # Configure CORS
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register routers
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(deployments_router, prefix="/api/v1")
    app.include_router(services_router, prefix="/api/v1")
    app.include_router(configurations_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        """
        return {"status": "healthy", "version": version}

    # Root endpoint
    @app.get("/")
    async def root():
        """
        Root endpoint with API information.
        """
        return {
            "name": title,
            "version": version,
            "description": description,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
