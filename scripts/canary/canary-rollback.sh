#!/bin/bash
# Emergency Canary Rollback Script
# Immediately reverts canary deployment

set -euo pipefail

NAMESPACE="${NAMESPACE:-tracertm}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $*"
}

main() {
    error "EMERGENCY ROLLBACK INITIATED"

    # 1. Set canary traffic to 0
    log "Disabling canary traffic..."
    kubectl patch ingress tracertm-ingress-canary -n "$NAMESPACE" \
        --type=json \
        -p='[{"op": "replace", "path": "/metadata/annotations/nginx.ingress.kubernetes.io~1canary-weight", "value": "0"}]' \
        2>/dev/null || warn "Failed to patch ingress (may not exist)"

    # 2. Scale canary deployments to 0
    log "Scaling down canary deployments..."
    kubectl scale deployment tracertm-api-canary -n "$NAMESPACE" --replicas=0 2>/dev/null || true
    kubectl scale deployment tracertm-backend-canary -n "$NAMESPACE" --replicas=0 2>/dev/null || true

    # 3. Wait for pods to terminate
    log "Waiting for canary pods to terminate..."
    kubectl wait --for=delete pod -l version=canary -n "$NAMESPACE" --timeout=60s 2>/dev/null || true

    # 4. Verify stable is healthy
    log "Verifying stable deployment health..."
    kubectl rollout status deployment/tracertm-api -n "$NAMESPACE" --timeout=30s
    kubectl rollout status deployment/tracertm-backend -n "$NAMESPACE" --timeout=30s

    log "✓ Canary rollback complete"
    log "All traffic is now routed to stable version"
}

main "$@"
