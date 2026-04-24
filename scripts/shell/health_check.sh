#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE=${1:-tracertm}
CONTEXT=${2:-$(kubectl config current-context)}

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}TraceRTM Health Check${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Namespace: $NAMESPACE"
echo "Context: $CONTEXT"
echo ""

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" --context="$CONTEXT" &> /dev/null; then
    echo -e "${RED}ERROR: Namespace '$NAMESPACE' not found${NC}"
    exit 1
fi

# Function to check pod health
check_pods() {
    local app=$1
    local name=$2

    echo -e "Checking ${YELLOW}$name${NC}..."

    # Get pod status
    local ready=$(kubectl get pods -l app="$app" -n "$NAMESPACE" --context="$CONTEXT" -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
    local running=$(kubectl get pods -l app="$app" -n "$NAMESPACE" --context="$CONTEXT" -o jsonpath='{.items[*].status.phase}' 2>/dev/null)

    if [ -z "$ready" ]; then
        echo -e "${RED}  ✗ No pods found${NC}"
        return 1
    fi

    if [[ "$ready" == *"False"* ]]; then
        echo -e "${RED}  ✗ Not ready${NC}"
        kubectl get pods -l app="$app" -n "$NAMESPACE" --context="$CONTEXT"
        return 1
    elif [[ "$running" != *"Running"* ]]; then
        echo -e "${RED}  ✗ Not running${NC}"
        kubectl get pods -l app="$app" -n "$NAMESPACE" --context="$CONTEXT"
        return 1
    else
        local pod_count=$(kubectl get pods -l app="$app" -n "$NAMESPACE" --context="$CONTEXT" --no-headers | wc -l | tr -d ' ')
        echo -e "${GREEN}  ✓ Healthy ($pod_count pod(s) running)${NC}"
        return 0
    fi
}

# Function to check service
check_service() {
    local service=$1
    local name=$2

    echo -e "Checking ${YELLOW}$name service${NC}..."

    if kubectl get svc "$service" -n "$NAMESPACE" --context="$CONTEXT" &> /dev/null; then
        local endpoints=$(kubectl get endpoints "$service" -n "$NAMESPACE" --context="$CONTEXT" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)
        if [ -z "$endpoints" ]; then
            echo -e "${RED}  ✗ No endpoints${NC}"
            return 1
        else
            echo -e "${GREEN}  ✓ Service active with endpoints${NC}"
            return 0
        fi
    else
        echo -e "${RED}  ✗ Service not found${NC}"
        return 1
    fi
}

# Function to check endpoint health
check_endpoint() {
    local service=$1
    local port=$2
    local path=$3
    local name=$4

    echo -e "Checking ${YELLOW}$name endpoint${NC}..."

    # Port forward in background
    kubectl port-forward "svc/$service" "$port:$port" -n "$NAMESPACE" --context="$CONTEXT" &> /tmp/pf-$service.log &
    local PF_PID=$!

    # Wait for port forward to be ready
    sleep 2

    # Make HTTP request
    if curl -sf "http://localhost:$port$path" &> /dev/null; then
        echo -e "${GREEN}  ✓ Endpoint responding${NC}"
        kill $PF_PID 2>/dev/null || true
        return 0
    else
        echo -e "${RED}  ✗ Endpoint not responding${NC}"
        kill $PF_PID 2>/dev/null || true
        return 1
    fi
}

ERRORS=0

# Infrastructure checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Infrastructure Components${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

check_pods "postgres" "PostgreSQL" || ((ERRORS++))
check_service "postgres-service" "PostgreSQL" || ((ERRORS++))

check_pods "redis" "Cache runtime" || ((ERRORS++))
check_service "redis-service" "Cache runtime" || ((ERRORS++))

check_pods "nats" "NATS" || ((ERRORS++))
check_service "nats-service" "NATS" || ((ERRORS++))

echo ""

# Backend checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Backend Services${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

check_pods "go-backend" "Go Backend" || ((ERRORS++))
check_service "go-backend-service" "Go Backend" || ((ERRORS++))

check_pods "python-backend" "Python Backend" || ((ERRORS++))
check_service "python-backend-service" "Python Backend" || ((ERRORS++))

echo ""

# Ingress checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Ingress${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

check_pods "nginx" "Nginx" || ((ERRORS++))
check_service "nginx-service" "Nginx" || ((ERRORS++))

echo ""

# HPA checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Autoscaling${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

if kubectl get hpa go-backend-hpa -n "$NAMESPACE" --context="$CONTEXT" &> /dev/null; then
    echo -e "${GREEN}✓ Go Backend HPA configured${NC}"
    kubectl get hpa go-backend-hpa -n "$NAMESPACE" --context="$CONTEXT"
else
    echo -e "${RED}✗ Go Backend HPA not found${NC}"
    ((ERRORS++))
fi

echo ""

if kubectl get hpa python-backend-hpa -n "$NAMESPACE" --context="$CONTEXT" &> /dev/null; then
    echo -e "${GREEN}✓ Python Backend HPA configured${NC}"
    kubectl get hpa python-backend-hpa -n "$NAMESPACE" --context="$CONTEXT"
else
    echo -e "${RED}✗ Python Backend HPA not found${NC}"
    ((ERRORS++))
fi

echo ""

# Storage checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Persistent Storage${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

pvcs=$(kubectl get pvc -n "$NAMESPACE" --context="$CONTEXT" --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [ "$pvcs" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $pvcs PVC(s)${NC}"
    kubectl get pvc -n "$NAMESPACE" --context="$CONTEXT"
else
    echo -e "${YELLOW}⚠ No PVCs found${NC}"
fi

echo ""

# Summary
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Summary${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓✓✓ All health checks passed!${NC}"
    echo ""
    echo "Your TraceRTM deployment is healthy and ready."
    exit 0
else
    echo -e "${RED}✗ Health checks failed with $ERRORS error(s)${NC}"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Check pod logs: kubectl logs -l app=<app-name> -n $NAMESPACE"
    echo "  2. Describe pods: kubectl describe pod -l app=<app-name> -n $NAMESPACE"
    echo "  3. Check events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    exit 1
fi
