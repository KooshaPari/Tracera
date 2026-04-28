"""
Phase 5 Integration Tests: Multi-Project and Shared Resource Scenarios

This module provides comprehensive integration tests for Phase 5 features
(Process Governance, Tunnel Governance, Cleanup Policies, Status Pages)
across multiple projects with shared resources.

Test scenarios:
- Multi-project process governance
- Shared resource coordination
- Tunnel lifecycle management
- Cleanup policy enforcement
- Status monitoring and dashboards
- Resource isolation and cleanup
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

import pytest

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


class TestMultiProjectProcessGovernance:
    """Test process governance across multiple projects."""

    @pytest.fixture
    async def setup_managers(self):
        """Set up managers for testing."""
        process_manager = ProcessGovernanceManager()
        tunnel_manager = TunnelGovernanceManager()
        cleanup_manager = CleanupPolicyManager()
        status_manager = StatusPageManager()

        return {
            "process_manager": process_manager,
            "tunnel_manager": tunnel_manager,
            "cleanup_manager": cleanup_manager,
            "status_manager": status_manager,
        }

    @pytest.fixture
    def test_projects(self):
        """Test project configurations."""
        return [
            {
                "name": "api-project",
                "services": ["api-server", "api-worker"],
                "strategy": CleanupStrategy.AGGRESSIVE,
                "pids": [1001, 1002],
            },
            {
                "name": "web-project",
                "services": ["web-server", "web-worker"],
                "strategy": CleanupStrategy.MODERATE,
                "pids": [2001, 2002],
            },
            {
                "name": "worker-project",
                "services": ["worker-server", "worker-processor"],
                "strategy": CleanupStrategy.CONSERVATIVE,
                "pids": [3001, 3002],
            },
        ]

    async def test_multi_project_process_registration(self, setup_managers, test_projects):
        """Test process registration across multiple projects."""
        managers = await setup_managers
        process_manager = managers["process_manager"]

        # Register processes for each project
        for project in test_projects:
            for i, service in enumerate(project["services"]):
                pid = project["pids"][i]
                metadata = ProcessMetadata(
                    project=project["name"],
                    service=service,
                    pid=pid,
                    command_line=["python", f"{service}.py"],
                    environment={"PROJECT": project["name"]},
                    scope="local",
                    resource_type=(
                        "api"
                        if "api" in project["name"]
                        else "web" if "web" in project["name"] else "worker"
                    ),
                    tags={service.split("-")[0], "test"},
                )
                process_manager.register_process(pid, metadata)

        # Verify process registration
        for project in test_projects:
            project_processes = process_manager.get_project_processes(project["name"])
            assert len(project_processes) == len(project["services"])

            for process in project_processes:
                assert process.project == project["name"]
                assert process.service in project["services"]

    async def test_project_specific_cleanup(self, setup_managers, test_projects):
        """Test project-specific process cleanup."""
        managers = await setup_managers
        process_manager = managers["process_manager"]
        cleanup_manager = managers["cleanup_manager"]

        # Set up cleanup policies for each project
        for project in test_projects:
            policy = cleanup_manager.create_default_policy(
                project_name=project["name"], strategy=project["strategy"]
            )

            # Customize cleanup rules
            cleanup_manager.update_project_rule(
                project_name=project["name"],
                resource_type=ResourceType.PROCESS,
                strategy=project["strategy"],
                patterns=[f"{project['name']}-*"],
                max_age=3600.0,
                force_cleanup=project["strategy"] == CleanupStrategy.AGGRESSIVE,
            )

        # Register processes
        for project in test_projects:
            for i, service in enumerate(project["services"]):
                pid = project["pids"][i]
                metadata = ProcessMetadata(
                    project=project["name"],
                    service=service,
                    pid=pid,
                    command_line=["python", f"{service}.py"],
                    environment={"PROJECT": project["name"]},
                    scope="local",
                    resource_type=(
                        "api"
                        if "api" in project["name"]
                        else "web" if "web" in project["name"] else "worker"
                    ),
                    tags={service.split("-")[0], "test"},
                )
                process_manager.register_process(pid, metadata)

        # Test project-specific cleanup
        for project in test_projects:
            stats = process_manager.cleanup_project_processes(project["name"])
            assert stats["terminated"] == len(project["services"])
            assert stats["skipped"] == 0

    async def test_cross_project_isolation(self, setup_managers, test_projects):
        """Test that projects are properly isolated."""
        managers = await setup_managers
        process_manager = managers["process_manager"]

        # Register processes for each project
        for project in test_projects:
            for i, service in enumerate(project["services"]):
                pid = project["pids"][i]
                metadata = ProcessMetadata(
                    project=project["name"],
                    service=service,
                    pid=pid,
                    command_line=["python", f"{service}.py"],
                    environment={"PROJECT": project["name"]},
                    scope="local",
                    resource_type=(
                        "api"
                        if "api" in project["name"]
                        else "web" if "web" in project["name"] else "worker"
                    ),
                    tags={service.split("-")[0], "test"},
                )
                process_manager.register_process(pid, metadata)

        # Verify isolation - cleaning up one project shouldn't affect others
        api_stats = process_manager.cleanup_project_processes("api-project")
        assert api_stats["terminated"] == 2  # api-server, api-worker

        # Other projects should still have their processes
        web_processes = process_manager.get_project_processes("web-project")
        worker_processes = process_manager.get_project_processes("worker-project")
        assert len(web_processes) == 2
        assert len(worker_processes) == 2


class TestSharedResourceCoordination:
    """Test shared resource coordination across projects."""

    @pytest.fixture
    async def setup_shared_resources(self):
        """Set up shared resources for testing."""
        deployment_manager = DeploymentManager()
        resource_coordinator = ResourceCoordinator(deployment_manager)
        global_registry = GlobalResourceRegistry()

        await resource_coordinator.initialize()

        # Deploy shared resources
        redis_resource = await deployment_manager.deploy_resource(
            name="shared-redis",
            resource_type="redis",
            mode="global",
            config={"host": "localhost", "port": 6379, "db": 0},
        )

        postgres_resource = await deployment_manager.deploy_resource(
            name="shared-postgres",
            resource_type="postgres",
            mode="global",
            config={"host": "localhost", "port": 5432, "database": "shared_db"},
        )

        # Register in global registry
        await global_registry.register_resource(
            name="shared-redis",
            resource_type="redis",
            config={"host": "localhost", "port": 6379, "db": 0},
            metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]},
        )

        await global_registry.register_resource(
            name="shared-postgres",
            resource_type="postgres",
            config={"host": "localhost", "port": 5432, "database": "shared_db"},
            metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]},
        )

        return {
            "deployment_manager": deployment_manager,
            "resource_coordinator": resource_coordinator,
            "global_registry": global_registry,
            "redis_resource": redis_resource,
            "postgres_resource": postgres_resource,
        }

    async def test_shared_resource_deployment(self, setup_shared_resources):
        """Test deployment of shared resources."""
        resources = await setup_shared_resources
        deployment_manager = resources["deployment_manager"]
        global_registry = resources["global_registry"]

        # Verify resources are deployed
        redis_resource = await deployment_manager.get_resource("shared-redis")
        postgres_resource = await deployment_manager.get_resource("shared-postgres")

        assert redis_resource is not None
        assert postgres_resource is not None
        assert redis_resource.resource_type == "redis"
        assert postgres_resource.resource_type == "postgres"

        # Verify global registry
        redis_registry = await global_registry.get_resource("shared-redis")
        postgres_registry = await global_registry.get_resource("shared-postgres")

        assert redis_registry is not None
        assert postgres_registry is not None
        assert redis_registry.metadata["shared"] is True

    async def test_project_resource_access(self, setup_shared_resources):
        """Test that projects can access shared resources."""
        resources = await setup_shared_resources
        global_registry = resources["global_registry"]

        # Test project access to shared resources
        projects = ["api-project", "web-project", "worker-project"]

        for project in projects:
            # Simulate project context
            with project_infra_context(project) as infra:
                # Projects should be able to access shared resources
                # This would typically involve service discovery or configuration
                # For testing, we verify the resources are available
                redis_resource = await global_registry.get_resource("shared-redis")
                postgres_resource = await global_registry.get_resource("shared-postgres")

                assert redis_resource is not None
                assert postgres_resource is not None
                assert project in redis_resource.metadata["projects"]
                assert project in postgres_resource.metadata["projects"]


class TestTunnelLifecycleManagement:
    """Test tunnel lifecycle management across projects."""

    @pytest.fixture
    async def setup_tunnel_management(self):
        """Set up tunnel management for testing."""
        tunnel_manager = TunnelGovernanceManager()
        process_manager = ProcessGovernanceManager()

        return {
            "tunnel_manager": tunnel_manager,
            "process_manager": process_manager,
        }

    async def test_tunnel_creation_and_reuse(self, setup_tunnel_management):
        """Test tunnel creation and reuse across projects."""
        managers = await setup_tunnel_management
        tunnel_manager = managers["tunnel_manager"]

        projects = ["api-project", "web-project", "worker-project"]

        # Create tunnels for each project
        tunnels = {}
        for project in projects:
            tunnel = tunnel_manager.create_tunnel(
                project=project,
                service=f"{project.split('-')[0]}-server",
                port=8000,
                provider="cloudflare",
                reuse_existing=True,
            )
            tunnels[project] = tunnel

            assert tunnel.project == project
            assert tunnel.status == "active"

        # Test tunnel reuse
        for project in projects:
            # Try to create another tunnel for the same project/service
            reused_tunnel = tunnel_manager.create_tunnel(
                project=project,
                service=f"{project.split('-')[0]}-server",
                port=8000,
                provider="cloudflare",
                reuse_existing=True,
            )

            # Should reuse existing tunnel
            assert reused_tunnel.tunnel_id == tunnels[project].tunnel_id

    async def test_tunnel_cleanup_by_project(self, setup_tunnel_management):
        """Test tunnel cleanup by project."""
        managers = await setup_tunnel_management
        tunnel_manager = managers["tunnel_manager"]

        projects = ["api-project", "web-project", "worker-project"]

        # Create tunnels for each project
        for project in projects:
            tunnel = tunnel_manager.create_tunnel(
                project=project,
                service=f"{project.split('-')[0]}-server",
                port=8000,
                provider="cloudflare",
                reuse_existing=False,
            )
            assert tunnel.project == project

        # Clean up tunnels for specific project
        cleanup_count = tunnel_manager.cleanup_project_tunnels("api-project")
        assert cleanup_count == 1

        # Verify other projects still have their tunnels
        web_tunnels = tunnel_manager.get_project_tunnels("web-project")
        worker_tunnels = tunnel_manager.get_project_tunnels("worker-project")
        assert len(web_tunnels) == 1
        assert len(worker_tunnels) == 1

    async def test_tunnel_credential_management(self, setup_tunnel_management):
        """Test tunnel credential management."""
        managers = await setup_tunnel_management
        tunnel_manager = managers["tunnel_manager"]

        # Set project-specific credentials
        tunnel_manager.set_credentials(
            project="api-project",
            service="api-server",
            provider="cloudflare",
            credentials={"token": "api-token-123"},
        )

        # Set global credentials
        tunnel_manager.set_credentials(
            project=None,
            service=None,
            provider="cloudflare",
            credentials={"token": "global-token-456"},
        )

        # Verify credentials
        api_creds = tunnel_manager.get_credentials("api-project", "api-server", "cloudflare")
        global_creds = tunnel_manager.get_credentials(None, None, "cloudflare")

        assert api_creds is not None
        assert api_creds.credentials["token"] == "api-token-123"
        assert global_creds is not None
        assert global_creds.credentials["token"] == "global-token-456"


class TestCleanupPolicyEnforcement:
    """Test cleanup policy enforcement across projects."""

    @pytest.fixture
    async def setup_cleanup_policies(self):
        """Set up cleanup policies for testing."""
        cleanup_manager = CleanupPolicyManager()
        process_manager = ProcessGovernanceManager()

        return {
            "cleanup_manager": cleanup_manager,
            "process_manager": process_manager,
        }

    async def test_project_specific_cleanup_policies(self, setup_cleanup_policies):
        """Test project-specific cleanup policies."""
        managers = await setup_cleanup_policies
        cleanup_manager = managers["cleanup_manager"]
        process_manager = managers["process_manager"]

        projects = [
            {"name": "api-project", "strategy": CleanupStrategy.AGGRESSIVE},
            {"name": "web-project", "strategy": CleanupStrategy.MODERATE},
            {"name": "worker-project", "strategy": CleanupStrategy.CONSERVATIVE},
        ]

        # Set up cleanup policies for each project
        for project in projects:
            policy = cleanup_manager.create_default_policy(
                project_name=project["name"], strategy=project["strategy"]
            )

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

            cleanup_manager.update_project_rule(
                project_name=project["name"],
                resource_type=ResourceType.PROCESS,
                strategy=project["strategy"],
                patterns=[f"{project['name']}-*"],
                max_age=max_age,
                force_cleanup=force_cleanup,
            )

        # Register processes for each project
        for project in projects:
            for i in range(3):  # 3 processes per project
                pid = 1000 + hash(project["name"]) % 1000 + i
                metadata = ProcessMetadata(
                    project=project["name"],
                    service=f"{project['name']}-service-{i}",
                    pid=pid,
                    command_line=["python", f"service_{i}.py"],
                    environment={"PROJECT": project["name"]},
                    scope="local",
                    resource_type=(
                        "api"
                        if "api" in project["name"]
                        else "web" if "web" in project["name"] else "worker"
                    ),
                    tags={"test"},
                )
                process_manager.register_process(pid, metadata)

        # Test cleanup policy enforcement
        for project in projects:
            # Get cleanup strategy for this project
            strategy = cleanup_manager.get_cleanup_strategy(
                project_name=project["name"], resource_type=ResourceType.PROCESS
            )

            assert strategy == project["strategy"]

            # Test cleanup with project-specific policy
            stats = process_manager.cleanup_project_processes(project["name"])
            assert stats["terminated"] == 3  # All 3 processes should be cleaned up

    async def test_global_cleanup_policy(self, setup_cleanup_policies):
        """Test global cleanup policy."""
        managers = await setup_cleanup_policies
        cleanup_manager = managers["cleanup_manager"]

        # Set global cleanup policy
        global_policy = cleanup_manager.get_global_policy()
        global_policy.default_strategy = CleanupStrategy.CONSERVATIVE
        global_policy.max_concurrent_cleanups = 5
        global_policy.cleanup_timeout = 300.0
        global_policy.enabled = True

        cleanup_manager.update_global_policy(global_policy)

        # Verify global policy
        updated_policy = cleanup_manager.get_global_policy()
        assert updated_policy.default_strategy == CleanupStrategy.CONSERVATIVE
        assert updated_policy.max_concurrent_cleanups == 5
        assert updated_policy.cleanup_timeout == 300.0
        assert updated_policy.enabled is True


class TestStatusMonitoringAndDashboards:
    """Test status monitoring and dashboards across projects."""

    @pytest.fixture
    async def setup_status_monitoring(self):
        """Set up status monitoring for testing."""
        status_manager = StatusPageManager()
        process_manager = ProcessGovernanceManager()
        tunnel_manager = TunnelGovernanceManager()

        return {
            "status_manager": status_manager,
            "process_manager": process_manager,
            "tunnel_manager": tunnel_manager,
        }

    async def test_multi_project_status_tracking(self, setup_status_monitoring):
        """Test status tracking across multiple projects."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        projects = ["api-project", "web-project", "worker-project"]
        services = ["api-server", "web-server", "worker-server"]

        # Update status for each project
        for i, project in enumerate(projects):
            service = services[i]
            status_manager.update_service_status(
                project_name=project,
                service_name=service,
                status="running",
                port=8000 + i * 1000,
                health_status="healthy",
            )

            # Update tunnel status
            status_manager.update_tunnel_status(
                project_name=project,
                service_name=service,
                status="active",
                hostname=f"{project}.example.com",
                provider="cloudflare",
            )

        # Verify status tracking
        for project in projects:
            project_status = status_manager.get_project_status(project)
            assert project_status is not None
            assert project_status.project_name == project
            assert len(project_status.services) == 1
            assert len(project_status.tunnels) == 1

            service_status = project_status.services[list(project_status.services.keys())[0]]
            assert service_status.status == "running"
            assert service_status.health_status == "healthy"

            tunnel_status = project_status.tunnels[list(project_status.tunnels.keys())[0]]
            assert tunnel_status.status == "active"

    async def test_global_status_dashboard(self, setup_status_monitoring):
        """Test global status dashboard generation."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        projects = ["api-project", "web-project", "worker-project"]
        services = ["api-server", "web-server", "worker-server"]

        # Update status for all projects
        for i, project in enumerate(projects):
            service = services[i]
            status_manager.update_service_status(
                project_name=project,
                service_name=service,
                status="running",
                port=8000 + i * 1000,
                health_status="healthy",
            )

            status_manager.update_tunnel_status(
                project_name=project,
                service_name=service,
                status="active",
                hostname=f"{project}.example.com",
                provider="cloudflare",
            )

        # Generate global status dashboard
        global_status = status_manager.generate_status_page("global", "dashboard")
        assert global_status is not None
        assert "global" in global_status.lower()

        # Generate project-specific status pages
        for project in projects:
            project_status = status_manager.generate_status_page(project, "status")
            assert project_status is not None
            assert project in project_status.lower()

    async def test_status_page_customization(self, setup_status_monitoring):
        """Test status page customization."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        # Update service status
        status_manager.update_service_status(
            project_name="api-project",
            service_name="api-server",
            status="running",
            port=8000,
            health_status="healthy",
        )

        # Generate different types of status pages
        status_page = status_manager.generate_status_page("api-project", "status")
        maintenance_page = status_manager.generate_status_page("api-project", "maintenance")
        error_page = status_manager.generate_status_page("api-project", "error")
        loading_page = status_manager.generate_status_page("api-project", "loading")

        assert status_page is not None
        assert maintenance_page is not None
        assert error_page is not None
        assert loading_page is not None

        # Verify page content
        assert "api-project" in status_page
        assert "maintenance" in maintenance_page.lower()
        assert "error" in error_page.lower()
        assert "loading" in loading_page.lower()


class TestResourceIsolationAndCleanup:
    """Test resource isolation and cleanup across projects."""

    @pytest.fixture
    async def setup_resource_isolation(self):
        """Set up resource isolation for testing."""
        process_manager = ProcessGovernanceManager()
        tunnel_manager = TunnelGovernanceManager()
        cleanup_manager = CleanupPolicyManager()
        status_manager = StatusPageManager()

        return {
            "process_manager": process_manager,
            "tunnel_manager": tunnel_manager,
            "cleanup_manager": cleanup_manager,
            "status_manager": status_manager,
        }

    async def test_resource_isolation(self, setup_resource_isolation):
        """Test that projects are properly isolated."""
        managers = await setup_resource_isolation
        process_manager = managers["process_manager"]
        tunnel_manager = managers["tunnel_manager"]

        projects = ["api-project", "web-project", "worker-project"]

        # Set up resources for each project
        for project in projects:
            # Register processes
            for i in range(2):
                pid = 1000 + hash(project) % 1000 + i
                metadata = ProcessMetadata(
                    project=project,
                    service=f"{project}-service-{i}",
                    pid=pid,
                    command_line=["python", f"service_{i}.py"],
                    environment={"PROJECT": project},
                    scope="local",
                    resource_type=(
                        "api" if "api" in project else "web" if "web" in project else "worker"
                    ),
                    tags={"test"},
                )
                process_manager.register_process(pid, metadata)

            # Create tunnels
            tunnel = tunnel_manager.create_tunnel(
                project=project,
                service=f"{project}-server",
                port=8000,
                provider="cloudflare",
                reuse_existing=False,
            )
            assert tunnel.project == project

        # Test isolation - cleanup one project shouldn't affect others
        api_stats = process_manager.cleanup_project_processes("api-project")
        assert api_stats["terminated"] == 2

        api_tunnel_count = tunnel_manager.cleanup_project_tunnels("api-project")
        assert api_tunnel_count == 1

        # Other projects should still have their resources
        web_processes = process_manager.get_project_processes("web-project")
        worker_processes = process_manager.get_project_processes("worker-project")
        web_tunnels = tunnel_manager.get_project_tunnels("web-project")
        worker_tunnels = tunnel_manager.get_project_tunnels("worker-project")

        assert len(web_processes) == 2
        assert len(worker_processes) == 2
        assert len(web_tunnels) == 1
        assert len(worker_tunnels) == 1

    async def test_global_cleanup(self, setup_resource_isolation):
        """Test global cleanup across all projects."""
        managers = await setup_resource_isolation
        process_manager = managers["process_manager"]
        tunnel_manager = managers["tunnel_manager"]

        projects = ["api-project", "web-project", "worker-project"]

        # Set up resources for each project
        for project in projects:
            # Register processes
            for i in range(2):
                pid = 1000 + hash(project) % 1000 + i
                metadata = ProcessMetadata(
                    project=project,
                    service=f"{project}-service-{i}",
                    pid=pid,
                    command_line=["python", f"service_{i}.py"],
                    environment={"PROJECT": project},
                    scope="local",
                    resource_type=(
                        "api" if "api" in project else "web" if "web" in project else "worker"
                    ),
                    tags={"test"},
                )
                process_manager.register_process(pid, metadata)

            # Create tunnels
            tunnel_manager.create_tunnel(
                project=project,
                service=f"{project}-server",
                port=8000,
                provider="cloudflare",
                reuse_existing=False,
            )

        # Test global cleanup
        total_terminated = 0
        total_tunnels_cleaned = 0

        for project in projects:
            process_stats = process_manager.cleanup_project_processes(project)
            tunnel_count = tunnel_manager.cleanup_project_tunnels(project)

            total_terminated += process_stats["terminated"]
            total_tunnels_cleaned += tunnel_count

        assert total_terminated == 6  # 2 processes per project * 3 projects
        assert total_tunnels_cleaned == 3  # 1 tunnel per project * 3 projects


class TestConfigurationIntegration:
    """Test configuration integration across projects."""

    @pytest.fixture
    async def setup_configuration(self):
        """Set up configuration for testing."""
        config_manager = KInfraConfigManager()

        return {
            "config_manager": config_manager,
        }

    async def test_multi_project_configuration(self, setup_configuration):
        """Test multi-project configuration management."""
        managers = await setup_configuration
        config_manager = managers["config_manager"]

        # Load configuration
        config = config_manager.load()

        # Set up project configurations
        projects = ["api-project", "web-project", "worker-project"]

        for project in projects:
            # Create project cleanup policy
            project_config = create_default_project_config(project)
            config_manager.set_project_config(project, project_config)

            # Create project routing configuration
            routing_config = create_default_routing_config(project, f"{project}.example.com")
            config_manager.set_project_routing(project, routing_config)

        # Verify configurations
        for project in projects:
            project_config = config_manager.get_project_config(project)
            routing_config = config_manager.get_project_routing(project)

            assert project_config is not None
            assert project_config.project_name == project
            assert routing_config is not None
            assert routing_config.project_name == project
            assert routing_config.domain == f"{project}.example.com"

    async def test_configuration_export_import(self, setup_configuration):
        """Test configuration export and import."""
        managers = await setup_configuration
        config_manager = managers["config_manager"]

        # Load configuration
        config = config_manager.load()

        # Set up project configurations
        projects = ["api-project", "web-project", "worker-project"]

        for project in projects:
            project_config = create_default_project_config(project)
            config_manager.set_project_config(project, project_config)

            routing_config = create_default_routing_config(project, f"{project}.example.com")
            config_manager.set_project_routing(project, routing_config)

        # Export configuration
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_manager.save_config(config, Path(f.name))
            config_file = Path(f.name)

        try:
            # Load configuration from file
            new_config_manager = KInfraConfigManager(config_file)
            new_config = new_config_manager.load()

            # Verify configurations match
            assert new_config.app_name == config.app_name
            assert len(new_config.projects) == len(config.projects)
            assert len(new_config.project_routing) == len(config.project_routing)

            for project in projects:
                assert project in new_config.projects
                assert project in new_config.project_routing

                new_project_config = new_config_manager.get_project_config(project)
                new_routing_config = new_config_manager.get_project_routing(project)

                assert new_project_config is not None
                assert new_routing_config is not None
                assert new_project_config.project_name == project
                assert new_routing_config.project_name == project

        finally:
            # Clean up temporary file
            config_file.unlink()


# Integration test runner
async def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Running Phase 5 Integration Tests...")

    # Test multi-project process governance
    print("📋 Testing multi-project process governance...")
    test_multi_project = TestMultiProjectProcessGovernance()
    await test_multi_project.test_multi_project_process_registration()
    await test_multi_project.test_project_specific_cleanup()
    await test_multi_project.test_cross_project_isolation()
    print("✅ Multi-project process governance tests passed")

    # Test shared resource coordination
    print("🏗️ Testing shared resource coordination...")
    test_shared_resources = TestSharedResourceCoordination()
    await test_shared_resources.test_shared_resource_deployment()
    await test_shared_resources.test_project_resource_access()
    print("✅ Shared resource coordination tests passed")

    # Test tunnel lifecycle management
    print("🌐 Testing tunnel lifecycle management...")
    test_tunnels = TestTunnelLifecycleManagement()
    await test_tunnels.test_tunnel_creation_and_reuse()
    await test_tunnels.test_tunnel_cleanup_by_project()
    await test_tunnels.test_tunnel_credential_management()
    print("✅ Tunnel lifecycle management tests passed")

    # Test cleanup policy enforcement
    print("🧹 Testing cleanup policy enforcement...")
    test_cleanup = TestCleanupPolicyEnforcement()
    await test_cleanup.test_project_specific_cleanup_policies()
    await test_cleanup.test_global_cleanup_policy()
    print("✅ Cleanup policy enforcement tests passed")

    # Test status monitoring and dashboards
    print("📊 Testing status monitoring and dashboards...")
    test_status = TestStatusMonitoringAndDashboards()
    await test_status.test_multi_project_status_tracking()
    await test_status.test_global_status_dashboard()
    await test_status.test_status_page_customization()
    print("✅ Status monitoring and dashboards tests passed")

    # Test resource isolation and cleanup
    print("🔒 Testing resource isolation and cleanup...")
    test_isolation = TestResourceIsolationAndCleanup()
    await test_isolation.test_resource_isolation()
    await test_isolation.test_global_cleanup()
    print("✅ Resource isolation and cleanup tests passed")

    # Test configuration integration
    print("⚙️ Testing configuration integration...")
    test_config = TestConfigurationIntegration()
    await test_config.test_multi_project_configuration()
    await test_config.test_configuration_export_import()
    print("✅ Configuration integration tests passed")

    print("🎉 All Phase 5 integration tests passed!")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
