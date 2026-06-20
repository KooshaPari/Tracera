#!/usr/bin/env bash
# Test pre-commit hook performance
# Usage: ./scripts/test-hook-performance.sh

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧪 Testing Pre-commit Hook Performance"
echo "======================================"
echo ""

# Test sample files - find real files that exist
FRONTEND_SAMPLE=$(find frontend/apps -name "*.tsx" -type f 2>/dev/null | head -1)
PYTHON_SAMPLE=$(find src/tracertm -name "*.py" -type f 2>/dev/null | head -1)
GO_SAMPLE=$(find backend -name "*.go" -type f 2>/dev/null | head -1)

# Helper function to time a command
time_command() {
    local name="$1"
    shift

    # Use gdate if available (GNU coreutils on macOS), otherwise use Perl
    if command -v gdate &>/dev/null; then
        local start=$(gdate +%s%3N)
    else
        local start=$(perl -MTime::HiRes=time -e 'printf("%.0f\n", time*1000)')
    fi

    # Run command, capturing both stdout and stderr
    if "$@" &>/dev/null; then
        local status="✓"
        local color="$GREEN"
    else
        local status="✗"
        local color="$RED"
    fi

    if command -v gdate &>/dev/null; then
        local end=$(gdate +%s%3N)
    else
        local end=$(perl -MTime::HiRes=time -e 'printf("%.0f\n", time*1000)')
    fi

    local duration=$((end - start))

    printf "${color}%-40s %6dms %s${NC}\n" "$name" "$duration" "$status"

    return 0
}

echo "📊 FAST CHECKS (Target: <5s total, <1s each)"
echo "----------------------------------------------"

# Frontend - oxlint
if [ -f "$FRONTEND_SAMPLE" ]; then
    time_command "oxlint (standard config)" \
        bun run --cwd frontend oxlint "$FRONTEND_SAMPLE"

    if [ -f "frontend/.oxlintrc.json" ]; then
        time_command "oxlint (strict config)" \
            bun run --cwd frontend oxlint -c .oxlintrc.json "$FRONTEND_SAMPLE"
    fi
fi

# Python - Ruff (fast)
if [ -f "$PYTHON_SAMPLE" ]; then
    time_command "Ruff check" \
        ruff check --fix --exit-non-zero-on-fix "$PYTHON_SAMPLE"

    time_command "Ruff format" \
        ruff format "$PYTHON_SAMPLE"
fi

# Go - gofmt (fast)
if [ -f "$GO_SAMPLE" ]; then
    time_command "gofmt" \
        gofmt -s -w "$GO_SAMPLE"
fi

# Basic file checks (very fast)
time_command "trailing-whitespace" \
    grep -q '[[:space:]]$' "$FRONTEND_SAMPLE" || true

time_command "end-of-file-fixer" \
    test -n "$(tail -c1 "$FRONTEND_SAMPLE")" || true

echo ""
echo "📊 SLOW CHECKS (CI only - not in pre-commit)"
echo "----------------------------------------------"

# Python - Ty (slow)
if [ -f "$PYTHON_SAMPLE" ]; then
    time_command "Ty (type checking)" \
        ty check "$PYTHON_SAMPLE" || true
fi

# Go - golangci-lint (comprehensive, can be slow)
if [ -f "$GO_SAMPLE" ]; then
    time_command "golangci-lint (7 new linters)" \
        bash -c 'cd backend && golangci-lint run --enable=dupl,goconst,funlen,mnd,nolintlint,gochecknoglobals,perfsprint cmd/server/main.go' || true
fi

# Security scans (slow)
if [ -f "$PYTHON_SAMPLE" ]; then
    time_command "Bandit (security)" \
        bandit -r src/tracertm/ -ll || true
fi

echo ""
echo "📊 CATEGORIZATION SUMMARY"
echo "========================="
echo ""
echo "✅ FAST (Local Pre-commit) - Target <5s total:"
echo "   • oxlint (standard config)          ~100-300ms"
echo "   • Ruff check + format               ~100-400ms"
echo "   • gofmt                              ~50-200ms"
echo "   • Basic file checks                  ~10-50ms"
echo ""
echo "⚠️  SLOW (CI Only) - Move to workflows:"
echo "   • Ty type checking                   >1s"
echo "   • golangci-lint (7 new linters)      >2s"
echo "   • Bandit security scan               >1s"
echo "   • Semgrep security scan              >2s"
echo ""
echo "✨ RECOMMENDATIONS:"
echo "   1. Keep oxlint with STANDARD config in pre-commit (fast)"
echo "   2. Run strict oxlint in CI (may be slower)"
echo "   3. Keep Ruff complexity rules in pre-commit (still fast)"
echo "   4. Move golangci-lint 7 new linters to CI if >5s"
echo "   5. All security scans stay in CI only"
echo ""
