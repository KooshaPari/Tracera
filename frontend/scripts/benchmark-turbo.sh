#!/usr/bin/env bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Turbo Pipeline Benchmark Tool${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Create benchmark results file
RESULTS_FILE="/tmp/turbo-benchmark-$(date +%Y%m%d-%H%M%S).txt"
echo "Benchmark Results - $(date)" > "$RESULTS_FILE"
echo "================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Function to measure time
measure_time() {
    local cmd="$1"
    local desc="$2"

    echo -e "${YELLOW}Running: $desc${NC}"
    echo "$desc" >> "$RESULTS_FILE"

    local start=$(date +%s)
    eval "$cmd" > /dev/null 2>&1
    local exit_code=$?
    local end=$(date +%s)
    local duration=$((end - start))

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Completed in ${duration}s${NC}"
        echo "Time: ${duration}s - ✓ Success" >> "$RESULTS_FILE"
    else
        echo -e "${RED}✗ Failed after ${duration}s${NC}"
        echo "Time: ${duration}s - ✗ Failed" >> "$RESULTS_FILE"
    fi

    echo "" >> "$RESULTS_FILE"
    echo ""

    return $duration
}

# 1. Cold cache build
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test 1: Full Build (Cold Cache)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Cleaning cache...${NC}"
turbo clean > /dev/null 2>&1
rm -rf .turbo/cache > /dev/null 2>&1
find apps -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find apps -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true

measure_time "bun run build" "Full build (cold cache)"
COLD_TIME=$?

# 2. Warm cache build
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test 2: Full Build (Warm Cache)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

measure_time "bun run build" "Full build (warm cache)"
WARM_TIME=$?

# 3. Web app only
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test 3: Web App Build${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

rm -rf apps/web/dist > /dev/null 2>&1
measure_time "bun run build:web" "Web app build"
WEB_TIME=$?

# 4. Typecheck
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test 4: Typecheck${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

measure_time "bun run typecheck" "Typecheck all packages"
TYPECHECK_TIME=$?

# 5. Lint
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test 5: Lint${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

measure_time "bun run lint:turbo" "Lint all packages"
LINT_TIME=$?

# 6. CI Build
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Test 6: CI Build (build + typecheck + lint)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

turbo clean > /dev/null 2>&1
rm -rf .turbo/cache > /dev/null 2>&1
find apps -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find apps -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true

measure_time "bun run ci:build" "CI build (cold cache)"
CI_TIME=$?

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Benchmark Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Summary" >> "$RESULTS_FILE"
echo "================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

print_result() {
    local name="$1"
    local time=$2
    local target=$3

    printf "%-30s %5ss" "$name" "$time"
    echo -n " | "

    if [ $time -le $target ]; then
        echo -e "${GREEN}✓ Target: <${target}s${NC}"
        echo "$name: ${time}s ✓ (target: <${target}s)" >> "$RESULTS_FILE"
    else
        echo -e "${RED}✗ Target: <${target}s (${time}s over)${NC}"
        echo "$name: ${time}s ✗ (target: <${target}s, over by $((time - target))s)" >> "$RESULTS_FILE"
    fi
}

print_result "Full build (cold)" $COLD_TIME 45
print_result "Full build (warm)" $WARM_TIME 5
print_result "Web app build" $WEB_TIME 15
print_result "Typecheck" $TYPECHECK_TIME 15
print_result "Lint" $LINT_TIME 10
print_result "CI build (cold)" $CI_TIME 50

echo ""
echo "" >> "$RESULTS_FILE"

# Cache statistics
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Cache Statistics${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Cache Statistics" >> "$RESULTS_FILE"
echo "================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

if [ -d ".turbo/cache" ]; then
    CACHE_SIZE=$(du -sh .turbo/cache 2>/dev/null | cut -f1)
    CACHE_FILES=$(find .turbo/cache -type f 2>/dev/null | wc -l | tr -d ' ')
    echo -e "Cache size: ${GREEN}$CACHE_SIZE${NC}"
    echo -e "Cache files: ${GREEN}$CACHE_FILES${NC}"
    echo "Cache size: $CACHE_SIZE" >> "$RESULTS_FILE"
    echo "Cache files: $CACHE_FILES" >> "$RESULTS_FILE"
else
    echo -e "${YELLOW}No cache directory found${NC}"
    echo "No cache directory found" >> "$RESULTS_FILE"
fi

echo ""
echo "" >> "$RESULTS_FILE"

# Overall assessment
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Assessment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Assessment" >> "$RESULTS_FILE"
echo "================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

PASSED=0
TOTAL=6

[ $COLD_TIME -le 45 ] && PASSED=$((PASSED + 1))
[ $WARM_TIME -le 5 ] && PASSED=$((PASSED + 1))
[ $WEB_TIME -le 15 ] && PASSED=$((PASSED + 1))
[ $TYPECHECK_TIME -le 15 ] && PASSED=$((PASSED + 1))
[ $LINT_TIME -le 10 ] && PASSED=$((PASSED + 1))
[ $CI_TIME -le 50 ] && PASSED=$((PASSED + 1))

PERCENTAGE=$((PASSED * 100 / TOTAL))

if [ $PERCENTAGE -ge 80 ]; then
    echo -e "${GREEN}✓ Optimization successful: $PASSED/$TOTAL tests passed ($PERCENTAGE%)${NC}"
    echo "✓ Optimization successful: $PASSED/$TOTAL tests passed ($PERCENTAGE%)" >> "$RESULTS_FILE"
elif [ $PERCENTAGE -ge 50 ]; then
    echo -e "${YELLOW}⚠ Partial optimization: $PASSED/$TOTAL tests passed ($PERCENTAGE%)${NC}"
    echo "⚠ Partial optimization: $PASSED/$TOTAL tests passed ($PERCENTAGE%)" >> "$RESULTS_FILE"
else
    echo -e "${RED}✗ Optimization incomplete: $PASSED/$TOTAL tests passed ($PERCENTAGE%)${NC}"
    echo "✗ Optimization incomplete: $PASSED/$TOTAL tests passed ($PERCENTAGE%)" >> "$RESULTS_FILE"
fi

echo ""
echo "" >> "$RESULTS_FILE"

# Improvement over baseline
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Improvement vs Baseline (~2min)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Improvement vs Baseline (120s)" >> "$RESULTS_FILE"
echo "================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

BASELINE=120
IMPROVEMENT=$((100 - (COLD_TIME * 100 / BASELINE)))
SPEEDUP=$(echo "scale=2; $BASELINE / $COLD_TIME" | bc)

echo -e "Baseline: ${YELLOW}120s${NC}"
echo -e "Current: ${GREEN}${COLD_TIME}s${NC}"
echo -e "Improvement: ${GREEN}${IMPROVEMENT}%${NC}"
echo -e "Speedup: ${GREEN}${SPEEDUP}x${NC}"

echo "Baseline: 120s" >> "$RESULTS_FILE"
echo "Current: ${COLD_TIME}s" >> "$RESULTS_FILE"
echo "Improvement: ${IMPROVEMENT}%" >> "$RESULTS_FILE"
echo "Speedup: ${SPEEDUP}x" >> "$RESULTS_FILE"

echo ""
echo "" >> "$RESULTS_FILE"

# Save results
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Results Saved${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}Results saved to: $RESULTS_FILE${NC}"
echo ""
echo -e "${YELLOW}View results: cat $RESULTS_FILE${NC}"
echo ""

# Recommendations
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Recommendations${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $COLD_TIME -gt 45 ]; then
    echo -e "${YELLOW}→ Cold build is slow. Consider:${NC}"
    echo "  - Checking for unnecessary dependencies"
    echo "  - Reviewing vite/next.config for optimizations"
    echo "  - Enabling remote caching"
    echo ""
fi

if [ $WARM_TIME -gt 5 ]; then
    echo -e "${YELLOW}→ Warm cache is slow. Check:${NC}"
    echo "  - Input patterns in turbo.json"
    echo "  - Cache directory: .turbo/cache"
    echo "  - Run: turbo build --force to regenerate"
    echo ""
fi

if [ $PERCENTAGE -lt 100 ]; then
    echo -e "${YELLOW}→ Some tests failed. Next steps:${NC}"
    echo "  - Review TURBO_OPTIMIZATION_GUIDE.md"
    echo "  - Check for build errors in individual apps"
    echo "  - Verify concurrency settings match CPU cores"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
