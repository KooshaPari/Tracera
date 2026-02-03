#!/usr/bin/env bash
# Real-time quality: re-run quality (per-step split + report) when source/config files change.
# Uses watchexec when available; otherwise polls every QUALITY_WATCH_INTERVAL seconds (default 30).
#
# Install watchexec: brew install watchexec (macOS) or cargo install watchexec-cli
#
# Usage: run-quality-watch.sh [--once]   (default: watch and re-run; --once = run once and exit)

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
INTERVAL="${QUALITY_WATCH_INTERVAL:-30}"

run_quality() {
  echo "[quality-watch] $(date -u +"%H:%M:%SZ") Running quality..."
  make quality
}

if [[ "${1:-}" == "--once" ]]; then
  run_quality
  exit 0
fi

if command -v watchexec &>/dev/null; then
  echo "[quality-watch] Real-time: watchexec will re-run quality on file change (debounce 2s). Stop with Ctrl+C."
  watchexec \
    --watch backend \
    --watch src \
    --watch tests \
    --watch frontend \
    --watch proto \
    --watch Makefile \
    --watch config/process-compose.quality.yaml \
    --watch pyproject.toml \
    --watch "frontend/package.json" \
    --ignore ".git" \
    --ignore "node_modules" \
    --ignore ".quality" \
    --ignore "__pycache__" \
    --ignore ".venv" \
    --ignore "*.log" \
    --debounce 2000 \
    -- \
    bash "$ROOT/scripts/shell/run-quality-split.sh"
  exit 0
fi

echo "[quality-watch] watchexec not found; polling every ${INTERVAL}s. Install: brew install watchexec. Stop with Ctrl+C."
run_quality
while true; do
  sleep "$INTERVAL"
  run_quality
done
