#!/usr/bin/env python3
"""
KInfra Documentation Finalization Tool: Mark Legacy APIs Deprecated

This tool finalizes documentation by marking legacy APIs as deprecated
with sunset timelines and ensuring all documentation is up to date.

Usage:
    python scripts/kinfra-docs-finalize.py [command] [options]

Commands:
    audit         Audit documentation completeness
    deprecate     Mark legacy APIs as deprecated
    generate      Generate final documentation
    validate      Validate documentation
    sunset        Create sunset timeline

Options:
    --project PROJECT    Target project (router, atoms, zen, all)
    --phase PHASE       Migration phase (1, 2, 3, 4)
    --output DIR        Output directory
    --verbose           Verbose output
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import re
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.infra.config_schemas import KInfraConfigManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager
from pheno.infra.fallback_site.status_pages import StatusPageManager


class KInfraDocsFinalizer:
    """KInfra documentation finalization tool."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the docs finalizer."""
        self.verbose = verbose
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Legacy APIs to deprecate
        self.legacy_apis = {
            "port_allocator": {
                "old_method": "allocate_port(service_name, port)",
                "new_method": "allocate_port(service_name, port, metadata={})",
                "deprecation_date": "2024-01-01",
                "sunset_date": "2024-06-01",
                "replacement": "Use allocate_port with metadata parameter"
            },
            "service_infra_manager": {
                "old_method": "register_process(pid, command_line)",
                "new_method": "register_process(pid, command_line, metadata=ProcessMetadata(...))",
                "deprecation_date": "2024-01-01",
                "sunset_date": "2024-06-01",
                "replacement": "Use register_process with ProcessMetadata"
            },
            "deployment_manager": {
                "old_method": "deploy_resource(name, type, mode, config)",
                "new_method": "Use ResourceCoordinator.get_or_deploy_resource()",
                "deprecation_date": "2024-01-01",
                "sunset_date": "2024-06-01",
                "replacement": "Use ResourceCoordinator for better resource coordination"
            }
        }
        
        # Documentation structure
        self.docs_structure = {
            "quickstart": [
                "single_project_setup.md",
                "shared_resource_setup.md",
                "cli_reference.md"
            ],
            "migration": [
                "MIGRATION_PLAN.md",
                "ROUTER_ADOPTION_GUIDE.md",
                "ATOMS_ADOPTION_GUIDE.md",
                "ZEN_ADOPTION_GUIDE.md"
            ],
            "api": [
                "process_governance.md",
                "tunnel_governance.md",
                "cleanup_policies.md",
                "status_monitoring.md",
                "resource_coordination.md"
            ],
            "examples": [
                "phase5_process_governance_example.py",
                "phase6_complete_integration_example.py"
            ]
        }
    
    def audit_documentation(self, project: str = None) -> Dict[str, Any]:
        """Audit documentation completeness."""
        self.logger.info("Auditing documentation completeness...")
        
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "project": project or "all",
            "total_files": 0,
            "missing_files": [],
            "outdated_files": [],
            "deprecated_apis": [],
            "coverage": {
                "quickstart": 0,
                "migration": 0,
                "api": 0,
                "examples": 0
            },
            "recommendations": []
        }
        
        # Check documentation structure
        docs_root = Path("docs")
        if not docs_root.exists():
            audit_results["missing_files"].append("docs/ directory")
            return audit_results
        
        # Check each documentation category
        for category, files in self.docs_structure.items():
            category_path = docs_root / category
            if not category_path.exists():
                audit_results["missing_files"].append(f"docs/{category}/ directory")
                continue
            
            for file_name in files:
                file_path = category_path / file_name
                if file_path.exists():
                    audit_results["total_files"] += 1
                    audit_results["coverage"][category] += 1
                    
                    # Check if file is outdated
                    if self._is_file_outdated(file_path):
                        audit_results["outdated_files"].append(str(file_path))
                else:
                    audit_results["missing_files"].append(str(file_path))
        
        # Check for deprecated APIs in documentation
        for file_path in docs_root.rglob("*.md"):
            if file_path.is_file():
                deprecated_apis = self._find_deprecated_apis_in_file(file_path)
                if deprecated_apis:
                    audit_results["deprecated_apis"].extend(deprecated_apis)
        
        # Generate recommendations
        audit_results["recommendations"] = self._generate_docs_recommendations(audit_results)
        
        return audit_results
    
    def _is_file_outdated(self, file_path: Path) -> bool:
        """Check if a file is outdated (older than 30 days)."""
        try:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_time < datetime.now() - timedelta(days=30)
        except:
            return True
    
    def _find_deprecated_apis_in_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Find deprecated APIs in a file."""
        try:
            content = file_path.read_text()
            deprecated_apis = []
            
            for api_name, api_info in self.legacy_apis.items():
                if api_info["old_method"] in content:
                    deprecated_apis.append({
                        "file": str(file_path),
                        "api": api_name,
                        "old_method": api_info["old_method"],
                        "new_method": api_info["new_method"],
                        "replacement": api_info["replacement"]
                    })
            
            return deprecated_apis
        except:
            return []
    
    def _generate_docs_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """Generate documentation recommendations."""
        recommendations = []
        
        if audit_results["missing_files"]:
            recommendations.append(f"Create {len(audit_results['missing_files'])} missing documentation files")
        
        if audit_results["outdated_files"]:
            recommendations.append(f"Update {len(audit_results['outdated_files'])} outdated documentation files")
        
        if audit_results["deprecated_apis"]:
            recommendations.append(f"Update {len(audit_results['deprecated_apis'])} files with deprecated APIs")
        
        # Coverage recommendations
        total_expected = sum(len(files) for files in self.docs_structure.values())
        total_actual = audit_results["total_files"]
        coverage_percent = (total_actual / total_expected) * 100 if total_expected > 0 else 0
        
        if coverage_percent < 80:
            recommendations.append(f"Improve documentation coverage (currently {coverage_percent:.1f}%)")
        
        return recommendations
    
    def deprecate_legacy_apis(self, project: str = None) -> Dict[str, Any]:
        """Mark legacy APIs as deprecated."""
        self.logger.info("Marking legacy APIs as deprecated...")
        
        deprecation_results = {
            "timestamp": datetime.now().isoformat(),
            "project": project or "all",
            "files_updated": [],
            "apis_deprecated": [],
            "errors": []
        }
        
        # Find all Python files that use legacy APIs
        python_files = []
        if project:
            project_paths = {
                "router": Path("../router"),
                "atoms": Path("../atoms-mcp-prod"),
                "zen": Path("../zen-mcp-server")
            }
            if project in project_paths:
                python_files = list(project_paths[project].rglob("*.py"))
        else:
            # Check all projects
            for project_name, project_path in {
                "router": Path("../router"),
                "atoms": Path("../atoms-mcp-prod"),
                "zen": Path("../zen-mcp-server")
            }.items():
                if project_path.exists():
                    python_files.extend(project_path.rglob("*.py"))
        
        # Process each file
        for file_path in python_files:
            try:
                updated = self._deprecate_apis_in_file(file_path)
                if updated:
                    deprecation_results["files_updated"].append(str(file_path))
            except Exception as e:
                deprecation_results["errors"].append(f"Error processing {file_path}: {e}")
        
        # Update documentation files
        docs_files = list(Path("docs").rglob("*.md"))
        for file_path in docs_files:
            try:
                updated = self._add_deprecation_warnings_to_docs(file_path)
                if updated:
                    deprecation_results["files_updated"].append(str(file_path))
            except Exception as e:
                deprecation_results["errors"].append(f"Error processing {file_path}: {e}")
        
        deprecation_results["apis_deprecated"] = list(self.legacy_apis.keys())
        
        return deprecation_results
    
    def _deprecate_apis_in_file(self, file_path: Path) -> bool:
        """Add deprecation warnings to a Python file."""
        try:
            content = file_path.read_text()
            original_content = content
            
            # Add deprecation warnings for each legacy API
            for api_name, api_info in self.legacy_apis.items():
                old_method = api_info["old_method"]
                new_method = api_info["new_method"]
                replacement = api_info["replacement"]
                sunset_date = api_info["sunset_date"]
                
                # Check if the old method is used in the file
                if old_method in content:
                    # Add deprecation warning
                    warning = f'''
# DEPRECATED: {old_method}
# This method is deprecated and will be removed on {sunset_date}
# Use: {new_method}
# Replacement: {replacement}
'''
                    
                    # Find the line with the old method and add warning before it
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if old_method in line and not line.strip().startswith('#'):
                            lines.insert(i, warning)
                            break
                    
                    content = '\n'.join(lines)
            
            # Write updated content if changed
            if content != original_content:
                file_path.write_text(content)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to process {file_path}: {e}")
            return False
    
    def _add_deprecation_warnings_to_docs(self, file_path: Path) -> bool:
        """Add deprecation warnings to documentation files."""
        try:
            content = file_path.read_text()
            original_content = content
            
            # Add deprecation section if not present
            if "## Deprecated APIs" not in content:
                deprecation_section = '''
## Deprecated APIs

The following APIs are deprecated and will be removed in future versions:

'''
                for api_name, api_info in self.legacy_apis.items():
                    deprecation_section += f'''
### {api_name}
- **Old Method**: `{api_info["old_method"]}`
- **New Method**: `{api_info["new_method"]}`
- **Deprecation Date**: {api_info["deprecation_date"]}
- **Sunset Date**: {api_info["sunset_date"]}
- **Replacement**: {api_info["replacement"]}

'''
                
                # Add deprecation section before the end of the file
                content = content.rstrip() + "\n" + deprecation_section
            
            # Write updated content if changed
            if content != original_content:
                file_path.write_text(content)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to process {file_path}: {e}")
            return False
    
    def generate_final_documentation(self, project: str = None, output_dir: str = None) -> Dict[str, Any]:
        """Generate final documentation."""
        self.logger.info("Generating final documentation...")
        
        output_path = Path(output_dir) if output_dir else Path("docs/final")
        output_path.mkdir(parents=True, exist_ok=True)
        
        generation_results = {
            "timestamp": datetime.now().isoformat(),
            "project": project or "all",
            "output_directory": str(output_path),
            "files_generated": [],
            "errors": []
        }
        
        try:
            # Generate main README
            readme_content = self._generate_main_readme(project)
            readme_path = output_path / "README.md"
            readme_path.write_text(readme_content)
            generation_results["files_generated"].append(str(readme_path))
            
            # Generate API reference
            api_ref_content = self._generate_api_reference()
            api_ref_path = output_path / "API_REFERENCE.md"
            api_ref_path.write_text(api_ref_content)
            generation_results["files_generated"].append(str(api_ref_path))
            
            # Generate migration guide
            migration_content = self._generate_migration_guide()
            migration_path = output_path / "MIGRATION_GUIDE.md"
            migration_path.write_text(migration_content)
            generation_results["files_generated"].append(str(migration_path))
            
            # Generate changelog
            changelog_content = self._generate_changelog()
            changelog_path = output_path / "CHANGELOG.md"
            changelog_path.write_text(changelog_content)
            generation_results["files_generated"].append(str(changelog_path))
            
            # Copy existing documentation
            self._copy_existing_docs(output_path)
            
        except Exception as e:
            generation_results["errors"].append(f"Failed to generate documentation: {e}")
        
        return generation_results
    
    def _generate_main_readme(self, project: str = None) -> str:
        """Generate main README content."""
        return f"""# KInfra Phase 5: Complete Infrastructure Management

## Overview

KInfra Phase 5 provides comprehensive infrastructure management capabilities including process governance, tunnel governance, cleanup policies, and status monitoring. This version represents the culmination of the KInfra transformation project.

## Features

### Process Governance
- Metadata-based process tracking
- Project-scoped process management
- Automatic cleanup policies
- Process health monitoring

### Tunnel Governance
- Smart tunnel reuse
- Project-scoped credentials
- Lifecycle management
- Health monitoring

### Cleanup Policies
- Project-specific cleanup rules
- Global cleanup coordination
- Resource-type specific policies
- Configurable strategies

### Status Monitoring
- Real-time service status
- Tunnel connectivity monitoring
- Health dashboards
- Project summaries

### Resource Coordination
- Shared resource management
- Global resource registry
- Resource discovery
- Cross-project coordination

## Quick Start

### Installation

```bash
pip install pheno-sdk
```

### Basic Usage

```python
from pheno.infra.project_context import project_infra_context
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager

async with project_infra_context("my-project") as infra:
    # Process governance
    process_manager = ProcessGovernanceManager()
    
    # Tunnel governance
    tunnel_manager = TunnelGovernanceManager()
    
    # Your application code here
```

## Migration

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions.

## API Reference

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.

## Examples

See the `examples/` directory for comprehensive usage examples.

## Support

For support and questions, please refer to the documentation or create an issue.

## License

This project is licensed under the MIT License.
"""
    
    def _generate_api_reference(self) -> str:
        """Generate API reference content."""
        return """# KInfra API Reference

## Process Governance

### ProcessGovernanceManager

```python
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata

manager = ProcessGovernanceManager()

# Register a process
metadata = ProcessMetadata(
    project="my-project",
    service="my-service",
    pid=12345,
    command_line=["python", "app.py"],
    environment={{}},
    scope="local",
    resource_type="api",
    tags={{'web', 'rest'}}
)
manager.register_process(12345, metadata)

# Get project processes
processes = manager.get_project_processes("my-project")

# Cleanup project processes
stats = manager.cleanup_project_processes("my-project")
```

## Tunnel Governance

### TunnelGovernanceManager

```python
from pheno.infra.tunnel_governance import TunnelGovernanceManager

manager = TunnelGovernanceManager()

# Create a tunnel
tunnel = manager.create_tunnel(
    project="my-project",
    service="my-service",
    port=8000,
    provider="cloudflare",
    reuse_existing=True
)

# Get project tunnels
tunnels = manager.get_project_tunnels("my-project")

# Cleanup project tunnels
count = manager.cleanup_project_tunnels("my-project")
```

## Cleanup Policies

### CleanupPolicyManager

```python
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType

manager = CleanupPolicyManager()

# Create project policy
policy = manager.create_default_policy(
    project_name="my-project",
    strategy=CleanupStrategy.MODERATE
)

# Update cleanup rule
manager.update_project_rule(
    project_name="my-project",
    resource_type=ResourceType.PROCESS,
    strategy=CleanupStrategy.AGGRESSIVE,
    patterns=["my-project-*"],
    max_age=1800.0,
    force_cleanup=True
)

# Set project policy
manager.set_project_policy("my-project", policy)
```

## Status Monitoring

### StatusPageManager

```python
from pheno.infra.fallback_site.status_pages import StatusPageManager

manager = StatusPageManager()

# Update service status
manager.update_service_status(
    project_name="my-project",
    service_name="my-service",
    status="running",
    port=8000,
    health_status="healthy"
)

# Update tunnel status
manager.update_tunnel_status(
    project_name="my-project",
    service_name="my-service",
    status="active",
    hostname="my-service.example.com",
    provider="cloudflare"
)

# Generate status page
status_page = manager.generate_status_page("my-project", "status")
```

## Resource Coordination

### ResourceCoordinator

```python
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

deployment_manager = DeploymentManager()
coordinator = ResourceCoordinator(deployment_manager)

await coordinator.initialize()

# Get or deploy resource
resource = await coordinator.get_or_deploy_resource(
    "shared-redis",
    "redis",
    "global",
    {{"host": "localhost", "port": 6379, "db": 0}}
)

# Discover resources
resources = await coordinator.discover_resources()
```

## Project Context

### project_infra_context

```python
from pheno.infra.project_context import project_infra_context

async with project_infra_context("my-project") as infra:
    # All services in this context will be associated with "my-project"
    # Automatic cleanup and resource management
    pass
```

## Deprecated APIs

The following APIs are deprecated and will be removed in future versions:

### Port Allocator
- **Old**: `allocate_port(service_name, port)`
- **New**: `allocate_port(service_name, port, metadata={{}})`
- **Sunset**: 2024-06-01

### Service Infrastructure Manager
- **Old**: `register_process(pid, command_line)`
- **New**: `register_process(pid, command_line, metadata=ProcessMetadata(...))`
- **Sunset**: 2024-06-01

### Deployment Manager
- **Old**: `deploy_resource(name, type, mode, config)`
- **New**: Use `ResourceCoordinator.get_or_deploy_resource()`
- **Sunset**: 2024-06-01
"""
    
    def _generate_migration_guide(self) -> str:
        """Generate migration guide content."""
        return """# KInfra Migration Guide

## Overview

This guide provides step-by-step instructions for migrating existing projects to KInfra Phase 5 features.

## Migration Phases

### Phase 1: Enable Metadata
- Add metadata to port allocation calls
- Add metadata to process registration
- Enable metadata tracking in configuration

### Phase 2: Adopt ProjectInfraContext
- Wrap service initialization with ProjectInfraContext
- Update configuration for project isolation
- Test project-scoped resource management

### Phase 3: Resource Helpers
- Replace direct DeploymentManager with ResourceCoordinator
- Set up shared resource configuration
- Test resource coordination

### Phase 4: Advanced Features
- Add process governance
- Add tunnel governance
- Add cleanup policies
- Add status monitoring

## Project-Specific Guides

### Router Project
See [ROUTER_ADOPTION_GUIDE.md](migration/ROUTER_ADOPTION_GUIDE.md)

### Atoms Project
See [ATOMS_ADOPTION_GUIDE.md](migration/ATOMS_ADOPTION_GUIDE.md)

### Zen Project
See [ZEN_ADOPTION_GUIDE.md](migration/ZEN_ADOPTION_GUIDE.md)

## Migration Tools

### Automated Migration
```bash
# Generate migration scripts
python scripts/kinfra-migrate.py generate --project router --phase 1

# Validate migration
python scripts/kinfra-migrate.py validate --project router --phase 1

# Rollback if needed
python scripts/kinfra-migrate.py rollback --project router --phase 1
```

### Manual Migration
Follow the step-by-step instructions in the project-specific guides.

## Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Smoke Tests
```bash
python -m pytest tests/smoke/
```

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Use `kinfra port list` to check for conflicts
2. **Process Cleanup**: Use `kinfra process cleanup-stale` to clean up stale processes
3. **Tunnel Failures**: Check credentials with `kinfra tunnel list`
4. **Resource Conflicts**: Use `kinfra resource list` to check resource usage

### Debugging
1. Enable debug logging in configuration
2. Check KInfra status with `kinfra status show-global`
3. View logs with `kinfra logs --project <project>`

## Support

For migration support, please refer to the documentation or create an issue.
"""
    
    def _generate_changelog(self) -> str:
        """Generate changelog content."""
        return """# Changelog

## [5.0.0] - 2024-01-01

### Added
- Process governance with metadata tracking
- Tunnel governance with smart reuse
- Cleanup policies with project-specific rules
- Status monitoring with real-time dashboards
- Resource coordination with shared resources
- Project context management
- Comprehensive CLI tools
- Migration tools and scripts
- Extensive documentation and examples

### Changed
- Port allocation now requires metadata
- Process registration now requires ProcessMetadata
- Resource deployment now uses ResourceCoordinator
- All APIs now support project-scoped operations

### Deprecated
- `allocate_port(service_name, port)` - use `allocate_port(service_name, port, metadata={})`
- `register_process(pid, command_line)` - use `register_process(pid, command_line, metadata=ProcessMetadata(...))`
- Direct `DeploymentManager.deploy_resource()` - use `ResourceCoordinator.get_or_deploy_resource()`

### Removed
- Legacy port allocation without metadata
- Legacy process registration without metadata
- Direct resource deployment without coordination

### Fixed
- Port conflict resolution
- Process cleanup issues
- Resource coordination problems
- Tunnel management reliability

### Security
- Enhanced process isolation
- Secure tunnel credential management
- Resource access controls

## [4.0.0] - 2023-12-01

### Added
- Reverse proxy and fallback experience
- Project routing templates
- Health monitoring integration
- Fallback page customization

## [3.0.0] - 2023-11-01

### Added
- Resource coordination
- Global resource registry
- Resource reference cache
- Enhanced CLI commands

## [2.0.0] - 2023-10-01

### Added
- Project context layer
- ProjectInfraContext wrapper
- Project bootstrap/teardown helpers
- Project-specific logging and metrics

## [1.0.0] - 2023-09-01

### Added
- Core state and metadata enhancements
- ServiceInfo schema extensions
- Metadata threading through components
- Registry migration routines
"""
    
    def _copy_existing_docs(self, output_path: Path):
        """Copy existing documentation to output directory."""
        docs_source = Path("docs")
        if docs_source.exists():
            for item in docs_source.iterdir():
                if item.is_file():
                    shutil.copy2(item, output_path / item.name)
                elif item.is_dir():
                    shutil.copytree(item, output_path / item.name, dirs_exist_ok=True)
    
    def validate_documentation(self, project: str = None) -> Dict[str, Any]:
        """Validate documentation."""
        self.logger.info("Validating documentation...")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "project": project or "all",
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": [],
            "warnings": [],
            "errors": []
        }
        
        # Validate documentation files
        docs_root = Path("docs")
        if not docs_root.exists():
            validation_results["errors"].append("docs/ directory not found")
            return validation_results
        
        for file_path in docs_root.rglob("*.md"):
            if file_path.is_file():
                validation_results["total_files"] += 1
                
                try:
                    content = file_path.read_text()
                    
                    # Check for required sections
                    if "README" in file_path.name or "GUIDE" in file_path.name:
                        if not self._has_required_sections(content):
                            validation_results["warnings"].append(f"{file_path}: Missing required sections")
                    
                    # Check for broken links
                    broken_links = self._find_broken_links(content, file_path.parent)
                    if broken_links:
                        validation_results["warnings"].extend([f"{file_path}: Broken link: {link}" for link in broken_links])
                    
                    # Check for deprecated APIs
                    deprecated_apis = self._find_deprecated_apis_in_file(file_path)
                    if deprecated_apis:
                        validation_results["warnings"].extend([f"{file_path}: Uses deprecated API: {api['api']}" for api in deprecated_apis])
                    
                    validation_results["valid_files"] += 1
                    
                except Exception as e:
                    validation_results["invalid_files"].append(f"{file_path}: {e}")
                    validation_results["errors"].append(f"Failed to validate {file_path}: {e}")
        
        return validation_results
    
    def _has_required_sections(self, content: str) -> bool:
        """Check if content has required sections."""
        required_sections = ["## Overview", "## Usage", "## Examples"]
        return all(section in content for section in required_sections)
    
    def _find_broken_links(self, content: str, base_path: Path) -> List[str]:
        """Find broken links in content."""
        broken_links = []
        
        # Find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        
        for text, link in matches:
            if link.startswith('http'):
                # External link - could check if it's accessible
                continue
            elif link.startswith('#'):
                # Anchor link - check if anchor exists
                anchor = link[1:]
                if anchor not in content:
                    broken_links.append(link)
            else:
                # Local file link
                link_path = base_path / link
                if not link_path.exists():
                    broken_links.append(link)
        
        return broken_links
    
    def create_sunset_timeline(self, project: str = None) -> Dict[str, Any]:
        """Create sunset timeline for deprecated APIs."""
        self.logger.info("Creating sunset timeline...")
        
        timeline = {
            "timestamp": datetime.now().isoformat(),
            "project": project or "all",
            "sunset_schedule": [],
            "recommendations": []
        }
        
        # Create sunset schedule
        for api_name, api_info in self.legacy_apis.items():
            timeline["sunset_schedule"].append({
                "api": api_name,
                "deprecation_date": api_info["deprecation_date"],
                "sunset_date": api_info["sunset_date"],
                "days_remaining": (datetime.strptime(api_info["sunset_date"], "%Y-%m-%d") - datetime.now()).days,
                "replacement": api_info["replacement"]
            })
        
        # Generate recommendations
        timeline["recommendations"] = [
            "Update all code to use new APIs before sunset dates",
            "Test thoroughly with new APIs before removing old ones",
            "Communicate sunset timeline to all users",
            "Provide migration support during transition period",
            "Monitor usage of deprecated APIs and provide warnings"
        ]
        
        return timeline


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="KInfra Documentation Finalization Tool")
    parser.add_argument("command", choices=["audit", "deprecate", "generate", "validate", "sunset"], help="Command to execute")
    parser.add_argument("--project", choices=["router", "atoms", "zen", "all"], help="Target project")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Migration phase")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize docs finalizer
    finalizer = KInfraDocsFinalizer(verbose=args.verbose)
    
    # Execute command
    if args.command == "audit":
        results = finalizer.audit_documentation(args.project)
        print(json.dumps(results, indent=2))
    
    elif args.command == "deprecate":
        results = finalizer.deprecate_legacy_apis(args.project)
        print(json.dumps(results, indent=2))
    
    elif args.command == "generate":
        results = finalizer.generate_final_documentation(args.project, args.output)
        print(json.dumps(results, indent=2))
    
    elif args.command == "validate":
        results = finalizer.validate_documentation(args.project)
        print(json.dumps(results, indent=2))
    
    elif args.command == "sunset":
        results = finalizer.create_sunset_timeline(args.project)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())