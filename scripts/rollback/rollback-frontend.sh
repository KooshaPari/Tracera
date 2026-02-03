#!/bin/bash
# Frontend Rollback Script
# Rolls back frontend to last stable version

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
SNAPSHOT_DIR="${PROJECT_ROOT}/.deployments/snapshots/frontend"
STABLE_VERSION_FILE="${PROJECT_ROOT}/.deployments/frontend-stable-version.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[FRONTEND-ROLLBACK]${NC} $*"
}

log_error() {
    echo -e "${RED}[FRONTEND-ROLLBACK ERROR]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[FRONTEND-ROLLBACK WARNING]${NC} $*"
}

# Get stable version
get_stable_version() {
    if [ -f "$STABLE_VERSION_FILE" ]; then
        cat "$STABLE_VERSION_FILE"
    else
        log_error "No stable version recorded"
        return 1
    fi
}

# Rollback frontend
rollback_frontend() {
    local stable_version
    stable_version=$(get_stable_version)

    log "Rolling back frontend to version: $stable_version"

    # Check if snapshot exists
    local snapshot_file="${SNAPSHOT_DIR}/${stable_version}.tar.gz"
    if [ ! -f "$snapshot_file" ]; then
        log_error "Snapshot not found: $snapshot_file"
        return 1
    fi

    # Backup current deployment
    local backup_dir="${PROJECT_ROOT}/.deployments/backups/frontend"
    mkdir -p "$backup_dir"
    local timestamp=$(date +%Y%m%d%H%M%S)

    if [ -d "${FRONTEND_DIR}/dist" ]; then
        log "Backing up current frontend to ${backup_dir}/${timestamp}.tar.gz"
        tar -czf "${backup_dir}/${timestamp}.tar.gz" -C "${FRONTEND_DIR}" dist 2>/dev/null || true
    fi

    # Stop frontend if running
    log "Stopping frontend service..."
    if command -v process-compose &>/dev/null; then
        process-compose restart frontend 2>/dev/null || true
    fi

    # Extract stable version
    log "Extracting stable version..."
    rm -rf "${FRONTEND_DIR}/dist"
    tar -xzf "$snapshot_file" -C "$FRONTEND_DIR"

    # Restart frontend
    log "Restarting frontend service..."
    if command -v process-compose &>/dev/null; then
        process-compose restart frontend
    else
        log_warning "process-compose not found - manual frontend restart required"
    fi

    # Wait for frontend to be healthy
    log "Waiting for frontend to become healthy..."
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:5173/ >/dev/null 2>&1; then
            log "Frontend is healthy"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 2
    done

    log_error "Frontend did not become healthy after rollback"
    return 1
}

# Verify frontend health
verify_health() {
    log "Verifying frontend health..."

    # Check if frontend is responding
    if ! curl -sf http://localhost:5173/ >/dev/null 2>&1; then
        log_error "Frontend is not responding"
        return 1
    fi

    # Check if critical routes are accessible
    local routes=("/" "/health")
    for route in "${routes[@]}"; do
        if ! curl -sf "http://localhost:5173${route}" >/dev/null 2>&1; then
            log_warning "Route $route is not accessible"
        fi
    done

    log "Frontend health verification passed"
    return 0
}

# Main
main() {
    log "Starting frontend rollback..."

    if rollback_frontend; then
        log "Frontend rollback successful"

        if verify_health; then
            log "Frontend health verified"
            exit 0
        else
            log_error "Frontend health verification failed"
            exit 1
        fi
    else
        log_error "Frontend rollback failed"
        exit 1
    fi
}

main "$@"
