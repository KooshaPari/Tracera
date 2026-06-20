#!/bin/bash
# Canary Deployment Script
# Manages progressive traffic shifting from 10% -> 50% -> 100%

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-tracertm}"
CANARY_IMAGE_TAG="${CANARY_IMAGE_TAG:-canary}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus:9090}"
CHECK_INTERVAL=60  # seconds between checks
PROMOTION_THRESHOLD_DURATION=300  # 5 minutes at each stage

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $*"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $*"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        error "kubectl not found. Please install kubectl."
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        error "jq not found. Please install jq."
        exit 1
    fi

    # Check kubectl access
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        error "Cannot access namespace $NAMESPACE"
        exit 1
    fi

    log "Prerequisites check passed"
}

# Deploy canary version
deploy_canary() {
    log "Deploying canary version..."

    # Update canary deployment with new image
    kubectl set image deployment/tracertm-api-canary \
        api="tracertm-api:${CANARY_IMAGE_TAG}" \
        -n "$NAMESPACE"

    kubectl set image deployment/tracertm-backend-canary \
        backend="tracertm-backend:${CANARY_IMAGE_TAG}" \
        -n "$NAMESPACE"

    log "Waiting for canary deployments to be ready..."
    kubectl rollout status deployment/tracertm-api-canary -n "$NAMESPACE" --timeout=5m
    kubectl rollout status deployment/tracertm-backend-canary -n "$NAMESPACE" --timeout=5m

    log "Canary deployment successful"
}

# Query Prometheus metrics
query_prometheus() {
    local query="$1"
    local result

    result=$(curl -s -G \
        --data-urlencode "query=${query}" \
        "${PROMETHEUS_URL}/api/v1/query" | jq -r '.data.result[0].value[1] // "0"')

    echo "$result"
}

# Check canary health metrics
check_metrics() {
    local error_rate
    local latency_p95
    local latency_p99
    local success_rate

    log "Checking canary metrics..."

    # Get error rate (should be < 1%)
    error_rate=$(query_prometheus "tracertm:canary:error_rate")
    error_rate_percent=$(echo "$error_rate * 100" | bc -l)

    # Get P95 latency (should be < 500ms)
    latency_p95=$(query_prometheus "tracertm:canary:latency_p95")
    latency_p95_ms=$(echo "$latency_p95 * 1000" | bc -l)

    # Get P99 latency (should be < 1s)
    latency_p99=$(query_prometheus "tracertm:canary:latency_p99")
    latency_p99_ms=$(echo "$latency_p99 * 1000" | bc -l)

    # Get success rate (should be > 99%)
    success_rate=$(query_prometheus "tracertm:canary:success_rate")
    success_rate_percent=$(echo "$success_rate * 100" | bc -l)

    log "Metrics:"
    log "  Error Rate: ${error_rate_percent}%"
    log "  P95 Latency: ${latency_p95_ms}ms"
    log "  P99 Latency: ${latency_p99_ms}ms"
    log "  Success Rate: ${success_rate_percent}%"

    # Check thresholds
    local failures=0

    if (( $(echo "$error_rate > 0.01" | bc -l) )); then
        error "Error rate ${error_rate_percent}% exceeds threshold (1%)"
        failures=$((failures + 1))
    fi

    if (( $(echo "$latency_p95 > 0.5" | bc -l) )); then
        error "P95 latency ${latency_p95_ms}ms exceeds threshold (500ms)"
        failures=$((failures + 1))
    fi

    if (( $(echo "$latency_p99 > 1.0" | bc -l) )); then
        warn "P99 latency ${latency_p99_ms}ms exceeds threshold (1000ms)"
    fi

    if (( $(echo "$success_rate < 0.99" | bc -l) )); then
        error "Success rate ${success_rate_percent}% below threshold (99%)"
        failures=$((failures + 1))
    fi

    return $failures
}

# Check pod health
check_pod_health() {
    log "Checking pod health..."

    # Check if pods are ready
    local canary_ready
    canary_ready=$(kubectl get deployment tracertm-api-canary -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}/{.status.replicas}')

    local backend_ready
    backend_ready=$(kubectl get deployment tracertm-backend-canary -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}/{.status.replicas}')

    log "API Canary: $canary_ready ready"
    log "Backend Canary: $backend_ready ready"

    # Check for pod restarts
    local restarts
    restarts=$(kubectl get pods -n "$NAMESPACE" -l version=canary \
        -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' | \
        awk '{for(i=1;i<=NF;i++) sum+=$i} END {print sum}')

    if [ "$restarts" -gt 2 ]; then
        error "Canary pods have $restarts restarts"
        return 1
    fi

    log "Pod health check passed"
    return 0
}

# Set traffic weight
set_traffic_weight() {
    local weight=$1
    log "Setting canary traffic weight to ${weight}%..."

    # Update ingress canary weight annotation
    kubectl patch ingress tracertm-ingress-canary -n "$NAMESPACE" \
        --type=json \
        -p="[{\"op\": \"replace\", \"path\": \"/metadata/annotations/nginx.ingress.kubernetes.io~1canary-weight\", \"value\": \"${weight}\"}]"

    log "Traffic weight set to ${weight}%"

    # Wait for ingress to propagate
    sleep 10
}

# Monitor stage
monitor_stage() {
    local stage=$1
    local duration=$2
    local checks=$((duration / CHECK_INTERVAL))

    log "Monitoring $stage stage for ${duration}s..."

    for ((i=1; i<=checks; i++)); do
        log "Check $i/$checks..."

        # Check pod health
        if ! check_pod_health; then
            error "Pod health check failed"
            return 1
        fi

        # Check metrics (allow first check to warm up)
        if [ "$i" -gt 1 ]; then
            if ! check_metrics; then
                error "Metrics check failed"
                return 1
            fi
        fi

        if [ "$i" -lt "$checks" ]; then
            log "Waiting ${CHECK_INTERVAL}s before next check..."
            sleep "$CHECK_INTERVAL"
        fi
    done

    log "$stage stage monitoring complete - all checks passed"
    return 0
}

# Rollback canary
rollback_canary() {
    error "Rolling back canary deployment..."

    # Set traffic weight to 0
    set_traffic_weight 0

    # Scale down canary deployments
    kubectl scale deployment tracertm-api-canary -n "$NAMESPACE" --replicas=0
    kubectl scale deployment tracertm-backend-canary -n "$NAMESPACE" --replicas=0

    error "Canary rollback complete"
}

# Promote canary to stable
promote_canary() {
    log "Promoting canary to stable..."

    # Update stable deployments with canary image
    kubectl set image deployment/tracertm-api \
        api="tracertm-api:${CANARY_IMAGE_TAG}" \
        -n "$NAMESPACE"

    kubectl set image deployment/tracertm-backend \
        backend="tracertm-backend:${CANARY_IMAGE_TAG}" \
        -n "$NAMESPACE"

    log "Waiting for stable deployments to roll out..."
    kubectl rollout status deployment/tracertm-api -n "$NAMESPACE" --timeout=10m
    kubectl rollout status deployment/tracertm-backend -n "$NAMESPACE" --timeout=10m

    # Set canary traffic to 0
    set_traffic_weight 0

    # Scale down canary deployments
    kubectl scale deployment tracertm-api-canary -n "$NAMESPACE" --replicas=0
    kubectl scale deployment tracertm-backend-canary -n "$NAMESPACE" --replicas=0

    log "Canary promotion complete!"
}

# Main deployment flow
main() {
    log "Starting canary deployment..."
    log "Namespace: $NAMESPACE"
    log "Image Tag: $CANARY_IMAGE_TAG"

    # Check prerequisites
    check_prerequisites

    # Deploy canary
    deploy_canary

    # Stage 1: 10% traffic
    log "=== Stage 1: 10% Traffic ==="
    set_traffic_weight 10
    if ! monitor_stage "10%" "$PROMOTION_THRESHOLD_DURATION"; then
        rollback_canary
        exit 1
    fi

    # Stage 2: 50% traffic
    log "=== Stage 2: 50% Traffic ==="
    set_traffic_weight 50
    if ! monitor_stage "50%" "$PROMOTION_THRESHOLD_DURATION"; then
        rollback_canary
        exit 1
    fi

    # Stage 3: 100% traffic (promote to stable)
    log "=== Stage 3: 100% Traffic (Promotion) ==="
    promote_canary

    log "✓ Canary deployment completed successfully!"
}

# Handle script interruption
trap 'error "Script interrupted"; rollback_canary; exit 130' INT TERM

# Run main function
main "$@"
