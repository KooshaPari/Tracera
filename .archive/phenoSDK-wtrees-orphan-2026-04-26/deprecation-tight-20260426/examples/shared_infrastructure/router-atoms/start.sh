#!/bin/bash
"""
Router + Atoms Integration Example

This example demonstrates how to integrate KInfra with existing router and atoms
projects, showing shared infrastructure management across multiple services.

Features demonstrated:
- Shared Redis and PostgreSQL databases
- Cross-project process governance
- Unified tunnel management
- Coordinated cleanup policies
- Global status monitoring
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ROUTER_PROJECT="router-project"
ATOMS_PROJECT="atoms-project"
SHARED_REDIS_PORT=6379
SHARED_POSTGRES_PORT=5432
ROUTER_PORT=8000
ATOMS_PORT=8001

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if KInfra is installed
    if ! command -v kinfra >/dev/null 2>&1; then
        log_error "KInfra CLI not found. Please install KInfra first."
        exit 1
    fi
    
    # Check if Python is available
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3 not found. Please install Python 3.11+ first."
        exit 1
    fi
    
    # Check if required tools are available
    for tool in redis-server postgres nats-server; do
        if ! command -v $tool >/dev/null 2>&1; then
            log_warning "$tool not found. Please install it for full functionality."
        fi
    done
    
    log_success "Prerequisites check complete"
}

# Start shared infrastructure
start_shared_infrastructure() {
    log_info "Starting shared infrastructure..."
    
    # Start Redis
    if command -v redis-server >/dev/null 2>&1; then
        log_info "Starting Redis..."
        redis-server --daemonize yes --port $SHARED_REDIS_PORT
        log_success "Redis started on port $SHARED_REDIS_PORT"
    else
        log_warning "Redis not found, skipping"
    fi
    
    # Start PostgreSQL
    if command -v postgres >/dev/null 2>&1; then
        log_info "Starting PostgreSQL..."
        pg_ctl -D /usr/local/var/postgres start 2>/dev/null || true
        log_success "PostgreSQL started on port $SHARED_POSTGRES_PORT"
    else
        log_warning "PostgreSQL not found, skipping"
    fi
    
    # Start NATS
    if command -v nats-server >/dev/null 2>&1; then
        log_info "Starting NATS..."
        nats-server --port 4222 --daemon
        log_success "NATS started on port 4222"
    else
        log_warning "NATS not found, skipping"
    fi
    
    log_success "Shared infrastructure started"
}

# Initialize KInfra configuration
init_kinfra_config() {
    log_info "Initializing KInfra configuration..."
    
    # Initialize global configuration
    kinfra config init --global --force
    
    # Initialize project configurations
    kinfra config init --project $ROUTER_PROJECT --force
    kinfra config init --project $ATOMS_PROJECT --force
    
    # Set up shared resources
    log_info "Setting up shared resources..."
    
    # Deploy shared Redis
    kinfra resource deploy shared-redis redis --mode global --config <(cat << EOF
{
  "host": "localhost",
  "port": $SHARED_REDIS_PORT,
  "db": 0
}
EOF
)
    
    # Deploy shared PostgreSQL
    kinfra resource deploy shared-postgres postgres --mode global --config <(cat << EOF
{
  "host": "localhost",
  "port": $SHARED_POSTGRES_PORT,
  "database": "shared_db"
}
EOF
)
    
    # Deploy shared NATS
    kinfra resource deploy shared-nats nats --mode global --config <(cat << EOF
{
  "url": "nats://localhost:4222"
}
EOF
)
    
    log_success "KInfra configuration initialized"
}

# Set up cleanup policies
setup_cleanup_policies() {
    log_info "Setting up cleanup policies..."
    
    # Router project cleanup policy (aggressive for performance)
    kinfra cleanup init-project $ROUTER_PROJECT --strategy aggressive
    kinfra cleanup set-rule $ROUTER_PROJECT process \
        --strategy aggressive \
        --patterns "router-*" \
        --max-age 1800 \
        --force
    
    # Atoms project cleanup policy (moderate for stability)
    kinfra cleanup init-project $ATOMS_PROJECT --strategy moderate
    kinfra cleanup set-rule $ATOMS_PROJECT process \
        --strategy moderate \
        --patterns "atoms-*" \
        --max-age 3600
    
    log_success "Cleanup policies configured"
}

# Start router project
start_router_project() {
    log_info "Starting router project..."
    
    # Start router services
    kinfra project start $ROUTER_PROJECT --services router-api,router-worker
    
    # Register processes with metadata
    kinfra process register $ROUTER_PROJECT router-api 1001 \
        --command-line '["python", "router_api.py"]' \
        --environment '{"PROJECT": "router-project", "REDIS_URL": "redis://localhost:6379/0"}' \
        --scope local \
        --resource-type api \
        --tags "web,rest,api"
    
    kinfra process register $ROUTER_PROJECT router-worker 1002 \
        --command-line '["python", "router_worker.py"]' \
        --environment '{"PROJECT": "router-project", "REDIS_URL": "redis://localhost:6379/0"}' \
        --scope local \
        --resource-type worker \
        --tags "worker,background"
    
    # Create tunnels
    kinfra tunnel create $ROUTER_PROJECT router-api $ROUTER_PORT \
        --provider cloudflare \
        --hostname router.example.com \
        --reuse
    
    # Set tunnel credentials
    kinfra tunnel set-credentials $ROUTER_PROJECT router-api cloudflare <(cat << EOF
{
  "token": "router-cloudflare-token-123"
}
EOF
)
    
    # Update status
    kinfra status update $ROUTER_PROJECT router-api \
        --status running \
        --health healthy \
        --port $ROUTER_PORT
    
    log_success "Router project started"
}

# Start atoms project
start_atoms_project() {
    log_info "Starting atoms project..."
    
    # Start atoms services
    kinfra project start $ATOMS_PROJECT --services atoms-api,atoms-worker
    
    # Register processes with metadata
    kinfra process register $ATOMS_PROJECT atoms-api 2001 \
        --command-line '["python", "atoms_api.py"]' \
        --environment '{"PROJECT": "atoms-project", "REDIS_URL": "redis://localhost:6379/1"}' \
        --scope local \
        --resource-type api \
        --tags "web,rest,api"
    
    kinfra process register $ATOMS_PROJECT atoms-worker 2002 \
        --command-line '["python", "atoms_worker.py"]' \
        --environment '{"PROJECT": "atoms-project", "REDIS_URL": "redis://localhost:6379/1"}' \
        --scope local \
        --resource-type worker \
        --tags "worker,background"
    
    # Create tunnels
    kinfra tunnel create $ATOMS_PROJECT atoms-api $ATOMS_PORT \
        --provider cloudflare \
        --hostname atoms.example.com \
        --reuse
    
    # Set tunnel credentials
    kinfra tunnel set-credentials $ATOMS_PROJECT atoms-api cloudflare <(cat << EOF
{
  "token": "atoms-cloudflare-token-456"
}
EOF
)
    
    # Update status
    kinfra status update $ATOMS_PROJECT atoms-api \
        --status running \
        --health healthy \
        --port $ATOMS_PORT
    
    log_success "Atoms project started"
}

# Set up monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Update status for all services
    kinfra status update $ROUTER_PROJECT router-worker \
        --status running \
        --health healthy \
        --port 8002
    
    kinfra status update $ATOMS_PROJECT atoms-worker \
        --status running \
        --health healthy \
        --port 8003
    
    # Generate status pages
    kinfra status generate $ROUTER_PROJECT --type status --output router-status.html
    kinfra status generate $ATOMS_PROJECT --type status --output atoms-status.html
    kinfra status generate global --type dashboard --output global-dashboard.html
    
    log_success "Monitoring set up"
}

# Show status
show_status() {
    log_info "Showing system status..."
    
    echo ""
    echo "=== KInfra Status ==="
    kinfra status show-global
    
    echo ""
    echo "=== Router Project Status ==="
    kinfra status show-project $ROUTER_PROJECT
    
    echo ""
    echo "=== Atoms Project Status ==="
    kinfra status show-project $ATOMS_PROJECT
    
    echo ""
    echo "=== Resource Status ==="
    kinfra resource status --all
    
    echo ""
    echo "=== Process Statistics ==="
    kinfra process stats
    
    echo ""
    echo "=== Tunnel Statistics ==="
    kinfra tunnel stats
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    
    # Stop projects
    kinfra project stop $ROUTER_PROJECT --cleanup
    kinfra project stop $ATOMS_PROJECT --cleanup
    
    # Stop shared infrastructure
    if command -v redis-cli >/dev/null 2>&1; then
        redis-cli shutdown 2>/dev/null || true
    fi
    
    if command -v pg_ctl >/dev/null 2>&1; then
        pg_ctl -D /usr/local/var/postgres stop 2>/dev/null || true
    fi
    
    if command -v nats-server >/dev/null 2>&1; then
        pkill nats-server 2>/dev/null || true
    fi
    
    log_success "Cleanup complete"
}

# Main function
main() {
    log_info "Starting Router + Atoms Integration Example"
    
    # Set up signal handlers
    trap cleanup EXIT INT TERM
    
    # Run setup steps
    check_prerequisites
    start_shared_infrastructure
    init_kinfra_config
    setup_cleanup_policies
    start_router_project
    start_atoms_project
    setup_monitoring
    
    # Show status
    show_status
    
    log_success "Router + Atoms Integration Example started successfully!"
    log_info "Press Ctrl+C to stop"
    
    # Keep running until interrupted
    while true; do
        sleep 10
        # Update status periodically
        kinfra status update $ROUTER_PROJECT router-api --status running --health healthy
        kinfra status update $ATOMS_PROJECT atoms-api --status running --health healthy
    done
}

# Run main function
main "$@"