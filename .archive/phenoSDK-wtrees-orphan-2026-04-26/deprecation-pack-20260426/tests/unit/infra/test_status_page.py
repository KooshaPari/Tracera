#!/usr/bin/env python3
"""Test & Demo Script for Status Page System.

Run this to see the status page system in action:
    python test_status_page.py

Then visit:
    - http://localhost:8080/invalid-route  (HTML 404 with suggestions)
    - http://localhost:8080/api/invalid    (JSON 404)
    - http://localhost:8080/__status__     (Status page)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from aiohttp import web

    from pheno.infra.status_page import StatusPageGenerator
    from pheno.infra.wildcard_handler import create_wildcard_handler
except ImportError as e:
    print(f"Error: {e}")
    print("Install dependencies: pip install aiohttp")
    sys.exit(1)


async def create_demo_app():
    """
    Create demo application with status pages.
    """
    app = web.Application()

    # Sample routes
    async def home(request):
        return web.Response(text="Welcome to Demo API!")

    async def get_users(request):
        return web.json_response({"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]})

    async def create_user(request):
        data = await request.json()
        return web.json_response({"created": data}, status=201)

    async def get_user(request):
        user_id = request.match_info["id"]
        return web.json_response({"id": user_id, "name": f"User {user_id}"})

    async def health(request):
        return web.json_response(
            {
                "status": "healthy",
                "checks": {
                    "database": {"status": "healthy", "latency_ms": 5},
                    "cache": {"status": "healthy", "latency_ms": 2},
                    "api": {"status": "healthy"},
                },
            },
        )

    async def metrics(request):
        return web.json_response(
            {
                "requests_per_minute": 1250,
                "avg_response_time_ms": 45,
                "active_connections": 23,
                "cpu_usage_percent": 35,
                "memory_usage_mb": 512,
            },
        )

    # Register routes
    app.router.add_get("/", home)
    app.router.add_get("/api/users", get_users)
    app.router.add_post("/api/users", create_user)
    app.router.add_get("/api/users/{id}", get_user)
    app.router.add_get("/health", health)
    app.router.add_get("/metrics", metrics)

    # Define routes for status page
    routes = [
        {"path": "/", "method": "GET", "description": "Home page - Welcome message"},
        {
            "path": "/api/users",
            "method": "GET",
            "description": "List all users with pagination support",
        },
        {"path": "/api/users", "method": "POST", "description": "Create a new user account"},
        {"path": "/api/users/{id}", "method": "GET", "description": "Get user details by ID"},
        {"path": "/health", "method": "GET", "description": "Health check endpoint for monitoring"},
        {"path": "/metrics", "method": "GET", "description": "Service metrics and statistics"},
    ]

    # Create wildcard handler with full configuration
    wildcard = create_wildcard_handler(
        service_name="Demo API",
        domain="localhost:8080",
        routes=routes,
        version="2.1.0",
        description="RESTful API demonstration with status pages",
        health_status={
            "status": "healthy",
            "checks": {
                "database": {"status": "healthy", "message": "PostgreSQL connected"},
                "cache": {"status": "healthy", "message": "Redis online"},
                "storage": {"status": "healthy", "message": "S3 accessible"},
            },
        },
        environment="development",
        uptime="5h 23m",
        metrics={
            "requests_per_minute": 1250,
            "avg_response_time_ms": 45,
            "active_connections": 23,
            "cpu_usage_percent": 35,
            "memory_usage_mb": 512,
        },
        docs_url="https://docs.example.com",
        support_url="https://support.example.com",
        enable_suggestions=True,
    )

    # Add dedicated status page endpoint
    async def status_page(request):
        html = wildcard.status_generator.generate_html(
            routes=routes,
            health_status=wildcard.health_status,
            environment=wildcard.environment,
            uptime=wildcard.uptime,
            metrics=wildcard.metrics,
        )
        return web.Response(text=html, content_type="text/html")

    async def status_json(request):
        data = wildcard.status_generator.generate_json(
            routes=routes,
            health_status=wildcard.health_status,
            environment=wildcard.environment,
            uptime=wildcard.uptime,
            metrics=wildcard.metrics,
        )
        return web.json_response(data)

    app.router.add_get("/__status__", status_page)
    app.router.add_get("/__status__.json", status_json)

    # Background task to update status
    async def update_status():
        """
        Simulate status updates.
        """
        await asyncio.sleep(2)  # Wait for server to start

        count = 0
        while True:
            count += 1

            # Simulate changing health
            if count % 3 == 0:
                # Occasionally show degraded status
                wildcard.update_health_status(
                    {
                        "status": "degraded",
                        "checks": {
                            "database": {"status": "healthy", "message": "Connected"},
                            "cache": {"status": "unhealthy", "message": "High latency"},
                            "storage": {"status": "healthy", "message": "S3 OK"},
                        },
                    },
                )
            else:
                wildcard.update_health_status(
                    {
                        "status": "healthy",
                        "checks": {
                            "database": {"status": "healthy", "message": "Connected"},
                            "cache": {"status": "healthy", "message": "Redis online"},
                            "storage": {"status": "healthy", "message": "S3 accessible"},
                        },
                    },
                )

            # Update metrics
            import random

            wildcard.update_metrics(
                {
                    "requests_per_minute": random.randint(1000, 1500),
                    "avg_response_time_ms": random.randint(30, 60),
                    "active_connections": random.randint(15, 30),
                    "cpu_usage_percent": random.randint(20, 50),
                    "memory_usage_mb": random.randint(480, 600),
                },
            )

            # Update uptime
            hours = count * 10 // 3600
            minutes = (count * 10 % 3600) // 60
            wildcard.update_uptime(f"{hours}h {minutes}m")

            await asyncio.sleep(10)

    # Start background task
    asyncio.create_task(update_status())

    # Add wildcard handler (MUST BE LAST!)
    app.router.add_route("*", "/{path:.*}", wildcard.handle_request)

    return app


def print_info():
    """
    Print startup information.
    """
    print("\n" + "=" * 70)
    print("🚀 Status Page Demo Server")
    print("=" * 70)
    print("\n📍 Available endpoints:")
    print("  • http://localhost:8080/              - Home page")
    print("  • http://localhost:8080/api/users     - User API")
    print("  • http://localhost:8080/health        - Health check")
    print("  • http://localhost:8080/metrics       - Metrics")
    print("  • http://localhost:8080/__status__    - Status page (HTML)")
    print("  • http://localhost:8080/__status__.json - Status page (JSON)")
    print("\n🔍 Test 404 handling:")
    print("  • http://localhost:8080/invalid-route  - HTML 404 with suggestions")
    print("  • http://localhost:8080/api/invalid    - JSON 404")
    print("  • http://localhost:8080/usr            - Suggests /api/users")
    print("\n💡 Try these commands:")
    print("  curl http://localhost:8080/invalid-route")
    print("  curl -H 'Accept: application/json' http://localhost:8080/invalid")
    print("  curl http://localhost:8080/__status__.json")
    print("\n🎨 Features:")
    print("  ✓ Beautiful gradient UI")
    print("  ✓ Smart route suggestions")
    print("  ✓ Real-time health updates (every 10s)")
    print("  ✓ Dynamic metrics")
    print("  ✓ Environment badges")
    print("  ✓ JSON/HTML content negotiation")
    print("\n" + "=" * 70)
    print("Server running on http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("=" * 70 + "\n")


async def main():
    """
    Run the demo server.
    """
    app = await create_demo_app()

    # Print startup info
    print_info()

    # Run the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)

    try:
        await site.start()
        # Keep running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
