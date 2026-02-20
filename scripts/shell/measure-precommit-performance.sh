#!/usr/bin/env bash
# Measure pre-commit hook performance
# Target: <5s execution time
# Usage: ./scripts/measure-precommit-performance.sh

set -euo pipefail

echo "🔍 Measuring pre-commit hook performance..."
echo "Target: <5s total execution time"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Run with timing
echo "Running pre-commit on all files..."
START_TIME=$(date +%s.%N)

if time pre-commit run --all-files; then
    EXIT_CODE=0
else
    EXIT_CODE=$?
fi

END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Performance Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Display duration with color coding
if (( $(echo "$DURATION < 5" | bc -l) )); then
    echo -e "${GREEN}✓ Total time: ${DURATION}s (Target: <5s)${NC}"
    echo -e "${GREEN}✓ Performance target met!${NC}"
elif (( $(echo "$DURATION < 10" | bc -l) )); then
    echo -e "${YELLOW}⚠ Total time: ${DURATION}s (Target: <5s)${NC}"
    echo -e "${YELLOW}⚠ Room for improvement${NC}"
else
    echo -e "${RED}✗ Total time: ${DURATION}s (Target: <5s)${NC}"
    echo -e "${RED}✗ Performance needs optimization${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show individual hook timings if available
if [ -d .git/hooks ]; then
    echo "💡 Tips for faster pre-commit:"
    echo "   • Only changed files are checked (pass_filenames: true)"
    echo "   • Hooks run in parallel automatically"
    echo "   • Slow checks (ty, pytest) moved to CI"
    echo "   • Use 'SKIP=<hook-id> git commit' to skip specific hooks"
    echo ""
fi

# Show what's in CI vs pre-commit
echo "📊 Check distribution:"
echo ""
echo "Pre-commit (fast checks, <5s):"
echo "  • ruff (lint + format)"
echo "  • pycln (unused imports)"
echo "  • oxfmt (frontend)"
echo "  • basic file checks"
echo "  • gofmt"
echo "  • oxlint (frontend)"
echo ""
echo "CI only (comprehensive checks):"
echo "  • ty (type checking)"
echo "  • bandit (security)"
echo "  • semgrep (security)"
echo "  • interrogate (docstrings)"
echo "  • tach (architecture)"
echo "  • golangci-lint (Go)"
echo "  • pytest (tests)"
echo ""

exit $EXIT_CODE
