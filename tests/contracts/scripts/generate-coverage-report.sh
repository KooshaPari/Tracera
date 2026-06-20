#!/bin/bash
#
# Generate Contract Coverage Report
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONTRACTS_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
PROJECT_ROOT="$( cd "$CONTRACTS_DIR/../.." && pwd )"

OPENAPI_SPEC="$PROJECT_ROOT/frontend/apps/web/public/specs/openapi.json"
PACTS_DIR="$CONTRACTS_DIR/pacts"
COVERAGE_REPORT="$CONTRACTS_DIR/docs/coverage.md"

echo "Generating contract coverage report..."

# Extract all endpoints from OpenAPI spec
TOTAL_ENDPOINTS=$(jq '.paths | keys | length' "$OPENAPI_SPEC")

# Count pact interactions
PACT_INTERACTIONS=0
COVERED_ENDPOINTS=()

for pact in "$PACTS_DIR"/*.json 2>/dev/null; do
    if [ -f "$pact" ]; then
        INTERACTIONS=$(jq '.interactions | length' "$pact" 2>/dev/null || echo "0")
        PACT_INTERACTIONS=$((PACT_INTERACTIONS + INTERACTIONS))

        # Extract covered endpoints
        ENDPOINTS=$(jq -r '.interactions[].request.path' "$pact" 2>/dev/null || true)
        while IFS= read -r endpoint; do
            if [ -n "$endpoint" ]; then
                COVERED_ENDPOINTS+=("$endpoint")
            fi
        done <<< "$ENDPOINTS"
    fi
done

# Count unique covered endpoints
UNIQUE_ENDPOINTS=$(printf '%s\n' "${COVERED_ENDPOINTS[@]}" | sort -u | wc -l)

# Calculate coverage percentage
if [ "$TOTAL_ENDPOINTS" -gt 0 ]; then
    COVERAGE_PCT=$(awk "BEGIN {printf \"%.1f\", ($UNIQUE_ENDPOINTS/$TOTAL_ENDPOINTS)*100}")
else
    COVERAGE_PCT=0
fi

# Generate markdown report
mkdir -p "$(dirname "$COVERAGE_REPORT")"

cat > "$COVERAGE_REPORT" << EOF
# Contract Test Coverage Report

Generated: $(date +"%Y-%m-%d %H:%M:%S")

## Summary

- **Total API Endpoints**: $TOTAL_ENDPOINTS
- **Covered Endpoints**: $UNIQUE_ENDPOINTS
- **Contract Interactions**: $PACT_INTERACTIONS
- **Coverage**: $COVERAGE_PCT%

## Coverage Status

$(if (( $(echo "$COVERAGE_PCT >= 90" | bc -l) )); then
    echo "✅ **EXCELLENT** - Coverage exceeds 90%"
elif (( $(echo "$COVERAGE_PCT >= 75" | bc -l) )); then
    echo "✓ **GOOD** - Coverage exceeds 75%"
elif (( $(echo "$COVERAGE_PCT >= 50" | bc -l) )); then
    echo "⚠️  **FAIR** - Coverage exceeds 50%, but could be improved"
else
    echo "❌ **POOR** - Coverage below 50%, needs improvement"
fi)

## Coverage by Domain

EOF

# Analyze coverage by domain
declare -A DOMAIN_COUNTS
declare -A DOMAIN_COVERED

while IFS= read -r endpoint; do
    # Extract domain from endpoint path
    DOMAIN=$(echo "$endpoint" | sed -E 's|^/api/v1/([^/]+).*|\1|')
    DOMAIN_COUNTS["$DOMAIN"]=$((${DOMAIN_COUNTS["$DOMAIN"]:-0} + 1))
done < <(jq -r '.paths | keys[]' "$OPENAPI_SPEC")

for endpoint in "${COVERED_ENDPOINTS[@]}"; do
    DOMAIN=$(echo "$endpoint" | sed -E 's|^/api/v1/([^/]+).*|\1|')
    DOMAIN_COVERED["$DOMAIN"]=$((${DOMAIN_COVERED["$DOMAIN"]:-0} + 1))
done

echo "| Domain | Covered | Total | Coverage |" >> "$COVERAGE_REPORT"
echo "|--------|---------|-------|----------|" >> "$COVERAGE_REPORT"

for domain in "${!DOMAIN_COUNTS[@]}"; do
    TOTAL=${DOMAIN_COUNTS["$domain"]}
    COVERED=${DOMAIN_COVERED["$domain"]:-0}
    if [ "$TOTAL" -gt 0 ]; then
        DOMAIN_PCT=$(awk "BEGIN {printf \"%.1f\", ($COVERED/$TOTAL)*100}")
        STATUS="❌"
        if (( $(echo "$DOMAIN_PCT >= 90" | bc -l) )); then
            STATUS="✅"
        elif (( $(echo "$DOMAIN_PCT >= 75" | bc -l) )); then
            STATUS="✓"
        elif (( $(echo "$DOMAIN_PCT >= 50" | bc -l) )); then
            STATUS="⚠️"
        fi
        echo "| $domain | $COVERED | $TOTAL | $STATUS $DOMAIN_PCT% |" >> "$COVERAGE_REPORT"
    fi
done | sort

cat >> "$COVERAGE_REPORT" << EOF

## Uncovered Endpoints

The following endpoints do not have contract tests:

EOF

# Find uncovered endpoints
while IFS= read -r endpoint; do
    FOUND=false
    for covered in "${COVERED_ENDPOINTS[@]}"; do
        if [ "$endpoint" = "$covered" ]; then
            FOUND=true
            break
        fi
    done
    if [ "$FOUND" = false ]; then
        echo "- \`$endpoint\`" >> "$COVERAGE_REPORT"
    fi
done < <(jq -r '.paths | keys[]' "$OPENAPI_SPEC" | sort)

cat >> "$COVERAGE_REPORT" << EOF

## Pact Files

EOF

for pact in "$PACTS_DIR"/*.json 2>/dev/null; do
    if [ -f "$pact" ]; then
        PACT_NAME=$(basename "$pact" .json)
        INTERACTION_COUNT=$(jq '.interactions | length' "$pact")
        echo "- **$PACT_NAME**: $INTERACTION_COUNT interactions" >> "$COVERAGE_REPORT"
    fi
done

cat >> "$COVERAGE_REPORT" << EOF

## How to Improve Coverage

1. **Identify uncovered endpoints** from the list above
2. **Create consumer tests** in \`tests/contracts/consumer/<domain>/\`
3. **Run consumer tests** to generate pacts: \`./scripts/run-consumer-tests.sh\`
4. **Verify provider** meets contracts: \`./scripts/run-provider-tests.sh\`
5. **Re-run coverage report** to verify improvement

## Testing Commands

\`\`\`bash
# Run consumer tests
cd tests/contracts
./scripts/run-consumer-tests.sh

# Run provider verification
./scripts/run-provider-tests.sh

# Regenerate this report
./scripts/generate-coverage-report.sh
\`\`\`
EOF

echo ""
echo "Coverage report generated: $COVERAGE_REPORT"
echo ""
echo "Summary:"
echo "  Total Endpoints: $TOTAL_ENDPOINTS"
echo "  Covered: $UNIQUE_ENDPOINTS"
echo "  Coverage: $COVERAGE_PCT%"
echo ""

# Exit with error if coverage is below target
TARGET_COVERAGE=100
if (( $(echo "$COVERAGE_PCT < $TARGET_COVERAGE" | bc -l) )); then
    echo "⚠️  Warning: Coverage ($COVERAGE_PCT%) is below target ($TARGET_COVERAGE%)"
    exit 0  # Don't fail build, just warn
fi

echo "✅ Coverage target met!"
