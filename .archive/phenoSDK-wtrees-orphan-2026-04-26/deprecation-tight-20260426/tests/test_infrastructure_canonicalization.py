"""Integration tests for infrastructure canonicalization refactoring.

This test validates that the refactored infrastructure components work correctly:
- ServiceInfraManager replaces KInfra
- Proxy/fallback modules are renamed
- Tunnel APIs are normalized
- All imports work correctly
"""

import sys
from pathlib import Path

import pytest

# Add the src directory to the path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pheno.infra.fallback_site import FallbackServer
from pheno.infra.orchestrator import OrchestratorConfig, ServiceOrchestrator
from pheno.infra.proxy_gateway import ProxyServer
from pheno.infra.service_infra import ServiceInfraManager
from pheno.infra.service_manager import ServiceManager


class TestInfrastructureCanonicalization:
    """
    Test the canonicalized infrastructure components.
    """

    def test_service_infra_manager_import(self):
        """
        Test that ServiceInfraManager can be imported and instantiated.
        """
        manager = ServiceInfraManager(domain="test.example.com")
        assert manager.domain == "test.example.com"
        assert hasattr(manager, "registry")
        assert hasattr(manager, "allocator")
        assert hasattr(manager, "tunnel_manager")

    def test_service_infra_manager_methods(self):
        """
        Test that ServiceInfraManager has the expected methods.
        """
        manager = ServiceInfraManager()

        # Test that canonical methods exist
        assert hasattr(manager, "allocate_port")
        assert hasattr(manager, "create_tunnel")
        assert hasattr(manager, "get_port")
        assert hasattr(manager, "get_info")
        assert hasattr(manager, "check_health")
        assert hasattr(manager, "cleanup")
        assert hasattr(manager, "cleanup_all")

    def test_deprecated_methods_removed(self):
        """
        Test that deprecated methods are removed from ServiceInfraManager.
        """
        manager = ServiceInfraManager()

        # These deprecated methods should not exist
        assert not hasattr(manager, "get_service_port")
        assert not hasattr(manager, "start_tunnel")
        assert not hasattr(manager, "get_service_url")
        assert not hasattr(manager, "get_service_info")
        assert not hasattr(manager, "health_check")

    def test_proxy_gateway_import(self):
        """
        Test that proxy_gateway module can be imported.
        """

        assert ProxyServer is not None

    def test_fallback_site_import(self):
        """
        Test that fallback_site module can be imported.
        """

        assert FallbackServer is not None

    def test_orchestrator_with_service_infra(self):
        """
        Test that ServiceOrchestrator works with ServiceInfraManager.
        """
        config = OrchestratorConfig(project_name="test-project")
        service_infra = ServiceInfraManager(domain="test.example.com")
        orchestrator = ServiceOrchestrator(config, service_infra)

        assert orchestrator.service_infra is not None
        assert orchestrator.service_infra.domain == "test.example.com"

    def test_service_manager_with_service_infra(self):
        """
        Test that ServiceManager works with ServiceInfraManager.
        """
        service_infra = ServiceInfraManager(domain="test.example.com")
        service_manager = ServiceManager(service_infra)

        assert service_manager is not None

    def test_port_allocation(self):
        """
        Test that port allocation works with ServiceInfraManager.
        """
        manager = ServiceInfraManager()

        # Test port allocation
        port = manager.allocate_port("test-service", preferred_port=8080)
        assert isinstance(port, int)
        assert port > 0

        # Test that the service is tracked
        assert "test-service" in manager._managed_services

        # Clean up
        manager.cleanup("test-service")

    def test_tunnel_creation(self):
        """
        Test that tunnel creation works with ServiceInfraManager.
        """
        manager = ServiceInfraManager()

        # Allocate a port first
        port = manager.allocate_port("test-service", preferred_port=8080)

        # Test tunnel creation (this might fail if cloudflared is not available)
        try:
            tunnel_info = manager.create_tunnel("test-service", port)
            assert tunnel_info is not None
            assert hasattr(tunnel_info, "hostname")
        except Exception as e:
            # If cloudflared is not available, that's okay for this test
            assert "cloudflared" in str(e).lower() or "tunnel" in str(e).lower()

        # Clean up
        manager.cleanup("test-service")

    def test_health_check(self):
        """
        Test that health checking works with ServiceInfraManager.
        """
        manager = ServiceInfraManager()

        # Test health check for non-existent service
        health = manager.check_health("non-existent-service")
        assert health["status"] == "not_found"
        assert not health["healthy"]

    def test_service_listing(self):
        """
        Test that service listing works with ServiceInfraManager.
        """
        manager = ServiceInfraManager()

        # Test listing services
        services = manager.list_services()
        assert isinstance(services, dict)

    def test_cleanup_functionality(self):
        """
        Test that cleanup functionality works with ServiceInfraManager.
        """
        manager = ServiceInfraManager()

        # Allocate a port
        port = manager.allocate_port("cleanup-test", preferred_port=8081)
        assert "cleanup-test" in manager._managed_services

        # Clean up the service
        success = manager.cleanup("cleanup-test")
        assert success
        assert "cleanup-test" not in manager._managed_services

    def test_context_manager(self):
        """
        Test that ServiceInfraManager works as a context manager.
        """
        with ServiceInfraManager(domain="context-test.example.com") as manager:
            assert manager.domain == "context-test.example.com"
            port = manager.allocate_port("context-test-service")
            assert port > 0
        # After exiting the context, cleanup should have been called


if __name__ == "__main__":
    pytest.main([__file__])
