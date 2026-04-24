#!/bin/bash
# Quick access to runbook commands
# Usage: ./scripts/runbook-quick-access.sh [scenario]

set -e

SCENARIO=${1:-menu}

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_menu() {
    echo -e "${BLUE}=== Incident Response Runbook Quick Access ===${NC}"
    echo ""
    echo "Select an incident scenario:"
    echo ""
    echo "  1) Database Connection Failures"
    echo "  2) High Latency / Timeouts"
    echo "  3) Memory Exhaustion"
    echo "  4) Disk Space Issues"
    echo "  5) Network Partitions"
    echo "  6) Authentication Failures"
    echo "  7) Cache Invalidation Issues"
    echo "  8) View All Runbooks"
    echo "  9) Run Runbook Tests"
    echo "  0) Exit"
    echo ""
    read -p "Enter choice [0-9]: " choice

    case $choice in
        1) database_quick_check ;;
        2) latency_quick_check ;;
        3) memory_quick_check ;;
        4) disk_quick_check ;;
        5) network_quick_check ;;
        6) auth_quick_check ;;
        7) cache_quick_check ;;
        8) view_all_runbooks ;;
        9) run_tests ;;
        0) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ; show_menu ;;
    esac
}

database_quick_check() {
    echo -e "${YELLOW}=== Database Connection Quick Check ===${NC}"
    echo ""

    echo "1. Database container status:"
    docker-compose ps postgres

    echo ""
    echo "2. Database connectivity test:"
    if docker-compose exec -T postgres pg_isready -U postgres; then
        echo -e "${GREEN}✓ Database is ready${NC}"
    else
        echo -e "${RED}✗ Database is not ready${NC}"
    fi

    echo ""
    echo "3. Active connections:"
    docker-compose exec -T postgres psql -U postgres -d trace -c "
    SELECT count(*) as active_connections,
           (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
    FROM pg_stat_activity;
    "

    echo ""
    echo "4. Application health check:"
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo -e "${GREEN}✓ Application healthy${NC}"
    else
        echo -e "${RED}✗ Application unhealthy${NC}"
    fi

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/database-connection-failures.md${NC}"
    press_to_continue
}

latency_quick_check() {
    echo -e "${YELLOW}=== High Latency Quick Check ===${NC}"
    echo ""

    echo "1. Current slow queries:"
    docker-compose exec -T postgres psql -U postgres -d trace -c "
    SELECT pid, now() - query_start AS duration, state, LEFT(query, 60) as query
    FROM pg_stat_activity
    WHERE state != 'idle'
      AND query NOT LIKE '%pg_stat_activity%'
    ORDER BY duration DESC
    LIMIT 5;
    "

    echo ""
    echo "2. API response time test:"
    time curl -o /dev/null -s http://localhost:8000/api/v1/items

    echo ""
    echo "3. Container resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}"

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/high-latency-timeouts.md${NC}"
    press_to_continue
}

memory_quick_check() {
    echo -e "${YELLOW}=== Memory Exhaustion Quick Check ===${NC}"
    echo ""

    echo "1. Container memory usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

    echo ""
    echo "2. Check for OOM kills:"
    for container in $(docker-compose ps -q); do
        name=$(docker inspect -f '{{.Name}}' $container | sed 's/\///')
        oom=$(docker inspect -f '{{.State.OOMKilled}}' $container)
        echo "$name: OOMKilled=$oom"
    done

    echo ""
    echo "3. System memory:"
    free -h

    echo ""
    echo "4. Memory logs (last 20 lines):"
    docker-compose logs --tail=20 backend | grep -i "memory\|oom" || echo "No memory-related errors"

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/memory-exhaustion.md${NC}"
    press_to_continue
}

disk_quick_check() {
    echo -e "${YELLOW}=== Disk Space Quick Check ===${NC}"
    echo ""

    echo "1. Filesystem usage:"
    df -h

    echo ""
    echo "2. Docker disk usage:"
    docker system df

    echo ""
    echo "3. Largest directories in current path:"
    du -h --max-depth=1 . 2>/dev/null | sort -hr | head -10

    echo ""
    echo "4. Docker log sizes:"
    find /var/lib/docker/containers -name "*-json.log" -exec du -h {} \; 2>/dev/null | sort -hr | head -5 || echo "Cannot access Docker logs (need sudo)"

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/disk-space-issues.md${NC}"
    press_to_continue
}

network_quick_check() {
    echo -e "${YELLOW}=== Network Partition Quick Check ===${NC}"
    echo ""

    echo "1. Inter-service connectivity:"
    services=("postgres" "dragonfly" "frontend")
    for service in "${services[@]}"; do
        if docker-compose exec -T backend ping -c 1 -W 2 "$service" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Can reach $service"
        else
            echo -e "${RED}✗${NC} Cannot reach $service"
        fi
    done

    echo ""
    echo "2. DNS resolution:"
    for service in "${services[@]}"; do
        if docker-compose exec -T backend nslookup "$service" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Can resolve $service"
        else
            echo -e "${RED}✗${NC} Cannot resolve $service"
        fi
    done

    echo ""
    echo "3. Port connectivity:"
    if docker-compose exec -T backend nc -zv postgres 5432 2>&1 | grep -q succeeded; then
        echo -e "${GREEN}✓${NC} PostgreSQL port accessible"
    else
        echo -e "${RED}✗${NC} PostgreSQL port not accessible"
    fi

    if docker-compose exec -T backend nc -zv dragonfly 6379 2>&1 | grep -q succeeded; then
        echo -e "${GREEN}✓${NC} Dragonfly port accessible"
    else
        echo -e "${RED}✗${NC} Dragonfly port not accessible"
    fi

    echo ""
    echo "4. Docker network:"
    docker network inspect trace_default | jq '.[0].Containers | length' | xargs echo "Containers in network:"

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/network-partitions.md${NC}"
    press_to_continue
}

auth_quick_check() {
    echo -e "${YELLOW}=== Authentication Quick Check ===${NC}"
    echo ""

    echo "1. Health endpoint (unauthenticated):"
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo -e "${GREEN}✓ Health endpoint accessible${NC}"
    else
        echo -e "${RED}✗ Health endpoint not accessible${NC}"
    fi

    echo ""
    echo "2. Protected endpoint without auth:"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/items)
    if [ "$STATUS" == "401" ]; then
        echo -e "${GREEN}✓ Returns 401 (correct)${NC}"
    else
        echo -e "${YELLOW}! Returns $STATUS (expected 401)${NC}"
    fi

    echo ""
    echo "3. Session store (Dragonfly):"
    if docker-compose exec -T dragonfly redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Session store accessible${NC}"
        SESSION_COUNT=$(docker-compose exec -T dragonfly redis-cli KEYS "session:*" | wc -l)
        echo "  Active sessions: $SESSION_COUNT"
    else
        echo -e "${RED}✗ Session store not accessible${NC}"
    fi

    echo ""
    echo "4. OAuth configuration:"
    if docker-compose exec -T backend env | grep -q WORKOS_API_KEY; then
        echo -e "${GREEN}✓ WorkOS configuration present${NC}"
    else
        echo -e "${YELLOW}! WorkOS configuration missing${NC}"
    fi

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/authentication-failures.md${NC}"
    press_to_continue
}

cache_quick_check() {
    echo -e "${YELLOW}=== Cache Invalidation Quick Check ===${NC}"
    echo ""

    echo "1. Cache connectivity:"
    if docker-compose exec -T dragonfly redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Cache accessible${NC}"
    else
        echo -e "${RED}✗ Cache not accessible${NC}"
        press_to_continue
        return
    fi

    echo ""
    echo "2. Cache statistics:"
    docker-compose exec -T dragonfly redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses"

    HITS=$(docker-compose exec -T dragonfly redis-cli INFO stats | grep keyspace_hits: | cut -d: -f2 | tr -d '\r')
    MISSES=$(docker-compose exec -T dragonfly redis-cli INFO stats | grep keyspace_misses: | cut -d: -f2 | tr -d '\r')

    if [ -n "$HITS" ] && [ -n "$MISSES" ]; then
        TOTAL=$((HITS + MISSES))
        if [ "$TOTAL" -gt "0" ]; then
            HIT_RATE=$(echo "scale=2; $HITS * 100 / $TOTAL" | bc)
            echo -e "Hit rate: ${GREEN}${HIT_RATE}%${NC}"
        fi
    fi

    echo ""
    echo "3. Memory usage:"
    docker-compose exec -T dragonfly redis-cli INFO memory | grep -E "used_memory_human|maxmemory"

    echo ""
    echo "4. Key count:"
    docker-compose exec -T dragonfly redis-cli DBSIZE

    echo ""
    echo "5. Eviction policy:"
    docker-compose exec -T dragonfly redis-cli CONFIG GET maxmemory-policy

    echo ""
    echo -e "${BLUE}Full runbook: docs/runbooks/cache-invalidation-issues.md${NC}"
    press_to_continue
}

view_all_runbooks() {
    echo -e "${YELLOW}=== Available Runbooks ===${NC}"
    echo ""

    runbooks=(
        "database-connection-failures.md|Database Connection Failures|Critical|< 5 min"
        "high-latency-timeouts.md|High Latency / Timeouts|High|< 10 min"
        "memory-exhaustion.md|Memory Exhaustion|Critical|< 5 min"
        "disk-space-issues.md|Disk Space Issues|High|< 15 min"
        "network-partitions.md|Network Partitions|Critical|< 5 min"
        "authentication-failures.md|Authentication Failures|High|< 10 min"
        "cache-invalidation-issues.md|Cache Invalidation Issues|Medium|< 20 min"
    )

    printf "%-40s %-10s %-15s\n" "Runbook" "Severity" "Response Time"
    echo "--------------------------------------------------------------------------------"

    for runbook in "${runbooks[@]}"; do
        IFS='|' read -r file name severity time <<< "$runbook"
        printf "%-40s %-10s %-15s\n" "$name" "$severity" "$time"
    done

    echo ""
    echo "Location: docs/runbooks/"
    echo ""

    press_to_continue
}

run_tests() {
    echo -e "${YELLOW}=== Running Runbook Tests ===${NC}"
    echo ""

    if [ -f scripts/runbook-test.sh ]; then
        read -p "Run all tests? (y/n): " run_all

        if [ "$run_all" == "y" ]; then
            bash scripts/runbook-test.sh all
        else
            echo ""
            echo "Available tests:"
            echo "  1) database-connection-failures"
            echo "  2) high-latency-timeouts"
            echo "  3) memory-exhaustion"
            echo "  4) disk-space-issues"
            echo "  5) network-partitions"
            echo "  6) authentication-failures"
            echo "  7) cache-invalidation-issues"
            echo ""
            read -p "Enter choice [1-7]: " test_choice

            case $test_choice in
                1) bash scripts/runbook-test.sh database-connection-failures ;;
                2) bash scripts/runbook-test.sh high-latency-timeouts ;;
                3) bash scripts/runbook-test.sh memory-exhaustion ;;
                4) bash scripts/runbook-test.sh disk-space-issues ;;
                5) bash scripts/runbook-test.sh network-partitions ;;
                6) bash scripts/runbook-test.sh authentication-failures ;;
                7) bash scripts/runbook-test.sh cache-invalidation-issues ;;
                *) echo -e "${RED}Invalid choice${NC}" ;;
            esac
        fi
    else
        echo -e "${RED}Test script not found: scripts/runbook-test.sh${NC}"
    fi

    echo ""
    press_to_continue
}

press_to_continue() {
    echo ""
    read -p "Press Enter to return to menu..." _
    show_menu
}

# Main execution
case $SCENARIO in
    menu)
        show_menu
        ;;
    database|db)
        database_quick_check
        ;;
    latency|timeout)
        latency_quick_check
        ;;
    memory|mem)
        memory_quick_check
        ;;
    disk)
        disk_quick_check
        ;;
    network|net)
        network_quick_check
        ;;
    auth|authentication)
        auth_quick_check
        ;;
    cache)
        cache_quick_check
        ;;
    list)
        view_all_runbooks
        exit 0
        ;;
    test)
        run_tests
        exit 0
        ;;
    *)
        echo -e "${RED}Unknown scenario: $SCENARIO${NC}"
        echo ""
        echo "Usage: $0 [scenario]"
        echo ""
        echo "Available scenarios:"
        echo "  menu         - Interactive menu (default)"
        echo "  database     - Database connection quick check"
        echo "  latency      - High latency quick check"
        echo "  memory       - Memory exhaustion quick check"
        echo "  disk         - Disk space quick check"
        echo "  network      - Network partition quick check"
        echo "  auth         - Authentication quick check"
        echo "  cache        - Cache invalidation quick check"
        echo "  list         - List all runbooks"
        echo "  test         - Run runbook tests"
        exit 1
        ;;
esac
