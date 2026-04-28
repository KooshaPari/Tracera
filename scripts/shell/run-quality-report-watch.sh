#!/usr/bin/env bash
# File-watched quality report: re-run report when .quality/logs or source files change.
# Use after running quality or quality-pc so the action plan refreshes on change.
# Uses watchexec when available; otherwise polls every QUALITY_REPORT_INTERVAL s (default 5).
#
# Install watchexec: brew install watchexec (macOS) or cargo install watchexec-cli
#
# Usage: run-quality-report-watch.sh [--once]   (default: watch and re-run; --once = run once and exit)

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p .quality/logs
INTERVAL="${QUALITY_REPORT_INTERVAL:-5}"

run_report() {
  echo "[quality-report] $(date -u +"%H:%M:%SZ") Refreshing action plan..."
  bash "$ROOT/scripts/shell/quality-report.sh"
}

if [[ "${1:-}" == "--once" ]]; then
  run_report
  exit 0
fi

if command -v watchexec &>/dev/null; then
  echo "[quality-report] File-watched report: re-running when .quality/logs or source changes (debounce 1s). Stop with Ctrl+C."
  watchexec \
    --watch .quality/logs \
    --watch backend \
    --watch src \
    --watch tests \
    --watch frontend \
    --watch Makefile \
    --watch config/process-compose.quality.yaml \
    --watch pyproject.toml \
    --watch "frontend/package.json" \
    --ignore ".git" \
    --ignore "node_modules" \
    --ignore "__pycache__" \
    --ignore ".venv" \
    --debounce 1000 \
    -- \
    bash "$ROOT/scripts/shell/quality-report.sh"
  exit 0
fi

echo "[quality-report] watchexec not found; polling every ${INTERVAL}s. Install: brew install watchexec. Stop with Ctrl+C."
run_report
while true; do
  sleep "$INTERVAL"
  run_report
done
