# Phase 5: Process & Tunnel Governance - Implementation Complete

## Overview

Phase 5 of the KInfra transformation implements sophisticated process and tunnel governance features, building upon the reverse proxy and fallback experience from Phase 4. This phase focuses on enhanced process management, tunnel lifecycle management, configurable cleanup policies, and status monitoring.

## Key Features Implemented

### 1. Process Governance with Metadata ✅
- **Metadata-Based Process Identification**: Track processes by project, service, scope, and resource type
- **Project-Specific Cleanup**: Clean up processes by project or service with metadata matching
- **Process Lifecycle Tracking**: Monitor process creation, updates, and cleanup
- **Configurable Cleanup Policies**: Conservative, moderate, and aggressive cleanup strategies

### 2. Tunnel Lifecycle Management ✅
- **Smart Tunnel Reuse**: Reuse existing tunnels when possible based on health and age
- **Project-Specific Credentials**: Manage tunnel credentials per project and service
- **Tunnel Health Monitoring**: Track tunnel status and health with automatic cleanup
- **Credential Sharing**: Share credentials within projects for efficiency

### 3. Configurable Cleanup Policies ✅
- **Resource-Specific Rules**: Different cleanup strategies for processes, tunnels, ports, files, etc.
- **Project-Specific Policies**: Customize cleanup behavior per project
- **Policy Configuration Files**: JSON/YAML configuration with import/export
- **Cleanup Strategy Enforcement**: Conservative, moderate, and aggressive strategies

### 4. Enhanced Status Pages ✅
- **Service Status Tracking**: Real-time service status with health monitoring
- **Tunnel Status Display**: Tunnel health and connectivity status
- **Project Status Dashboards**: Overall project health with service/tunnel aggregation
- **Maintenance Mode Support**: Enhanced maintenance pages with project context

## Architecture

```
Phase 5: Process & Tunnel Governance
├── ProcessGovernanceManager
│   ├── ProcessMetadata (project, service, scope tracking)
│   ├── Project/Service Process Tracking
│   ├── Metadata-Based Cleanup
│   └── Process Lifecycle Management
├── TunnelGovernanceManager
│   ├── TunnelInfo (tunnel status and metadata)
│   ├── TunnelCredentials (project-specific credentials)
│   ├── Smart Tunnel Reuse
│   └── Tunnel Health Monitoring
├── CleanupPolicyManager
│   ├── CleanupRule (resource-specific rules)
│   ├── ProjectCleanupPolicy (project-specific policies)
│   ├── CleanupStrategy (conservative, moderate, aggressive)
│   └── Policy Configuration Files
└── StatusPageManager
    ├── ServiceStatus (service health tracking)
    ├── TunnelStatus (tunnel health tracking)
    ├── ProjectStatus (project aggregation)
    └── Enhanced Status Pages
```

## Usage Examples

### Process Governance

```python
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata

# Create process governance manager
process_manager = ProcessGovernanceManager()

# Register a process with metadata
metadata = ProcessMetadata(
    project="api-project",
    service="api-server",
    pid=1001,
    command_line=["python", "api_server.py"],
    environment={"PROJECT": "api-project", "SERVICE": "api-server"},
    scope="local",
    resource_type="api",
    tags={"web", "rest"},
)

process_manager.register_process(1001, metadata)

# Clean up processes by project
stats = process_manager.cleanup_project_processes("api-project")
print(f"Cleaned up {stats['terminated']} processes")

# Clean up processes by service
stats = process_manager.cleanup_service_processes("api-server")
print(f"Cleaned up {stats['terminated']} processes")

# Clean up stale processes
stats = process_manager.cleanup_stale_processes(max_age=3600.0)
print(f"Cleaned up {stats['terminated']} stale processes")
```

### Tunnel Governance

```python
from pheno.infra.tunnel_governance import TunnelGovernanceManager

# Create tunnel governance manager
tunnel_manager = TunnelGovernanceManager()

# Create a tunnel with smart reuse
tunnel_info = tunnel_manager.create_tunnel(
    project="api-project",
    service="api-server",
    port=8001,
    provider="cloudflare",
    hostname="api.example.com",
    reuse_existing=True,
)

# Set project-specific credentials
credentials = {
    "token": "api-token-123",
    "account_id": "account-456",
    "zone_id": "zone-789",
}

tunnel_manager.set_credentials(
    project="api-project",
    service="api-server",
    provider="cloudflare",
    credentials=credentials,
)

# Update tunnel status
tunnel_manager.update_tunnel_status(
    tunnel_id=tunnel_info.tunnel_id,
    status="active",
    hostname="api.example.com",
)

# Get tunnel statistics
stats = tunnel_manager.get_tunnel_stats()
print(f"Total tunnels: {stats['total_tunnels']}")
print(f"Active tunnels: {stats['active_tunnels']}")
```

### Cleanup Policies

```python
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType, CleanupRule

# Create cleanup policy manager
cleanup_manager = CleanupPolicyManager()

# Create default policy for a project
policy = cleanup_manager.create_default_policy(
    project_name="api-project",
    strategy=CleanupStrategy.MODERATE,
)

# Update specific cleanup rule
rule = CleanupRule(
    resource_type=ResourceType.PROCESS,
    strategy=CleanupStrategy.AGGRESSIVE,
    patterns=["api-project-*", "*api-project*"],
    exclude_patterns=["system", "kernel"],
    max_age=1800.0,  # 30 minutes
    force_cleanup=True,
    enabled=True,
)

cleanup_manager.update_project_rule("api-project", ResourceType.PROCESS, rule)

# Get cleanup strategy for a project and resource type
strategy = cleanup_manager.get_cleanup_strategy("api-project", ResourceType.PROCESS)
print(f"Cleanup strategy: {strategy.value}")

# Export policy
policy_json = cleanup_manager.export_policy("api-project", "json")
```

### Status Pages

```python
from pheno.infra.fallback_site.status_pages import StatusPageManager

# Create status page manager
status_manager = StatusPageManager()

# Update service status
status_manager.update_service_status(
    project_name="api-project",
    service_name="api-server",
    status="running",
    port=8001,
    host="localhost",
    pid=1001,
    uptime=3600.0,
    health_status="healthy",
    metadata={"version": "1.0.0", "environment": "production"},
)

# Update tunnel status
status_manager.update_tunnel_status(
    project_name="api-project",
    tunnel_id="api-tunnel-123",
    service_name="api-server",
    hostname="api.example.com",
    port=8001,
    status="active",
    provider="cloudflare",
    health_status="healthy",
)

# Set maintenance mode
status_manager.set_maintenance_mode(
    project_name="api-project",
    enabled=True,
    message="API project is under maintenance for updates",
)

# Generate status page
status_page = status_manager.generate_status_page("api-project", "status")
print(f"Generated status page: {len(status_page)} characters")

# Generate project summary
summary = status_manager.generate_project_summary("api-project")
print(f"Project summary: {summary}")
```

## CLI Usage

### Process Management

```bash
# Register a process with metadata
pheno process register api-project api-server 1001 \
  --command-line '["python", "api_server.py"]' \
  --environment '{"PROJECT": "api-project"}' \
  --scope local \
  --resource-type api \
  --tags "web,rest"

# Clean up processes by project
pheno process cleanup-project api-project --force

# Clean up processes by service
pheno process cleanup-service api-server --force

# Clean up stale processes
pheno process cleanup-stale --max-age 3600

# List processes for a project
pheno process list-project api-project

# List processes for a service
pheno process list-service api-server
```

### Tunnel Management

```bash
# Create a tunnel
pheno tunnel create api-project api-server 8001 \
  --provider cloudflare \
  --hostname api.example.com \
  --reuse

# Stop a tunnel
pheno tunnel stop api-tunnel-123

# Clean up a tunnel
pheno tunnel cleanup api-tunnel-123

# Clean up all tunnels for a project
pheno tunnel cleanup-project api-project

# List tunnels for a project
pheno tunnel list-project api-project

# Set credentials
pheno tunnel set-credentials api-project api-server cloudflare credentials.json
```

### Cleanup Policy Management

```bash
# Initialize cleanup policy for a project
pheno cleanup init-project api-project --strategy moderate

# Set cleanup rule
pheno cleanup set-rule api-project process \
  --strategy aggressive \
  --patterns "api-project-*,*api-project*" \
  --exclude-patterns "system,kernel" \
  --max-age 1800 \
  --force \
  --enabled

# Show cleanup policy
pheno cleanup show-policy api-project
```

### Status Monitoring

```bash
# Show project status
pheno status show-project api-project --format html
pheno status show-project api-project --format json

# List all projects
pheno status list-projects

# Show governance statistics
pheno stats
```

## Key Benefits

### 1. **Enhanced Process Management**
- Metadata-based process identification and tracking
- Project and service-specific cleanup strategies
- Configurable cleanup policies with different strategies
- Process lifecycle monitoring and management

### 2. **Sophisticated Tunnel Management**
- Smart tunnel reuse based on health and age
- Project-specific credential management
- Tunnel health monitoring and automatic cleanup
- Credential sharing within projects

### 3. **Configurable Cleanup Policies**
- Resource-specific cleanup rules (processes, tunnels, ports, files, etc.)
- Project-specific policy customization
- Conservative, moderate, and aggressive cleanup strategies
- Policy configuration files with import/export

### 4. **Enhanced Status Monitoring**
- Real-time service and tunnel status tracking
- Project-level health aggregation
- Enhanced status pages with service/tunnel information
- Maintenance mode support with project context

### 5. **Developer Experience**
- Rich CLI commands for all governance features
- Comprehensive examples and documentation
- Integration with existing KInfra components
- Flexible configuration and customization

## File Structure

```
pheno-sdk/src/pheno/infra/
├── process_governance.py      # Process governance with metadata
├── tunnel_governance.py       # Tunnel lifecycle management
├── cleanup_policies.py        # Configurable cleanup policies
├── fallback_site/
│   └── status_pages.py        # Enhanced status pages
├── cli/
│   └── process_governance_cli.py  # CLI commands
└── examples/
    └── phase5_process_governance_example.py  # Comprehensive examples
```

## Integration with Previous Phases

Phase 5 builds upon the foundation from previous phases:

- **Phase 2 (Project Context)**: Uses `ProjectInfraContext` for project-scoped infrastructure
- **Phase 3 (Resource Coordination)**: Integrates with `ResourceCoordinator` for resource management
- **Phase 4 (Reverse Proxy)**: Enhances fallback pages with service/tunnel status
- **Phase 5 (Process Governance)**: Adds sophisticated process and tunnel management

## Testing

Run the comprehensive example to see Phase 5 in action:

```bash
cd pheno-sdk
python examples/phase5_process_governance_example.py
```

This demonstrates all the key features of Phase 5 process and tunnel governance.

## Next Steps (Phase 6)

Phase 5 provides the foundation for Phase 6 (Configuration & Developer Experience), which will focus on:

1. **Configuration Management**: Merge new options into config-kit schemas
2. **Documentation**: Author quickstart guides and CLI reference
3. **Integration Testing**: Cover multi-project and shared resource scenarios
4. **Developer Experience**: Improve ergonomics and missing features

## Conclusion

Phase 5 successfully implements sophisticated process and tunnel governance features, providing metadata-based process management, smart tunnel lifecycle management, configurable cleanup policies, and enhanced status monitoring. The implementation enables fine-grained control over process and tunnel lifecycles while maintaining project isolation and providing excellent developer experience.

The process and tunnel governance layer makes it easy to manage complex multi-service applications with shared infrastructure, providing enterprise-grade process management and tunnel governance capabilities.