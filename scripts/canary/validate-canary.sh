#!/bin/bash
# Pre-deployment validation script
# Validates environment and prerequisites before canary deployment

set -euo pipefail

NAMESPACE="${NAMESPACE:-tracertm}"
IMAGE_TAG="${IMAGE_TAG:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[CHECK]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

CHECKS_PASSED=0
CHECKS_FAILED=0

check() {
    local name="$1"
    shift
    log "Checking: $name"

    if "$@"; then
        echo -e "${GREEN}  ✓ Passed${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}  ✗ Failed${NC}"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

# Check prerequisites
check_kubectl() {
    command -v kubectl &> /dev/null
}

check_jq() {
    command -v jq &> /dev/null
}

check_curl() {
    command -v curl &> /dev/null
}

# Check cluster access
check_cluster() {
    kubectl cluster-info &> /dev/null
}

check_namespace() {
    kubectl get namespace "$NAMESPACE" &> /dev/null
}

# Check required resources exist
check_stable_deployments() {
    kubectl get deployment tracertm-api -n "$NAMESPACE" &> /dev/null && \
    kubectl get deployment tracertm-backend -n "$NAMESPACE" &> /dev/null
}

check_stable_healthy() {
    local api_ready backend_ready

    api_ready=$(kubectl get deployment tracertm-api -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}/{.status.replicas}' 2>/dev/null || echo "0/0")

    backend_ready=$(kubectl get deployment tracertm-backend -n "$NAMESPACE" \
        -o jsonpath='{.status.readyReplicas}/{.status.replicas}' 2>/dev/null || echo "0/0")

    log "Stable deployments: API=$api_ready, Backend=$backend_ready"

    [ "$api_ready" != "0/0" ] && [[ "$api_ready" =~ ^([0-9]+)/\1$ ]] && \
    [ "$backend_ready" != "0/0" ] && [[ "$backend_ready" =~ ^([0-9]+)/\1$ ]]
}

check_ingress_exists() {
    kubectl get ingress tracertm-ingress -n "$NAMESPACE" &> /dev/null
}

check_prometheus() {
    local prometheus_url="${PROMETHEUS_URL:-http://prometheus:9090}"

    if [[ "$prometheus_url" =~ ^http://prometheus ]]; then
        # Cluster-internal URL, check via kubectl
        kubectl get service prometheus -n "$NAMESPACE" &> /dev/null || \
        kubectl get service prometheus -n monitoring &> /dev/null
    else
        # External URL, check with curl
        curl -sf "${prometheus_url}/-/healthy" &> /dev/null
    fi
}

check_image_tag() {
    if [ -z "$IMAGE_TAG" ]; then
        error "IMAGE_TAG environment variable not set"
        return 1
    fi
    log "Image tag: $IMAGE_TAG"
    return 0
}

check_no_active_canary() {
    local canary_weight

    canary_weight=$(kubectl get ingress tracertm-ingress-canary -n "$NAMESPACE" \
        -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}' \
        2>/dev/null || echo "0")

    if [ "$canary_weight" != "0" ]; then
        warn "Active canary detected (weight: ${canary_weight}%)"
        return 1
    fi
    return 0
}

check_servicemonitor() {
    kubectl get servicemonitor -n "$NAMESPACE" &> /dev/null || \
    kubectl get servicemonitor -n monitoring &> /dev/null
}

main() {
    echo -e "\n${GREEN}=== Canary Deployment Validation ===${NC}\n"

    # Prerequisites
    echo "Prerequisites:"
    check "kubectl installed" check_kubectl
    check "jq installed" check_jq
    check "curl installed" check_curl

    # Cluster access
    echo -e "\nCluster Access:"
    check "Kubernetes cluster accessible" check_cluster
    check "Namespace '$NAMESPACE' exists" check_namespace

    # Stable deployments
    echo -e "\nStable Deployments:"
    check "Stable deployments exist" check_stable_deployments
    check "Stable deployments healthy" check_stable_healthy

    # Infrastructure
    echo -e "\nInfrastructure:"
    check "Ingress exists" check_ingress_exists
    check "Prometheus accessible" check_prometheus
    check "ServiceMonitor exists" check_servicemonitor

    # Pre-deployment checks
    echo -e "\nPre-deployment:"
    check "Image tag specified" check_image_tag
    check "No active canary deployment" check_no_active_canary

    # Summary
    echo -e "\n${GREEN}=== Validation Summary ===${NC}\n"
    echo "Checks Passed: ${CHECKS_PASSED}"
    echo "Checks Failed: ${CHECKS_FAILED}"

    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All validations passed - ready for canary deployment${NC}\n"
        return 0
    else
        echo -e "\n${RED}✗ Some validations failed - fix issues before deploying${NC}\n"
        return 1
    fi
}

main "$@"
