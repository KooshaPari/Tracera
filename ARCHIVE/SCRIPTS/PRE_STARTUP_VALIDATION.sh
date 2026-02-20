#!/bin/bash
# PRE_STARTUP_VALIDATION.sh
# Run this after: pip install -e ".[dev,test]"
# Expected: All checks PASS
# Purpose: Catch setup errors before Day 1 work starts

set -e

echo "════════════════════════════════════════════════════════════"
echo "TraceRTM Agent Onboarding - Environment Verification"
echo "════════════════════════════════════════════════════════════"
echo ""

PASS="✅ PASS"
FAIL="❌ FAIL"
WARN="⚠️  WARNING"

# Helper function for error reporting
report_error() {
    local check_name="$1"
    local message="$2"
    local fix="$3"
    echo "$FAIL: $check_name"
    echo "   Error: $message"
    if [ -n "$fix" ]; then
        echo "   Fix: $fix"
    fi
}

# Check 1: Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
    echo "$PASS: Python $PYTHON_VERSION"
else
    report_error "Python Version" "Python $PYTHON_VERSION (need 3.12+)" "Install Python 3.12 or higher"
    exit 1
fi

# Check 2: pytest installed
echo ""
echo "2. Checking pytest..."
if pytest --version 2>/dev/null | grep -q "pytest"; then
    PYTEST_VERSION=$(pytest --version 2>/dev/null | awk '{print $2}')
    echo "$PASS: pytest $PYTEST_VERSION"
else
    report_error "pytest Installation" "pytest not found or not installed" "python3 -m pip install -e '.[dev,test]'"
    exit 1
fi

# Check 3: coverage installed
echo ""
echo "3. Checking coverage..."
if coverage --version 2>/dev/null | grep -q "coverage"; then
    COVERAGE_VERSION=$(coverage --version 2>/dev/null | awk '{print $NF}')
    echo "$PASS: coverage $COVERAGE_VERSION"
else
    report_error "coverage Installation" "coverage not found" "python3 -m pip install -e '.[dev,test]'"
    exit 1
fi

# Check 4: git configured
echo ""
echo "4. Checking git configuration..."
if git config user.email >/dev/null 2>&1; then
    EMAIL=$(git config user.email)
    echo "$PASS: git configured ($EMAIL)"
else
    echo "$WARN: git user.email not set"
    echo "   This is not critical but do it before committing"
    echo "   Fix: git config user.email 'your@email.com'"
fi

# Check 5: pytest can find tests
echo ""
echo "5. Checking test discovery..."
if pytest --collect-only tests/ -q >/dev/null 2>&1; then
    COUNT=$(pytest --collect-only tests/ -q 2>/dev/null | tail -1 | awk '{print $1}')
    echo "$PASS: pytest found ~$COUNT tests"
else
    report_error "Test Discovery" "pytest can't find tests" "Make sure you're in project root: /Users/kooshapari/temp-PRODVERCEL/485/kush/trace"
    exit 1
fi

# Check 6: Can import tracertm
echo ""
echo "6. Checking module imports..."
if python3 -c "import sys; sys.path.insert(0, '.'); from src.tracertm import api" 2>/dev/null; then
    echo "$PASS: tracertm imports OK"
else
    report_error "Module Import" "Can't import tracertm" "Are you in project root? Run: cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace"
    exit 1
fi

# Check 7: Database connectivity (optional but good to verify)
echo ""
echo "7. Checking database setup..."
if python3 -c "import sqlite3; db = sqlite3.connect(':memory:'); db.close()" 2>/dev/null; then
    echo "$PASS: SQLite database available"
else
    report_error "Database" "SQLite not available" "SQLite3 should be built-in. Contact your admin."
    exit 1
fi

# Check 8: Git repository setup
echo ""
echo "8. Checking git repository..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    echo "$PASS: git repository initialized (on branch: $CURRENT_BRANCH)"
else
    report_error "Git Repository" "Not a git repository" "Make sure you're in project root with .git directory"
    exit 1
fi

# Success!
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ All checks passed! You're ready to start."
echo ""
echo "Next Steps:"
echo "1. Read: AGENT_QUICK_START.md"
echo "2. Run: HELLO_WORLD_TEST.py"
echo "3. Find: Your assignment in WORK_PACKAGE_INDEX.md"
echo "4. Start: Your first work package"
echo ""
echo "════════════════════════════════════════════════════════════"
