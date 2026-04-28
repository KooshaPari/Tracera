#!/bin/bash
# Validation script for load testing setup
set -e

echo "🔍 Validating Load Testing Setup..."
echo ""

# Check k6 installation
echo "1. Checking k6 installation..."
if command -v k6 &> /dev/null; then
    echo "   ✓ k6 is installed: $(k6 version)"
else
    echo "   ✗ k6 is not installed"
    echo "   Run: ./scripts/shell/install_k6.sh"
    exit 1
fi

# Check test files exist
echo ""
echo "2. Checking test files..."
test_files=(
    "load-tests/smoke-test.js"
    "load-tests/go-items.js"
    "load-tests/go-graph.js"
    "load-tests/python-specs.js"
    "load-tests/python-ai.js"
    "load-tests/websocket.js"
    "load-tests/e2e-scenario.js"
    "load-tests/stress-test.js"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file missing"
        exit 1
    fi
done

# Check scripts exist and are executable
echo ""
echo "3. Checking scripts..."
scripts=(
    "scripts/shell/install_k6.sh"
    "scripts/shell/run_load_tests.sh"
    "scripts/python/generate_load_test_report.py"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo "   ✓ $script (executable)"
    elif [ -f "$script" ]; then
        echo "   ⚠ $script (not executable)"
        chmod +x "$script"
        echo "   ✓ Made executable"
    else
        echo "   ✗ $script missing"
        exit 1
    fi
done

# Check documentation
echo ""
echo "4. Checking documentation..."
docs=(
    "docs/testing/load_testing_guide.md"
    "load-tests/README.md"
    "LOAD_TESTING_IMPLEMENTATION_SUMMARY.md"
    "LOAD_TESTING_QUICK_START.md"
    "LOAD_TESTING_INDEX.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "   ✓ $doc"
    else
        echo "   ✗ $doc missing"
        exit 1
    fi
done

# Check directories
echo ""
echo "5. Checking directories..."
if [ -d "load-tests" ]; then
    echo "   ✓ load-tests/"
else
    echo "   ✗ load-tests/ missing"
    exit 1
fi

if [ -d "load-tests/results" ]; then
    echo "   ✓ load-tests/results/"
else
    echo "   ⚠ load-tests/results/ missing, creating..."
    mkdir -p load-tests/results
    echo "   ✓ Created"
fi

# Check backend services (if running)
echo ""
echo "6. Checking backend services..."
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "   ✓ Nginx gateway is healthy"
else
    echo "   ⚠ Nginx not responding (services may not be running)"
fi

if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✓ Go backend is healthy"
else
    echo "   ⚠ Go backend not responding"
fi

if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Python backend is healthy"
else
    echo "   ⚠ Python backend not responding"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Load Testing Setup Validation Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. If services are not running: docker-compose up -d"
echo "  2. Run smoke test: k6 run load-tests/smoke-test.js"
echo "  3. Run full suite: ./scripts/shell/run_load_tests.sh"
echo "  4. View report: open load-tests/results/report.html"
echo ""
echo "Documentation:"
echo "  - Quick Start: LOAD_TESTING_QUICK_START.md"
echo "  - Full Guide: docs/testing/load_testing_guide.md"
echo "  - Index: LOAD_TESTING_INDEX.md"
echo ""
