#!/usr/bin/env bash
set -euo pipefail

THRESHOLD=${1:-85}

echo "Running Go tests with coverage..."
cd "$(dirname "$0")/.."

go test -coverprofile=coverage.out -covermode=atomic ./...

TOTAL=$(go tool cover -func=coverage.out | grep '^total:' | awk '{print $3}' | tr -d '%')

echo "Total coverage: ${TOTAL}%"
echo "Threshold: ${THRESHOLD}%"

if (( $(echo "$TOTAL < $THRESHOLD" | bc -l) )); then
  echo "FAIL: Coverage ${TOTAL}% is below threshold ${THRESHOLD}%"
  exit 1
fi

echo "PASS: Coverage ${TOTAL}% meets threshold ${THRESHOLD}%"
