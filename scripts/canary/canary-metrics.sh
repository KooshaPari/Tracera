#!/bin/bash
# Canary Metrics Analysis Script
# Provides detailed metrics comparison between canary and stable versions

set -euo pipefail

NAMESPACE="${NAMESPACE:-tracertm}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus:9090}"
LOOKBACK="${LOOKBACK:-5m}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

query_prometheus() {
    local query="$1"
    curl -s -G --data-urlencode "query=${query}" "${PROMETHEUS_URL}/api/v1/query" | \
        jq -r '.data.result[0].value[1] // "0"'
}

format_percentage() {
    local value=$1
    printf "%.2f%%" "$(echo "$value * 100" | bc -l)"
}

format_milliseconds() {
    local value=$1
    printf "%.2fms" "$(echo "$value * 1000" | bc -l)"
}

format_requests() {
    local value=$1
    printf "%.2f req/s" "$value"
}

compare_versions() {
    echo -e "\n${GREEN}=== Canary vs Stable Comparison ===${NC}\n"

    # Error Rate
    echo "Error Rate (target: <1%):"
    local canary_error=$(query_prometheus "tracertm:canary:error_rate")
    local stable_error=$(query_prometheus "tracertm:stable:error_rate")
    echo "  Canary: $(format_percentage "$canary_error")"
    echo "  Stable: $(format_percentage "$stable_error")"
    local error_diff=$(echo "$canary_error - $stable_error" | bc -l)
    if (( $(echo "$error_diff > 0.005" | bc -l) )); then
        echo -e "  ${RED}⚠ Canary error rate is significantly higher${NC}"
    else
        echo -e "  ${GREEN}✓ Error rate acceptable${NC}"
    fi

    # P95 Latency
    echo -e "\nP95 Latency (target: <500ms):"
    local canary_p95=$(query_prometheus "tracertm:canary:latency_p95")
    local stable_p95=$(query_prometheus "tracertm:stable:latency_p95")
    echo "  Canary: $(format_milliseconds "$canary_p95")"
    echo "  Stable: $(format_milliseconds "$stable_p95")"
    local latency_diff=$(echo "$canary_p95 - $stable_p95" | bc -l)
    if (( $(echo "$latency_diff > 0.1" | bc -l) )); then
        echo -e "  ${YELLOW}⚠ Canary latency is higher${NC}"
    else
        echo -e "  ${GREEN}✓ Latency acceptable${NC}"
    fi

    # P99 Latency
    echo -e "\nP99 Latency (target: <1000ms):"
    local canary_p99=$(query_prometheus "tracertm:canary:latency_p99")
    local stable_p99=$(query_prometheus "tracertm:stable:latency_p99")
    echo "  Canary: $(format_milliseconds "$canary_p99")"
    echo "  Stable: $(format_milliseconds "$stable_p99")"

    # Request Rate
    echo -e "\nRequest Rate:"
    local canary_rate=$(query_prometheus "tracertm:canary:request_rate")
    local stable_rate=$(query_prometheus "tracertm:stable:request_rate")
    echo "  Canary: $(format_requests "$canary_rate")"
    echo "  Stable: $(format_requests "$stable_rate")"

    # Success Rate
    echo -e "\nSuccess Rate (target: >99%):"
    local canary_success=$(query_prometheus "tracertm:canary:success_rate")
    local stable_success=$(query_prometheus "tracertm:stable:success_rate")
    echo "  Canary: $(format_percentage "$canary_success")"
    echo "  Stable: $(format_percentage "$stable_success")"
    if (( $(echo "$canary_success < 0.99" | bc -l) )); then
        echo -e "  ${RED}⚠ Canary success rate below threshold${NC}"
    else
        echo -e "  ${GREEN}✓ Success rate acceptable${NC}"
    fi

    # Overall verdict
    echo -e "\n${GREEN}=== Overall Assessment ===${NC}"
    if (( $(echo "$canary_error > 0.01" | bc -l) )) || \
       (( $(echo "$canary_p95 > 0.5" | bc -l) )) || \
       (( $(echo "$canary_success < 0.99" | bc -l) )); then
        echo -e "${RED}⚠ CANARY HAS ISSUES - CONSIDER ROLLBACK${NC}"
        return 1
    else
        echo -e "${GREEN}✓ CANARY METRICS LOOK GOOD${NC}"
        return 0
    fi
}

show_active_alerts() {
    echo -e "\n${GREEN}=== Active Alerts ===${NC}\n"

    local alerts=$(curl -s "${PROMETHEUS_URL}/api/v1/alerts" | \
        jq -r '.data.alerts[] | select(.labels.component == "canary") |
        "\(.labels.alertname): \(.annotations.summary)"')

    if [ -z "$alerts" ]; then
        echo "No active canary alerts"
    else
        echo "$alerts"
    fi
}

show_pod_status() {
    echo -e "\n${GREEN}=== Pod Status ===${NC}\n"

    kubectl get pods -n "$NAMESPACE" -l version=canary \
        -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,AGE:.metadata.creationTimestamp
}

main() {
    echo -e "${GREEN}Canary Metrics Analysis${NC}"
    echo "Namespace: $NAMESPACE"
    echo "Lookback: $LOOKBACK"
    echo ""

    compare_versions
    show_active_alerts
    show_pod_status
}

main "$@"
