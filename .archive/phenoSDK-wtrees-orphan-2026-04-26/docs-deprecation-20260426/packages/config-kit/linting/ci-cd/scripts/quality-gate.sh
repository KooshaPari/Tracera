#!/bin/bash

# Quality Gate Script for config-kit
# This script runs all quality checks and exits with non-zero if any fail

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
PASSED=0
FAILED=0
TOTAL=0
RESULTS_FILE="quality_gate_results.json"

# Function to print colored output
print_header() {
    echo -e "${BLUE}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to initialize results JSON
init_results() {
    cat > "$RESULTS_FILE" << EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "project": "config-kit",
    "checks": {}
}
EOF
}

# Function to add check result to JSON
add_check_result() {
    local check_name="$1"
    local status="$2"
    local message="$3"
    local details="$4"
    
    # Use jq to update the JSON file
    if command_exists jq; then
        jq --arg name "$check_name" --arg status "$status" --arg message "$message" --arg details "$details" '
        .checks[$name] = {
            "status": $status,
            "message": $message,
            "details": $details,
            "timestamp": now
        }' "$RESULTS_FILE" > temp.json && mv temp.json "$RESULTS_FILE"
    fi
}

# Function to run check and count results
run_check() {
    local check_name="$1"
    local check_command="$2"
    local success_message="$3"
    local failure_message="$4"
    
    TOTAL=$((TOTAL + 1))
    print_header "RUNNING" "$check_name"
    
    if eval "$check_command" >/dev/null 2>&1; then
        PASSED=$((PASSED + 1))
        print_success "$success_message"
        add_check_result "$check_name" "passed" "$success_message" ""
        return 0
    else
        FAILED=$((FAILED + 1))
        print_error "$failure_message"
        add_check_result "$check_name" "failed" "$failure_message" ""
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Linting checks
run_linting_checks() {
    print_header "SECTION" "Linting Checks"
    
    run_check "Ruff" "ruff check --exit-zero" "Ruff passed" "Ruff failed"
    run_check "Black formatting" "black --check ." "Black format passed" "Black format failed"
    run_check "Import sorting" "isort --check-only ." "isort passed" "isort failed"
    run_check "Type checking" "mypy --ignore-missing-imports src/" "Mypy passed" "Mypy failed"
}

# Security checks
run_security_checks() {
    print_header "SECTION" "Security Checks"
    
    run_check "Bandit security scan" "bandit -r src -f json -o bandit-report.json" "Bandit passed" "Bandit failed"
    run_check "Safety vulnerability check" "safety check --json --output safety-report.json" "Safety passed" "Safety failed"
    run_check "Secrets detection" "detect-secrets scan --baseline .secrets.baseline" "Secrets check passed" "Secrets check failed"
}

# Documentation checks
run_documentation_checks() {
    print_header "SECTION" "Documentation Checks"
    
    run_check "Docstring style" "pydocstyle --convention=google src/" "Pydocstyle passed" "Pydocstyle failed"
    run_check "Coverage check" "pytest --cov=src --cov-report=term-missing --cov-fail-under=80" "Coverage check passed" "Coverage check failed"
}

# Performance checks
run_performance_checks() {
    print_header "SECTION" "Performance Checks"
    
    run_check "Complexity check" "radon cc src/ -nb -a" "Complexity check passed" "Complexity check failed"
    run_check "Maintainability index" "radon cc src/ -nb" "Maintainability check passed" "Maintainability check failed"
}

# Dependency checks
run_dependency_checks() {
    print_header "SECTION" "Dependency Checks"
    
    run_check "Dependency vulnerability" "pip-audit" "Dependency audit passed" "Dependency audit failed"
    run_check "Outdated dependencies" "pip list --outdated --format=json --timeout 60" "Dependency check passed" "Dependency check failed"
}

# Code quality metrics
run_quality_metrics() {
    print_header "SECTION" "Quality Metrics"
    
    # Check file sizes
    local large_files=$(find src/ -name "*.py" -size +50k)
    if [ -n "$large_files" ]; then
        print_warning "Large files found: $large_files"
        add_check_result "File sizes" "warning" "Large files detected" "$large_files"
        TOTAL=$((TOTAL + 1))
        FAILED=$((FAILED + 1))
    else
        PASSED=$((PASSED + 1))
        print_success "All files are under size limit"
        add_check_result "File sizes" "passed" "All files under size limit" ""
    fi
    
    # Check cyclomatic complexity
    local complex_files=$(radon cc src/ -nb -a | grep -v "F" | awk '$2 > 10 {print $1}')
    if [ -n "$complex_files" ]; then
        print_warning "Complex files found: $complex_files"
        add_check_result "Complexity" "warning" "Complex files detected" "$complex_files"
        TOTAL=$((TOTAL + 1))
        FAILED=$((FAILED + 1))
    else
        PASSED=$((PASSED + 1))
        print_success "All files have acceptable complexity"
        add_check_result "Complexity" "passed" "All files have acceptable complexity" ""
    fi
}

# Cleanup function
cleanup() {
    # Remove temporary files
    rm -f temp.json bandit-report.json safety-report.json
}

# Main execution
main() {
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Initialize results
    init_results
    
    echo "Starting Quality Gate checks..."
    echo "=================================="
    
    # Run all checks
    run_linting_checks
    run_security_checks
    run_documentation_checks
    run_performance_checks
    run_dependency_checks
    run_quality_metrics
    
    # Summary
    echo ""
    echo "=================================="
    echo "Quality Gate Summary"
    echo "=================================="
    echo "Total checks: $TOTAL"
    echo "Passed: $PASSED"
    echo "Failed: $FAILED"
    
    if [ $FAILED -eq 0 ]; then
        echo ""
        print_success "All checks passed! Quality gate passed."
        exit 0
    else
        echo ""
        print_error "$FAILED checks failed. Quality gate failed."
        exit 1
    fi
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src" ]; then
    print_error "This script must be run from the config-kit root directory"
    exit 1
fi

# Check for required commands
if ! command_exists ruff; then
    print_error "ruff is required but not installed"
    exit 1
fi

if ! command_exists black; then
    print_error "black is required but not installed"
    exit 1
fi

if ! command_exists isort; then
    print_error "isort is required but not installed"
    exit 1
fi

if ! command_exists mypy; then
    print_error "mypy is required but not installed"
    exit 1
fi

# Run main function
main "$@"
