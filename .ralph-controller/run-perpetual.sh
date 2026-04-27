#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/kooshapari/CodeProjects/Phenotype/repos/.ralph-controller"
PROMPT=".agents/tasks/phenotype-perpetual-loop.md"
LOG="$ROOT/.ralph/perpetual.log"
STOP="$ROOT/STOP"
PAUSE_HHMM="04:30"

mkdir -p "$ROOT/.ralph"
cd "$ROOT"

export RALPH_CODEX_BINARY="${RALPH_CODEX_BINARY:-/Users/kooshapari/.local/bin/codex}"

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] starting perpetual Ralph loop" >> "$LOG"

while true; do
  if [[ -f "$STOP" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] STOP found; exiting" >> "$LOG"
    exit 0
  fi

  now_hm="$(date '+%H:%M')"
  if [[ "$now_hm" == "$PAUSE_HHMM" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 04:30 pause checkpoint; exiting" >> "$LOG"
    agent-imessage notify "Phenotype Ralph loop paused at ${PAUSE_HHMM} MST. Review .ralph-controller/.ralph/perpetual.log and active repo statuses before resuming." >/dev/null 2>&1 || true
    touch "$STOP"
    exit 0
  fi

  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] iteration begin" >> "$LOG"
  set +e
  npx -y @th0rgal/ralph-wiggum \
    --prompt-file "$PROMPT" \
    --agent codex \
    --model gpt-5.5 \
    --tasks \
    --no-commit \
    --allow-all \
    --max-iterations 1 \
    --completion-promise PHENOTYPE_DAG_COMPLETE >> "$LOG" 2>&1
  code=$?
  set -e
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] iteration end code=$code" >> "$LOG"

  if [[ "$code" -ne 0 ]]; then
    sleep 300
  else
    sleep 120
  fi
done
