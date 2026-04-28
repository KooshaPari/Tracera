#!/bin/bash
# Orchestrates the full 10k concurrent users load test
# Includes monitoring, test execution, and analysis

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/performance-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${RESULTS_DIR}/test-run-${TIMESTAMP}.log"

# Test configuration
API_URL="${API_URL:-http://localhost:3030}"
PROJECT_ID="${PROJECT_ID:-load-test-project}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
DRY_RUN="${DRY_RUN:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
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

success() {
  echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "${LOG_FILE}"
}

header() {
  echo "" | tee -a "${LOG_FILE}"
  echo -e "${MAGENTA}$1${NC}" | tee -a "${LOG_FILE}"
  echo -e "${MAGENTA}$(echo "$1" | sed 's/./=/g')${NC}" | tee -a "${LOG_FILE}"
  echo "" | tee -a "${LOG_FILE}"
}

# Check dependencies
check_dependencies() {
  header "Checking Dependencies"

  local missing=()

  if ! command -v k6 &> /dev/null; then
    missing+=("k6")
  fi

  if ! command -v node &> /dev/null; then
    missing+=("node")
  fi

  if ! command -v curl &> /dev/null; then
    missing+=("curl")
  fi

  if [ ${#missing[@]} -ne 0 ]; then
    error "Missing required dependencies: ${missing[*]}"
    error "Please install missing tools before running the test"
    error ""
    error "Installation instructions:"
    error "  macOS:   brew install k6 node"
    error "  Linux:   See README.md for k6 installation"
    exit 1
  fi

  success "All dependencies installed"
  log "  k6:   $(k6 version | head -1)"
  log "  node: $(node --version)"
}

# Verify backend is running
verify_backend() {
  header "Verifying Backend Service"

  log "Testing API endpoint: ${API_URL}"

  if ! curl -sf -o /dev/null "${API_URL}/health" 2>/dev/null; then
    error "Backend service is not responding at ${API_URL}"
    error "Please ensure the backend is running before starting the test"
    exit 1
  fi

  success "Backend service is running"

  # Check if project exists
  log "Checking test project..."
  local project_check
  project_check=$(curl -sf -H "Authorization: Bearer ${AUTH_TOKEN}" \
    "${API_URL}/api/v1/projects/${PROJECT_ID}" 2>/dev/null || echo "")

  if [ -z "${project_check}" ]; then
    warn "Test project '${PROJECT_ID}' not found - will be created during test setup"
  else
    success "Test project '${PROJECT_ID}' exists"
  fi
}

# Check system resources
check_resources() {
  header "Checking System Resources"

  # Check available memory
  if [[ "$OSTYPE" == "darwin"* ]]; then
    total_mem=$(sysctl -n hw.memsize | awk '{print $1/1073741824}')
    info "Total Memory: ${total_mem} GB"
  else
    total_mem=$(free -g | grep Mem | awk '{print $2}')
    info "Total Memory: ${total_mem} GB"
  fi

  # Check available disk space
  available_space=$(df -h "${RESULTS_DIR}" | tail -1 | awk '{print $4}')
  info "Available Disk Space: ${available_space}"

  # Check CPU cores
  if [[ "$OSTYPE" == "darwin"* ]]; then
    cpu_cores=$(sysctl -n hw.ncpu)
  else
    cpu_cores=$(nproc)
  fi
  info "CPU Cores: ${cpu_cores}"

  # Warn if resources are low
  if [ "${cpu_cores}" -lt 4 ]; then
    warn "Low CPU cores detected (${cpu_cores}). Recommended: 4+ cores"
  fi

  success "Resource check complete"
}

# Setup test environment
setup_test() {
  header "Setting Up Test Environment"

  # Create results directory
  mkdir -p "${RESULTS_DIR}"
  mkdir -p "${RESULTS_DIR}/monitoring"
  log "Created results directory: ${RESULTS_DIR}"

  # Export environment variables for k6
  export API_URL
  export PROJECT_ID
  export AUTH_TOKEN

  # Create a test summary file
  cat > "${RESULTS_DIR}/test-info-${TIMESTAMP}.txt" << EOF
10K Concurrent Users Load Test
==============================

Start Time: $(date)
API URL: ${API_URL}
Project ID: ${PROJECT_ID}
Timestamp: ${TIMESTAMP}

Test Configuration:
- Target Users: 10,000 concurrent
- Ramp-up: 30 minutes
- Sustained Load: 2 hours
- Total Duration: ~2.5 hours

Target Metrics:
- Throughput: > 1000 req/s
- P95 Latency: < 500ms
- P99 Latency: < 1000ms
- Error Rate: < 1%
EOF

  success "Test environment setup complete"
}

# Start monitoring
start_monitoring() {
  header "Starting System Monitoring"

  if [ ! -x "${SCRIPT_DIR}/monitor.sh" ]; then
    warn "Monitoring script not executable or not found"
    warn "Skipping monitoring - test will continue without it"
    return 0
  fi

  log "Starting monitoring script..."
  "${SCRIPT_DIR}/monitor.sh" > "${RESULTS_DIR}/monitoring.log" 2>&1 &
  MONITOR_PID=$!

  # Wait a moment to ensure monitor started
  sleep 2

  if ps -p ${MONITOR_PID} > /dev/null 2>&1; then
    success "Monitoring started (PID: ${MONITOR_PID})"
    echo "${MONITOR_PID}" > "${RESULTS_DIR}/.monitor.pid"
  else
    warn "Monitoring script failed to start - continuing without monitoring"
    MONITOR_PID=""
  fi
}

# Run the load test
run_load_test() {
  header "Running 10k Concurrent Users Load Test"

  log "Test will run for approximately 2.5 hours"
  log "  - Ramp-up: 30 minutes (0 → 10,000 users)"
  log "  - Sustained: 2 hours (10,000 users)"
  log "  - Spike: 2 minutes at 12,000 users (during sustained phase)"
  log ""
  log "Press Ctrl+C to stop the test early (not recommended)"
  log ""

  if [ "${DRY_RUN}" = "true" ]; then
    warn "DRY RUN MODE - Skipping actual test execution"
    log "Would execute: k6 run --out json=${RESULTS_DIR}/results-${TIMESTAMP}.json ${SCRIPT_DIR}/10k-users.js"
    return 0
  fi

  # Run k6 test with JSON output
  local k6_output="${RESULTS_DIR}/results-${TIMESTAMP}.json"

  log "Starting k6 load test..."
  log "Results will be saved to: ${k6_output}"
  log ""

  if k6 run --out "json=${k6_output}" "${SCRIPT_DIR}/10k-users.js" 2>&1 | tee -a "${LOG_FILE}"; then
    success "Load test completed successfully"
    return 0
  else
    error "Load test failed or was interrupted"
    return 1
  fi
}

# Stop monitoring
stop_monitoring() {
  header "Stopping System Monitoring"

  if [ -f "${RESULTS_DIR}/.monitor.pid" ]; then
    MONITOR_PID=$(cat "${RESULTS_DIR}/.monitor.pid")
    if ps -p ${MONITOR_PID} > /dev/null 2>&1; then
      log "Stopping monitoring (PID: ${MONITOR_PID})..."
      kill ${MONITOR_PID} 2>/dev/null || true
      sleep 2
      success "Monitoring stopped"
    fi
    rm -f "${RESULTS_DIR}/.monitor.pid"
  else
    info "No monitoring process to stop"
  fi
}

# Analyze results
analyze_results() {
  header "Analyzing Test Results"

  if [ "${DRY_RUN}" = "true" ]; then
    warn "DRY RUN MODE - Skipping analysis"
    return 0
  fi

  if [ ! -x "${SCRIPT_DIR}/analyze-results.js" ]; then
    warn "Analysis script not found or not executable"
    warn "Skipping automated analysis"
    return 0
  fi

  log "Running performance analyzer..."
  if node "${SCRIPT_DIR}/analyze-results.js" "${RESULTS_DIR}" 2>&1 | tee -a "${LOG_FILE}"; then
    success "Analysis completed"
  else
    warn "Analysis encountered errors but completed"
  fi
}

# Generate summary
generate_summary() {
  header "Test Summary"

  local end_time=$(date)
  local summary_file="${RESULTS_DIR}/test-summary-${TIMESTAMP}.txt"

  cat > "${summary_file}" << EOF
╔══════════════════════════════════════════════════════════════════════════════╗
║              10K CONCURRENT USERS LOAD TEST - EXECUTION SUMMARY              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Test Information
────────────────────────────────────────────────────────────────────────────────
Start Time:       $(head -1 "${RESULTS_DIR}/test-info-${TIMESTAMP}.txt" | tail -1)
End Time:         ${end_time}
Results Directory: ${RESULTS_DIR}
Log File:         ${LOG_FILE}

Configuration
────────────────────────────────────────────────────────────────────────────────
API URL:          ${API_URL}
Project ID:       ${PROJECT_ID}
Target Users:     10,000 concurrent
Ramp-up Period:   30 minutes
Sustained Load:   2 hours

Test Files
────────────────────────────────────────────────────────────────────────────────
EOF

  # List generated files
  echo "Generated files:" >> "${summary_file}"
  find "${RESULTS_DIR}" -type f -name "*${TIMESTAMP}*" | while read -r file; do
    echo "  - $(basename "${file}")" >> "${summary_file}"
  done

  # Check for bottleneck analysis
  if [ -f "${RESULTS_DIR}/bottleneck-analysis.txt" ]; then
    echo "" >> "${summary_file}"
    echo "Bottleneck Analysis: Available (see bottleneck-analysis.txt)" >> "${summary_file}"
  fi

  echo "" >> "${summary_file}"
  echo "═══════════════════════════════════════════════════════════════════════════════" >> "${summary_file}"
  echo "" >> "${summary_file}"

  # Display summary
  cat "${summary_file}" | tee -a "${LOG_FILE}"

  success "Test execution complete!"
  log ""
  log "Next steps:"
  log "  1. Review results in: ${RESULTS_DIR}"
  log "  2. Check bottleneck analysis: ${RESULTS_DIR}/bottleneck-analysis.txt"
  log "  3. Review monitoring data: ${RESULTS_DIR}/monitoring/"
  log "  4. Implement recommended optimizations"
  log ""
  log "Full log: ${LOG_FILE}"
}

# Cleanup on exit
cleanup() {
  local exit_code=$?

  header "Cleaning Up"

  # Stop monitoring if still running
  stop_monitoring

  # Update summary with exit status
  if [ ${exit_code} -ne 0 ]; then
    error "Test exited with code ${exit_code}"
    echo "" >> "${LOG_FILE}"
    echo "Test failed or was interrupted" >> "${LOG_FILE}"
  fi

  log "Cleanup complete"
  exit ${exit_code}
}

# Display banner
display_banner() {
  cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                 TraceRTM - 10K Concurrent Users Load Test                    ║
║                                                                              ║
║                      Production-Scale Performance Testing                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
  echo ""
}

# Main execution
main() {
  # Setup cleanup trap
  trap cleanup EXIT INT TERM

  # Display banner
  display_banner

  # Create results directory
  mkdir -p "${RESULTS_DIR}"

  # Start logging
  log "Starting 10k concurrent users load test orchestration"
  log "Results will be saved to: ${RESULTS_DIR}"
  log "Log file: ${LOG_FILE}"
  log ""

  # Pre-flight checks
  check_dependencies
  verify_backend
  check_resources
  setup_test

  # Run the test
  start_monitoring
  local test_result=0
  run_load_test || test_result=$?

  # Post-test steps
  stop_monitoring

  if [ ${test_result} -eq 0 ]; then
    analyze_results
    generate_summary
  else
    error "Test failed - skipping analysis"
    exit ${test_result}
  fi
}

# Run main function
main "$@"
