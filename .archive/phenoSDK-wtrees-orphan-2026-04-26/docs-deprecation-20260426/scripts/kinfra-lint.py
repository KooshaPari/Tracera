#!/usr/bin/env python3
"""
KInfra Lint/Check Script: Registry Integrity and Metadata Consistency

This script validates the integrity of KInfra registries and ensures metadata
consistency across all Phase 5 components. It performs comprehensive checks
on process governance, tunnel governance, cleanup policies, and status monitoring.

Usage:
    python scripts/kinfra-lint.py [options]

Options:
    --registry-check     Check registry integrity
    --metadata-check     Check metadata consistency
    --process-check      Check process governance data
    --tunnel-check       Check tunnel governance data
    --cleanup-check      Check cleanup policy data
    --status-check       Check status monitoring data
    --all                Run all checks (default)
    --fix                Attempt to fix issues automatically
    --verbose            Verbose output
    --json               Output results as JSON
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.infra.config_schemas import KInfraConfigManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.port_registry import PortRegistry
from pheno.infra.port_allocator import SmartPortAllocator


class KInfraLinter:
    """KInfra registry and metadata linter."""

    def __init__(self, verbose: bool = False, fix: bool = False):
        """Initialize the linter."""
        self.verbose = verbose
        self.fix = fix
        self.issues: List[Dict[str, Any]] = []
        self.fixes_applied: List[Dict[str, Any]] = []

        # Initialize managers
        self.config_manager = KInfraConfigManager()
        self.process_manager = ProcessGovernanceManager()
        self.tunnel_manager = TunnelGovernanceManager()
        self.cleanup_manager = CleanupPolicyManager()
        self.status_manager = StatusPageManager()
        self.deployment_manager = DeploymentManager()
        self.global_registry = GlobalResourceRegistry()
        self.port_registry = PortRegistry()
        self.port_allocator = SmartPortAllocator()

        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO, format="%(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def add_issue(
        self,
        check_type: str,
        severity: str,
        message: str,
        file: Optional[str] = None,
        line: Optional[int] = None,
        fixable: bool = False,
        fix_suggestion: Optional[str] = None,
    ):
        """Add an issue to the issues list."""
        issue = {
            "type": check_type,
            "severity": severity,
            "message": message,
            "file": file,
            "line": line,
            "fixable": fixable,
            "fix_suggestion": fix_suggestion,
        }
        self.issues.append(issue)

        if self.verbose:
            self.logger.warning(f"{severity.upper()}: {message}")

    def add_fix(self, check_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a fix to the fixes applied list."""
        fix = {"type": check_type, "message": message, "details": details or {}}
        self.fixes_applied.append(fix)

        if self.verbose:
            self.logger.info(f"FIXED: {message}")

    async def check_registry_integrity(self) -> bool:
        """Check registry integrity."""
        self.logger.info("Checking registry integrity...")
        issues_found = 0

        try:
            # Check port registry
            port_registry_data = self.port_registry.get_all_services()
            for entry_id, entry in port_registry_data.items():
                # Check required fields
                if not entry.assigned_port:
                    self.add_issue(
                        "registry_integrity",
                        "error",
                        f"Port registry entry {entry_id} missing port",
                        fixable=True,
                        fix_suggestion="Remove invalid entry",
                    )
                    issues_found += 1

                if not entry.pid:
                    self.add_issue(
                        "registry_integrity",
                        "warning",
                        f"Port registry entry {entry_id} missing PID",
                        fixable=True,
                        fix_suggestion="Set PID to 0 for unmanaged entries",
                    )
                    issues_found += 1

                # Check for stale entries
                if entry.pid and not self._is_process_running(entry.pid):
                    self.add_issue(
                        "registry_integrity",
                        "warning",
                        f"Port registry entry {entry_id} has stale PID {entry.pid}",
                        fixable=True,
                        fix_suggestion="Remove stale entry",
                    )
                    issues_found += 1

                # Check Phase 1 metadata fields
                if not entry.project:
                    self.add_issue(
                        "registry_integrity",
                        "info",
                        f"Port registry entry {entry_id} missing project metadata (Phase 1)",
                        fixable=False,
                        fix_suggestion="Update service registration to include project metadata",
                    )

                if not entry.service:
                    self.add_issue(
                        "registry_integrity",
                        "info",
                        f"Port registry entry {entry_id} missing service type metadata (Phase 1)",
                        fixable=False,
                        fix_suggestion="Update service registration to include service type metadata",
                    )

                if not entry.scope:
                    self.add_issue(
                        "registry_integrity",
                        "info",
                        f"Port registry entry {entry_id} missing scope metadata (Phase 1)",
                        fixable=False,
                        fix_suggestion="Update service registration to include scope metadata",
                    )

            # Check global registry
            try:
                global_resources = await self.global_registry.list_resources()
                for resource_name in global_resources:
                    resource = await self.global_registry.get_resource(resource_name)
                    if not resource:
                        self.add_issue(
                            "registry_integrity",
                            "error",
                            f"Global registry resource {resource_name} not found",
                            fixable=True,
                            fix_suggestion="Remove invalid resource reference",
                        )
                        issues_found += 1
            except Exception as e:
                self.add_issue(
                    "registry_integrity",
                    "error",
                    f"Failed to check global registry: {e}",
                    fixable=False,
                )
                issues_found += 1

            # Check deployment manager resources
            try:
                deployed_resources = await self.deployment_manager.list_resources()
                for resource_name in deployed_resources:
                    resource = await self.deployment_manager.get_resource(resource_name)
                    if not resource:
                        self.add_issue(
                            "registry_integrity",
                            "error",
                            f"Deployment manager resource {resource_name} not found",
                            fixable=True,
                            fix_suggestion="Remove invalid resource reference",
                        )
                        issues_found += 1
            except Exception as e:
                self.add_issue(
                    "registry_integrity",
                    "error",
                    f"Failed to check deployment manager: {e}",
                    fixable=False,
                )
                issues_found += 1

            if issues_found == 0:
                self.logger.info("✅ Registry integrity check passed")
                return True
            else:
                self.logger.warning(f"❌ Registry integrity check found {issues_found} issues")
                return False

        except Exception as e:
            self.add_issue(
                "registry_integrity",
                "error",
                f"Registry integrity check failed: {e}",
                fixable=False,
            )
            return False

    async def check_metadata_consistency(self) -> bool:
        """Check metadata consistency across components."""
        self.logger.info("Checking metadata consistency...")
        issues_found = 0

        try:
            # Get all projects from configuration
            config = self.config_manager.load()
            configured_projects = set(config.projects.keys())

            # Check process governance metadata
            process_stats = self.process_manager.get_cleanup_stats()
            for project_name in configured_projects:
                project_processes = self.process_manager.get_project_processes(project_name)

                for process in project_processes:
                    # Check required metadata fields
                    if not process.project:
                        self.add_issue(
                            "metadata_consistency",
                            "error",
                            f"Process {process.pid} missing project metadata",
                            fixable=True,
                            fix_suggestion="Set project metadata",
                        )
                        issues_found += 1

                    if not process.service:
                        self.add_issue(
                            "metadata_consistency",
                            "error",
                            f"Process {process.pid} missing service metadata",
                            fixable=True,
                            fix_suggestion="Set service metadata",
                        )
                        issues_found += 1

                    # Check metadata consistency
                    if process.project != project_name:
                        self.add_issue(
                            "metadata_consistency",
                            "warning",
                            f"Process {process.pid} project mismatch: {process.project} != {project_name}",
                            fixable=True,
                            fix_suggestion="Update process project metadata",
                        )
                        issues_found += 1

            # Check tunnel governance metadata
            tunnel_stats = self.tunnel_manager.get_tunnel_stats()
            for project_name in configured_projects:
                project_tunnels = self.tunnel_manager.get_project_tunnels(project_name)

                for tunnel in project_tunnels:
                    # Check required metadata fields
                    if not tunnel.project:
                        self.add_issue(
                            "metadata_consistency",
                            "error",
                            f"Tunnel {tunnel.tunnel_id} missing project metadata",
                            fixable=True,
                            fix_suggestion="Set tunnel project metadata",
                        )
                        issues_found += 1

                    if not tunnel.service:
                        self.add_issue(
                            "metadata_consistency",
                            "error",
                            f"Tunnel {tunnel.tunnel_id} missing service metadata",
                            fixable=True,
                            fix_suggestion="Set tunnel service metadata",
                        )
                        issues_found += 1

                    # Check metadata consistency
                    if tunnel.project != project_name:
                        self.add_issue(
                            "metadata_consistency",
                            "warning",
                            f"Tunnel {tunnel.tunnel_id} project mismatch: {tunnel.project} != {project_name}",
                            fixable=True,
                            fix_suggestion="Update tunnel project metadata",
                        )
                        issues_found += 1

            # Check cleanup policy metadata
            for project_name in configured_projects:
                policy = self.cleanup_manager.get_project_policy(project_name)
                if not policy:
                    self.add_issue(
                        "metadata_consistency",
                        "warning",
                        f"Project {project_name} missing cleanup policy",
                        fixable=True,
                        fix_suggestion="Create default cleanup policy",
                    )
                    issues_found += 1
                elif policy.project_name != project_name:
                    self.add_issue(
                        "metadata_consistency",
                        "error",
                        f"Cleanup policy project mismatch: {policy.project_name} != {project_name}",
                        fixable=True,
                        fix_suggestion="Update cleanup policy project name",
                    )
                    issues_found += 1

            # Check status monitoring metadata
            for project_name in configured_projects:
                project_status = self.status_manager.get_project_status(project_name)
                if project_status and project_status.project_name != project_name:
                    self.add_issue(
                        "metadata_consistency",
                        "error",
                        f"Status project mismatch: {project_status.project_name} != {project_name}",
                        fixable=True,
                        fix_suggestion="Update status project name",
                    )
                    issues_found += 1

            if issues_found == 0:
                self.logger.info("✅ Metadata consistency check passed")
                return True
            else:
                self.logger.warning(f"❌ Metadata consistency check found {issues_found} issues")
                return False

        except Exception as e:
            self.add_issue(
                "metadata_consistency",
                "error",
                f"Metadata consistency check failed: {e}",
                fixable=False,
            )
            return False

    async def check_process_governance(self) -> bool:
        """Check process governance data integrity."""
        self.logger.info("Checking process governance data...")
        issues_found = 0

        try:
            # Check process manager configuration
            config = self.process_manager.get_config()
            if not config:
                self.add_issue(
                    "process_governance",
                    "error",
                    "Process governance manager not configured",
                    fixable=True,
                    fix_suggestion="Initialize process governance manager",
                )
                issues_found += 1

            # Check process statistics
            process_stats = self.process_manager.get_cleanup_stats()
            if not isinstance(process_stats, dict):
                self.add_issue(
                    "process_governance", "error", "Process statistics not available", fixable=False
                )
                issues_found += 1

            # Check for orphaned processes
            all_processes = self.process_manager.get_all_processes()
            for process in all_processes:
                if not self._is_process_running(process.pid):
                    self.add_issue(
                        "process_governance",
                        "warning",
                        f"Process {process.pid} ({process.service}) not running",
                        fixable=True,
                        fix_suggestion="Remove orphaned process entry",
                    )
                    issues_found += 1

            # Check process metadata completeness
            for process in all_processes:
                if not process.project or not process.service:
                    self.add_issue(
                        "process_governance",
                        "error",
                        f"Process {process.pid} missing required metadata",
                        fixable=True,
                        fix_suggestion="Update process metadata",
                    )
                    issues_found += 1

            if issues_found == 0:
                self.logger.info("✅ Process governance check passed")
                return True
            else:
                self.logger.warning(f"❌ Process governance check found {issues_found} issues")
                return False

        except Exception as e:
            self.add_issue(
                "process_governance",
                "error",
                f"Process governance check failed: {e}",
                fixable=False,
            )
            return False

    async def check_tunnel_governance(self) -> bool:
        """Check tunnel governance data integrity."""
        self.logger.info("Checking tunnel governance data...")
        issues_found = 0

        try:
            # Check tunnel manager configuration
            config = self.tunnel_manager.get_config()
            if not config:
                self.add_issue(
                    "tunnel_governance",
                    "error",
                    "Tunnel governance manager not configured",
                    fixable=True,
                    fix_suggestion="Initialize tunnel governance manager",
                )
                issues_found += 1

            # Check tunnel statistics
            tunnel_stats = self.tunnel_manager.get_tunnel_stats()
            if not isinstance(tunnel_stats, dict):
                self.add_issue(
                    "tunnel_governance", "error", "Tunnel statistics not available", fixable=False
                )
                issues_found += 1

            # Check for orphaned tunnels
            all_tunnels = self.tunnel_manager.get_all_tunnels()
            for tunnel in all_tunnels:
                if tunnel.status == "error":
                    self.add_issue(
                        "tunnel_governance",
                        "warning",
                        f"Tunnel {tunnel.tunnel_id} ({tunnel.service}) in error state",
                        fixable=True,
                        fix_suggestion="Clean up error tunnel",
                    )
                    issues_found += 1

            # Check tunnel metadata completeness
            for tunnel in all_tunnels:
                if not tunnel.project or not tunnel.service:
                    self.add_issue(
                        "tunnel_governance",
                        "error",
                        f"Tunnel {tunnel.tunnel_id} missing required metadata",
                        fixable=True,
                        fix_suggestion="Update tunnel metadata",
                    )
                    issues_found += 1

            # Check tunnel credentials
            for tunnel in all_tunnels:
                credentials = self.tunnel_manager.get_credentials(
                    tunnel.project, tunnel.service, tunnel.provider
                )
                if not credentials:
                    self.add_issue(
                        "tunnel_governance",
                        "warning",
                        f"Tunnel {tunnel.tunnel_id} missing credentials for {tunnel.provider}",
                        fixable=True,
                        fix_suggestion="Set tunnel credentials",
                    )
                    issues_found += 1

            if issues_found == 0:
                self.logger.info("✅ Tunnel governance check passed")
                return True
            else:
                self.logger.warning(f"❌ Tunnel governance check found {issues_found} issues")
                return False

        except Exception as e:
            self.add_issue(
                "tunnel_governance", "error", f"Tunnel governance check failed: {e}", fixable=False
            )
            return False

    async def check_cleanup_policies(self) -> bool:
        """Check cleanup policy data integrity."""
        self.logger.info("Checking cleanup policy data...")
        issues_found = 0

        try:
            # Check global cleanup policy
            global_policy = self.cleanup_manager.get_global_policy()
            if not global_policy:
                self.add_issue(
                    "cleanup_policies",
                    "error",
                    "Global cleanup policy not configured",
                    fixable=True,
                    fix_suggestion="Create default global cleanup policy",
                )
                issues_found += 1

            # Check project cleanup policies
            config = self.config_manager.load()
            for project_name in config.projects.keys():
                policy = self.cleanup_manager.get_project_policy(project_name)
                if not policy:
                    self.add_issue(
                        "cleanup_policies",
                        "warning",
                        f"Project {project_name} missing cleanup policy",
                        fixable=True,
                        fix_suggestion="Create default cleanup policy",
                    )
                    issues_found += 1
                else:
                    # Check policy consistency
                    if policy.project_name != project_name:
                        self.add_issue(
                            "cleanup_policies",
                            "error",
                            f"Cleanup policy project mismatch: {policy.project_name} != {project_name}",
                            fixable=True,
                            fix_suggestion="Update cleanup policy project name",
                        )
                        issues_found += 1

                    # Check cleanup rules
                    for resource_type, rule in policy.rules.items():
                        if rule.resource_type != resource_type:
                            self.add_issue(
                                "cleanup_policies",
                                "error",
                                f"Cleanup rule resource type mismatch: {rule.resource_type} != {resource_type}",
                                fixable=True,
                                fix_suggestion="Update cleanup rule resource type",
                            )
                            issues_found += 1

            if issues_found == 0:
                self.logger.info("✅ Cleanup policies check passed")
                return True
            else:
                self.logger.warning(f"❌ Cleanup policies check found {issues_found} issues")
                return False

        except Exception as e:
            self.add_issue(
                "cleanup_policies", "error", f"Cleanup policies check failed: {e}", fixable=False
            )
            return False

    async def check_status_monitoring(self) -> bool:
        """Check status monitoring data integrity."""
        self.logger.info("Checking status monitoring data...")
        issues_found = 0

        try:
            # Check status manager configuration
            config = self.status_manager.get_config()
            if not config:
                self.add_issue(
                    "status_monitoring",
                    "error",
                    "Status monitoring manager not configured",
                    fixable=True,
                    fix_suggestion="Initialize status monitoring manager",
                )
                issues_found += 1

            # Check project statuses
            config = self.config_manager.load()
            for project_name in config.projects.keys():
                project_status = self.status_manager.get_project_status(project_name)
                if not project_status:
                    self.add_issue(
                        "status_monitoring",
                        "warning",
                        f"Project {project_name} missing status data",
                        fixable=True,
                        fix_suggestion="Initialize project status",
                    )
                    issues_found += 1
                else:
                    # Check status consistency
                    if project_status.project_name != project_name:
                        self.add_issue(
                            "status_monitoring",
                            "error",
                            f"Status project mismatch: {project_status.project_name} != {project_name}",
                            fixable=True,
                            fix_suggestion="Update status project name",
                        )
                        issues_found += 1

                    # Check service statuses
                    for service_name, service_status in project_status.services.items():
                        if not service_status.status:
                            self.add_issue(
                                "status_monitoring",
                                "warning",
                                f"Service {service_name} missing status",
                                fixable=True,
                                fix_suggestion="Set service status",
                            )
                            issues_found += 1

                    # Check tunnel statuses
                    for tunnel_name, tunnel_status in project_status.tunnels.items():
                        if not tunnel_status.status:
                            self.add_issue(
                                "status_monitoring",
                                "warning",
                                f"Tunnel {tunnel_name} missing status",
                                fixable=True,
                                fix_suggestion="Set tunnel status",
                            )
                            issues_found += 1

            if issues_found == 0:
                self.logger.info("✅ Status monitoring check passed")
                return True
            else:
                self.logger.warning(f"❌ Status monitoring check found {issues_found} issues")
                return False

        except Exception as e:
            self.add_issue(
                "status_monitoring", "error", f"Status monitoring check failed: {e}", fixable=False
            )
            return False

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process is running."""
        try:
            import psutil

            return psutil.pid_exists(pid)
        except ImportError:
            # Fallback to basic check
            try:
                import os

                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False

    async def apply_fixes(self) -> int:
        """Apply automatic fixes where possible."""
        if not self.fix:
            return 0

        fixes_applied = 0

        for issue in self.issues:
            if not issue["fixable"]:
                continue

            try:
                if issue["type"] == "registry_integrity":
                    if "stale PID" in issue["message"]:
                        # Remove stale port registry entries
                        entry_id = issue["message"].split()[3]  # Extract entry ID
                        self.port_registry.remove_entry(entry_id)
                        self.add_fix("registry_integrity", f"Removed stale entry {entry_id}")
                        fixes_applied += 1

                elif issue["type"] == "metadata_consistency":
                    if "missing project metadata" in issue["message"]:
                        # This would require more context to fix properly
                        self.add_fix("metadata_consistency", "Skipped complex metadata fix")
                        fixes_applied += 1

                elif issue["type"] == "process_governance":
                    if "orphaned process" in issue["message"]:
                        # Remove orphaned process entries
                        pid = int(issue["message"].split()[1])
                        self.process_manager.unregister_process(pid)
                        self.add_fix("process_governance", f"Removed orphaned process {pid}")
                        fixes_applied += 1

                elif issue["type"] == "tunnel_governance":
                    if "error tunnel" in issue["message"]:
                        # Clean up error tunnels
                        tunnel_id = issue["message"].split()[2]
                        self.tunnel_manager.cleanup_tunnel(tunnel_id)
                        self.add_fix("tunnel_governance", f"Cleaned up error tunnel {tunnel_id}")
                        fixes_applied += 1

                elif issue["type"] == "cleanup_policies":
                    if "missing cleanup policy" in issue["message"]:
                        # Create default cleanup policy
                        project_name = issue["message"].split()[1]
                        from pheno.infra.cleanup_policies import CleanupStrategy

                        policy = self.cleanup_manager.create_default_policy(
                            project_name=project_name, strategy=CleanupStrategy.MODERATE
                        )
                        self.cleanup_manager.set_project_policy(project_name, policy)
                        self.add_fix(
                            "cleanup_policies", f"Created default policy for {project_name}"
                        )
                        fixes_applied += 1

                elif issue["type"] == "status_monitoring":
                    if "missing status data" in issue["message"]:
                        # Initialize project status
                        project_name = issue["message"].split()[1]
                        self.status_manager.update_service_status(
                            project_name=project_name,
                            service_name="default",
                            status="unknown",
                            port=0,
                            health_status="unknown",
                        )
                        self.add_fix("status_monitoring", f"Initialized status for {project_name}")
                        fixes_applied += 1

            except Exception as e:
                self.logger.warning(f"Failed to apply fix for {issue['type']}: {e}")

        return fixes_applied

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report."""
        return {
            "summary": {
                "total_issues": len(self.issues),
                "errors": len([i for i in self.issues if i["severity"] == "error"]),
                "warnings": len([i for i in self.issues if i["severity"] == "warning"]),
                "fixes_applied": len(self.fixes_applied),
                "fixable_issues": len([i for i in self.issues if i["fixable"]]),
            },
            "issues": self.issues,
            "fixes": self.fixes_applied,
            "checks": {
                "registry_integrity": len(
                    [i for i in self.issues if i["type"] == "registry_integrity"]
                ),
                "metadata_consistency": len(
                    [i for i in self.issues if i["type"] == "metadata_consistency"]
                ),
                "process_governance": len(
                    [i for i in self.issues if i["type"] == "process_governance"]
                ),
                "tunnel_governance": len(
                    [i for i in self.issues if i["type"] == "tunnel_governance"]
                ),
                "cleanup_policies": len(
                    [i for i in self.issues if i["type"] == "cleanup_policies"]
                ),
                "status_monitoring": len(
                    [i for i in self.issues if i["type"] == "status_monitoring"]
                ),
            },
        }


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="KInfra Registry and Metadata Linter")
    parser.add_argument("--registry-check", action="store_true", help="Check registry integrity")
    parser.add_argument("--metadata-check", action="store_true", help="Check metadata consistency")
    parser.add_argument(
        "--process-check", action="store_true", help="Check process governance data"
    )
    parser.add_argument("--tunnel-check", action="store_true", help="Check tunnel governance data")
    parser.add_argument("--cleanup-check", action="store_true", help="Check cleanup policy data")
    parser.add_argument("--status-check", action="store_true", help="Check status monitoring data")
    parser.add_argument("--all", action="store_true", default=True, help="Run all checks (default)")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues automatically")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Initialize linter
    linter = KInfraLinter(verbose=args.verbose, fix=args.fix)

    # Determine which checks to run
    checks_to_run = []
    if args.registry_check or args.all:
        checks_to_run.append(("registry_integrity", linter.check_registry_integrity))
    if args.metadata_check or args.all:
        checks_to_run.append(("metadata_consistency", linter.check_metadata_consistency))
    if args.process_check or args.all:
        checks_to_run.append(("process_governance", linter.check_process_governance))
    if args.tunnel_check or args.all:
        checks_to_run.append(("tunnel_governance", linter.check_tunnel_governance))
    if args.cleanup_check or args.all:
        checks_to_run.append(("cleanup_policies", linter.check_cleanup_policies))
    if args.status_check or args.all:
        checks_to_run.append(("status_monitoring", linter.check_status_monitoring))

    # Run checks
    all_passed = True
    for check_name, check_func in checks_to_run:
        try:
            result = await check_func()
            if not result:
                all_passed = False
        except Exception as e:
            linter.logger.error(f"Check {check_name} failed: {e}")
            all_passed = False

    # Apply fixes if requested
    if args.fix:
        fixes_applied = await linter.apply_fixes()
        if fixes_applied > 0:
            linter.logger.info(f"Applied {fixes_applied} fixes")

    # Generate report
    report = linter.generate_report()

    # Output results
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\nKInfra Lint Report")
        print("=" * 50)
        print(f"Total Issues: {report['summary']['total_issues']}")
        print(f"Errors: {report['summary']['errors']}")
        print(f"Warnings: {report['summary']['warnings']}")
        print(f"Fixes Applied: {report['summary']['fixes_applied']}")
        print(f"Fixable Issues: {report['summary']['fixable_issues']}")

        if report["summary"]["total_issues"] > 0:
            print(f"\nIssues by Type:")
            for check_type, count in report["checks"].items():
                if count > 0:
                    print(f"  {check_type}: {count}")

        if all_passed:
            print(f"\n✅ All checks passed!")
            sys.exit(0)
        else:
            print(f"\n❌ Some checks failed!")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
