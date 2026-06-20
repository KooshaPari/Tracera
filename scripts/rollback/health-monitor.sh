#!/bin/bash
# Health Monitor Daemon
# Continuously monitors system health and triggers automatic rollback when needed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MONITOR_LOG="${PROJECT_ROOT}/.rollback-logs/health-monitor.log"
MONITOR_PID_FILE="${PROJECT_ROOT}/.rollback-logs/health-monitor.pid"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"  # Check every 30 seconds
COOLDOWN_PERIOD=300  # 5 minute cooldown after rollback

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[HEALTH-MONITOR]${NC} $(date -u +"%Y-%m-%dT%H:%M:%SZ") $*" | tee -a "$MONITOR_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date -u +"%Y-%m-%dT%H:%M:%SZ") $*" | tee -a "$MONITOR_LOG" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date -u +"%Y-%m-%dT%H:%M:%SZ") $*" | tee -a "$MONITOR_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date -u +"%Y-%m-%dT%H:%M:%SZ") $*" | tee -a "$MONITOR_LOG"
}

# Initialize monitoring
init_monitor() {
    mkdir -p "$(dirname "$MONITOR_LOG")"
    log "Health monitor starting with check interval: ${CHECK_INTERVAL}s"

    # Record PID
    echo $$ > "$MONITOR_PID_FILE"

    # Trap signals for graceful shutdown
    trap cleanup EXIT INT TERM
}

# Cleanup on exit
cleanup() {
    log "Health monitor shutting down"
    rm -f "$MONITOR_PID_FILE"
}

# Check if cooldown period has passed
check_cooldown() {
    local last_rollback_file="${PROJECT_ROOT}/.rollback-logs/last-rollback-time"

    if [ -f "$last_rollback_file" ]; then
        local last_rollback=$(cat "$last_rollback_file")
        local current_time=$(date +%s)
        local elapsed=$((current_time - last_rollback))

        if [ $elapsed -lt $COOLDOWN_PERIOD ]; then
            local remaining=$((COOLDOWN_PERIOD - elapsed))
            log "In cooldown period - ${remaining}s remaining"
            return 1
        fi
    fi

    return 0
}

# Record rollback time
record_rollback() {
    local last_rollback_file="${PROJECT_ROOT}/.rollback-logs/last-rollback-time"
    date +%s > "$last_rollback_file"
}

# Check error rate from Prometheus
check_error_rate() {
    local threshold="${1:-5}"  # 5% default

    # Query Prometheus for error rate
    local query="rate(http_requests_total{status=~\"5..\"}[5m])/rate(http_requests_total[5m])*100"
    local result=$(curl -s "http://localhost:9090/api/v1/query?query=${query}" 2>/dev/null || echo "")

    if [ -z "$result" ]; then
        log_warning "Could not query Prometheus for error rate"
        return 1
    fi

    local error_rate=$(echo "$result" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")

    if [ "$(echo "$error_rate > $threshold" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        log_error "Error rate ${error_rate}% exceeds threshold ${threshold}%"
        export ROLLBACK_REASON="error_rate_threshold:${error_rate}%"
        return 0
    fi

    return 1
}

# Check latency from Prometheus
check_latency() {
    local multiplier="${1:-2}"  # 2x baseline default

    # Query current P95 latency (5 minute window)
    local current_query="histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))"
    local current_result=$(curl -s "http://localhost:9090/api/v1/query?query=${current_query}" 2>/dev/null || echo "")

    if [ -z "$current_result" ]; then
        log_warning "Could not query Prometheus for current latency"
        return 1
    fi

    local current_latency=$(echo "$current_result" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")

    # Query baseline P95 latency (1 hour window, 1 day ago)
    local baseline_query="histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[1h] offset 1d))"
    local baseline_result=$(curl -s "http://localhost:9090/api/v1/query?query=${baseline_query}" 2>/dev/null || echo "")

    if [ -z "$baseline_result" ]; then
        log_warning "Could not query Prometheus for baseline latency"
        return 1
    fi

    local baseline_latency=$(echo "$baseline_result" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")

    # Check if baseline is valid
    if [ "$(echo "$baseline_latency <= 0" | bc -l 2>/dev/null || echo 1)" -eq 1 ]; then
        log_warning "Invalid baseline latency: $baseline_latency"
        return 1
    fi

    # Calculate multiplier
    local latency_mult=$(echo "$current_latency / $baseline_latency" | bc -l 2>/dev/null || echo "0")

    if [ "$(echo "$latency_mult > $multiplier" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        log_error "Latency ${current_latency}s exceeds ${multiplier}x baseline ${baseline_latency}s (${latency_mult}x)"
        export ROLLBACK_REASON="latency_threshold:${latency_mult}x_baseline"
        return 0
    fi

    return 1
}

# Check service health
check_service_health() {
    local failures=0

    # Check Go backend
    if ! curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        log_error "Go backend health check failed"
        ((failures++))
    fi

    # Check Python backend
    if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        log_error "Python backend health check failed"
        ((failures++))
    fi

    # Check Postgres
    if ! pg_isready -h localhost -p 5432 -U tracertm >/dev/null 2>&1; then
        log_error "PostgreSQL health check failed"
        ((failures++))
    fi

    # Check Redis
    if ! redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
        log_error "Redis health check failed"
        ((failures++))
    fi

    # Check NATS
    if ! curl -sf http://localhost:8222/healthz >/dev/null 2>&1; then
        log_error "NATS health check failed"
        ((failures++))
    fi

    if [ $failures -gt 0 ]; then
        export ROLLBACK_REASON="service_health_failures:$failures"
        return 0
    fi

    return 1
}

# Check memory usage
check_memory_usage() {
    local threshold="${1:-90}"  # 90% default

    # Get memory usage
    local memory_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}' 2>/dev/null || \
                         vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages active:\s+(\d+)/ and printf("%.2f", $1 * $size / 1024 / 1024);' 2>/dev/null || \
                         echo "0")

    if [ "$(echo "$memory_usage > $threshold" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        log_warning "Memory usage ${memory_usage}% exceeds threshold ${threshold}%"
        export ROLLBACK_REASON="memory_threshold:${memory_usage}%"
        return 0
    fi

    return 1
}

# Check disk usage
check_disk_usage() {
    local threshold="${1:-85}"  # 85% default

    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$disk_usage" -gt "$threshold" ]; then
        log_warning "Disk usage ${disk_usage}% exceeds threshold ${threshold}%"
        return 0  # Don't trigger rollback, just warn
    fi

    return 1
}

# Perform health checks
perform_health_checks() {
    local issues=0

    # Critical checks (trigger rollback)
    if check_service_health; then
        ((issues++))
    fi

    if check_error_rate 5; then
        ((issues++))
    fi

    if check_latency 2; then
        ((issues++))
    fi

    # Warning checks (don't trigger rollback)
    check_memory_usage 90 || true
    check_disk_usage 85 || true

    return $issues
}

# Trigger automatic rollback
trigger_rollback() {
    log_warning "Health checks failed - triggering automatic rollback"
    log "Rollback reason: ${ROLLBACK_REASON:-unknown}"

    # Record rollback time
    record_rollback

    # Execute rollback
    if bash "${SCRIPT_DIR}/rollback.sh" rollback all; then
        log_success "Automatic rollback completed successfully"

        # Send notification
        send_notification "success" "Automatic rollback completed" "$ROLLBACK_REASON"
    else
        log_error "Automatic rollback failed"

        # Send notification
        send_notification "failure" "Automatic rollback failed" "$ROLLBACK_REASON"
    fi
}

# Send notification (placeholder - integrate with your notification system)
send_notification() {
    local status="$1"
    local message="$2"
    local reason="${3:-unknown}"

    log "Notification: [$status] $message - Reason: $reason"

    # TODO: Integrate with actual notification system
    # Examples:
    # - Slack webhook
    # - PagerDuty
    # - Email
    # - SMS
}

# Monitoring loop
monitor_loop() {
    while true; do
        log "Performing health checks..."

        if perform_health_checks; then
            # Health checks passed
            log_success "All health checks passed"
        else
            # Health checks failed
            if check_cooldown; then
                trigger_rollback
            else
                log_warning "Health checks failed but in cooldown period - skipping rollback"
            fi
        fi

        # Sleep until next check
        sleep "$CHECK_INTERVAL"
    done
}

# Main
main() {
    local action="${1:-start}"

    case "$action" in
        start)
            if [ -f "$MONITOR_PID_FILE" ] && kill -0 "$(cat "$MONITOR_PID_FILE")" 2>/dev/null; then
                log_error "Health monitor is already running (PID: $(cat "$MONITOR_PID_FILE"))"
                exit 1
            fi

            init_monitor
            log "Health monitor started (PID: $$)"
            monitor_loop
            ;;
        stop)
            if [ -f "$MONITOR_PID_FILE" ]; then
                local pid=$(cat "$MONITOR_PID_FILE")
                log "Stopping health monitor (PID: $pid)"
                kill "$pid" 2>/dev/null || true
                rm -f "$MONITOR_PID_FILE"
            else
                log "Health monitor is not running"
            fi
            ;;
        status)
            if [ -f "$MONITOR_PID_FILE" ] && kill -0 "$(cat "$MONITOR_PID_FILE")" 2>/dev/null; then
                log "Health monitor is running (PID: $(cat "$MONITOR_PID_FILE"))"
            else
                log "Health monitor is not running"
            fi
            ;;
        check)
            log "Running one-time health check..."
            if perform_health_checks; then
                log_success "Health check passed"
                exit 0
            else
                log_error "Health check failed"
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {start|stop|status|check}"
            exit 1
            ;;
    esac
}

# Check dependencies
if ! command -v jq &>/dev/null; then
    log_error "jq is required but not installed"
    exit 1
fi

if ! command -v bc &>/dev/null; then
    log_warning "bc not installed - some checks will be limited"
fi

main "$@"
