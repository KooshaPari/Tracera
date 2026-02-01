#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$SCRIPT_DIR/../infrastructure/k8s"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Kubernetes Manifest Validation${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}ERROR: kubectl not found${NC}"
    exit 1
fi

ERRORS=0
WARNINGS=0

# Function to validate a manifest
validate_manifest() {
    local file=$1
    local name=$(basename "$file")

    echo -e "Validating: ${YELLOW}$name${NC}"

    # Check if file exists
    if [ ! -f "$file" ]; then
        echo -e "${RED}  ✗ File not found${NC}"
        ((ERRORS++))
        return
    fi

    # Validate YAML syntax
    if ! kubectl apply -f "$file" --dry-run=client &> /tmp/validate-error.txt; then
        echo -e "${RED}  ✗ Invalid YAML or Kubernetes resource${NC}"
        cat /tmp/validate-error.txt | head -5
        ((ERRORS++))
        return
    fi

    # Server-side validation (if connected to cluster)
    if kubectl cluster-info &> /dev/null; then
        if ! kubectl apply -f "$file" --dry-run=server &> /tmp/validate-server-error.txt; then
            echo -e "${YELLOW}  ⚠ Server-side validation warnings${NC}"
            cat /tmp/validate-server-error.txt | head -3
            ((WARNINGS++))
        else
            echo -e "${GREEN}  ✓ Valid${NC}"
        fi
    else
        echo -e "${GREEN}  ✓ Client-side validation passed${NC}"
        echo -e "${YELLOW}  ⚠ Not connected to cluster - skipping server-side validation${NC}"
    fi

    echo ""
}

# Validate all manifests in order
echo -e "${GREEN}Validating manifests...${NC}"
echo ""

validate_manifest "$K8S_DIR/00-namespace.yaml"
validate_manifest "$K8S_DIR/01-configmaps.yaml"
validate_manifest "$K8S_DIR/02-secrets.yaml"
validate_manifest "$K8S_DIR/03-postgres.yaml"
validate_manifest "$K8S_DIR/04-redis.yaml"
validate_manifest "$K8S_DIR/05-nats.yaml"
validate_manifest "$K8S_DIR/06-go-backend.yaml"
validate_manifest "$K8S_DIR/07-python-backend.yaml"
validate_manifest "$K8S_DIR/08-ingress.yaml"

# Optional manifests
if [ -f "$K8S_DIR/09-monitoring.yaml" ]; then
    validate_manifest "$K8S_DIR/09-monitoring.yaml"
fi

if [ -f "$K8S_DIR/10-network-policies.yaml" ]; then
    validate_manifest "$K8S_DIR/10-network-policies.yaml"
fi

# Summary
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Validation Summary${NC}"
echo -e "${GREEN}=========================================${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All manifests are valid${NC}"
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $WARNINGS warning(s)${NC}"
fi

echo ""

# Security checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Security Checks${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

echo -e "${YELLOW}Checking secrets configuration...${NC}"

# Check if default passwords are still in use
if grep -q "CHANGE_ME" "$K8S_DIR/02-secrets.yaml"; then
    echo -e "${RED}✗ WARNING: Default secrets detected in 02-secrets.yaml${NC}"
    echo -e "${RED}  Please update all CHANGE_ME values before deployment!${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ No default secrets detected${NC}"
fi

# Check for self-signed certificates
if grep -q "REPLACE_WITH_YOUR" "$K8S_DIR/02-secrets.yaml"; then
    echo -e "${YELLOW}⚠ Placeholder TLS certificates detected${NC}"
    echo -e "${YELLOW}  Update with valid certificates for production${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ TLS certificates configured${NC}"
fi

echo ""

# Resource checks
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Resource Checks${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

echo -e "${YELLOW}Checking resource configurations...${NC}"

# Extract and sum resource requests
total_cpu_requests=0
total_mem_requests=0

for file in "$K8S_DIR"/*.yaml; do
    # This is a simplified check - you'd want more sophisticated parsing in production
    if grep -q "resources:" "$file"; then
        echo -e "${GREEN}✓ Resources defined in $(basename "$file")${NC}"
    fi
done

echo ""

# Final summary
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Final Summary${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓✓✓ All validations passed! Ready to deploy.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation passed with $WARNINGS warning(s)${NC}"
    echo -e "${YELLOW}Review warnings before production deployment${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo -e "${RED}Fix errors before deployment${NC}"
    exit 1
fi
