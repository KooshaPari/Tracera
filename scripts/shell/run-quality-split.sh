#!/usr/bin/env bash
# Run quality as multiple parallel steps (lint, type, proto, build, test per suite).
# Each step writes to .quality/logs/<step>.log and .quality/logs/<step>.exit.
# Linters use grouped output format (grouped by file) for easy processing by agents.
# Report is run after all steps (and optionally every REFRESH_INTERVAL s while running).
# Usage: REFRESH_INTERVAL=2 (optional) to refresh report as logs arrive.

set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p .quality/logs
LOG_DIR=".quality/logs"

# Step name, make target, log file (no path - we prepend LOG_DIR)
STEPS=(
  naming
  go-lint
  go-proto
  go-build
  go-test
  py-lint
  py-type
  py-test
  fe-lint
  fe-type
  fe-build
  fe-test
)

run_one() {
  local step="$1"
  local log="$LOG_DIR/$step.log"
  local exitf="$LOG_DIR/$step.exit"
  case "$step" in
    naming)    task lint:naming               > "$log" 2>&1; echo $? > "$exitf" ;;
    go-lint)   PORT=18080 task go:lint        > "$log" 2>&1; echo $? > "$exitf" ;;
    go-proto)  task proto:gen                 > "$log" 2>&1; echo $? > "$exitf" ;;
    go-build)  task go:build                > "$log" 2>&1; echo $? > "$exitf" ;;
    go-test)   PORT=18080 task go:test       > "$log" 2>&1; echo $? > "$exitf" ;;
    py-lint)   poe lint                       > "$log" 2>&1; echo $? > "$exitf" ;;
    py-type)   poe type-check                 > "$log" 2>&1; echo $? > "$exitf" ;;
    py-test)   poe test                       > "$log" 2>&1; echo $? > "$exitf" ;;
    fe-lint)   bun run --cwd frontend lint    > "$log" 2>&1; echo $? > "$exitf" ;;
    fe-type)   bun run --cwd frontend typecheck > "$log" 2>&1; echo $? > "$exitf" ;;
    fe-build)  bun run --cwd frontend build   > "$log" 2>&1; echo $? > "$exitf" ;;
    fe-test)   bun run --cwd frontend test    > "$log" 2>&1; echo $? > "$exitf" ;;
    *) echo "Unknown step: $step" >&2; echo 1 > "$exitf" ;;
  esac
}

# Optional: refresh report every N seconds while steps run (populate as they come)
REFRESH_INTERVAL="${REFRESH_INTERVAL:-}"
if [ -n "$REFRESH_INTERVAL" ]; then
  (
    while true; do
      done=0
      for step in "${STEPS[@]}"; do [ -f "$LOG_DIR/$step.exit" ] && done=$((done+1)); done
      [ "$done" -eq "${#STEPS[@]}" ] && break
      "$ROOT/scripts/shell/quality-report.sh" 2>/dev/null || true
      sleep "$REFRESH_INTERVAL"
    done
  ) &
  REFRESH_PID=$!
fi

# Run all steps in parallel
echo "[quality-split] Running ${#STEPS[@]} steps in parallel..."
for step in "${STEPS[@]}"; do
  run_one "$step" &
done
wait
[ -n "${REFRESH_PID:-}" ] && kill "$REFRESH_PID" 2>/dev/null || true

# Per-step exit codes for last-run.json
FAILED_STEPS=()
for step in "${STEPS[@]}"; do
  exit_code=$(cat "$LOG_DIR/$step.exit" 2>/dev/null || echo 1)
  if [ "$exit_code" != "0" ]; then
    FAILED_STEPS+=("$step")
  fi
done

# Write last-run state (per-step)
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '%s' '{"timestamp":"'"$TS"'","steps":{' > "$ROOT/.quality/last-run.json"
first=1
for step in "${STEPS[@]}"; do
  exit_code=$(cat "$LOG_DIR/$step.exit" 2>/dev/null || echo 1)
  [ $first -eq 0 ] && printf ',' >> "$ROOT/.quality/last-run.json"
  printf '"%s":%s' "$step" "$exit_code" >> "$ROOT/.quality/last-run.json"
  first=0
done
printf '},"failed_steps":[' >> "$ROOT/.quality/last-run.json"
first=1
for s in "${FAILED_STEPS[@]}"; do
  [ $first -eq 0 ] && printf ',' >> "$ROOT/.quality/last-run.json"
  printf '"%s"' "$s" >> "$ROOT/.quality/last-run.json"
  first=0
done
printf '],"ok":%s}' "$([ ${#FAILED_STEPS[@]} -eq 0 ] && echo true || echo false)" >> "$ROOT/.quality/last-run.json"

# Report (reads per-step logs; groups lint/type by file, tests separate)
"$ROOT/scripts/shell/quality-report.sh" "$@"

[ ${#FAILED_STEPS[@]} -gt 0 ] && exit 1
exit 0
