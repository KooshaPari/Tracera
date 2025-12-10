#!/bin/bash

unit_test_files=0
unit_test_count=0
integration_test_files=0
integration_test_count=0
e2e_test_files=0
e2e_test_count=0
benchmark_count=0
total_files=0

while IFS='|' read -r file package tests benchs category; do
  total_files=$((total_files + 1))
  benchmark_count=$((benchmark_count + benchs))
  
  if [ "$category" = "unit" ]; then
    unit_test_files=$((unit_test_files + 1))
    unit_test_count=$((unit_test_count + tests))
  elif [ "$category" = "integration" ]; then
    integration_test_files=$((integration_test_files + 1))
    integration_test_count=$((integration_test_count + tests))
  elif [ "$category" = "e2e" ]; then
    e2e_test_files=$((e2e_test_files + 1))
    e2e_test_count=$((e2e_test_count + tests))
  fi
done < <(find backend -name "*_test.go" -type f | sort | while read testfile; do
  category="unit"
  if [[ "$testfile" == *"/load/"* ]] || [[ "$testfile" == *"load_test.go"* ]]; then
    category="e2e"
  elif [[ "$testfile" == *"/security/"* ]]; then
    category="e2e"
  elif [[ "$testfile" == *"integration_test.go"* ]]; then
    category="integration"
  fi
  package=$(grep "^package" "$testfile" | head -1 | awk '{print $2}')
  test_count=$(grep -c "^func Test" "$testfile")
  bench_count=$(grep -c "^func Benchmark" "$testfile")
  echo "$testfile|$package|$test_count|$bench_count|$category"
done | sort)

echo "GO TEST INFRASTRUCTURE SUMMARY"
echo "=============================="
echo "Total Test Files: $total_files"
echo ""
echo "BY TYPE:"
echo "  Unit Tests: $unit_test_files files, $unit_test_count test functions"
echo "  Integration Tests: $integration_test_files files, $integration_test_count test functions"
echo "  E2E/Load Tests: $e2e_test_files files, $e2e_test_count test functions"
echo ""
echo "BENCHMARK TESTS: $benchmark_count functions"
echo ""
total_tests=$((unit_test_count + integration_test_count + e2e_test_count))
echo "TOTAL TEST FUNCTIONS: $total_tests"
