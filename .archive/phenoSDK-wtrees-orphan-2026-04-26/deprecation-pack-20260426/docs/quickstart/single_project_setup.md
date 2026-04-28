# KInfra Quickstart: Single Project Setup

This guide walks you through setting up KInfra for a single project with all Phase 5 features (Process Governance, Tunnel Governance, Cleanup Policies, and Status Pages).

## Prerequisites

- Python 3.11+
- pip or poetry
- Basic understanding of Python projects

## Installation

```bash
# Install pheno-sdk with infra extras
pip install pheno-sdk[infra]

# Or with poetry
poetry add pheno-sdk[infra]
```

## Quick Start

### 1. Initialize KInfra Configuration

```bash
# Initialize KInfra configuration
kinfra config init --project my-api-project

# This creates:
# - ~/.kinfra/config/kinfra.yaml
# - Project-specific cleanup policies
# - Default routing configuration
```

### 2. Basic Project Setup

```python
from pheno.infra.project_context import project_infra_context
from pheno.infra.config_schemas import KInfraConfigManager

# Load configuration
config_manager = KInfraConfigManager()
config = config_manager.load()

# Use project context for infrastructure management
with project_infra_context("my-api-project") as infra:
    # Start your services
    infra.start_service("api-server", port=8000)
    infra.start_service("worker", port=8001)
    
    # Create tunnels
    tunnel = infra.create_tunnel("api-server", port=8000)
    print(f"API available at: {tunnel.public_url}")
    
    # Your application code here
    # ...
```

### 3. Process Governance

```python
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata

# Create process governance manager
process_manager = ProcessGovernanceManager()

# Register your processes with metadata
metadata = ProcessMetadata(
    project="my-api-project",
    service="api-server",
    pid=12345,
    command_line=["python", "api_server.py"],
    environment={"PROJECT": "my-api-project"},
    scope="local",
    resource_type="api",
    tags={"web", "rest"}
)

process_manager.register_process(12345, metadata)

# Clean up processes by project
stats = process_manager.cleanup_project_processes("my-api-project")
print(f"Cleaned up {stats['terminated']} processes")
```

### 4. Tunnel Governance

```python
from pheno.infra.tunnel_governance import TunnelGovernanceManager

# Create tunnel governance manager
tunnel_manager = TunnelGovernanceManager()

# Create tunnel with smart reuse
tunnel_info = tunnel_manager.create_tunnel(
    project="my-api-project",
    service="api-server",
    port=8000,
    provider="cloudflare",
    reuse_existing=True
)

# Set project-specific credentials
tunnel_manager.set_credentials(
    project="my-api-project",
    service="api-server",
    provider="cloudflare",
    credentials={"token": "your-cloudflare-token"}
)
```

### 5. Cleanup Policies

```python
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType

# Create cleanup policy manager
cleanup_manager = CleanupPolicyManager()

# Initialize project cleanup policy
policy = cleanup_manager.create_default_policy(
    project_name="my-api-project",
    strategy=CleanupStrategy.MODERATE
)

# Customize cleanup rules
cleanup_manager.update_project_rule(
    project_name="my-api-project",
    resource_type=ResourceType.PROCESS,
    strategy=CleanupStrategy.AGGRESSIVE,
    patterns=["my-api-project-*"],
    max_age=1800.0,
    force_cleanup=True
)
```

### 6. Status Pages

```python
from pheno.infra.fallback_site.status_pages import StatusPageManager

# Create status page manager
status_manager = StatusPageManager()

# Update service status
status_manager.update_service_status(
    project_name="my-api-project",
    service_name="api-server",
    status="running",
    port=8000,
    health_status="healthy"
)

# Generate status page
status_page = status_manager.generate_status_page("my-api-project", "status")
print(status_page)
```

## CLI Usage

### Process Management

```bash
# Register a process
kinfra process register my-api-project api-server 12345 \
  --command-line '["python", "api_server.py"]' \
  --environment '{"PROJECT": "my-api-project"}' \
  --scope local \
  --resource-type api

# Clean up processes
kinfra process cleanup-project my-api-project --force
kinfra process cleanup-service api-server --force
kinfra process cleanup-stale --max-age 3600
```

### Tunnel Management

```bash
# Create a tunnel
kinfra tunnel create my-api-project api-server 8000 \
  --provider cloudflare \
  --hostname api.example.com \
  --reuse

# Stop a tunnel
kinfra tunnel stop my-tunnel-123

# Set credentials
kinfra tunnel set-credentials my-api-project api-server cloudflare credentials.json
```

### Cleanup Policy Management

```bash
# Initialize cleanup policy
kinfra cleanup init-project my-api-project --strategy moderate

# Set cleanup rule
kinfra cleanup set-rule my-api-project process \
  --strategy aggressive \
  --patterns "my-api-project-*" \
  --max-age 1800 \
  --force

# Show cleanup policy
kinfra cleanup show-policy my-api-project
```

### Status Monitoring

```bash
# Show project status
kinfra status show-project my-api-project --format html
kinfra status show-project my-api-project --format json

# List all projects
kinfra status list-projects

# Show statistics
kinfra stats
```

## Configuration

### Basic Configuration

Create `~/.kinfra/config/kinfra.yaml`:

```yaml
app_name: "my-api-project"
debug: false
log_level: "INFO"
environment: "development"

process_governance:
  enable_metadata_tracking: true
  max_process_age: 3600.0
  cleanup_interval: 300.0
  force_cleanup: false

tunnel_governance:
  default_lifecycle_policy: "smart"
  tunnel_reuse_threshold: 1800.0
  max_tunnel_age: 7200.0
  credential_scope: "project"

global_cleanup_policy:
  default_strategy: "conservative"
  max_concurrent_cleanups: 5
  cleanup_timeout: 300.0
  enabled: true

status_pages:
  auto_refresh_interval: 5
  include_service_details: true
  include_tunnel_details: true
  include_health_metrics: true
  theme: "default"

projects:
  my-api-project:
    project_name: "my-api-project"
    default_strategy: "moderate"
    enabled: true
    rules:
      process:
        resource_type: "process"
        strategy: "moderate"
        patterns: ["my-api-project-*"]
        max_age: 3600.0
        force_cleanup: false
        enabled: true
      tunnel:
        resource_type: "tunnel"
        strategy: "conservative"
        patterns: ["my-api-project-*"]
        max_age: 7200.0
        force_cleanup: false
        enabled: true

project_routing:
  my-api-project:
    project_name: "my-api-project"
    domain: "api.example.com"
    base_path: "/"
    enable_health_checks: true
    health_check_interval: 5.0
    health_check_timeout: 2.0
    fallback_enabled: true
    maintenance_enabled: false
```

### Environment Variables

You can override configuration using environment variables:

```bash
export KINFRA_DEBUG=true
export KINFRA_LOG_LEVEL=DEBUG
export KINFRA_PROCESS_GOVERNANCE__MAX_PROCESS_AGE=7200
export KINFRA_TUNNEL_GOVERNANCE__DEFAULT_LIFECYCLE_POLICY=reuse
export KINFRA_GLOBAL_CLEANUP_POLICY__DEFAULT_STRATEGY=aggressive
```

## Complete Example

Here's a complete example that demonstrates all Phase 5 features:

```python
#!/usr/bin/env python3
"""
Complete KInfra single project example with all Phase 5 features.
"""

import asyncio
import time
from pathlib import Path

from pheno.infra.project_context import project_infra_context
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.config_schemas import KInfraConfigManager


async def main():
    """Main example function."""
    print("🚀 Starting KInfra single project example...")
    
    # Initialize configuration
    config_manager = KInfraConfigManager()
    config = config_manager.load()
    print(f"✅ Configuration loaded: {config.app_name}")
    
    # Initialize managers
    process_manager = ProcessGovernanceManager()
    tunnel_manager = TunnelGovernanceManager()
    cleanup_manager = CleanupPolicyManager()
    status_manager = StatusPageManager()
    
    project_name = "my-api-project"
    
    # Set up cleanup policies
    print("📋 Setting up cleanup policies...")
    policy = cleanup_manager.create_default_policy(
        project_name=project_name,
        strategy=CleanupStrategy.MODERATE
    )
    print(f"✅ Cleanup policy created: {policy.project_name}")
    
    # Use project context for infrastructure management
    with project_infra_context(project_name) as infra:
        print("🏗️ Starting infrastructure...")
        
        # Start services
        api_port = infra.start_service("api-server", port=8000)
        worker_port = infra.start_service("worker", port=8001)
        print(f"✅ Services started: API={api_port}, Worker={worker_port}")
        
        # Register processes with metadata
        print("📝 Registering processes...")
        api_metadata = ProcessMetadata(
            project=project_name,
            service="api-server",
            pid=12345,
            command_line=["python", "api_server.py"],
            environment={"PROJECT": project_name},
            scope="local",
            resource_type="api",
            tags={"web", "rest"}
        )
        process_manager.register_process(12345, api_metadata)
        
        worker_metadata = ProcessMetadata(
            project=project_name,
            service="worker",
            pid=12346,
            command_line=["python", "worker.py"],
            environment={"PROJECT": project_name},
            scope="local",
            resource_type="worker",
            tags={"background", "queue"}
        )
        process_manager.register_process(12346, worker_metadata)
        print("✅ Processes registered")
        
        # Create tunnels
        print("🌐 Creating tunnels...")
        api_tunnel = tunnel_manager.create_tunnel(
            project=project_name,
            service="api-server",
            port=api_port,
            provider="cloudflare",
            reuse_existing=True
        )
        print(f"✅ API tunnel created: {api_tunnel.hostname}")
        
        # Update status
        print("📊 Updating status...")
        status_manager.update_service_status(
            project_name=project_name,
            service_name="api-server",
            status="running",
            port=api_port,
            health_status="healthy"
        )
        status_manager.update_service_status(
            project_name=project_name,
            service_name="worker",
            status="running",
            port=worker_port,
            health_status="healthy"
        )
        print("✅ Status updated")
        
        # Generate status page
        status_page = status_manager.generate_status_page(project_name, "status")
        print("📄 Status page generated")
        
        # Simulate some work
        print("⏳ Simulating work...")
        await asyncio.sleep(5)
        
        # Show statistics
        print("📈 Showing statistics...")
        process_stats = process_manager.get_cleanup_stats()
        tunnel_stats = tunnel_manager.get_tunnel_stats()
        print(f"Process stats: {process_stats}")
        print(f"Tunnel stats: {tunnel_stats}")
        
        print("✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

1. **Explore Shared Resource Setup**: See the [Shared Resource Setup Guide](shared_resource_setup.md)
2. **Read the CLI Reference**: See the [CLI Reference Guide](cli_reference.md)
3. **Learn about Integration Testing**: See the [Integration Testing Guide](integration_testing.md)
4. **Customize Configuration**: See the [Configuration Guide](configuration.md)

## Troubleshooting

### Common Issues

1. **Process not found**: Ensure the process is registered with correct metadata
2. **Tunnel creation failed**: Check tunnel provider credentials and network connectivity
3. **Cleanup not working**: Verify cleanup policies are enabled and configured correctly
4. **Status page not updating**: Ensure status callbacks are registered and called

### Getting Help

- Check the [CLI Reference](cli_reference.md) for command details
- See the [Configuration Guide](configuration.md) for advanced configuration
- Review the [Integration Testing Guide](integration_testing.md) for testing patterns

## Conclusion

This quickstart guide has shown you how to set up KInfra for a single project with all Phase 5 features. You now have:

- Process governance with metadata-based cleanup
- Tunnel governance with smart reuse
- Configurable cleanup policies
- Enhanced status pages
- Comprehensive CLI commands

You're ready to build sophisticated applications with shared infrastructure management!