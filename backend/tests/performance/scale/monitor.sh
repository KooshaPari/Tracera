#!/bin/bash
# Production-scale load test monitoring script
# Monitors system resources during 10k concurrent user load test

set -e

# Configuration
RESULTS_DIR="./performance-results/monitoring"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MONITOR_INTERVAL=5  # seconds between samples
LOG_FILE="${RESULTS_DIR}/monitor_${TIMESTAMP}.log"

# Service endpoints
API_URL="${API_URL:-http://localhost:3030}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Create results directory
mkdir -p "${RESULTS_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

error() {
  echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "${LOG_FILE}"
}

warn() {
  echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "${LOG_FILE}"
}

info() {
  echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "${LOG_FILE}"
}

# Check if monitoring tools are available
check_dependencies() {
  local missing=()

  if ! command -v docker &> /dev/null && ! command -v ps &> /dev/null; then
    missing+=("docker or ps")
  fi

  if ! command -v curl &> /dev/null; then
    missing+=("curl")
  fi

  if [ ${#missing[@]} -ne 0 ]; then
    error "Missing required dependencies: ${missing[*]}"
    error "Please install missing tools before running monitoring"
    exit 1
  fi
}

# Initialize monitoring files
init_monitoring() {
  log "Initializing monitoring files..."

  # CPU monitoring
  echo "timestamp,cpu_user,cpu_system,cpu_idle,cpu_iowait" > "${RESULTS_DIR}/cpu_${TIMESTAMP}.csv"

  # Memory monitoring
  echo "timestamp,total_mb,used_mb,free_mb,available_mb,usage_percent" > "${RESULTS_DIR}/memory_${TIMESTAMP}.csv"

  # Backend service monitoring
  echo "timestamp,cpu_percent,memory_mb,memory_percent,threads,connections" > "${RESULTS_DIR}/backend_${TIMESTAMP}.csv"

  # Database monitoring
  echo "timestamp,connections,active_connections,idle_connections,waiting_connections,db_size_mb" > "${RESULTS_DIR}/database_${TIMESTAMP}.csv"

  # Redis monitoring
  echo "timestamp,connected_clients,used_memory_mb,keyspace_hits,keyspace_misses,hit_rate" > "${RESULTS_DIR}/redis_${TIMESTAMP}.csv"

  # Network monitoring
  echo "timestamp,rx_bytes,tx_bytes,rx_packets,tx_packets" > "${RESULTS_DIR}/network_${TIMESTAMP}.csv"

  # Response time monitoring
  echo "timestamp,endpoint,response_time_ms,status_code" > "${RESULTS_DIR}/response_times_${TIMESTAMP}.csv"

  log "Monitoring initialized. Results will be saved to: ${RESULTS_DIR}"
}

# Monitor CPU usage
monitor_cpu() {
  if command -v mpstat &> /dev/null; then
    # Use mpstat for detailed CPU stats
    cpu_stats=$(mpstat 1 1 | tail -1)
    cpu_user=$(echo "${cpu_stats}" | awk '{print $3}')
    cpu_system=$(echo "${cpu_stats}" | awk '{print $5}')
    cpu_idle=$(echo "${cpu_stats}" | awk '{print $12}')
    cpu_iowait=$(echo "${cpu_stats}" | awk '{print $6}')
  else
    # Fallback to top
    cpu_stats=$(top -l 1 | grep "CPU usage" 2>/dev/null || echo "0% user, 0% sys, 100% idle, 0% io")
    cpu_user=$(echo "${cpu_stats}" | grep -oE '[0-9.]+%' | head -1 | tr -d '%')
    cpu_system=$(echo "${cpu_stats}" | grep -oE '[0-9.]+%' | sed -n '2p' | tr -d '%')
    cpu_idle=$(echo "${cpu_stats}" | grep -oE '[0-9.]+%' | sed -n '3p' | tr -d '%')
    cpu_iowait="0"
  fi

  echo "$(date +%s),${cpu_user:-0},${cpu_system:-0},${cpu_idle:-100},${cpu_iowait:-0}" >> "${RESULTS_DIR}/cpu_${TIMESTAMP}.csv"
}

# Monitor memory usage
monitor_memory() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    mem_stats=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);')
    total=$(sysctl -n hw.memsize | awk '{print $1/1048576}')
    used=$(echo "${mem_stats}" | grep "active" | awk '{sum+=$2} END {print sum}')
    free=$(echo "${mem_stats}" | grep "free" | awk '{print $2}')
    available=$((total - used))
    usage_percent=$(echo "scale=2; (${used} / ${total}) * 100" | bc)
  else
    # Linux
    mem_info=$(free -m | grep Mem)
    total=$(echo "${mem_info}" | awk '{print $2}')
    used=$(echo "${mem_info}" | awk '{print $3}')
    free=$(echo "${mem_info}" | awk '{print $4}')
    available=$(echo "${mem_info}" | awk '{print $7}')
    usage_percent=$(echo "scale=2; (${used} / ${total}) * 100" | bc)
  fi

  echo "$(date +%s),${total:-0},${used:-0},${free:-0},${available:-0},${usage_percent:-0}" >> "${RESULTS_DIR}/memory_${TIMESTAMP}.csv"
}

# Monitor backend service (Go backend)
monitor_backend() {
  # Try to find the backend process
  if command -v docker &> /dev/null; then
    # Docker deployment
    container_id=$(docker ps -q -f "name=trace-backend" 2>/dev/null || echo "")
    if [ -n "${container_id}" ]; then
      stats=$(docker stats --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" "${container_id}")
      cpu_percent=$(echo "${stats}" | cut -d',' -f1 | tr -d '%')
      mem_usage=$(echo "${stats}" | cut -d',' -f2 | awk '{print $1}' | sed 's/MiB//')

      # Get connection count from backend metrics endpoint
      connections=$(curl -s "${API_URL}/metrics" | grep "^http_connections" | awk '{print $2}' || echo "0")

      echo "$(date +%s),${cpu_percent:-0},${mem_usage:-0},0,0,${connections:-0}" >> "${RESULTS_DIR}/backend_${TIMESTAMP}.csv"
    fi
  else
    # Local process
    pid=$(pgrep -f "trace-backend" || pgrep -f "go run" || echo "")
    if [ -n "${pid}" ]; then
      if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        cpu_percent=$(ps -p "${pid}" -o %cpu | tail -1)
        mem_mb=$(ps -p "${pid}" -o rss | tail -1 | awk '{print $1/1024}')
      else
        # Linux
        cpu_percent=$(ps -p "${pid}" -o %cpu | tail -1)
        mem_mb=$(ps -p "${pid}" -o rss | tail -1 | awk '{print $1/1024}')
      fi

      threads=$(ps -M "${pid}" 2>/dev/null | wc -l || echo "1")
      connections=$(lsof -p "${pid}" 2>/dev/null | grep -c "ESTABLISHED" || echo "0")

      echo "$(date +%s),${cpu_percent:-0},${mem_mb:-0},0,${threads:-0},${connections:-0}" >> "${RESULTS_DIR}/backend_${TIMESTAMP}.csv"
    fi
  fi
}

# Monitor database (PostgreSQL)
monitor_database() {
  if command -v psql &> /dev/null; then
    # Direct PostgreSQL connection
    db_stats=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER:-postgres}" -d "${DB_NAME:-trace}" -t -c "
      SELECT
        (SELECT count(*) FROM pg_stat_activity) as total_connections,
        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active,
        (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle,
        (SELECT count(*) FROM pg_stat_activity WHERE wait_event_type IS NOT NULL) as waiting,
        (SELECT pg_database_size('${DB_NAME:-trace}')/(1024*1024)) as db_size_mb;
    " 2>/dev/null || echo "0|0|0|0|0")

    IFS='|' read -r total_conn active_conn idle_conn waiting_conn db_size <<< "${db_stats}"

    echo "$(date +%s),${total_conn:-0},${active_conn:-0},${idle_conn:-0},${waiting_conn:-0},${db_size:-0}" >> "${RESULTS_DIR}/database_${TIMESTAMP}.csv"
  else
    # Fallback: estimate from metrics endpoint
    echo "$(date +%s),0,0,0,0,0" >> "${RESULTS_DIR}/database_${TIMESTAMP}.csv"
  fi
}

# Monitor Redis
monitor_redis() {
  if command -v redis-cli &> /dev/null; then
    redis_info=$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" INFO 2>/dev/null || echo "")

    clients=$(echo "${redis_info}" | grep "^connected_clients:" | cut -d':' -f2 | tr -d '\r')
    memory=$(echo "${redis_info}" | grep "^used_memory:" | cut -d':' -f2 | tr -d '\r' | awk '{print $1/1048576}')
    hits=$(echo "${redis_info}" | grep "^keyspace_hits:" | cut -d':' -f2 | tr -d '\r')
    misses=$(echo "${redis_info}" | grep "^keyspace_misses:" | cut -d':' -f2 | tr -d '\r')

    hit_rate=0
    if [ "${hits:-0}" -gt 0 ] || [ "${misses:-0}" -gt 0 ]; then
      hit_rate=$(echo "scale=4; ${hits:-0} / (${hits:-0} + ${misses:-0})" | bc)
    fi

    echo "$(date +%s),${clients:-0},${memory:-0},${hits:-0},${misses:-0},${hit_rate}" >> "${RESULTS_DIR}/redis_${TIMESTAMP}.csv"
  else
    echo "$(date +%s),0,0,0,0,0" >> "${RESULTS_DIR}/redis_${TIMESTAMP}.csv"
  fi
}

# Monitor network traffic
monitor_network() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    net_stats=$(netstat -ibn | grep -E "en0" | head -1 || echo "")
    rx_bytes=$(echo "${net_stats}" | awk '{print $7}')
    tx_bytes=$(echo "${net_stats}" | awk '{print $10}')
    rx_packets=$(echo "${net_stats}" | awk '{print $5}')
    tx_packets=$(echo "${net_stats}" | awk '{print $8}')
  else
    # Linux
    net_stats=$(cat /proc/net/dev | grep "eth0" | head -1 || echo "")
    rx_bytes=$(echo "${net_stats}" | awk '{print $2}')
    tx_bytes=$(echo "${net_stats}" | awk '{print $10}')
    rx_packets=$(echo "${net_stats}" | awk '{print $3}')
    tx_packets=$(echo "${net_stats}" | awk '{print $11}')
  fi

  echo "$(date +%s),${rx_bytes:-0},${tx_bytes:-0},${rx_packets:-0},${tx_packets:-0}" >> "${RESULTS_DIR}/network_${TIMESTAMP}.csv"
}

# Monitor API response times
monitor_response_times() {
  local endpoints=(
    "/api/v1/projects/${PROJECT_ID}/items"
    "/api/v1/search"
    "/api/v1/graph/viewport/${PROJECT_ID}"
  )

  for endpoint in "${endpoints[@]}"; do
    start_time=$(date +%s%3N)
    status_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${API_URL}${endpoint}" 2>/dev/null || echo "000")
    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))

    echo "$(date +%s),${endpoint},${response_time},${status_code}" >> "${RESULTS_DIR}/response_times_${TIMESTAMP}.csv"
  done
}

# Display real-time dashboard
display_dashboard() {
  clear
  cat << EOF
╔══════════════════════════════════════════════════════════════════════════════╗
║                     10K LOAD TEST - LIVE MONITORING                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Monitoring started: $(date)
Results directory: ${RESULTS_DIR}

Press Ctrl+C to stop monitoring...

EOF
}

# Main monitoring loop
monitor_loop() {
  local iteration=0

  while true; do
    iteration=$((iteration + 1))

    # Collect all metrics
    monitor_cpu &
    monitor_memory &
    monitor_backend &
    monitor_database &
    monitor_redis &
    monitor_network &
    monitor_response_times &

    # Wait for all background jobs
    wait

    # Display progress every 10 iterations (50 seconds)
    if [ $((iteration % 10)) -eq 0 ]; then
      info "Monitoring iteration ${iteration} - Data collected successfully"
    fi

    # Sleep until next interval
    sleep "${MONITOR_INTERVAL}"
  done
}

# Cleanup on exit
cleanup() {
  log "Stopping monitoring..."
  log "Results saved to: ${RESULTS_DIR}"
  log "Log file: ${LOG_FILE}"
  exit 0
}

# Main execution
main() {
  trap cleanup INT TERM

  log "Starting production-scale load test monitoring"
  log "Configuration:"
  log "  - API URL: ${API_URL}"
  log "  - Database: ${DB_HOST}:${DB_PORT}"
  log "  - Redis: ${REDIS_HOST}:${REDIS_PORT}"
  log "  - Monitor interval: ${MONITOR_INTERVAL}s"
  log ""

  check_dependencies
  init_monitoring
  display_dashboard
  monitor_loop
}

# Run main
main "$@"
