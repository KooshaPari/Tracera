#!/bin/bash

###############################################################################
# Test Pyramid Verification Script
#
# Verifies test pyramid ratios: unit tests >> integration >> E2E
# Fails if pyramid is inverted or imbalanced
#
# Test Categories:
#   - Unit: Single function, no external deps (*_test.go, *.test.ts, test_*.py)
#   - Integration: Real DB/Redis/services (*_integration.go, *.integration.test.ts)
#   - E2E: Browser/full app (e2e/*.spec.ts, *.e2e.test.ts)
#
# Constraints:
#   - Unit tests >= 70% (required)
#   - Integration 15-25% (recommended)
#   - E2E <= 10% (required)
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Counters
UNIT_COUNT=0
INTEGRATION_COUNT=0
E2E_COUNT=0
UNIT_FILES=()
INTEGRATION_FILES=()
E2E_FILES=()

###############################################################################
# Helper Functions
###############################################################################

log_info() {
  echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
  echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
  echo -e "${RED}✗${NC} $*"
}

count_test_files() {
  local pattern=$1
  local type=$2
  local paths=("${@:3}")

  for path in "${paths[@]}"; do
    if [[ -d "$PROJECT_ROOT/$path" ]]; then
      while IFS= read -r file; do
        case "$type" in
          "unit")
            UNIT_COUNT=$((UNIT_COUNT + 1))
            UNIT_FILES+=("$file")
            ;;
          "integration")
            INTEGRATION_COUNT=$((INTEGRATION_COUNT + 1))
            INTEGRATION_FILES+=("$file")
            ;;
          "e2e")
            E2E_COUNT=$((E2E_COUNT + 1))
            E2E_FILES+=("$file")
            ;;
        esac
      done < <(find "$PROJECT_ROOT/$path" -type f -name "$pattern" 2>/dev/null || true)
    fi
  done
}

# Count Go unit tests (*_test.go, excluding *_integration_test.go)
count_go_unit_tests() {
  for path in "$@"; do
    if [[ -d "$PROJECT_ROOT/$path" ]]; then
      while IFS= read -r file; do
        # Skip integration tests
        if [[ ! "$file" =~ _integration_test\.go$ ]]; then
          UNIT_COUNT=$((UNIT_COUNT + 1))
          UNIT_FILES+=("${file#$PROJECT_ROOT/}")
        fi
      done < <(find "$PROJECT_ROOT/$path" -type f -name "*_test.go" 2>/dev/null || true)
    fi
  done
}

# Count Go integration tests (*_integration_test.go)
count_go_integration_tests() {
  for path in "$@"; do
    if [[ -d "$PROJECT_ROOT/$path" ]]; then
      while IFS= read -r file; do
        INTEGRATION_COUNT=$((INTEGRATION_COUNT + 1))
        INTEGRATION_FILES+=("${file#$PROJECT_ROOT/}")
      done < <(find "$PROJECT_ROOT/$path" -type f -name "*_integration_test.go" 2>/dev/null || true)
    fi
  done
}

# Count TypeScript/React unit tests (*.test.ts, *.test.tsx)
count_ts_unit_tests() {
  for path in "$@"; do
    if [[ -d "$PROJECT_ROOT/$path" ]]; then
      while IFS= read -r file; do
        # Skip integration and e2e tests
        if [[ ! "$file" =~ \.integration\.test\.ts(x)?$ ]] && [[ ! "$file" =~ \.e2e\.test\.ts(x)?$ ]]; then
          UNIT_COUNT=$((UNIT_COUNT + 1))
          UNIT_FILES+=("${file#$PROJECT_ROOT/}")
        fi
      done < <(find "$PROJECT_ROOT/$path" -type f \( -name "*.test.ts" -o -name "*.test.tsx" \) 2>/dev/null || true)
    fi
  done
}

# Count TypeScript integration tests (*.integration.test.ts)
count_ts_integration_tests() {
  for path in "$@"; do
    if [[ -d "$PROJECT_ROOT/$path" ]]; then
      while IFS= read -r file; do
        INTEGRATION_COUNT=$((INTEGRATION_COUNT + 1))
        INTEGRATION_FILES+=("${file#$PROJECT_ROOT/}")
      done < <(find "$PROJECT_ROOT/$path" -type f -name "*.integration.test.ts*" 2>/dev/null || true)
    fi
  done
}

# Count TypeScript E2E tests (e2e/*.spec.ts, *.e2e.test.ts)
count_ts_e2e_tests() {
  # Count e2e/ directory tests
  if [[ -d "$PROJECT_ROOT/frontend/apps/web/e2e" ]]; then
    while IFS= read -r file; do
      E2E_COUNT=$((E2E_COUNT + 1))
      E2E_FILES+=("${file#$PROJECT_ROOT/}")
    done < <(find "$PROJECT_ROOT/frontend/apps/web/e2e" -type f \( -name "*.spec.ts" -o -name "*.e2e.test.ts" -o -name "*.e2e.test.tsx" \) 2>/dev/null || true)
  fi

  # Count *.e2e.test.ts files in __tests__
  for path in "$@"; do
    if [[ -d "$PROJECT_ROOT/$path" ]]; then
      while IFS= read -r file; do
        E2E_COUNT=$((E2E_COUNT + 1))
        E2E_FILES+=("${file#$PROJECT_ROOT/}")
      done < <(find "$PROJECT_ROOT/$path" -type f \( -name "*.e2e.test.ts*" \) 2>/dev/null || true)
    fi
  done
}

# Count Python tests (test_*.py for unit, *_integration_test.py for integration)
count_python_tests() {
  if [[ -d "$PROJECT_ROOT/backend/tests" ]]; then
    while IFS= read -r file; do
      if [[ "$file" =~ _integration_test\.py$ ]] || [[ "$file" =~ _integration\.py$ ]]; then
        INTEGRATION_COUNT=$((INTEGRATION_COUNT + 1))
        INTEGRATION_FILES+=("${file#$PROJECT_ROOT/}")
      else
        UNIT_COUNT=$((UNIT_COUNT + 1))
        UNIT_FILES+=("${file#$PROJECT_ROOT/}")
      fi
    done < <(find "$PROJECT_ROOT/backend/tests" -type f -name "test_*.py" 2>/dev/null || true)
  fi
}

print_pyramid() {
  local total=$((UNIT_COUNT + INTEGRATION_COUNT + E2E_COUNT))

  if [[ $total -eq 0 ]]; then
    log_error "No tests found!"
    return 1
  fi

  local unit_pct=$((UNIT_COUNT * 100 / total))
  local integration_pct=$((INTEGRATION_COUNT * 100 / total))
  local e2e_pct=$((E2E_COUNT * 100 / total))

  # ASCII Pyramid
  echo ""
  echo -e "${BLUE}Test Pyramid Visualization:${NC}"
  echo ""
  echo "           /\\"
  echo -e "          /  \\  ${YELLOW}E2E Tests${NC} ($e2e_pct%, $E2E_COUNT tests)"
  echo "         /____\\"
  echo "        /      \\"
  echo -e "       /        \\  ${YELLOW}Integration Tests${NC} ($integration_pct%, $INTEGRATION_COUNT tests)"
  echo "      /          \\"
  echo "     /____________\\"
  echo -e "    ${YELLOW}Unit Tests${NC} ($unit_pct%, $UNIT_COUNT tests)"
  echo ""
}

print_detailed_report() {
  local total=$((UNIT_COUNT + INTEGRATION_COUNT + E2E_COUNT))

  if [[ $total -eq 0 ]]; then
    return
  fi

  local unit_pct=$((UNIT_COUNT * 100 / total))
  local integration_pct=$((INTEGRATION_COUNT * 100 / total))
  local e2e_pct=$((E2E_COUNT * 100 / total))

  echo ""
  echo -e "${BLUE}Detailed Test Count Report:${NC}"
  echo ""
  echo "Total Tests: $total"
  echo "├── Unit Tests:        $UNIT_COUNT ($unit_pct%)"
  echo "├── Integration Tests: $INTEGRATION_COUNT ($integration_pct%)"
  echo "└── E2E Tests:         $E2E_COUNT ($e2e_pct%)"
  echo ""
}

print_constraint_analysis() {
  local total=$((UNIT_COUNT + INTEGRATION_COUNT + E2E_COUNT))

  if [[ $total -eq 0 ]]; then
    return
  fi

  local unit_pct=$((UNIT_COUNT * 100 / total))
  local integration_pct=$((INTEGRATION_COUNT * 100 / total))
  local e2e_pct=$((E2E_COUNT * 100 / total))

  echo -e "${BLUE}Constraint Analysis:${NC}"
  echo ""

  # Unit tests >= 70%
  if [[ $unit_pct -ge 70 ]]; then
    log_success "Unit tests >= 70% ($unit_pct%)"
  else
    log_error "Unit tests < 70% ($unit_pct%) - REQUIRED CONSTRAINT VIOLATED"
  fi

  # Integration 15-25%
  if [[ $integration_pct -ge 15 && $integration_pct -le 25 ]]; then
    log_success "Integration tests 15-25% ($integration_pct%)"
  else
    log_warning "Integration tests outside 15-25% range ($integration_pct%) - not ideal"
  fi

  # E2E <= 10%
  if [[ $e2e_pct -le 10 ]]; then
    log_success "E2E tests <= 10% ($e2e_pct%)"
  else
    log_error "E2E tests > 10% ($e2e_pct%) - REQUIRED CONSTRAINT VIOLATED"
  fi

  echo ""
}

print_pyramid_status() {
  local total=$((UNIT_COUNT + INTEGRATION_COUNT + E2E_COUNT))

  if [[ $total -eq 0 ]]; then
    return
  fi

  local unit_pct=$((UNIT_COUNT * 100 / total))
  local integration_pct=$((INTEGRATION_COUNT * 100 / total))
  local e2e_pct=$((E2E_COUNT * 100 / total))

  echo -e "${BLUE}Pyramid Status:${NC}"
  echo ""

  # Check if pyramid is healthy
  local unit_ok=0
  local e2e_ok=0

  if [[ $unit_pct -ge 70 ]]; then
    unit_ok=1
  fi

  if [[ $e2e_pct -le 10 ]]; then
    e2e_ok=1
  fi

  if [[ $unit_ok -eq 1 && $e2e_ok -eq 1 ]]; then
    log_success "Test pyramid is HEALTHY"
    echo "  • Strong unit test foundation (${unit_pct}%)"
    echo "  • Acceptable E2E test coverage (${e2e_pct}%)"
    return 0
  else
    log_error "Test pyramid is IMBALANCED or INVERTED"
    if [[ $unit_ok -eq 0 ]]; then
      echo "  • Unit tests too low (${unit_pct}% vs required 70%)"
    fi
    if [[ $e2e_ok -eq 0 ]]; then
      echo "  • E2E tests too high (${e2e_pct}% vs required max 10%)"
    fi
    return 1
  fi
}

print_recommendations() {
  local total=$((UNIT_COUNT + INTEGRATION_COUNT + E2E_COUNT))

  if [[ $total -eq 0 ]]; then
    return
  fi

  local unit_pct=$((UNIT_COUNT * 100 / total))
  local integration_pct=$((INTEGRATION_COUNT * 100 / total))
  local e2e_pct=$((E2E_COUNT * 100 / total))

  echo ""
  echo -e "${BLUE}Recommendations:${NC}"
  echo ""

  if [[ $unit_pct -lt 70 ]]; then
    log_warning "Increase unit tests to reach 70%"
    local needed=$((UNIT_COUNT * 100 / 70 - total))
    echo "  → Need ~$needed more tests (favoring unit tests)"
  fi

  if [[ $e2e_pct -gt 10 ]]; then
    log_warning "Reduce E2E tests to reach <= 10%"
    local excess=$((E2E_COUNT - total * 10 / 100))
    echo "  → Consider moving $excess tests to integration or unit level"
  fi

  if [[ $integration_pct -lt 15 ]]; then
    log_warning "Integration tests below recommended 15%"
    echo "  → Consider adding more integration tests"
  elif [[ $integration_pct -gt 25 ]]; then
    log_warning "Integration tests above recommended 25%"
    echo "  → Consider converting some to unit tests"
  fi

  echo ""
}

print_file_lists() {
  local verbose=$1

  if [[ "$verbose" != "1" ]]; then
    return
  fi

  echo -e "${BLUE}Unit Test Files:${NC}"
  for file in "${UNIT_FILES[@]:0:5}"; do
    echo "  • $file"
  done
  if [[ ${#UNIT_FILES[@]} -gt 5 ]]; then
    echo "  ... and $((${#UNIT_FILES[@]} - 5)) more"
  fi
  echo ""

  echo -e "${BLUE}Integration Test Files:${NC}"
  for file in "${INTEGRATION_FILES[@]:0:5}"; do
    echo "  • $file"
  done
  if [[ ${#INTEGRATION_FILES[@]} -gt 5 ]]; then
    echo "  ... and $((${#INTEGRATION_FILES[@]} - 5)) more"
  fi
  echo ""

  echo -e "${BLUE}E2E Test Files:${NC}"
  for file in "${E2E_FILES[@]:0:5}"; do
    echo "  • $file"
  done
  if [[ ${#E2E_FILES[@]} -gt 5 ]]; then
    echo "  ... and $((${#E2E_FILES[@]} - 5)) more"
  fi
  echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
  log_info "Scanning test pyramid..."
  echo ""

  # Count Go tests
  log_info "Scanning Go backend tests..."
  count_go_unit_tests "backend/internal"
  count_go_integration_tests "backend/internal"

  # Count TypeScript/React tests
  log_info "Scanning TypeScript/React tests..."
  count_ts_unit_tests \
    "frontend/apps/web/src/__tests__" \
    "frontend/apps/docs/src/__tests__" \
    "frontend/packages/ui/src/__tests__" \
    "frontend/packages/state/src/__tests__" \
    "frontend/packages/api-client/src/__tests__" \
    "frontend/packages/env-manager/src/__tests__"

  count_ts_integration_tests \
    "frontend/apps/web/src/__tests__" \
    "frontend/apps/docs/src/__tests__"

  count_ts_e2e_tests \
    "frontend/apps/web/src/__tests__"

  # Count Python tests
  log_info "Scanning Python backend tests..."
  count_python_tests

  # Print results
  echo ""
  print_detailed_report
  print_pyramid
  print_constraint_analysis

  local status=0
  if ! print_pyramid_status; then
    status=1
  fi

  print_recommendations

  # Verbose output if requested
  if [[ "${1:-}" == "-v" || "${1:-}" == "--verbose" ]]; then
    print_file_lists 1
  fi

  exit $status
}

main "$@"
