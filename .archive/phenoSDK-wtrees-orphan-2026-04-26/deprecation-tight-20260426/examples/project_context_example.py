#!/usr/bin/env python3
"""
Project Context Example - Demonstrates Phase 2 project-scoped infrastructure management.

This example shows how to use the new ProjectInfraContext for managing
project-specific infrastructure with automatic cleanup, resource coordination,
and reverse proxy integration.
"""

import asyncio
import logging
import time
from pathlib import Path

# Add the src directory to the path so we can import pheno modules
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.infra.project_context import (
    ProjectInfraContext,
    project_infra_context,
    quick_project_setup,
)
from pheno.infra.deployment_manager import ResourceMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_project_context():
    """Example 1: Basic project context usage."""
    print("\n=== Example 1: Basic Project Context ===")

    with project_infra_context(
        project_name="demo-frontend",
        domain="kooshapari.com",
        enable_proxy=True,
    ) as ctx:
        # Allocate ports for different services
        api_port = ctx.allocate_port(
            service_name="api",
            preferred_port=8001,
            service_type="api",
            scope="tenant",
        )

        web_port = ctx.allocate_port(
            service_name="web",
            preferred_port=8002,
            service_type="web",
            scope="tenant",
        )

        # Start tunnels
        api_tunnel = ctx.start_tunnel("api", api_port)
        web_tunnel = ctx.start_tunnel("web", web_port)

        # Register proxy routes
        ctx.register_proxy_route("/api", api_port, service_name="api")
        ctx.register_proxy_route("/", web_port, service_name="web")

        print(f"API Service: Port {api_port}, URL: https://{api_tunnel.hostname}")
        print(f"Web Service: Port {web_port}, URL: https://{web_tunnel.hostname}")
        print(f"Proxy Server: http://localhost:9100")

        # Show environment variables
        env_vars = ctx.export_environment_variables()
        print("\nEnvironment Variables:")
        for key, value in env_vars.items():
            print(f"  {key}={value}")

        # Simulate some work
        print("\nSimulating work for 3 seconds...")
        time.sleep(3)

        # Show project services
        services = ctx.get_project_services()
        print(f"\nProject Services: {len(services)}")
        for name, info in services.items():
            print(f"  {name}: {info['service_type']} on port {info['port']}")


async def example_resource_coordination():
    """Example 2: Resource coordination with deployment manager."""
    print("\n=== Example 2: Resource Coordination ===")

    with project_infra_context(
        project_name="demo-backend",
        enable_proxy=False,  # No proxy for this example
    ) as ctx:
        # Deploy a Redis resource for the project
        redis_config = {
            "type": "docker",
            "image": "redis:7-alpine",
            "ports": {6379: 6379},
            "environment": {"REDIS_PASSWORD": "demo123"},
        }

        success = await ctx.deploy_resource(
            name="redis",
            config=redis_config,
            mode=ResourceMode.TENANTED,
            metadata={"description": "Project Redis cache"},
        )

        if success:
            print("✓ Redis resource deployed for project")

            # Start the resource
            started = await ctx.start_resource("redis")
            if started:
                print("✓ Redis resource started")
            else:
                print("✗ Failed to start Redis resource")
        else:
            print("✗ Failed to deploy Redis resource")


def example_quick_project_setup():
    """Example 3: Quick project setup with multiple services."""
    print("\n=== Example 3: Quick Project Setup ===")

    # Define services for a full-stack application
    services_config = {
        "frontend": {
            "preferred_port": 3000,
            "service_type": "web",
            "scope": "tenant",
            "proxy_path": "/",
        },
        "api": {
            "preferred_port": 8000,
            "service_type": "api",
            "scope": "tenant",
            "proxy_path": "/api",
        },
        "admin": {
            "preferred_port": 8001,
            "service_type": "admin",
            "scope": "tenant",
            "proxy_path": "/admin",
        },
        "websocket": {
            "preferred_port": 8002,
            "service_type": "websocket",
            "scope": "tenant",
            "proxy_path": "/ws",
        },
    }

    # Quick setup
    results = quick_project_setup(
        project_name="fullstack-app",
        services=services_config,
        domain="kooshapari.com",
        enable_proxy=True,
    )

    print("Quick Project Setup Results:")
    for service_name, result in results.items():
        if "error" in result:
            print(f"  {service_name}: ERROR - {result['error']}")
        else:
            print(f"  {service_name}: Port {result['port']}, URL: {result['url']}")


def example_multi_project_isolation():
    """Example 4: Multi-project isolation."""
    print("\n=== Example 4: Multi-Project Isolation ===")

    # Project A
    with project_infra_context(project_name="project-a") as ctx_a:
        port_a = ctx_a.allocate_port("service", preferred_port=9000)
        print(f"Project A - Service port: {port_a}")

        # Project B (should get different port even if same preferred)
        with project_infra_context(project_name="project-b") as ctx_b:
            port_b = ctx_b.allocate_port("service", preferred_port=9000)
            print(f"Project B - Service port: {port_b}")

            # Show that projects are isolated
            services_a = ctx_a.get_project_services()
            services_b = ctx_b.get_project_services()

            print(f"Project A services: {len(services_a)}")
            print(f"Project B services: {len(services_b)}")

            # Both projects can use the same preferred port because they're isolated
            print(f"Ports are isolated: {port_a != port_b or 'Same port (unexpected)'}")


def example_environment_variables():
    """Example 5: Environment variable management."""
    print("\n=== Example 5: Environment Variables ===")

    with project_infra_context(
        project_name="env-demo",
        enable_proxy=True,
    ) as ctx:
        # Allocate some services
        ctx.allocate_port("api", service_type="api")
        ctx.allocate_port("web", service_type="web")

        # Export environment variables
        env_vars = ctx.export_environment_variables()

        print("Project Environment Variables:")
        for key, value in sorted(env_vars.items()):
            print(f"  {key}={value}")

        # Set them in the current process
        ctx.set_environment_variables()

        # Verify they're set
        import os

        print(f"\nKINFRA_PROJECT: {os.environ.get('KINFRA_PROJECT')}")
        print(f"KINFRA_DOMAIN: {os.environ.get('KINFRA_DOMAIN')}")
        print(f"KINFRA_PROXY_PORT: {os.environ.get('KINFRA_PROXY_PORT')}")


async def main():
    """Run all examples."""
    print("Project Context Examples - Phase 2 Implementation")
    print("=" * 50)

    try:
        # Run synchronous examples
        example_basic_project_context()
        example_quick_project_setup()
        example_multi_project_isolation()
        example_environment_variables()

        # Run async examples
        await example_resource_coordination()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
