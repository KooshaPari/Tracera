#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/kooshapari/CodeProjects/Phenotype/repos/.ralph-controller"
LOG="$ROOT/.ralph/perpetual.log"
STOP="$ROOT/STOP"
PAUSE_HHMM="${1:-04:30}"

kill_tree() {
  local pid="$1"
  local child
  for child in $(pgrep -P "$pid" 2>/dev/null || true); do
    kill_tree "$child"
  done
  kill "$pid" 2>/dev/null || true
}

while true; do
  now_hm="$(date '+%H:%M')"
  if [[ "$now_hm" > "$PAUSE_HHMM" || "$now_hm" == "$PAUSE_HHMM" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] watchdog pause checkpoint" >> "$LOG"
    touch "$STOP"
    for pid in $(pgrep -f "$ROOT/run-perpetual.sh" 2>/dev/null || true); do
      [[ "$pid" == "$$" ]] && continue
      kill_tree "$pid"
    done
    agent-imessage notify "Phenotype Ralph loop paused by watchdog at ${PAUSE_HHMM} MST. STOP file is set at ${STOP}." >/dev/null 2>&1 || true
    exit 0
  fi
  sleep 15
done
