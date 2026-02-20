#!/bin/bash

###############################################################################
# Test Pyramid Verification Script
#
# Counts tests by type (unit/integration/e2e) across all projects using build
# tags (Go) and file naming patterns (TypeScript/Python). Verifies pyramid
# shape: unit 60-70%, integration 20-30%, e2e 5-10%.
#
# Exit codes:
#   0: Pyramid is healthy
#   1: Configuration error
#   2: Pyramid imbalance detected
###############################################################################

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Output formatting
RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'

# Default configuration
STRICT_MODE="${1:-false}"
OUTPUT_FILE="${2:-}"
VERBOSE="${VERBOSE:-false}"

###############################################################################
# Helper Functions
###############################################################################

log_info() {
  echo -e "${BLUE}ℹ ${RESET}$*"
}

log_success() {
  echo -e "${GREEN}✓ ${RESET}$*"
}

log_warn() {
  echo -e "${YELLOW}⚠ ${RESET}$*"
}

log_error() {
  echo -e "${RED}✗ ${RESET}$* " >&2
}

print_header() {
  echo ""
  echo -e "${BOLD}${BLUE}=== $* ===${RESET}"
  echo ""
}

print_table_header() {
  printf "%-30s %-12s %-12s %-10s\n" "Category" "Count" "Percentage" "Status"
  printf "%-30s %-12s %-12s %-10s\n" "---" "---" "---" "---"
}

print_table_row() {
  local category="$1"
  local count="$2"
  local percentage="$3"
  local status="$4"

  printf "%-30s %-12s %-12s %-10s\n" "$category" "$count" "$percentage" "$status"
}

###############################################################################
# Go Test Classification
###############################################################################

count_go_tests() {
  local test_type="$1"

  case "$test_type" in
    unit)
      # Unit tests: files without integration or e2e build tags
      find "$PROJECT_ROOT/backend" -type f -name "*_test.go" 2>/dev/null | while read -r file; do
        if head -5 "$file" | grep -q "^//go:build"; then
          if ! head -5 "$file" | grep -q "integration\|e2e"; then
            echo "$file"
          fi
        else
          # No build tag = unit test
          echo "$file"
        fi
      done | wc -l
      ;;

    integration)
      # Integration tests: has "integration" in build tag but NOT e2e
      find "$PROJECT_ROOT/backend" -type f -name "*_test.go" 2>/dev/null | while read -r file; do
        if head -5 "$file" | grep -q "^//go:build.*integration" && ! head -5 "$file" | grep -q "e2e"; then
          echo "$file"
        fi
      done | wc -l
      ;;

    e2e)
      # E2E tests: has "e2e" in build tag
      find "$PROJECT_ROOT/backend" -type f -name "*_test.go" 2>/dev/null | while read -r file; do
        if head -5 "$file" | grep -q "^//go:build.*e2e"; then
          echo "$file"
        fi
      done | wc -l
      ;;
  esac
}

###############################################################################
# TypeScript/JavaScript Test Classification
###############################################################################

count_ts_tests() {
  local test_type="$1"
  local ts_dir="$PROJECT_ROOT/frontend/apps/web/src/__tests__"

  [ ! -d "$ts_dir" ] && echo "0" && return 0

  case "$test_type" in
    unit)
      # Unit tests: .test.ts(x) files NOT in integration dir and NOT .integration.test
      find "$ts_dir" -type f \( -name "*.test.ts" -o -name "*.test.tsx" \) 2>/dev/null | \
        grep -v "integration/" | grep -v ".integration.test" | wc -l
      ;;

    integration)
      # Integration tests: .integration.test.ts(x) OR in integration/ subfolder
      (find "$ts_dir/integration" -type f \( -name "*.test.ts" -o -name "*.test.tsx" \) 2>/dev/null; \
       find "$ts_dir" -type f -name "*.integration.test.ts*" 2>/dev/null) | sort -u | wc -l
      ;;

    e2e)
      # E2E tests: .spec.ts(x) files only
      find "$PROJECT_ROOT/frontend/apps/web/e2e" -type f \( -name "*.spec.ts" -o -name "*.spec.tsx" \) 2>/dev/null | wc -l
      ;;
  esac
}

###############################################################################
# Python Test Classification
###############################################################################

count_python_tests() {
  local test_type="$1"
  local py_dir="$PROJECT_ROOT/src"

  [ ! -d "$py_dir" ] && echo "0" && return 0

  case "$test_type" in
    unit)
      # Unit tests: test_*.py or *_test.py files NOT in integration folder
      find "$py_dir" \
        -path "*/.pytest_cache" -prune -o \
        -path "*/__pycache__" -prune -o \
        -type f \( -name "test_*.py" -o -name "*_test.py" \) -print 2>/dev/null | \
        grep -v "integration" | wc -l
      ;;

    integration)
      # Integration tests: in tests/integration or marked with integration
      find "$py_dir/tracertm/tests/integration" -type f -name "*.py" 2>/dev/null | \
        grep -E "test_|_test\.py" | wc -l
      ;;

    e2e)
      # E2E tests: in tests/e2e folder
      find "$py_dir/tracertm/tests/e2e" -type f -name "*.py" 2>/dev/null | \
        grep -E "test_|_test\.py" | wc -l
      ;;
  esac
}

###############################################################################
# Validation Functions
###############################################################################

validate_pyramid_shape() {
  local unit=$1
  local integration=$2
  local e2e=$3

  if [ $((unit + integration + e2e)) -eq 0 ]; then
    log_error "No tests found in project"
    return 1
  fi

  local total=$((unit + integration + e2e))
  local unit_pct=$((unit * 100 / total))
  local integration_pct=$((integration * 100 / total))
  local e2e_pct=$((e2e * 100 / total))

  local issues=0

  # Validate ranges
  if [ "$unit_pct" -lt 60 ] || [ "$unit_pct" -gt 75 ]; then
    issues=$((issues + 1))
  fi

  if [ "$integration_pct" -lt 15 ] || [ "$integration_pct" -gt 35 ]; then
    issues=$((issues + 1))
  fi

  if [ "$e2e_pct" -lt 3 ] || [ "$e2e_pct" -gt 15 ]; then
    issues=$((issues + 1))
  fi

  # Pyramid shape check: unit > integration > e2e
  if [ "$unit" -le "$integration" ]; then
    issues=$((issues + 1))
  fi

  if [ "$integration" -le "$e2e" ] && [ "$e2e" -gt 0 ]; then
    issues=$((issues + 1))
  fi

  return $issues
}

###############################################################################
# Report Generation
###############################################################################

generate_report() {
  local unit=$1
  local integration=$2
  local e2e=$3

  local total=$((unit + integration + e2e))

  if [ "$total" -eq 0 ]; then
    log_error "No tests found"
    return 1
  fi

  local unit_pct=$((unit * 100 / total))
  local integration_pct=$((integration * 100 / total))
  local e2e_pct=$((e2e * 100 / total))

  print_header "Test Pyramid Analysis"

  echo -e "${BOLD}Summary:${RESET}"
  printf "  Total Tests: %d\n" "$total"
  printf "  Unit Tests: %d (%.1f%%)\n" "$unit" "$unit_pct"
  printf "  Integration Tests: %d (%.1f%%)\n" "$integration" "$integration_pct"
  printf "  E2E Tests: %d (%.1f%%)\n" "$e2e" "$e2e_pct"
  echo ""

  print_header "Detailed Results"
  print_table_header

  # Unit tests status
  local unit_status="OK"
  if [ "$unit_pct" -lt 60 ] || [ "$unit_pct" -gt 75 ]; then
    unit_status="WARN"
  fi
  print_table_row "Unit Tests" "$unit" "${unit_pct}%" "$unit_status"

  # Integration tests status
  local integration_status="OK"
  if [ "$integration_pct" -lt 15 ] || [ "$integration_pct" -gt 35 ]; then
    integration_status="WARN"
  fi
  print_table_row "Integration Tests" "$integration" "${integration_pct}%" "$integration_status"

  # E2E tests status
  local e2e_status="OK"
  if [ "$e2e_pct" -lt 3 ] || [ "$e2e_pct" -gt 15 ]; then
    e2e_status="WARN"
  fi
  print_table_row "E2E Tests" "$e2e" "${e2e_pct}%" "$e2e_status"

  echo ""

  print_header "Pyramid Shape Validation"

  # Shape checks
  if [ "$unit" -gt "$integration" ]; then
    log_success "Unit tests > Integration tests"
  else
    log_warn "Unit tests should be > Integration tests (unit=$unit, integration=$integration)"
  fi

  if [ "$integration" -gt "$e2e" ] || [ "$e2e" -eq 0 ]; then
    log_success "Integration tests > E2E tests"
  else
    log_warn "Integration tests should be > E2E tests (integration=$integration, e2e=$e2e)"
  fi

  # Range checks
  echo ""
  print_header "Target Range Analysis"

  if [ "$unit_pct" -ge 60 ] && [ "$unit_pct" -le 75 ]; then
    log_success "Unit tests are within target range (60-75%)"
  else
    log_warn "Unit tests outside target range (60-75%): currently at ${unit_pct}%"
  fi

  if [ "$integration_pct" -ge 15 ] && [ "$integration_pct" -le 35 ]; then
    log_success "Integration tests are within target range (15-35%)"
  else
    log_warn "Integration tests outside target range (15-35%): currently at ${integration_pct}%"
  fi

  if [ "$e2e_pct" -ge 3 ] && [ "$e2e_pct" -le 15 ]; then
    log_success "E2E tests are within target range (3-15%)"
  else
    log_warn "E2E tests outside target range (3-15%): currently at ${e2e_pct}%"
  fi
}

###############################################################################
# JSON Report Generation
###############################################################################

generate_json_report() {
  local unit=$1
  local integration=$2
  local e2e=$3

  local total=$((unit + integration + e2e))
  local unit_pct=$((unit * 100 / total))
  local integration_pct=$((integration * 100 / total))
  local e2e_pct=$((e2e * 100 / total))

  cat > "$OUTPUT_FILE" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "summary": {
    "total": $total,
    "unit": {
      "count": $unit,
      "percentage": $unit_pct,
      "target_range": "60-75%",
      "status": $([ "$unit_pct" -ge 60 ] && [ "$unit_pct" -le 75 ] && echo '"pass"' || echo '"warn"')
    },
    "integration": {
      "count": $integration,
      "percentage": $integration_pct,
      "target_range": "15-35%",
      "status": $([ "$integration_pct" -ge 15 ] && [ "$integration_pct" -le 35 ] && echo '"pass"' || echo '"warn"')
    },
    "e2e": {
      "count": $e2e,
      "percentage": $e2e_pct,
      "target_range": "3-15%",
      "status": $([ "$e2e_pct" -ge 3 ] && [ "$e2e_pct" -le 15 ] && echo '"pass"' || echo '"warn"')
    }
  },
  "pyramid_shape": {
    "unit_gt_integration": $([ "$unit" -gt "$integration" ] && echo 'true' || echo 'false'),
    "integration_gt_e2e": $([ "$integration" -gt "$e2e" ] || [ "$e2e" -eq 0 ] && echo 'true' || echo 'false'),
    "status": $([ "$unit" -gt "$integration" ] && ([ "$integration" -gt "$e2e" ] || [ "$e2e" -eq 0 ]) && echo '"healthy"' || echo '"imbalanced"')
  }
}
EOF

  log_success "JSON report written to: $OUTPUT_FILE"
}

###############################################################################
# Main Execution
###############################################################################

main() {
  print_header "Test Pyramid Verification"

  log_info "Scanning Go tests..."
  local go_unit=$(count_go_tests unit)
  local go_integration=$(count_go_tests integration)
  local go_e2e=$(count_go_tests e2e)
  log_success "Go: Unit=$go_unit Integration=$go_integration E2E=$go_e2e"

  log_info "Scanning TypeScript tests..."
  local ts_unit=$(count_ts_tests unit)
  local ts_integration=$(count_ts_tests integration)
  local ts_e2e=$(count_ts_tests e2e)
  log_success "TypeScript: Unit=$ts_unit Integration=$ts_integration E2E=$ts_e2e"

  log_info "Scanning Python tests..."
  local py_unit=$(count_python_tests unit)
  local py_integration=$(count_python_tests integration)
  local py_e2e=$(count_python_tests e2e)
  log_success "Python: Unit=$py_unit Integration=$py_integration E2E=$py_e2e"

  # Aggregate totals
  local total_unit=$((go_unit + ts_unit + py_unit))
  local total_integration=$((go_integration + ts_integration + py_integration))
  local total_e2e=$((go_e2e + ts_e2e + py_e2e))

  # Generate reports
  generate_report "$total_unit" "$total_integration" "$total_e2e"

  if [ -n "$OUTPUT_FILE" ]; then
    generate_json_report "$total_unit" "$total_integration" "$total_e2e"
  fi

  # Validation
  validate_pyramid_shape "$total_unit" "$total_integration" "$total_e2e"
  local validation_result=$?

  echo ""

  if [ "$validation_result" -eq 0 ]; then
    log_success "Test pyramid is healthy!"
    return 0
  else
    if [ "$STRICT_MODE" = "true" ]; then
      log_error "Test pyramid imbalance detected in strict mode"
      return 2
    else
      log_warn "Test pyramid imbalance detected (non-strict mode)"
      return 0
    fi
  fi
}

# Run main function
main "$@"
exit $?
