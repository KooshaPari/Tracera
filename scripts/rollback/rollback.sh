#!/bin/bash
# Main Rollback Orchestrator
# Coordinates automated rollback of frontend, backend, and database components
# Target: <2 minute rollback time from detection to completion

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ROLLBACK_LOG_DIR="${PROJECT_ROOT}/.rollback-logs"
ROLLBACK_STATE_FILE="${ROLLBACK_LOG_DIR}/rollback-state.json"
HEALTH_THRESHOLD_ERROR_RATE=5    # 5% error rate triggers rollback
HEALTH_THRESHOLD_LATENCY_MULT=2  # 2x baseline latency triggers rollback
ROLLBACK_TIMEOUT=120             # 2 minute timeout for entire rollback

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log() {
    echo -e "${BLUE}[ROLLBACK]${NC} $*" | tee -a "${ROLLBACK_LOG_DIR}/rollback.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "${ROLLBACK_LOG_DIR}/rollback.log" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "${ROLLBACK_LOG_DIR}/rollback.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "${ROLLBACK_LOG_DIR}/rollback.log"
}

# Initialize rollback environment
init_rollback() {
    mkdir -p "${ROLLBACK_LOG_DIR}"
    log "Initializing rollback at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Record rollback start
    cat > "${ROLLBACK_STATE_FILE}" <<EOF
{
    "rollback_start": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "trigger_reason": "${ROLLBACK_REASON:-manual}",
    "status": "in_progress",
    "components": {
        "frontend": "pending",
        "backend": "pending",
        "database": "pending"
    }
}
EOF
}

# Update rollback state
update_state() {
    local component="$1"
    local status="$2"

    if [ -f "${ROLLBACK_STATE_FILE}" ]; then
        jq --arg comp "$component" --arg stat "$status" \
            '.components[$comp] = $stat | .last_update = now | todateiso8601' \
            "${ROLLBACK_STATE_FILE}" > "${ROLLBACK_STATE_FILE}.tmp"
        mv "${ROLLBACK_STATE_FILE}.tmp" "${ROLLBACK_STATE_FILE}"
    fi
}

# Get previous stable version
get_stable_version() {
    local component="$1"
    local version_file="${PROJECT_ROOT}/.deployments/${component}-stable-version.txt"

    if [ -f "$version_file" ]; then
        cat "$version_file"
    else
        log_error "No stable version found for $component"
        echo "unknown"
    fi
}

# Check if rollback is needed (can be called by monitoring)
check_rollback_needed() {
    log "Checking if rollback is needed..."

    # Check error rate
    local error_rate=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])/rate(http_requests_total[5m])*100" | \
        jq -r '.data.result[0].value[1] // "0"')

    if [ -n "$error_rate" ] && [ "$(echo "$error_rate > $HEALTH_THRESHOLD_ERROR_RATE" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        log_warning "Error rate ${error_rate}% exceeds threshold ${HEALTH_THRESHOLD_ERROR_RATE}%"
        export ROLLBACK_REASON="error_rate_threshold_exceeded"
        return 0
    fi

    # Check latency
    local current_latency=$(curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))" | \
        jq -r '.data.result[0].value[1] // "0"')
    local baseline_latency=$(curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[1h] offset 1d))" | \
        jq -r '.data.result[0].value[1] // "0"')

    if [ -n "$current_latency" ] && [ -n "$baseline_latency" ] && [ "$(echo "$baseline_latency > 0" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        local latency_mult=$(echo "$current_latency / $baseline_latency" | bc -l 2>/dev/null || echo 0)
        if [ "$(echo "$latency_mult > $HEALTH_THRESHOLD_LATENCY_MULT" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
            log_warning "Latency ${current_latency}s exceeds ${HEALTH_THRESHOLD_LATENCY_MULT}x baseline ${baseline_latency}s"
            export ROLLBACK_REASON="latency_threshold_exceeded"
            return 0
        fi
    fi

    # Check critical service health
    local services=("go-backend:8080" "python-backend:8000" "postgres:5432" "redis:6379")
    for service_spec in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_spec"
        if ! nc -z localhost "$port" 2>/dev/null; then
            log_warning "Critical service $service is down"
            export ROLLBACK_REASON="critical_service_failure:$service"
            return 0
        fi
    done

    log "All health checks passed - no rollback needed"
    return 1
}

# Perform rollback
perform_rollback() {
    local component="${1:-all}"
    local start_time=$(date +%s)

    init_rollback

    log "Starting rollback for: $component"
    log "Reason: ${ROLLBACK_REASON:-manual}"

    case "$component" in
        frontend)
            rollback_frontend
            ;;
        backend)
            rollback_backend
            ;;
        database)
            rollback_database
            ;;
        all)
            # Rollback in reverse order of dependency
            rollback_frontend
            rollback_backend
            rollback_database
            ;;
        *)
            log_error "Unknown component: $component"
            exit 1
            ;;
    esac

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Update final state
    jq --arg dur "$duration" --arg stat "completed" \
        '.status = $stat | .rollback_end = (now | todateiso8601) | .duration_seconds = ($dur | tonumber)' \
        "${ROLLBACK_STATE_FILE}" > "${ROLLBACK_STATE_FILE}.tmp"
    mv "${ROLLBACK_STATE_FILE}.tmp" "${ROLLBACK_STATE_FILE}"

    log_success "Rollback completed in ${duration}s"

    if [ "$duration" -gt "$ROLLBACK_TIMEOUT" ]; then
        log_warning "Rollback took longer than target ${ROLLBACK_TIMEOUT}s"
    fi

    # Verify health after rollback
    verify_rollback_health
}

# Rollback frontend
rollback_frontend() {
    log "Rolling back frontend..."
    update_state "frontend" "in_progress"

    if bash "${SCRIPT_DIR}/rollback-frontend.sh"; then
        update_state "frontend" "success"
        log_success "Frontend rollback successful"
    else
        update_state "frontend" "failed"
        log_error "Frontend rollback failed"
        return 1
    fi
}

# Rollback backend
rollback_backend() {
    log "Rolling back backend..."
    update_state "backend" "in_progress"

    if bash "${SCRIPT_DIR}/rollback-backend.sh"; then
        update_state "backend" "success"
        log_success "Backend rollback successful"
    else
        update_state "backend" "failed"
        log_error "Backend rollback failed"
        return 1
    fi
}

# Rollback database
rollback_database() {
    log "Rolling back database..."
    update_state "database" "in_progress"

    if bash "${SCRIPT_DIR}/rollback-database.sh"; then
        update_state "database" "success"
        log_success "Database rollback successful"
    else
        update_state "database" "failed"
        log_error "Database rollback failed"
        return 1
    fi
}

# Verify health after rollback
verify_rollback_health() {
    log "Verifying system health post-rollback..."

    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if check_all_services_healthy; then
            log_success "All services healthy after rollback"
            return 0
        fi

        attempt=$((attempt + 1))
        log "Waiting for services to stabilize... ($attempt/$max_attempts)"
        sleep 2
    done

    log_error "Services did not become healthy after rollback"
    return 1
}

# Check all services are healthy
check_all_services_healthy() {
    local healthy=true

    # Check Go backend
    if ! curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        healthy=false
    fi

    # Check Python backend
    if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        healthy=false
    fi

    # Check Postgres
    if ! pg_isready -h localhost -p 5432 -U tracertm >/dev/null 2>&1; then
        healthy=false
    fi

    # Check Redis
    if ! redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
        healthy=false
    fi

    $healthy
}

# Create deployment snapshot (to be called before deployments)
create_deployment_snapshot() {
    local component="$1"
    local version="$2"

    local snapshot_dir="${PROJECT_ROOT}/.deployments/snapshots/${component}"
    mkdir -p "$snapshot_dir"

    log "Creating deployment snapshot for $component version $version"

    case "$component" in
        frontend)
            # Snapshot frontend build
            if [ -d "${PROJECT_ROOT}/frontend/dist" ]; then
                tar -czf "${snapshot_dir}/${version}.tar.gz" -C "${PROJECT_ROOT}/frontend" dist
            fi
            ;;
        backend)
            # Snapshot backend binary
            if [ -f "${PROJECT_ROOT}/backend/tracertm" ]; then
                cp "${PROJECT_ROOT}/backend/tracertm" "${snapshot_dir}/${version}"
            fi
            ;;
        database)
            # Create database backup
            pg_dump -h localhost -U tracertm tracertm > "${snapshot_dir}/${version}.sql"
            ;;
    esac

    # Mark this version as stable
    echo "$version" > "${PROJECT_ROOT}/.deployments/${component}-stable-version.txt"
    log_success "Snapshot created for $component version $version"
}

# Show rollback status
show_status() {
    if [ -f "${ROLLBACK_STATE_FILE}" ]; then
        echo "=== Rollback Status ==="
        jq -r '
            "Start Time: \(.rollback_start)",
            "Reason: \(.trigger_reason)",
            "Status: \(.status)",
            "Duration: \(.duration_seconds // "in progress")s",
            "",
            "Components:",
            "  Frontend: \(.components.frontend)",
            "  Backend: \(.components.backend)",
            "  Database: \(.components.database)"
        ' "${ROLLBACK_STATE_FILE}"
    else
        echo "No rollback in progress or completed recently"
    fi
}

# Main
main() {
    local action="${1:-check}"

    case "$action" in
        check)
            if check_rollback_needed; then
                log_warning "Rollback is needed!"
                exit 2
            else
                log_success "System is healthy"
                exit 0
            fi
            ;;
        rollback)
            local component="${2:-all}"
            perform_rollback "$component"
            ;;
        snapshot)
            local component="${2:-}"
            local version="${3:-$(date +%Y%m%d%H%M%S)}"
            if [ -z "$component" ]; then
                log_error "Component required for snapshot"
                exit 1
            fi
            create_deployment_snapshot "$component" "$version"
            ;;
        status)
            show_status
            ;;
        auto)
            # Auto mode: check and rollback if needed
            if check_rollback_needed; then
                log_warning "Triggering automatic rollback"
                perform_rollback all
            else
                log "No rollback needed"
            fi
            ;;
        *)
            echo "Usage: $0 {check|rollback [component]|snapshot <component> [version]|status|auto}"
            echo ""
            echo "Commands:"
            echo "  check              - Check if rollback is needed"
            echo "  rollback [comp]    - Perform rollback (all|frontend|backend|database)"
            echo "  snapshot <comp> [v] - Create deployment snapshot"
            echo "  status             - Show rollback status"
            echo "  auto               - Check and auto-rollback if needed"
            exit 1
            ;;
    esac
}

# Ensure jq and bc are available
if ! command -v jq &>/dev/null; then
    log_error "jq is required but not installed"
    exit 1
fi

if ! command -v bc &>/dev/null; then
    log_warning "bc not installed - some checks will be skipped"
fi

main "$@"
