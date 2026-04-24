#!/usr/bin/env bash
# Parse .quality/logs/*.log and print action plan by file.
# Called by run-quality-parallel.sh after quality suites run.

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p .quality/logs

exec python3 "$ROOT/scripts/python/quality-report.py" "$@"
