"""
Phase 5: Process & Tunnel Governance - Comprehensive Example

Demonstrates enhanced process and tunnel governance features:
- Process naming and cleanup using metadata
- Tunnel lifecycle management (reuse vs recreate)
- Configurable cleanup policies
- Enhanced fallback pages with service/tunnel status
"""

import asyncio
import json
import logging
import time
from pathlib import Path

from pheno.infra.process_governance import (
    ProcessGovernanceManager,
    ProcessMetadata,
    ProcessGovernanceConfig,
    CleanupPolicy,
)
from pheno.infra.tunnel_governance import (
    TunnelGovernanceManager,
    TunnelGovernanceConfig,
    TunnelLifecyclePolicy,
)
from pheno.infra.cleanup_policies import (
    CleanupPolicyManager,
    CleanupStrategy,
    ResourceType,
)
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.project_context import project_infra_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_process_governance():
    """Demonstrate process governance with metadata-based cleanup."""
    print("\n=== Process Governance ===")

    # Create process governance manager
    config = ProcessGovernanceConfig(
        cleanup_policy=CleanupPolicy.MODERATE,
        grace_period=5.0,
        force_kill=True,
        max_process_age=3600.0,
        enable_metadata_tracking=True,
        project_isolation=True,
    )

    process_manager = ProcessGovernanceManager(config)

    # Register some processes with metadata
    processes = [
        ProcessMetadata(
            project="api-project",
            service="api-server",
            pid=1001,
            command_line=["python", "api_server.py"],
            environment={"PROJECT": "api-project", "SERVICE": "api-server"},
            scope="local",
            resource_type="api",
            tags={"web", "rest"},
        ),
        ProcessMetadata(
            project="api-project",
            service="worker",
            pid=1002,
            command_line=["python", "worker.py"],
            environment={"PROJECT": "api-project", "SERVICE": "worker"},
            scope="local",
            resource_type="worker",
            tags={"background", "queue"},
        ),
        ProcessMetadata(
            project="web-project",
            service="frontend",
            pid=2001,
            command_line=["npm", "start"],
            environment={"PROJECT": "web-project", "SERVICE": "frontend"},
            scope="local",
            resource_type="web",
            tags={"ui", "react"},
        ),
    ]

    for process in processes:
        process_manager.register_process(process.pid, process)
        print(f"Registered process {process.pid} for {process.project}:{process.service}")

    # List processes by project
    api_processes = process_manager.get_project_processes("api-project")
    print(f"API project processes: {len(api_processes)}")
    for process in api_processes:
        print(f"  {process.service} (PID: {process.pid}) - {process.resource_type}")

    # List processes by service
    api_server_processes = process_manager.get_service_processes("api-server")
    print(f"API server processes: {len(api_server_processes)}")
    for process in api_server_processes:
        print(f"  {process.project} (PID: {process.pid}) - {process.scope}")

    # Demonstrate cleanup (simulated)
    print("\n--- Simulating Process Cleanup ---")
    stats = process_manager.cleanup_project_processes("api-project")
    print(f"Cleanup stats: {stats}")

    # Clean up stale processes
    stats = process_manager.cleanup_stale_processes(max_age=300.0)  # 5 minutes
    print(f"Stale cleanup stats: {stats}")


async def demonstrate_tunnel_governance():
    """Demonstrate tunnel governance with lifecycle management."""
    print("\n=== Tunnel Governance ===")

    # Create tunnel governance manager
    config = TunnelGovernanceConfig(
        lifecycle_policy=TunnelLifecyclePolicy.SMART,
        tunnel_reuse_threshold=300.0,
        tunnel_health_check_interval=30.0,
        max_tunnel_age=3600.0,
        enable_credential_sharing=True,
        enable_tunnel_reuse=True,
        cleanup_stale_tunnels=True,
    )

    tunnel_manager = TunnelGovernanceManager(config)

    # Create tunnels for different projects
    tunnels = []

    # API project tunnels
    api_tunnel = tunnel_manager.create_tunnel(
        project="api-project",
        service="api-server",
        port=8001,
        provider="cloudflare",
        hostname="api.example.com",
        reuse_existing=True,
    )
    tunnels.append(api_tunnel)
    print(f"Created tunnel {api_tunnel.tunnel_id} for API server")

    # Web project tunnel
    web_tunnel = tunnel_manager.create_tunnel(
        project="web-project",
        service="frontend",
        port=3000,
        provider="cloudflare",
        hostname="web.example.com",
        reuse_existing=True,
    )
    tunnels.append(web_tunnel)
    print(f"Created tunnel {web_tunnel.tunnel_id} for frontend")

    # Set credentials for projects
    api_credentials = {
        "token": "api-token-123",
        "account_id": "account-456",
        "zone_id": "zone-789",
    }

    tunnel_manager.set_credentials(
        project="api-project",
        service="api-server",
        provider="cloudflare",
        credentials=api_credentials,
    )
    print("Set credentials for API project")

    # List tunnels by project
    api_tunnels = tunnel_manager.get_project_tunnels("api-project")
    print(f"API project tunnels: {len(api_tunnels)}")
    for tunnel in api_tunnels:
        print(f"  {tunnel.service_name} -> {tunnel.hostname}:{tunnel.port}")

    # Update tunnel status
    tunnel_manager.update_tunnel_status(
        tunnel_id=api_tunnel.tunnel_id,
        status="active",
        hostname="api.example.com",
    )
    print(f"Updated tunnel {api_tunnel.tunnel_id} status to active")

    # Demonstrate tunnel reuse
    reused_tunnel = tunnel_manager.create_tunnel(
        project="api-project",
        service="api-server",
        port=8001,
        provider="cloudflare",
        reuse_existing=True,
    )
    print(f"Reused tunnel: {reused_tunnel.tunnel_id}")

    # Get tunnel statistics
    stats = tunnel_manager.get_tunnel_stats()
    print(f"Tunnel stats: {stats}")


async def demonstrate_cleanup_policies():
    """Demonstrate configurable cleanup policies."""
    print("\n=== Cleanup Policies ===")

    cleanup_manager = CleanupPolicyManager()

    # Create cleanup policies for different projects
    projects = ["api-project", "web-project", "worker-project"]

    for project in projects:
        # Create default policy
        policy = cleanup_manager.create_default_policy(
            project_name=project,
            strategy=CleanupStrategy.MODERATE,
        )
        print(f"Created cleanup policy for {project}: {policy.global_strategy.value}")

    # Update specific rules for api-project
    from pheno.infra.cleanup_policies import CleanupRule

    # More aggressive process cleanup for API project
    process_rule = CleanupRule(
        resource_type=ResourceType.PROCESS,
        strategy=CleanupStrategy.AGGRESSIVE,
        patterns=[f"api-project-*", f"*api-project*"],
        exclude_patterns=["system", "kernel"],
        max_age=1800.0,  # 30 minutes
        force_cleanup=True,
        enabled=True,
    )

    cleanup_manager.update_project_rule("api-project", ResourceType.PROCESS, process_rule)
    print("Updated process cleanup rule for api-project to aggressive")

    # Conservative tunnel cleanup for web project
    tunnel_rule = CleanupRule(
        resource_type=ResourceType.TUNNEL,
        strategy=CleanupStrategy.CONSERVATIVE,
        patterns=[f"web-project-*", f"*web-project*"],
        exclude_patterns=[],
        max_age=7200.0,  # 2 hours
        force_cleanup=False,
        enabled=True,
    )

    cleanup_manager.update_project_rule("web-project", ResourceType.TUNNEL, tunnel_rule)
    print("Updated tunnel cleanup rule for web-project to conservative")

    # Get cleanup strategies
    api_process_strategy = cleanup_manager.get_cleanup_strategy("api-project", ResourceType.PROCESS)
    web_tunnel_strategy = cleanup_manager.get_cleanup_strategy("web-project", ResourceType.TUNNEL)

    print(f"API project process strategy: {api_process_strategy.value}")
    print(f"Web project tunnel strategy: {web_tunnel_strategy.value}")

    # Get cleanup patterns
    api_patterns = cleanup_manager.get_cleanup_patterns("api-project", ResourceType.PROCESS)
    web_patterns = cleanup_manager.get_cleanup_patterns("web-project", ResourceType.TUNNEL)

    print(f"API project process patterns: {api_patterns}")
    print(f"Web project tunnel patterns: {web_patterns}")

    # Export policy
    policy_json = cleanup_manager.export_policy("api-project", "json")
    print(f"Exported API project policy: {len(policy_json)} characters")


async def demonstrate_status_pages():
    """Demonstrate enhanced status pages with service/tunnel status."""
    print("\n=== Status Pages ===")

    status_manager = StatusPageManager()

    # Update service statuses
    status_manager.update_service_status(
        project_name="api-project",
        service_name="api-server",
        status="running",
        port=8001,
        host="localhost",
        pid=1001,
        uptime=3600.0,  # 1 hour
        health_status="healthy",
        metadata={"version": "1.0.0", "environment": "production"},
    )

    status_manager.update_service_status(
        project_name="api-project",
        service_name="worker",
        status="running",
        port=8002,
        host="localhost",
        pid=1002,
        uptime=1800.0,  # 30 minutes
        health_status="healthy",
        metadata={"version": "1.0.0", "environment": "production"},
    )

    status_manager.update_service_status(
        project_name="web-project",
        service_name="frontend",
        status="starting",
        port=3000,
        host="localhost",
        pid=2001,
        uptime=60.0,  # 1 minute
        health_status="starting",
        metadata={"version": "2.0.0", "environment": "staging"},
    )

    # Update tunnel statuses
    status_manager.update_tunnel_status(
        project_name="api-project",
        tunnel_id="api-tunnel-123",
        service_name="api-server",
        hostname="api.example.com",
        port=8001,
        status="active",
        provider="cloudflare",
        health_status="healthy",
        metadata={"zone_id": "zone-789"},
    )

    status_manager.update_tunnel_status(
        project_name="web-project",
        tunnel_id="web-tunnel-456",
        service_name="frontend",
        hostname="web.example.com",
        port=3000,
        status="active",
        provider="cloudflare",
        health_status="healthy",
        metadata={"zone_id": "zone-789"},
    )

    # Set maintenance mode for web project
    status_manager.set_maintenance_mode(
        project_name="web-project",
        enabled=True,
        message="Web project is under maintenance for updates",
    )

    # Generate status pages
    api_status_page = status_manager.generate_status_page("api-project", "status")
    print(f"Generated API project status page: {len(api_status_page)} characters")

    web_loading_page = status_manager.generate_status_page("web-project", "loading")
    print(f"Generated web project loading page: {len(web_loading_page)} characters")

    # Generate project summaries
    api_summary = status_manager.generate_project_summary("api-project")
    print(f"API project summary: {api_summary}")

    web_summary = status_manager.generate_project_summary("web-project")
    print(f"Web project summary: {web_summary}")

    # List all projects
    projects = status_manager.get_all_projects()
    print(f"All projects: {projects}")


async def demonstrate_project_integration():
    """Demonstrate integration with ProjectInfraContext."""
    print("\n=== Project Integration ===")

    with project_infra_context("demo-project") as ctx:
        # Deploy resources with enhanced metadata
        await ctx.deploy_resource(
            name="api-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8001: 80},
                "environment": {
                    "PROJECT": "demo-project",
                    "SERVICE": "api-service",
                },
            },
            metadata={
                "project": "demo-project",
                "service": "api-service",
                "resource_type": "api",
                "tags": ["web", "rest"],
            },
        )

        await ctx.deploy_resource(
            name="worker-service",
            config={
                "type": "docker",
                "image": "redis:alpine",
                "ports": {6379: 6379},
                "environment": {
                    "PROJECT": "demo-project",
                    "SERVICE": "worker-service",
                },
            },
            metadata={
                "project": "demo-project",
                "service": "worker-service",
                "resource_type": "worker",
                "tags": ["background", "queue"],
            },
        )

        # Get project resources
        resources = await ctx.get_project_resources()
        print(f"Deployed {len(resources)} resources for demo-project")

        for resource in resources:
            print(f"  {resource['name']}: {resource['mode']} - {resource['health']}")
            if "metadata" in resource:
                print(f"    Metadata: {resource['metadata']}")


async def demonstrate_cli_integration():
    """Demonstrate CLI integration."""
    print("\n=== CLI Integration ===")

    # Simulate CLI commands
    print("Available CLI commands:")
    print("  pheno process register <project> <service> <pid>")
    print("  pheno process cleanup-project <project>")
    print("  pheno process cleanup-service <service>")
    print("  pheno tunnel create <project> <service> <port>")
    print("  pheno tunnel cleanup-project <project>")
    print("  pheno cleanup init-project <project>")
    print("  pheno cleanup set-rule <project> <resource-type>")
    print("  pheno status show-project <project>")
    print("  pheno status list-projects")
    print("  pheno stats")

    # Simulate policy export
    cleanup_manager = CleanupPolicyManager()
    policy = cleanup_manager.create_default_policy("demo-project")

    policy_json = cleanup_manager.export_policy("demo-project", "json")
    print(f"\nExported policy for demo-project: {len(policy_json)} characters")

    # Simulate status generation
    status_manager = StatusPageManager()
    status_manager.update_service_status(
        project_name="demo-project",
        service_name="api-service",
        status="running",
        port=8001,
        health_status="healthy",
    )

    status_page = status_manager.generate_status_page("demo-project", "status")
    print(f"Generated status page: {len(status_page)} characters")


async def main():
    """Run all Phase 5 demonstrations."""
    print("Phase 5: Process & Tunnel Governance Demonstration")
    print("=" * 60)

    try:
        await demonstrate_process_governance()
        await demonstrate_tunnel_governance()
        await demonstrate_cleanup_policies()
        await demonstrate_status_pages()
        await demonstrate_project_integration()
        await demonstrate_cli_integration()

        print("\n" + "=" * 60)
        print("Phase 5 demonstration completed successfully!")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"\n✗ Demonstration failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
