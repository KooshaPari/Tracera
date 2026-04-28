#!/usr/bin/env bash
#
# verify-ci-improvements.sh - Verify CI/CD improvements are working correctly
#
# Usage: bash scripts/verify-ci-improvements.sh

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CI/CD Improvements Verification ===${NC}\n"

# Check workflow files exist and are valid YAML
echo -e "${YELLOW}1. Checking workflow files...${NC}"
if [ -f .github/workflows/tests.yml ]; then
    echo "  ✅ tests.yml exists"
    python3 -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml'))" 2>/dev/null && echo "  ✅ tests.yml is valid YAML" || echo "  ❌ tests.yml has invalid YAML"
else
    echo "  ❌ tests.yml not found"
fi

if [ -f .github/workflows/ci.yml ]; then
    echo "  ✅ ci.yml exists"
    python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" 2>/dev/null && echo "  ✅ ci.yml is valid YAML" || echo "  ❌ ci.yml has invalid YAML"
else
    echo "  ❌ ci.yml not found"
fi

# Check Taskfile targets
echo -e "\n${YELLOW}2. Checking Taskfile targets...${NC}"
for target in test:unit test:e2e test:integration; do
    if grep -q "  $target:" Taskfile.yml 2>/dev/null; then
        echo "  ✅ task $target exists"
    else
        echo "  ❌ task $target not found"
    fi
done

# Check pytest markers
echo -e "\n${YELLOW}3. Checking pytest markers...${NC}"
if grep -q "markers = \[" pyproject.toml 2>/dev/null; then
    echo "  ✅ Pytest markers configured in pyproject.toml"

    # Check for specific markers
    for marker in "unit" "integration" "e2e" "slow"; do
        if grep -q "\"$marker:" pyproject.toml 2>/dev/null; then
            echo "  ✅ Marker '$marker' is defined"
        else
            echo "  ⚠️  Marker '$marker' not found"
        fi
    done
else
    echo "  ❌ Pytest markers not found in pyproject.toml"
fi

# Check documentation
echo -e "\n${YELLOW}4. Checking documentation...${NC}"
if [ -f docs/guides/CI_CD_IMPROVEMENTS.md ]; then
    echo "  ✅ CI/CD Improvements guide exists"
else
    echo "  ❌ CI/CD Improvements guide not found"
fi

if [ -f docs/reference/CI_CD_QUICK_REFERENCE.md ]; then
    echo "  ✅ CI/CD Quick Reference exists"
else
    echo "  ❌ CI/CD Quick Reference not found"
fi

if [ -f docs/reports/CI_CD_IMPROVEMENTS_SUMMARY.md ]; then
    echo "  ✅ CI/CD Improvements Summary exists"
else
    echo "  ❌ CI/CD Improvements Summary not found"
fi

# Check CHANGELOG
echo -e "\n${YELLOW}5. Checking CHANGELOG...${NC}"
if grep -q "CI/CD Pipeline Improvements" CHANGELOG.md 2>/dev/null; then
    echo "  ✅ CHANGELOG updated with CI/CD improvements"
else
    echo "  ⚠️  CHANGELOG not updated"
fi

# Test matrix verification
echo -e "\n${YELLOW}6. Checking test matrix configuration...${NC}"
if grep -q "test-type: \[unit, integration, e2e\]" .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Test matrix configured with unit, integration, e2e"
else
    echo "  ❌ Test matrix not properly configured"
fi

if grep -q "python-version: \[\"3.11\", \"3.12\"\]" .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Python version matrix configured (3.11, 3.12)"
else
    echo "  ⚠️  Python version matrix not found"
fi

# Retry configuration
echo -e "\n${YELLOW}7. Checking retry configuration...${NC}"
if grep -q "nick-fields/retry@v3" .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Retry action configured in tests.yml"
else
    echo "  ⚠️  Retry action not found in tests.yml"
fi

if grep -q "nick-fields/retry@v3" .github/workflows/ci.yml 2>/dev/null; then
    echo "  ✅ Retry action configured in ci.yml"
else
    echo "  ⚠️  Retry action not found in ci.yml"
fi

# Test summaries
echo -e "\n${YELLOW}8. Checking test summary generation...${NC}"
if grep -q "GITHUB_STEP_SUMMARY" .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Test summaries configured in tests.yml"
else
    echo "  ⚠️  Test summaries not found in tests.yml"
fi

if grep -q "GITHUB_STEP_SUMMARY" .github/workflows/ci.yml 2>/dev/null; then
    echo "  ✅ Test summaries configured in ci.yml"
else
    echo "  ⚠️  Test summaries not found in ci.yml"
fi

# Fast/slow test ordering
echo -e "\n${YELLOW}9. Checking fast/slow test ordering...${NC}"
if grep -q '"unit and not slow"' .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Fast test ordering configured (not slow first)"
else
    echo "  ⚠️  Fast test ordering not found"
fi

if grep -q '"unit and slow"' .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Slow test ordering configured (slow second)"
else
    echo "  ⚠️  Slow test ordering not found"
fi

# Flaky test detection
echo -e "\n${YELLOW}10. Checking flaky test detection...${NC}"
if grep -q "Detect flaky tests" .github/workflows/tests.yml 2>/dev/null; then
    echo "  ✅ Flaky test detection configured"
else
    echo "  ⚠️  Flaky test detection not found"
fi

# Final summary
echo -e "\n${GREEN}=== Verification Complete ===${NC}\n"

# Run a quick local test to verify markers work
echo -e "${YELLOW}11. Testing pytest markers locally...${NC}"
if command -v pytest &> /dev/null; then
    # Check if any tests exist
    if [ -d tests/ ] && [ -n "$(find tests/ -name 'test_*.py' -o -name '*_test.py' 2>/dev/null)" ]; then
        echo "  Testing 'unit' marker..."
        if pytest --collect-only -m unit -q 2>/dev/null | grep -q "test"; then
            echo "  ✅ 'unit' marker works"
        else
            echo "  ⚠️  No unit tests found or marker not working"
        fi

        echo "  Testing 'slow' marker..."
        if pytest --collect-only -m slow -q 2>/dev/null | grep -q "test"; then
            echo "  ✅ 'slow' marker works"
        elif pytest --collect-only -m slow -q 2>/dev/null | grep -q "no tests collected"; then
            echo "  ℹ️  'slow' marker works (no slow tests yet)"
        else
            echo "  ⚠️  'slow' marker not working"
        fi
    else
        echo "  ℹ️  No tests found to verify markers"
    fi
else
    echo "  ℹ️  pytest not installed, skipping marker verification"
fi

echo -e "\n${GREEN}✅ CI/CD improvements verification complete!${NC}"
echo -e "\nNext steps:"
echo "  1. Review the verification results above"
echo "  2. Fix any warnings or errors"
echo "  3. Run 'task test:unit' to test locally"
echo "  4. Push changes to trigger CI/CD workflows"
echo "  5. Check GitHub Actions for test matrix execution"
