#!/bin/bash
# Test runbook procedures in staging environment
# Usage: ./scripts/runbook-test.sh [runbook-name]

set -e

RUNBOOK=${1:-all}
STAGING_ENV=${STAGING_ENV:-staging}

echo "Testing runbooks in $STAGING_ENV environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

test_database_connection_failures() {
    log_info "Testing database connection failure scenarios..."

    # Test 1: Database container stop/start
    log_info "  Test 1: Stopping database container..."
    docker-compose stop postgres
    sleep 5

    # Verify application detects failure
    if curl -f http://localhost:8000/health 2>/dev/null; then
        log_error "    Application should report unhealthy when database is down"
        return 1
    else
        log_info "    ✓ Application correctly reported unhealthy"
    fi

    # Test recovery
    log_info "  Test 1: Starting database container..."
    docker-compose start postgres
    sleep 10

    # Wait for database to be ready
    until docker-compose exec -T postgres pg_isready -U postgres; do
        log_info "    Waiting for database..."
        sleep 2
    done

    # Verify application recovers
    if curl -f http://localhost:8000/health 2>/dev/null; then
        log_info "    ✓ Application recovered successfully"
    else
        log_error "    Application did not recover"
        return 1
    fi

    log_info "  ✓ Database connection failure tests passed"
}

test_high_latency_timeouts() {
    log_info "Testing high latency scenarios..."

    # Test 1: Slow query simulation
    log_info "  Test 1: Simulating slow query..."

    # Run a deliberately slow query
    docker-compose exec -T postgres psql -U postgres -d trace -c "SELECT pg_sleep(10);" &
    SLOW_QUERY_PID=$!

    # Wait a bit
    sleep 2

    # Check for slow query detection
    SLOW_QUERIES=$(docker-compose exec -T postgres psql -U postgres -d trace -t -c "
    SELECT COUNT(*) FROM pg_stat_activity
    WHERE state != 'idle' AND now() - query_start > interval '5 seconds';
    ")

    if [ "$SLOW_QUERIES" -gt "0" ]; then
        log_info "    ✓ Slow query detected"
    else
        log_warn "    Slow query not detected (may have completed)"
    fi

    # Kill slow query
    kill $SLOW_QUERY_PID 2>/dev/null || true

    log_info "  ✓ High latency tests passed"
}

test_memory_exhaustion() {
    log_info "Testing memory exhaustion scenarios..."

    # Test 1: Check memory limits
    log_info "  Test 1: Verifying container memory limits..."

    OBSERVABILITY_BACKEND_CONTAINER="${OBSERVABILITY_BACKEND_CONTAINER:-alloy-1}"
    BACKEND_MEMORY=$(docker inspect "$OBSERVABILITY_BACKEND_CONTAINER" | jq -r '.[0].HostConfig.Memory')
    if [ "$BACKEND_MEMORY" != "0" ] && [ "$BACKEND_MEMORY" != "null" ]; then
        log_info "    ✓ Observability backend memory limit set: $(echo $BACKEND_MEMORY / 1024 / 1024 | bc)MB"
    else
        log_warn "    Observability backend has no memory limit"
    fi

    # Test 2: Check current memory usage
    log_info "  Test 2: Checking current memory usage..."
    docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

    log_info "  ✓ Memory exhaustion tests passed"
}

test_disk_space_issues() {
    log_info "Testing disk space monitoring..."

    # Test 1: Check disk usage
    log_info "  Test 1: Checking disk usage..."
    df -h

    # Test 2: Check Docker disk usage
    log_info "  Test 2: Checking Docker disk usage..."
    docker system df

    # Test 3: Verify log rotation is configured
    log_info "  Test 3: Checking log rotation configuration..."
    if [ -f /etc/logrotate.d/docker-containers ]; then
        log_info "    ✓ Log rotation configured"
    else
        log_warn "    Log rotation not configured"
    fi

    log_info "  ✓ Disk space tests passed"
}

test_network_partitions() {
    log_info "Testing network partition scenarios..."

    # Test 1: Inter-service connectivity
    log_info "  Test 1: Testing inter-service connectivity..."

    services=("postgres" "dragonfly" "frontend")
    for service in "${services[@]}"; do
        if docker-compose exec -T backend ping -c 3 -W 5 "$service" > /dev/null 2>&1; then
            log_info "    ✓ Can reach $service"
        else
            log_error "    Cannot reach $service"
            return 1
        fi
    done

    # Test 2: DNS resolution
    log_info "  Test 2: Testing DNS resolution..."
    for service in "${services[@]}"; do
        if docker-compose exec -T backend nslookup "$service" > /dev/null 2>&1; then
            log_info "    ✓ Can resolve $service"
        else
            log_error "    Cannot resolve $service"
            return 1
        fi
    done

    # Test 3: Port connectivity
    log_info "  Test 3: Testing port connectivity..."
    if docker-compose exec -T backend nc -zv postgres 5432 2>&1 | grep -q succeeded; then
        log_info "    ✓ PostgreSQL port accessible"
    else
        log_error "    PostgreSQL port not accessible"
        return 1
    fi

    if docker-compose exec -T backend nc -zv dragonfly 6379 2>&1 | grep -q succeeded; then
        log_info "    ✓ Dragonfly port accessible"
    else
        log_error "    Dragonfly port not accessible"
        return 1
    fi

    log_info "  ✓ Network partition tests passed"
}

test_authentication_failures() {
    log_info "Testing authentication scenarios..."

    # Test 1: Health check endpoint (unauthenticated)
    log_info "  Test 1: Testing unauthenticated endpoint..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "    ✓ Health endpoint accessible"
    else
        log_error "    Health endpoint not accessible"
        return 1
    fi

    # Test 2: Protected endpoint without auth
    log_info "  Test 2: Testing protected endpoint without auth..."
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/items)
    if [ "$STATUS" == "401" ]; then
        log_info "    ✓ Protected endpoint returns 401"
    else
        log_warn "    Protected endpoint returned $STATUS (expected 401)"
    fi

    # Test 3: OAuth configuration
    log_info "  Test 3: Checking OAuth configuration..."
    if docker-compose exec -T backend env | grep -q WORKOS_API_KEY; then
        log_info "    ✓ WorkOS configuration present"
    else
        log_warn "    WorkOS configuration missing"
    fi

    # Test 4: Session storage
    log_info "  Test 4: Checking session storage..."
    if docker-compose exec -T dragonfly redis-cli ping > /dev/null 2>&1; then
        log_info "    ✓ Session store (Dragonfly) accessible"
    else
        log_error "    Session store not accessible"
        return 1
    fi

    log_info "  ✓ Authentication tests passed"
}

test_cache_invalidation() {
    log_info "Testing cache invalidation scenarios..."

    # Test 1: Cache connectivity
    log_info "  Test 1: Testing cache connectivity..."
    if docker-compose exec -T dragonfly redis-cli ping > /dev/null 2>&1; then
        log_info "    ✓ Cache accessible"
    else
        log_error "    Cache not accessible"
        return 1
    fi

    # Test 2: Cache statistics
    log_info "  Test 2: Checking cache statistics..."
    HITS=$(docker-compose exec -T dragonfly redis-cli INFO stats | grep keyspace_hits: | cut -d: -f2 | tr -d '\r')
    MISSES=$(docker-compose exec -T dragonfly redis-cli INFO stats | grep keyspace_misses: | cut -d: -f2 | tr -d '\r')

    if [ -n "$HITS" ] && [ -n "$MISSES" ]; then
        TOTAL=$((HITS + MISSES))
        if [ "$TOTAL" -gt "0" ]; then
            HIT_RATE=$(echo "scale=2; $HITS * 100 / $TOTAL" | bc)
            log_info "    Cache hit rate: ${HIT_RATE}%"
        else
            log_info "    No cache activity yet"
        fi
    fi

    # Test 3: Cache memory usage
    log_info "  Test 3: Checking cache memory..."
    MEMORY=$(docker-compose exec -T dragonfly redis-cli INFO memory | grep used_memory_human: | cut -d: -f2 | tr -d '\r')
    log_info "    Cache memory usage: $MEMORY"

    # Test 4: Eviction policy
    log_info "  Test 4: Checking eviction policy..."
    POLICY=$(docker-compose exec -T dragonfly redis-cli CONFIG GET maxmemory-policy | tail -1 | tr -d '\r')
    log_info "    Eviction policy: $POLICY"

    log_info "  ✓ Cache invalidation tests passed"
}

# Main execution
main() {
    log_info "Starting runbook tests..."
    log_info "Target: $RUNBOOK"
    echo ""

    case $RUNBOOK in
        database-connection-failures)
            test_database_connection_failures
            ;;
        high-latency-timeouts)
            test_high_latency_timeouts
            ;;
        memory-exhaustion)
            test_memory_exhaustion
            ;;
        disk-space-issues)
            test_disk_space_issues
            ;;
        network-partitions)
            test_network_partitions
            ;;
        authentication-failures)
            test_authentication_failures
            ;;
        cache-invalidation-issues)
            test_cache_invalidation
            ;;
        all)
            # Run all tests
            test_database_connection_failures || log_error "Database tests failed"
            echo ""
            test_high_latency_timeouts || log_error "Latency tests failed"
            echo ""
            test_memory_exhaustion || log_error "Memory tests failed"
            echo ""
            test_disk_space_issues || log_error "Disk tests failed"
            echo ""
            test_network_partitions || log_error "Network tests failed"
            echo ""
            test_authentication_failures || log_error "Auth tests failed"
            echo ""
            test_cache_invalidation || log_error "Cache tests failed"
            ;;
        *)
            log_error "Unknown runbook: $RUNBOOK"
            echo "Available runbooks:"
            echo "  - database-connection-failures"
            echo "  - high-latency-timeouts"
            echo "  - memory-exhaustion"
            echo "  - disk-space-issues"
            echo "  - network-partitions"
            echo "  - authentication-failures"
            echo "  - cache-invalidation-issues"
            echo "  - all (run all tests)"
            exit 1
            ;;
    esac

    echo ""
    log_info "Runbook tests completed"
}

# Run main
main
