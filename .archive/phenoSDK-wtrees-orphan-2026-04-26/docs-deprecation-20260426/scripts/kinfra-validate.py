#!/usr/bin/env python3
"""
KInfra Validation Script: Phase 5 Component Health and Functionality

This script validates the health and functionality of all Phase 5 components,
ensuring they work correctly in production environments.

Usage:
    python scripts/kinfra-validate.py [options]

Options:
    --component COMPONENT    Validate specific component (process, tunnel, cleanup, status, config)
    --all                    Validate all components (default)
    --health-check           Run health checks
    --functionality-test     Run functionality tests
    --performance-test       Run performance tests
    --verbose                Verbose output
    --json                   Output results as JSON
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.infra.config_schemas import KInfraConfigManager
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.port_allocator import SmartPortAllocator
from pheno.infra.port_registry import PortRegistry


class KInfraValidator:
    """KInfra Phase 5 component validator."""

    def __init__(self, verbose: bool = False):
        """Initialize the validator."""
        self.verbose = verbose
        self.results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

        # Initialize managers
        self.config_manager = KInfraConfigManager()
        self.process_manager = ProcessGovernanceManager()
        self.tunnel_manager = TunnelGovernanceManager()
        self.cleanup_manager = CleanupPolicyManager()
        self.status_manager = StatusPageManager()
        self.deployment_manager = DeploymentManager()
        self.resource_coordinator = ResourceCoordinator(self.deployment_manager)
        self.global_registry = GlobalResourceRegistry()
        self.port_allocator = SmartPortAllocator()
        self.port_registry = PortRegistry()

        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO, format="%(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def add_error(self, component: str, message: str):
        """Add an error to the results."""
        self.errors.append(f"{component}: {message}")
        if self.verbose:
            self.logger.error(f"ERROR [{component}]: {message}")

    def add_warning(self, component: str, message: str):
        """Add a warning to the results."""
        self.warnings.append(f"{component}: {message}")
        if self.verbose:
            self.logger.warning(f"WARNING [{component}]: {message}")

    def add_result(
        self, component: str, test: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """Add a test result."""
        if component not in self.results:
            self.results[component] = {}

        self.results[component][test] = {
            "status": status,
            "details": details or {},
            "timestamp": time.time(),
        }

        if self.verbose:
            self.logger.info(f"RESULT [{component}][{test}]: {status}")

    async def validate_configuration(self) -> bool:
        """Validate configuration management."""
        self.logger.info("Validating configuration management...")
        component = "configuration"
        all_passed = True

        try:
            # Test configuration loading
            config = self.config_manager.load()
            if config is None:
                self.add_error(component, "Failed to load configuration")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "config_loading",
                    "PASS",
                    {
                        "app_name": config.app_name,
                        "debug": config.debug,
                        "log_level": config.log_level,
                    },
                )

            # Test project configuration
            test_project = "validation-test-project"
            project_config = self.config_manager.get_project_config(test_project)
            if project_config is None:
                self.add_warning(component, f"Project {test_project} not configured")
            else:
                self.add_result(
                    component,
                    "project_config",
                    "PASS",
                    {
                        "project_name": project_config.project_name,
                        "default_strategy": project_config.default_strategy,
                    },
                )

            # Test configuration export/import
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                self.config_manager.save_config(config, Path(f.name))
                new_config_manager = KInfraConfigManager(f.name)
                new_config = new_config_manager.load()

                if new_config.app_name != config.app_name:
                    self.add_error(component, "Configuration export/import failed")
                    all_passed = False
                else:
                    self.add_result(component, "config_export_import", "PASS")

            if all_passed:
                self.logger.info("✅ Configuration validation passed")
            else:
                self.logger.warning("❌ Configuration validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Configuration validation failed: {e}")
            return False

    async def validate_process_governance(self) -> bool:
        """Validate process governance functionality."""
        self.logger.info("Validating process governance...")
        component = "process_governance"
        all_passed = True

        try:
            # Test process registration
            test_pid = 99999  # Use a high PID that's unlikely to conflict
            metadata = ProcessMetadata(
                project="validation-test",
                service="test-service",
                pid=test_pid,
                command_line=["python", "test.py"],
                environment={"TEST": "true"},
                scope="local",
                resource_type="test",
                tags={"validation", "test"},
            )

            self.process_manager.register_process(test_pid, metadata)
            project_processes = self.process_manager.get_project_processes("validation-test")

            if len(project_processes) != 1:
                self.add_error(component, "Process registration failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "process_registration",
                    "PASS",
                    {"pid": test_pid, "project": "validation-test", "service": "test-service"},
                )

            # Test process statistics
            stats = self.process_manager.get_cleanup_stats()
            if not isinstance(stats, dict):
                self.add_error(component, "Process statistics not available")
                all_passed = False
            else:
                self.add_result(component, "process_statistics", "PASS", stats)

            # Test process cleanup
            cleanup_stats = self.process_manager.cleanup_project_processes("validation-test")
            if cleanup_stats["terminated"] != 1:
                self.add_error(component, "Process cleanup failed")
                all_passed = False
            else:
                self.add_result(component, "process_cleanup", "PASS", cleanup_stats)

            # Verify cleanup worked
            project_processes = self.process_manager.get_project_processes("validation-test")
            if len(project_processes) != 0:
                self.add_warning(component, "Process cleanup may not have worked completely")

            if all_passed:
                self.logger.info("✅ Process governance validation passed")
            else:
                self.logger.warning("❌ Process governance validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Process governance validation failed: {e}")
            return False

    async def validate_tunnel_governance(self) -> bool:
        """Validate tunnel governance functionality."""
        self.logger.info("Validating tunnel governance...")
        component = "tunnel_governance"
        all_passed = True

        try:
            # Test tunnel creation
            tunnel = self.tunnel_manager.create_tunnel(
                project="validation-test",
                service="test-service",
                port=8000,
                provider="cloudflare",
                reuse_existing=False,
            )

            if tunnel is None:
                self.add_error(component, "Tunnel creation failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "tunnel_creation",
                    "PASS",
                    {
                        "tunnel_id": tunnel.tunnel_id,
                        "project": tunnel.project,
                        "service": tunnel.service,
                        "port": tunnel.port,
                        "provider": tunnel.provider,
                    },
                )

            # Test tunnel reuse
            reused_tunnel = self.tunnel_manager.create_tunnel(
                project="validation-test",
                service="test-service",
                port=8000,
                provider="cloudflare",
                reuse_existing=True,
            )

            if reused_tunnel.tunnel_id != tunnel.tunnel_id:
                self.add_error(component, "Tunnel reuse failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "tunnel_reuse",
                    "PASS",
                    {
                        "original_tunnel_id": tunnel.tunnel_id,
                        "reused_tunnel_id": reused_tunnel.tunnel_id,
                    },
                )

            # Test tunnel statistics
            stats = self.tunnel_manager.get_tunnel_stats()
            if not isinstance(stats, dict):
                self.add_error(component, "Tunnel statistics not available")
                all_passed = False
            else:
                self.add_result(component, "tunnel_statistics", "PASS", stats)

            # Test tunnel cleanup
            cleanup_count = self.tunnel_manager.cleanup_project_tunnels("validation-test")
            if cleanup_count != 1:
                self.add_error(component, "Tunnel cleanup failed")
                all_passed = False
            else:
                self.add_result(
                    component, "tunnel_cleanup", "PASS", {"cleanup_count": cleanup_count}
                )

            # Verify cleanup worked
            project_tunnels = self.tunnel_manager.get_project_tunnels("validation-test")
            if len(project_tunnels) != 0:
                self.add_warning(component, "Tunnel cleanup may not have worked completely")

            if all_passed:
                self.logger.info("✅ Tunnel governance validation passed")
            else:
                self.logger.warning("❌ Tunnel governance validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Tunnel governance validation failed: {e}")
            return False

    async def validate_cleanup_policies(self) -> bool:
        """Validate cleanup policy functionality."""
        self.logger.info("Validating cleanup policies...")
        component = "cleanup_policies"
        all_passed = True

        try:
            # Test cleanup policy creation
            test_project = "validation-test"
            policy = self.cleanup_manager.create_default_policy(
                project_name=test_project, strategy=CleanupStrategy.MODERATE
            )

            if policy is None:
                self.add_error(component, "Cleanup policy creation failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "policy_creation",
                    "PASS",
                    {
                        "project_name": policy.project_name,
                        "default_strategy": policy.default_strategy,
                    },
                )

            # Test cleanup rule management
            self.cleanup_manager.update_project_rule(
                project_name=test_project,
                resource_type=ResourceType.PROCESS,
                strategy=CleanupStrategy.AGGRESSIVE,
                patterns=[f"{test_project}-*"],
                max_age=1800.0,
                force_cleanup=True,
            )

            updated_policy = self.cleanup_manager.get_project_policy(test_project)
            if updated_policy is None:
                self.add_error(component, "Cleanup policy retrieval failed")
                all_passed = False
            elif ResourceType.PROCESS not in updated_policy.rules:
                self.add_error(component, "Cleanup rule not found")
                all_passed = False
            elif updated_policy.rules[ResourceType.PROCESS].strategy != CleanupStrategy.AGGRESSIVE:
                self.add_error(component, "Cleanup rule update failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "rule_management",
                    "PASS",
                    {
                        "resource_type": ResourceType.PROCESS,
                        "strategy": CleanupStrategy.AGGRESSIVE,
                        "patterns": [f"{test_project}-*"],
                        "max_age": 1800.0,
                        "force_cleanup": True,
                    },
                )

            # Test global cleanup policy
            global_policy = self.cleanup_manager.get_global_policy()
            if global_policy is None:
                self.add_error(component, "Global cleanup policy not available")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "global_policy",
                    "PASS",
                    {
                        "default_strategy": global_policy.default_strategy,
                        "max_concurrent_cleanups": global_policy.max_concurrent_cleanups,
                        "cleanup_timeout": global_policy.cleanup_timeout,
                        "enabled": global_policy.enabled,
                    },
                )

            if all_passed:
                self.logger.info("✅ Cleanup policies validation passed")
            else:
                self.logger.warning("❌ Cleanup policies validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Cleanup policies validation failed: {e}")
            return False

    async def validate_status_monitoring(self) -> bool:
        """Validate status monitoring functionality."""
        self.logger.info("Validating status monitoring...")
        component = "status_monitoring"
        all_passed = True

        try:
            # Test service status update
            self.status_manager.update_service_status(
                project_name="validation-test",
                service_name="test-service",
                status="running",
                port=8000,
                health_status="healthy",
            )

            project_status = self.status_manager.get_project_status("validation-test")
            if project_status is None:
                self.add_error(component, "Project status not available")
                all_passed = False
            elif "test-service" not in project_status.services:
                self.add_error(component, "Service status not found")
                all_passed = False
            else:
                service_status = project_status.services["test-service"]
                self.add_result(
                    component,
                    "service_status_update",
                    "PASS",
                    {
                        "status": service_status.status,
                        "health_status": service_status.health_status,
                        "port": service_status.port,
                    },
                )

            # Test tunnel status update
            self.status_manager.update_tunnel_status(
                project_name="validation-test",
                service_name="test-service",
                status="active",
                hostname="test.example.com",
                provider="cloudflare",
            )

            project_status = self.status_manager.get_project_status("validation-test")
            if project_status is None:
                self.add_error(component, "Project status not available after tunnel update")
                all_passed = False
            elif "test-service" not in project_status.tunnels:
                self.add_error(component, "Tunnel status not found")
                all_passed = False
            else:
                tunnel_status = project_status.tunnels["test-service"]
                self.add_result(
                    component,
                    "tunnel_status_update",
                    "PASS",
                    {
                        "status": tunnel_status.status,
                        "hostname": tunnel_status.hostname,
                        "provider": tunnel_status.provider,
                    },
                )

            # Test status page generation
            status_page = self.status_manager.generate_status_page("validation-test", "status")
            if status_page is None:
                self.add_error(component, "Status page generation failed")
                all_passed = False
            elif "validation-test" not in status_page:
                self.add_error(component, "Status page content invalid")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "status_page_generation",
                    "PASS",
                    {
                        "page_length": len(status_page),
                        "contains_project": "validation-test" in status_page,
                    },
                )

            # Test project summary generation
            summary = self.status_manager.generate_project_summary("validation-test")
            if summary is None:
                self.add_error(component, "Project summary generation failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "project_summary_generation",
                    "PASS",
                    {
                        "summary_length": len(summary),
                        "contains_project": "validation-test" in summary,
                    },
                )

            if all_passed:
                self.logger.info("✅ Status monitoring validation passed")
            else:
                self.logger.warning("❌ Status monitoring validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Status monitoring validation failed: {e}")
            return False

    async def validate_resource_coordination(self) -> bool:
        """Validate resource coordination functionality."""
        self.logger.info("Validating resource coordination...")
        component = "resource_coordination"
        all_passed = True

        try:
            # Initialize resource coordination
            await self.resource_coordinator.initialize()
            self.add_result(component, "initialization", "PASS")

            # Test resource deployment
            test_resource = await self.deployment_manager.deploy_resource(
                name="validation-test-resource",
                resource_type="redis",
                mode="global",
                config={"host": "localhost", "port": 6379, "db": 0},
            )

            if test_resource is None:
                self.add_error(component, "Resource deployment failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "resource_deployment",
                    "PASS",
                    {"resource_name": "validation-test-resource", "resource_type": "redis"},
                )

            # Test global registry
            await self.global_registry.register_resource(
                name="validation-test-registry",
                resource_type="postgres",
                config={"host": "localhost", "port": 5432, "database": "test"},
                metadata={"shared": True, "projects": ["validation-test"]},
            )

            registered_resource = await self.global_registry.get_resource(
                "validation-test-registry"
            )
            if registered_resource is None:
                self.add_error(component, "Global registry registration failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "global_registry",
                    "PASS",
                    {
                        "resource_name": "validation-test-registry",
                        "resource_type": "postgres",
                        "shared": registered_resource.metadata.get("shared", False),
                    },
                )

            # Test resource discovery
            resources = await self.resource_coordinator.discover_resources()
            if not isinstance(resources, list):
                self.add_error(component, "Resource discovery failed")
                all_passed = False
            else:
                self.add_result(
                    component, "resource_discovery", "PASS", {"resource_count": len(resources)}
                )

            if all_passed:
                self.logger.info("✅ Resource coordination validation passed")
            else:
                self.logger.warning("❌ Resource coordination validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Resource coordination validation failed: {e}")
            return False

    async def validate_port_allocation(self) -> bool:
        """Validate port allocation functionality."""
        self.logger.info("Validating port allocation...")
        component = "port_allocation"
        all_passed = True

        try:
            # Test port allocation
            port = self.port_allocator.allocate_port("validation-test", 8000)
            if port is None:
                self.add_error(component, "Port allocation failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "port_allocation",
                    "PASS",
                    {"port": port, "service": "validation-test"},
                )

            # Test port reuse
            reused_port = self.port_allocator.allocate_port("validation-test", 8000)
            if reused_port != port:
                self.add_error(component, "Port reuse failed")
                all_passed = False
            else:
                self.add_result(
                    component,
                    "port_reuse",
                    "PASS",
                    {"original_port": port, "reused_port": reused_port},
                )

            # Test port release
            self.port_allocator.release_port(port)
            self.add_result(component, "port_release", "PASS", {"released_port": port})

            # Test port registry
            entries = self.port_registry.get_all_entries()
            if not isinstance(entries, dict):
                self.add_error(component, "Port registry not available")
                all_passed = False
            else:
                self.add_result(component, "port_registry", "PASS", {"entry_count": len(entries)})

            if all_passed:
                self.logger.info("✅ Port allocation validation passed")
            else:
                self.logger.warning("❌ Port allocation validation failed")

            return all_passed

        except Exception as e:
            self.add_error(component, f"Port allocation validation failed: {e}")
            return False

    async def run_health_checks(self) -> Dict[str, Any]:
        """Run health checks for all components."""
        self.logger.info("Running health checks...")
        health_results = {}

        try:
            # Configuration health
            config = self.config_manager.load()
            health_results["configuration"] = {
                "status": "healthy" if config else "unhealthy",
                "details": {"app_name": config.app_name if config else None},
            }

            # Process governance health
            process_stats = self.process_manager.get_cleanup_stats()
            health_results["process_governance"] = {
                "status": "healthy" if isinstance(process_stats, dict) else "unhealthy",
                "details": process_stats,
            }

            # Tunnel governance health
            tunnel_stats = self.tunnel_manager.get_tunnel_stats()
            health_results["tunnel_governance"] = {
                "status": "healthy" if isinstance(tunnel_stats, dict) else "unhealthy",
                "details": tunnel_stats,
            }

            # Cleanup policies health
            global_policy = self.cleanup_manager.get_global_policy()
            health_results["cleanup_policies"] = {
                "status": "healthy" if global_policy else "unhealthy",
                "details": {"enabled": global_policy.enabled if global_policy else False},
            }

            # Status monitoring health
            all_projects = self.status_manager.get_all_projects()
            health_results["status_monitoring"] = {
                "status": "healthy" if isinstance(all_projects, list) else "unhealthy",
                "details": {
                    "project_count": len(all_projects) if isinstance(all_projects, list) else 0
                },
            }

            return health_results

        except Exception as e:
            self.add_error("health_checks", f"Health checks failed: {e}")
            return {"error": str(e)}

    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests for all components."""
        self.logger.info("Running performance tests...")
        performance_results = {}

        try:
            # Process governance performance
            start_time = time.time()
            for i in range(100):
                metadata = ProcessMetadata(
                    project="perf-test",
                    service=f"service-{i}",
                    pid=90000 + i,
                    command_line=["python", "test.py"],
                    environment={"TEST": "true"},
                    scope="local",
                    resource_type="test",
                    tags={"performance", "test"},
                )
                self.process_manager.register_process(90000 + i, metadata)

            process_time = time.time() - start_time
            performance_results["process_registration"] = {
                "operations": 100,
                "time_seconds": process_time,
                "ops_per_second": 100 / process_time,
            }

            # Clean up
            self.process_manager.cleanup_project_processes("perf-test")

            # Tunnel governance performance
            start_time = time.time()
            tunnels = []
            for i in range(50):
                tunnel = self.tunnel_manager.create_tunnel(
                    project="perf-test",
                    service=f"service-{i}",
                    port=8000 + i,
                    provider="cloudflare",
                    reuse_existing=False,
                )
                tunnels.append(tunnel)

            tunnel_time = time.time() - start_time
            performance_results["tunnel_creation"] = {
                "operations": 50,
                "time_seconds": tunnel_time,
                "ops_per_second": 50 / tunnel_time,
            }

            # Clean up
            self.tunnel_manager.cleanup_project_tunnels("perf-test")

            # Status monitoring performance
            start_time = time.time()
            for i in range(100):
                self.status_manager.update_service_status(
                    project_name="perf-test",
                    service_name=f"service-{i}",
                    status="running",
                    port=8000 + i,
                    health_status="healthy",
                )

            status_time = time.time() - start_time
            performance_results["status_updates"] = {
                "operations": 100,
                "time_seconds": status_time,
                "ops_per_second": 100 / status_time,
            }

            return performance_results

        except Exception as e:
            self.add_error("performance_tests", f"Performance tests failed: {e}")
            return {"error": str(e)}

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        return {
            "summary": {
                "total_components": len(self.results),
                "total_tests": sum(
                    len(component_tests) for component_tests in self.results.values()
                ),
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "overall_status": "PASS" if len(self.errors) == 0 else "FAIL",
            },
            "components": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": time.time(),
        }


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="KInfra Phase 5 Component Validator")
    parser.add_argument(
        "--component",
        choices=["process", "tunnel", "cleanup", "status", "config", "resource", "port"],
        help="Validate specific component",
    )
    parser.add_argument(
        "--all", action="store_true", default=True, help="Validate all components (default)"
    )
    parser.add_argument("--health-check", action="store_true", help="Run health checks")
    parser.add_argument("--functionality-test", action="store_true", help="Run functionality tests")
    parser.add_argument("--performance-test", action="store_true", help="Run performance tests")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Initialize validator
    validator = KInfraValidator(verbose=args.verbose)

    # Determine which validations to run
    validations = []
    if args.component:
        component_map = {
            "process": validator.validate_process_governance,
            "tunnel": validator.validate_tunnel_governance,
            "cleanup": validator.validate_cleanup_policies,
            "status": validator.validate_status_monitoring,
            "config": validator.validate_configuration,
            "resource": validator.validate_resource_coordination,
            "port": validator.validate_port_allocation,
        }
        validations.append((args.component, component_map[args.component]))
    elif args.all:
        validations = [
            ("configuration", validator.validate_configuration),
            ("process_governance", validator.validate_process_governance),
            ("tunnel_governance", validator.validate_tunnel_governance),
            ("cleanup_policies", validator.validate_cleanup_policies),
            ("status_monitoring", validator.validate_status_monitoring),
            ("resource_coordination", validator.validate_resource_coordination),
            ("port_allocation", validator.validate_port_allocation),
        ]

    # Run validations
    all_passed = True
    for component_name, validation_func in validations:
        try:
            result = await validation_func()
            if not result:
                all_passed = False
        except Exception as e:
            validator.add_error(component_name, f"Validation failed: {e}")
            all_passed = False

    # Run additional tests
    if args.health_check:
        health_results = await validator.run_health_checks()
        validator.results["health_checks"] = health_results

    if args.performance_test:
        performance_results = await validator.run_performance_tests()
        validator.results["performance_tests"] = performance_results

    # Generate report
    report = validator.generate_report()

    # Output results
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\nKInfra Phase 5 Validation Report")
        print("=" * 50)
        print(f"Overall Status: {report['summary']['overall_status']}")
        print(f"Components Validated: {report['summary']['total_components']}")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Errors: {report['summary']['total_errors']}")
        print(f"Warnings: {report['summary']['total_warnings']}")

        if report["summary"]["total_errors"] > 0:
            print(f"\nErrors:")
            for error in report["errors"]:
                print(f"  - {error}")

        if report["summary"]["total_warnings"] > 0:
            print(f"\nWarnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")

        print(f"\nComponent Results:")
        for component, tests in report["components"].items():
            print(f"  {component}:")
            for test, result in tests.items():
                print(f"    {test}: {result['status']}")

    if all_passed:
        print(f"\n✅ All validations passed!")
        sys.exit(0)
    else:
        print(f"\n❌ Some validations failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
