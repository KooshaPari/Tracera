#!/usr/bin/env python3
"""
KInfra Migration Tool: Automated Migration for Router, Atoms, and Zen

This tool provides automated migration capabilities for existing codebases
to adopt KInfra Phase 5 features. It supports gradual, safe migration
with rollback capabilities.

Usage:
    python scripts/kinfra-migrate.py [command] [options]

Commands:
    generate    Generate migration scripts for a project
    validate    Validate migration progress
    rollback    Rollback migration changes
    status      Show migration status
    plan        Show migration plan for a project

Options:
    --project PROJECT    Target project (router, atoms, zen)
    --phase PHASE       Migration phase (1, 2, 3, 4)
    --dry-run           Show what would be changed without making changes
    --force             Force migration even if validation fails
    --verbose           Verbose output
    --json              Output results as JSON
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import shutil
import subprocess
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.infra.config_schemas import KInfraConfigManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.port_allocator import SmartPortAllocator
from pheno.infra.port_registry import PortRegistry


class KInfraMigrator:
    """KInfra migration tool for existing codebases."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the migrator."""
        self.verbose = verbose
        self.projects = {
            "router": {
                "path": "../router",
                "services": ["api", "worker", "routing-engine"],
                "dependencies": ["redis", "postgres", "nats"],
                "priority": "high"
            },
            "atoms": {
                "path": "../atoms-mcp-prod",
                "services": ["mcp-server", "atomic-ops", "data-processor"],
                "dependencies": ["redis", "postgres"],
                "priority": "high"
            },
            "zen": {
                "path": "../zen-mcp-server",
                "services": ["api-gateway", "microservices", "db-services"],
                "dependencies": ["postgres", "redis", "external"],
                "priority": "medium"
            }
        }
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_project_path(self, project: str) -> Path:
        """Get the project path."""
        if project not in self.projects:
            raise ValueError(f"Unknown project: {project}")
        
        project_path = Path(self.projects[project]["path"])
        if not project_path.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")
        
        return project_path
    
    def generate_migration_script(self, project: str, phase: int, dry_run: bool = False) -> Dict[str, Any]:
        """Generate migration script for a project and phase."""
        self.logger.info(f"Generating migration script for {project} phase {phase}")
        
        project_path = self.get_project_path(project)
        project_info = self.projects[project]
        
        # Phase-specific migration templates
        templates = {
            1: self._generate_phase1_template(project, project_info),
            2: self._generate_phase2_template(project, project_info),
            3: self._generate_phase3_template(project, project_info),
            4: self._generate_phase4_template(project, project_info)
        }
        
        if phase not in templates:
            raise ValueError(f"Unknown phase: {phase}")
        
        template = templates[phase]
        
        # Generate migration script
        script_content = self._create_migration_script(project, phase, template)
        
        # Write script file
        script_path = project_path / f"migrate_phase{phase}.py"
        
        if not dry_run:
            with open(script_path, 'w') as f:
                f.write(script_content)
            self.logger.info(f"Migration script written to {script_path}")
        else:
            self.logger.info(f"Would write migration script to {script_path}")
        
        # Generate configuration changes
        config_changes = self._generate_config_changes(project, phase)
        
        # Generate code changes
        code_changes = self._generate_code_changes(project, phase, project_path)
        
        return {
            "project": project,
            "phase": phase,
            "script_path": str(script_path),
            "config_changes": config_changes,
            "code_changes": code_changes,
            "dry_run": dry_run
        }
    
    def _generate_phase1_template(self, project: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 1 (Enable Metadata) template."""
        return {
            "title": f"Phase 1: Enable Metadata for {project}",
            "description": "Enable metadata tracking without breaking existing functionality",
            "changes": [
                {
                    "file": "port_allocation.py",
                    "type": "modify",
                    "description": "Add metadata to port allocation calls",
                    "old_code": "port_allocator.allocate_port(service_name, port)",
                    "new_code": f"port_allocator.allocate_port(service_name, port, metadata={{\n    'project': '{project}',\n    'service': service_name,\n    'environment': os.getenv('ENVIRONMENT', 'development'),\n    'version': '{project_info.get('version', '1.0.0')}'\n}})"
                },
                {
                    "file": "process_management.py",
                    "type": "modify",
                    "description": "Add metadata to process registration",
                    "old_code": "process_manager.register_process(pid, command_line)",
                    "new_code": f"process_manager.register_process(pid, command_line, metadata={{\n    'project': '{project}',\n    'service': service_name,\n    'environment': os.getenv('ENVIRONMENT', 'development'),\n    'version': '{project_info.get('version', '1.0.0')}'\n}})"
                }
            ],
            "config_changes": {
                "enable_metadata_tracking": True,
                "metadata_fields": ["project", "service", "environment", "version"]
            }
        }
    
    def _generate_phase2_template(self, project: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 2 (Adopt ProjectInfraContext) template."""
        return {
            "title": f"Phase 2: Adopt ProjectInfraContext for {project}",
            "description": "Migrate to project-scoped infrastructure management",
            "changes": [
                {
                    "file": "main.py",
                    "type": "modify",
                    "description": "Wrap service initialization with ProjectInfraContext",
                    "old_code": "service_manager = ServiceInfraManager()\nawait service_manager.start_all()",
                    "new_code": f"from pheno.infra.project_context import project_infra_context\n\nasync with project_infra_context('{project}') as infra:\n    service_manager = ServiceInfraManager()\n    await service_manager.start_all()"
                },
                {
                    "file": "service_config.py",
                    "type": "modify",
                    "description": "Add project-specific configuration",
                    "old_code": "config = load_config()",
                    "new_code": f"config = load_config()\nconfig.project_name = '{project}'\nconfig.enable_project_isolation = True"
                }
            ],
            "config_changes": {
                "project_name": project,
                "enable_project_isolation": True,
                "project_services": project_info["services"]
            }
        }
    
    def _generate_phase3_template(self, project: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 3 (Resource Helpers) template."""
        return {
            "title": f"Phase 3: Adopt Resource Helpers for {project}",
            "description": "Adopt shared resource management and coordination",
            "changes": [
                {
                    "file": "resource_management.py",
                    "type": "modify",
                    "description": "Replace direct DeploymentManager with ResourceCoordinator",
                    "old_code": "deployment_manager = DeploymentManager()\nresource = await deployment_manager.deploy_resource(name, type, mode, config)",
                    "new_code": f"from pheno.infra.resource_coordinator import ResourceCoordinator\n\nresource_coordinator = ResourceCoordinator(deployment_manager)\nawait resource_coordinator.initialize()\nresource = await resource_coordinator.get_or_deploy_resource(name, type, 'global', config)"
                },
                {
                    "file": "shared_resources.py",
                    "type": "create",
                    "description": "Create shared resource configuration",
                    "content": f"# Shared resources for {project}\nSHARED_RESOURCES = {{\n    'redis': {{\n        'type': 'redis',\n        'config': {{'host': 'localhost', 'port': 6379, 'db': 0}},\n        'shared': True\n    }},\n    'postgres': {{\n        'type': 'postgres',\n        'config': {{'host': 'localhost', 'port': 5432, 'database': 'shared'}},\n        'shared': True\n    }}\n}}"
                }
            ],
            "config_changes": {
                "enable_resource_sharing": True,
                "shared_resources": project_info["dependencies"],
                "resource_coordination": True
            }
        }
    
    def _generate_phase4_template(self, project: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 4 (Advanced Features) template."""
        return {
            "title": f"Phase 4: Adopt Advanced Features for {project}",
            "description": "Adopt process governance, tunnel governance, and cleanup policies",
            "changes": [
                {
                    "file": "process_governance.py",
                    "type": "create",
                    "description": "Add process governance",
                    "content": f"from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata\n\nprocess_manager = ProcessGovernanceManager()\n\n# Register processes with metadata\nfor service in {project_info['services']}:\n    metadata = ProcessMetadata(\n        project='{project}',\n        service=service,\n        pid=os.getpid(),\n        command_line=sys.argv,\n        environment=dict(os.environ),\n        scope='local',\n        resource_type='service',\n        tags={{'web', 'rest', 'api'}}\n    )\n    process_manager.register_process(os.getpid(), metadata)"
                },
                {
                    "file": "tunnel_governance.py",
                    "type": "create",
                    "description": "Add tunnel governance",
                    "content": f"from pheno.infra.tunnel_governance import TunnelGovernanceManager\n\ntunnel_manager = TunnelGovernanceManager()\n\n# Create tunnels for services\nfor service in {project_info['services']}:\n    tunnel = tunnel_manager.create_tunnel(\n        project='{project}',\n        service=service,\n        port=8000 + hash(service) % 1000,\n        provider='cloudflare',\n        reuse_existing=True\n    )"
                },
                {
                    "file": "cleanup_policies.py",
                    "type": "create",
                    "description": "Add cleanup policies",
                    "content": f"from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy\n\ncleanup_manager = CleanupPolicyManager()\n\n# Set up project-specific cleanup policies\ncleanup_manager.set_project_policy(\n    '{project}',\n    cleanup_manager.create_default_policy(\n        project_name='{project}',\n        strategy=CleanupStrategy.MODERATE\n    )\n)"
                },
                {
                    "file": "status_monitoring.py",
                    "type": "create",
                    "description": "Add status monitoring",
                    "content": f"from pheno.infra.fallback_site.status_pages import StatusPageManager\n\nstatus_manager = StatusPageManager()\n\n# Update service status\nfor service in {project_info['services']}:\n    status_manager.update_service_status(\n        project_name='{project}',\n        service_name=service,\n        status='running',\n        port=8000 + hash(service) % 1000,\n        health_status='healthy'\n    )"
                }
            ],
            "config_changes": {
                "enable_process_governance": True,
                "enable_tunnel_governance": True,
                "enable_cleanup_policies": True,
                "enable_status_monitoring": True
            }
        }
    
    def _create_migration_script(self, project: str, phase: int, template: Dict[str, Any]) -> str:
        """Create migration script content."""
        return f'''#!/usr/bin/env python3
"""
{template['title']}

{template['description']}

This script was generated by kinfra-migrate.py
Generated on: {datetime.now().isoformat()}
Project: {project}
Phase: {phase}
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add pheno-sdk to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pheno-sdk" / "src"))

from pheno.infra.config_schemas import KInfraConfigManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.port_allocator import SmartPortAllocator
from pheno.infra.port_registry import PortRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_phase{phase}():
    """Migrate {project} to Phase {phase}."""
    logger.info(f"Starting Phase {phase} migration for {project}")
    
    try:
        # Initialize KInfra components
        config_manager = KInfraConfigManager()
        process_manager = ProcessGovernanceManager()
        tunnel_manager = TunnelGovernanceManager()
        cleanup_manager = CleanupPolicyManager()
        status_manager = StatusPageManager()
        deployment_manager = DeploymentManager()
        resource_coordinator = ResourceCoordinator(deployment_manager)
        global_registry = GlobalResourceRegistry()
        port_allocator = SmartPortAllocator()
        port_registry = PortRegistry()
        
        # Phase {phase} specific migration
        {self._generate_phase_migration_code(project, phase, template)}
        
        logger.info(f"Phase {phase} migration completed successfully for {project}")
        return True
        
    except Exception as e:
        logger.error(f"Phase {phase} migration failed for {project}: {{e}}")
        return False

async def rollback_phase{phase}():
    """Rollback Phase {phase} migration for {project}."""
    logger.info(f"Starting Phase {phase} rollback for {project}")
    
    try:
        # Phase {phase} specific rollback
        {self._generate_phase_rollback_code(project, phase, template)}
        
        logger.info(f"Phase {phase} rollback completed successfully for {project}")
        return True
        
    except Exception as e:
        logger.error(f"Phase {phase} rollback failed for {project}: {{e}}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=f"Phase {phase} migration for {project}")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    
    args = parser.parse_args()
    
    if args.rollback:
        success = asyncio.run(rollback_phase{phase}())
    else:
        success = asyncio.run(migrate_phase{phase}())
    
    sys.exit(0 if success else 1)
'''
    
    def _generate_phase_migration_code(self, project: str, phase: int, template: Dict[str, Any]) -> str:
        """Generate phase-specific migration code."""
        if phase == 1:
            return f"""
        # Phase 1: Enable metadata tracking
        config = config_manager.load()
        config.enable_metadata_tracking = True
        config_manager.save_config(config)
        
        # Update port allocation calls
        logger.info("Updating port allocation calls with metadata")
        # This would be done by modifying the actual code files
        """
        elif phase == 2:
            return f"""
        # Phase 2: Adopt ProjectInfraContext
        config = config_manager.load()
        config.project_name = '{project}'
        config.enable_project_isolation = True
        config_manager.save_config(config)
        
        # Update service initialization
        logger.info("Updating service initialization with ProjectInfraContext")
        # This would be done by modifying the actual code files
        """
        elif phase == 3:
            return f"""
        # Phase 3: Adopt resource helpers
        await resource_coordinator.initialize()
        
        # Set up shared resources
        logger.info("Setting up shared resources")
        for resource_name, resource_config in {template['config_changes']['shared_resources']}.items():
            await resource_coordinator.get_or_deploy_resource(
                resource_name, 
                resource_config['type'], 
                'global', 
                resource_config['config']
            )
        """
        elif phase == 4:
            return f"""
        # Phase 4: Adopt advanced features
        # Set up process governance
        process_policy = cleanup_manager.create_default_policy(
            project_name='{project}',
            strategy=CleanupStrategy.MODERATE
        )
        cleanup_manager.set_project_policy('{project}', process_policy)
        
        # Set up tunnel governance
        logger.info("Setting up tunnel governance")
        for service in {self.projects[project]['services']}:
            tunnel = tunnel_manager.create_tunnel(
                project='{project}',
                service=service,
                port=8000 + hash(service) % 1000,
                provider='cloudflare',
                reuse_existing=True
            )
        
        # Set up status monitoring
        logger.info("Setting up status monitoring")
        for service in {self.projects[project]['services']}:
            status_manager.update_service_status(
                project_name='{project}',
                service_name=service,
                status='running',
                port=8000 + hash(service) % 1000,
                health_status='healthy'
            )
        """
        else:
            return "# Unknown phase"
    
    def _generate_phase_rollback_code(self, project: str, phase: int, template: Dict[str, Any]) -> str:
        """Generate phase-specific rollback code."""
        if phase == 1:
            return f"""
        # Phase 1 rollback: Disable metadata tracking
        config = config_manager.load()
        config.enable_metadata_tracking = False
        config_manager.save_config(config)
        """
        elif phase == 2:
            return f"""
        # Phase 2 rollback: Remove ProjectInfraContext
        config = config_manager.load()
        config.project_name = None
        config.enable_project_isolation = False
        config_manager.save_config(config)
        """
        elif phase == 3:
            return f"""
        # Phase 3 rollback: Remove resource coordination
        await resource_coordinator.shutdown()
        """
        elif phase == 4:
            return f"""
        # Phase 4 rollback: Remove advanced features
        cleanup_manager.remove_project_policy('{project}')
        tunnel_manager.cleanup_project_tunnels('{project}')
        status_manager.remove_project_status('{project}')
        """
        else:
            return "# Unknown phase"
    
    def _generate_config_changes(self, project: str, phase: int) -> Dict[str, Any]:
        """Generate configuration changes for a phase."""
        config_changes = {
            1: {
                "enable_metadata_tracking": True,
                "metadata_fields": ["project", "service", "environment", "version"]
            },
            2: {
                "project_name": project,
                "enable_project_isolation": True,
                "project_services": self.projects[project]["services"]
            },
            3: {
                "enable_resource_sharing": True,
                "shared_resources": self.projects[project]["dependencies"],
                "resource_coordination": True
            },
            4: {
                "enable_process_governance": True,
                "enable_tunnel_governance": True,
                "enable_cleanup_policies": True,
                "enable_status_monitoring": True
            }
        }
        
        return config_changes.get(phase, {})
    
    def _generate_code_changes(self, project: str, phase: int, project_path: Path) -> List[Dict[str, Any]]:
        """Generate code changes for a phase."""
        # This would analyze the actual codebase and generate specific changes
        # For now, return template changes
        return [
            {
                "file": "main.py",
                "type": "modify",
                "description": f"Phase {phase} changes for {project}",
                "changes": f"Phase {phase} specific code changes"
            }
        ]
    
    def validate_migration(self, project: str, phase: int) -> Dict[str, Any]:
        """Validate migration progress for a project."""
        self.logger.info(f"Validating migration for {project} phase {phase}")
        
        project_path = self.get_project_path(project)
        validation_results = {
            "project": project,
            "phase": phase,
            "status": "unknown",
            "checks": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if migration script exists
            script_path = project_path / f"migrate_phase{phase}.py"
            if script_path.exists():
                validation_results["checks"].append({
                    "check": "migration_script_exists",
                    "status": "pass",
                    "message": f"Migration script found: {script_path}"
                })
            else:
                validation_results["checks"].append({
                    "check": "migration_script_exists",
                    "status": "fail",
                    "message": f"Migration script not found: {script_path}"
                })
                validation_results["errors"].append("Migration script not found")
            
            # Check configuration
            config_path = project_path / "kinfra_config.yaml"
            if config_path.exists():
                validation_results["checks"].append({
                    "check": "config_file_exists",
                    "status": "pass",
                    "message": f"Configuration file found: {config_path}"
                })
            else:
                validation_results["checks"].append({
                    "check": "config_file_exists",
                    "status": "warn",
                    "message": f"Configuration file not found: {config_path}"
                })
                validation_results["warnings"].append("Configuration file not found")
            
            # Check for KInfra integration
            kinfra_files = list(project_path.glob("**/*kinfra*"))
            if kinfra_files:
                validation_results["checks"].append({
                    "check": "kinfra_integration",
                    "status": "pass",
                    "message": f"KInfra integration found: {len(kinfra_files)} files"
                })
            else:
                validation_results["checks"].append({
                    "check": "kinfra_integration",
                    "status": "warn",
                    "message": "No KInfra integration found"
                })
                validation_results["warnings"].append("No KInfra integration found")
            
            # Determine overall status
            if validation_results["errors"]:
                validation_results["status"] = "failed"
            elif validation_results["warnings"]:
                validation_results["status"] = "warning"
            else:
                validation_results["status"] = "passed"
            
            return validation_results
            
        except Exception as e:
            validation_results["errors"].append(f"Validation failed: {e}")
            validation_results["status"] = "error"
            return validation_results
    
    def rollback_migration(self, project: str, phase: int, force: bool = False) -> Dict[str, Any]:
        """Rollback migration for a project."""
        self.logger.info(f"Rolling back migration for {project} phase {phase}")
        
        project_path = self.get_project_path(project)
        rollback_results = {
            "project": project,
            "phase": phase,
            "status": "unknown",
            "actions": [],
            "errors": []
        }
        
        try:
            # Run rollback script if it exists
            script_path = project_path / f"migrate_phase{phase}.py"
            if script_path.exists():
                result = subprocess.run([
                    sys.executable, str(script_path), "--rollback"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    rollback_results["actions"].append({
                        "action": "rollback_script_executed",
                        "status": "success",
                        "message": "Rollback script executed successfully"
                    })
                else:
                    rollback_results["actions"].append({
                        "action": "rollback_script_executed",
                        "status": "failed",
                        "message": f"Rollback script failed: {result.stderr}"
                    })
                    rollback_results["errors"].append("Rollback script failed")
            else:
                rollback_results["actions"].append({
                    "action": "rollback_script_executed",
                    "status": "skipped",
                    "message": "Rollback script not found"
                })
            
            # Remove migration artifacts
            artifacts = [
                f"migrate_phase{phase}.py",
                f"migrate_phase{phase}.py.bak",
                f"kinfra_config.yaml.bak"
            ]
            
            for artifact in artifacts:
                artifact_path = project_path / artifact
                if artifact_path.exists():
                    artifact_path.unlink()
                    rollback_results["actions"].append({
                        "action": "remove_artifact",
                        "status": "success",
                        "message": f"Removed {artifact}"
                    })
            
            rollback_results["status"] = "completed" if not rollback_results["errors"] else "failed"
            return rollback_results
            
        except Exception as e:
            rollback_results["errors"].append(f"Rollback failed: {e}")
            rollback_results["status"] = "error"
            return rollback_results
    
    def get_migration_status(self, project: str = None) -> Dict[str, Any]:
        """Get migration status for all projects or a specific project."""
        if project:
            projects = [project]
        else:
            projects = list(self.projects.keys())
        
        status_results = {
            "timestamp": datetime.now().isoformat(),
            "projects": {}
        }
        
        for proj in projects:
            project_path = self.get_project_path(proj)
            project_status = {
                "project": proj,
                "path": str(project_path),
                "phases": {},
                "overall_status": "unknown"
            }
            
            # Check each phase
            for phase in range(1, 5):
                phase_status = self.validate_migration(proj, phase)
                project_status["phases"][f"phase_{phase}"] = phase_status
            
            # Determine overall status
            phase_statuses = [phase["status"] for phase in project_status["phases"].values()]
            if "failed" in phase_statuses:
                project_status["overall_status"] = "failed"
            elif "warning" in phase_statuses:
                project_status["overall_status"] = "warning"
            elif all(status == "passed" for status in phase_statuses):
                project_status["overall_status"] = "completed"
            else:
                project_status["overall_status"] = "in_progress"
            
            status_results["projects"][proj] = project_status
        
        return status_results


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="KInfra Migration Tool")
    parser.add_argument("command", choices=["generate", "validate", "rollback", "status", "plan"], help="Command to execute")
    parser.add_argument("--project", choices=["router", "atoms", "zen"], help="Target project")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Migration phase")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--force", action="store_true", help="Force migration even if validation fails")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = KInfraMigrator(verbose=args.verbose)
    
    # Execute command
    if args.command == "generate":
        if not args.project or not args.phase:
            print("Error: --project and --phase are required for generate command")
            sys.exit(1)
        
        result = migrator.generate_migration_script(
            args.project, 
            args.phase, 
            dry_run=args.dry_run
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Generated migration script for {args.project} phase {args.phase}")
            print(f"Script path: {result['script_path']}")
            print(f"Config changes: {len(result['config_changes'])} items")
            print(f"Code changes: {len(result['code_changes'])} items")
    
    elif args.command == "validate":
        if not args.project or not args.phase:
            print("Error: --project and --phase are required for validate command")
            sys.exit(1)
        
        result = migrator.validate_migration(args.project, args.phase)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Validation results for {args.project} phase {args.phase}:")
            print(f"Status: {result['status']}")
            print(f"Checks: {len(result['checks'])}")
            print(f"Errors: {len(result['errors'])}")
            print(f"Warnings: {len(result['warnings'])}")
    
    elif args.command == "rollback":
        if not args.project or not args.phase:
            print("Error: --project and --phase are required for rollback command")
            sys.exit(1)
        
        result = migrator.rollback_migration(args.project, args.phase, force=args.force)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Rollback results for {args.project} phase {args.phase}:")
            print(f"Status: {result['status']}")
            print(f"Actions: {len(result['actions'])}")
            print(f"Errors: {len(result['errors'])}")
    
    elif args.command == "status":
        result = migrator.get_migration_status(args.project)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Migration Status:")
            for project, status in result["projects"].items():
                print(f"  {project}: {status['overall_status']}")
                for phase, phase_status in status["phases"].items():
                    print(f"    {phase}: {phase_status['status']}")
    
    elif args.command == "plan":
        if not args.project:
            print("Error: --project is required for plan command")
            sys.exit(1)
        
        # Generate migration plan
        plan = {
            "project": args.project,
            "phases": []
        }
        
        for phase in range(1, 5):
            phase_plan = migrator.generate_migration_script(args.project, phase, dry_run=True)
            plan["phases"].append({
                "phase": phase,
                "title": phase_plan["config_changes"].get("title", f"Phase {phase}"),
                "description": phase_plan["config_changes"].get("description", f"Phase {phase} migration"),
                "config_changes": len(phase_plan["config_changes"]),
                "code_changes": len(phase_plan["code_changes"])
            })
        
        if args.json:
            print(json.dumps(plan, indent=2))
        else:
            print(f"Migration plan for {args.project}:")
            for phase_plan in plan["phases"]:
                print(f"  Phase {phase_plan['phase']}: {phase_plan['title']}")
                print(f"    Description: {phase_plan['description']}")
                print(f"    Config changes: {phase_plan['config_changes']}")
                print(f"    Code changes: {phase_plan['code_changes']}")


if __name__ == "__main__":
    asyncio.run(main())