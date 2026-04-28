# KInfra CLI Reference

This comprehensive CLI reference covers all KInfra commands for Phase 5 features (Process Governance, Tunnel Governance, Cleanup Policies, and Status Pages).

## Table of Contents

- [Configuration Commands](#configuration-commands)
- [Process Governance Commands](#process-governance-commands)
- [Tunnel Governance Commands](#tunnel-governance-commands)
- [Cleanup Policy Commands](#cleanup-policy-commands)
- [Status Monitoring Commands](#status-monitoring-commands)
- [Resource Management Commands](#resource-management-commands)
- [Project Management Commands](#project-management-commands)
- [Global Commands](#global-commands)

## Configuration Commands

### `kinfra config init`

Initialize KInfra configuration.

```bash
# Initialize global configuration
kinfra config init --global

# Initialize project-specific configuration
kinfra config init --project PROJECT_NAME

# Initialize with custom config file
kinfra config init --project PROJECT_NAME --config-file /path/to/config.yaml

# Initialize with environment prefix
kinfra config init --project PROJECT_NAME --env-prefix KINFRA_
```

**Options:**
- `--global`: Initialize global configuration
- `--project PROJECT_NAME`: Initialize project-specific configuration
- `--config-file PATH`: Use custom configuration file
- `--env-prefix PREFIX`: Environment variable prefix (default: KINFRA_)
- `--force`: Overwrite existing configuration

### `kinfra config show`

Show current configuration.

```bash
# Show all configuration
kinfra config show

# Show specific section
kinfra config show --section process_governance
kinfra config show --section tunnel_governance
kinfra config show --section cleanup_policies
kinfra config show --section status_pages

# Show project-specific configuration
kinfra config show --project PROJECT_NAME

# Show in different formats
kinfra config show --format yaml
kinfra config show --format json
kinfra config show --format table
```

**Options:**
- `--section SECTION`: Show specific configuration section
- `--project PROJECT_NAME`: Show project-specific configuration
- `--format FORMAT`: Output format (yaml, json, table)
- `--verbose`: Show detailed information

### `kinfra config set`

Set configuration values.

```bash
# Set global configuration
kinfra config set debug true
kinfra config set log_level DEBUG
kinfra config set process_governance.max_process_age 7200

# Set project-specific configuration
kinfra config set --project PROJECT_NAME cleanup_policy.default_strategy aggressive
kinfra config set --project PROJECT_NAME tunnel_governance.credential_scope service
```

**Options:**
- `--project PROJECT_NAME`: Set project-specific configuration
- `--global`: Set global configuration
- `--value VALUE`: Configuration value

### `kinfra config export`

Export configuration to file.

```bash
# Export all configuration
kinfra config export --output config.yaml

# Export project-specific configuration
kinfra config export --project PROJECT_NAME --output project-config.yaml

# Export specific section
kinfra config export --section process_governance --output process-config.yaml
```

**Options:**
- `--project PROJECT_NAME`: Export project-specific configuration
- `--section SECTION`: Export specific configuration section
- `--output PATH`: Output file path
- `--format FORMAT`: Output format (yaml, json)

### `kinfra config import`

Import configuration from file.

```bash
# Import configuration
kinfra config import --input config.yaml

# Import project-specific configuration
kinfra config import --project PROJECT_NAME --input project-config.yaml

# Import with merge
kinfra config import --input config.yaml --merge
```

**Options:**
- `--project PROJECT_NAME`: Import project-specific configuration
- `--input PATH`: Input file path
- `--merge`: Merge with existing configuration
- `--force`: Overwrite existing configuration

## Process Governance Commands

### `kinfra process register`

Register a process with metadata.

```bash
# Basic registration
kinfra process register PROJECT_NAME SERVICE_NAME PID

# With command line
kinfra process register PROJECT_NAME SERVICE_NAME PID \
  --command-line '["python", "api_server.py"]'

# With environment variables
kinfra process register PROJECT_NAME SERVICE_NAME PID \
  --environment '{"PROJECT": "api-project", "ENV": "production"}'

# With full metadata
kinfra process register PROJECT_NAME SERVICE_NAME PID \
  --command-line '["python", "api_server.py"]' \
  --environment '{"PROJECT": "api-project"}' \
  --scope local \
  --resource-type api \
  --tags "web,rest,api"
```

**Options:**
- `--command-line JSON`: Process command line as JSON array
- `--environment JSON`: Environment variables as JSON object
- `--scope SCOPE`: Process scope (local, global, tenanted)
- `--resource-type TYPE`: Resource type (api, web, worker, etc.)
- `--tags TAGS`: Comma-separated tags
- `--metadata JSON`: Additional metadata as JSON object

### `kinfra process unregister`

Unregister a process.

```bash
# Unregister by PID
kinfra process unregister PID

# Unregister by project and service
kinfra process unregister --project PROJECT_NAME --service SERVICE_NAME

# Unregister all processes for a project
kinfra process unregister --project PROJECT_NAME --all
```

**Options:**
- `--project PROJECT_NAME`: Project name
- `--service SERVICE_NAME`: Service name
- `--all`: Unregister all processes for project/service

### `kinfra process list`

List registered processes.

```bash
# List all processes
kinfra process list

# List processes by project
kinfra process list --project PROJECT_NAME

# List processes by service
kinfra process list --service SERVICE_NAME

# List with filters
kinfra process list --resource-type api --scope local
```

**Options:**
- `--project PROJECT_NAME`: Filter by project
- `--service SERVICE_NAME`: Filter by service
- `--resource-type TYPE`: Filter by resource type
- `--scope SCOPE`: Filter by scope
- `--format FORMAT`: Output format (table, json, yaml)

### `kinfra process cleanup-project`

Clean up processes by project.

```bash
# Clean up all processes for a project
kinfra process cleanup-project PROJECT_NAME

# Clean up with force
kinfra process cleanup-project PROJECT_NAME --force

# Clean up with timeout
kinfra process cleanup-project PROJECT_NAME --timeout 60

# Clean up with dry run
kinfra process cleanup-project PROJECT_NAME --dry-run
```

**Options:**
- `--force`: Force cleanup of processes
- `--timeout SECONDS`: Cleanup timeout in seconds
- `--dry-run`: Show what would be cleaned up
- `--verbose`: Show detailed output

### `kinfra process cleanup-service`

Clean up processes by service.

```bash
# Clean up all processes for a service
kinfra process cleanup-service SERVICE_NAME

# Clean up with force
kinfra process cleanup-service SERVICE_NAME --force

# Clean up with timeout
kinfra process cleanup-service SERVICE_NAME --timeout 60
```

**Options:**
- `--force`: Force cleanup of processes
- `--timeout SECONDS`: Cleanup timeout in seconds
- `--dry-run`: Show what would be cleaned up
- `--verbose`: Show detailed output

### `kinfra process cleanup-stale`

Clean up stale processes.

```bash
# Clean up stale processes
kinfra process cleanup-stale

# Clean up with max age
kinfra process cleanup-stale --max-age 3600

# Clean up with force
kinfra process cleanup-stale --force

# Clean up with dry run
kinfra process cleanup-stale --dry-run
```

**Options:**
- `--max-age SECONDS`: Maximum age for processes
- `--force`: Force cleanup of processes
- `--dry-run`: Show what would be cleaned up
- `--verbose`: Show detailed output

### `kinfra process stats`

Show process statistics.

```bash
# Show process statistics
kinfra process stats

# Show statistics for project
kinfra process stats --project PROJECT_NAME

# Show statistics for service
kinfra process stats --service SERVICE_NAME
```

**Options:**
- `--project PROJECT_NAME`: Filter by project
- `--service SERVICE_NAME`: Filter by service
- `--format FORMAT`: Output format (table, json, yaml)

## Tunnel Governance Commands

### `kinfra tunnel create`

Create a tunnel.

```bash
# Basic tunnel creation
kinfra tunnel create PROJECT_NAME SERVICE_NAME PORT

# With provider
kinfra tunnel create PROJECT_NAME SERVICE_NAME PORT --provider cloudflare

# With hostname
kinfra tunnel create PROJECT_NAME SERVICE_NAME PORT \
  --provider cloudflare \
  --hostname api.example.com

# With reuse
kinfra tunnel create PROJECT_NAME SERVICE_NAME PORT \
  --provider cloudflare \
  --reuse

# With credentials
kinfra tunnel create PROJECT_NAME SERVICE_NAME PORT \
  --provider cloudflare \
  --credentials credentials.json
```

**Options:**
- `--provider PROVIDER`: Tunnel provider (cloudflare, ngrok, localtunnel)
- `--hostname HOSTNAME`: Custom hostname
- `--reuse`: Reuse existing tunnel if available
- `--credentials PATH`: Credentials file path
- `--timeout SECONDS`: Creation timeout

### `kinfra tunnel list`

List tunnels.

```bash
# List all tunnels
kinfra tunnel list

# List tunnels by project
kinfra tunnel list --project PROJECT_NAME

# List tunnels by service
kinfra tunnel list --service SERVICE_NAME

# List tunnels by provider
kinfra tunnel list --provider cloudflare
```

**Options:**
- `--project PROJECT_NAME`: Filter by project
- `--service SERVICE_NAME`: Filter by service
- `--provider PROVIDER`: Filter by provider
- `--status STATUS`: Filter by status
- `--format FORMAT`: Output format (table, json, yaml)

### `kinfra tunnel stop`

Stop a tunnel.

```bash
# Stop tunnel by ID
kinfra tunnel stop TUNNEL_ID

# Stop tunnel by project and service
kinfra tunnel stop --project PROJECT_NAME --service SERVICE_NAME

# Stop all tunnels for project
kinfra tunnel stop --project PROJECT_NAME --all
```

**Options:**
- `--project PROJECT_NAME`: Project name
- `--service SERVICE_NAME`: Service name
- `--all`: Stop all tunnels for project/service
- `--force`: Force stop tunnel

### `kinfra tunnel cleanup`

Clean up a tunnel.

```bash
# Clean up tunnel by ID
kinfra tunnel cleanup TUNNEL_ID

# Clean up tunnel by project and service
kinfra tunnel cleanup --project PROJECT_NAME --service SERVICE_NAME

# Clean up all tunnels for project
kinfra tunnel cleanup --project PROJECT_NAME --all
```

**Options:**
- `--project PROJECT_NAME`: Project name
- `--service SERVICE_NAME`: Service name
- `--all`: Clean up all tunnels for project/service
- `--force`: Force cleanup tunnel

### `kinfra tunnel set-credentials`

Set tunnel credentials.

```bash
# Set credentials for project
kinfra tunnel set-credentials PROJECT_NAME SERVICE_NAME PROVIDER credentials.json

# Set credentials for service
kinfra tunnel set-credentials PROJECT_NAME SERVICE_NAME PROVIDER credentials.json --scope service

# Set global credentials
kinfra tunnel set-credentials --global PROVIDER credentials.json
```

**Options:**
- `--scope SCOPE`: Credential scope (global, project, service)
- `--global`: Set global credentials
- `--force`: Overwrite existing credentials

### `kinfra tunnel stats`

Show tunnel statistics.

```bash
# Show tunnel statistics
kinfra tunnel stats

# Show statistics for project
kinfra tunnel stats --project PROJECT_NAME

# Show statistics for provider
kinfra tunnel stats --provider cloudflare
```

**Options:**
- `--project PROJECT_NAME`: Filter by project
- `--provider PROVIDER`: Filter by provider
- `--format FORMAT`: Output format (table, json, yaml)

## Cleanup Policy Commands

### `kinfra cleanup init-project`

Initialize cleanup policy for a project.

```bash
# Initialize with default strategy
kinfra cleanup init-project PROJECT_NAME

# Initialize with specific strategy
kinfra cleanup init-project PROJECT_NAME --strategy moderate

# Initialize with custom rules
kinfra cleanup init-project PROJECT_NAME \
  --strategy aggressive \
  --rules cleanup-rules.json
```

**Options:**
- `--strategy STRATEGY`: Cleanup strategy (conservative, moderate, aggressive)
- `--rules PATH`: Custom rules file path
- `--force`: Overwrite existing policy

### `kinfra cleanup set-rule`

Set cleanup rule for a project.

```bash
# Set process cleanup rule
kinfra cleanup set-rule PROJECT_NAME process \
  --strategy aggressive \
  --patterns "api-project-*" \
  --max-age 1800 \
  --force

# Set tunnel cleanup rule
kinfra cleanup set-rule PROJECT_NAME tunnel \
  --strategy conservative \
  --patterns "api-project-*" \
  --max-age 7200

# Set port cleanup rule
kinfra cleanup set-rule PROJECT_NAME port \
  --strategy aggressive \
  --patterns "api-project-*" \
  --max-age 1800 \
  --force
```

**Options:**
- `--strategy STRATEGY`: Cleanup strategy
- `--patterns PATTERNS`: Comma-separated patterns
- `--exclude-patterns PATTERNS`: Comma-separated exclude patterns
- `--max-age SECONDS`: Maximum age for resources
- `--force`: Force cleanup
- `--enabled`: Enable the rule
- `--disabled`: Disable the rule

### `kinfra cleanup show-policy`

Show cleanup policy.

```bash
# Show project policy
kinfra cleanup show-policy PROJECT_NAME

# Show global policy
kinfra cleanup show-policy --global

# Show in different formats
kinfra cleanup show-policy PROJECT_NAME --format json
kinfra cleanup show-policy PROJECT_NAME --format yaml
```

**Options:**
- `--global`: Show global policy
- `--format FORMAT`: Output format (table, json, yaml)
- `--verbose`: Show detailed information

### `kinfra cleanup export`

Export cleanup policy.

```bash
# Export project policy
kinfra cleanup export PROJECT_NAME --output policy.yaml

# Export global policy
kinfra cleanup export --global --output global-policy.yaml
```

**Options:**
- `--global`: Export global policy
- `--output PATH`: Output file path
- `--format FORMAT`: Output format (yaml, json)

### `kinfra cleanup import`

Import cleanup policy.

```bash
# Import project policy
kinfra cleanup import PROJECT_NAME --input policy.yaml

# Import global policy
kinfra cleanup import --global --input global-policy.yaml
```

**Options:**
- `--global`: Import global policy
- `--input PATH`: Input file path
- `--merge`: Merge with existing policy
- `--force`: Overwrite existing policy

## Status Monitoring Commands

### `kinfra status show-project`

Show project status.

```bash
# Show project status
kinfra status show-project PROJECT_NAME

# Show in different formats
kinfra status show-project PROJECT_NAME --format html
kinfra status show-project PROJECT_NAME --format json
kinfra status show-project PROJECT_NAME --format yaml

# Show with details
kinfra status show-project PROJECT_NAME --detailed
```

**Options:**
- `--format FORMAT`: Output format (html, json, yaml, table)
- `--detailed`: Show detailed information
- `--verbose`: Show verbose output

### `kinfra status show-global`

Show global status.

```bash
# Show global status
kinfra status show-global

# Show in different formats
kinfra status show-global --format html
kinfra status show-global --format json

# Show with details
kinfra status show-global --detailed
```

**Options:**
- `--format FORMAT`: Output format (html, json, yaml, table)
- `--detailed`: Show detailed information
- `--verbose`: Show verbose output

### `kinfra status list-projects`

List all projects.

```bash
# List all projects
kinfra status list-projects

# List with status
kinfra status list-projects --with-status

# List in different formats
kinfra status list-projects --format json
kinfra status list-projects --format yaml
```

**Options:**
- `--with-status`: Include project status
- `--format FORMAT`: Output format (table, json, yaml)
- `--verbose`: Show verbose output

### `kinfra status update`

Update service status.

```bash
# Update service status
kinfra status update PROJECT_NAME SERVICE_NAME --status running --health healthy

# Update with port
kinfra status update PROJECT_NAME SERVICE_NAME \
  --status running \
  --health healthy \
  --port 8000

# Update with metadata
kinfra status update PROJECT_NAME SERVICE_NAME \
  --status running \
  --health healthy \
  --metadata '{"version": "1.0.0"}'
```

**Options:**
- `--status STATUS`: Service status (running, stopped, error)
- `--health HEALTH`: Health status (healthy, unhealthy, unknown)
- `--port PORT`: Service port
- `--metadata JSON`: Additional metadata as JSON object

### `kinfra status generate`

Generate status page.

```bash
# Generate status page
kinfra status generate PROJECT_NAME --type status

# Generate maintenance page
kinfra status generate PROJECT_NAME --type maintenance

# Generate with custom template
kinfra status generate PROJECT_NAME --type status --template custom.html
```

**Options:**
- `--type TYPE`: Page type (status, maintenance, error, loading)
- `--template PATH`: Custom template file
- `--output PATH`: Output file path
- `--format FORMAT`: Output format (html, json)

## Resource Management Commands

### `kinfra resource deploy`

Deploy a resource.

```bash
# Deploy global resource
kinfra resource deploy RESOURCE_NAME RESOURCE_TYPE --mode global

# Deploy tenanted resource
kinfra resource deploy RESOURCE_NAME RESOURCE_TYPE --mode tenanted --project PROJECT_NAME

# Deploy with configuration
kinfra resource deploy RESOURCE_NAME RESOURCE_TYPE \
  --mode global \
  --config config.json
```

**Options:**
- `--mode MODE`: Resource mode (global, tenanted, local)
- `--project PROJECT_NAME`: Project name for tenanted resources
- `--config PATH`: Configuration file path
- `--force`: Force deployment

### `kinfra resource list`

List resources.

```bash
# List all resources
kinfra resource list

# List resources by mode
kinfra resource list --mode global
kinfra resource list --mode tenanted

# List resources by project
kinfra resource list --project PROJECT_NAME
```

**Options:**
- `--mode MODE`: Filter by resource mode
- `--project PROJECT_NAME`: Filter by project
- `--format FORMAT`: Output format (table, json, yaml)

### `kinfra resource status`

Show resource status.

```bash
# Show resource status
kinfra resource status RESOURCE_NAME

# Show all resources status
kinfra resource status --all

# Show resources by mode
kinfra resource status --mode global
```

**Options:**
- `--all`: Show all resources status
- `--mode MODE`: Filter by resource mode
- `--project PROJECT_NAME`: Filter by project
- `--format FORMAT`: Output format (table, json, yaml)

### `kinfra resource cleanup`

Clean up resources.

```bash
# Clean up resource
kinfra resource cleanup RESOURCE_NAME

# Clean up all resources
kinfra resource cleanup --all

# Clean up resources by mode
kinfra resource cleanup --mode tenanted
```

**Options:**
- `--all`: Clean up all resources
- `--mode MODE`: Filter by resource mode
- `--project PROJECT_NAME`: Filter by project
- `--force`: Force cleanup
- `--dry-run`: Show what would be cleaned up

## Project Management Commands

### `kinfra project start`

Start a project.

```bash
# Start project
kinfra project start PROJECT_NAME

# Start with services
kinfra project start PROJECT_NAME --services api-server,worker

# Start with configuration
kinfra project start PROJECT_NAME --config project-config.yaml
```

**Options:**
- `--services SERVICES`: Comma-separated service names
- `--config PATH`: Project configuration file
- `--force`: Force start project

### `kinfra project stop`

Stop a project.

```bash
# Stop project
kinfra project stop PROJECT_NAME

# Stop with cleanup
kinfra project stop PROJECT_NAME --cleanup

# Stop with force
kinfra project stop PROJECT_NAME --force
```

**Options:**
- `--cleanup`: Clean up project resources
- `--force`: Force stop project
- `--timeout SECONDS`: Stop timeout

### `kinfra project status`

Show project status.

```bash
# Show project status
kinfra project status PROJECT_NAME

# Show all projects status
kinfra project status --all
```

**Options:**
- `--all`: Show all projects status
- `--format FORMAT`: Output format (table, json, yaml)

### `kinfra project list`

List projects.

```bash
# List all projects
kinfra project list

# List with status
kinfra project list --with-status
```

**Options:**
- `--with-status`: Include project status
- `--format FORMAT`: Output format (table, json, yaml)

## Global Commands

### `kinfra stats`

Show global statistics.

```bash
# Show all statistics
kinfra stats

# Show specific statistics
kinfra stats --process
kinfra stats --tunnel
kinfra stats --cleanup
kinfra stats --status
```

**Options:**
- `--process`: Show process statistics
- `--tunnel`: Show tunnel statistics
- `--cleanup`: Show cleanup statistics
- `--status`: Show status statistics
- `--format FORMAT`: Output format (table, json, yaml)

### `kinfra health`

Check system health.

```bash
# Check system health
kinfra health

# Check specific components
kinfra health --process
kinfra health --tunnel
kinfra health --cleanup
kinfra health --status
```

**Options:**
- `--process`: Check process governance health
- `--tunnel`: Check tunnel governance health
- `--cleanup`: Check cleanup policy health
- `--status`: Check status monitoring health
- `--verbose`: Show detailed health information

### `kinfra version`

Show version information.

```bash
# Show version
kinfra version

# Show detailed version
kinfra version --verbose
```

**Options:**
- `--verbose`: Show detailed version information

## Environment Variables

KInfra supports configuration via environment variables with the `KINFRA_` prefix:

```bash
# Global configuration
export KINFRA_DEBUG=true
export KINFRA_LOG_LEVEL=DEBUG
export KINFRA_ENVIRONMENT=production

# Process governance
export KINFRA_PROCESS_GOVERNANCE__MAX_PROCESS_AGE=7200
export KINFRA_PROCESS_GOVERNANCE__CLEANUP_INTERVAL=300

# Tunnel governance
export KINFRA_TUNNEL_GOVERNANCE__DEFAULT_LIFECYCLE_POLICY=smart
export KINFRA_TUNNEL_GOVERNANCE__TUNNEL_REUSE_THRESHOLD=1800

# Cleanup policies
export KINFRA_GLOBAL_CLEANUP_POLICY__DEFAULT_STRATEGY=conservative
export KINFRA_GLOBAL_CLEANUP_POLICY__MAX_CONCURRENT_CLEANUPS=10

# Status pages
export KINFRA_STATUS_PAGES__AUTO_REFRESH_INTERVAL=5
export KINFRA_STATUS_PAGES__INCLUDE_SERVICE_DETAILS=true
```

## Configuration Files

KInfra supports multiple configuration file formats:

- **YAML**: `kinfra.yaml`, `kinfra.yml`
- **JSON**: `kinfra.json`
- **TOML**: `kinfra.toml`

Configuration files are loaded in this order:
1. `~/.kinfra/config/kinfra.yaml`
2. `./kinfra.yaml`
3. `./kinfra.yml`
4. `./kinfra.json`
5. `./kinfra.toml`

## Examples

### Basic Project Setup

```bash
# Initialize project
kinfra config init --project my-api

# Start project
kinfra project start my-api --services api-server,worker

# Create tunnels
kinfra tunnel create my-api api-server 8000 --provider cloudflare

# Set up cleanup policies
kinfra cleanup init-project my-api --strategy moderate

# Show status
kinfra status show-project my-api
```

### Advanced Resource Management

```bash
# Deploy shared resources
kinfra resource deploy shared-redis redis --mode global
kinfra resource deploy shared-postgres postgres --mode global

# Start multiple projects
kinfra project start api-project --services api-server,api-worker
kinfra project start web-project --services web-server,web-worker

# Set up project-specific cleanup policies
kinfra cleanup init-project api-project --strategy aggressive
kinfra cleanup init-project web-project --strategy moderate

# Show global status
kinfra status show-global
```

### Troubleshooting

```bash
# Check system health
kinfra health --verbose

# Show process statistics
kinfra process stats --project my-api

# Show tunnel statistics
kinfra tunnel stats --project my-api

# Clean up stale processes
kinfra process cleanup-stale --dry-run

# Show configuration
kinfra config show --project my-api
```

## Conclusion

This CLI reference provides comprehensive coverage of all KInfra commands for Phase 5 features. Use these commands to manage processes, tunnels, cleanup policies, and status monitoring across your projects.

For more information, see:
- [Single Project Setup Guide](single_project_setup.md)
- [Shared Resource Setup Guide](shared_resource_setup.md)
- [Integration Testing Guide](integration_testing.md)
- [Configuration Guide](configuration.md)