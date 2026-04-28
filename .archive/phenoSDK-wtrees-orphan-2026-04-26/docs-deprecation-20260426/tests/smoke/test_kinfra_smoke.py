"""
KInfra Smoke Tests: Port Allocation, Proxy Mapping, Resource Reuse

This module provides smoke tests for CI integration, focusing on critical
KInfra functionality that must work reliably in production environments.

Test categories:
- Port allocation and reuse
- Proxy mapping and routing
- Resource coordination and reuse
- Process governance basics
- Tunnel governance basics
- Cleanup policy enforcement
- Status monitoring functionality
"""

import asyncio
import pytest
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from pheno.infra.config_schemas import KInfraConfigManager, create_default_project_config
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.port_allocator import SmartPortAllocator
from pheno.infra.port_registry import PortRegistry
from pheno.infra.proxy_gateway.server.core import ProxyServer
from pheno.infra.fallback_site.server.core import FallbackServer
from pheno.infra.project_context import project_infra_context


class TestPortAllocationSmoke:
    """Smoke tests for port allocation functionality."""

    @pytest.fixture
    async def setup_port_allocation(self):
        """Set up port allocation for testing."""
        port_registry = PortRegistry()
        port_allocator = SmartPortAllocator()

        return {
            "port_registry": port_registry,
            "port_allocator": port_allocator,
        }

    async def test_basic_port_allocation(self, setup_port_allocation):
        """Test basic port allocation functionality."""
        managers = await setup_port_allocation
        port_allocator = managers["port_allocator"]

        # Test port allocation
        port = port_allocator.allocate_port("test-service", 8000)
        assert port is not None
        assert port >= 8000

        # Test port reuse
        reused_port = port_allocator.allocate_port("test-service", 8000)
        assert reused_port == port

        # Test port release
        port_allocator.release_port(port)

        # Test new allocation after release
        new_port = port_allocator.allocate_port("test-service", 8000)
        assert new_port is not None

    async def test_port_conflict_resolution(self, setup_port_allocation):
        """Test port conflict resolution."""
        managers = await setup_port_allocation
        port_allocator = managers["port_allocator"]

        # Allocate multiple ports
        ports = []
        for i in range(5):
            port = port_allocator.allocate_port(f"service-{i}", 8000 + i)
            ports.append(port)
            assert port is not None

        # Verify all ports are unique
        assert len(set(ports)) == len(ports)

        # Clean up
        for port in ports:
            port_allocator.release_port(port)

    async def test_port_registry_persistence(self, setup_port_allocation):
        """Test port registry persistence."""
        managers = await setup_port_allocation
        port_registry = managers["port_registry"]
        port_allocator = managers["port_allocator"]

        # Allocate a port
        port = port_allocator.allocate_port("persistent-service", 8000)
        assert port is not None

        # Verify port is in registry
        entries = port_registry.get_all_entries()
        assert len(entries) > 0

        # Find our entry
        our_entry = None
        for entry_id, entry in entries.items():
            if entry.get("service") == "persistent-service":
                our_entry = entry
                break

        assert our_entry is not None
        assert our_entry["port"] == port


class TestProxyMappingSmoke:
    """Smoke tests for proxy mapping functionality."""

    @pytest.fixture
    async def setup_proxy_mapping(self):
        """Set up proxy mapping for testing."""
        proxy_server = ProxyServer()
        fallback_server = FallbackServer()

        return {
            "proxy_server": proxy_server,
            "fallback_server": fallback_server,
        }

    async def test_proxy_server_initialization(self, setup_proxy_mapping):
        """Test proxy server initialization."""
        managers = await setup_proxy_mapping
        proxy_server = managers["proxy_server"]

        # Test proxy server can be initialized
        assert proxy_server is not None

        # Test basic configuration
        config = proxy_server.get_config()
        assert config is not None

    async def test_fallback_server_initialization(self, setup_proxy_mapping):
        """Test fallback server initialization."""
        managers = await setup_proxy_mapping
        fallback_server = managers["fallback_server"]

        # Test fallback server can be initialized
        assert fallback_server is not None

        # Test basic configuration
        config = fallback_server.get_config()
        assert config is not None

    async def test_proxy_routing_configuration(self, setup_proxy_mapping):
        """Test proxy routing configuration."""
        managers = await setup_proxy_mapping
        proxy_server = managers["proxy_server"]

        # Test adding a route
        route_added = proxy_server.add_route(
            path="/test", target_host="localhost", target_port=8000
        )
        assert route_added is True

        # Test getting routes
        routes = proxy_server.get_routes()
        assert len(routes) > 0

        # Test removing a route
        route_removed = proxy_server.remove_route("/test")
        assert route_removed is True


class TestResourceReuseSmoke:
    """Smoke tests for resource reuse functionality."""

    @pytest.fixture
    async def setup_resource_reuse(self):
        """Set up resource reuse for testing."""
        deployment_manager = DeploymentManager()
        resource_coordinator = ResourceCoordinator(deployment_manager)
        global_registry = GlobalResourceRegistry()

        await resource_coordinator.initialize()

        return {
            "deployment_manager": deployment_manager,
            "resource_coordinator": resource_coordinator,
            "global_registry": global_registry,
        }

    async def test_global_resource_deployment(self, setup_resource_reuse):
        """Test global resource deployment."""
        managers = await setup_resource_reuse
        deployment_manager = managers["deployment_manager"]
        global_registry = managers["global_registry"]

        # Deploy a global resource
        resource = await deployment_manager.deploy_resource(
            name="test-redis",
            resource_type="redis",
            mode="global",
            config={"host": "localhost", "port": 6379, "db": 0},
        )
        assert resource is not None

        # Register in global registry
        await global_registry.register_resource(
            name="test-redis",
            resource_type="redis",
            config={"host": "localhost", "port": 6379, "db": 0},
            metadata={"shared": True, "projects": ["test-project"]},
        )

        # Verify resource is available
        registered_resource = await global_registry.get_resource("test-redis")
        assert registered_resource is not None
        assert registered_resource.metadata["shared"] is True

    async def test_resource_coordination(self, setup_resource_reuse):
        """Test resource coordination."""
        managers = await setup_resource_reuse
        resource_coordinator = managers["resource_coordinator"]

        # Test resource coordination is initialized
        assert resource_coordinator is not None

        # Test resource discovery
        resources = await resource_coordinator.discover_resources()
        assert isinstance(resources, list)

    async def test_resource_reuse_across_projects(self, setup_resource_reuse):
        """Test resource reuse across projects."""
        managers = await setup_resource_reuse
        global_registry = managers["global_registry"]

        # Register a shared resource
        await global_registry.register_resource(
            name="shared-db",
            resource_type="postgres",
            config={"host": "localhost", "port": 5432, "database": "shared"},
            metadata={"shared": True, "projects": ["project-a", "project-b"]},
        )

        # Test both projects can access the resource
        for project in ["project-a", "project-b"]:
            resource = await global_registry.get_resource("shared-db")
            assert resource is not None
            assert project in resource.metadata["projects"]


class TestProcessGovernanceSmoke:
    """Smoke tests for process governance functionality."""

    @pytest.fixture
    async def setup_process_governance(self):
        """Set up process governance for testing."""
        process_manager = ProcessGovernanceManager()

        return {
            "process_manager": process_manager,
        }

    async def test_process_registration(self, setup_process_governance):
        """Test process registration."""
        managers = await setup_process_governance
        process_manager = managers["process_manager"]

        # Register a test process
        metadata = ProcessMetadata(
            project="test-project",
            service="test-service",
            pid=12345,
            command_line=["python", "test.py"],
            environment={"TEST": "true"},
            scope="local",
            resource_type="test",
            tags={"smoke", "test"},
        )

        process_manager.register_process(12345, metadata)

        # Verify process is registered
        project_processes = process_manager.get_project_processes("test-project")
        assert len(project_processes) == 1
        assert project_processes[0].pid == 12345
        assert project_processes[0].service == "test-service"

    async def test_process_cleanup(self, setup_process_governance):
        """Test process cleanup."""
        managers = await setup_process_governance
        process_manager = managers["process_manager"]

        # Register a test process
        metadata = ProcessMetadata(
            project="test-project",
            service="test-service",
            pid=12346,
            command_line=["python", "test.py"],
            environment={"TEST": "true"},
            scope="local",
            resource_type="test",
            tags={"smoke", "test"},
        )

        process_manager.register_process(12346, metadata)

        # Clean up processes for the project
        stats = process_manager.cleanup_project_processes("test-project")
        assert stats["terminated"] == 1
        assert stats["skipped"] == 0

        # Verify process is no longer registered
        project_processes = process_manager.get_project_processes("test-project")
        assert len(project_processes) == 0

    async def test_process_statistics(self, setup_process_governance):
        """Test process statistics."""
        managers = await setup_process_governance
        process_manager = managers["process_manager"]

        # Get process statistics
        stats = process_manager.get_cleanup_stats()
        assert isinstance(stats, dict)
        assert "total_processes" in stats
        assert "active_processes" in stats


class TestTunnelGovernanceSmoke:
    """Smoke tests for tunnel governance functionality."""

    @pytest.fixture
    async def setup_tunnel_governance(self):
        """Set up tunnel governance for testing."""
        tunnel_manager = TunnelGovernanceManager()

        return {
            "tunnel_manager": tunnel_manager,
        }

    async def test_tunnel_creation(self, setup_tunnel_governance):
        """Test tunnel creation."""
        managers = await setup_tunnel_governance
        tunnel_manager = managers["tunnel_manager"]

        # Create a test tunnel
        tunnel = tunnel_manager.create_tunnel(
            project="test-project",
            service="test-service",
            port=8000,
            provider="cloudflare",
            reuse_existing=False,
        )

        assert tunnel is not None
        assert tunnel.project == "test-project"
        assert tunnel.service == "test-service"
        assert tunnel.port == 8000
        assert tunnel.provider == "cloudflare"

    async def test_tunnel_reuse(self, setup_tunnel_governance):
        """Test tunnel reuse."""
        managers = await setup_tunnel_governance
        tunnel_manager = managers["tunnel_manager"]

        # Create a tunnel
        tunnel1 = tunnel_manager.create_tunnel(
            project="test-project",
            service="test-service",
            port=8000,
            provider="cloudflare",
            reuse_existing=False,
        )

        # Try to create the same tunnel with reuse
        tunnel2 = tunnel_manager.create_tunnel(
            project="test-project",
            service="test-service",
            port=8000,
            provider="cloudflare",
            reuse_existing=True,
        )

        # Should reuse the existing tunnel
        assert tunnel2.tunnel_id == tunnel1.tunnel_id

    async def test_tunnel_cleanup(self, setup_tunnel_governance):
        """Test tunnel cleanup."""
        managers = await setup_tunnel_governance
        tunnel_manager = managers["tunnel_manager"]

        # Create a tunnel
        tunnel = tunnel_manager.create_tunnel(
            project="test-project",
            service="test-service",
            port=8000,
            provider="cloudflare",
            reuse_existing=False,
        )

        # Clean up tunnels for the project
        cleanup_count = tunnel_manager.cleanup_project_tunnels("test-project")
        assert cleanup_count == 1

        # Verify tunnel is no longer active
        project_tunnels = tunnel_manager.get_project_tunnels("test-project")
        assert len(project_tunnels) == 0

    async def test_tunnel_statistics(self, setup_tunnel_governance):
        """Test tunnel statistics."""
        managers = await setup_tunnel_governance
        tunnel_manager = managers["tunnel_manager"]

        # Get tunnel statistics
        stats = tunnel_manager.get_tunnel_stats()
        assert isinstance(stats, dict)
        assert "total_tunnels" in stats
        assert "active_tunnels" in stats


class TestCleanupPolicySmoke:
    """Smoke tests for cleanup policy functionality."""

    @pytest.fixture
    async def setup_cleanup_policies(self):
        """Set up cleanup policies for testing."""
        cleanup_manager = CleanupPolicyManager()

        return {
            "cleanup_manager": cleanup_manager,
        }

    async def test_cleanup_policy_creation(self, setup_cleanup_policies):
        """Test cleanup policy creation."""
        managers = await setup_cleanup_policies
        cleanup_manager = managers["cleanup_manager"]

        # Create a cleanup policy
        policy = cleanup_manager.create_default_policy(
            project_name="test-project", strategy=CleanupStrategy.MODERATE
        )

        assert policy is not None
        assert policy.project_name == "test-project"
        assert policy.default_strategy == CleanupStrategy.MODERATE

    async def test_cleanup_rule_management(self, setup_cleanup_policies):
        """Test cleanup rule management."""
        managers = await setup_cleanup_policies
        cleanup_manager = managers["cleanup_manager"]

        # Create a policy
        policy = cleanup_manager.create_default_policy(
            project_name="test-project", strategy=CleanupStrategy.MODERATE
        )

        # Update a cleanup rule
        cleanup_manager.update_project_rule(
            project_name="test-project",
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.AGGRESSIVE,
            patterns=["test-project-*"],
            max_age=1800.0,
            force_cleanup=True,
        )

        # Verify rule was updated
        updated_policy = cleanup_manager.get_project_policy("test-project")
        assert updated_policy is not None
        assert ResourceType.PROCESS in updated_policy.rules
        assert updated_policy.rules[ResourceType.PROCESS].strategy == CleanupStrategy.AGGRESSIVE

    async def test_global_cleanup_policy(self, setup_cleanup_policies):
        """Test global cleanup policy."""
        managers = await setup_cleanup_policies
        cleanup_manager = managers["cleanup_manager"]

        # Get global cleanup policy
        global_policy = cleanup_manager.get_global_policy()
        assert global_policy is not None
        assert global_policy.default_strategy is not None
        assert global_policy.max_concurrent_cleanups > 0


class TestStatusMonitoringSmoke:
    """Smoke tests for status monitoring functionality."""

    @pytest.fixture
    async def setup_status_monitoring(self):
        """Set up status monitoring for testing."""
        status_manager = StatusPageManager()

        return {
            "status_manager": status_manager,
        }

    async def test_service_status_update(self, setup_status_monitoring):
        """Test service status update."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        # Update service status
        status_manager.update_service_status(
            project_name="test-project",
            service_name="test-service",
            status="running",
            port=8000,
            health_status="healthy",
        )

        # Verify status was updated
        project_status = status_manager.get_project_status("test-project")
        assert project_status is not None
        assert "test-service" in project_status.services
        assert project_status.services["test-service"].status == "running"
        assert project_status.services["test-service"].health_status == "healthy"

    async def test_tunnel_status_update(self, setup_status_monitoring):
        """Test tunnel status update."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        # Update tunnel status
        status_manager.update_tunnel_status(
            project_name="test-project",
            service_name="test-service",
            status="active",
            hostname="test.example.com",
            provider="cloudflare",
        )

        # Verify status was updated
        project_status = status_manager.get_project_status("test-project")
        assert project_status is not None
        assert "test-service" in project_status.tunnels
        assert project_status.tunnels["test-service"].status == "active"
        assert project_status.tunnels["test-service"].hostname == "test.example.com"

    async def test_status_page_generation(self, setup_status_monitoring):
        """Test status page generation."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        # Update some status
        status_manager.update_service_status(
            project_name="test-project",
            service_name="test-service",
            status="running",
            port=8000,
            health_status="healthy",
        )

        # Generate status page
        status_page = status_manager.generate_status_page("test-project", "status")
        assert status_page is not None
        assert "test-project" in status_page
        assert "test-service" in status_page

    async def test_project_summary_generation(self, setup_status_monitoring):
        """Test project summary generation."""
        managers = await setup_status_monitoring
        status_manager = managers["status_manager"]

        # Update some status
        status_manager.update_service_status(
            project_name="test-project",
            service_name="test-service",
            status="running",
            port=8000,
            health_status="healthy",
        )

        # Generate project summary
        summary = status_manager.generate_project_summary("test-project")
        assert summary is not None
        assert "test-project" in summary


class TestIntegrationSmoke:
    """Smoke tests for integrated functionality."""

    @pytest.fixture
    async def setup_integration(self):
        """Set up integration testing."""
        config_manager = KInfraConfigManager()
        process_manager = ProcessGovernanceManager()
        tunnel_manager = TunnelGovernanceManager()
        cleanup_manager = CleanupPolicyManager()
        status_manager = StatusPageManager()

        return {
            "config_manager": config_manager,
            "process_manager": process_manager,
            "tunnel_manager": tunnel_manager,
            "cleanup_manager": cleanup_manager,
            "status_manager": status_manager,
        }

    async def test_project_lifecycle(self, setup_integration):
        """Test complete project lifecycle."""
        managers = await setup_integration
        config_manager = managers["config_manager"]
        process_manager = managers["process_manager"]
        tunnel_manager = managers["tunnel_manager"]
        cleanup_manager = managers["cleanup_manager"]
        status_manager = managers["status_manager"]

        project_name = "smoke-test-project"

        # Set up project configuration
        project_config = create_default_project_config(project_name)
        config_manager.set_project_config(project_name, project_config)

        # Set up cleanup policy
        cleanup_policy = cleanup_manager.create_default_policy(
            project_name=project_name, strategy=CleanupStrategy.MODERATE
        )
        cleanup_manager.set_project_policy(project_name, cleanup_policy)

        # Register a process
        metadata = ProcessMetadata(
            project=project_name,
            service="test-service",
            pid=12347,
            command_line=["python", "test.py"],
            environment={"PROJECT": project_name},
            scope="local",
            resource_type="test",
            tags={"smoke", "test"},
        )
        process_manager.register_process(12347, metadata)

        # Create a tunnel
        tunnel = tunnel_manager.create_tunnel(
            project=project_name,
            service="test-service",
            port=8000,
            provider="cloudflare",
            reuse_existing=False,
        )

        # Update status
        status_manager.update_service_status(
            project_name=project_name,
            service_name="test-service",
            status="running",
            port=8000,
            health_status="healthy",
        )

        # Verify everything is set up
        project_processes = process_manager.get_project_processes(project_name)
        assert len(project_processes) == 1

        project_tunnels = tunnel_manager.get_project_tunnels(project_name)
        assert len(project_tunnels) == 1

        project_status = status_manager.get_project_status(project_name)
        assert project_status is not None
        assert "test-service" in project_status.services

        # Clean up
        process_manager.cleanup_project_processes(project_name)
        tunnel_manager.cleanup_project_tunnels(project_name)

        # Verify cleanup
        project_processes = process_manager.get_project_processes(project_name)
        assert len(project_processes) == 0

        project_tunnels = tunnel_manager.get_project_tunnels(project_name)
        assert len(project_tunnels) == 0

    async def test_multi_project_isolation(self, setup_integration):
        """Test multi-project isolation."""
        managers = await setup_integration
        process_manager = managers["process_manager"]
        tunnel_manager = managers["tunnel_manager"]

        projects = ["project-a", "project-b", "project-c"]

        # Set up processes and tunnels for each project
        for project in projects:
            # Register process
            metadata = ProcessMetadata(
                project=project,
                service=f"{project}-service",
                pid=12348 + hash(project) % 1000,
                command_line=["python", f"{project}.py"],
                environment={"PROJECT": project},
                scope="local",
                resource_type="test",
                tags={"smoke", "test"},
            )
            process_manager.register_process(metadata.pid, metadata)

            # Create tunnel
            tunnel_manager.create_tunnel(
                project=project,
                service=f"{project}-service",
                port=8000 + hash(project) % 1000,
                provider="cloudflare",
                reuse_existing=False,
            )

        # Verify isolation - clean up one project shouldn't affect others
        process_manager.cleanup_project_processes("project-a")
        tunnel_manager.cleanup_project_tunnels("project-a")

        # Check that other projects are unaffected
        for project in ["project-b", "project-c"]:
            project_processes = process_manager.get_project_processes(project)
            project_tunnels = tunnel_manager.get_project_tunnels(project)
            assert len(project_processes) == 1
            assert len(project_tunnels) == 1

        # Clean up remaining projects
        for project in ["project-b", "project-c"]:
            process_manager.cleanup_project_processes(project)
            tunnel_manager.cleanup_project_tunnels(project)


# Smoke test runner
async def run_smoke_tests():
    """Run all smoke tests."""
    print("🚀 Running KInfra Smoke Tests...")

    # Test port allocation
    print("📋 Testing port allocation...")
    test_port = TestPortAllocationSmoke()
    await test_port.test_basic_port_allocation()
    await test_port.test_port_conflict_resolution()
    await test_port.test_port_registry_persistence()
    print("✅ Port allocation tests passed")

    # Test proxy mapping
    print("🌐 Testing proxy mapping...")
    test_proxy = TestProxyMappingSmoke()
    await test_proxy.test_proxy_server_initialization()
    await test_proxy.test_fallback_server_initialization()
    await test_proxy.test_proxy_routing_configuration()
    print("✅ Proxy mapping tests passed")

    # Test resource reuse
    print("🏗️ Testing resource reuse...")
    test_resource = TestResourceReuseSmoke()
    await test_resource.test_global_resource_deployment()
    await test_resource.test_resource_coordination()
    await test_resource.test_resource_reuse_across_projects()
    print("✅ Resource reuse tests passed")

    # Test process governance
    print("📋 Testing process governance...")
    test_process = TestProcessGovernanceSmoke()
    await test_process.test_process_registration()
    await test_process.test_process_cleanup()
    await test_process.test_process_statistics()
    print("✅ Process governance tests passed")

    # Test tunnel governance
    print("🌐 Testing tunnel governance...")
    test_tunnel = TestTunnelGovernanceSmoke()
    await test_tunnel.test_tunnel_creation()
    await test_tunnel.test_tunnel_reuse()
    await test_tunnel.test_tunnel_cleanup()
    await test_tunnel.test_tunnel_statistics()
    print("✅ Tunnel governance tests passed")

    # Test cleanup policies
    print("🧹 Testing cleanup policies...")
    test_cleanup = TestCleanupPolicySmoke()
    await test_cleanup.test_cleanup_policy_creation()
    await test_cleanup.test_cleanup_rule_management()
    await test_cleanup.test_global_cleanup_policy()
    print("✅ Cleanup policies tests passed")

    # Test status monitoring
    print("📊 Testing status monitoring...")
    test_status = TestStatusMonitoringSmoke()
    await test_status.test_service_status_update()
    await test_status.test_tunnel_status_update()
    await test_status.test_status_page_generation()
    await test_status.test_project_summary_generation()
    print("✅ Status monitoring tests passed")

    # Test integration
    print("🔗 Testing integration...")
    test_integration = TestIntegrationSmoke()
    await test_integration.test_project_lifecycle()
    await test_integration.test_multi_project_isolation()
    print("✅ Integration tests passed")

    print("🎉 All smoke tests passed!")


if __name__ == "__main__":
    asyncio.run(run_smoke_tests())
