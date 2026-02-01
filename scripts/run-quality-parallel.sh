#!/usr/bin/env bash
# Run quality-go, quality-python, quality-frontend in parallel; then print action plan by file.
# Logs go to .quality/logs; script exits with 1 if any suite failed.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p .quality/logs

LOG_GO=".quality/logs/quality-go.log"
LOG_PY=".quality/logs/quality-python.log"
LOG_FE=".quality/logs/quality-frontend.log"

run_go()   { PORT=18080 make quality-go   > "$LOG_GO" 2>&1; echo $? > .quality/logs/quality-go.exit; }
run_py()   { make quality-python > "$LOG_PY" 2>&1; echo $? > .quality/logs/quality-python.exit; }
run_fe()   { make quality-frontend > "$LOG_FE" 2>&1; echo $? > .quality/logs/quality-frontend.exit; }

echo "[quality] Running Go, Python, frontend in parallel..."
run_go & run_py & run_fe & wait

EXIT_GO=$(cat .quality/logs/quality-go.exit 2>/dev/null || echo 1)
EXIT_PY=$(cat .quality/logs/quality-python.exit 2>/dev/null || echo 1)
EXIT_FE=$(cat .quality/logs/quality-frontend.exit 2>/dev/null || echo 1)

FAILED=0
[ "$EXIT_GO" != "0" ] && { echo "[quality] Go suite failed (see $LOG_GO)"; FAILED=1; }
[ "$EXIT_PY" != "0" ] && { echo "[quality] Python suite failed (see $LOG_PY)"; FAILED=1; }
[ "$EXIT_FE" != "0" ] && { echo "[quality] Frontend suite failed (see $LOG_FE)"; FAILED=1; }

# Write last-run state before report so report sees current run (for short success when all pass)
mkdir -p "$ROOT/.quality"
LAST_RUN="$ROOT/.quality/last-run.json"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FAILED_SUITES=""
[ "$EXIT_GO" != "0" ] && FAILED_SUITES="${FAILED_SUITES:+$FAILED_SUITES,}\"go\""
[ "$EXIT_PY" != "0" ] && FAILED_SUITES="${FAILED_SUITES:+$FAILED_SUITES,}\"python\""
[ "$EXIT_FE" != "0" ] && FAILED_SUITES="${FAILED_SUITES:+$FAILED_SUITES,}\"frontend\""
printf '%s\n' "{\"timestamp\":\"$TS\",\"exit_go\":$EXIT_GO,\"exit_python\":$EXIT_PY,\"exit_frontend\":$EXIT_FE,\"failed_suites\":[$FAILED_SUITES],\"ok\":$([ "$FAILED" = 0 ] && echo true || echo false)}" > "$LAST_RUN"

# Run report (uses last-run.json for short success when all pass)
"$ROOT/scripts/quality-report.sh" "$@"

[ "$FAILED" = 1 ] && exit 1
exit 0
