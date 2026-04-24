#!/bin/bash
echo "================================"
echo "E2E Test Suite Verification"
echo "================================"
echo ""

echo "Test Files:"
find e2e -name "*.spec.ts" -type f | wc -l
echo ""

echo "Total Lines of Test Code:"
wc -l e2e/*.spec.ts | tail -1
echo ""

echo "Test Helper Lines:"
wc -l e2e/fixtures/test-helpers.ts
echo ""

echo "Total Tests (Playwright):"
npx playwright test --list 2>&1 | grep -c "› "
echo ""

echo "Test Files Breakdown:"
for file in e2e/*.spec.ts; do
  tests=$(grep -c "test(" "$file" || echo "0")
  lines=$(wc -l < "$file")
  printf "%-35s %3d tests, %4d lines\n" "$(basename $file)" "$tests" "$lines"
done
echo ""

echo "================================"
echo "Verification Complete!"
echo "================================"
