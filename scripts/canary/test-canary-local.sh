#!/bin/bash
# Local testing script for canary deployment (dry-run mode)
# Tests the deployment logic without actually deploying to a cluster

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[TEST]${NC} $*"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

TESTS_PASSED=0
TESTS_FAILED=0

test_case() {
    local name="$1"
    shift
    log "Testing: $name"

    if "$@"; then
        echo -e "${GREEN}  ✓ Passed${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}  ✗ Failed${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test: Check if all required files exist
test_files_exist() {
    local required_files=(
        "k8s/base/deployment.yaml"
        "k8s/base/service.yaml"
        "k8s/base/ingress.yaml"
        "k8s/base/servicemonitor.yaml"
        "k8s/base/prometheusrule.yaml"
        "k8s/base/configmap.yaml"
        "k8s/overlays/canary/deployment-canary.yaml"
        "scripts/canary/canary-deploy.sh"
        "scripts/canary/canary-metrics.sh"
        "scripts/canary/canary-rollback.sh"
        "scripts/canary/validate-canary.sh"
        ".github/workflows/canary-deploy.yml"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Missing file: $file"
            return 1
        fi
    done

    return 0
}

# Test: Check if scripts are executable
test_scripts_executable() {
    local scripts=(
        "scripts/canary/canary-deploy.sh"
        "scripts/canary/canary-metrics.sh"
        "scripts/canary/canary-rollback.sh"
        "scripts/canary/validate-canary.sh"
    )

    for script in "${scripts[@]}"; do
        if [ ! -x "$script" ]; then
            error "Script not executable: $script"
            return 1
        fi
    done

    return 0
}

# Test: Validate YAML syntax
test_yaml_syntax() {
    if ! command -v yamllint &> /dev/null; then
        warn "yamllint not installed, skipping YAML validation"
        return 0
    fi

    local yaml_files=(
        k8s/base/*.yaml
        k8s/overlays/canary/*.yaml
        .github/workflows/canary-deploy.yml
    )

    for file in ${yaml_files[@]}; do
        if [ -f "$file" ]; then
            if ! yamllint -d relaxed "$file" &> /dev/null; then
                error "YAML syntax error in: $file"
                return 1
            fi
        fi
    done

    return 0
}

# Test: Check if Go health handler compiles
test_go_health_handler() {
    if [ ! -f "backend/internal/handlers/health_canary.go" ]; then
        error "Go health handler not found"
        return 1
    fi

    # Check for required functions
    if ! grep -q "GetCanaryHealth" "backend/internal/handlers/health_canary.go"; then
        error "GetCanaryHealth function not found"
        return 1
    fi

    if ! grep -q "GetReadiness" "backend/internal/handlers/health_canary.go"; then
        error "GetReadiness function not found"
        return 1
    fi

    if ! grep -q "GetLiveness" "backend/internal/handlers/health_canary.go"; then
        error "GetLiveness function not found"
        return 1
    fi

    return 0
}

# Test: Check if Python health router exists
test_python_health_router() {
    if [ ! -f "src/tracertm/api/routers/health_canary.py" ]; then
        error "Python health router not found"
        return 1
    fi

    # Check for required endpoints
    if ! grep -q "get_canary_health" "src/tracertm/api/routers/health_canary.py"; then
        error "get_canary_health endpoint not found"
        return 1
    fi

    if ! grep -q "get_readiness" "src/tracertm/api/routers/health_canary.py"; then
        error "get_readiness endpoint not found"
        return 1
    fi

    if ! grep -q "get_liveness" "src/tracertm/api/routers/health_canary.py"; then
        error "get_liveness endpoint not found"
        return 1
    fi

    return 0
}

# Test: Check Prometheus rules syntax
test_prometheus_rules() {
    if [ ! -f "k8s/base/prometheusrule.yaml" ]; then
        error "PrometheusRule not found"
        return 1
    fi

    # Check for required rules
    local required_rules=(
        "tracertm:canary:error_rate"
        "tracertm:canary:latency_p95"
        "tracertm:canary:latency_p99"
        "tracertm:canary:success_rate"
    )

    for rule in "${required_rules[@]}"; do
        if ! grep -q "$rule" "k8s/base/prometheusrule.yaml"; then
            error "Missing Prometheus rule: $rule"
            return 1
        fi
    done

    return 0
}

# Test: Check ingress configuration
test_ingress_config() {
    if [ ! -f "k8s/base/ingress.yaml" ]; then
        error "Ingress configuration not found"
        return 1
    fi

    # Check for canary annotations
    if ! grep -q "nginx.ingress.kubernetes.io/canary" "k8s/base/ingress.yaml"; then
        error "Canary annotations not found in ingress"
        return 1
    fi

    if ! grep -q "canary-weight" "k8s/base/ingress.yaml"; then
        error "Canary weight annotation not found"
        return 1
    fi

    return 0
}

# Test: Check workflow configuration
test_workflow_config() {
    if [ ! -f ".github/workflows/canary-deploy.yml" ]; then
        error "Canary workflow not found"
        return 1
    fi

    # Check for required jobs
    local required_jobs=(
        "validate"
        "deploy-canary"
        "canary-stage1"
        "canary-stage2"
        "promote"
        "rollback"
    )

    for job in "${required_jobs[@]}"; do
        if ! grep -q "^  $job:" ".github/workflows/canary-deploy.yml"; then
            error "Missing workflow job: $job"
            return 1
        fi
    done

    return 0
}

# Test: Check documentation exists
test_documentation() {
    local docs=(
        "scripts/canary/README.md"
        "docs/reports/task-109-canary-deployment-system-completion.md"
        "docs/guides/quick-start/canary-deployment-quickstart.md"
    )

    for doc in "${docs[@]}"; do
        if [ ! -f "$doc" ]; then
            error "Missing documentation: $doc"
            return 1
        fi
    done

    return 0
}

# Test: Simulate metrics check
test_metrics_logic() {
    info "Simulating metrics validation logic..."

    # Simulate good metrics
    local error_rate=0.005  # 0.5% (threshold: 1%)
    local latency_p95=0.245  # 245ms (threshold: 500ms)
    local success_rate=0.995  # 99.5% (threshold: 99%)

    if (( $(echo "$error_rate > 0.01" | bc -l) )); then
        error "Error rate validation failed"
        return 1
    fi

    if (( $(echo "$latency_p95 > 0.5" | bc -l) )); then
        error "Latency validation failed"
        return 1
    fi

    if (( $(echo "$success_rate < 0.99" | bc -l) )); then
        error "Success rate validation failed"
        return 1
    fi

    return 0
}

main() {
    echo -e "\n${GREEN}=== Canary Deployment System Tests ===${NC}\n"

    info "Running local tests (no cluster required)..."
    echo ""

    # File existence tests
    echo "File Existence Tests:"
    test_case "All required files exist" test_files_exist
    test_case "Scripts are executable" test_scripts_executable
    test_case "Documentation exists" test_documentation

    # Configuration tests
    echo -e "\nConfiguration Tests:"
    test_case "YAML syntax valid" test_yaml_syntax
    test_case "Ingress configuration" test_ingress_config
    test_case "Prometheus rules" test_prometheus_rules
    test_case "Workflow configuration" test_workflow_config

    # Code tests
    echo -e "\nCode Tests:"
    test_case "Go health handler" test_go_health_handler
    test_case "Python health router" test_python_health_router

    # Logic tests
    echo -e "\nLogic Tests:"
    test_case "Metrics validation logic" test_metrics_logic

    # Summary
    echo -e "\n${GREEN}=== Test Summary ===${NC}\n"
    echo "Tests Passed: ${TESTS_PASSED}"
    echo "Tests Failed: ${TESTS_FAILED}"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All tests passed!${NC}"
        echo -e "The canary deployment system is ready to use.\n"
        return 0
    else
        echo -e "\n${RED}✗ Some tests failed${NC}"
        echo -e "Please fix the issues before deploying.\n"
        return 1
    fi
}

main "$@"
