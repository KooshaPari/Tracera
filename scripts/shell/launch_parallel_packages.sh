#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
PROMPT_DIR="$ROOT_DIR/task-tool/parallel_packages"
LOG_DIR="$ROOT_DIR/task-tool/logs"
mkdir -p "$LOG_DIR"

log_msg() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$1"
}

launch_agent() {
  local pkg_id="$1"
  local agent_type="$2"
  local cmd="$3"
  local log_file="$LOG_DIR/${pkg_id}.log"
  local pid_file="$LOG_DIR/${pkg_id}.pid"

  log_msg "Launching ${pkg_id} via ${agent_type}. Logs: ${log_file}"
  bash -lc "cd '$ROOT_DIR' && { ${cmd}; }" >"${log_file}" 2>&1 &
  local pid=$!
  echo "${pid}" >"${pid_file}"
  log_msg "${pkg_id} started with PID ${pid}"
}

# Package commands
CODex_CMD_P1="cat '$PROMPT_DIR/package_a_codex.txt' | codex exec --json --cd '$ROOT_DIR'"
CURSOR_CMD_P2="cat '$PROMPT_DIR/package_b_cursor.txt' | cursor-agent --print --force --output-format stream-json --stream-partial-output"
CODex_CMD_P3="cat '$PROMPT_DIR/package_c_codex.txt' | codex exec --json --cd '$ROOT_DIR'"
CURSOR_CMD_P4="cat '$PROMPT_DIR/package_d_cursor.txt' | cursor-agent --print --force --output-format stream-json --stream-partial-output"

launch_agent "package_a" "codex" "$CODex_CMD_P1"
launch_agent "package_b" "cursor-agent" "$CURSOR_CMD_P2"
launch_agent "package_c" "codex" "$CODex_CMD_P3"
launch_agent "package_d" "cursor-agent" "$CURSOR_CMD_P4"

log_msg "All packages launched. Monitor $LOG_DIR for progress."
