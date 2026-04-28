"""
Phase 4: Reverse Proxy & Fallback Experience - Comprehensive Example

Demonstrates enhanced reverse proxy and fallback features:
- Project routing templates with domain + base path mapping
- Fallback configuration API/CLI
- Health monitoring with project metadata
- Sample compose files for shared proxy + multiple services
"""

import asyncio
import json
import logging
import time
from pathlib import Path

from pheno.infra.proxy_gateway.project_routing import ProjectRoutingManager, ProjectRoute
from pheno.infra.fallback_site.config_manager import FallbackConfigManager
from pheno.infra.proxy_gateway.health_dashboard import HealthDashboard
from pheno.infra.project_context import project_infra_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_project_routing():
    """Demonstrate project routing templates."""
    print("\n=== Project Routing Templates ===")

    routing_manager = ProjectRoutingManager()

    # Create default routing config for a project
    config = routing_manager.create_default_config(
        project_name="api-project",
        domain="api.example.com",
        base_path="/api/v1",
        services=[
            {"name": "users", "port": 8001, "health_check_path": "/health"},
            {"name": "orders", "port": 8002, "health_check_path": "/health"},
            {"name": "payments", "port": 8003, "health_check_path": "/health"},
        ],
    )

    print(f"Created routing config for project '{config.project_name}'")
    print(f"  Domain: {config.domain}")
    print(f"  Base path: {config.base_path}")
    print(f"  Routes: {len(config.routes)}")

    # Add additional routes
    routing_manager.add_route(
        project_name="api-project",
        service_name="analytics",
        port=8004,
        path_prefix="/api/v1/analytics",
        health_check_path="/health",
    )

    # Add routes for another project
    routing_manager.add_route(
        project_name="web-project",
        service_name="frontend",
        port=8005,
        path_prefix="/",
        domain="web.example.com",
        health_check_path="/health",
    )

    # Find routes by path
    api_route = routing_manager.get_route_by_path("/api/v1/users")
    if api_route:
        print(f"Found route for '/api/v1/users': {api_route.service_name} on port {api_route.port}")

    # Export configuration
    config_json = routing_manager.export_config("api-project", "json")
    print(f"Exported config: {len(config_json)} characters")

    # List all routes
    all_routes = routing_manager.get_all_routes()
    print(f"Total active routes: {len(all_routes)}")


async def demonstrate_fallback_configuration():
    """Demonstrate fallback configuration API/CLI."""
    print("\n=== Fallback Configuration ===")

    config_manager = FallbackConfigManager()

    # Create project configuration
    project_config = config_manager.create_project_config("demo-project")
    print(f"Created fallback config for project '{project_config.project_name}'")

    # Update fallback pages
    from pheno.infra.fallback_site.config_manager import FallbackPageConfig

    loading_page = FallbackPageConfig(
        page_type="loading",
        service_name="demo-project",
        title="Demo Project - Starting Up",
        message="Demo project is currently starting up...",
        refresh_interval=3,
        custom_css="body { background: linear-gradient(45deg, #667eea, #764ba2); }",
    )

    config_manager.update_fallback_page("demo-project", "loading", loading_page)

    error_page = FallbackPageConfig(
        page_type="error",
        service_name="demo-project",
        title="Demo Project - Service Unavailable",
        message="Demo project is temporarily unavailable. Please try again later.",
        refresh_interval=10,
        template_vars={"contact_email": "support@example.com"},
    )

    config_manager.update_fallback_page("demo-project", "error", error_page)

    # Enable maintenance mode
    config_manager.enable_maintenance(
        project_name="demo-project",
        message="Demo project is under maintenance",
        estimated_duration="1 hour",
        contact_info="support@example.com",
    )

    print("Updated fallback pages and enabled maintenance mode")

    # Set custom template
    custom_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{service_name}} - {{title}}</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; }
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 20px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="spinner"></div>
            <h1>{{service_name}}</h1>
            <p>{{message}}</p>
        </div>
    </body>
    </html>
    """

    config_manager.set_custom_template("demo-project", "loading", custom_template)
    print("Set custom template for loading page")

    # Export configuration
    config_json = config_manager.export_project_config("demo-project", "json")
    print(f"Exported fallback config: {len(config_json)} characters")

    # List project pages
    pages = config_manager.list_project_pages("demo-project")
    print(f"Available pages: {', '.join(pages)}")


async def demonstrate_health_monitoring():
    """Demonstrate health monitoring with project metadata."""
    print("\n=== Health Monitoring ===")

    health_dashboard = HealthDashboard()
    await health_dashboard.initialize()

    # Register health checkers
    async def api_health_check():
        # Simulate health check
        await asyncio.sleep(0.1)
        return True

    async def web_health_check():
        # Simulate health check
        await asyncio.sleep(0.1)
        return False  # Simulate unhealthy service

    health_dashboard.register_health_checker("api-service", api_health_check)
    health_dashboard.register_health_checker("web-service", web_health_check)

    # Update service health
    health_dashboard.update_service_health(
        project_name="api-project",
        service_name="api-service",
        status="healthy",
        port=8001,
        metadata={"version": "1.0.0", "environment": "production"},
        dependencies=["redis", "postgres"],
    )

    health_dashboard.update_service_health(
        project_name="web-project",
        service_name="web-service",
        status="unhealthy",
        port=8002,
        error_message="Connection timeout",
        metadata={"version": "2.0.0", "environment": "staging"},
        dependencies=["api-service"],
    )

    # Set maintenance mode
    health_dashboard.set_maintenance_mode("api-project", True)

    # Get project health
    api_health = health_dashboard.get_project_health("api-project")
    if api_health:
        print(f"API Project Status: {api_health.overall_status}")
        print(f"  Services: {len(api_health.services)}")
        print(f"  Maintenance Mode: {api_health.maintenance_mode}")

    web_health = health_dashboard.get_project_health("web-project")
    if web_health:
        print(f"Web Project Status: {web_health.overall_status}")
        print(f"  Services: {len(web_health.services)}")
        print(f"  Maintenance Mode: {web_health.maintenance_mode}")

    # Get dashboard data
    dashboard_data = health_dashboard.get_dashboard_data()
    print(f"Dashboard data: {len(dashboard_data.get('projects', []))} projects")

    # Export health data
    health_json = health_dashboard.export_health_data(format="json")
    print(f"Exported health data: {len(health_json)} characters")

    await health_dashboard.shutdown()


async def demonstrate_project_integration():
    """Demonstrate integration with ProjectInfraContext."""
    print("\n=== Project Integration ===")

    with project_infra_context("demo-project") as ctx:
        # Set up project routing
        routing_manager = ProjectRoutingManager()
        routing_config = routing_manager.create_default_config(
            project_name="demo-project",
            domain="demo.example.com",
            base_path="/demo",
            services=[
                {"name": "api", "port": 8001},
                {"name": "web", "port": 8002},
            ],
        )

        # Set up fallback configuration
        config_manager = FallbackConfigManager()
        fallback_config = config_manager.create_project_config("demo-project")

        # Deploy resources with project context
        await ctx.deploy_resource(
            name="api-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8001: 80},
                "environment": {"SERVICE_NAME": "api-service"},
            },
            metadata={"project": "demo-project", "service": "api"},
        )

        await ctx.deploy_resource(
            name="web-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8002: 80},
                "environment": {"SERVICE_NAME": "web-service"},
            },
            metadata={"project": "demo-project", "service": "web"},
        )

        # Get project resources
        resources = await ctx.get_project_resources()
        print(f"Deployed {len(resources)} resources for demo-project")

        for resource in resources:
            print(f"  {resource['name']}: {resource['mode']} - {resource['health']}")


async def demonstrate_compose_integration():
    """Demonstrate Docker Compose integration."""
    print("\n=== Docker Compose Integration ===")

    # Read the sample compose file
    compose_file = Path(__file__).parent / "docker-compose-shared-proxy.yml"
    if compose_file.exists():
        compose_content = compose_file.read_text()
        print(f"Sample compose file: {len(compose_content)} characters")

        # Parse and display services
        import yaml

        compose_data = yaml.safe_load(compose_content)
        services = compose_data.get("services", {})

        print(f"Services defined: {len(services)}")
        for service_name, service_config in services.items():
            ports = service_config.get("ports", [])
            environment = service_config.get("environment", {})
            project_name = None
            for env_var in environment:
                if env_var.startswith("PROJECT_NAME="):
                    project_name = env_var.split("=", 1)[1]
                    break

            print(f"  {service_name}:")
            print(f"    Ports: {ports}")
            print(f"    Project: {project_name or 'N/A'}")

    # Read the nginx configuration
    nginx_file = Path(__file__).parent / "nginx.conf"
    if nginx_file.exists():
        nginx_content = nginx_file.read_text()
        print(f"Nginx configuration: {len(nginx_content)} characters")

        # Count location blocks
        location_count = nginx_content.count("location ")
        print(f"Location blocks: {location_count}")


async def main():
    """Run all Phase 4 demonstrations."""
    print("Phase 4: Reverse Proxy & Fallback Experience Demonstration")
    print("=" * 60)

    try:
        await demonstrate_project_routing()
        await demonstrate_fallback_configuration()
        await demonstrate_health_monitoring()
        await demonstrate_project_integration()
        await demonstrate_compose_integration()

        print("\n" + "=" * 60)
        print("Phase 4 demonstration completed successfully!")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"\n✗ Demonstration failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
