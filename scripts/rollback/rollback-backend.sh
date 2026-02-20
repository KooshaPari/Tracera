#!/bin/bash
# Backend Rollback Script
# Rolls back both Go and Python backends to last stable versions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GO_BACKEND_DIR="${PROJECT_ROOT}/backend"
PYTHON_BACKEND_DIR="${PROJECT_ROOT}/src"
SNAPSHOT_DIR="${PROJECT_ROOT}/.deployments/snapshots/backend"
STABLE_VERSION_FILE="${PROJECT_ROOT}/.deployments/backend-stable-version.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[BACKEND-ROLLBACK]${NC} $*"
}

log_error() {
    echo -e "${RED}[BACKEND-ROLLBACK ERROR]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[BACKEND-ROLLBACK WARNING]${NC} $*"
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

# Rollback Go backend
rollback_go_backend() {
    local stable_version="$1"

    log "Rolling back Go backend to version: $stable_version"

    # Check if snapshot exists
    local snapshot_file="${SNAPSHOT_DIR}/go-${stable_version}"
    if [ ! -f "$snapshot_file" ]; then
        log_error "Go backend snapshot not found: $snapshot_file"
        return 1
    fi

    # Backup current binary
    if [ -f "${GO_BACKEND_DIR}/tracertm" ]; then
        local backup_dir="${PROJECT_ROOT}/.deployments/backups/backend/go"
        mkdir -p "$backup_dir"
        local timestamp=$(date +%Y%m%d%H%M%S)
        cp "${GO_BACKEND_DIR}/tracertm" "${backup_dir}/tracertm-${timestamp}"
    fi

    # Stop Go backend
    log "Stopping Go backend..."
    if command -v process-compose &>/dev/null; then
        process-compose stop go-backend 2>/dev/null || true
    fi

    # Restore stable version
    log "Restoring Go backend binary..."
    cp "$snapshot_file" "${GO_BACKEND_DIR}/tracertm"
    chmod +x "${GO_BACKEND_DIR}/tracertm"

    # Restart Go backend
    log "Starting Go backend..."
    if command -v process-compose &>/dev/null; then
        process-compose start go-backend
    else
        log_warning "process-compose not found - manual restart required"
    fi

    # Wait for health
    log "Waiting for Go backend health..."
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
            log "Go backend is healthy"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 2
    done

    log_error "Go backend did not become healthy"
    return 1
}

# Rollback Python backend
rollback_python_backend() {
    local stable_version="$1"

    log "Rolling back Python backend to version: $stable_version"

    # For Python, we use git to rollback to tagged version
    # In production, you might use containers or different deployment artifacts

    # Check if git tag exists
    if ! git -C "$PROJECT_ROOT" rev-parse "python-${stable_version}" >/dev/null 2>&1; then
        log_warning "No git tag found for python-${stable_version}, using snapshot"

        local snapshot_file="${SNAPSHOT_DIR}/python-${stable_version}.tar.gz"
        if [ ! -f "$snapshot_file" ]; then
            log_error "Python backend snapshot not found: $snapshot_file"
            return 1
        fi

        # Backup current code
        local backup_dir="${PROJECT_ROOT}/.deployments/backups/backend/python"
        mkdir -p "$backup_dir"
        local timestamp=$(date +%Y%m%d%H%M%S)
        tar -czf "${backup_dir}/python-${timestamp}.tar.gz" -C "$PROJECT_ROOT" src

        # Restore from snapshot
        tar -xzf "$snapshot_file" -C "$PROJECT_ROOT"
    fi

    # Stop Python backend
    log "Stopping Python backend..."
    if command -v process-compose &>/dev/null; then
        process-compose stop python-backend 2>/dev/null || true
    fi

    # Reinstall dependencies if needed
    if [ -f "${PROJECT_ROOT}/pyproject.toml" ]; then
        log "Reinstalling Python dependencies..."
        cd "$PROJECT_ROOT"
        if command -v uv &>/dev/null; then
            uv sync 2>/dev/null || pip install -e ".[dev]"
        else
            pip install -e ".[dev]"
        fi
    fi

    # Restart Python backend
    log "Starting Python backend..."
    if command -v process-compose &>/dev/null; then
        process-compose start python-backend
    else
        log_warning "process-compose not found - manual restart required"
    fi

    # Wait for health
    log "Waiting for Python backend health..."
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            log "Python backend is healthy"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 2
    done

    log_error "Python backend did not become healthy"
    return 1
}

# Verify backend health
verify_health() {
    log "Verifying backend health..."

    # Check Go backend
    if ! curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        log_error "Go backend health check failed"
        return 1
    fi

    # Check Python backend
    if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        log_error "Python backend health check failed"
        return 1
    fi

    # Check critical endpoints
    local go_endpoints=("/api/v1/health" "/api/v1/items")
    for endpoint in "${go_endpoints[@]}"; do
        if ! curl -sf "http://localhost:8080${endpoint}" >/dev/null 2>&1; then
            log_warning "Go endpoint $endpoint is not accessible"
        fi
    done

    local python_endpoints=("/health" "/docs")
    for endpoint in "${python_endpoints[@]}"; do
        if ! curl -sf "http://localhost:8000${endpoint}" >/dev/null 2>&1; then
            log_warning "Python endpoint $endpoint is not accessible"
        fi
    done

    log "Backend health verification passed"
    return 0
}

# Main
main() {
    log "Starting backend rollback..."

    local stable_version
    stable_version=$(get_stable_version)

    # Rollback both backends
    local go_success=false
    local python_success=false

    if rollback_go_backend "$stable_version"; then
        log "Go backend rollback successful"
        go_success=true
    else
        log_error "Go backend rollback failed"
    fi

    if rollback_python_backend "$stable_version"; then
        log "Python backend rollback successful"
        python_success=true
    else
        log_error "Python backend rollback failed"
    fi

    # Check if at least one succeeded
    if [ "$go_success" = true ] && [ "$python_success" = true ]; then
        if verify_health; then
            log "Backend rollback and health verification successful"
            exit 0
        else
            log_error "Backend health verification failed"
            exit 1
        fi
    else
        log_error "Backend rollback failed"
        exit 1
    fi
}

main "$@"
