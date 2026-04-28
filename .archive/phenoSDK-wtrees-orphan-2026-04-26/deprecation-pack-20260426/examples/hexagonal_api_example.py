#!/usr/bin/env python3
"""Example demonstrating the hexagonal architecture REST API adapter.

This example shows how to run the FastAPI server with the hexagonal architecture.

To run:
    python examples/hexagonal_api_example.py

Then visit:
    - http://localhost:8000/docs - Interactive API documentation
    - http://localhost:8000/redoc - ReDoc documentation
    - http://localhost:8000/health - Health check
"""

import uvicorn

from pheno.adapters.api.app import create_app
from pheno.adapters.container_config import configure_in_memory_container, set_container


def main():
    """
    Run the FastAPI server.
    """
    print("=" * 60)
    print("Hexagonal Architecture REST API Example")
    print("=" * 60)
    print()
    print("Configuring dependency injection container...")

    # Configure container with in-memory implementations
    container = configure_in_memory_container()
    set_container(container)

    print("✓ Container configured")
    print()
    print("Creating FastAPI application...")

    # Create FastAPI app
    app = create_app(
        title="Pheno SDK API",
        version="2.0.0",
        description="REST API for Pheno SDK with Hexagonal Architecture",
        enable_cors=True,
    )

    print("✓ Application created")
    print()
    print("=" * 60)
    print("Starting server...")
    print("=" * 60)
    print()
    print("API Documentation:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("  - OpenAPI:    http://localhost:8000/openapi.json")
    print()
    print("Endpoints:")
    print("  - Health:     http://localhost:8000/health")
    print("  - Users:      http://localhost:8000/api/v1/users")
    print("  - Deployments: http://localhost:8000/api/v1/deployments")
    print("  - Services:   http://localhost:8000/api/v1/services")
    print("  - Config:     http://localhost:8000/api/v1/config")
    print()
    print("=" * 60)
    print()

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
