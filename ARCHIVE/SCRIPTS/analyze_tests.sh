#!/bin/bash

declare -A unit_tests
declare -A integration_tests
declare -A e2e_tests
declare -A benchmark_tests

unit_count=0
integration_count=0
e2e_count=0
benchmark_count=0
total_files=0

for testfile in $(find backend -name "*_test.go" -type f | sort); do
  total_files=$((total_files + 1))
  
  # Determine test type by filename and content
  if [[ "$testfile" == *"/load/"* ]] || [[ "$testfile" == *"load_test.go"* ]]; then
    category="e2e"
  elif [[ "$testfile" == *"/security/"* ]]; then
    category="e2e"
  elif [[ "$testfile" == *"integration_test.go"* ]]; then
    category="integration"
  elif [[ "$testfile" == *"_test.go"* ]]; then
    # Default to unit if not specified
    category="unit"
  fi
  
  # Count test functions
  test_count=$(grep -c "^func Test" "$testfile")
  bench_count=$(grep -c "^func Benchmark" "$testfile")
  
  if [ "$test_count" -gt 0 ] || [ "$bench_count" -gt 0 ]; then
    package=$(grep "^package" "$testfile" | head -1 | awk '{print $2}')
    echo "$testfile|$package|$test_count|$bench_count|$category"
  fi
done | sort
