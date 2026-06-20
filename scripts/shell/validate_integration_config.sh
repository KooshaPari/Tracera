#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load integration config
if [ -f .env.integration ]; then
    export $(cat .env.integration | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env.integration file not found${NC}"
    exit 1
fi

echo "======================================================================"
echo "TraceRTM Integration Configuration Validation"
echo "======================================================================"
echo ""

# Function to check service
check_service() {
    local service_name=$1
    local check_command=$2

    echo -n "Checking $service_name... "
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local service_name=$1
    local url=$2

    echo -n "Checking $service_name... "
    if curl -f -s -o /dev/null --max-time 5 "$url"; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Not reachable (may not be running)${NC}"
        return 1
    fi
}

# Track overall status
FAILED=0

echo "Infrastructure Checks:"
echo "----------------------------------------------------------------------"

# PostgreSQL
if ! check_service "PostgreSQL" "psql \"$DATABASE_URL\" -c 'SELECT 1'"; then
    echo "  Error: Could not connect to PostgreSQL"
    echo "  URL: $DATABASE_URL"
    FAILED=1
fi

# NATS (check if nats-cli is installed first)
if command -v nats &> /dev/null; then
    if ! check_service "NATS" "nats --server \"$NATS_URL\" account info"; then
        echo "  Error: Could not connect to NATS"
        echo "  URL: $NATS_URL"
        FAILED=1
    fi
else
    echo -e "Checking NATS... ${YELLOW}⚠ nats-cli not installed, skipping${NC}"
fi

# Redis
if command -v redis-cli &> /dev/null; then
    if ! check_service "Redis" "redis-cli -u \"$REDIS_URL\" PING"; then
        echo "  Error: Could not connect to Redis"
        echo "  URL: ${REDIS_URL%%@*}@***" # Mask password
        FAILED=1
    fi
else
    echo -e "Checking Redis... ${YELLOW}⚠ redis-cli not installed, skipping${NC}"
fi

# Neo4j (basic check if bolt protocol is available)
echo -n "Checking Neo4j... "
if command -v cypher-shell &> /dev/null; then
    if cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${YELLOW}⚠ Not reachable (may not be running)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ cypher-shell not installed, skipping${NC}"
fi

echo ""
echo "Backend Service Checks:"
echo "----------------------------------------------------------------------"

# Go Backend
check_http "Go Backend" "$GO_BACKEND_URL/health"

# Python Backend
check_http "Python Backend" "$PYTHON_BACKEND_URL/health"

echo ""
echo "Configuration Validation:"
echo "----------------------------------------------------------------------"

# Check required environment variables
REQUIRED_VARS=(
    "DATABASE_URL"
    "REDIS_URL"
    "NATS_URL"
    "NEO4J_URI"
    "WORKOS_CLIENT_ID"
    "WORKOS_API_KEY"
    "JWT_SECRET"
)

for var in "${REQUIRED_VARS[@]}"; do
    echo -n "Checking $var... "
    if [ -z "${!var}" ]; then
        echo -e "${RED}✗ Not set${NC}"
        FAILED=1
    else
        echo -e "${GREEN}✓ Set${NC}"
    fi
done

echo ""
echo "======================================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All integration checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed. Please review the errors above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Ensure all services are running (PostgreSQL, Redis, NATS)"
    echo "  - Check connection strings in .env.integration"
    echo "  - Verify network connectivity to remote services"
    exit 1
fi
