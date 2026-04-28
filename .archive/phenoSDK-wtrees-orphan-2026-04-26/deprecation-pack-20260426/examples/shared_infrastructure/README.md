# KInfra Shared Infrastructure Examples

This directory contains comprehensive examples demonstrating how to use KInfra for shared infrastructure management across multiple projects. These examples show real-world patterns for building sophisticated multi-service applications with shared resources.

## Examples Overview

### 1. Router + Atoms Integration (`router-atoms/`)
Demonstrates how to integrate KInfra with existing router and atoms projects, showing:
- Shared Redis and PostgreSQL databases
- Cross-project process governance
- Unified tunnel management
- Coordinated cleanup policies
- Global status monitoring

### 2. Microservices Architecture (`microservices/`)
Shows a complete microservices setup with:
- API Gateway with KInfra proxy
- Multiple backend services
- Shared message queues (NATS)
- Distributed logging and monitoring
- Service discovery and health checks

### 3. Development Environment (`dev-environment/`)
Provides a complete development environment with:
- Docker Compose integration
- Hot reloading for development
- Shared development databases
- Local tunnel management
- Development-specific cleanup policies

### 4. Production Deployment (`production/`)
Demonstrates production-ready deployment with:
- Kubernetes integration
- High availability setup
- Monitoring and alerting
- Backup and recovery
- Security best practices

## Quick Start

### Prerequisites

1. Install KInfra and dependencies:
   ```bash
   ./scripts/kinfra-bootstrap.sh --all
   ```

2. Set up tunnel credentials:
   ```bash
   kinfra tunnel set-credentials my-project api-server cloudflare credentials.json
   ```

### Running Examples

1. **Router + Atoms Integration**:
   ```bash
   cd examples/shared_infrastructure/router-atoms
   ./start.sh
   ```

2. **Microservices Architecture**:
   ```bash
   cd examples/shared_infrastructure/microservices
   docker-compose up -d
   ```

3. **Development Environment**:
   ```bash
   cd examples/shared_infrastructure/dev-environment
   ./dev-setup.sh
   ```

4. **Production Deployment**:
   ```bash
   cd examples/shared_infrastructure/production
   ./deploy.sh
   ```

## Architecture Patterns

### Shared Resource Management

All examples demonstrate these key patterns:

1. **Global Resources**: Shared databases, message queues, and caches
2. **Project Isolation**: Each project manages its own services while sharing infrastructure
3. **Resource Coordination**: Automatic cleanup and lifecycle management
4. **Status Monitoring**: Unified visibility across all projects and services

### Process Governance

- **Metadata-based Tracking**: All processes tagged with project and service information
- **Automatic Cleanup**: Stale processes cleaned up based on project policies
- **Cross-project Isolation**: Processes from different projects don't interfere

### Tunnel Management

- **Smart Reuse**: Tunnels reused when possible to reduce costs
- **Project-scoped Credentials**: Each project can have its own tunnel credentials
- **Health Monitoring**: Automatic detection and cleanup of failed tunnels

### Cleanup Policies

- **Project-specific Rules**: Each project can have different cleanup strategies
- **Resource-type Policies**: Different rules for processes, tunnels, ports, etc.
- **Global Coordination**: Global policies ensure system-wide consistency

## Configuration

### Global Configuration

All examples use a shared global configuration:

```yaml
# ~/.kinfra/config/kinfra.yaml
app_name: "shared-infrastructure"
debug: false
log_level: "INFO"
environment: "production"

# Global resource settings
enable_nats: true
nats_url: "nats://localhost:4222"
enable_metrics: true
metrics_port: 9090

# Global cleanup policy
global_cleanup_policy:
  default_strategy: "conservative"
  max_concurrent_cleanups: 10
  cleanup_timeout: 600.0
  enabled: true
```

### Project Configuration

Each project has its own configuration:

```yaml
# Project-specific cleanup policy
projects:
  router-project:
    project_name: "router-project"
    default_strategy: "aggressive"
    enabled: true
    rules:
      process:
        resource_type: "process"
        strategy: "aggressive"
        patterns: ["router-*"]
        max_age: 1800.0
        force_cleanup: true
        enabled: true

# Project-specific routing
project_routing:
  router-project:
    project_name: "router-project"
    domain: "router.example.com"
    base_path: "/"
    enable_health_checks: true
    health_check_interval: 5.0
    health_check_timeout: 2.0
    fallback_enabled: true
    maintenance_enabled: false
```

## Monitoring and Observability

### Status Dashboards

Each example includes status dashboards showing:
- Service health and status
- Tunnel connectivity
- Resource usage
- Cleanup statistics
- Performance metrics

### Health Checks

- **Service Health**: Automatic health checks for all services
- **Tunnel Health**: Monitoring of tunnel connectivity and performance
- **Resource Health**: Database and message queue health monitoring
- **System Health**: Overall system health and performance

### Metrics Collection

- **Process Metrics**: CPU, memory, and resource usage per process
- **Tunnel Metrics**: Connection counts, latency, and error rates
- **Resource Metrics**: Database connections, queue depths, and cache hit rates
- **System Metrics**: Overall system performance and health

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Use `kinfra port list` to check for conflicts
2. **Tunnel Failures**: Check credentials with `kinfra tunnel list`
3. **Process Cleanup**: Use `kinfra process cleanup-stale` to clean up stale processes
4. **Resource Conflicts**: Use `kinfra resource list` to check resource usage

### Debugging

1. **Enable Debug Logging**: Set `debug: true` in configuration
2. **Check Logs**: Use `kinfra logs` to view system logs
3. **Status Monitoring**: Use `kinfra status show-global` for overall status
4. **Health Checks**: Use `kinfra health` to check system health

### Getting Help

- Check the [CLI Reference](../../docs/quickstart/cli_reference.md) for command details
- See the [Configuration Guide](../../docs/quickstart/configuration.md) for advanced configuration
- Review the [Integration Testing Guide](../../docs/quickstart/integration_testing.md) for testing patterns

## Contributing

To add new examples:

1. Create a new directory under `examples/shared_infrastructure/`
2. Include a `README.md` explaining the example
3. Provide configuration files and scripts
4. Add integration tests
5. Update this README with the new example

## License

These examples are part of the KInfra project and are licensed under the same terms as the main project.