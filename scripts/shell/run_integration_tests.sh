#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Integration Test Suite${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.test.yml"
WAIT_TIME=10

# Check if docker-compose.test.yml exists and still matches the Dragonfly layout
if [ ! -f "$DOCKER_COMPOSE_FILE" ] || ! grep -q '^  dragonfly:' "$DOCKER_COMPOSE_FILE"; then
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "${YELLOW}Warning: $DOCKER_COMPOSE_FILE is stale or missing Dragonfly${NC}"
    else
        echo -e "${YELLOW}Warning: $DOCKER_COMPOSE_FILE not found${NC}"
    fi
    echo -e "${YELLOW}Creating minimal test configuration...${NC}"

    cat > "$DOCKER_COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: testdb
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser"]
      interval: 5s
      timeout: 5s
      retries: 5

  dragonfly:
    image: docker.dragonflydb.io/dragonflydb/dragonfly:latest
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  nats:
    image: nats:2.10-alpine
    ports:
      - "4223:4222"
      - "8223:8222"
    command: "-js -m 8222"
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8222/healthz"]
      interval: 5s
      timeout: 5s
      retries: 5
EOF
fi

# Function to check if a service is healthy
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}Waiting for $service to be healthy...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps $service | grep -q "healthy\|Up"; then
            echo -e "${GREEN}✓ $service is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done

    echo -e "${RED}✗ $service failed to start${NC}"
    return 1
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up test infrastructure...${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v 2>/dev/null || true
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start test infrastructure
echo -e "${YELLOW}Starting test infrastructure...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

# Wait for services to be healthy
wait_for_service postgres
wait_for_service dragonfly
wait_for_service nats

echo -e "${GREEN}All services are ready!${NC}"
echo ""

# Export test environment variables
export DATABASE_URL="postgresql://testuser:testpass@localhost:5433/testdb"
export REDIS_URL="redis://localhost:6380"
export NATS_URL="nats://localhost:4223"
export NATS_INTEGRATION_TESTS="true"

# Run Go integration tests
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Running Go Integration Tests${NC}"
echo -e "${GREEN}========================================${NC}"

GO_TEST_EXIT_CODE=0

if [ -d "backend/tests/integration/python" ]; then
    cd backend/tests/integration/python
    echo -e "${YELLOW}Running Python client integration tests...${NC}"
    go test -v -timeout 5m . || GO_TEST_EXIT_CODE=$?
    cd ../../../..
else
    echo -e "${YELLOW}Warning: Go integration tests directory not found${NC}"
fi

if [ $GO_TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Go integration tests passed${NC}"
else
    echo -e "${RED}✗ Go integration tests failed${NC}"
fi

echo ""

# Run Python integration tests
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Running Python Integration Tests${NC}"
echo -e "${GREEN}========================================${NC}"

PYTHON_TEST_EXIT_CODE=0

if [ -d "tests/integration" ]; then
    echo -e "${YELLOW}Running integration tests...${NC}"

    # Check if virtual environment exists
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Run tests with pytest
    pytest tests/integration/test_go_integration.py -v --tb=short || PYTHON_TEST_EXIT_CODE=$?
    pytest tests/integration/test_nats_flow_mock.py -v --tb=short || PYTHON_TEST_EXIT_CODE=$?
else
    echo -e "${YELLOW}Warning: Python integration tests directory not found${NC}"
fi

if [ $PYTHON_TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Python integration tests passed${NC}"
else
    echo -e "${RED}✗ Python integration tests failed${NC}"
fi

echo ""

# Final summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}========================================${NC}"

TOTAL_EXIT_CODE=0

if [ $GO_TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Go integration tests: PASSED${NC}"
else
    echo -e "${RED}✗ Go integration tests: FAILED${NC}"
    TOTAL_EXIT_CODE=1
fi

if [ $PYTHON_TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Python integration tests: PASSED${NC}"
else
    echo -e "${RED}✗ Python integration tests: FAILED${NC}"
    TOTAL_EXIT_CODE=1
fi

echo ""

if [ $TOTAL_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}All integration tests passed! 🎉${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Some integration tests failed${NC}"
    echo -e "${RED}========================================${NC}"
fi

exit $TOTAL_EXIT_CODE
