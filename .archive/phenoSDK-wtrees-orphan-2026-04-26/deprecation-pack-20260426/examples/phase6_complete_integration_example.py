#!/usr/bin/env python3
"""
Phase 6: Complete Integration Example - Configuration & Developer Experience

This comprehensive example demonstrates all Phase 5 features working together
with enhanced configuration management and developer experience:

- Multi-project process governance with metadata-based cleanup
- Shared resource coordination and management
- Tunnel lifecycle management with smart reuse
- Configurable cleanup policies across projects
- Enhanced status monitoring and dashboards
- Configuration management and export/import
- CLI integration and automation

This example shows how to build sophisticated multi-service applications
with shared infrastructure using KInfra Phase 5 features.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from pheno.infra.config_schemas import (
    KInfraConfig,
    KInfraConfigManager,
    ProcessGovernanceConfig,
    TunnelGovernanceConfig,
    CleanupStrategy,
    ResourceType,
    create_default_project_config,
    create_default_routing_config,
)
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
from pheno.infra.tunnel_governance import TunnelGovernanceManager, TunnelLifecyclePolicy
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupRule
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.project_context import project_infra_context


class KInfraPhase6Demo:
    """Complete KInfra Phase 6 demonstration."""

    def __init__(self):
        """Initialize the demo."""
        self.config_manager = KInfraConfigManager()
        self.config = None

        # Managers
        self.deployment_manager = None
        self.resource_coordinator = None
        self.global_registry = None
        self.process_manager = None
        self.tunnel_manager = None
        self.cleanup_manager = None
        self.status_manager = None

        # Demo data
        self.projects = [
            {
                "name": "api-project",
                "services": ["api-server", "api-worker"],
                "strategy": CleanupStrategy.AGGRESSIVE,
                "domain": "api.example.com",
                "pids": [1001, 1002],
            },
            {
                "name": "web-project",
                "services": ["web-server", "web-worker"],
                "strategy": CleanupStrategy.MODERATE,
                "domain": "web.example.com",
                "pids": [2001, 2002],
            },
            {
                "name": "worker-project",
                "services": ["worker-server", "worker-processor"],
                "strategy": CleanupStrategy.CONSERVATIVE,
                "domain": "worker.example.com",
                "pids": [3001, 3002],
            },
        ]

        self.shared_resources = [
            {
                "name": "shared-redis",
                "type": "redis",
                "config": {"host": "localhost", "port": 6379, "db": 0},
            },
            {
                "name": "shared-postgres",
                "type": "postgres",
                "config": {"host": "localhost", "port": 5432, "database": "shared_db"},
            },
            {
                "name": "shared-nats",
                "type": "nats",
                "config": {"url": "nats://localhost:4222"},
            },
        ]

    async def initialize(self):
        """Initialize the demo environment."""
        print("🚀 Initializing KInfra Phase 6 Demo...")

        # Load configuration
        self.config = self.config_manager.load()
        print(f"✅ Configuration loaded: {self.config.app_name}")

        # Initialize managers
        self.deployment_manager = DeploymentManager()
        self.resource_coordinator = ResourceCoordinator(self.deployment_manager)
        self.global_registry = GlobalResourceRegistry()
        self.process_manager = ProcessGovernanceManager()
        self.tunnel_manager = TunnelGovernanceManager()
        self.cleanup_manager = CleanupPolicyManager()
        self.status_manager = StatusPageManager()

        # Initialize resource coordination
        await self.resource_coordinator.initialize()
        print("✅ Resource coordination initialized")

        print("✅ Demo initialization complete")

    async def setup_shared_resources(self):
        """Set up shared resources."""
        print("🏗️ Setting up shared resources...")

        # Deploy shared resources
        for resource in self.shared_resources:
            deployed_resource = await self.deployment_manager.deploy_resource(
                name=resource["name"],
                resource_type=resource["type"],
                mode="global",
                config=resource["config"],
            )

            # Register in global registry
            await self.global_registry.register_resource(
                name=resource["name"],
                resource_type=resource["type"],
                config=resource["config"],
                metadata={
                    "shared": True,
                    "projects": [project["name"] for project in self.projects],
                },
            )

            print(f"✅ Deployed shared resource: {resource['name']}")

        print("✅ Shared resources setup complete")

    async def setup_project_configurations(self):
        """Set up project-specific configurations."""
        print("⚙️ Setting up project configurations...")

        for project in self.projects:
            # Create project cleanup policy
            project_config = create_default_project_config(project["name"])
            project_config.default_strategy = project["strategy"]

            # Customize cleanup rules based on strategy
            if project["strategy"] == CleanupStrategy.AGGRESSIVE:
                max_age = 1800.0
                force_cleanup = True
            elif project["strategy"] == CleanupStrategy.MODERATE:
                max_age = 3600.0
                force_cleanup = False
            else:  # CONSERVATIVE
                max_age = 7200.0
                force_cleanup = False

            # Update process cleanup rule
            project_config.rules[ResourceType.PROCESS] = CleanupRule(
                resource_type=ResourceType.PROCESS,
                strategy=project["strategy"],
                patterns=[f"{project['name']}-*"],
                max_age=max_age,
                force_cleanup=force_cleanup,
                enabled=True,
            )

            # Update tunnel cleanup rule
            project_config.rules[ResourceType.TUNNEL] = CleanupRule(
                resource_type=ResourceType.TUNNEL,
                strategy=CleanupStrategy.CONSERVATIVE,
                patterns=[f"{project['name']}-*"],
                max_age=7200.0,
                force_cleanup=False,
                enabled=True,
            )

            # Update port cleanup rule
            project_config.rules[ResourceType.PORT] = CleanupRule(
                resource_type=ResourceType.PORT,
                strategy=CleanupStrategy.AGGRESSIVE,
                patterns=[f"{project['name']}-*"],
                max_age=1800.0,
                force_cleanup=True,
                enabled=True,
            )

            self.cleanup_manager.set_project_config(project["name"], project_config)

            # Create project routing configuration
            routing_config = create_default_routing_config(project["name"], project["domain"])
            self.config_manager.set_project_routing(project["name"], routing_config)

            print(f"✅ Configured project: {project['name']} (strategy: {project['strategy']})")

        print("✅ Project configurations setup complete")

    async def setup_projects(self):
        """Set up individual projects."""
        print("🏗️ Setting up projects...")

        for project in self.projects:
            print(f"  Setting up {project['name']}...")

            # Use project context for infrastructure management
            with project_infra_context(project["name"]) as infra:
                # Start services
                services = {}
                for i, service in enumerate(project["services"]):
                    port = 8000 + hash(project["name"]) % 1000 + i * 100
                    services[service] = infra.start_service(service, port=port)
                    print(f"    Started {service} on port {port}")

                # Register processes with metadata
                for i, service in enumerate(project["services"]):
                    pid = project["pids"][i]
                    metadata = ProcessMetadata(
                        project=project["name"],
                        service=service,
                        pid=pid,
                        command_line=["python", f"{service}.py"],
                        environment={
                            "PROJECT": project["name"],
                            "SERVICE": service,
                            "REDIS_URL": "redis://localhost:6379/0",
                            "POSTGRES_URL": "postgresql://postgres:postgres@localhost:5432/shared_db",
                            "NATS_URL": "nats://localhost:4222",
                        },
                        scope="local",
                        resource_type=(
                            "api"
                            if "api" in project["name"]
                            else "web" if "web" in project["name"] else "worker"
                        ),
                        tags={service.split("-")[0], "test", "demo"},
                    )
                    self.process_manager.register_process(pid, metadata)
                    print(f"    Registered process {pid} for {service}")

                # Create tunnels
                for i, service in enumerate(project["services"]):
                    if "server" in service:  # Only create tunnels for server services
                        tunnel = self.tunnel_manager.create_tunnel(
                            project=project["name"],
                            service=service,
                            port=services[service],
                            provider="cloudflare",
                            hostname=f"{project['name']}.example.com",
                            reuse_existing=True,
                        )
                        print(f"    Created tunnel for {service}: {tunnel.hostname}")

                # Set tunnel credentials
                self.tunnel_manager.set_credentials(
                    project=project["name"],
                    service=project["services"][0],
                    provider="cloudflare",
                    credentials={"token": f"{project['name']}-token-123"},
                )
                print(f"    Set tunnel credentials for {project['name']}")

        print("✅ Projects setup complete")

    async def setup_status_monitoring(self):
        """Set up status monitoring."""
        print("📊 Setting up status monitoring...")

        for project in self.projects:
            for service in project["services"]:
                # Update service status
                self.status_manager.update_service_status(
                    project_name=project["name"],
                    service_name=service,
                    status="running",
                    port=8000 + hash(project["name"]) % 1000,
                    health_status="healthy",
                )

                # Update tunnel status for server services
                if "server" in service:
                    self.status_manager.update_tunnel_status(
                        project_name=project["name"],
                        service_name=service,
                        status="active",
                        hostname=f"{project['name']}.example.com",
                        provider="cloudflare",
                    )

            print(f"  Updated status for {project['name']}")

        print("✅ Status monitoring setup complete")

    async def demonstrate_process_governance(self):
        """Demonstrate process governance features."""
        print("📋 Demonstrating process governance...")

        # Show process statistics
        process_stats = self.process_manager.get_cleanup_stats()
        print(f"  Process statistics: {process_stats}")

        # Show processes by project
        for project in self.projects:
            project_processes = self.process_manager.get_project_processes(project["name"])
            print(f"  {project['name']}: {len(project_processes)} processes")

            for process in project_processes:
                print(
                    f"    - {process.service} (PID: {process.pid}, Type: {process.resource_type})"
                )

        # Demonstrate cleanup by project
        print("  Testing project-specific cleanup...")
        api_stats = self.process_manager.cleanup_project_processes("api-project")
        print(f"  API project cleanup: {api_stats}")

        # Verify isolation
        web_processes = self.process_manager.get_project_processes("web-project")
        worker_processes = self.process_manager.get_project_processes("worker-project")
        print(f"  Web project processes remaining: {len(web_processes)}")
        print(f"  Worker project processes remaining: {len(worker_processes)}")

        print("✅ Process governance demonstration complete")

    async def demonstrate_tunnel_governance(self):
        """Demonstrate tunnel governance features."""
        print("🌐 Demonstrating tunnel governance...")

        # Show tunnel statistics
        tunnel_stats = self.tunnel_manager.get_tunnel_stats()
        print(f"  Tunnel statistics: {tunnel_stats}")

        # Show tunnels by project
        for project in self.projects:
            project_tunnels = self.tunnel_manager.get_project_tunnels(project["name"])
            print(f"  {project['name']}: {len(project_tunnels)} tunnels")

            for tunnel in project_tunnels:
                print(f"    - {tunnel.service} -> {tunnel.hostname} (Status: {tunnel.status})")

        # Demonstrate tunnel reuse
        print("  Testing tunnel reuse...")
        for project in self.projects:
            # Try to create another tunnel for the same project/service
            reused_tunnel = self.tunnel_manager.create_tunnel(
                project=project["name"],
                service=project["services"][0],
                port=8000 + hash(project["name"]) % 1000,
                provider="cloudflare",
                reuse_existing=True,
            )
            print(f"  {project['name']}: Tunnel reuse successful")

        # Demonstrate tunnel cleanup
        print("  Testing tunnel cleanup...")
        web_tunnel_count = self.tunnel_manager.cleanup_project_tunnels("web-project")
        print(f"  Web project tunnels cleaned up: {web_tunnel_count}")

        print("✅ Tunnel governance demonstration complete")

    async def demonstrate_cleanup_policies(self):
        """Demonstrate cleanup policy features."""
        print("🧹 Demonstrating cleanup policies...")

        # Show cleanup policies for each project
        for project in self.projects:
            policy = self.cleanup_manager.get_project_policy(project["name"])
            if policy:
                print(f"  {project['name']}: {policy.default_strategy} strategy")

                for resource_type, rule in policy.rules.items():
                    print(
                        f"    - {resource_type}: {rule.strategy} (max_age: {rule.max_age}s, force: {rule.force_cleanup})"
                    )

        # Show global cleanup policy
        global_policy = self.cleanup_manager.get_global_policy()
        print(f"  Global policy: {global_policy.default_strategy} strategy")
        print(f"  Max concurrent cleanups: {global_policy.max_concurrent_cleanups}")
        print(f"  Cleanup timeout: {global_policy.cleanup_timeout}s")

        # Demonstrate policy enforcement
        print("  Testing policy enforcement...")
        for project in self.projects:
            strategy = self.cleanup_manager.get_cleanup_strategy(
                project_name=project["name"], resource_type=ResourceType.PROCESS
            )
            print(f"  {project['name']} process cleanup strategy: {strategy}")

        print("✅ Cleanup policies demonstration complete")

    async def demonstrate_status_monitoring(self):
        """Demonstrate status monitoring features."""
        print("📊 Demonstrating status monitoring...")

        # Show project status
        for project in self.projects:
            project_status = self.status_manager.get_project_status(project["name"])
            if project_status:
                print(f"  {project['name']}:")
                print(f"    Services: {len(project_status.services)}")
                print(f"    Tunnels: {len(project_status.tunnels)}")

                for service_name, service_status in project_status.services.items():
                    print(
                        f"      - {service_name}: {service_status.status} ({service_status.health_status})"
                    )

                for tunnel_name, tunnel_status in project_status.tunnels.items():
                    print(
                        f"      - {tunnel_name}: {tunnel_status.status} ({tunnel_status.hostname})"
                    )

        # Generate status pages
        print("  Generating status pages...")

        # Generate project-specific status pages
        for project in self.projects:
            status_page = self.status_manager.generate_status_page(project["name"], "status")
            print(f"  Generated status page for {project['name']} ({len(status_page)} characters)")

        # Generate global status dashboard
        global_status = self.status_manager.generate_status_page("global", "dashboard")
        print(f"  Generated global status dashboard ({len(global_status)} characters)")

        # Generate project summary
        project_summary = self.status_manager.generate_project_summary("api-project")
        print(f"  Generated project summary for api-project: {project_summary}")

        print("✅ Status monitoring demonstration complete")

    async def demonstrate_configuration_management(self):
        """Demonstrate configuration management features."""
        print("⚙️ Demonstrating configuration management...")

        # Show current configuration
        print("  Current configuration:")
        print(f"    App name: {self.config.app_name}")
        print(f"    Debug mode: {self.config.debug}")
        print(f"    Log level: {self.config.log_level}")
        print(f"    Environment: {self.config.environment}")

        # Show project configurations
        for project in self.projects:
            project_config = self.config_manager.get_project_config(project["name"])
            routing_config = self.config_manager.get_project_routing(project["name"])

            if project_config:
                print(f"  {project['name']} cleanup policy: {project_config.default_strategy}")

            if routing_config:
                print(
                    f"  {project['name']} routing: {routing_config.domain}{routing_config.base_path}"
                )

        # Export configuration
        print("  Exporting configuration...")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            self.config_manager.save_config(self.config, Path(f.name))
            config_file = Path(f.name)

        print(f"  Configuration exported to: {config_file}")

        # Import configuration
        print("  Importing configuration...")
        new_config_manager = KInfraConfigManager(config_file)
        new_config = new_config_manager.load()

        print(f"  Imported configuration: {new_config.app_name}")

        # Clean up temporary file
        config_file.unlink()

        print("✅ Configuration management demonstration complete")

    async def demonstrate_cli_integration(self):
        """Demonstrate CLI integration."""
        print("💻 Demonstrating CLI integration...")

        # Simulate CLI commands
        print("  Simulating CLI commands...")

        # Process management commands
        print("    kinfra process list --project api-project")
        api_processes = self.process_manager.get_project_processes("api-project")
        print(f"      Found {len(api_processes)} processes")

        print("    kinfra process cleanup-project web-project --force")
        web_stats = self.process_manager.cleanup_project_processes("web-project")
        print(f"      Cleaned up {web_stats['terminated']} processes")

        # Tunnel management commands
        print("    kinfra tunnel list --project worker-project")
        worker_tunnels = self.tunnel_manager.get_project_tunnels("worker-project")
        print(f"      Found {len(worker_tunnels)} tunnels")

        print("    kinfra tunnel cleanup --project worker-project")
        worker_tunnel_count = self.tunnel_manager.cleanup_project_tunnels("worker-project")
        print(f"      Cleaned up {worker_tunnel_count} tunnels")

        # Cleanup policy commands
        print("    kinfra cleanup show-policy api-project")
        api_policy = self.cleanup_manager.get_project_policy("api-project")
        if api_policy:
            print(f"      Policy: {api_policy.default_strategy}")

        # Status monitoring commands
        print("    kinfra status show-project api-project")
        api_status = self.status_manager.get_project_status("api-project")
        if api_status:
            print(f"      Services: {len(api_status.services)}, Tunnels: {len(api_status.tunnels)}")

        print("    kinfra status list-projects")
        all_projects = self.status_manager.get_all_projects()
        print(f"      Projects: {all_projects}")

        # Statistics commands
        print("    kinfra stats")
        process_stats = self.process_manager.get_cleanup_stats()
        tunnel_stats = self.tunnel_manager.get_tunnel_stats()
        print(f"      Process stats: {process_stats}")
        print(f"      Tunnel stats: {tunnel_stats}")

        print("✅ CLI integration demonstration complete")

    async def run_demo(self):
        """Run the complete demo."""
        print("🎬 Starting KInfra Phase 6 Complete Integration Demo")
        print("=" * 60)

        try:
            # Initialize
            await self.initialize()

            # Set up shared resources
            await self.setup_shared_resources()

            # Set up project configurations
            await self.setup_project_configurations()

            # Set up projects
            await self.setup_projects()

            # Set up status monitoring
            await self.setup_status_monitoring()

            print("\n" + "=" * 60)
            print("🎯 DEMONSTRATION PHASE")
            print("=" * 60)

            # Demonstrate features
            await self.demonstrate_process_governance()
            print()

            await self.demonstrate_tunnel_governance()
            print()

            await self.demonstrate_cleanup_policies()
            print()

            await self.demonstrate_status_monitoring()
            print()

            await self.demonstrate_configuration_management()
            print()

            await self.demonstrate_cli_integration()
            print()

            print("=" * 60)
            print("🎉 KInfra Phase 6 Demo Complete!")
            print("=" * 60)

            # Final statistics
            print("\n📊 Final Statistics:")
            process_stats = self.process_manager.get_cleanup_stats()
            tunnel_stats = self.tunnel_manager.get_tunnel_stats()

            print(f"  Process governance: {process_stats}")
            print(f"  Tunnel governance: {tunnel_stats}")

            # Show remaining resources
            print("\n🔍 Remaining Resources:")
            for project in self.projects:
                project_processes = self.process_manager.get_project_processes(project["name"])
                project_tunnels = self.tunnel_manager.get_project_tunnels(project["name"])
                print(
                    f"  {project['name']}: {len(project_processes)} processes, {len(project_tunnels)} tunnels"
                )

            print("\n✅ Demo completed successfully!")

        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            import traceback

            traceback.print_exc()
            raise


async def main():
    """Main function."""
    demo = KInfraPhase6Demo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
