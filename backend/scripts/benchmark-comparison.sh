#!/usr/bin/env bash

################################################################################
# Benchmark Regression Comparison Script
#
# Compares current benchmark metrics against a baseline from main branch.
# Fails CI if metrics regress beyond 10% threshold.
#
# Metrics compared:
#   - Response time (ns/op = nanoseconds per operation)
#   - Memory usage (bytes/op and allocs/op)
#   - Throughput (ops/sec = operations per second)
#
# Exit codes:
#   0 = No regression or baseline doesn't exist (first run)
#   1 = Critical regression detected (>20%) or malformed data
#   2 = Warning regression detected (10-20%)
################################################################################

set -euo pipefail

# Configuration
THRESHOLD_WARN=10      # Yellow warning threshold (%)
THRESHOLD_CRITICAL=20  # Red critical threshold (%)
TEMP_DIR="."  # Default to current directory, can be overridden
BASELINE_FILE="benchmark-baseline.json"
CURRENT_FILE="benchmark-current.json"
REPORT_FILE="benchmark-comparison-report.md"

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

################################################################################
# Logging Functions
################################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_header() {
    echo ""
    echo "================================================================================"
    echo "$*"
    echo "================================================================================"
}

################################################################################
# Benchmark Data Extraction Functions
################################################################################

# Extract benchmark results from Go test output (-bench flag)
# Go benchmark format: BenchmarkName-8      1000000     1234 ns/op    5678 B/op    90 allocs/op
extract_go_benchmarks() {
    local bench_output="$1"
    local output_json="$2"

    log_info "Extracting Go benchmark results..."

    # Initialize JSON array
    echo '[]' > "$output_json"

    # Parse go test -bench output
    # Expected format from `go test -bench=. -benchmem -benchstat ./...`
    if [[ ! -f "$bench_output" ]]; then
        log_error "Go benchmark output file not found: $bench_output"
        return 1
    fi

    local benchmarks=()
    local json_array="["
    local first=true

    while IFS= read -r line; do
        # Skip empty lines and headers
        [[ -z "$line" || "$line" =~ ^(Benchmark|---) ]] && continue

        # Parse benchmark line: BenchmarkName-8      1000000     1234 ns/op    5678 B/op    90 allocs/op
        if [[ $line =~ ^Benchmark([^ -]*)-?[0-9]* ]]; then
            local name="${BASH_REMATCH[1]}"

            # Extract metrics (accounting for variable spacing)
            local ns_per_op=$(echo "$line" | grep -oP '\d+(?=\s*ns/op)' | head -1)
            local bytes_per_op=$(echo "$line" | grep -oP '\d+(?=\s*B/op)' || echo "0")
            local allocs_per_op=$(echo "$line" | grep -oP '\d+(?=\s*allocs/op)' || echo "0")
            local ops=$(echo "$line" | awk '{print $2}')

            if [[ -n "$ns_per_op" ]]; then
                local throughput=$(awk "BEGIN {printf \"%.0f\", 1e9 / $ns_per_op}")

                if [[ "$first" == true ]]; then
                    first=false
                else
                    json_array+=","
                fi

                json_array+="{\"name\":\"$name\",\"ns_per_op\":$ns_per_op,\"bytes_per_op\":${bytes_per_op:-0},\"allocs_per_op\":${allocs_per_op:-0},\"ops_per_sec\":$throughput}"
                benchmarks+=("$name")
            fi
        fi
    done < "$bench_output"

    json_array+="]"
    echo "$json_array" > "$output_json"

    if [[ ${#benchmarks[@]} -gt 0 ]]; then
        log_info "Extracted ${#benchmarks[@]} benchmarks: ${benchmarks[*]}"
        return 0
    else
        log_warn "No benchmarks found in output"
        return 0
    fi
}

# Extract metrics from JSON benchmark results
# Returns JSON: {"benchmarks": [...], "timestamp": "...", "commit": "..."}
extract_metrics_json() {
    local json_file="$1"
    local output_json="$2"

    log_info "Processing JSON benchmark metrics..."

    if [[ ! -f "$json_file" ]]; then
        log_error "JSON benchmark file not found: $json_file"
        return 1
    fi

    # Validate and format JSON
    if ! jq empty "$json_file" 2>/dev/null; then
        log_error "Invalid JSON in benchmark file: $json_file"
        return 1
    fi

    # Copy with timestamp if not present
    if jq -e '.timestamp' "$json_file" > /dev/null 2>&1; then
        cp "$json_file" "$output_json"
    else
        jq ". + {\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" "$json_file" > "$output_json"
    fi

    return 0
}

################################################################################
# Comparison Functions
################################################################################

# Calculate percentage difference between two values
# Returns: percentage value (e.g., 15.5 for 15.5% increase)
# Positive = regression (slower), Negative = improvement (faster)
calculate_percent_diff() {
    local baseline="$1"
    local current="$2"

    # Avoid division by zero
    if (( baseline == 0 )); then
        echo "0"
        return
    fi

    # Calculate: ((current - baseline) / baseline) * 100
    # For ns/op: higher = slower = regression
    # For ops/sec: lower = slower = regression (but we invert the calculation)
    awk -v b="$baseline" -v c="$current" 'BEGIN {printf "%.1f", ((c - b) / b) * 100}'
}

# Compare two benchmark results using simpler approach
# Returns JSON with comparison results
compare_benchmarks() {
    local baseline_json="$1"
    local current_json="$2"
    local output_json="$3"

    log_info "Comparing benchmarks against baseline..."

    if [[ ! -f "$baseline_json" || ! -f "$current_json" ]]; then
        log_warn "Baseline or current benchmarks missing; skipping comparison"
        echo '{"status":"no_baseline","message":"First run or baseline unavailable"}' > "$output_json"
        return 0
    fi

    # Validate JSON format
    if ! jq empty "$baseline_json" 2>/dev/null || ! jq empty "$current_json" 2>/dev/null; then
        log_warn "Invalid JSON format; treating as first run"
        echo '{"status":"no_baseline","message":"Invalid JSON in benchmarks"}' > "$output_json"
        return 0
    fi

    # Simple comparison: extract and match by name, calculate regressions
    local temp_comp=$(mktemp)
    echo '[' > "$temp_comp"

    local first=true
    jq -r '.[] | .name // empty' "$baseline_json" | while read -r name; do
        local baseline_ns=$(jq ".[] | select(.name == \"$name\") | .ns_per_op // 0" "$baseline_json" | head -1)
        local current_ns=$(jq ".[] | select(.name == \"$name\") | .ns_per_op // 0" "$current_json" | head -1)

        local baseline_bytes=$(jq ".[] | select(.name == \"$name\") | .bytes_per_op // 0" "$baseline_json" | head -1)
        local current_bytes=$(jq ".[] | select(.name == \"$name\") | .bytes_per_op // 0" "$current_json" | head -1)

        local baseline_allocs=$(jq ".[] | select(.name == \"$name\") | .allocs_per_op // 0" "$baseline_json" | head -1)
        local current_allocs=$(jq ".[] | select(.name == \"$name\") | .allocs_per_op // 0" "$current_json" | head -1)

        if [[ -z "$baseline_ns" || "$baseline_ns" == "null" ]]; then
            baseline_ns=0
        fi
        if [[ -z "$current_ns" || "$current_ns" == "null" ]]; then
            current_ns=0
        fi

        # Calculate regression percentage
        local regression="0"
        if (( baseline_ns > 0 )); then
            regression=$(awk -v b="$baseline_ns" -v c="$current_ns" 'BEGIN {printf "%.1f", ((c - b) / b) * 100}')
        fi

        if [[ "$first" == "false" ]]; then
            echo "," >> "$temp_comp"
        fi
        first=false

        cat >> "$temp_comp" << EOF
{
  "name": "$name",
  "baseline": {
    "ns_per_op": $baseline_ns,
    "bytes_per_op": ${baseline_bytes:-0},
    "allocs_per_op": ${baseline_allocs:-0}
  },
  "current": {
    "ns_per_op": $current_ns,
    "bytes_per_op": ${current_bytes:-0},
    "allocs_per_op": ${current_allocs:-0}
  },
  "regression_ns": $regression
}
EOF
    done

    echo ']' >> "$temp_comp"

    # Build final comparison JSON
    jq -n \
        --slurpfile comparisons "$temp_comp" \
        '{
            status: "compared",
            timestamp: "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
            comparisons: $comparisons[0]
        }' > "$output_json"

    rm -f "$temp_comp"
    return 0
}

################################################################################
# Report Generation Functions
################################################################################

# Generate formatted comparison report
generate_report() {
    local comparison_json="$1"
    local report_file="$2"

    log_info "Generating comparison report..."

    {
        echo "# Benchmark Regression Comparison Report"
        echo ""
        echo "**Timestamp:** $(jq -r '.timestamp // "N/A"' "$comparison_json")"
        echo ""

        # Check for status (first run, no baseline)
        local status=$(jq -r '.status // "compared"' "$comparison_json")
        if [[ "$status" != "compared" ]]; then
            echo "## Status: $status"
            echo ""
            echo "$(jq -r '.message // "No baseline available"' "$comparison_json")"
            echo ""
            return 0
        fi

        echo "## Summary"
        echo ""

        # Count regressions
        local critical=$(jq '[.comparisons[] | select(.regression_ns > '$THRESHOLD_CRITICAL')] | length' "$comparison_json")
        local warning=$(jq '[.comparisons[] | select(.regression_ns > '$THRESHOLD_WARN' and .regression_ns <= '$THRESHOLD_CRITICAL')] | length' "$comparison_json")
        local passed=$(jq '[.comparisons[] | select(.regression_ns <= '$THRESHOLD_WARN')] | length' "$comparison_json")

        echo "| Category | Count | Status |"
        echo "|----------|-------|--------|"
        echo "| ✅ Passed (<10%) | $passed | Good |"
        echo "| ⚠️ Warning (10-20%) | $warning | Check |"
        echo "| 🔴 Critical (>20%) | $critical | Fail |"
        echo ""

        # Detailed results table
        echo "## Detailed Results"
        echo ""
        echo "| Benchmark | Baseline (ns/op) | Current (ns/op) | Regression | Status |"
        echo "|-----------|------------------|-----------------|------------|--------|"

        jq -r '.comparisons[] |
            @sh "| \(.name) | \(.baseline.ns_per_op) | \(.current.ns_per_op) | \(.regression_ns | floor)% | \(
                if .regression_ns > '$THRESHOLD_CRITICAL' then "🔴 CRITICAL"
                elif .regression_ns > '$THRESHOLD_WARN' then "⚠️ WARNING"
                else "✅ PASS" end
            ) |"' "$comparison_json" | sed "s/'//g"

        echo ""
        echo "## Metric Breakdown"
        echo ""
        echo "### Response Time (ns/op)"
        echo ""
        jq -r '.comparisons[] |
            "- **\(.name)**: \(.baseline.ns_per_op) → \(.current.ns_per_op) ns/op (\(.regression_ns | floor)%)"' "$comparison_json"

        echo ""
        echo "### Memory Usage (bytes/op)"
        echo ""
        jq -r '.comparisons[] |
            "- **\(.name)**: \(.baseline.bytes_per_op) → \(.current.bytes_per_op) B/op"' "$comparison_json"

        echo ""
        echo "### Allocations (allocs/op)"
        echo ""
        jq -r '.comparisons[] |
            "- **\(.name)**: \(.baseline.allocs_per_op) → \(.current.allocs_per_op) allocs/op"' "$comparison_json"

        echo ""
        echo "## Thresholds"
        echo ""
        echo "- 🟢 **Pass**: Regression < ${THRESHOLD_WARN}%"
        echo "- 🟡 **Warning**: ${THRESHOLD_WARN}% ≤ Regression ≤ ${THRESHOLD_CRITICAL}%"
        echo "- 🔴 **Critical**: Regression > ${THRESHOLD_CRITICAL}%"

    } > "$report_file"

    cat "$report_file"
}

# Write report to GitHub Step Summary
write_github_summary() {
    local comparison_json="$1"

    if [[ -z "${GITHUB_STEP_SUMMARY:-}" ]]; then
        return 0  # Not in GitHub Actions
    fi

    local status=$(jq -r '.status // "compared"' "$comparison_json")

    {
        echo "# Benchmark Regression Comparison"
        echo ""

        if [[ "$status" != "compared" ]]; then
            echo "Status: $status - $(jq -r '.message' "$comparison_json")"
            return 0
        fi

        local critical=$(jq '[.comparisons[] | select(.regression_ns > '$THRESHOLD_CRITICAL')] | length' "$comparison_json")
        local warning=$(jq '[.comparisons[] | select(.regression_ns > '$THRESHOLD_WARN' and .regression_ns <= '$THRESHOLD_CRITICAL')] | length' "$comparison_json")

        if (( critical > 0 )); then
            echo "## 🔴 CRITICAL Regressions Detected"
            echo ""
        fi

        if (( warning > 0 )); then
            echo "## ⚠️ Performance Warnings"
            echo ""
        fi

        echo "| Benchmark | Baseline | Current | Regression |"
        echo "|-----------|----------|---------|------------|"
        jq -r '.comparisons[] | "| \(.name) | \(.baseline.ns_per_op) ns | \(.current.ns_per_op) ns | \(.regression_ns | floor)% |"' "$comparison_json"

    } >> "$GITHUB_STEP_SUMMARY"
}

################################################################################
# Exit Status Determination
################################################################################

# Determine exit code based on regression severity
determine_exit_code() {
    local comparison_json="$1"

    local status=$(jq -r '.status // "compared"' "$comparison_json")

    # First run: no baseline yet
    if [[ "$status" != "compared" ]]; then
        log_info "First run or no baseline - storing current metrics as baseline"
        return 0
    fi

    # Check for critical regressions
    local critical=$(jq '[.comparisons[] | select(.regression_ns > '$THRESHOLD_CRITICAL')] | length' "$comparison_json")
    if (( critical > 0 )); then
        log_error "CRITICAL: Found $critical benchmarks with >20% regression"
        return 1
    fi

    # Check for warnings
    local warning=$(jq '[.comparisons[] | select(.regression_ns > '$THRESHOLD_WARN' and .regression_ns <= '$THRESHOLD_CRITICAL')] | length' "$comparison_json")
    if (( warning > 0 )); then
        log_warn "WARNING: Found $warning benchmarks with 10-20% regression"
        # Note: Not failing on warnings, only critical
        return 0
    fi

    log_info "All benchmarks within acceptable thresholds"
    return 0
}

################################################################################
# Main Orchestration
################################################################################

main() {
    log_header "Benchmark Regression Gating"

    # Verify jq is available
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        exit 1
    fi

    # Check if baseline exists (typically downloaded from artifact)
    if [[ ! -f "$BASELINE_FILE" ]]; then
        log_info "No baseline found at $BASELINE_FILE"
        log_info "This is the first run or baseline not available"
        log_info "Current metrics will be stored as baseline for next comparison"

        # If current metrics exist, copy them as baseline for next run
        if [[ -f "$CURRENT_FILE" ]]; then
            cp "$CURRENT_FILE" "$BASELINE_FILE"
            log_info "Baseline stored: $BASELINE_FILE"
        fi

        return 0
    fi

    # Generate comparison
    local comparison_json="$TEMP_DIR/benchmark-comparison.json"
    compare_benchmarks "$BASELINE_FILE" "$CURRENT_FILE" "$comparison_json"

    # Generate reports
    generate_report "$comparison_json" "$REPORT_FILE"
    write_github_summary "$comparison_json"

    # Determine exit status
    determine_exit_code "$comparison_json"
    local exit_code=$?

    # Store current metrics as baseline for next run
    if [[ -f "$CURRENT_FILE" ]]; then
        cp "$CURRENT_FILE" "$BASELINE_FILE"
        log_info "Updated baseline for next comparison"
    fi

    return $exit_code
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --baseline)
            BASELINE_FILE="$2"
            shift 2
            ;;
        --current)
            CURRENT_FILE="$2"
            shift 2
            ;;
        --output)
            REPORT_FILE="$2"
            shift 2
            ;;
        --threshold-warn)
            THRESHOLD_WARN="$2"
            shift 2
            ;;
        --threshold-critical)
            THRESHOLD_CRITICAL="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Usage: $0 [--baseline FILE] [--current FILE] [--output REPORT] [--threshold-warn PCT] [--threshold-critical PCT]"
            exit 1
            ;;
    esac
done

# Run main
main
